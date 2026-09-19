#!/usr/bin/env python3
"""Constructive feasibility: can P29's route work be scheduled inside a producer
region without exceeding 32 vector registers?

Model of the fused P0 region (P2 normalizes its own output before storing, so the
route no longer re-normalizes it):
  per (top,t):  normalize P0's own Q in registers (6)  +  ldr P2's Q (1)
                +  ext to split P0's Q into two D halves (1)  +  st3 (1)
P0 no longer stores its 32 Q, so 32 str disappear from the producer.

Scheduling rule: keep the producer's Slothy order fixed and insert route
instructions only where the live count stays within the budget.  This is a
sufficient (not optimal) schedule, so success here is a real feasibility proof.
"""
import re, sys, collections
sys.path.insert(0, '.')
from pressure import parse

PROD = '../gt864-p28-paired-i16/candidate-main.sym.S'
BUDGET = 32
CONSTANTS = 4            # tern_hi, tern_lo, tern_recip, tern_three held live

ins = parse(PROD)
# producer stores identify when each of its 32 output Q becomes final
store_idx = [i for i, (op, d, u) in enumerate(ins) if op == 'str']
store_val = {}
raw = [re.sub(r'//.*', '', l).strip() for l in open(PROD)]
raw = [s for s in raw if s and not s.startswith(('.', '#')) and not s.endswith(':')]
for i in store_idx:
    m = re.search(r'[VQD]<([A-Za-z0-9_]+)>', raw[i])
    store_val[i] = m.group(1) if m else f'out{i}'
print(f"producer: {len(ins)} instructions, {len(store_idx)} output stores, "
      f"first at {store_idx[0]}, last at {store_idx[-1]}")

# producer liveness
last_use = {}
for i, (op, d, u) in enumerate(ins):
    for r in u | d: last_use[r] = i

# route chain per producer output: 9 instructions, working set = 3 beyond constants
CHAIN = [('cmgt',1),('cmgt',1),('add',0),('sub',0),('sqrdmulh',1),('mls',0),
         ('ldr',1),('ext',1),('st3',-3)]   # second element: net live-register delta

sched, cur, peak, pending = [], set(), 0, collections.deque()
route_emitted = 0
for i, (op, d, u) in enumerate(ins):
    if op == 'str':                       # P0 keeps its Q in registers instead
        pending.append([store_val[i], 0]) # queue this output's route chain
        continue
    for r in d | u: cur.add(r)
    sched.append(('P', op))
    live = len(cur) + CONSTANTS
    peak = max(peak, live)
    for r in list(cur):
        if last_use.get(r, -1) <= i: cur.discard(r)
    # opportunistically drain route work into the headroom
    extra = 0
    while pending:
        val, pos = pending[0]
        need = CHAIN[pos][1]
        if len(cur) + CONSTANTS + extra + max(need, 0) + 1 > BUDGET:
            break
        extra = max(0, extra + need)
        sched.append(('R', CHAIN[pos][0])); route_emitted += 1
        peak = max(peak, len(cur) + CONSTANTS + extra)
        pending[0][1] += 1
        if pending[0][1] >= len(CHAIN):
            pending.popleft(); extra = 0
# drain whatever is left after the producer finishes
tail_len = sum(len(CHAIN) - p for _, p in pending)
route_total = 32 * len(CHAIN)
print(f"\nfused P0 region")
print(f"  producer instructions kept        : {sum(1 for k,_ in sched if k=='P')}"
      f"   (32 str removed)")
print(f"  route instructions interleaved    : {route_emitted} / {route_total}"
      f"   ({100*route_emitted/route_total:.1f}%)")
print(f"  route instructions left as a tail : {tail_len}")
print(f"  total region length               : {len(sched)+tail_len}")
print(f"  PEAK LIVE VECTOR REGISTERS        : {peak}   (budget {BUDGET})")
print(f"  verdict: {'FEASIBLE' if peak <= BUDGET else 'OVER BUDGET'}")
