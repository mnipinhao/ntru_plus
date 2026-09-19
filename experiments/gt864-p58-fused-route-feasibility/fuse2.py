#!/usr/bin/env python3
"""Feasibility variants.  The blocker in fuse.py was the four permanently live
ternary constants, not the route work.  Variants:

  A  constants held live for the whole region            (fuse.py baseline)
  B  sqrdmulh/mls take their constant by element, so the
     recip/three pair collapses into one vector          (4 -> 3 live)
  C  constants reloaded from memory once per burst; none
     stay live.  Extra loads are free: measured 2026-09-18,
     substituting movi for the 448 composite-table loads made
     BOTH hosts slower because the load ports sit idle.
"""
import re, sys, collections
sys.path.insert(0, '.')
from pressure import parse

PROD = '../gt864-p28-paired-i16/candidate-main.sym.S'
BUDGET = 32
ins = parse(PROD)
raw = [re.sub(r'//.*', '', l).strip() for l in open(PROD)]
raw = [s for s in raw if s and not s.startswith(('.', '#')) and not s.endswith(':')]
last_use = {}
for i, (op, d, u) in enumerate(ins):
    for r in u | d: last_use[r] = i

def run(label, const_live, chain, prod_bias=0):
    cur, peak, pending, emitted, kept = set(), 0, collections.deque(), 0, 0
    for i, (op, d, u) in enumerate(ins):
        if op == 'str':
            pending.append([i, 0]); continue
        for r in d | u: cur.add(r)
        kept += 1
        peak = max(peak, len(cur) + const_live + prod_bias)
        for r in list(cur):
            if last_use.get(r, -1) <= i: cur.discard(r)
        extra = 0
        while pending:
            _, pos = pending[0]
            need = chain[pos][1]
            if len(cur) + const_live + prod_bias + extra + max(need, 0) + 1 > BUDGET:
                break
            extra = max(0, extra + need)
            emitted += 1
            peak = max(peak, len(cur) + const_live + prod_bias + extra)
            pending[0][1] += 1
            if pending[0][1] >= len(chain):
                pending.popleft(); extra = 0
    left = sum(len(chain) - p for _, p in pending)
    total = 32 * len(chain)
    print(f"  {label}")
    print(f"     route interleaved {emitted}/{total} ({100*emitted/total:5.1f}%)"
          f"   left as tail {left:4d}   region length {kept+emitted+left}")
    print(f"     PEAK LIVE {peak:3d} / {BUDGET}   -> {'FEASIBLE' if peak<=BUDGET else 'OVER by '+str(peak-BUDGET)}")

# (opcode, net live delta while this step is in flight)
A = [('cmgt',1),('cmgt',1),('add',0),('sub',0),('sqrdmulh',1),('mls',0),
     ('ldr',1),('ext',1),('st3',-3)]
B = A
C = [('ldr:hi',1),('ldr:lo',1),('cmgt',1),('cmgt',1),('add',-2),('sub',0),
     ('ldr:rs',1),('sqrdmulh',1),('mls',-1),('ldr:p2',1),('ext',1),('st3',-4)]

print(f"producer {len(ins)} instructions, symbolic peak 33 (allocator fits 32,"
      f" so the model is +1 conservative)\n")
run("A  4 constants live for the whole region      ", 4, A)
run("B  3 constants live (recip/three by element)  ", 3, B)
run("C  constants reloaded per burst, none live    ", 0, C)
print()
run("C' variant C, producer at its true peak 32    ", 0, C, prod_bias=-1)
