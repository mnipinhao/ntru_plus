#!/usr/bin/env python3
"""P138: medians of the sessions in runs_*.txt, GT against every Official build.
usage: tables.py runs_m2.txt|runs_pi.txt"""
import sys, statistics as st, collections
runs = collections.defaultdict(lambda: collections.defaultdict(list))
for line in open(sys.argv[1]):
    p = line.split()
    if len(p) < 7 or p[1] != 'keygen': continue
    for op, v in (('keygen', p[2]), ('encaps', p[4]), ('decaps', p[6])):
        runs[p[0]][op].append(int(v))
med = {b: {op: st.median(v) for op, v in ops.items()} for b, ops in runs.items()}
n = {b: len(ops['keygen']) for b, ops in runs.items()}
labels = {'noce': 'Official as SUPERCOP ships it', 'ce': 'Official + CryptoExtension',
          'gtk': 'Official sponge + GT permutation', 'gtks': 'Official sponge + GT permutation',
          'offhash': 'GT arithmetic + Official sponge'}
for s in ('768', '864', '1152'):
    g = med.get('gt' + s)
    if not g: continue
    print(f'NTRU+{s}: GT {g["keygen"]:,.0f} / {g["encaps"]:,.0f} / {g["decaps"]:,.0f}  (sessions: {n["gt" + s]})')
    for v in ('noce', 'ce', 'gtk', 'gtks'):
        o = med.get(f'off{s}_{v}')
        if not o: continue
        d = [(g[op] - o[op]) / o[op] * 100 for op in ('keygen', 'encaps', 'decaps')]
        print(f'  vs {labels[v]:34s} {o["keygen"]:7,.0f} / {o["encaps"]:7,.0f} / {o["decaps"]:7,.0f}   '
              f'{d[0]:+6.1f}% / {d[1]:+6.1f}% / {d[2]:+6.1f}%')
    o = med.get(f'gt{s}_offhash')
    if o:
        print(f'  {labels["offhash"]:37s} {o["keygen"]:7,.0f} / {o["encaps"]:7,.0f} / {o["decaps"]:7,.0f}')
