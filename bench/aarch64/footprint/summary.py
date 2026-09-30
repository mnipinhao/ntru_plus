#!/usr/bin/env python3
"""Tables from run.sh output: the package READMEs' code-size and cold-start sentences.

usage: summary.py RUN_OUTPUT...     (several outputs are pooled, e.g. two runs of the pairs)

KB are 1,000 bytes, as the READMEs use them.  A cold figure is the median over
the process medians.  "GT faster" counts the pairs whose GT process beat its
official partner.
"""
import collections
import re
import statistics
import sys

size, foot = {}, {}
cold = collections.defaultdict(list)          # set -> [(impl, [keygen, encaps, decaps]), ...] in order
for fn in sys.argv[1:]:
    for line in open(fn):
        if m := re.match(r'size (gt|off)(\d+) kem_text (\d+)', line):
            size[(m[2], m[1])] = int(m[3])
        elif m := re.match(r'footprint (gt|off)(\d+) op(\d) (\d+) bytes KEM code', line):
            foot[(m[2], m[1], int(m[3]))] = int(m[4])
        elif m := re.match(r'(gt|off)(\d+) cold keygen (\d+) encaps (\d+) decaps (\d+)', line):
            cold[m[2]].append((m[1], [int(m[3]), int(m[4]), int(m[5])]))

for s in ('768', '864', '1152'):
    if (s, 'gt') not in size and s not in cold:
        continue
    print(f'NTRU+{s}')
    if (s, 'gt') in size:
        print(f"  linked KEM text   GT {size[(s, 'gt')]:,} B ({size[(s, 'gt')] / 1000:.1f} KB)   "
              f"official {size[(s, 'off')]:,} B ({size[(s, 'off')] / 1000:.1f} KB)")
    if (s, 'gt', 0) in foot:
        kb = lambda i: ' / '.join(f'{foot[(s, i, op)] / 1000:.1f}' for op in range(3))
        print(f"  executed KB       GT {kb('gt')}   official {kb('off')}   (keygen / encaps / decaps)")
    if cold[s]:
        rows = cold[s]
        pairs = [rows[i:i + 2] for i in range(0, len(rows) - 1, 2)]
        assert all({a[0], b[0]} == {'gt', 'off'} for a, b in pairs), f'NTRU+{s}: cold lines are not in pairs'
        med = {i: [statistics.median(v[k] for impl, v in rows if impl == i) for k in range(3)] for i in ('gt', 'off')}
        wins = [sum(dict(p)['gt'][k] < dict(p)['off'][k] for p in pairs) for k in range(3)]
        fmt = lambda xs: ' / '.join(f'{x:,.1f}'.rstrip('0').rstrip('.') for x in xs)
        print(f"  cold cycles       GT {fmt(med['gt'])}   official {fmt(med['off'])}")
        print('  cold margin       ' + ' / '.join(f"{(g - o) / o * 100:+.1f}%" for g, o in zip(med['gt'], med['off'])) +
              f"   GT faster in {' / '.join(map(str, wins))} of {len(pairs)} pairs")
