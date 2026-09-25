#!/usr/bin/env python3
"""P138: Official from SUPERCOP 20260831 against Official from GitHub main (3991b2a), and GT's margin
over the GitHub main builds.  usage: main.py runs4_*.txt"""
import sys, statistics as st, collections
runs = collections.defaultdict(lambda: collections.defaultdict(list))
for line in open(sys.argv[1]):
    p = line.split()
    if len(p) < 7 or p[1] != 'keygen': continue
    for op, v in (('keygen', p[2]), ('encaps', p[4]), ('decaps', p[6])): runs[p[0]][op].append(int(v))
med = {b: {op: st.median(v) for op, v in ops.items()} for b, ops in runs.items()}
n = {b: len(v['keygen']) for b, v in runs.items()}
OPS = ('keygen', 'encaps', 'decaps')
T = lambda d: ' / '.join(f'{d[o]:,.0f}' for o in OPS)
P = lambda xs: ' / '.join(f'{x:+.1f}%' for x in xs)
for s in ('768', '864', '1152'):
    g = med[f'gt{s}']
    print(f'NTRU+{s}: GT {T(g)}  (sessions {n["gt" + s]})')
    for v, name in (('noce', 'NO_CE build (SUPERCOP leaf form)'), ('ce', 'CE build (main default)')):
        a, m = med.get(f'off{s}_{v}'), med.get(f'offm{s}_{v}')
        if not m: continue
        print(f'  {name:34s} SUPERCOP/old {T(a)}  GitHub main {T(m)}  ({P([(m[o] - a[o]) / a[o] * 100 for o in OPS])})')
        print(f'  {"":34s} GT vs GitHub main {P([(g[o] - m[o]) / m[o] * 100 for o in OPS])}')
