#!/usr/bin/env python3
"""Same-DAG frontend/D16/D8 register allocation with explicit boundary homes.

Expand the reachable clean macros into SSA. Reorder independent instructions,
allocate 16 YMM registers, and materialize only named frontend/radix boundaries
in the existing 1536-byte scratch. No arithmetic recomputation or stack spill.
This is a bounded constructive search, NOT an impossibility proof.
"""
import collections
import hashlib
import itertools
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CLEAN = ROOT.parent.parent / "clean/avx2-gt32-clean"
REG = re.compile(r"%ymm\d+")


def macros(text):
    result = {}
    for m in re.finditer(r"(?m)^\s*\.macro (\w+)([^\n]*)\n(.*?)^\s*\.endm", text, re.S):
        result[m[1]] = ([x.strip() for x in m[2].strip().split(',') if x.strip()], m[3])
    return result


def expand(line, definitions):
    line = line.strip()
    if not line:
        return []
    op, *rest = line.split(None, 1)
    if op not in definitions:
        return [line]
    params, body = definitions[op]
    args = [x.strip() for x in rest[0].split(',')] if rest else []
    assert len(params) == len(args), (op, params, args)
    mapping = dict(zip(params, args))
    body = re.sub(r"\\(\w+)", lambda m: mapping[m[1]], body)
    return [s for row in body.splitlines() for s in expand(row, definitions)]


class DAG:
    def __init__(self):
        self.nodes = []
        self.regs = {}
        self.home = {}
        self.stage = {}

    def add(self, text, packet, region):
        op, args = text.split(None, 1)
        args = [s.strip() for s in args.split(',')]
        # Every selected instruction has one vector destination or is a store.
        output = bool(REG.fullmatch(args[-1]))
        ins = args[:-1] if output else args
        deps = [self.regs[r] for s in ins for r in REG.findall(s)]
        rendered = [REG.sub(lambda m: f"@{self.regs[m[0]]}@", s) for s in ins]
        idx = len(self.nodes)
        if output:
            if op in ('vmovdqa', 'vmovdqu') and len(deps) == 1 and REG.fullmatch(ins[0]):
                self.regs[args[-1]] = deps[0]
                return deps[0]
            self.regs[args[-1]] = idx
            rendered.append(f"@{idx}@")
        self.nodes.append({'op': op, 'args': rendered, 'deps': deps, 'out': output,
                           'packet': packet, 'region': region})
        return idx


def make_dag(selected, order, ftext, ctext):
    defs = macros(ftext[:ftext.index('.globl ntruplus768_ntt_frontend_avx2')])
    d = DAG()
    q = d.add('vmovdqa .Lwf_f_tile4_q(%rip), %ymm15', -1, 'constant')
    produced = {}
    for ordinal, packet in enumerate(order):
        d.regs = {'%ymm15': q}
        rot = packet % 3
        regs = [f'%ymm{(j+rot)%3}' for j in range(3)]
        regs += [f'%ymm{3+(j+rot)%3}' for j in range(3)]
        lines = expand('FRONTEND_WIDE_ITER_BODY '+str(32*packet)+','+','.join(regs), defs)
        for line in lines:
            if line.startswith('addq'):
                continue
            line = line.replace('.L', '.Lwf_f_')
            line = re.sub(r'([\d+]+)\(%rsi\)',
                          lambda m: f'{sum(map(int,m[1].split("+")))}(%r9)', line)
            for ptr, table in (('rdx','qinv'), ('rcx','factor')):
                line = re.sub(r'([\d+]+)\(%'+ptr+r'\)',
                              lambda m: '.Lwf_f_tile4_frontend_wide_twist_'+table+'+'
                              +str(192*packet+sum(map(int,m[1].split('+'))))+'(%rip)', line)
            if re.match(r'vmovdqu %ymm\d+,', line):
                src, offset = re.fullmatch(r'vmovdqu (%ymm\d+), (\d+)\(%rdi\)', line).groups()
                tile = int(offset)//256
                value = d.regs[src]
                produced[tile, packet] = value
                d.home[value] = 256*tile+32*packet
                d.stage[value] = 'frontend'
                if tile not in selected:
                    d.add(f'vmovdqu {src}, {d.home[value]}(%rdx)', ordinal, 'frontend-store')
            else:
                d.add(line, ordinal, 'frontend')
    for tile in selected:
        vals = {j: produced[tile,j] for j in range(8)}
        for j in range(4):
            d.regs = {'%ymm0':vals[j], '%ymm1':vals[j+4]}
            plus = d.add('vpaddw %ymm1, %ymm0, %ymm2', -1, 'D16')
            minus = d.add('vpsubw %ymm1, %ymm0, %ymm3', -1, 'D16')
            vals[j], vals[j+4] = plus, minus
            for k,v in ((j,plus),(j+4,minus)):
                d.home[v] = 256*tile+32*k
                d.stage[v] = 'D16'
        d8 = {}
        for pair, (a,b) in enumerate(((0,2),(1,3),(4,6),(5,7))):
            d.regs = {'%ymm0':vals[a], '%ymm1':vals[b], '%ymm15':q}
            off = 32*pair
            lines = [f'vpmullw .Lwf_c_tile4_fwd_s2_qinv+{off}(%rip), %ymm1, %ymm2',
                     f'vpmulhw .Lwf_c_tile4_fwd_s2_factor+{off}(%rip), %ymm1, %ymm3',
                     'vpmulhw %ymm15, %ymm2, %ymm2', 'vpsubw %ymm2, %ymm3, %ymm3',
                     'vpaddw %ymm3, %ymm0, %ymm4', 'vpsubw %ymm3, %ymm0, %ymm5']
            for line in lines:
                d.add(line, -1, 'D8')
            for reg,k in (('%ymm4',a),('%ymm5',b)):
                v = d.regs[reg]
                d8[k] = v
                d.home[v] = 256*tile+32*k
                d.stage[v] = 'D8'
        # Keep the frozen D4/D2/D1 suffix, but allow it to consume the ready
        # D8 values. Otherwise eight D8 stores merely replace eight frontend
        # stores and no materialization has actually disappeared.
        d.regs = {f'%ymm{k}':d8[k] for k in range(8)}
        d.regs['%ymm15'] = q
        d.add('vmovdqa .Lwf_c_fr_plane_pshufb(%rip), %ymm14', -1, 'terminal-constant')
        body = ctext.split('.Lfr_core_loop:\n',1)[1].split(' addq $256, %rsi',1)[0]
        start = body.index(' FR_MONT_CROSS4 %ymm0,%ymm1')
        for line in body[start:].splitlines():
            for s in expand(line, macros(ctext)):
                s = s.replace('.L','.Lwf_c_')
                s = re.sub(r'([\d+]+)\(%rdi\)',lambda m:
                           str(256*tile+sum(map(int,m[1].split('+'))))+'(%rdi)',s)
                d.add(s, -1, 'terminal')
    return d


def allocate(d, policy=0):
    nodes = d.nodes
    users = collections.defaultdict(list)
    for i,n in enumerate(nodes):
        for v in set(n['deps']):
            users[v].append(i)
    remaining = {v:len(us) for v,us in users.items()}
    pending = set(range(len(nodes)))
    done, live, stored = set(), {}, {}
    output, trace = [], []
    peak = 0
    extra_stores = extra_loads = 0
    memory_owner = {}
    while pending:
        packet = min((nodes[i]['packet'] for i in pending if nodes[i]['packet'] >= 0), default=8)
        ready = [i for i in pending if nodes[i]['packet'] <= packet
                 and all(x in done for x in nodes[i]['deps'])]
        assert ready
        def cost(i):
            n = nodes[i]
            deps = set(n['deps'])
            need = len(deps-live.keys())
            kills = sum(remaining[x] == 1 for x in deps)
            net = need + int(n['out']) - kills
            # Prefer ready consumer work; alternatively minimize live growth first.
            consumer = 0 if n['region'].startswith('D') else 1
            return (net, consumer, i) if policy == 0 else (consumer, net, i)
        ready.sort(key=cost)
        chosen = None
        for i in ready:
            n = nodes[i]; deps = set(n['deps'])
            count = len(live) + len(deps-live.keys())
            if count <= 16 and count+int(n['out'])-sum(remaining[x] == 1 for x in deps) <= 16:
                chosen = i; break
        if chosen is None:
            # Explicitly price a legal boundary home; never spill a multiply temporary.
            choices = [v for v in live if v in d.home and remaining.get(v,0)]
            if not choices:
                return {'feasible':False, 'reason':'bounded allocator blocked', 'at':len(output)}
            choices.sort(key=lambda v: (min(users[v]),v), reverse=True)
            v = choices[0]; addr = d.home[v]
            old = memory_owner.get(addr)
            if old is not None and old != v and old not in live and remaining.get(old,0):
                return {'feasible':False, 'reason':'home overwrite while old value live'}
            if stored.get(v) != addr or memory_owner.get(addr) != v:
                output.append(f'vmovdqu %ymm{live[v]}, {addr}(%rdx)')
                extra_stores += 1
                stored[v] = addr; memory_owner[addr] = v
            del live[v]
            continue
        i = chosen; n = nodes[i]; deps = set(n['deps'])
        for v in sorted(deps-live.keys()):
            assert v in stored and memory_owner[stored[v]] == v
            reg = min(set(range(16))-set(live.values()))
            live[v] = reg
            output.append(f'vmovdqu {stored[v]}(%rdx), %ymm{reg}')
            extra_loads += 1
        peak = max(peak,len(live))
        before = dict(live)
        for v in deps:
            remaining[v] -= 1
            if remaining[v] == 0:
                del live[v]
        if n['out']:
            reg = min(set(range(16))-set(live.values()))
            live[i] = reg
            before[i] = reg
        operands = [re.sub(r'@(\d+)@',lambda m:f'%ymm{before[int(m[1])]}',s) for s in n['args']]
        # Audit every scratch write against pending materialized values.
        if not n['out'] and '(%rdx)' in operands[-1]:
            addr = int(re.fullmatch(r'(\d+)\(%rdx\)',operands[-1])[1])
            old = memory_owner.get(addr)
            assert old is None or old in live or not remaining.get(old,0), (i,addr,old)
            memory_owner[addr] = None
        output.append(n['op']+' '+', '.join(operands))
        peak = max(peak,len(live))
        trace.append({'node':i,'instruction':len(output)-1,'region':n['region'],
                      'live_after':dict(live)})
        pending.remove(i); done.add(i)
    assert not live, live
    return {'feasible':True,'peak_ymm':peak,'extra_boundary_stores':extra_stores,
            'extra_boundary_reloads':extra_loads,'instructions':output,'def_use_trace':trace}


def terminal(ctext, selected):
    defs = macros(ctext)
    body = ctext.split('.Lfr_core_loop:\n',1)[1].split(' addq $256, %rsi',1)[0]
    result = ['vmovdqa .Lwf_c_fr_q(%rip), %ymm15',
              'vmovdqa .Lwf_c_fr_plane_pshufb(%rip), %ymm14']
    for tile in range(6):
        if tile in selected:
            continue
        for line in body.splitlines():
            if tile in selected and (line.strip().startswith('FR_RAW_CROSS4') or
                                    ' .Ltile4_fwd_s2_qinv,' in line):
                continue
            for expanded in expand(line, defs):
                expanded = expanded.replace('.L','.Lwf_c_')
                expanded = re.sub(r'([\d+]+)\(%rsi\)', lambda m:
                                 str(256*tile+sum(map(int,m[1].split('+'))))+'(%rdx)',expanded)
                expanded = re.sub(r'([\d+]+)\(%rdi\)', lambda m:
                                 str(256*tile+sum(map(int,m[1].split('+'))))+'(%rdi)',expanded)
                result.append(expanded)
    return result


def main():
    ftext = (CLEAN/'ntt.s').read_text(); ctext = (CLEAN/'ntt_m.s').read_text()
    orders = [list(range(8)),[0,4,1,5,2,6,3,7],[0,4,2,6,1,5,3,7]]
    records = []; candidates = []
    for width in (1,2):
        best = None
        for tiles, order, policy in itertools.product(itertools.combinations(range(6),width),orders,range(2)):
            d = make_dag(tiles,order,ftext,ctext)
            a = allocate(d,policy)
            record = {'tiles':tiles,'packet_order':order,'policy':policy,
                      **{k:v for k,v in a.items() if k not in ('instructions','def_use_trace')}}
            if a['feasible']:
                ins = a['instructions']+terminal(ctext,tiles)
                loads = sum(bool(re.match(r'vmovdq[au] \d+\(%r(?:9|dx)\),',s)) for s in ins)
                stores = sum(bool(re.match(r'vmovdq[au] %ymm\d+, \d+\(%r(?:di|dx)\)',s)) for s in ins)
                record.update(data_loads=loads,data_stores=stores,
                              memory_delta=loads+stores-192,instructions=len(ins))
                rank = (loads+stores,len(ins),tiles,order,policy)
                if best is None or rank < best[0]:
                    best = (rank,record,ins,a['def_use_trace'])
            records.append(record)
        if best:
            candidates.append(best)
    generated = ROOT/'generated'
    report = {'schema':'ntruplus768-encap-wavefront-v1','search_kind':'bounded constructive allocation',
              'control':{'data_loads':96,'data_stores':96,'boundary_bytes':1536},
              'records':records,'selected':[],
              'source_sha256':{p:hashlib.sha256((CLEAN/p).read_bytes()).hexdigest() for p in ('ntt.s','ntt_m.s')}}
    for num, (_,record,ins,trace) in enumerate(candidates,1):
        symbol = f'ntruplus768_exp_encap_wavefront_{num}'
        record = dict(record, symbol=symbol)
        report['selected'].append(record)
        # out=rdi, immutable coefficients=rsi, existing scratch=rdx.
        source = ['/* Generated same-DAG wavefront; do not edit. */','.text','.p2align 5',
                  f'.globl {symbol}',f'.type {symbol},@function',symbol+':','movq %rsi, %r9']
        source += ins+['vzeroupper','ret',f'.size {symbol},.-{symbol}']
        for text,prefix in ((ftext,'f'),(ctext,'c')):
            rodata = text[text.index('.section .rodata'):].split('.section .note.GNU-stack')[0]
            source.append(rodata.replace('.L',f'.Lwf_{prefix}_'))
        source.append('.section .note.GNU-stack,"",@progbits')
        (generated/f'encap_wavefront_{num}.s').write_text('\n'.join(source)+'\n')
        (generated/f'encap_wavefront_{num}_def_use.json').write_text(json.dumps(trace,indent=2)+'\n')
    (generated/'tile4_encap_wavefront_search.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['selected'],indent=2))


if __name__ == '__main__':
    main()
