#!/usr/bin/env python3
"""Pressure profile: how much register headroom the producer leaves, and where."""
import sys, collections
sys.path.insert(0,'.')
from pressure import parse

def profile(path):
    ins = parse(path)
    last_use = {}
    for i,(op,d,u) in enumerate(ins):
        for r in u|d: last_use[r]=i
    cur=set(); prof=[]
    for i,(op,d,u) in enumerate(ins):
        for r in d|u: cur.add(r)
        prof.append(len(cur))
        for r in list(cur):
            if last_use.get(r,-1)<=i: cur.discard(r)
    return ins, prof

for path in sys.argv[1:]:
    ins, prof = profile(path)
    n=len(prof)
    print(f"=== {path.split('/')[-1]}  ({n} instructions) ===")
    h=collections.Counter(prof)
    print("  pressure histogram (live vector values -> % of schedule):")
    for p in sorted(h):
        if h[p]*100//n >= 1 or p>=30:
            bar='#'*max(1,h[p]*60//n)
            print(f"    {p:3d}: {h[p]:5d} ({h[p]*100/n:5.1f}%) {bar}")
    for k in (4,6,8,10,12):
        free=sum(1 for p in prof if p<=32-k)
        print(f"  slots with >= {k:2d} free registers: {free:5d} / {n}  ({free*100/n:5.1f}%)")
    print()
