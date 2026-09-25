#!/usr/bin/env python3
"""P138 part 2: split GT's lead over Official-with-GT's-permutation into the hash layer and the rest.
  total      = GT - Official(sponge Official, permutation GT)
  hash layer = GT - GT_offhash            (same arithmetic and KEM flow, only the sponge differs)
  rest       = GT_offhash - Official      (same sponge and permutation: arithmetic + KEM glue)
usage: split.py runs2_m2.txt|runs2_pi.txt"""
import sys, statistics as st, collections
runs = collections.defaultdict(lambda: collections.defaultdict(list))
for line in open(sys.argv[1]):
    p = line.split()
    if len(p) < 7 or p[1] != 'keygen': continue
    for op, v in (('keygen', p[2]), ('encaps', p[4]), ('decaps', p[6])):
        runs[p[0]][op].append(int(v))
med = {b: {op: st.median(v) for op, v in ops.items()} for b, ops in runs.items()}
for s in ('768', '864', '1152'):
    o = med.get(f'off{s}_gtk') or med.get(f'off{s}_gtks'); h = med[f'gt{s}_offhash']; g = med[f'gt{s}']
    print(f'NTRU+{s}  (Official {o["keygen"]:,.0f}/{o["encaps"]:,.0f}/{o["decaps"]:,.0f}, '
          f'GT+Official sponge {h["keygen"]:,.0f}/{h["encaps"]:,.0f}/{h["decaps"]:,.0f}, GT {g["keygen"]:,.0f}/{g["encaps"]:,.0f}/{g["decaps"]:,.0f})')
    for op in ('keygen', 'encaps', 'decaps'):
        tot, hl, rest = g[op] - o[op], g[op] - h[op], h[op] - o[op]
        print(f'  {op}: total {tot:+7.0f} ({tot / o[op] * 100:+5.1f}%) = hash layer {hl:+7.0f} ({hl / tot * 100 if tot else 0:3.0f}%)'
              f' + arithmetic & glue {rest:+7.0f} ({rest / tot * 100 if tot else 0:3.0f}%)')
