#!/usr/bin/env python3
"""Combine the authorized two-pair schedule and eight S0 Barrett omissions."""
import hashlib
import json
import random
from pathlib import Path

from close_yang_contract import ROOT, tail_program
from audit_yang_followup import allocate, paired_schedule, prefix_bounds, range_result
from probe_inverse_ct_gauge import compute
from prove_inverse_ct_range import repaired_replay

NAME = 'ntruplus768_officialopt_invntt_yang_pair32'
TABLE = 'yang_pair32_tail_table'


def generate():
    previous=json.loads((ROOT/'results/yang-222-schedule-reduction-audit.json').read_text())
    for name,h in previous['source_sha256'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h,('stale dependency',name)
    control=tail_program('factored');p=paired_schedule(control)
    remove=set();replace={};sites=0
    for i,o in enumerate(p.ops):
        if o['op']!='vpmulhrsw':continue
        mul,sub=p.ops[i+1:i+3]
        assert mul['op']=='vpmullw' and sub['src']==[o['src'][0],mul['dst']]
        if sites<8:
            remove.update((i,i+1,i+2));replace[sub['dst']]=o['src'][0]
        sites+=1
    assert sites==16 and len(remove)==24
    before=[0]
    for i in range(len(p.ops)):before.append(before[-1]+(i not in remove))
    kept=[]
    for i,o in enumerate(p.ops):
        if i not in remove:
            o['src']=[replace.get(s,s) for s in o['src']];kept.append(o)
    p.ops=kept
    for loop in p.loops:
        loop['expanded_start']=before[loop['expanded_start']]
        loop['expanded_end']=before[loop['expanded_end']]
    p.lifetime={s:before[e+1]-1 for s,e in p.lifetime.items()}
    allocate(p)
    data=compute();bounds,_=prefix_bounds(data,repaired_replay(7644,data)['plan'])
    ranges=range_result(p,bounds)
    assert ranges['status']=='proved_safe' and ranges['max_output_abs']<=4288
    assert p.monts==144 and sum(o['op']=='vpmulhrsw' for o in p.ops)==8
    rng=random.Random(22232)
    for trial in range(160):
        memory=[[hi if trial<64 and trial>>(k//8)&1 else lo if trial<64
                 else rng.randint(lo,hi) for lo,hi in vec] for k,vec in enumerate(bounds)]
        ref,out=control.run(memory),p.run(memory)
        assert all((a-b)%3457==0 for av,bv in zip(ref,out) for a,b in zip(av,bv))
    # Retain byte-identical constant data and use the previous verified table
    # layout. The only changed instruction streams are in the allocated tail.
    closure=json.loads((ROOT/'results/yang-closure-schedule-20260923.json').read_text())['tail']['factored']
    assert p.tables==closure['tables']
    layout=closure['table_layout']
    original=ROOT/'asm/ntruplus768_officialopt_invntt_yang_factored.s'
    source=original.read_text();oldname='ntruplus768_officialopt_invntt_yang_factored'
    prefix=source.split(oldname+'_tail:')[0]
    constants=source[source.index('.section .rodata'):]
    def rename(s):
        return s.replace(oldname,NAME).replace('yang_stage','yang_pair32_stage').replace('yang_tail_table',TABLE)
    prefix=rename(prefix);constants=rename(constants)
    lines=[prefix,NAME+'_tail:','mov %rdi,%r8'];vector_lines=[]
    static_loops=[]
    def lower(o,db=None,cb=None):
        def operand(s):
            if s.startswith('v'):return '%ymm'+str(o['read_registers'][s])
            if s.startswith('data:'):return str(32*(int(s[5:])-db))+'(%rdi)'
            off=layout[s[6:]]['offset']
            return f'{off-cb}(%r10)' if cb is not None else f'{TABLE}+{off}(%rip)'
        if o['op']=='store':return f"vmovdqa {operand(o['src'][0])},{32*(o['address']-db)}(%rdi)"
        args=[operand(s) for s in o['src']]
        if len(args)==2:args.reverse()
        return ('vmovdqa' if o['op']=='load' else o['op'])+' '+','.join(args+['%ymm'+str(o['write_register'])])
    loops={l['expanded_start']:l for l in p.loops};i=0
    while i<len(p.ops):
        if i not in loops:
            line=lower(p.ops[i]);lines.append(line);vector_lines.append(line);i+=1;continue
        loop=loops[i];body=loop['body'];trip=loop['trip_count']
        db=min(int(s[5:]) for o in body for s in o['src'] if s.startswith('data:'))
        cb=min(layout[s[6:]]['offset'] for o in body for s in o['src'] if s.startswith('const:'))
        ds=64 if trip==4 else 32
        cs=256 if trip==4 else 192 if loop['label']=='r3_half_1' else 128
        emitted=[lower(o,db,cb) for o in body]
        stride=len(body)
        for t in range(trip):
            iteration=p.ops[i+t*stride:i+(t+1)*stride]
            assert [lower(o,db+t*(ds//32),cb+t*cs) for o in iteration]==emitted
        label='_yang_pair32_'+loop['label']
        lines += [f'lea {db*32}(%r8),%rdi','lea 256(%rdi),%r9',
                  f'lea {TABLE}+{cb}(%rip),%r10','.p2align 5',label+':']
        lines+=emitted;vector_lines+=emitted
        lines += [f'add ${cs},%r10',f'add ${ds},%rdi','cmp %r9,%rdi','jb '+label]
        static_loops.append({'label':label,'trip_count':trip,'data_stride':ds,
                             'constant_stride':cs,'body':emitted})
        i=loop['expanded_end']
    lines+=['ret',f'.size {NAME},.-{NAME}',constants]
    asm=ROOT/'asm'/f'{NAME}.s';asm.write_text('\n'.join(lines)+'\n')
    oldlower=json.loads((ROOT/'results/yang-factored-lowering.json').read_text())
    model={'operations':p.ops,'tables':p.tables,'loops':p.loops,
           'input_lane_bounds':bounds,'range':ranges,'peak_YMM':p.peak}
    result={'name':NAME,'class':'combined range/allocated model and generated ASM, not linked evidence',
       'full_inverse_Montgomery':222,'Barrett_vectors':32,'model_residue_cases':160,
       'tail_vector_instructions':vector_lines,'table_hex':oldlower['table_hex'],
       'loops':static_loops,'tail_model_peak_YMM':p.peak,'model':model,
       'asm_sha256':hashlib.sha256(asm.read_bytes()).hexdigest(),
       'prefix_sha256':hashlib.sha256(prefix.encode()).hexdigest(),
       'source_sha256':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest()
          for f in [Path(__file__),original,ROOT/'tools/audit_yang_followup.py',ROOT/'tools/close_yang_contract.py']}}
    (ROOT/'results/yang-pair32-lowering.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'asm':str(asm),'tail_peak':p.peak,'max_add_sub':ranges['max_add_sub_abs'],
                      'output_bound':ranges['max_output_abs'],'Montgomery':222,'Barrett':32}))


if __name__=='__main__':generate()
