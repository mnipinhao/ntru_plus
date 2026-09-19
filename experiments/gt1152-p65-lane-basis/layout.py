#!/usr/bin/env python3
"""The rebase contract, as an exact index map.

Source (basemul output, the NTT domain) -- lane is t within a group of eight:

    old_halfword(h, j, tg, c, u) = h*576 + j*64 + tg*32 + c*8 + u

Destination -- lane is (component, half), one vector per (j, t):

    new_halfword(j, t, c, h) = j*128 + t*8 + (c + 4*h)

with t = tg*8 + u.  Both cover 1152 coefficients; the destination is exactly the
2304-byte scratch already allocated.
"""
def old(h,j,tg,c,u): return h*576 + j*64 + tg*32 + c*8 + u
def new(j,t,c,h):    return j*128 + t*8 + (c + 4*h)

seen_o=set(); seen_n=set(); pairs=[]
for h in range(2):
  for j in range(9):
    for tg in range(2):
      for c in range(4):
        for u in range(8):
          t=tg*8+u
          o,n=old(h,j,tg,c,u), new(j,t,c,h)
          seen_o.add(o); seen_n.add(n); pairs.append((o,n))
print(f"  {len(pairs)} coefficients mapped")
print(f"  source indices  : {len(seen_o)} distinct, range {min(seen_o)}..{max(seen_o)}")
print(f"  dest indices    : {len(seen_n)} distinct, range {min(seen_n)}..{max(seen_n)}")
print(f"  bijection       : {len(seen_o)==len(seen_n)==1152 and max(seen_n)==1151}")
print()
print("  one transpose group (j=0, tg=0): eight source vectors ->")
for c in range(4):
  for h in range(2):
    base=old(h,0,0,c,0)
    print(f"    V[{c+4*h}] = halfwords {base}..{base+7}  (component {c}, half {h})   byte offset {2*base}")
print("  after the 8x8 transpose, W[u] holds lanes (c,h) for t=u, stored at")
for u in range(3):
  print(f"    W[{u}] -> halfwords {new(0,u,0,0)}..{new(0,u,3,1)}  byte offset {2*new(0,u,0,0)}")
print("    ...")
