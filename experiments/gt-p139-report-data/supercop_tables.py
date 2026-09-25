#!/usr/bin/env python3
"""P139: SUPERCOP medians (median over rounds of SUPERCOP's median) and, for key generation, the
mean over every sample (the expected cost under retries).  usage: supercop_tables.py supercop-summary.json"""
import json, sys, statistics as st
rows = json.load(open(sys.argv[1]))
K = ['keypair_cycles', 'enc_cycles', 'dec_cycles']
for s in ('768', '864', '1152'):
    R = [r for r in rows if r['set'] == s]
    med = {v: {k: st.median([r['median'][k] for r in R if r['variant'] == v]) for k in K} for v in ('official', 'official-main', 'gt')}
    mean = {v: {k: st.fmean([r['mean'][k] for r in R if r['variant'] == v]) for k in K} for v in ('official', 'official-main', 'gt')}
    spread = {v: (min(r['median']['keypair_cycles'] for r in R if r['variant'] == v), max(r['median']['keypair_cycles'] for r in R if r['variant'] == v)) for v in med}
    n = sum(r['n']['keypair_cycles'] for r in R if r['variant'] == 'gt')
    print(f'NTRU+{s}  (rounds {len(R)//3}; {n} key generation samples per leaf)')
    for v in ('official', 'official-main', 'gt'):
        print(f'  {v:14s} median  {med[v]["keypair_cycles"]:>9,.1f} / {med[v]["enc_cycles"]:>9,.1f} / {med[v]["dec_cycles"]:>9,.1f}'
              f'   keypair mean {mean[v]["keypair_cycles"]:>9,.0f}  (round medians {spread[v][0]:,}-{spread[v][1]:,})')
    for base in ('official', 'official-main'):
        d = [(med['gt'][k] - med[base][k]) / med[base][k] * 100 for k in K]
        dm = (mean['gt']['keypair_cycles'] - mean[base]['keypair_cycles']) / mean[base]['keypair_cycles'] * 100
        print(f'  GT vs {base:14s} {d[0]:+.2f}% / {d[1]:+.2f}% / {d[2]:+.2f}%   keypair by mean {dm:+.2f}%')
print(sorted({l for r in rows for x in (r["before"], r["after"]) for l in x.splitlines() if "thr" in l}))
