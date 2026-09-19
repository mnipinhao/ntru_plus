#!/usr/bin/env python3
"""Physical vector-register pressure of packed_i9.

Live range = one def to the last use before the NEXT def of the same register.
The def/use rule matters: stores and umov READ their vector operand, mls/mla
accumulate into the destination, and `mov Vd.d[1], Vn.d[0]` / `ins Vd.d[1], Xn`
write one lane so the destination survives.
"""
import re, sys, collections
VR=re.compile(r'\bv(\d+)\.',re.I); QR=re.compile(r'\bq(\d+)\b',re.I); DR=re.compile(r'\bd(\d+)\b',re.I)
RMW=('mls','mla','smlal','smlal2','sri','sli','bit','bif','bsl')
ST=('str','st1','st2','st3','st4','stur')
def du(s):
    op=s.split()[0].lower()
    vs=[int(x) for x in VR.findall(s)]+[int(x) for x in QR.findall(s)]+[int(x) for x in DR.findall(s)]
    if not vs: return set(),set()
    if op.startswith(ST): return set(),set(vs)
    if op in ('umov','smov'): return set(),set(vs)
    if op in RMW: return {vs[0]},set(vs)
    if op in ('mov','ins') and '[' in s.split(',')[0]: return {vs[0]},set(vs)
    return {vs[0]},set(vs[1:])
def profile(path):
    ins=[]
    for ln in open(path):
        s=re.sub(r'//.*','',ln).strip()
        if not s or s.startswith(('.','#')) or s.endswith(':'): continue
        ins.append(s)
    tl={r:[] for r in range(32)}
    for i,s in enumerate(ins):
        d,u=du(s)
        for r in u: tl[r].append((i,'u'))
        for r in d: tl[r].append((i,'d'))
    live=[0]*len(ins)
    for r,evs in tl.items():
        evs.sort(key=lambda e:(e[0],e[1]=='d')); cur=lastu=None; iv=[]
        for i,k in evs:
            if k=='d':
                if cur is not None: iv.append((cur,lastu))
                cur=lastu=i
            elif cur is not None: lastu=i
            else: cur,lastu=0,i
        if cur is not None: iv.append((cur,lastu))
        for a,b in iv:
            for i in range(a,b+1): live[i]+=1
    return ins, live
for p,lbl in ((sys.argv[1] if len(sys.argv)>1 else '../gt1152-p10-kem/inverse9.S','packed_i9 (1152)'),):
    ins,live=profile(p)
    h=collections.Counter(live); n=len(ins)
    print(f"  {lbl}: {n} instructions, peak live {max(live)}")
    print("  pressure histogram:")
    for v in sorted(h):
        if h[v]*100//n>=2 or v>=max(live)-2:
            print(f"    {v:3d}: {h[v]:4d} ({h[v]*100/n:5.1f}%) {'#'*max(1,h[v]*50//n)}")
    for k in (4,8,12,16):
        f=sum(1 for x in live if x<=32-k)
        print(f"  slots with >= {k:2d} free: {f:4d}/{n} ({f*100/n:5.1f}%)")
