#!/usr/bin/env python3
"""Author the three fused producer kernels from P28's allocated producer.

Natural order is n = top*432 + t*27 + row*3 + component, so the ST3 base for
(top,t) is 864*top + 54*t bytes.  The producer stores at [x0,#16t] for top 0 and
[x1,#16t] for top 1, giving a linear map with no permutation table.

  bank0 (call 1)  ST3#1 = {b0.low, b0.high, b2.low }   at base
  bank1 (call 2)  ST3#2 = {b1.low, b1.high, b2.high}   at base + 24
  bank2 (call 3)  normalises its own output and keeps the plain store

Registers: x2 natural output base, x3 address scratch (dead after instr 326),
x4 composite table extended with four broadcast ternary constants, x17 scratch
base.  Each chain needs two free vector registers; the worst store point has
three free.
"""
import re, sys
from pathlib import Path

SRC = Path('../gt864-p28s-timing/candidate-main.timing.S')
VR=re.compile(r'\bv(\d+)\.',re.I); QR=re.compile(r'\bq(\d+)\b',re.I)
RMW=('mls','mla','smlal','smlal2','ins','sri','sli','bit','bif','bsl')
ST=('str','st1','st2','st3','st4','stur')
CONST=1024          # byte offset of the ternary constants inside the x4 table
B2_TOP0, B2_TOP1 = 1024, 1280   # bank2 Q blocks inside the scratch

raw = SRC.read_text().splitlines()
def code(l):
    s=re.sub(r'//.*','',l).rstrip(); t=s.strip()
    return None if (not t or t.startswith(('.','#')) or t.endswith(':')) else s
idx=[i for i,l in enumerate(raw) if code(l) is not None]
ins=[code(raw[i]).strip() for i in idx]

def du(s):
    """Def/use of vector registers.  Getting this exactly right matters:
      - stores and umov/smov READ their vector operand, they do not define it
      - mls/mla accumulate into the destination, so it is read too
      - `mov Vd.d[1], Vn.d[0]` and `ins Vd.d[1], Xn` write ONE LANE, so the rest
        of Vd survives and the destination is read as well
    """
    op=s.split()[0].lower()
    vs=[int(x) for x in VR.findall(s)]+[int(x) for x in QR.findall(s)]
    if not vs: return set(),set()
    if op.startswith(ST): return set(),set(vs)
    if op in ('umov','smov'): return set(),set(vs)
    if op in RMW: return {vs[0]},set(vs)
    if op in ('mov','ins') and '[' in s.split(',')[0]: return {vs[0]},set(vs)
    return {vs[0]},set(vs[1:])

# physical liveness by def..last-use-before-next-def
tl={r:[] for r in range(32)}
for i,s in enumerate(ins):
    d,u=du(s)
    for r in u: tl[r].append((i,'u'))
    for r in d: tl[r].append((i,'d'))
live=[set() for _ in ins]
for r,evs in tl.items():
    evs.sort(key=lambda e: (e[0], e[1]=='d')); cur=lastu=None; iv=[]
    for i,k in evs:
        if k=='d':
            if cur is not None: iv.append((cur,lastu))
            cur=lastu=i
        elif cur is not None: lastu=i
        else: cur,lastu=0,i
    if cur is not None: iv.append((cur,lastu))
    for a,b in iv:
        for i in range(a,b+1): live[i].add(r)

def triple(free, n):
    """ST3 needs Vt,Vt+1,Vt+2 consecutive (wrapping).  The stored value's own
    register frees up once the chain has consumed it, so it may join the pool."""
    pool = free | {n}
    for k in range(32):
        if all(((k+j) % 32) in pool for j in (0,1,2)):
            return k
    return None

def normalise(n,a,b):
    return [f"ldr q{a}, [x4, #{CONST}]",
            f"cmgt v{b}.8h, v{n}.8h, v{a}.8h",
            f"ldr q{a}, [x4, #{CONST+16}]",
            f"cmgt v{a}.8h, v{a}.8h, v{n}.8h",
            f"add v{n}.8h, v{n}.8h, v{b}.8h",
            f"sub v{n}.8h, v{n}.8h, v{a}.8h",
            f"ldr q{a}, [x4, #{CONST+32}]",
            f"sqrdmulh v{b}.8h, v{n}.8h, v{a}.8h",
            f"ldr q{a}, [x4, #{CONST+48}]",
            f"mls v{n}.8h, v{b}.8h, v{a}.8h"]

def chain(kind,n,k,top,t,orig):
    if kind=='bank2':
        _,a,b = k
        return normalise(n,a,b) + [orig]
    """Normalise straight into the ST3 triple k,k+1,k+2 so no extra register
    is needed beyond it; k+1 and k+2 double as the masks and the constant."""
    A,B,C = k%32, (k+1)%32, (k+2)%32
    out=[f"ldr q{C}, [x4, #{CONST}]",
         f"cmgt v{B}.8h, v{n}.8h, v{C}.8h",
         f"ldr q{C}, [x4, #{CONST+16}]",
         f"cmgt v{C}.8h, v{C}.8h, v{n}.8h",
         f"add v{A}.8h, v{n}.8h, v{B}.8h",
         f"sub v{A}.8h, v{A}.8h, v{C}.8h",
         f"ldr q{C}, [x4, #{CONST+32}]",
         f"sqrdmulh v{B}.8h, v{A}.8h, v{C}.8h",
         f"ldr q{C}, [x4, #{CONST+48}]",
         f"mls v{A}.8h, v{B}.8h, v{C}.8h"]
    if kind=='bank2':
        out.append(f"str q{A}, {orig.split(chr(44),1)[1].strip()}")
        return out
    b2 = (B2_TOP0 if top==0 else B2_TOP1) + 16*t
    base = 864*top + 54*t + (24 if kind=='bank1' else 0)
    out.append("ldr x17, [sp, #8]")            # bank2 scratch base
    out.append(f"ldr q{C}, [x17, #{b2}]")
    if kind=='bank1':
        out.append(f"ext v{C}.16b, v{C}.16b, v{C}.16b, #8")
    out.append(f"ext v{B}.16b, v{A}.16b, v{A}.16b, #8")
    out.append("ldr x17, [sp, #0]")            # natural output base
    out.append(f"add x17, x17, #{base}")
    out.append(f"st3 {{v{A}.4h, v{B}.4h, v{C}.4h}}, [x17]")
    return out

def build(kind, path, sym, limit=99):
    body=[]; k=0; worst=99
    for i,l in enumerate(raw):
        c=code(l)
        if c is None: body.append(l); continue
        j=idx.index(i) if False else None
        body.append(l)
    # rebuild properly: walk instruction stream, substituting stores
    body=[]; pos=0; worst=99; nstore=0; deferred=[]
    for i,l in enumerate(raw):
        c=code(l)
        if c is None:
            body.append(l); continue
        s=c.strip()
        m=re.match(r'str\s+q(\d+),\s*\[(x[01])(?:,\s*#(\d+))?\]',s)
        if m:
            n=int(m.group(1)); top=0 if m.group(2)=='x0' else 1
            t=int(m.group(3) or 0)//16
            free=set(range(32))-live[pos]
            if kind=='bank2':
                f=sorted(free-{n})
                k=('pair', f[0], f[1]) if len(f)>=2 else None
            else:
                k=triple(free,n)
            ind=c[:len(c)-len(c.lstrip())]
            if k is None or nstore>=limit:
                body.append(l); deferred.append((top,t))    # keep the raw store
            else:
                for e in chain(kind,n,k,top,t,s): body.append(ind+e)
                nstore+=1
        else:
            body.append(l)
        pos+=1
    txt="\n".join(body)
    if kind!='bank2':
        txt=txt.replace("p28_paired_i16:\n",
                        "p28_paired_i16:\n        sub sp, sp, #16\n"
                        "        stp x2, x17, [sp]\n", 1)
        txt=re.sub(r'^(\s*)ret\s*$', r'\1add sp, sp, #16\n\1ret', txt, count=1, flags=re.M)
    txt=txt.replace("p28_paired_i16", sym)
    Path(path).write_text(txt+"\n")
    n_out=len([1 for l in txt.splitlines() if code(l) is not None])
    print(f"  {path:22s} {n_out:4d} instructions, {nstore}/32 fused, "
          f"{len(deferred)} deferred")
    return deferred

import os
LIM=int(os.environ.get('P60_LIMIT','99'))
d0=build('bank0','fused_bank0.S','p60_fused_bank0',LIM)
d1=build('bank1','fused_bank1.S','p60_fused_bank1',LIM)
d2=build('bank2','fused_bank2.S','p60_fused_bank2')
import json
json.dump({'bank0':d0,'bank1':d1,'bank2':d2}, open('deferred.json','w'), indent=1)
print(f"\n  deferred (top,t) groups: bank0 {d0}\n                           bank1 {d1}\n                           bank2 {d2}")
