#!/usr/bin/env python3
"""P45 pair-route search and exact joint-pack static ledger."""
from __future__ import annotations
import argparse, importlib.util, json, math, random, subprocess, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
P41 = ROOT / "experiments/gt864-p41-paired-record-store/search.py"

def load():
    spec = importlib.util.spec_from_file_location("p41_pair_for_p45", P41)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec); sys.modules[spec.name] = module
    spec.loader.exec_module(module); return module

def compile_dag(module, outputs, pairs):
    p23=module.load_p23(); nodes=set().union(*(p23.closure(x) for x in outputs.values()))
    ids={node:i for i,node in enumerate(nodes)}
    deps={ids[n]:tuple(ids[x] for x in n.inputs) for n in nodes}
    operation={ids[n]:n.operation for n in nodes}; source={ids[n]:n.source for n in nodes}
    roots={o:ids[n] for o,n in outputs.items()}; memo={}
    def cost(n):
        if n not in memo:memo[n]=1+sum(cost(x) for x in deps[n])
        return memo[n]
    for n in deps:cost(n)
    closures={}
    def close(n):
        if n not in closures:closures[n]={n}.union(*(close(x) for x in deps[n]))
        return closures[n]
    pair_closures=[close(roots[a])|close(roots[b]) for a,b in pairs]
    return deps,operation,source,roots,memo,pair_closures

def simulate(compiled,pairs,order,capacity):
    deps,operation,source,roots,memo,pair_closures=compiled
    future={n:[] for values in pair_closures for n in values}
    for pos,pair_index in enumerate(order):
        for n in pair_closures[pair_index]:future[n].append(pos)
    next_table={}
    end=len(order)+1
    for n,uses in future.items():
        use_set=set(uses); row=[end]*len(order); following=end
        for pos in range(len(order)-1,-1,-1):
            row[pos]=following
            if pos in use_set:following=pos
        next_table[n]=row
    cache=set();counts=Counter();peak=0
    def next_use(n,pos):
        return next_table[n][pos]
    def ensure(n,pos,protected):
        nonlocal peak
        if n in cache:return
        ready=set()
        for d in deps[n]:ensure(d,pos,protected|ready);ready.add(d)
        if len(cache)>=capacity:
            choices=cache-protected
            if not choices:raise RuntimeError("frontier infeasible")
            victim=max(choices,key=lambda x:(next_use(x,pos),-memo[x],operation[x],source[x]))
            cache.remove(victim)
        cache.add(n);peak=max(peak,len(cache));counts[operation[n]]+=1
    for pos,pair_index in enumerate(order):
        a,b=pairs[pair_index];ra,rb=roots[a],roots[b]
        ensure(ra,pos,set());ensure(rb,pos,{ra});cache.remove(ra);cache.remove(rb)
        for n in tuple(cache):
            if next_use(n,pos)>len(order):cache.remove(n)
    return {"instructions":sum(counts.values()),"source_loads":counts["load"],
      "routing_arithmetic":sum(counts.values())-counts["load"],"peak_route_registers":peak,
      "counts":dict(sorted(counts.items()))}

def anneal(module, compiled, pairs, initial, capacity, iterations, seed):
    rng = random.Random(seed); current = list(initial)
    current_result = simulate(compiled,pairs,current,capacity)
    best, best_result = list(current), current_result
    for step in range(iterations):
        candidate = list(current); move = rng.randrange(3)
        if move == 0:
            a,b = rng.sample(range(27),2); candidate[a],candidate[b]=candidate[b],candidate[a]
        elif move == 1:
            a,b = sorted(rng.sample(range(27),2)); candidate[a:b]=reversed(candidate[a:b])
        else:
            a,b = rng.sample(range(27),2); candidate.insert(b,candidate.pop(a))
        result = simulate(compiled,pairs,candidate,capacity)
        delta = result["instructions"]-current_result["instructions"]
        temp=max(.05,8*(1-step/iterations))
        if ((result["instructions"],result["source_loads"]) <
            (current_result["instructions"],current_result["source_loads"]) or
            rng.random() < math.exp(-max(delta,0)/temp)):
            current,current_result=candidate,result
        if ((result["instructions"],result["source_loads"]) <
            (best_result["instructions"],best_result["source_loads"])):
            best,best_result=list(candidate),result
    return best,best_result

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--iterations",type=int,default=50000)
    ap.add_argument("--seeds",type=int,default=4); args=ap.parse_args()
    m=load(); p23=m.load_p23(); outputs,_=p23.build_dag(); pairs=m.pairs_in_wire_order()
    compiled=compile_dag(m,outputs,pairs)
    report=json.loads(subprocess.check_output(["git","show",
        "ba6bc701:experiments/gt864-p41-paired-record-store/search-results.json"],
        cwd=ROOT))
    initial=report["pair_order"]
    variants=[]
    # More route registers require fewer resident indices and therefore public
    # index reloads.  All variants reserve q, reciprocal and one work vector.
    for capacity,index_loads in ((27,0),(28,27),(29,54)):
        best=None; order=None
        for i in range(args.seeds):
            o,r=anneal(m,compiled,pairs,initial,capacity,args.iterations,451864+1000*capacity+i)
            if best is None or (r["instructions"],r["source_loads"]) < (best["instructions"],best["source_loads"]):
                order,best=o,r
        total=best["instructions"]+index_loads+270+243
        variants.append({"route_capacity":capacity,"resident_indices":29-capacity,
          "index_loads_per_top":index_loads,"pair_order":order,"route":best,
          "joint_pack_store_per_top":243,"normalization_per_top":270,
          "candidate_total_per_top":total,"delta_vs_p24_complete":2*(total-1041),
          "hard_gate":{"route_at_most_300":best["instructions"]+index_loads<=300,
            "coefficient_loads_at_most_61":best["source_loads"]<=61,
            "pack_store_saves_at_least_4_per_record":True}})
    out={"experiment":"GT864-P45-TWO-RECORD-PACK-20260916","p24":{"total_per_top":1041,"route":285,"loads":61,"pack_store":486},
      "joint_pack_identity":"9 instructions/pair = 243/top","iterations_per_seed":args.iterations,"seeds":args.seeds,"variants":variants}
    (HERE/"search-results.json").write_text(json.dumps(out,indent=2)+"\n"); print(json.dumps(out,indent=2))
if __name__ == "__main__": main()
