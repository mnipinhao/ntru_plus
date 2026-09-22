"""Small fail-closed GAS macro expander for this checkpoint's source ledger.

Not an assembler or disassembler. Only the explicitly selected public loops
are replayed. Unknown directives/conditionals fail rather than imply zero cost.
"""
import re
from collections import Counter


def operands(text):
    return re.split(r",(?![^()]*\))", text)


class Source:
    def __init__(self, text):
        self.text = text
        self.macros = {}
        self.serial = 0
        self.definitions=[]
        for m in re.finditer(r"^\s*\.macro\s+(\w+)([^\n]*)\n(.*?)^\s*\.endm", text, re.M|re.S):
            names=[x.strip() for x in m[2].strip().split(",") if x.strip()]
            self.macros[m[1]]=(names,m[3].splitlines())
            self.definitions.append((m.end(),m[1],(names,m[3].splitlines())))

    def at(self, offset):
        self.macros={}
        for end,name,value in self.definitions:
            if end<=offset:
                self.macros[name]=value

    def expand(self, lines):
        result=[]
        active=[True]
        for line in lines:
            line=line.split("#",1)[0].strip()
            if not line:
                continue
            if line.startswith(".if "):
                expr=line[4:].strip()
                assert re.fullmatch(r"[0-9() +*/%=!<>-]+",expr),line
                yes=(not int(expr[1:])) if re.fullmatch(r"!\d+",expr) else bool(eval(expr.replace('/', '//'),{'__builtins__':{}},{}))
                active.append(active[-1] and yes)
                continue
            if line==".else":
                active[-1]=active[-2] and not active[-1]
                continue
            if line==".endif":
                active.pop()
                continue
            if not active[-1]:
                continue
            words=line.split(None,1)
            if words[0] in self.macros:
                names,body=self.macros[words[0]]
                values=[x.strip() for x in operands(words[1])] if len(words)>1 else []
                assert len(names)==len(values),(words,names,values)
                subst=dict(zip(names,values))
                serial=self.serial
                self.serial+=1
                expanded=[]
                for old in body:
                    new=old.replace("\\@",str(serial))
                    new=re.sub(r"\\([A-Za-z_]\w*)",lambda m:subst[m[1]],new)
                    expanded.append(new.replace("\\()",""))
                result.extend(self.expand(expanded))
            else:
                assert "\\" not in line,line
                result.append(line)
        assert len(active)==1
        return result

    def function(self, name):
        match=re.search(r"^"+re.escape(name)+r":\n(.*?)^\s*\.size\s+"+re.escape(name)+r",",self.text,re.M|re.S)
        if match:
            self.at(match.start())
            return self.expand(match[1].splitlines())
        # A complete function may be emitted by one selected macro invocation.
        for line in self.text.splitlines():
            if re.match(r"\s*[A-Z]\w*\s+"+re.escape(name)+",",line):
                self.at(self.text.index(line))
                expanded=self.expand([line])
                first=expanded.index(name+":")+1
                return expanded[first:next(i for i in range(first,len(expanded)) if expanded[i].startswith(".size "))]
        raise AssertionError(("missing reachable function",name))


def replay_loop(lines, count, label_prefix):
    begin=next(i for i,x in enumerate(lines) if x.startswith(label_prefix) and x.endswith(":"))
    label=lines[begin][:-1]
    end=next(i for i,x in enumerate(lines) if x in ("jne "+label,"jnz "+label))
    return lines[:begin]+lines[begin+1:end+1]*count+lines[end+1:]


def stats(lines,constant_bases=()):
    counts=Counter()
    classes=Counter()
    constant_expressions=Counter()
    definitions=[]
    for line in lines:
        if line.endswith(":") or line.startswith("."):
            continue
        op,*rest=line.split(None,1)
        counts[op]+=1
        args=[x.strip() for x in operands(rest[0])] if rest else []
        if op.startswith(("vperm","vpshuf","vpunpck","vpblend","vinsert","vextract")):
            classes['routing']+=1
        elif op in ('vpaddw','vpsubw'):
            classes['add_sub']+=1
        elif op=='vpmulhrsw':
            classes['Barrett_vectors']+=1
        elif not op.startswith('v'):
            classes['GPR_control_call_ret']+=1
        if op.startswith('v'):
            for j,arg in enumerate(args):
                if '(' not in arg:
                    continue
                if j==len(args)-1:
                    classes['data_store_instructions']+=1
                elif '%rip' in arg or any('%'+base in arg for base in constant_bases):
                    classes['constant_memory_operands']+=1
                    constant_expressions[arg]+=1
                else:
                    classes['data_load_instructions']+=1
        regs=lambda a:{int(x) for x in re.findall(r'%[xy]mm(\d+)',a)}
        dest=regs(args[-1]) if args and re.fullmatch(r'%[xy]mm\d+',args[-1]) else set()
        reads=set().union(*(regs(x) for x in (args[:-1] if dest else args))) if args else set()
        if op=='vpxor' and len(args)==3 and args[0]==args[1]:
            reads=set()
        definitions.append((line,reads,dest))
    initialized=set()
    for line,reads,writes in definitions:
        assert reads<=initialized,("uninitialized register",line,reads-initialized)
        initialized|=writes
    live=set()
    trace=[]
    peak=0
    for line,reads,writes in reversed(definitions):
        after=sorted(live)
        live=(live-writes)|reads
        peak=max(peak,len(live),len(after))
        trace.append(dict(instruction=line,live_before=sorted(live),live_after=after))
    assert not live and peak<=16
    return dict(opcodes=dict(counts),classes=dict(classes),instructions=sum(counts.values()),
                constant_address_expressions=dict(constant_expressions),
                peak_live_YMM=peak,def_use=list(reversed(trace)),
                evidence="expanded source path; VEX XMM writes kill upper YMM; not linked-binary proof",
                excludes="assembler-inserted alignment padding and final code placement; .org padding after ret is unreachable")


def current_ledger(clean):
    ntt=Source((clean/'ntt.s').read_text())
    term=Source((clean/'ntt_m.s').read_text())
    bm=Source((clean/'basemul.s').read_text())
    pack=Source((clean/'pack.s').read_text())
    front=stats(ntt.function('ntruplus768_ntt_frontend_avx2'),('rdx','rcx'))
    terminal=stats(replay_loop(term.function('ntruplus768_ntt_m_avx2'),6,'.Lfr_core_loop'))
    arithmetic=stats(replay_loop(bm.function('ntruplus768_basemul_general_m_avx2'),12,'.Ltile4_bm_b3_loop'),('r8','r9'))
    decode_lines=pack.function('ntruplus768_unpack_m_avx2')
    body=pack.function('ntruplus768_unpack_m_body_avx2')
    decoded=[]
    for line in decode_lines:
        decoded.append(line)
        if line=='call ntruplus768_unpack_m_body_avx2':
            decoded.extend(body)
    decoder=stats(decoded)
    serializer=stats(pack.function('ntruplus768_pack_m_lazy10788_avx2'))
    return dict(frontend=front,NTT32_terminal=terminal,Mul=arithmetic,decode=decoder,pack=serializer,
                note="highrange pack is a tail jump to lazy pack; include that one GPR jump for ciphertext; separate add-m is additional")


def wire_ledger(root):
    fwd=Source((root/'generated/encap_wire_forward.S').read_text()).function('ntruplus768_wire_research_forward')
    begin=fwd.index('.Lwire_forward_loop:')
    dispatch=fwd.index('cmpl $0,%ecx')
    next_label=fwd.index('.Lwire_forward_next:')
    end=fwd.index('jne .Lwire_forward_loop')
    path=fwd[:begin]
    for tile in range(6):
        path+=fwd[begin+1:dispatch]
        for j in range(min(tile+1,5)):
            path += [f'cmpl ${j},%ecx',f'je .Lwire_terminal_{j}']
        if tile==5:
            path+=['jmp .Lwire_terminal_5']
        at=fwd.index(f'.Lwire_terminal_{tile}:')
        stop=next(i for i in range(at+1,len(fwd)) if fwd[i]=='jmp .Lwire_forward_next')
        path+=fwd[at+1:stop+1]+fwd[next_label+1:end+1]
    path+=fwd[end+1:]
    codec=Source((root/'generated/encap_wire_codec.S').read_text())
    decode=codec.function('ntruplus768_wire_research_decode')
    pack=codec.function('ntruplus768_wire_research_pack')
    loop=pack.index('.Lwire_pack_loop:')
    conditional=pack.index('je .Lwire_pack_tail')
    back=pack.index('jmp .Lwire_pack_loop')
    tail=pack.index('.Lwire_pack_tail:')
    pack_path=pack[:loop]+pack[loop+1:back+1]*47+pack[loop+1:conditional+1]+pack[tail+1:]
    return dict(NTT32_terminal=stats(path),decode=stats(decode),pack=stats(pack_path),
                note="existing W source paths reused unchanged; aggregated MulAdd is a separate proposed instruction model")
