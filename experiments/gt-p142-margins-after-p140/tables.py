#!/usr/bin/env python3
"""P142: GT against GitHub main's builds (medians of the sessions), and the permutation-equal lead
split into GT's hash layer and the rest.  usage: tables.py runs_m2.txt|runs_pi.txt"""
import sys, statistics as st, collections
runs = collections.defaultdict(lambda: collections.defaultdict(list))
for line in open(sys.argv[1]):
    p = line.split()
    if len(p) < 7 or p[1] != 'keygen': continue
    for op, v in (('keygen', p[2]), ('encaps', p[4]), ('decaps', p[6])): runs[p[0]][op].append(int(v))
med = {b: {op: st.median(v) for op, v in ops.items()} for b, ops in runs.items()}
n = min(len(v['keygen']) for v in runs.values())
OPS = ('keygen', 'encaps', 'decaps')
T = lambda d: ' / '.join(f'{d[o]:,.0f}' for o in OPS)
pct = lambda g, o: ' / '.join(f'{(g[k] - o[k]) / o[k] * 100:+.1f}%' for k in OPS)
names = {'offm{}_ce': 'main, default (CE) build', 'offm{}_noce': 'main, NO_CE build', 'offm{}_gtk': 'main sponge + GT permutation'}
print(f'(sessions: {n})')
for s in ('768', '864', '1152'):
    g = med[f'gt{s}']; print(f'NTRU+{s}: GT {T(g)}')
    for k, name in names.items():
        o = med.get(k.format(s))
        if o: print(f'  vs {name:30s} {T(o):>26s}   {pct(g, o)}')
    o, h = med[f'offm{s}_gtk'], med[f'gt{s}_offhash']
    for op in OPS:
        tot, hl = g[op] - o[op], g[op] - h[op]
        print(f'    {op}: permutation-equal lead {tot:+.0f} = GT hash layer {hl:+.0f} ({hl / tot * 100 if tot else 0:.0f}%) + arithmetic and glue {tot - hl:+.0f}')
