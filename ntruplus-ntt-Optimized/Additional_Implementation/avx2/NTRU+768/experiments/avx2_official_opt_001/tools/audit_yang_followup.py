#!/usr/bin/env python3
"""222-chain schedule and Barrett-removal model gate; no ASM or timing.

Failed intervals are proof insufficiency, never a reachable overflow witness.
Reuse the previously machine-anchored factored SSA and its word semantics.
"""
import copy
import hashlib
import json
import random
from collections import Counter
from pathlib import Path

from close_yang_contract import ROOT, tail_program
from probe_inverse_ct_gauge import compute, route
from prove_inverse_ct_range import repaired_replay, barrett_bound, mont_bound


def allocate(p):
    loops = p.loops
    p.loops = []  # inherited allocator's signature check assumes trip_count=8
    p.allocate()
    p.loops = loops
    for loop in loops:
        rows = p.ops[loop['expanded_start']:loop['expanded_end']]
        trip = loop['trip_count']
        assert len(rows) % trip == 0
        stride = len(rows) // trip
        def sig(block):
            return [(o['op'], list(o['read_registers'].values()),
                     o.get('write_register')) for o in block]
        assert all(sig(rows[i*stride:(i+1)*stride]) == sig(rows[:stride])
                   for i in range(trip)), loop['label']
        loop['instruction_rows_per_iteration'] = stride
        loop['body'] = rows[:stride]


def paired_schedule(control):
    p = copy.deepcopy(control)
    for loop in p.loops:
        if not loop['label'].startswith('level0'): continue
        start, end = loop['expanded_start'], loop['expanded_end']
        old = p.ops[start:end]
        stride = len(old)//8
        rows = []
        for i in range(0, 8, 2):
            a, b = old[i*stride:(i+1)*stride], old[(i+1)*stride:(i+2)*stride]
            # Each stream keeps its full dependency order; disjoint data slots.
            for x, y in zip(a, b): rows.extend((x, y))
        p.ops[start:end] = rows
        loop['trip_count'] = 4
        loop['gpr_contract'] = {'data_stride': 64, 'constant_stride': 256,
                               'mechanism': 'two independent pairs, instruction interleave'}
    allocate(p)
    return p


def without_tail_reductions(control, selected):
    p = copy.deepcopy(control)
    # Match the exact three-instruction Barrett pattern and substitute its
    # result with its already-computed unreduced sum, no replacement multiply.
    remove, replace, sites = set(), {}, []
    for i, op in enumerate(p.ops):
        if op['op'] != 'vpmulhrsw': continue
        mul, sub = p.ops[i+1:i+3]
        assert mul['op']=='vpmullw' and mul['src'][0]==op['dst']
        assert sub['op']=='vpsubw' and sub['src']==[op['src'][0],mul['dst']]
        sites.append(i)
        if len(sites)-1 in selected:
            remove.update((i,i+1,i+2));replace[sub['dst']]=op['src'][0]
    kept=[]
    for i,op in enumerate(p.ops):
        if i not in remove:
            op['src']=[replace.get(s,s) for s in op['src']];kept.append(op)
    p.ops=kept;p.loops=[];p.lifetime={};p.allocate()
    return p


def prefix_bounds(data, plan, omit=None):
    mem=[[7644]*16 for _ in range(48)]
    ledger=[]
    for stage in data['stages']:
        st=stage['stage'];new=[[0]*16 for _ in range(48)]
        for packet in range(6):
            base=packet*8
            for pair in range(4):
                a,b=mem[base+pair][:],mem[base+pair+4][:]
                for side,vec in [('a',a),('b',b)]:
                    if plan[st][pair][side] and (st,packet,pair,side)!=omit:
                        vec[:]=[barrett_bound(x) for x in vec]
                tw=stage['twiddles'][packet*4+pair]
                product=b if tw==[1]*16 else [mont_bound(x,t) for x,t in zip(b,tw)]
                out=[x+y for x,y in zip(a,product)]
                if max(out)>32767:
                    return None, {'stage':st,'packet':packet,'pair':pair,
                                  'lane':out.index(max(out)), 'abs_bound':max(out),
                                  'status':'interval_insufficient_not_overflow_witness'}
                new[base+pair]=out;new[base+pair+4]=out[:]
            if st!=2:
                group=new[base:base+8]
                for pair in range(4):
                    lo,hi=route(st,group[2*pair],group[2*pair+1])
                    new[base+pair]=lo;new[base+pair+4]=hi
        mem=new;ledger.append({'stage':st,'max_abs':max(map(max,mem))})
    return [[(-x,x) for x in v] for v in mem], ledger


def range_result(p, bounds):
    try:
        return {'status':'proved_safe', **p.range(bounds)}
    except AssertionError as exc:
        op, intervals=exc.args[0]
        return {'status':'interval_insufficient_not_overflow_witness',
                'first_op':op['op'], 'dst':op['dst'], 'lane_bounds':intervals}


def main():
    data=compute();plan=repaired_replay(7644,data)['plan']
    bounds,stages=prefix_bounds(data,plan)
    assert bounds is not None
    control=tail_program('factored');paired=paired_schedule(control)
    assert Counter(o['op'] for o in control.ops)==Counter(o['op'] for o in paired.ops)
    assert paired.monts==control.monts==144
    pair_range=range_result(paired,bounds);assert pair_range['status']=='proved_safe'
    rng=random.Random(22240)
    for trial in range(160):
        memory=[]
        for k,vec in enumerate(bounds):
            memory.append([hi if trial<64 and trial>>(k//8)&1 else lo if trial<64
                           else rng.randint(lo,hi) for lo,hi in vec])
        assert paired.run(memory)==control.run(memory)
    tail_rows=[]
    for site in range(16):
        p=without_tail_reductions(control,{site})
        tail_rows.append({'site':site,'branch':site//8,'cohort':site%8,
                          'range':range_result(p,bounds)})
    all_tail=range_result(without_tail_reductions(control,set(range(16))),bounds)
    # Only S0 changes, and level0_j0 pairs cohort i with i+8. Examine both
    # removals in each independent pair, then recheck the combined choice.
    pair_trials=[];selected=set()
    for i in range(8):
        trial=range_result(without_tail_reductions(control,{i,i+8}),bounds)
        pair_trials.append({'cohort':i,'range':trial})
        if trial['status']=='proved_safe':selected.update((i,i+8))
        else:
            assert tail_rows[i]['range']['status']=='proved_safe'
            selected.add(i)
    reduced=without_tail_reductions(control,selected)
    reduced_range=range_result(reduced,bounds)
    assert reduced_range['status']=='proved_safe'
    assert reduced_range['max_output_abs']<=4288  # existing exhaustive crepmod3 gate
    rng=random.Random(40222)
    for trial in range(160):
        memory=[]
        for k,vec in enumerate(bounds):
            memory.append([hi if trial<64 and trial>>(k//8)&1 else lo if trial<64
                           else rng.randint(lo,hi) for lo,hi in vec])
        a,b=control.run(memory),reduced.run(memory)
        assert all((x-y)%3457==0 for av,bv in zip(a,b) for x,y in zip(av,bv))
    prefix_rows=[]
    for st,pairs in plan.items():
        for pair,sides in enumerate(pairs):
            for side,on in sides.items():
                if not on:continue
                for packet in range(6):
                    b,evidence=prefix_bounds(data,plan,(st,packet,pair,side))
                    result=range_result(copy.deepcopy(control),b) if b is not None else evidence
                    prefix_rows.append({'stage':st,'packet':packet,'pair':pair,'side':side,'range':result})
    assert len(prefix_rows)==24 and len(tail_rows)==16
    # Count reusable full-vector values, not table labels or semantic factors.
    finals={n:tuple(v) for n,v in control.tables.items() if n.startswith('final')}
    multiplicities=Counter(finals.values())
    result={'kind':'model_gate_not_linked_or_performance',
      'contract':'accepted canonical BaseMulScale operands -> inherited +/-7644 input cap',
      'prefix_stages':stages,'prefix_removal_trials':prefix_rows,
      'tail_single_removal_trials':tail_rows,'tail_all_removed':all_tail,
      'tail_paired_removal_trials':pair_trials,
      'selected_reduction_cover':{'removed_sites':sorted(selected),
        'remaining_barrett_vectors':40-len(selected),'full_inverse_montgomery':222,
        'range':reduced_range,'residue_fixtures':160,
        'consumer':'output remains inside prior exhaustive crepmod3 +/-4288 domain',
        'scope':'maximal for independent S0 pairs under this interval certificate, not a global lower bound'},
      'schedule':{'full_inverse_montgomery':222,'full_inverse_barrett':40,
        'control_tail_peak':control.peak,'paired_tail_peak':paired.peak,
        'raw_exact_fixtures':160,'arithmetic_and_memory_opcode_multiset_unchanged':True,
        'tail_iterations_control':40,'tail_iterations_paired':28,
        'loop_body_control_instruction_delta':-48,
        'constant_operand_delta':0,'range':pair_range,
        'loops':paired.loops,'operations':paired.ops},
      'final_constant_reuse':{'table_vectors':len(finals),
        'distinct_vector_bytes':len(multiplicities),
        'multiplicity_histogram':dict(Counter(multiplicities.values())),
        'note':'deduplication is not automatic runtime load elimination'},
      'source_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in [Path(__file__),ROOT/'tools/close_yang_contract.py',
          ROOT/'tools/prove_inverse_ct_range.py',ROOT/'asm/ntruplus768_officialopt_invntt_yang_factored.s']}}
    out=ROOT/'results/yang-222-schedule-reduction-audit.json'
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'paired_peak':paired.peak,'tail_safe_sites':[x['site'] for x in tail_rows if x['range']['status']=='proved_safe'],
      'prefix_safe_sites':[x for x in prefix_rows if x['range']['status']=='proved_safe'],
      'all_tail':all_tail['status'],'removed_together':sorted(selected),
      'remaining_barrett':40-len(selected),'output_bound':reduced_range['max_output_abs'],
      'constant_reuse':result['final_constant_reuse']},indent=2))


if __name__=='__main__':main()
