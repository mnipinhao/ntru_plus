#!/usr/bin/env python3
"""Generate the NTRU+864 AVX2 exp002 codec kernels (direct 12-bit codec).

Writes two files:

asm/ntruplus864_officialopt_codec_direct.s   (candidate exp002)
  tobytes_direct   == poly_tobytes   (poly_ntt_pack + poly_tobytes_raw)
  frombytes_direct == poly_frombytes (poly_frombytes_raw + poly_ntt_unpack),
                      same return value
asm/ntruplus864_officialopt_codec_fused_min.s (diagnostic control)
  tobytes_fused_min == exp001 tobytes_fused with only the 2-op freeze

Design (per 96-coefficient block, internal 6-way layout: register R_r, word
l (0..15) holds wire coefficient 6l + r):

tobytes
  1. freeze each R_r: Official Barrett (pack.s:401-418: vpmulhrsw _16xv,
     vpmullw _16xq, vpsubw) followed by the 2-op canonicalisation
     y = vpaddw(b, q); out = vpminuw(b, y) instead of pack.s:420-437
     (vpsraw 15 / vpand q / vpaddw).  Exhaustive record:
     tools/prove_freeze_2op.py and tests/test_freeze_2op.c (Barrett output in
     [-3291, 3291] for all int16 inputs; 2-op == 3-op bit for bit).
  2. wire pairs are (R_{2s}[l], R_{2s+1}[l]), s = 0..2: vpunpck{l,h}wd puts
     each pair in one dword and vpmaddwd by (1, 4096) forms the 24-bit wire
     value c_even + 4096 c_odd.  D_s^lo holds pairs 3l+s for l = 0..3 (lane 0)
     and l = 8..11 (lane 1); D_s^hi l = 4..7 / 12..15.
  3. a 5-op in-lane dword interleave per (D_0, D_1, D_2) triple
        X = unpckldq(D1, D2)   Y = unpckhdq(D0, D1)
        O0 = unpcklqdq(D0, X)  O1 = blendd(Y, X, 0xCC)  O2 = unpckhqdq(Y, D2)
     leaves 4 consecutive wire pairs (one 12-byte wire group) in every
     128-bit lane: O_k^lo lanes = groups k, 6+k; O_k^hi lanes = 3+k, 9+k.
  4. one vpshufb per O_k orders the pairs and drops the 4th byte of every
     dword (12 bytes + 4 zero bytes per lane); each lane is stored with a
     16-byte store at 12*group (vmovdqu xmm / vextracti128 m128).  The 4
     spill bytes are overwritten by the next group's store, so the stores are
     kept in ascending address order (scheduler chain).  The very last group
     (bytes 1284..1295) is stored with vextracti128 + vmovq + vpextrd so that
     nothing is written beyond byte 1295.
frombytes (mirror)
  1. 16-byte loads at 12*group (vmovdqu xmm + vinserti128 m128), the last
     group loaded from byte 1280 with a lane-shifted mask (no read beyond
     byte 1295); one vpshufb per register expands each lane's 12 bytes to 4
     dwords [b0 b1 b2 0] in the O_k order above.
  2. the inverse 5-op interleave
        Z = unpckldq(O1, O2)   W = unpckhdq(O0, O1)
        D0 = unpcklqdq(O0, Z)  D1 = blendd(W, Z, 0xCC)  D2 = unpckhqdq(W, O2)
  3. even coefficient = D & 0xFFF, odd = D >> 12 (vpand / vpsrld), and
     vpackusdw(lo, hi) restores the 6-way word order (values <= 4095, no
     saturation).
  4. canonical check: vpmaxuw of every output register into one accumulator,
     one vpcmpgtw _16xqm1 / vpmovmskb at the end (as exp001; max > q-1 iff
     some coefficient > q-1).
Blocking: 4 x 192-coefficient iterations + a final 96-coefficient block (the
one with the special last group).  Every straight-line block is list-
scheduled (critical path first, register-pressure capped) with the exp001
Kernel scheduler, extended by an ordering chain for the overlapping stores.
No stack, no calls, no vzeroupper.  Pointer contract as exp001: poly 32-byte
aligned, byte array unaligned, byte array and poly must not overlap.

  generate_codec_direct.py --experiment .           # write
  generate_codec_direct.py --experiment . --check   # verify files are current
"""

import argparse
import hashlib
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("gcf", HERE / "generate_codec_fused.py")
gcf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gcf)

OUT_DIRECT = "asm/ntruplus864_officialopt_codec_direct.s"
OUT_MIN = "asm/ntruplus864_officialopt_codec_fused_min.s"
TOB = "ntruplus864_officialopt_tobytes_direct"
FROMB = "ntruplus864_officialopt_frombytes_direct"
TOB_MIN = "ntruplus864_officialopt_tobytes_fused_min"
C = ".Lntruplus864_officialopt_direct_"   # local constant labels

gcf.LATENCY.update({"vpmaddwd": 5, "vpminuw": 1})


class Kernel(gcf.Kernel):
    """exp001 Kernel plus ordered stores: a store created with order=True
    depends on the previous ordered store (overlapping 16-byte stores must
    retire in ascending address order)."""

    def __init__(self, pinned):
        super().__init__(pinned)
        self.chain = {}      # index -> index of previous ordered store
        self._last = None

    def store(self, mnem, src, mem, x=False, imm=None, order=False):
        super().store(mnem, src, mem, x=x, imm=imm)
        if order:
            i = len(self.ins) - 1
            if self._last is not None:
                self.chain[i] = self._last
            self._last = i

    def schedule(self, limit):
        # same algorithm as gcf.Kernel.schedule with the extra chain edges
        ins = self.ins
        n = len(ins)
        defs, deps = {}, []
        for i, x in enumerate(ins):
            d = {defs[u] for u in gcf.uses_of(x) if u in defs}
            if i in self.chain:
                d.add(self.chain[i])
            deps.append(sorted(d))
            if gcf.def_of(x) is not None:
                defs[gcf.def_of(x)] = i
        users = [[] for _ in range(n)]
        for i, d in enumerate(deps):
            for j in d:
                users[j].append(i)
        prio = [0] * n
        for i in reversed(range(n)):
            prio[i] = gcf.latency(ins[i]) + max((prio[j] for j in users[i]), default=0)
        remaining = {}
        for x in ins:
            for u in gcf.uses_of(x):
                remaining[u] = remaining.get(u, 0) + 1
        live, order = set(), []
        waiting = [len(d) for d in deps]
        ready = [i for i in range(n) if waiting[i] == 0]
        while ready:
            best = None
            for i in ready:
                x = ins[i]
                u = gcf.uses_of(x)
                kills = sum(1 for r in set(u) if r not in self.pinned and remaining[r] == u.count(r))
                d = gcf.def_of(x)
                grow = (d is not None and d not in self.pinned) - kills
                key = (True, prio[i], -i) if len(live) + grow <= limit else (False, -grow, -i)
                if best is None or key > best[0]:
                    best = (key, i)
            i = best[1]
            ready.remove(i)
            x = ins[i]
            for r in gcf.uses_of(x):
                remaining[r] -= 1
                if remaining[r] == 0:
                    live.discard(r)
            d = gcf.def_of(x)
            if d is not None and d not in self.pinned and remaining.get(d, 0):
                live.add(d)
            order.append(i)
            for j in users[i]:
                waiting[j] -= 1
                if waiting[j] == 0:
                    ready.append(j)
        if len(order) != n:
            raise ValueError("scheduling left instructions behind")
        pos = {old: new for new, old in enumerate(order)}
        for i, j in self.chain.items():
            if pos[j] > pos[i]:
                raise ValueError("store order violated")
        self.ins = [ins[i] for i in order]

    def emit(self):
        out = super().emit()
        # vextracti128 to a register: ymm source, xmm destination
        fixed = []
        for line in out:
            if line.startswith("vextracti128 $1, %ymm") and "(" not in line:
                a, b = line.rsplit(", %ymm", 1)
                line = f"{a}, %xmm{b}"
            fixed.append(line)
        return fixed


# ------------------------------------------------------------------ constants
def tob_masks():
    """vpshufb masks (both lanes identical): output byte 3j+t = byte t of the
    dword holding local pair j; bytes 12..15 zero."""
    orders = ([0, 3, 1, 2], [2, 3, 0, 1], [1, 2, 0, 3])   # local pair at dword position p
    masks = []
    for order in orders:
        pos = {pair: p for p, pair in enumerate(order)}
        lane = [0x80] * 16
        for j in range(4):
            for t in range(3):
                lane[3 * j + t] = 4 * pos[j] + t
        masks.append(lane + lane)
    return masks, orders


def fromb_masks():
    """expand masks: dword position p gets bytes 3*order[p] .. +2, byte 3 zero.
    The fourth mask is mask 2 with lane 1 reading 4 bytes further (last group
    loaded from byte 1280 instead of 1284)."""
    _, orders = tob_masks()
    masks = []
    for order in orders:
        lane = [0x80] * 16
        for p in range(4):
            for t in range(3):
                lane[4 * p + t] = 3 * order[p] + t
        masks.append(lane + lane)
    last = list(masks[2])
    for i in range(16, 32):
        if last[i] != 0x80:
            last[i] += 4
    masks.append(last)
    return masks


def rodata():
    tm, _ = tob_masks()
    fm = fromb_masks()
    L = [".section .rodata", ".p2align 5"]

    def table(name, data):
        L.append(f"{C}{name}:")
        for i in range(0, 32, 16):
            L.append(".byte " + ", ".join(f"0x{b:02x}" for b in data[i:i + 16]))
    madd = []
    for _ in range(8):
        madd += [0x01, 0x00, 0x00, 0x10]      # words (1, 4096)
    table("madd", madd)
    low12 = []
    for _ in range(8):
        low12 += [0xff, 0x0f, 0x00, 0x00]
    table("low12", low12)
    for i, m in enumerate(tm):
        table(f"tb{i}", m)
    for i, m in enumerate(fm[:3]):
        table(f"fb{i}", m)
    table("fb2last", fm[3])
    return L


# ------------------------------------------------------------------ tobytes
def freeze2(k, x):
    """Official Barrett (pack.s:401-418) + vpaddw q / vpminuw."""
    t = k.op("vpmulhrsw", k.v(), x, "%V")
    t = k.op("vpmullw", k.v(), t, "%Q")
    b = k.op("vpsubw", k.v(), x, t)
    y = k.op("vpaddw", k.v(), b, "%Q")
    return k.op("vpminuw", k.v(), b, y)


def interleave(k, d0, d1, d2):
    x = k.op("vpunpckldq", k.v(), d1, d2)
    y = k.op("vpunpckhdq", k.v(), d0, d1)
    return (k.op("vpunpcklqdq", k.v(), d0, x), k.op("vpblendd", k.v(), y, x, imm="0xCC"),
            k.op("vpunpckhqdq", k.v(), y, d2))


def tobytes_block(k, base, out, last=False):
    """96 coefficients at base(%rsi) -> 144 bytes at out(%rdi)."""
    r = [freeze2(k, k.load("vmovdqa", k.v("r"), f"{base + 32 * i}(%rsi)")) for i in range(6)]
    dlo, dhi = [], []
    for s in range(3):
        lo = k.op("vpunpcklwd", k.v(), r[2 * s], r[2 * s + 1])
        hi = k.op("vpunpckhwd", k.v(), r[2 * s], r[2 * s + 1])
        dlo.append(k.op("vpmaddwd", k.v(), lo, "%MADD"))
        dhi.append(k.op("vpmaddwd", k.v(), hi, "%MADD"))
    olo = [k.op("vpshufb", k.v(), o, f"{C}tb{i}(%rip)") for i, o in enumerate(interleave(k, *dlo))]
    ohi = [k.op("vpshufb", k.v(), o, f"{C}tb{i}(%rip)") for i, o in enumerate(interleave(k, *dhi))]
    # group g -> (register, lane)
    where = {}
    for i in range(3):
        where[i], where[6 + i] = (olo[i], 0), (olo[i], 1)
        where[3 + i], where[9 + i] = (ohi[i], 0), (ohi[i], 1)
    for g in range(12):
        reg, lane = where[g]
        mem = f"{out + 12 * g}(%rdi)"
        if last and g == 11:
            t = k.op("vextracti128", k.v(), reg, imm=1)
            k.store("vmovq", t, mem, x=True, order=True)
            k.store("vpextrd", t, f"{out + 12 * g + 8}(%rdi)", x=True, imm=2, order=True)
        elif lane == 0:
            k.store("vmovdqu", reg, mem, x=True, order=True)
        else:
            k.store("vextracti128", reg, mem, imm=1, order=True)


TOB_PIN = {"%V": 15, "%Q": 14, "%MADD": 13}


def tobytes_iteration():
    k = Kernel(TOB_PIN)
    tobytes_block(k, 0, 0)
    tobytes_block(k, 192, 144)
    return k.emit()


def tobytes_final():
    k = Kernel(TOB_PIN)
    tobytes_block(k, 0, 0, last=True)
    return k.emit()


# ---------------------------------------------------------------- frombytes
def frombytes_block(k, off, out, acc, last=False):
    """144 bytes at off(%rsi) -> 96 coefficients at out(%rdi)."""
    def expand(g0, g1, i):
        mask, g1off = f"{C}fb{i}(%rip)", off + 12 * g1
        if last and g1 == 11:
            mask, g1off = f"{C}fb2last(%rip)", off + 12 * g1 - 4
        lo = k.load("vmovdqu", k.v("l"), f"{off + 12 * g0}(%rsi)", x=True)
        v = k.op("vinserti128", k.v(), lo, f"{g1off}(%rsi)", imm=1)
        return k.op("vpshufb", k.v(), v, mask)
    olo = [expand(i, 6 + i, i) for i in range(3)]
    ohi = [expand(3 + i, 9 + i, i) for i in range(3)]

    def deinterleave(o0, o1, o2):
        z = k.op("vpunpckldq", k.v(), o1, o2)
        w = k.op("vpunpckhdq", k.v(), o0, o1)
        return (k.op("vpunpcklqdq", k.v(), o0, z), k.op("vpblendd", k.v(), w, z, imm="0xCC"),
                k.op("vpunpckhqdq", k.v(), w, o2))
    dlo = deinterleave(*olo)
    dhi = deinterleave(*ohi)
    for s in range(3):
        elo = k.op("vpand", k.v(), dlo[s], "%LOW")
        ehi = k.op("vpand", k.v(), dhi[s], "%LOW")
        odl = k.op("vpsrld", k.v(), dlo[s], imm=12)
        odh = k.op("vpsrld", k.v(), dhi[s], imm=12)
        for j, (a, b) in enumerate(((elo, ehi), (odl, odh))):
            rr = k.op("vpackusdw", k.v(), a, b)
            k.op("vpmaxuw", acc, acc, rr)
            k.store("vmovdqa", rr, f"{out + 32 * (2 * s + j)}(%rdi)")
    return acc


FROMB_PIN = {"%LOW": 15, "%ACC": 14}


def frombytes_iteration():
    k = Kernel(FROMB_PIN)
    acc = frombytes_block(k, 0, 0, "%ACC")
    frombytes_block(k, 144, 192, acc)
    return k.emit()


def frombytes_final():
    k = Kernel(FROMB_PIN)
    frombytes_block(k, 0, 0, "%ACC", last=True)
    return k.emit() + ["vpcmpgtw _16xqm1(%rip), %ymm14, %ymm14", "vpmovmskb %ymm14, %eax"]


def header(w, pack_sha, gen_sha):
    w("# GENERATED by tools/generate_codec_direct.py -- do not edit by hand.")
    w(f"# Source: upstream/supercop-avx2/pack.s sha256 {pack_sha}")
    w(f"#         tools/generate_codec_fused.py sha256 {gen_sha} (scheduler / exp001 kernels)")
    w("# Pointer contract (as exp001): poly 32-byte aligned (vmovdqa); byte array unaligned;")
    w("# the byte array and the poly must not overlap.  No stack, no calls, no vzeroupper.")


def generate_direct(pack_sha, gen_sha):
    L = []
    w = L.append
    w("# NTRU+864 Official AVX2: direct 12-bit codec (exp002), candidate code.")
    header(w, pack_sha, gen_sha)
    w("#   tobytes_direct(r, a)   == poly_tobytes(r, a)")
    w("#   frombytes_direct(r, a) == poly_frombytes(r, a), same return value")
    w("# freeze: Official Barrett + 2-op canonicalisation (vpaddw q, vpminuw), see")
    w("# tools/prove_freeze_2op.py; packing: vpunpck{l,h}wd + vpmaddwd (1,4096) + 5-op dword")
    w("# interleave + vpshufb, 16-byte stores in ascending order (last group 8+4 bytes).")
    w("")
    L.extend(rodata())
    w("")
    w(".text")
    w(".p2align 5")
    w(f".global {TOB}")
    w(f".type {TOB},@function")
    w(f"{TOB}:")
    w("vmovdqa _16xv(%rip), %ymm15")
    w("vmovdqa _16xq(%rip), %ymm14")
    w(f"vmovdqa {C}madd(%rip), %ymm13")
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
    w("# coefficients 768..863 (bytes 1152..1295; last group stored as 8 + 4 bytes)")
    L.extend(tobytes_final())
    w("ret")
    w(f".size {TOB}, .-{TOB}")
    w("")
    w(".p2align 5")
    w(f".global {FROMB}")
    w(f".type {FROMB},@function")
    w(f"{FROMB}:")
    w(f"vmovdqa {C}low12(%rip), %ymm15")
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
    w("# coefficients 768..863 (last group loaded from byte 1280)")
    L.extend(frombytes_final())
    w("test %eax, %eax")
    w("setne %al")
    w("movzbl %al, %eax")
    w("ret")
    w(f".size {FROMB}, .-{FROMB}")
    w("")
    w(".section .note.GNU-stack,\"\",@progbits")
    return "\n".join(L) + "\n"


# ------------------------------------------------- freeze-only exp001 control
def pack_block_min(k, base):
    """gcf.pack_block with the 2-op canonicalisation (everything else equal)."""
    r = [k.load("vmovdqa", k.v("r"), f"{base + 32 * i}(%rsi)") for i in range(6)]
    g = [freeze2(k, x) for x in r]
    r0, r1, r2, r3, r4, r5 = g

    def pair16(lo, hi):
        s = k.op("vpslld", k.v(), hi, imm=16)
        t = k.op("vpsrld", k.v(), lo, imm=16)
        return (k.op("vpblendw", k.v(), lo, s, imm="0xAA"), k.op("vpblendw", k.v(), t, hi, imm="0xAA"))
    y6, y9 = pair16(r0, r1)
    y7, y10 = pair16(r2, r3)
    y8, y11 = pair16(r4, r5)

    def pair32(lo, hi):
        s = k.op("vpsllq", k.v(), hi, imm=32)
        t = k.op("vpsrlq", k.v(), lo, imm=32)
        return (k.op("vpblendd", k.v(), lo, s, imm="0xAA"), k.op("vpblendd", k.v(), t, hi, imm="0xAA"))
    z0, z3 = pair32(y6, y7)
    z1, z4 = pair32(y8, y9)
    z2, z5 = pair32(y10, y11)

    def pairq(a, b):
        return (k.op("vpunpcklqdq", k.v(), a, b), k.op("vpunpckhqdq", k.v(), a, b))
    p0, p3 = pairq(z0, z1)
    p1, p4 = pairq(z2, z3)
    p2, p5 = pairq(z4, z5)
    return [p0, p1, p2, p3, p4, p5]


def generate_min(pack_sha, gen_sha):
    saved = gcf.pack_block
    gcf.pack_block = pack_block_min
    try:
        full = gcf.generate(pack_sha)
    finally:
        gcf.pack_block = saved
    # keep only the tobytes function, renamed
    start = full.index(".p2align 5\n.global " + gcf.TOB)
    end = full.index(f".size {gcf.TOB}, .-{gcf.TOB}\n") + len(f".size {gcf.TOB}, .-{gcf.TOB}\n")
    body = full[start:end].replace(gcf.TOB, TOB_MIN)
    L = ["# NTRU+864 Official AVX2: exp001 tobytes_fused with the 2-op freeze only (diagnostic control)."]
    header(L.append, pack_sha, gen_sha)
    L.append("# == exp001 ntruplus864_officialopt_tobytes_fused except pack.s:420-437 (vpsraw/vpand/")
    L.append("# vpaddw) -> vpaddw q + vpminuw per register (then list-scheduled as exp001).")
    L += ["", ".text", body.rstrip("\n"), "", ".section .note.GNU-stack,\"\",@progbits"]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--check", action="store_true")
    args = ap.parse_args()
    root = args.experiment.resolve()
    pack_sha = hashlib.sha256((root / "upstream/supercop-avx2/pack.s").read_bytes()).hexdigest()
    gen_sha = hashlib.sha256((root / "tools/generate_codec_fused.py").read_bytes()).hexdigest()
    outputs = {OUT_DIRECT: generate_direct(pack_sha, gen_sha), OUT_MIN: generate_min(pack_sha, gen_sha)}
    rc = 0
    for rel, text in outputs.items():
        target = root / rel
        if args.check:
            if not target.exists() or target.read_text() != text:
                print(f"{rel} is stale; run make generate-codec-direct", file=sys.stderr)
                rc = 1
            else:
                print(f"{rel} up to date")
        else:
            target.write_text(text)
            print(f"wrote {rel} ({text.count(chr(10))} lines)")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
