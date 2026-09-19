#!/usr/bin/env python3
"""Recover P29's scratch-offset -> natural-position permutation exactly.

Provenance rule: a destination keeps its provenance when it is also a source
(the normalise chain modifies its value in place); `ldr` from the scratch sets
provenance; `ext` marks the high half; anything else clears it.
"""
import re, json
from pathlib import Path
SRC = Path('../gt864-p29-direct-st3/candidate-main-route.alloc.S')
lines=[]
for ln in SRC.read_text().splitlines():
    s=re.sub(r'//.*','',ln).strip()
    if not s or s.startswith(('.','#')) or s.endswith(':'): continue
    lines.append(s)

prov={}; pos=0; recs=[]
for s in lines:
    m=re.match(r'ldr\s+q(\d+),\s*\[x1(?:,\s*#(\d+))?\]',s)
    if m: prov[int(m.group(1))]=('lo',int(m.group(2) or 0)); continue
    m=re.match(r'ext\s+v(\d+)\.16b,\s*v(\d+)\.16b,\s*v(\d+)\.16b,\s*#8',s,re.I)
    if m:
        d,a=int(m.group(1)),int(m.group(2))
        p=prov.get(a); prov[d]=('hi',p[1]) if p else None; continue
    m=re.match(r'st3\s+\{v(\d+)\.4H,\s*v(\d+)\.4H,\s*v(\d+)\.4H\},\s*\[x2\](?:,\s*#(\d+))?',s,re.I)
    if m:
        recs.append((pos,[prov.get(int(m.group(i))) for i in (1,2,3)]))
        pos+=int(m.group(4) or 0); continue
    m=re.match(r'add\s+x2,\s*x2,\s*#(\d+)',s)
    if m: pos+=int(m.group(1)); continue
    m=re.match(r'[a-z0-9]+\s+v(\d+)\.',s,re.I)
    if m:
        d=int(m.group(1))
        op=s.split()[0].lower()
        srcs=[int(x) for x in re.findall(r'v(\d+)\.',s)][1:]
        # mls/mla and friends accumulate into their destination, so it survives
        rmw = op in ('mls','mla','smlal','smlal2','sri','sli','ins','bit','bif','bsl')
        if not rmw and d not in srcs: prov[d]=None
    continue
bad=sum(1 for _,v in recs if any(x is None for x in v))
print(f"  {len(recs)} ST3 records, {bad} with unresolved provenance")
print("\n  natural byte   lane0        lane1        lane2")
f=lambda v: f"{v[0]}:{v[1]:4d}" if v else "?"
for p,v in recs[:8]: print(f"    {p:6d}      {f(v[0]):12s} {f(v[1]):12s} {f(v[2]):12s}")
print("    ...")
for p,v in recs[-4:]: print(f"    {p:6d}      {f(v[0]):12s} {f(v[1]):12s} {f(v[2]):12s}")
Path('perm.json').write_text(json.dumps(
    [{'natural':p,'lanes':[list(x) if x else None for x in v]} for p,v in recs], indent=1))
