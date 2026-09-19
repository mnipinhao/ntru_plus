#!/usr/bin/env python3
"""For every inserted chain, check that each register it clobbers is either
dead or redefined before its next read in the producer."""
import re
VR=re.compile(r'\bv(\d+)\.',re.I); QR=re.compile(r'\bq(\d+)\b',re.I)
ST=('str','st1','st2','st3','st4','stur')
ins=[]
for ln in open('../gt864-p28s-timing/candidate-main.timing.S'):
    s=re.sub(r'//.*','',ln).strip()
    if not s or s.startswith(('.','#')) or s.endswith(':'): continue
    ins.append(s)

def next_kind(i, r):
    """After instruction i, is v{r} first written (safe) or read (clobbered)?"""
    for j in range(i+1, len(ins)):
        s=ins[j]; op=s.split()[0].lower()
        rs=[int(x) for x in VR.findall(s)]+[int(x) for x in QR.findall(s)]
        if r not in rs: continue
        if op.startswith(ST): return 'READ', j, s          # store reads
        if op in ('umov','smov'): return 'READ', j, s      # umov reads its vector
        if op in ('mov','ins') and '[' in s.split(',')[0]:
            return 'READ', j, s                            # lane insert: dest survives
        if rs[0]==r and op not in ('mls','mla','smlal','smlal2','ins','sri','sli'):
            return 'WRITE', j, s
        return 'READ', j, s
    return 'DEAD', None, None

# replay the allocator exactly as emit.py does
exec(open('emit.py').read().split("def triple")[0])
bad=[]
pos=0
for i,l in enumerate(raw):
    c=code(l)
    if c is None: continue
    s=c.strip()
    m=re.match(r'str\s+q(\d+),\s*\[(x[01])(?:,\s*#(\d+))?\]',s)
    if m:
        n=int(m.group(1)); free=set(range(32))-live[pos]
        # pair path used by bank2
        f=sorted(free-{n})
        pair=f[:2] if len(f)>=2 else []
        # triple path used by bank0/bank1
        pool=free|{n}
        k=next((k for k in range(32) if all(((k+j)%32) in pool for j in (0,1,2))), None)
        trip=[(k+j)%32 for j in (0,1,2)] if k is not None else []
        for tag,regs in (('pair(bank2)',pair),('triple(bank0/1)',trip)):
            for r in regs:
                kind,j,t = next_kind(pos,r)
                if kind=='READ': bad.append((pos,tag,r,j,t))
    pos+=1
print(f"  clobbered-then-read violations: {len(bad)}")
for b in bad[:10]:
    print(f"    store {b[0]:4d}  {b[1]:16s} v{b[2]:<2d} read at {b[3]} : {b[4][:46]}")
