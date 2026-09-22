#!/usr/bin/env python3
"""Source-instruction BaseMulScale range closure and executable Yang tail schedule.

No candidate ASM is emitted. Existing immutable ASM is compiled only as oracle.
"""
import ctypes
import hashlib
import json
import random
import re
import subprocess
import tempfile
from collections import Counter
from pathlib import Path

from probe_inverse_ct_gauge import ROOT, Q, RINV, compute
from prove_forward_lanes import signed16, mont_word, barrett_word
from prove_yang_tail import word
from generate_inverse_ct_full import constants


def bounds_op(op, a, b):
    if op == 'vpmullw':
        products=[x*y for x in a for y in b]
        if min(products)>=-32768 and max(products)<=32767:
            return (min(products),max(products))
        if a[0] == a[1] and b[0] == b[1]:
            v = signed16(a[0]*b[0]); return (v,v)
        return (-32768,32767)  # intentional low-word modular product
    products = [x*y for x in a for y in b]
    if op == 'vpmulhw': return (min(products)//65536,max(products)//65536)
    if op == 'vpaddw': return (a[0]+b[0],a[1]+b[1])
    if op == 'vpsubw': return (a[0]-b[1],a[1]-b[0])
    raise ValueError(op)


def arithmetic(op, a, b):
    if op == 'vpmullw': return signed16(a*b)
    if op == 'vpmulhw': return (a*b)//65536
    if op == 'vpmulhrsw': return max(-32768,min(32767,(a*b+16384)>>15))
    v = a+b if op == 'vpaddw' else a-b
    assert -32768 <= v <= 32767, (op,a,b,v)
    return v


def scaled_body(lib, av=None, bv=None):
    """Interpret the actual AT&T source; no formula-level reduction shortcut."""
    src=(ROOT/'upstream/supercop-avx2/basemul.s').read_text().split('poly_basemul_scale:\n')[1]
    lines=[s.split('#')[0].strip() for s in src.splitlines()]
    lines=[s for s in lines if s and not s.startswith('.')]
    labels={s[:-1]:i for i,s in enumerate(lines) if s.endswith(':')}
    interval=av is None; regs={}; ptr={'%rsi':0,'%rdx':0,'%rdi':0}
    csrc=(ROOT/'upstream/supercop-avx2/consts.c').read_text()
    zeta=[int(x) for x in re.findall(r'-?\d+',re.search(r'const int16_t zetas\[816\].*?=\s*\{(.*?)\};',csrc,re.S)[1])]
    assert len(zeta)==816
    out=[None]*768; log=[]; pc=0; carry=False
    def read(s):
        if s.startswith('%ymm'): return regs[s]
        m=re.fullmatch(r'(\w+)\(%rip\)',s)
        if m: vals=[{'_16xq':Q,'_16xqinv':12929}[m[1]]]*16
        else:
            m=re.fullmatch(r'(\d*)\(%r(si|dx|cx)\)',s); assert m,s
            base='%r'+m[2]; off=(ptr[base]+int(m[1] or 0))//2
            if base=='%rcx': vals=zeta[off:off+16]
            elif interval: return [(0,3456)]*16
            else: vals=(av if base=='%rsi' else bv)[off:off+16]
        return [(x,x) for x in vals] if interval else vals
    while pc<len(lines):
        line=lines[pc];pc+=1
        if line.endswith(':'): continue
        op,_,arg=line.partition(' '); args=[a.strip() for a in arg.split(',')]
        if op=='ret': break
        if op=='lea':
            if args[0]=='zetas(%rip)': ptr[args[1]]=0
            else:
                m=re.fullmatch(r'(\d+)\((%r\w+)\)',args[0]);assert m,line
                ptr[args[1]]=ptr[m[2]]+int(m[1])
        elif op=='add': ptr[args[1]]+=int(args[0][1:])
        elif op=='cmp': carry=ptr[args[1]]<ptr[args[0]]
        elif op=='jb':
            if carry: pc=labels[args[0]]+1
        elif op=='vmovdqa':
            if args[1].startswith('%ymm'): regs[args[1]]=read(args[0])[:]
            else:
                m=re.fullmatch(r'(\d*)\(%rdi\)',args[1]);assert m,line
                off=(ptr['%rdi']+int(m[1] or 0))//2
                assert 0<=off<=752
                out[off:off+16]=regs[args[0]][:]
        else:
            assert op in ('vpmullw','vpmulhw','vpaddw','vpsubw'),line
            b,a=read(args[0]),read(args[1])
            v=[bounds_op(op,x,y) if interval else arithmetic(op,x,y) for x,y in zip(a,b)]
            if interval:
                assert all(-32768<=lo<=hi<=32767 for lo,hi in v),(line,v)
                log.append({'instruction':line,'input_byte_offset':ptr['%rsi'],
                            'output_bounds':v,'intentional_low_word_wrap':op=='vpmullw'})
            regs[args[2]]=v
    assert all(x is not None for x in out)
    return out,log


class Program:
    """SSA VEX word program, then last-use physical allocation; no stack."""
    def __init__(self): self.ops=[];self.tables={};self.loops=[];self.monts=0;self.lifetime={}
    def op(self, opcode, *src, **extra):
        dst=None if opcode=='store' else 'v'+str(len(self.ops))
        self.ops.append(dict(op=opcode,src=list(src),dst=dst,**extra));return dst
    def const(self,name,vec):
        assert len(vec)==16
        if name in self.tables: assert self.tables[name]==vec
        self.tables[name]=vec
        return 'const:'+name
    def resident(self,name,vec): return self.op('load',self.const(name,vec))
    def factors(self,name,fs):
        ws=[word(f) for f in fs]
        return self.const(name+'_qinv',[signed16(w*12929) for w in ws]),self.const(name+'_word',ws)
    def mont(self,x,comp,w):
        self.monts+=1
        lo=self.op('vpmullw',x,comp);hi=self.op('vpmulhw',x,w)
        red=self.op('vpmulhw',lo,self.q)
        return self.op('vpsubw',hi,red)
    def load(self,index,version): return self.op('load',f'data:{index}',version=version)
    def store(self,index,x,version): self.op('store',x,address=index,version=version)
    def loop(self,label,start,end,trip,contract):
        self.loops.append(dict(label=label,expanded_start=start,expanded_end=end,trip_count=trip,
                               gpr_contract=contract,alignment=32))
    def allocate(self):
        last={s:i for i,o in enumerate(self.ops) for s in o['src'] if s.startswith('v')}
        for s,end in self.lifetime.items():last[s]=max(last.get(s,0),end)
        live={};peak=0
        for i,o in enumerate(self.ops):
            reads={s:live[s] for s in o['src'] if s.startswith('v')}
            o['read_registers']=reads.copy();o['last_use']=[s for s in reads if last[s]==i]
            for s in o['last_use']:del live[s]
            if o['dst'] is not None:
                free=sorted(set(range(16))-set(live.values()));assert free,(i,o)
                live[o['dst']]=free[0];o['write_register']=free[0]
                peak=max(peak,len(live))
                if o['dst'] not in last:del live[o['dst']]
            o['live_after']=dict(live)
            # Constants have an explicit loop scope even when the last real
            # use is earlier: release only at the public loop boundary.
            for s in list(live):
                if last.get(s)==i:del live[s]
        self.peak=peak
        for loop in self.loops:
            ops=self.ops[loop['expanded_start']:loop['expanded_end']]
            assert len(ops)%8==0
            stride=len(ops)//8
            def signature(block):
                return [(o['op'],list(o['read_registers'].values()),o.get('write_register')) for o in block]
            sig=signature(ops[:stride])
            assert all(signature(ops[i*stride:(i+1)*stride])==sig for i in range(8)),loop['label']
            loop['instruction_rows_per_iteration']=stride
            loop['stable_register_assignment_all_iterations']=True
            loop['body']=ops[:stride]
    def run(self,memory):
        mem=[x[:] for x in memory];versions=['prefix']*48;regs={};ssa={}
        for o in self.ops:
            def read(s):
                if s.startswith('const:'):return self.tables[s[6:]]
                if s.startswith('data:'):
                    idx=int(s[5:]);assert versions[idx]==o['version'];return mem[idx]
                v=regs[o['read_registers'][s]];assert v==ssa[s];return v
            args=[read(s)[:] for s in o['src']]
            if o['op']=='store':
                mem[o['address']]=args[0];versions[o['address']]=o['version'];continue
            if o['op'] in ('load','vpbroadcastd'):v=args[0]
            else:v=[arithmetic(o['op'],a,b) for a,b in zip(*args)]
            regs[o['write_register']]=v;ssa[o['dst']]=v
        assert versions==['final']*48
        return mem

    def range(self,memory):
        mem=[[tuple(x) for x in v] for v in memory];env={};definitions={o['dst']:o for o in self.ops if o['dst']}
        peak=0
        for o in self.ops:
            def read(s):
                if s.startswith('const:'):return [(x,x) for x in self.tables[s[6:]]]
                if s.startswith('data:'):return mem[int(s[5:])]
                return env[s]
            args=[read(s) for s in o['src']]
            if o['op']=='store':mem[o['address']]=args[0];continue
            if o['op'] in ('load','vpbroadcastd'):v=args[0]
            elif o['op']=='vpmulhrsw':
                v=[(max(-32768,min(32767,(min(x*y for x in a for y in b)+16384)>>15)),
                    max(-32768,min(32767,(max(x*y for x in a for y in b)+16384)>>15))) for a,b in zip(*args)]
            else:
                # Exact local correlation for the existing 3-instruction
                # Barrett block, rather than subtract unrelated intervals.
                red=definitions.get(o['src'][1],{}) if o['op']=='vpsubw' else {}
                rnd=definitions.get(red.get('src',[''])[0],{})
                correlated=(red.get('op')=='vpmullw' and red['src'][1]==self.q and
                            rnd.get('op')=='vpmulhrsw' and rnd['src'][0]==o['src'][0] and
                            read(rnd['src'][1])==[(9,9)]*16)
                if correlated:
                    v=[]
                    for lo,hi in args[0]:
                        xs=[x-Q*((x*9+16384)>>15) for x in range(lo,hi+1)]
                        v.append((min(xs),max(xs)))
                    o['range_correlation']='exact Barrett enumeration over input interval'
                else:v=[bounds_op(o['op'],a,b) for a,b in zip(*args)]
            assert all(-32768<=lo<=hi<=32767 for lo,hi in v),(o,v)
            env[o['dst']]=v;o['output_lane_bounds']=v
            if o['op'] in ('vpaddw','vpsubw'):peak=max(peak,max(max(abs(lo),abs(hi)) for lo,hi in v))
        return {'max_add_sub_abs':peak,'output_lane_bounds':mem,
                'max_output_abs':max(max(abs(lo),abs(hi)) for v in mem for lo,hi in v)}


def tail_program(kind):
    p=Program();d=compute();gs=d['stages'][-1]['output_gauges'];rel,_=constants()
    zsrc=(ROOT/'upstream/supercop-avx2/consts.c').read_text()
    zi=[int(x)%Q for x in re.findall(r'-?\d+',re.search(r'const int16_t zetas_inv\[816\].*?=\s*\{(.*?)\};',zsrc,re.S)[1])]
    alpha=[[1,zi[794+8*b]*RINV%Q,zi[798+8*b]*RINV%Q] for b in range(2)]
    n=1679*RINV%Q;phi=zi[810]*RINV%Q
    p.q=p.resident('q',[Q]*16);v=p.resident('barrett_v',[9]*16)
    wc,ww=p.factors('omega',[(-886)*RINV%Q]*16)
    wc=p.op('load',wc);ww=p.op('load',ww)
    for b in range(2):
        start=len(p.ops)
        for i in range(8):
            k=i+24*b; x,y,z=[p.load(k+8*j,'prefix') for j in range(3)]
            vals=[x,y,z]
            for j in range(0 if b else 1,3):
                factors=[gs[k+8*j][l]*pow(gs[i][l],-1,Q)%Q for l in range(16)]
                vals[j]=p.mont(vals[j],*p.factors(f'rel_{k+8*j}',factors))
            x,y,z=vals
            t=p.mont(p.op('vpsubw',y,z),wc,ww)
            s1=p.op('vpsubw',p.op('vpsubw',x,y),t)
            s2=p.op('vpaddw',p.op('vpsubw',x,z),t)
            s0=p.op('vpaddw',p.op('vpaddw',x,y),z)
            red=p.op('vpmulhrsw',s0,v);red=p.op('vpmullw',red,p.q)
            s0=p.op('vpsubw',s0,red)
            for j,s in enumerate((s0,s1,s2)):p.store(k+8*j,s,'r3')
        p.loop(f'r3_half_{b}',start,len(p.ops),8,
               {'data':'rdi = base + 768*b; increment32; offsets0,256,512',
                'constants':f'r10 relative table; increment {192 if b else 128}',
                'control':'r9=end; add data/constant pointers, cmp r9,rdi; jb; public'})
    for s in (v,wc,ww):p.lifetime[s]=len(p.ops)-1
    pc,pw=p.factors('phi',[phi]*16);pc=p.op('load',pc);pw=p.op('load',pw)
    for j in range(3):
        a,b=alpha[0][j],alpha[1][j]
        ratio=None
        if kind=='factored' and j:
            c,w=p.factors(f'ratio{j}',[b*pow(a,-1,Q)%Q]*16)
            ratio=(p.op('vpbroadcastd',c),p.op('vpbroadcastd',w))
        start=len(p.ops)
        for i in range(8):
            k=i+8*j;u=p.load(k,'r3');lo=p.load(k+24,'r3');g=gs[i]
            if kind=='matrix' and j:
                factors=[[n*gg*(1-phi)*a%Q for gg in g],[n*gg*(1+phi)*b%Q for gg in g],
                         [2*n*gg*phi*a%Q for gg in g],[-2*n*gg*phi*b%Q for gg in g]]
                sums=[]
                for out in range(2):
                    uu=p.mont(u,*p.factors(f'matrix{j}_{i}_{2*out}',factors[2*out]))
                    vv=p.mont(lo,*p.factors(f'matrix{j}_{i}_{2*out+1}',factors[2*out+1]))
                    sums.append(p.op('vpaddw',uu,vv))
                upper,lower=sums
            else:
                if ratio:lo=p.mont(lo,*ratio)
                diff=p.op('vpsubw',u,lo);s=p.op('vpaddw',u,lo)
                t=p.mont(diff,pc,pw);s=p.op('vpsubw',s,t)
                upper=p.mont(s,*p.factors(f'final{j}_{i}_up',[n*gg*a%Q for gg in g]))
                lower=p.mont(t,*p.factors(f'final{j}_{i}_lo',[2*n*gg*a%Q for gg in g]))
            p.store(k,upper,'final');p.store(k+24,lower,'final')
        p.loop(f'level0_j{j}',start,len(p.ops),8,
               {'data':f'rdi=base+{256*j}; increment32; offsets0,768',
                'constants':f'r10 table; increment {256 if kind=="matrix" and j else 128}',
                'control':'r9=end; add data/constant pointers, cmp r9,rdi; jb; public'})
        if ratio:
            for s in ratio:p.lifetime[s]=len(p.ops)-1
    for s in (p.q,pc,pw):p.lifetime[s]=len(p.ops)-1
    p.allocate();assert p.monts==144
    return p


def main():
    proof=json.loads((ROOT/'results/yang-tail-proof-20260922.json').read_text())
    for name,digest in proof['source_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,('stale tail proof',name)
    rng=random.Random(20260923)
    with tempfile.TemporaryDirectory(prefix='yang-closure-') as td:
        libpath=Path(td)/'anchor.so'
        objects=[]
        for source in ('basemul.s','pack.s','consts.c'):
            obj=Path(td)/(Path(source).stem+'.o');objects.append(str(obj))
            # Stable object basenames prevent the driver's random temporary
            # names entering STT_FILE symbols and changing the anchor ELF hash.
            subprocess.run(['cc','-c','-fPIC','-mavx2','-o',str(obj),str(ROOT/'upstream/supercop-avx2'/source)],check=True,capture_output=True)
        subprocess.run(['cc','-shared','-o',str(libpath),*objects],check=True,capture_output=True)
        lib=ctypes.CDLL(str(libpath));bufs=[]
        anchor_sha256=hashlib.sha256(libpath.read_bytes()).hexdigest()
        for _ in range(4):
            buf=ctypes.create_string_buffer(1536+31);ptr=(ctypes.addressof(buf)+31)&~31
            bufs.append((buf,ptr,(ctypes.c_int16*768).from_address(ptr)))
        f=lib.poly_basemul_scale;f.argtypes=[ctypes.c_void_p]*3
        decode=lib.poly_frombytes;decode.argtypes=[ctypes.c_void_p,ctypes.c_void_p];decode.restype=ctypes.c_int
        out,ledger=scaled_body(lib)
        assert max(max(abs(a),abs(b)) for a,b in out)<=7644
        csrc=(ROOT/'upstream/supercop-avx2/consts.c').read_text()
        zeta=[int(x) for x in re.findall(r'-?\d+',re.search(r'const int16_t zetas\[816\].*?=\s*\{(.*?)\};',csrc,re.S)[1])]
        for block in range(6):
            off=624+32*block
            assert all(signed16(zeta[off+16+l]*12929)==zeta[off+l] for l in range(16))
        for i in range(1003):
            a=[rng.randrange(Q) for _ in range(768)];b=[rng.randrange(Q) for _ in range(768)]
            if i<3:a=[(0,3456,1)[i]]*768;b=a[:]
            model,_=scaled_body(lib,a,b)
            bufs[0][2][:]=a;bufs[1][2][:]=b
            f(bufs[2][1],bufs[0][1],bufs[1][1]);assert model==list(bufs[2][2])
            assert all(lo<=v<=hi for v,(lo,hi) in zip(model,out))
            # Independent quartic convolution, not the machine's schedule.
            for tile in range(12):
                for lane in range(16):
                    lam=zeta[624+32*(tile//2)+16+lane]*RINV%Q
                    if tile%2:lam=-lam%Q
                    aa=[a[64*tile+16*j+lane] for j in range(4)]
                    bb=[b[64*tile+16*j+lane] for j in range(4)]
                    for j in range(4):
                        val=sum(aa[u]*bb[v]*(lam if u+v>=4 else 1) for u in range(4) for v in range(4) if (u+v)%4==j)*RINV%Q
                        assert model[64*tile+16*j+lane]%Q==val
        # Every 12-bit value, broadcast throughout the external wire, checks
        # acceptance and all decoded slots independent of physical permutation.
        for x in range(4096):
            packet=bytes((x&255,((x>>8)|((x&15)<<4)),x>>4))*384
            raw=ctypes.create_string_buffer(packet)
            rc=decode(bufs[3][1],ctypes.addressof(raw))
            assert bool(rc)==(x>=Q)
            if not rc:assert list(bufs[3][2])==[x]*768
        for index in range(768):
            for x in (3456,3457,4095):
                coeff=[0]*768;coeff[index]=x;packet=bytearray()
                for j in range(0,768,2):
                    a,b=coeff[j:j+2];packet.extend((a&255,(a>>8)|((b&15)<<4),b>>4))
                raw=ctypes.create_string_buffer(bytes(packet))
                rc=decode(bufs[3][1],ctypes.addressof(raw));assert bool(rc)==(x>=Q)
                if not rc:
                    values=list(bufs[3][2]);assert max(values)==x and all(0<=v<Q for v in values)
    programs={k:tail_program(k) for k in ('matrix','factored')}
    from prove_inverse_ct_range import repaired_replay
    prefix=repaired_replay(7644,compute())['stages'][-1]['per_vector_max_abs_bound']
    schedule_ranges={k:p.range([[(-b,b)]*16 for b in prefix]) for k,p in programs.items()}
    cases=0
    for trial in range(160):
        memory=[[0]*16 for _ in range(48)];expected={k:[[0]*16 for _ in range(48)] for k in programs}
        for row in proof['lanes']:
            i,l=row['cohort'],row['lane'];indices=row['physical_vectors'];g=row['paired_gauge']
            # Use prefix bounds, not already-normalized radix3 bounds.
            vals=[rng.randint(-prefix[k],prefix[k]) for k in indices]
            if trial<64:vals=[prefix[k]*(1 if trial>>j&1 else -1) for j,k in enumerate(indices)]
            for k,x in zip(indices,vals):memory[k][l]=x
            triples=[]
            for b in range(2):
                xyz=[vals[3*b+j] if b==0 and j==0 else mont_word(vals[3*b+j],word(row['gauges'][3*b+j]*pow(g,-1,Q)%Q)) for j in range(3)]
                x,y,z=xyz;t=mont_word(y-z,word(proof['omega']))
                triples.append([barrett_word(x+y+z),x-y-t,x-z+t])
            for j in range(3):
                u,v=triples[0][j],triples[1][j];a,b=row['alpha'][0][j],row['alpha'][1][j]
                phi,n=proof['phi'],proof['nscale']
                for kind in programs:
                    def m(x,f):return mont_word(x,word(f%Q))
                    if kind=='matrix' and j:
                        c=row['matrix_constants_j1_j2'][j-1]
                        res=[m(u,c[0])+m(v,c[1]),m(u,c[2])+m(v,c[3])]
                    else:
                        vv=m(v,b*pow(a,-1,Q)) if j else v
                        t=m(u-vv,phi);res=[m(u+vv-t,n*g*a),m(t,2*n*g*a)]
                    expected[kind][i+8*j][l]=res[0];expected[kind][i+24+8*j][l]=res[1]
        for kind,p in programs.items():assert p.run(memory)==expected[kind]
        cases+=1
    result={'kind':'source_instruction_interval_proof_and_executable_schedule_not_new_linked_ASM',
            'existing_anchor_ELF_sha256':anchor_sha256,
            'BaseMulScale':{'input':[0,3456],'output_lane_bounds':out,'instruction_ledger':ledger,
                            'maximum_abs':max(max(abs(a),abs(b)) for a,b in out),
                            'raw_machine_cases':1003,'independent_quartic_oracle_cases':1003,'decoder_values_checked':4096,'decoder_single_position_cases':2304,
                            'scope':'all canonically decoded CT and f, including canonical invalid keys/ciphertexts; invalid encodings return before arithmetic'},
            'tail':{},'full_tail_cases_per_variant':cases,'proof_dependency_sha256':hashlib.sha256((ROOT/'results/yang-tail-proof-20260922.json').read_bytes()).hexdigest()}
    for kind,p in programs.items():
        # Ratio words/companions are 4-byte duplicated-int16 broadcast sources,
        # packed into one aligned 32-byte block; other entries are full YMMs.
        ratio_names=[name for name in p.tables if name.startswith('ratio')]
        assert all(len(set(p.tables[name]))==1 for name in ratio_names)
        table_bytes=32*(len(p.tables)-len(ratio_names))+(32 if ratio_names else 0)
        table_layout={};offset=0
        for name in p.tables:
            if name not in ratio_names:
                table_layout[name]={'offset':offset,'bytes':32,'alignment':32};offset+=32
        for name in ratio_names:
            table_layout[name]={'offset':offset,'bytes':4,'alignment':4,
                                'int16_payload':[p.tables[name][0]]*2};offset+=4
        assert (offset+31)//32*32==table_bytes
        # Each expanded iteration must be encodable by the SAME compact body:
        # identical registers, data offset +32, constant cursor +128/192/256.
        for loop in p.loops:
            count=loop['instruction_rows_per_iteration'];start=loop['expanded_start']
            first=p.ops[start:start+count]
            const_names=[s[6:] for o in first for s in o['src'] if s.startswith('const:')]
            stride=32*len(const_names)
            for it in range(8):
                for a,b in zip(first,p.ops[start+it*count:start+(it+1)*count]):
                    for x,y in zip(a['src'],b['src']):
                        if x.startswith('data:'):assert int(y[5:])==int(x[5:])+it
                        if x.startswith('const:'):assert table_layout[y[6:]]['offset']==table_layout[x[6:]]['offset']+it*stride
                    if a['op']=='store':assert b['address']==a['address']+it
            loop['constant_cursor_stride_bytes']=stride
            loop['address_replay_all_iterations']=True
            loop['gpr_setup_instructions']=['lea data_group(%r8),%rdi','lea 256(%rdi),%r9','lea table_group(%rip),%r10']
            loop['gpr_body_instructions']=[f'add ${stride},%r10','add $32,%rdi','cmp %r9,%rdi','jb loop_label']
        result['tail'][kind]={'peak_YMM':p.peak,'montgomery_chains':p.monts,'full_inverse_chains':p.monts+78,
                             'range':schedule_ranges[kind],
                             'opcode_counts':dict(Counter(o['op'] for o in p.ops)),
                             'constant_operands':sum(s.startswith('const:') for o in p.ops for s in o['src']),
                             'constant_bytes':table_bytes,'table_layout':table_layout,'broadcast_table_names':ratio_names,'loops':p.loops,'operations':p.ops,'tables':p.tables,
                             'gpr_control_dynamic_instructions':177,
                             'gpr_control_accounting':'mov rdi,r8 once + 3 setup per loop + 4 per iteration * 40 + ret; no callee-saved GPR',
                             'alignment':32,'scratch':'existing 1536-byte in-place state; no new array',
                             'memory_versions':'prefix -> r3 -> final; all reads checked before overwrite',
                             'gpr_loop_lowering':'public pointer schedule specified; instruction encodings and linked execution not tested'}
    sources=[Path(__file__),*[ROOT/'tools'/f for f in ('prove_yang_tail.py','prove_inverse_ct_range.py','probe_inverse_ct_gauge.py','generate_inverse_ct_full.py','prove_forward_lanes.py')],*[ROOT/'upstream/supercop-avx2'/f for f in ('basemul.s','pack.s','kem.c','consts.c')]]
    result['source_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    path=ROOT/'results/yang-closure-schedule-20260923.json';path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'caller_bound':result['BaseMulScale']['maximum_abs'],'tail':{k:{x:v[x] for x in ('peak_YMM','montgomery_chains','constant_operands','constant_bytes')} for k,v in result['tail'].items()}},indent=2))


if __name__=='__main__':main()
