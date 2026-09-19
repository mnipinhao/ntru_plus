#!/usr/bin/env python3
"""Symbolic vector-register pressure of straight-line Slothy sources.

Live range of a symbolic value = [first def, last use].  Straight-line code with
no branches, so maximum concurrent live values is the exact pressure lower bound
any allocator must meet.
"""
import re, sys, collections

SYM = re.compile(r'[VQD]<([A-Za-z0-9_]+)>')
# instructions whose first vector operand is written, not read
DEFS_FIRST = re.compile(r'^(ldr|ld1|ld2|ld3|ld4|mov|movi|dup|orr|and|eor|add|sub|mul|smull|smull2|'
                        r'sqrdmulh|sqdmulh|cmgt|cmge|cmeq|trn1|trn2|zip1|zip2|uzp1|uzp2|ext|tbl|'
                        r'shl|sshr|ushr|neg|rev\d*|addp|sqadd|sqsub|umull|xtn|sqxtn)\b', re.I)
# read-modify-write: first operand is both read and written
RMW = re.compile(r'^(mls|mla|smlal|smlal2|sri|sli|ins|bit|bif|bsl)\b', re.I)
STORES = re.compile(r'^(str|st1|st2|st3|st4|stur)\b', re.I)

def parse(path):
    insns = []
    for ln in open(path):
        s = re.sub(r'//.*', '', ln).strip()
        if not s or s.startswith(('.', '#')) or s.endswith(':'):
            continue
        op = s.split()[0].lower()
        syms = SYM.findall(s)
        if not syms:
            insns.append((op, set(), set())); continue
        first = syms[0]
        if STORES.match(op):                 # every symbolic operand is read
            d, u = set(), set(syms)
        elif RMW.match(op):
            d, u = {first}, set(syms)
        elif DEFS_FIRST.match(op):
            d, u = {first}, set(syms[1:])
        else:                                # unknown: conservative, read+write
            d, u = {first}, set(syms)
        insns.append((op, d, u))
    return insns

def pressure(insns):
    first_def, last_use = {}, {}
    for i, (op, d, u) in enumerate(insns):
        for r in d:
            first_def.setdefault(r, i)
        for r in u | d:
            last_use[r] = i
    live, peak, peak_at, cur = set(), 0, 0, set()
    for i, (op, d, u) in enumerate(insns):
        for r in d | u:
            cur.add(r)
        n = len(cur)
        if n > peak:
            peak, peak_at, live = n, i, set(cur)
        for r in list(cur):
            if last_use.get(r, -1) <= i:
                cur.discard(r)
    return peak, peak_at, live, len(first_def)

for path in sys.argv[1:]:
    ins = parse(path)
    peak, at, live, nval = pressure(ins)
    ops = collections.Counter(o for o, _, _ in ins)
    print(f"{path}")
    print(f"  instructions {len(ins):5d}   distinct symbolic values {nval:4d}"
          f"   PEAK LIVE {peak:3d}  (at instruction {at})")
    print(f"  top opcodes: " + ", ".join(f"{k}={v}" for k, v in ops.most_common(8)))
    print()
