#!/usr/bin/env python3
"""Fallback check: does the route fit into the ALREADY-ALLOCATED producer?

Physical registers are reused, so a live range is one def up to the last use
before the NEXT def of that same register — not first-def to last-use, which
would report every reused register as live throughout.
"""
import re
from pathlib import Path
PROD = Path('../gt864-p28s-timing/candidate-main.timing.S')
VREG = re.compile(r'\bv(\d+)\.', re.I)
QREG = re.compile(r'\bq(\d+)\b', re.I)
RMW  = ('mls','mla','smlal','smlal2','ins','sri','sli','bit','bif','bsl')
ST   = ('str','st1','st2','st3','st4','stur')

lines = []
for l in PROD.read_text().splitlines():
    s = re.sub(r'//.*', '', l).rstrip(); t = s.strip()
    if not t or t.startswith(('.', '#')) or t.endswith(':'): continue
    lines.append(s)

def du(s):
    rs = [int(x) for x in VREG.findall(s)] + [int(x) for x in QREG.findall(s)]
    if not rs: return set(), set()
    op = s.strip().split()[0].lower()
    if op.startswith(ST): return set(), set(rs)
    if op in RMW:         return {rs[0]}, set(rs)
    return {rs[0]}, set(rs[1:])

# per-register def/use timeline -> live intervals
timeline = {r: [] for r in range(32)}
for i, s in enumerate(lines):
    d, u = du(s)
    for r in u: timeline[r].append((i, 'u'))
    for r in d: timeline[r].append((i, 'd'))
intervals = []
for r, evs in timeline.items():
    evs.sort()
    start = None
    for i, kind in evs:
        if kind == 'd':
            if start is not None: pass          # previous value ends at its last use
            start = i
        else:
            if start is None: start = 0         # live-in
    # walk again building [def, last use before next def]
    cur = None; lastu = None
    for i, kind in evs:
        if kind == 'd':
            if cur is not None and lastu is not None: intervals.append((r, cur, lastu))
            cur, lastu = i, i
        elif cur is not None:
            lastu = i
        else:
            cur, lastu = 0, i
    if cur is not None and lastu is not None: intervals.append((r, cur, lastu))

live = [0]*len(lines)
for r, a, b in intervals:
    for i in range(a, b+1): live[i] += 1
free = [32 - x for x in live]
store_at = [i for i, s in enumerate(lines) if s.strip().startswith('str ')]
sf = sorted(free)
print(f"  producer: {len(lines)} instructions, {len(store_at)} stores, {len(intervals)} live intervals")
print(f"  free physical vector registers: min {min(free)}, p25 {sf[len(sf)//4]}, "
      f"median {sf[len(sf)//2]}, max {max(free)}")
for k in (3, 4, 6, 8):
    n = sum(1 for f in free if f >= k)
    print(f"    slots with >= {k} free: {n:4d}/{len(lines)} ({100*n/len(lines):5.1f}%)")
need_slots = len(store_at) * 12
print(f"  route to place: {len(store_at)} bursts x 12 = {need_slots} instructions, "
      f"working set 4")
n4 = sum(1 for f in free if f >= 4)
print(f"  verdict: {'placeable without re-allocation' if n4 >= need_slots else 'needs re-allocation'}"
      f"  ({n4} eligible slots vs {need_slots} needed)")
