#!/usr/bin/env python3
"""What is free at each of the producer's 32 store points?

Physical liveness: one def up to the last use before the NEXT def of the same
register (not first-def to last-use, which counts every reused register as live
throughout).
"""
import re, sys
from pathlib import Path
SRC = Path('../gt864-p28s-timing/candidate-main.timing.S')
VR = re.compile(r'\bv(\d+)\.', re.I); QR = re.compile(r'\bq(\d+)\b', re.I)
XR = re.compile(r'\bx(\d+)\b')
RMW = ('mls','mla','smlal','smlal2','ins','sri','sli','bit','bif','bsl')
ST  = ('str','st1','st2','st3','st4','stur')

lines=[]
for l in SRC.read_text().splitlines():
    s=re.sub(r'//.*','',l).rstrip(); t=s.strip()
    if not t or t.startswith(('.','#')) or t.endswith(':'): continue
    lines.append(s)

def vdu(s):
    rs=[int(x) for x in VR.findall(s)]+[int(x) for x in QR.findall(s)]
    if not rs: return set(),set()
    op=s.strip().split()[0].lower()
    if op.startswith(ST): return set(),set(rs)
    if op in RMW: return {rs[0]},set(rs)
    return {rs[0]},set(rs[1:])

def xdu(s):
    rs=[int(x) for x in XR.findall(s)]
    if not rs: return set(),set()
    op=s.strip().split()[0].lower()
    if op.startswith(ST) or op.startswith('cmp'): return set(),set(rs)
    if op in ('umov',): return {rs[0]},set(rs[1:])
    if op.startswith(('ldr','ldp','mov','add','sub','madd','lsl','orr')): return {rs[0]},set(rs[1:])
    return set(),set(rs)

def live_profile(du, nreg):
    tl={r:[] for r in range(nreg)}
    for i,s in enumerate(lines):
        d,u=du(s)
        for r in u:
            if r<nreg: tl[r].append((i,'u'))
        for r in d:
            if r<nreg: tl[r].append((i,'d'))
    live=[set() for _ in lines]
    for r,evs in tl.items():
        evs.sort(); cur=None; lastu=None
        iv=[]
        for i,k in evs:
            if k=='d':
                if cur is not None and lastu is not None: iv.append((cur,lastu))
                cur,lastu=i,i
            elif cur is not None: lastu=i
            else: cur,lastu=0,i
        if cur is not None and lastu is not None: iv.append((cur,lastu))
        for a,b in iv:
            for i in range(a,b+1): live[i].add(r)
    return live

vlive=live_profile(vdu,32); xlive=live_profile(xdu,31)
stores=[(i,s) for i,s in enumerate(lines) if s.strip().startswith('str ')]
print(f"  producer {len(lines)} instructions, {len(stores)} stores\n")
print("   idx   free V regs   free X regs (0-17)")
worstv=99; worstx=99
for i,s in stores:
    fv=sorted(set(range(32))-vlive[i]); fx=sorted(set(range(18))-xlive[i])
    worstv=min(worstv,len(fv)); worstx=min(worstx,len(fx))
    if len(stores)<=8 or i in [t[0] for t in stores[:3]+stores[-2:]]:
        print(f"  {i:4d}   {len(fv):2d} {str(fv[:8]):28s} {len(fx):2d} {fx[:6]}")
print(f"\n  worst case over all 32 stores: {worstv} free V, {worstx} free X")
print(f"  chain needs: 4 V (2 masks, 1 quot, 1 loaded bank2) + 1 X (address)")
print(f"  verdict: {'OK' if worstv>=4 and worstx>=1 else 'TIGHT'}")
