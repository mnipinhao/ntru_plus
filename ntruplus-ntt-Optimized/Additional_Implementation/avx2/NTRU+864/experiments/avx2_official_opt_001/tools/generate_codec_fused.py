#!/usr/bin/env python3
"""Generate asm/ntruplus864_officialopt_codec_fused.s (NTRU+864 AVX2, Option A).

Fuses the Official layout permutations into the byte codec:
  tobytes_fused   == poly_ntt_pack (freeze + 6-way -> natural) + poly_tobytes_raw
  frombytes_fused == poly_frombytes_raw (+ canonical check) + poly_ntt_unpack
without the 1728-byte stack/in-place round trip.  Every arithmetic and
in-128-bit-lane shuffle instruction is copied, with the same immediates and
the same data dependences, from the pinned upstream pack.s (line ranges cited
below); only the following change:
  1. Cross-lane data movement.  The two vperm2i128 stages that meet at the
     natural-order memory image (pack's output perm + tobytes_raw's input
     perm; frombytes_raw's output perm + unpack's input perm) are composed
     into ONE vperm2i128 (vinserti128 for a lo|lo pair) per register, i.e.
     12 instead of 24 per 192 coefficients.  The byte-side permutes are
     folded into memory access: tobytes stores the six 16-byte halves that
     pack.s:66-72 would permute (vmovdqu xmm / vextracti128 to memory), and
     frombytes forms pack.s:154-156's half-pairs with 16-byte loads and
     vinserti128 from memory.
  2. The 64-coefficient codec blocks and 96-coefficient layout blocks are
     interleaved in 192-coefficient super-iterations (2 layout blocks = 3
     codec blocks, 4 iterations) plus one 96-coefficient final part (one
     64-coefficient codec block and the 32-coefficient tail).  The tobytes
     tail runs the ymm body on the pack registers whose upper lanes hold the
     tail coefficients and stores those upper lanes (vextracti128 to memory);
     the frombytes tail is Official's xmm tail.
  3. Instruction order: each straight-line block is list-scheduled on its
     data-dependence graph (critical path first, register-pressure capped;
     see Kernel.schedule).  Without it the fused chains starved the ports
     (measured: tobytes ~570 vs Official ~495 cycles in a tight loop).
  4. frombytes accumulates the per-block vpmaxuw into one register and does
     the single vpcmpgtw/vpmovmskb at the end: max_i a_i > q-1 iff some
     a_i > q-1, so the return value is identical to Official's OR of
     per-block masks (both normalised by setne).
Physical registers are assigned by a deterministic linear-scan allocator
(free a source at its last use, lowest free register first).

  generate_codec_fused.py --experiment .           # write
  generate_codec_fused.py --experiment . --check   # verify file is current
"""

import argparse
import hashlib
import sys
from pathlib import Path

N_REGS = 16
OUT = "asm/ntruplus864_officialopt_codec_fused.s"
TOB = "ntruplus864_officialopt_tobytes_fused"
FROMB = "ntruplus864_officialopt_frombytes_fused"


class Kernel:
    """Straight-line code over virtual registers; emit() maps them to ymm."""

    def __init__(self, pinned):
        self.ins = []           # ("op"|"load"|"store", ...)
        self.pinned = dict(pinned)  # virtual -> physical (never freed)
        self.n = 0

    def v(self, prefix="t"):
        self.n += 1
        return f"%{prefix}{self.n}"

    def op(self, mnem, dst, *srcs, imm=None, x=False):
        """Intel operand order: dst = mnem(srcs[0], srcs[1], ...)."""
        self.ins.append(("op", mnem, imm, x, dst, list(srcs)))
        return dst

    def load(self, mnem, dst, mem, x=False):
        self.ins.append(("load", mnem, x, dst, mem))
        return dst

    def store(self, mnem, src, mem, x=False, imm=None):
        self.ins.append(("store", mnem, x, src, mem, imm))

    def schedule(self, limit):
        """Deterministic greedy list scheduling of the straight-line block.
        Ready instructions are ordered by the latency-weighted longest path to
        the end of the block (ties: original order), subject to at most
        `limit` simultaneously live non-pinned values; if no ready instruction
        fits, the one that grows pressure least is taken.  Only true data
        dependences constrain the order: loads read only the input array and
        stores write only the output array (the codec's no-overlap contract),
        and the pinned accumulator is chained through its successive writes."""
        ins = self.ins
        n = len(ins)
        defs, deps = {}, []
        for i, x in enumerate(ins):
            deps.append(sorted({defs[u] for u in uses_of(x) if u in defs}))
            if def_of(x) is not None:
                defs[def_of(x)] = i
        users = [[] for _ in range(n)]
        for i, d in enumerate(deps):
            for j in d:
                users[j].append(i)
        prio = [0] * n
        for i in reversed(range(n)):
            prio[i] = latency(ins[i]) + max((prio[j] for j in users[i]), default=0)
        remaining = {}
        for x in ins:
            for u in uses_of(x):
                remaining[u] = remaining.get(u, 0) + 1
        live, order = set(), []
        waiting = [len(d) for d in deps]
        ready = [i for i in range(n) if waiting[i] == 0]
        while ready:
            best = None
            for i in ready:
                x = ins[i]
                u = uses_of(x)
                kills = sum(1 for r in set(u) if r not in self.pinned and remaining[r] == u.count(r))
                d = def_of(x)
                grow = (d is not None and d not in self.pinned) - kills
                key = (True, prio[i], -i) if len(live) + grow <= limit else (False, -grow, -i)
                if best is None or key > best[0]:
                    best = (key, i)
            i = best[1]
            ready.remove(i)
            x = ins[i]
            for r in uses_of(x):
                remaining[r] -= 1
                if remaining[r] == 0:
                    live.discard(r)
            d = def_of(x)
            if d is not None and d not in self.pinned and remaining.get(d, 0):
                live.add(d)
            order.append(i)
            for j in users[i]:
                waiting[j] -= 1
                if waiting[j] == 0:
                    ready.append(j)
        if len(order) != n:
            raise ValueError("scheduling left instructions behind")
        self.ins = [ins[i] for i in order]

    def emit(self):
        self.schedule(N_REGS - len(self.pinned))
        # last-use index per virtual register
        last = {}
        for i, ins in enumerate(self.ins):
            for r in uses_of(ins):
                last[r] = i
        free = [r for r in range(N_REGS) if r not in self.pinned.values()]
        phys = dict(self.pinned)
        out = []
        for i, ins in enumerate(self.ins):
            srcs = uses_of(ins)
            for r in srcs:
                if r not in phys:
                    raise ValueError(f"use before def {r} at {i}")
            # release sources that die here (dst may then reuse them)
            for r in dict.fromkeys(srcs):
                if last[r] == i and r not in self.pinned:
                    free.append(phys[r])
            free.sort()
            dst = def_of(ins)
            if dst is not None:
                if dst in phys and dst not in srcs:
                    raise ValueError(f"redefinition of {dst}")
                if dst in self.pinned:
                    if dst not in srcs:
                        raise ValueError(f"non-accumulating write to pinned {dst}")
                    out.append(render(ins, phys))
                    continue
                if not free:
                    raise ValueError(f"out of registers at {i}: {ins}")
                phys[dst] = free.pop(0)
                if dst not in last:     # dead definition
                    free.append(phys[dst])
            out.append(render(ins, phys))
        return out


LATENCY = {"vpmulhrsw": 5, "vpmullw": 5, "vperm2i128": 3, "vinserti128": 3, "load": 6}


def latency(ins):
    """Scheduling weights (approximate Golden/Redwood Cove latencies)."""
    return LATENCY.get("load" if ins[0] == "load" else ins[1], 1)


def uses_of(ins):
    kind = ins[0]
    if kind == "op":
        return [s for s in ins[5] if isinstance(s, str) and s.startswith("%")]
    if kind == "load":
        return []
    return [ins[3]]


def def_of(ins):
    if ins[0] == "op":
        return ins[4]
    if ins[0] == "load":
        return ins[3]
    return None


def reg(phys, v, x):
    return f"%{'x' if x else 'y'}mm{phys[v]}"


def operand(phys, s, x):
    return reg(phys, s, x) if isinstance(s, str) and s.startswith("%") else s


def render(ins, phys):
    kind = ins[0]
    if kind == "op":
        _, mnem, imm, x, dst, srcs = ins
        ops = [operand(phys, s, x) for s in reversed(srcs)]
        if mnem == "vinserti128":   # vinserti128 $1, %xmm_src2|m128, %ymm_src1, %ymm_dst
            ops = [operand(phys, srcs[1], True), reg(phys, srcs[0], False)]
        parts = ([f"${imm}"] if imm is not None else []) + ops + [reg(phys, dst, x)]
        return f"{mnem} " + ", ".join(parts)
    if kind == "load":
        _, mnem, x, dst, mem = ins
        return f"{mnem} {mem}, {reg(phys, dst, x)}"
    _, mnem, x, src, mem, imm = ins
    pre = f"${imm}, " if imm is not None else ""
    return f"{mnem} {pre}{reg(phys, src, x)}, {mem}"


# ------------------------------------------------------------------ tobytes
def pack_block(k, base):
    """pack.s:394-473 (load, freeze, 16/32-bit and qword in-lane stages) on
    the 96 coefficients at base(%rsi).  Returns the six pre-perm registers
    p[k] = [H_k | H_{k+6}] (H_i = natural coefficients 8i..8i+7)."""
    r = [k.load("vmovdqa", k.v("r"), f"{base + 32 * i}(%rsi)") for i in range(6)]
    f = []
    # pack.s:401-437: Official's per-lane sequence (vpmulhrsw v, vpmullw q,
    # vpsubw; vpsraw 15, vpand q, vpaddw), issued register by register rather
    # than interleaved over all six so that it fits next to live carries.
    for x in r:
        t = k.op("vpmulhrsw", k.v(), x, "%V")
        t = k.op("vpmullw", k.v(), t, "%Q")
        x = k.op("vpsubw", k.v(), x, t)
        f.append(x)
    g = []
    for x in f:
        t = k.op("vpsraw", k.v(), x, imm=15)
        t = k.op("vpand", k.v(), t, "%Q")
        g.append(k.op("vpaddw", k.v(), x, t))
    r0, r1, r2, r3, r4, r5 = g
    # pack.s:440-451
    def pair16(lo, hi):
        s = k.op("vpslld", k.v(), hi, imm=16)
        t = k.op("vpsrld", k.v(), lo, imm=16)
        a = k.op("vpblendw", k.v(), lo, s, imm="0xAA")
        b = k.op("vpblendw", k.v(), t, hi, imm="0xAA")
        return a, b
    y6, y9 = pair16(r0, r1)
    y7, y10 = pair16(r2, r3)
    y8, y11 = pair16(r4, r5)
    # pack.s:454-465
    def pair32(lo, hi):
        s = k.op("vpsllq", k.v(), hi, imm=32)
        t = k.op("vpsrlq", k.v(), lo, imm=32)
        a = k.op("vpblendd", k.v(), lo, s, imm="0xAA")
        b = k.op("vpblendd", k.v(), t, hi, imm="0xAA")
        return a, b
    z0, z3 = pair32(y6, y7)
    z1, z4 = pair32(y8, y9)
    z2, z5 = pair32(y10, y11)
    # pack.s:468-473
    def pairq(a, b):
        return (k.op("vpunpcklqdq", k.v(), a, b), k.op("vpunpckhqdq", k.v(), a, b))
    p0, p3 = pairq(z0, z1)
    p1, p4 = pairq(z2, z3)
    p2, p5 = pairq(z4, z5)
    return [p0, p1, p2, p3, p4, p5]


def lanes(k, pairs):
    """One cross-lane op per output: pairs of (reg, half) -> [lo | hi]."""
    out = []
    for (a, ha), (b, hb) in pairs:
        if ha == 0 and hb == 0:
            out.append(k.op("vinserti128", k.v(), a, b, imm=1))
        else:
            out.append(k.op("vperm2i128", k.v(), a, b, imm=f"0x{2 + hb}{ha}"))
    return out


def tobytes_body(k, t, out_off, tail=False):
    """pack.s:18-72 on t = ([G0|G4],[G1|G5],[G2|G6],[G3|G7]); stores 96 bytes
    at out_off(%rdi).  tail=True: pack.s:85-135 semantics on the upper lanes
    (G0..G3 there are the last 32 coefficients); stores 48 bytes."""
    t4, t5, t6, t7 = t
    u0 = k.op("vpunpcklqdq", k.v(), t4, t6)
    u1 = k.op("vpunpckhqdq", k.v(), t4, t6)
    u2 = k.op("vpunpcklqdq", k.v(), t5, t7)
    u3 = k.op("vpunpckhqdq", k.v(), t5, t7)
    a = k.op("vpsllq", k.v(), u2, imm=32)
    b = k.op("vpsrlq", k.v(), u0, imm=32)
    c = k.op("vpsllq", k.v(), u3, imm=32)
    d = k.op("vpsrlq", k.v(), u1, imm=32)
    v4 = k.op("vpblendd", k.v(), u0, a, imm="0xAA")
    v5 = k.op("vpblendd", k.v(), b, u2, imm="0xAA")
    v6 = k.op("vpblendd", k.v(), u1, c, imm="0xAA")
    v7 = k.op("vpblendd", k.v(), d, u3, imm="0xAA")
    a = k.op("vpsllq", k.v(), v6, imm=16)
    b = k.op("vpsrlq", k.v(), v4, imm=16)
    c = k.op("vpsllq", k.v(), v7, imm=16)
    d = k.op("vpsrlq", k.v(), v5, imm=16)
    w0 = k.op("vpblendw", k.v(), v4, a, imm="0xAA")
    w1 = k.op("vpblendw", k.v(), b, v6, imm="0xAA")
    w2 = k.op("vpblendw", k.v(), v5, c, imm="0xAA")
    w3 = k.op("vpblendw", k.v(), d, v7, imm="0xAA")
    # bit packing, pack.s:41-48
    m = k.op("vpsllw", k.v(), w1, imm=12)
    x0 = k.op("vpxor", k.v(), w0, m)
    m = k.op("vpsllw", k.v(), w2, imm=8)
    n = k.op("vpsrlw", k.v(), w1, imm=4)
    x1 = k.op("vpxor", k.v(), n, m)
    m = k.op("vpsllw", k.v(), w3, imm=4)
    n = k.op("vpsrlw", k.v(), w2, imm=8)
    x2 = k.op("vpxor", k.v(), n, m)
    # byte arrangement, pack.s:50-68
    a = k.op("vpslld", k.v(), x1, imm=16)
    b = k.op("vpsrld", k.v(), x1, imm=16)
    s3 = k.op("vpblendw", k.v(), x0, a, imm="0xAA")
    s4 = k.op("vpblendw", k.v(), x2, x0, imm="0xAA")
    s5 = k.op("vpblendw", k.v(), b, x2, imm="0xAA")
    a = k.op("vpsllq", k.v(), s4, imm=32)
    b = k.op("vpsrlq", k.v(), s4, imm=32)
    y0 = k.op("vpblendd", k.v(), s3, a, imm="0xAA")
    y1 = k.op("vpblendd", k.v(), s5, s3, imm="0xAA")
    y2 = k.op("vpblendd", k.v(), b, s5, imm="0xAA")
    z3 = k.op("vpunpcklqdq", k.v(), y0, y1)
    z4 = k.op("vpblendd", k.v(), y2, y0, imm="0xCC")
    z5 = k.op("vpunpckhqdq", k.v(), y1, y2)
    # pack.s:66-72 stores [z3.lo|z4.lo] [z5.lo|z3.hi] [z4.hi|z5.hi]: the same
    # six 16-byte halves are stored directly (no vperm2i128); the tail
    # (pack.s:133-135) stores only the upper halves.
    if not tail:
        for i, z in enumerate((z3, z4, z5)):
            k.store("vmovdqu", z, f"{out_off + 16 * i}(%rdi)", x=True)
        out_off += 48
    for i, z in enumerate((z3, z4, z5)):
        k.store("vextracti128", z, f"{out_off + 16 * i}(%rdi)", imm=1)


def tobytes_iteration():
    """192 coefficients (384 B in) -> 288 B out."""
    k = Kernel({"%V": 15, "%Q": 14})
    p = pack_block(k, 0)
    # codec block 0 = H0..H7: [H0|H4] [H1|H5] [H2|H6] [H3|H7]
    t = lanes(k, [((p[0], 0), (p[4], 0)), ((p[1], 0), (p[5], 0)),
                  ((p[2], 0), (p[0], 1)), ((p[3], 0), (p[1], 1))])
    tobytes_body(k, t, 0)
    q = pack_block(k, 192)   # H12..H23: q[k] = [H_{12+k} | H_{18+k}]
    # block 1 = H8..H15, block 2 = H16..H23
    t1 = lanes(k, [((p[2], 1), (q[0], 0)), ((p[3], 1), (q[1], 0)),
                   ((p[4], 1), (q[2], 0)), ((p[5], 1), (q[3], 0))])
    t2 = lanes(k, [((q[4], 0), (q[2], 1)), ((q[5], 0), (q[3], 1)),
                   ((q[0], 1), (q[4], 1)), ((q[1], 1), (q[5], 1))])
    tobytes_body(k, t1, 96)
    tobytes_body(k, t2, 192)
    return k.emit()


def tobytes_final():
    """last 96 coefficients (192 B in) -> 144 B out."""
    k = Kernel({"%V": 15, "%Q": 14})
    p = pack_block(k, 0)
    t = lanes(k, [((p[0], 0), (p[4], 0)), ((p[1], 0), (p[5], 0)),
                  ((p[2], 0), (p[0], 1)), ((p[3], 0), (p[1], 1))])
    tobytes_body(k, t, 0)
    # tail H8..H11 sit in the upper lanes of p2..p5
    tobytes_body(k, [p[2], p[3], p[4], p[5]], 96, tail=True)
    return k.emit()


# ---------------------------------------------------------------- frombytes
def frombytes_body(k, off, acc):
    """pack.s:150-210 on 96 bytes at off(%rsi): returns
    ([G0|G4],[G1|G5],[G2|G6],[G3|G7]) and the updated vpmaxuw accumulator."""
    # pack.s:150-156 load 32-byte L4 L5 L6 and permute to a0=[c0|c3],
    # a1=[c1|c4], a2=[c2|c5] (c = 16-byte chunks); the same registers are
    # formed directly from 16-byte loads (no vperm2i128).
    a = []
    for c in range(3):
        lo = k.load("vmovdqu", k.v("l"), f"{off + 16 * c}(%rsi)", x=True)
        a.append(k.op("vinserti128", k.v(), lo, f"{off + 48 + 16 * c}(%rsi)", imm=1))
    return frombytes_inlane(k, a[0], a[1], a[2], acc)


def frombytes_inlane(k, a0, a1, a2, acc, x=False):
    s13 = k.op("vpshufd", k.v(), a0, imm="0x4E", x=x)
    b4 = k.op("vpblendd", k.v(), a0, a1, imm="0xCC", x=x)
    b5 = k.op("vpunpcklqdq", k.v(), s13, a2, x=x)
    b6 = k.op("vpblendd", k.v(), a1, a2, imm="0xCC", x=x)
    c12 = k.op("vpsrlq", k.v(), b4, imm=32, x=x)
    c13 = k.op("vpsllq", k.v(), b6, imm=32, x=x)
    d0 = k.op("vpblendd", k.v(), b4, b5, imm="0xAA", x=x)
    d1 = k.op("vpblendd", k.v(), c12, c13, imm="0xAA", x=x)
    d2 = k.op("vpblendd", k.v(), b5, b6, imm="0xAA", x=x)
    e12 = k.op("vpsrld", k.v(), d0, imm=16, x=x)
    e13 = k.op("vpslld", k.v(), d2, imm=16, x=x)
    f4 = k.op("vpblendw", k.v(), d0, d1, imm="0xAA", x=x)
    f5 = k.op("vpblendw", k.v(), e12, e13, imm="0xAA", x=x)
    f6 = k.op("vpblendw", k.v(), d1, d2, imm="0xAA", x=x)
    g0 = k.op("vpand", k.v(), f4, "%M", x=x)
    h = k.op("vpsrlw", k.v(), f4, imm=12, x=x)
    i = k.op("vpsllw", k.v(), f5, imm=4, x=x)
    h = k.op("vpxor", k.v(), h, i, x=x)
    g1 = k.op("vpand", k.v(), h, "%M", x=x)
    h = k.op("vpsrlw", k.v(), f5, imm=8, x=x)
    i = k.op("vpsllw", k.v(), f6, imm=8, x=x)
    h = k.op("vpxor", k.v(), h, i, x=x)
    g2 = k.op("vpand", k.v(), h, "%M", x=x)
    h = k.op("vpsrlw", k.v(), f6, imm=4, x=x)
    g3 = k.op("vpand", k.v(), h, "%M", x=x)
    k10 = k.op("vpslld", k.v(), g1, imm=16, x=x)
    k11 = k.op("vpslld", k.v(), g3, imm=16, x=x)
    k12 = k.op("vpsrld", k.v(), g0, imm=16, x=x)
    k13 = k.op("vpsrld", k.v(), g2, imm=16, x=x)
    l4 = k.op("vpblendw", k.v(), g0, k10, imm="0xAA", x=x)
    l5 = k.op("vpblendw", k.v(), g2, k11, imm="0xAA", x=x)
    l6 = k.op("vpblendw", k.v(), k12, g1, imm="0xAA", x=x)
    l7 = k.op("vpblendw", k.v(), k13, g3, imm="0xAA", x=x)
    m10 = k.op("vpsllq", k.v(), l5, imm=32, x=x)
    m11 = k.op("vpsllq", k.v(), l7, imm=32, x=x)
    m12 = k.op("vpsrlq", k.v(), l4, imm=32, x=x)
    m13 = k.op("vpsrlq", k.v(), l6, imm=32, x=x)
    n0 = k.op("vpblendd", k.v(), l4, m10, imm="0xAA", x=x)
    n1 = k.op("vpblendd", k.v(), l6, m11, imm="0xAA", x=x)
    n2 = k.op("vpblendd", k.v(), m12, l5, imm="0xAA", x=x)
    n3 = k.op("vpblendd", k.v(), m13, l7, imm="0xAA", x=x)
    f0 = k.op("vpunpcklqdq", k.v(), n0, n1, x=x)
    f1 = k.op("vpunpcklqdq", k.v(), n2, n3, x=x)
    f2 = k.op("vpunpckhqdq", k.v(), n0, n1, x=x)
    f3 = k.op("vpunpckhqdq", k.v(), n2, n3, x=x)
    # canonical check (pack.s:222-227 / 297-302), accumulated
    for f in (f0, f1, f2, f3):
        k.op("vpmaxuw", acc, acc, f)
    return [f0, f1, f2, f3], acc


def unpack_inlane(k, p, off):
    """pack.s:333-374 after its perm: p[k] = [H_k|H_{k+6}] -> 6-way, stored
    at off(%rdi)."""
    y10, y11, y12, y13, y14, y15 = p
    o = [None] * 6
    o[0] = k.op("vpunpcklqdq", k.v(), y10, y13)
    o[1] = k.op("vpunpckhqdq", k.v(), y10, y13)
    o[2] = k.op("vpunpcklqdq", k.v(), y11, y14)
    o[3] = k.op("vpunpckhqdq", k.v(), y11, y14)
    o[4] = k.op("vpunpcklqdq", k.v(), y12, y15)
    o[5] = k.op("vpunpckhqdq", k.v(), y12, y15)
    def pair(lo, hi, sh, blend):
        a = k.op(f"vpsllq", k.v(), hi, imm=sh)
        b = k.op(f"vpsrlq", k.v(), lo, imm=sh)
        return (k.op(blend, k.v(), lo, a, imm="0xAA"), k.op(blend, k.v(), b, hi, imm="0xAA"))
    # pack.s:341-352: (0,3)->(10,11) (1,4)->(12,13) (2,5)->(14,15)
    s10, s11 = pair(o[0], o[3], 32, "vpblendd")
    s12, s13 = pair(o[1], o[4], 32, "vpblendd")
    s14, s15 = pair(o[2], o[5], 32, "vpblendd")
    # pack.s:355-366: (10,13)->(0,1) (11,14)->(2,3) (12,15)->(4,5)
    w0, w1 = pair(s10, s13, 16, "vpblendw")
    w2, w3 = pair(s11, s14, 16, "vpblendw")
    w4, w5 = pair(s12, s15, 16, "vpblendw")
    for i, w in enumerate((w0, w1, w2, w3, w4, w5)):
        k.store("vmovdqa", w, f"{off + 32 * i}(%rdi)")


def frombytes_iteration():
    """288 B in -> 192 coefficients (384 B) out."""
    k = Kernel({"%M": 15, "%ACC": 14})
    b0, acc = frombytes_body(k, 0, "%ACC")
    b1, acc = frombytes_body(k, 96, acc)
    # G^b_i = H_{8b+i}; b[b][i] = [G_i | G_{i+4}]
    p = lanes(k, [((b0[0], 0), (b0[2], 1)), ((b0[1], 0), (b0[3], 1)),
                  ((b0[2], 0), (b1[0], 0)), ((b0[3], 0), (b1[1], 0)),
                  ((b0[0], 1), (b1[2], 0)), ((b0[1], 1), (b1[3], 0))])
    unpack_inlane(k, p, 0)
    b2, acc = frombytes_body(k, 192, acc)
    q = lanes(k, [((b1[0], 1), (b2[2], 0)), ((b1[1], 1), (b2[3], 0)),
                  ((b1[2], 1), (b2[0], 1)), ((b1[3], 1), (b2[1], 1)),
                  ((b2[0], 0), (b2[2], 1)), ((b2[1], 0), (b2[3], 1))])
    unpack_inlane(k, q, 192)
    return k.emit()


def frombytes_final():
    """last 144 B -> 96 coefficients; tail per pack.s:234-285."""
    k = Kernel({"%M": 15, "%ACC": 14})
    b0, acc = frombytes_body(k, 0, "%ACC")
    x0 = k.load("vmovdqu", k.v("l"), "96(%rsi)", x=True)
    x1 = k.load("vmovdqu", k.v("l"), "112(%rsi)", x=True)
    x2 = k.load("vmovdqu", k.v("l"), "128(%rsi)", x=True)
    xt, acc = frombytes_inlane(k, x0, x1, x2, acc, x=True)
    # the xmm results have zero upper lanes; H8..H11 = xt[0..3] (lower lane).
    # the accumulating vpmaxuw is always ymm, so the upper lane survives.
    p = lanes(k, [((b0[0], 0), (b0[2], 1)), ((b0[1], 0), (b0[3], 1)),
                  ((b0[2], 0), (xt[0], 0)), ((b0[3], 0), (xt[1], 0)),
                  ((b0[0], 1), (xt[2], 0)), ((b0[1], 1), (xt[3], 0))])
    unpack_inlane(k, p, 0)
    out = k.emit()
    return out + ["vpcmpgtw _16xqm1(%rip), %ymm14, %ymm14", "vpmovmskb %ymm14, %eax"]


def generate(pack_sha):
    L = []
    w = L.append
    w("# NTRU+864 Official AVX2: layout-fused byte codec (Option A), candidate code.")
    w("# GENERATED by tools/generate_codec_fused.py -- do not edit by hand.")
    w(f"# Source: upstream/supercop-avx2/pack.s sha256 {pack_sha}")
    w("#   tobytes_fused(r, a)   == poly_tobytes(r, a)   = poly_ntt_pack + poly_tobytes_raw")
    w("#   frombytes_fused(r, a) == poly_frombytes(r, a) = poly_frombytes_raw + poly_ntt_unpack")
    w("# All arithmetic / in-lane shuffles are Official's (same order, same immediates);")
    w("# the pair of cross-lane vperm2i128 stages meeting at the natural-order image is")
    w("# composed into one per register, and no stack or intermediate buffer is used.")
    w("# Pointer contract = Official: poly (a for tobytes, r for frombytes) 32-byte")
    w("# aligned (vmovdqa); byte arrays unaligned (vmovdqu).  No vzeroupper (as pack.s).")
    w("# The byte array and the poly must not overlap (no KEM call site overlaps them;")
    w("# Official poly_tobytes tolerates overlap through its stack copy, the fused one does not).")
    w("")
    w(".text")
    w(".p2align 5")
    w(f".global {TOB}")
    w(f".type {TOB},@function")
    w(f"{TOB}:")
    w("vmovdqa _16xv(%rip), %ymm15")
    w("vmovdqa _16xq(%rip), %ymm14")
    w("lea 1536(%rsi), %r8")
    w("")
    w(".p2align 5")
    w(f"{TOB}_loop:")
    L.extend(tobytes_iteration())
    w("")
    w("add $384, %rsi")
    w("add $288, %rdi")
    w("cmp %r8, %rsi")
    w(f"jb {TOB}_loop")
    w("")
    w("# coefficients 768..863: one 64-coefficient block + 32-coefficient tail")
    L.extend(tobytes_final())
    w("ret")
    w(f".size {TOB}, .-{TOB}")
    w("")
    w(".p2align 5")
    w(f".global {FROMB}")
    w(f".type {FROMB},@function")
    w(f"{FROMB}:")
    w("vmovdqa _low_mask(%rip), %ymm15")
    w("vpxor %ymm14, %ymm14, %ymm14")
    w("lea 1536(%rdi), %r8")
    w("")
    w(".p2align 5")
    w(f"{FROMB}_loop:")
    L.extend(frombytes_iteration())
    w("")
    w("add $384, %rdi")
    w("add $288, %rsi")
    w("cmp %r8, %rdi")
    w(f"jb {FROMB}_loop")
    w("")
    w("# coefficients 768..863")
    L.extend(frombytes_final())
    w("test %eax, %eax")
    w("setne %al")
    w("movzbl %al, %eax")
    w("ret")
    w(f".size {FROMB}, .-{FROMB}")
    w("")
    w(".section .note.GNU-stack,\"\",@progbits")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    root = args.experiment.resolve()
    pack = (root / "upstream/supercop-avx2/pack.s").read_bytes()
    text = generate(hashlib.sha256(pack).hexdigest())
    target = root / OUT
    if args.check:
        if not target.exists() or target.read_text() != text:
            print(f"{OUT} is stale; run make generate-codec", file=sys.stderr)
            return 1
        print(f"{OUT} up to date")
        return 0
    target.write_text(text)
    print(f"wrote {OUT} ({text.count(chr(10))} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
