#!/usr/bin/env python3
"""P138: what the two sponge fixes give Official, and what is left of GT's margin.  usage: fix.py runs3_*.txt"""
import sys, statistics as st, collections
runs = collections.defaultdict(lambda: collections.defaultdict(list))
for line in open(sys.argv[1]):
    p = line.split()
    if len(p) < 7 or p[1] != 'keygen': continue
    for op, v in (('keygen', p[2]), ('encaps', p[4]), ('decaps', p[6])): runs[p[0]][op].append(int(v))
med = {b: {op: st.median(v) for op, v in ops.items()} for b, ops in runs.items()}
OPS = ('keygen', 'encaps', 'decaps')
fmt = lambda d: ' / '.join(f'{x:+.1f}%' for x in d)
for s in ('768', '864', '1152'):
    g = med[f'gt{s}']
    print(f'NTRU+{s}: GT {" / ".join(f"{g[o]:,.0f}" for o in OPS)}')
    for base, fixed, name in (('noce', 'nocefix', "SUPERCOP's Official"), ('ce', 'cefix', 'Official + CE (upstream default)')):
        a, b = med.get(f'off{s}_{base}'), med.get(f'off{s}_{fixed}')
        if not a: continue
        fx = [(b[o] - a[o]) / a[o] * 100 for o in OPS]
        m0 = [(g[o] - a[o]) / a[o] * 100 for o in OPS]; m1 = [(g[o] - b[o]) / b[o] * 100 for o in OPS]
        print(f'  {name:34s} {" / ".join(f"{a[o]:,.0f}" for o in OPS)} -> fixed {" / ".join(f"{b[o]:,.0f}" for o in OPS)}  ({fmt(fx)})')
        print(f'  {"":34s} GT margin {fmt(m0)} -> {fmt(m1)}')
