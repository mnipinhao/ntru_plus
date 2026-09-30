#!/usr/bin/env python3
"""Per-operation tables from run_sessions.sh output.

usage: tables.py RUNS [MIN_CEILING_MHZ]

Each line of RUNS is one run of one build.  A run reports, per operation, the
fastest of its batches that passed the clock gate, in ns.  A build's figure is
the median over its runs.

A run is skipped when fewer than 20 batches of an operation passed the gate.
With MIN_CEILING_MHZ, a run is also skipped when its fastest witness never
reached that clock.  On M2 Pro the single-core top state is 3,504 MHz; a busy
core elsewhere in the cluster holds the whole run at 3,408 MHz, and every
figure then reads about 2.8% high while still passing the gate.

For each set this prints GT and each official build, and GT's margin against
each.  The package READMEs use:
- the CE build for "vs Official" on M2;
- the NO_CE build for "vs Official" on the Pi;
- "main sponge + GT permutation" for "same Keccak permutation".

It also splits the permutation-equal lead in two, using gt<set>_offhash (GT's
arithmetic with main's sponge): GT's hash layer, and the arithmetic with its
glue.
"""
import collections
import re
import statistics
import sys

OPS = ('keygen', 'encaps', 'decaps')
MIN_ACCEPTED = 20
ceiling = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
runs = collections.defaultdict(lambda: collections.defaultdict(list))
few = low = 0
for line in open(sys.argv[1]):
    p = line.split()
    if len(p) < 13 or p[1] != 'keygen':
        continue
    accepted = [int(a) for a in re.findall(r'(\d+)/\d+', line)]
    if accepted and min(accepted) < MIN_ACCEPTED:
        few += 1
        continue
    if float(p[8]) < ceiling:
        low += 1
        continue
    for op, value in zip(OPS, (p[2], p[4], p[6])):
        runs[p[0]][op].append(int(value))

med = {b: {op: statistics.median(v) for op, v in ops.items()} for b, ops in runs.items()}
count = {b: len(ops['keygen']) for b, ops in runs.items()}
fmt = lambda d: ' / '.join(f'{d[o]:,.0f}' for o in OPS)
pct = lambda g, o: ' / '.join(f'{(g[k] - o[k]) / o[k] * 100:+.1f}%' for k in OPS)
NAMES = (('ce', 'main, default (CE) build'), ('noce', 'main, NO_CE build'),
         ('gtk', 'main sponge + GT permutation'))

print(f'runs skipped: {few} with fewer than {MIN_ACCEPTED} accepted batches, '
      f'{low} below a {ceiling:.0f} MHz ceiling')
for s in ('768', '864', '1152'):
    g = med.get(f'gt{s}')
    if not g:
        continue
    print(f'NTRU+{s}: GT {fmt(g)} ns  ({count[f"gt{s}"]} runs)')
    for key, name in NAMES:
        o = med.get(f'offm{s}_{key}')
        if o:
            print(f'  vs {name:30s} {fmt(o):>26s}   {pct(g, o)}   ({count[f"offm{s}_{key}"]} runs)')
    o, h = med.get(f'offm{s}_gtk'), med.get(f'gt{s}_offhash')
    if o and h:
        for op in OPS:
            lead, hash_layer = g[op] - o[op], g[op] - h[op]
            share = f'{hash_layer / lead * 100:.0f}%' if lead else '-'
            print(f'    {op}: permutation-equal lead {lead:+.0f} = GT hash layer {hash_layer:+.0f} '
                  f'({share}) + arithmetic and glue {lead - hash_layer:+.0f}')
