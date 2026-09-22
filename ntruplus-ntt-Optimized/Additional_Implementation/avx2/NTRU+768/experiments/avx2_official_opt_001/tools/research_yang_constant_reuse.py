#!/usr/bin/env python3
"""Gauge-anchor census and executable shared-finalizer model; no new ASM."""
import hashlib
import itertools
import json
import random
import re
from collections import Counter
from pathlib import Path

from close_yang_contract import ROOT, tail_program
from audit_yang_followup import allocate, paired_schedule, prefix_bounds, range_result
from probe_inverse_ct_gauge import Q, compute
from prove_inverse_ct_range import repaired_replay


def remap(p, new, before):
    for l in p.loops:
        l['expanded_start']=before[l['expanded_start']]
        l['expanded_end']=before[l['expanded_end']]
    p.lifetime={s:before[e+1]-1 for s,e in p.lifetime.items()}
    p.ops=new
    allocate(p)
    return p


def drop_upper_barrett(p):
    remove=set();replacements={};site=0
    for i,o in enumerate(p.ops):
        if o['op']!='vpmulhrsw':continue
        if site<8:
            mul,sub=p.ops[i+1:i+3]
            assert sub['src']==[o['src'][0],mul['dst']]
            remove.update((i,i+1,i+2));replacements[sub['dst']]=o['src'][0]
        site+=1
    new=[];before=[]
    for i,o in enumerate(p.ops):
        before.append(len(new))
        if i not in remove:
            o['src']=[replacements.get(s,s) for s in o['src']];new.append(o)
    before.append(len(new))
    return remap(p,new,before)


def shared_finalizer():
    p=tail_program('factored');original=p.ops;new=[];before=[]
    cache={};replace={}
    lower_outputs={o['src'][0] for o in original
                   if o['op']=='store' and o['version']=='final' and o['address']>=24}
    for o in original:
        before.append(len(new))
        for s in o['src']:
            m=re.fullmatch(r'const:(final\d_\d+)_up_qinv',s)
            if not m:continue
            key=m[1]
            if key not in cache:
                assert all((lo-2*up)%Q==0 for lo,up in
                           zip(p.tables[key+'_lo_word'],p.tables[key+'_up_word']))
                cache[key]={}
                for part in ('qinv','word'):
                    value='v_share_'+key+'_'+part
                    new.append({'op':'load','src':['const:'+key+'_up_'+part],'dst':value})
                    cache[key][part]=value
        src=[]
        for s in o['src']:
            m=re.fullmatch(r'const:(final\d_\d+)_(?:up|lo)_(qinv|word)',s)
            src.append(cache[m[1]][m[2]] if m else replace.get(s,s))
        o['src']=src;new.append(o)
        if o['dst'] in lower_outputs:
            value='v_double_'+o['dst']
            new.append({'op':'vpaddw','src':[o['dst'],o['dst']],'dst':value})
            replace[o['dst']]=value
    before.append(len(new))
    # Lower result now uses 2*Mont(T,K), not Mont(T,2K). Both have e=0.
    for name in list(p.tables):
        if re.fullmatch(r'final\d_\d+_lo_(qinv|word)',name):del p.tables[name]
    p=remap(p,new,before)
    p=paired_schedule(p)
    return drop_upper_barrett(p)


def gauge_search(data):
    gauges=data['stages'][-1]['output_gauges'];a=[1,867,1520];b=[1,3091,2590]
    rows=[]
    scale=lambda v,c:tuple(x*c%Q for x in v)
    for i in range(8):
        upper=[tuple(gauges[i+8*j]) for j in range(3)]
        lower=[tuple(gauges[i+24+8*j]) for j in range(3)]
        cu=set(upper);cl=set(lower)
        for j in range(3):
            cu.update(scale(v,b[j]*pow(a[j],-1,Q)%Q) for v in lower)
            cl.update(scale(v,a[j]*pow(b[j],-1,Q)%Q) for v in upper)
        best=99;solutions=[]
        for u,l in itertools.product(cu,cl):
            pre=sum(v!=u for v in upper)+sum(v!=l for v in lower)
            post=sum(scale(u,a[j])!=scale(l,b[j]) for j in range(3))
            if pre+post<best:best=pre+post;solutions=[]
            if pre+post==best:solutions.append({'pre':pre,'post':post,'upper':u,'lower':l})
        rows.append({'cohort':i,'minimum_chains':best,'solutions':solutions,
                     'candidate_pairs':len(cu)*len(cl)})
    return {'cohorts':rows,'total_minimum':sum(x['minimum_chains'] for x in rows),
      'scope':'fixed radix3 formulas, whole-vector identity-only omissions; no sign/routing/prefix changes',
      'completeness':'For cost <7, either pre<=3 (impossible: each triple has distinct gauges), '
        'or pre=4 and post<=2 (both input anchors enumerated), or pre=5 and post<=1 '
        '(one input anchor and each post-identity partner enumerated); pre>=6 has post>=2 '
        'because the three alpha ratios are distinct. No global arithmetic lower bound.'}


def main():
    data=compute();bounds,_=prefix_bounds(data,repaired_replay(7644,data)['plan'])
    control=drop_upper_barrett(paired_schedule(tail_program('factored')))
    p=shared_finalizer();ranges=range_result(p,bounds)
    assert ranges['status']=='proved_safe' and ranges['max_output_abs']<=4288
    rng=random.Random(222344);raw_different=0
    for trial in range(160):
        memory=[[hi if trial<64 and trial>>(k//8)&1 else lo if trial<64
                 else rng.randint(lo,hi) for lo,hi in vec] for k,vec in enumerate(bounds)]
        ref,out=control.run(memory),p.run(memory)
        for av,bv in zip(ref,out):
            for x,y in zip(av,bv):
                assert (x-y)%Q==0
                raw_different+=x!=y
    def ledger(program):
        ops=Counter(o['op'] for o in program.ops)
        return {'tail_montgomery':program.monts,'full_inverse_montgomery':78+program.monts,
          'tail_barrett':ops['vpmulhrsw'],'full_inverse_barrett':24+ops['vpmulhrsw'],
          'constant_memory_operands':sum(s.startswith('const:') for o in program.ops for s in o['src']),
          'data_loads':sum(o['op']=='load' and o['src'][0].startswith('data:') for o in program.ops),
          'data_stores':ops['store'],'vector_instruction_rows':len(program.ops),
          'peak_YMM':program.peak,'opcodes':dict(ops),
          'final_constant_vectors':sum(n.startswith('final') for n in program.tables)}
    prefix=[]
    unique_prefix=set()
    for stage in data['stages']:
        tw=stage['twiddles'];first=tw[:4]
        assert all(tw[4*k:4*k+4]==first for k in range(6))
        unique_prefix.update(tuple(v) for v in first if v!=[1]*16)
        prefix.append({'stage':stage['stage'],'repeated_across_six_packets':True,
          'pair_factors':first,'unique_nonidentity_vectors':len(set(tuple(v) for v in first if v!=[1]*16))})
    # Existing stage5 pair2 and pair3 consume equal constants without clobber
    # of ymm15/ymm2 between them; this is a 12-load opportunity, not a benchmark.
    asm=(ROOT/'asm/ntruplus768_officialopt_invntt_yang_pair32.s').read_text()
    stored=[]
    for line in asm.split('yang_pair32_stage5:\n')[1].split('yang_pair32_stage4:')[0].splitlines():
        line=line.strip()
        if line.startswith('.short '):stored.extend(map(int,line[7:].split(',')))
    assert len(stored)==6*4*32
    for packet in range(6):
        base=packet*4*32
        assert stored[base+2*32:base+3*32]==stored[base+3*32:base+4*32]
    stage5=asm.split('# CT stage 5:')[1].split('#shuffle')[0]
    lo=stage5.index('vmovdqa 160(%r10), %ymm2')+len('vmovdqa 160(%r10), %ymm2')
    hi=stage5.index('vmovdqa 192(%r10), %ymm15')
    assert not re.search(r',\s*%ymm(?:15|2)\s*$',stage5[lo:hi],re.M)
    assert data['stages'][1]['twiddles'][2]==data['stages'][1]['twiddles'][3]
    lc,lp=ledger(control),ledger(p)
    assert lp['constant_memory_operands']==lc['constant_memory_operands']-48
    assert lp['full_inverse_montgomery']==222 and lp['full_inverse_barrett']==32
    result={'class':'research_model_not_ASM_or_cycle_evidence','control':'yang_pair32',
      'prefix_reuse':prefix,'stage5_same_packet_reuse':{'removed_loads_per_call':12,
        'registers':['ymm15','ymm2'],'extra_registers':0,'arithmetic_change':False,
        'status':'source def/use and constant identity pass; not linked candidate'},
      'prefix_table_compaction':{'existing_allocated_bytes':7680,
        'currently_referenced_nonidentity_bytes':78*64,
        'distinct_nonidentity_factor_pairs':len(unique_prefix),
        'simple_deduplicated_bytes':len(unique_prefix)*64,
        'runtime_load_operand_delta_from_dedup_alone':0,
        'status':'exact factor-vector census, addressing/linked realization unimplemented'},
      'gauge_anchor_search':gauge_search(data),
      'shared_finalizer':{'identity':'Mont(T,2K) mod q = 2*Mont(T,K) mod q; e unchanged',
        'control_ledger':lc,'candidate_ledger':lp,'range':ranges,
        'residue_fixtures':160,'raw_different_cells':raw_different,
        'consumer':'inside existing exhaustive crepmod3 +/-4288 domain',
        'operations':p.ops,'loops':p.loops,'tables':p.tables},
      'source_sha256':{str(f.relative_to(ROOT)):hashlib.sha256(f.read_bytes()).hexdigest()
        for f in [Path(__file__),ROOT/'tools/close_yang_contract.py',
                  ROOT/'tools/audit_yang_followup.py',ROOT/'tools/probe_inverse_ct_gauge.py',
                  ROOT/'asm/ntruplus768_officialopt_invntt_yang_pair32.s']}}
    (ROOT/'results/yang-constant-reuse-research.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'control':lc,'shared_finalizer':lp,
      'max_add_sub':ranges['max_add_sub_abs'],'final_bound':ranges['max_output_abs'],
      'gauge_normalization_minimum':result['gauge_anchor_search']['total_minimum'],
      'raw_different_cells':raw_different},indent=2))


if __name__=='__main__':main()
