#!/usr/bin/env python3
"""Where is the fused peak attained, and how much route work fits per budget?"""
import re, sys, collections
sys.path.insert(0, '.')
from pressure import parse
PROD = '../gt864-p28-paired-i16/candidate-main.sym.S'
ins = parse(PROD)
last_use = {}
for i,(op,d,u) in enumerate(ins):
    for r in u|d: last_use[r]=i
C = [('ldr',1),('ldr',1),('cmgt',1),('cmgt',1),('add',-2),('sub',0),
     ('ldr',1),('sqrdmulh',1),('mls',-1),('ldr',1),('ext',1),('st3',-4)]

def run(budget):
    cur,peak,peak_kind,pending,emitted = set(),0,'?',collections.deque(),0
    for i,(op,d,u) in enumerate(ins):
        if op=='str': pending.append([i,0]); continue
        for r in d|u: cur.add(r)
        if len(cur)>peak: peak,peak_kind=len(cur),'producer-only'
        for r in list(cur):
            if last_use.get(r,-1)<=i: cur.discard(r)
        extra=0
        while pending:
            _,pos=pending[0]; need=C[pos][1]
            if len(cur)+extra+max(need,0)+1>budget: break
            extra=max(0,extra+need); emitted+=1
            if len(cur)+extra>peak: peak,peak_kind=len(cur)+extra,'route-inflated'
            pending[0][1]+=1
            if pending[0][1]>=len(C): pending.popleft(); extra=0
    left=sum(len(C)-p for _,p in pending)
    return peak,peak_kind,emitted,left

print("  budget   peak  peak attained at      route interleaved   left as tail")
for b in (28,30,31,32,33):
    p,k,e,l = run(b)
    tot=32*len(C)
    print(f"    {b:2d}      {p:3d}   {k:16s}      {e:4d}/{tot} ({100*e/tot:5.1f}%)      {l:4d}")
print()
print("  producer's own symbolic peak: 33  (allocated version fits 32 exactly,")
print("  so the model is +1 conservative on the producer and 0 on the route)")
