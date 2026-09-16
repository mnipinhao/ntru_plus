#!/usr/bin/env python3
"""Exact scalar identity for P45's proposed nine-instruction joint pack."""
from __future__ import annotations
import random

Q=3457
IDX0=(0,1,16,2,3,18,4,5,20,6,7,22,8,9,24,10)
IDX1=(11,26,12,13,28,14,15,30)

def scalar(values):
    out=[]
    for a,b in zip(values[0::2],values[1::2]):
        out += [a&255,((a>>8)|((b&15)<<4))&255,(b>>4)&255]
    return bytes(out)

def joint(a,b):
    even=a[0::2]+b[0::2];odd=a[1::2]+b[1::2]
    words=[(x|(y<<12))&0xffff for x,y in zip(even,odd)]
    thirds=[y>>4 for y in odd]
    table=bytearray()
    for x in words:table += bytes((x&255,x>>8))
    for x in thirds:table += bytes((x&255,x>>8))
    return bytes(table[i] for i in IDX0)+bytes(table[i] for i in IDX1)

def main():
    # Exhaust the arithmetic identity for one coefficient pair.
    for a in range(Q):
        for b in range(Q):
            assert scalar([a,b]) == bytes((a&255,((a>>8)|((b&15)<<4))&255,b>>4))
    rng=random.Random(450864)
    cases=[[0]*16,[Q-1]*16,list(range(16))]
    cases += [[rng.randrange(Q) for _ in range(16)] for _ in range(10000)]
    for values in cases:assert joint(values[:8],values[8:])==scalar(values)
    print(f"P45 oracle passed: {Q*Q} coefficient pairs and {len(cases)} exact 24-byte records")
if __name__=="__main__":main()
