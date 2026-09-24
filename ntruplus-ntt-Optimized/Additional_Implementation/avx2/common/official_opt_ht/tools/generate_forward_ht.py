#!/usr/bin/env python3
"""Generate the NTRU+768 / 864 / 1152 "HT" caller-lazy Forward (Hwang-style data movement).

Output: asm/ntruplus{N}_officialopt_ntt_ht.s, a drop-in replacement for the
caller-lazy Forward asm/ntruplus{N}_officialopt_ntt_caller_lazy.s (common
official_opt_lazy/tools/generate_forward_caller_lazy.py --param N; no
terminal Barrett).  Same Official decomposition, twiddle representatives,
Montgomery domain and output layout; only the passes and the data movement
change:

  pass A   level 0 (x^N - x^(N/2) + 1 split, raw zeta1 product) fused with the
           level-1 radix-3 butterflies, 6 vectors per iteration (Hwang 3x2
           style); rows N/6 coefficients apart.  Radix-3 constants are the
           Official broadcast pairs (zetas words 4..11 and 12..19), stored
           as full vectors so they can be memory operands (all 16 YMM
           registers are live).
  level 2  the Official level-2 pass, copied verbatim from the lazy asm
           (768: radix 2; 864/1152: radix 3).
  block    levels 3..6 of each block in one pass, natural input order,
           unpack-only exchange network.  Final layout = Official.

NTRU+768 (--param 768, the default; output unchanged by the generalisation):
  rows 128*b + 16*v, v = 0..7; 128-coefficient blocks in 8 registers,
  L3 (d=32), L4 (d=16), vperm2i128, L5 (d=8), vpunpck{l,h}wd,
  vpunpck{l,h}dq, vpunpck{l,h}dq, L6 (d=4) (the scratch search_stages.py
  network); 32 shuffle uops per block (the Official network needs 48);
  register r of block b holds coefficients 128b + 8l + r (lane l), stored
  at 32*r.
NTRU+1152 (--param 1152): the NTRU+768 block network unchanged on nine
  128-coefficient blocks (32 vs 48 shuffle uops); only the twiddles differ.
NTRU+864 (--param 864): 96-coefficient blocks in 6 registers, distances
  24/12/6/3 (cubic leaves): vperm2i128, L3 (d=24), vpunpck{l,h}wd, L4 (d=12),
  vpunpck{l,h}wd, L5 (d=6), vpunpck{l,h}wd, L6 (d=3).  Every stage pairs
  logical registers (i, i+3), i = 0..2, and its lo/hi outputs become logical
  registers 2i / 2i+1 (a renaming, no instruction); the scratch exhaustive
  search found this to be the only 4-stage unpack-only network.  24 shuffle
  uops per block (Official: 36); register r lane l of block b holds
  coefficient 96b + 6l + r, as in the lazy Forward.
  864/1152 pitfall: the Official radix-3 level 2 reuses ymm2/ymm3 (w*qinv, w)
  loaded in the level-1 prologue; pass A keeps w/w*qinv in ymm13/ymm14, so it
  restores ymm2/ymm3 before the verbatim level 2 (checked below: the level-2
  body reads exactly ymm0, ymm2 and ymm3 before writing them).

Twiddles are not recomputed: every per-lane (zeta, zeta*qinv) pair is the one
the lazy Forward applies to the same data, found by executing the lazy asm
symbolically (tools/symexec.py) and matching the operand forms.  The
generator then executes the emitted asm symbolically and requires every one
of the N output words to have the same interned form as the lazy Forward's
output word, which proves bit-identical outputs for every int16 input.  It
also checks: no stack, call or vzeroupper; every store inside the polynomial;
all memory operands 32-byte aligned; entry and tables .p2align 5.

  generate_forward_ht.py [--param N] --experiment .           # write asm (+ --meta json)
  generate_forward_ht.py [--param N] --experiment . --check   # verify, write nothing
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from symexec import Forms, SymExec, parse_consts, s16  # noqa: E402

Q, QINV = 3457, 12929

# Block networks on logical registers r0..r(NR-1) (natural order: r_i = coefficients 16i..16i+15).
# ('BF', lo, hi, distance) / ('PERM'|'UNP16'|'UNP32', i, j) / ('REN',).  Groups of up to four
# butterflies of one level are emitted interleaved (Official style).  ('REN',) renames
# logical registers after a stage on the pairs (i, i+3): lo of pair i -> 2i, hi -> 2i+1.
NET8 = [("BF", 0, 2, 32), ("BF", 1, 3, 32), ("BF", 4, 6, 32), ("BF", 5, 7, 32),
        ("BF", 0, 1, 16), ("BF", 2, 3, 16), ("BF", 4, 5, 16), ("BF", 6, 7, 16),
        ("PERM", 0, 4), ("PERM", 1, 5), ("PERM", 2, 6), ("PERM", 3, 7),
        ("BF", 0, 4, 8), ("BF", 1, 5, 8), ("BF", 2, 6, 8), ("BF", 3, 7, 8),
        ("UNP16", 0, 4), ("UNP16", 1, 5), ("UNP16", 2, 6), ("UNP16", 3, 7),
        ("UNP32", 0, 2), ("UNP32", 1, 3), ("UNP32", 4, 6), ("UNP32", 5, 7),
        ("UNP32", 0, 1), ("UNP32", 2, 3), ("UNP32", 4, 5), ("UNP32", 6, 7),
        ("BF", 0, 4, 4), ("BF", 1, 5, 4), ("BF", 2, 6, 4), ("BF", 3, 7, 4)]
REN = ("REN",)
NET6 = [("PERM", 0, 3), ("PERM", 1, 4), ("PERM", 2, 5), REN,
        ("BF", 0, 3, 24), ("BF", 1, 4, 24), ("BF", 2, 5, 24),
        ("UNP16", 0, 3), ("UNP16", 1, 4), ("UNP16", 2, 5), REN,
        ("BF", 0, 3, 12), ("BF", 1, 4, 12), ("BF", 2, 5, 12),
        ("UNP16", 0, 3), ("UNP16", 1, 4), ("UNP16", 2, 5), REN,
        ("BF", 0, 3, 6), ("BF", 1, 4, 6), ("BF", 2, 5, 6),
        ("UNP16", 0, 3), ("UNP16", 1, 4), ("UNP16", 2, 5), REN,
        ("BF", 0, 3, 3), ("BF", 1, 4, 3), ("BF", 2, 5, 3)]

PARAMS = {
    768: {"nr": 8, "net": NET8, "level": {32: 3, 16: 4, 8: 5, 4: 6}, "radix3_level2": False,
          "pins": {
              # imported, never-edited SUPERCOP 20260831 crypto_kem/ntruplus768/avx2
              "upstream/supercop-avx2/consts.c": "52649ae464c507e80169367621ea4e07ec11a25dc7f162467bf1dd96dc6fb080",
              "upstream/supercop-avx2/ntt.s": "992b613701be5988e83798a4a8f56a798c7e47e4616db70e65eee7feb75332f4",
              # generate_forward_caller_lazy.py --param 768 output (its --check is a prerequisite)
              "asm/ntruplus768_officialopt_ntt_caller_lazy.s":
                  "66c3fa6e90bf7cfd74543e8c6748a625c70de560a590b11257d3059d9e1c43e4"}},
    864: {"nr": 6, "net": NET6, "level": {24: 3, 12: 4, 6: 5, 3: 6}, "radix3_level2": True,
          "pins": {
              # imported, never-edited SUPERCOP 20260831 crypto_kem/ntruplus864/avx2
              "upstream/supercop-avx2/consts.c": "0c60897a0d2e8264a75f44b5b7ef49bbaa7a5f55cf3019ffc1b0ac9864534412",
              "upstream/supercop-avx2/ntt.s": "980cad5ef69a78f9ed1f2f45fc5dcaa0a04cc07693cf65ea108acc41c547db92",
              # generate_forward_caller_lazy.py --param 864 output (its --check is a prerequisite)
              "asm/ntruplus864_officialopt_ntt_caller_lazy.s":
                  "db5d489658d4f5b77ce181c691d7c3b9e054a0a14ebc7c693f79df382a8f0497"}},
    1152: {"nr": 8, "net": NET8, "level": {32: 3, 16: 4, 8: 5, 4: 6}, "radix3_level2": True,
           "pins": {
               # imported, never-edited SUPERCOP 20260831 crypto_kem/ntruplus1152/avx2
               "upstream/supercop-avx2/consts.c": "0c60897a0d2e8264a75f44b5b7ef49bbaa7a5f55cf3019ffc1b0ac9864534412",
               "upstream/supercop-avx2/ntt.s": "23c851702f9ca399945c71ee90d6f26d0e6ebf6c602f4d1a7e09c4761bf1ede5",
               # generate_forward_caller_lazy.py --param 1152 output (its --check is a prerequisite)
               "asm/ntruplus1152_officialopt_ntt_caller_lazy.s":
                   "eb6a536cffef99339ee3b479a9a1299e54a50d15375daba68ac08ca1924be092"}},
}

# Module-level names for the selected parameter (set by configure(); default NTRU+768 so
# that importers such as mutate_ht.py see the historical constants).
N = NAME = LAZY = TAB_A = TAB_B = PINS = NET = LEVEL = None
NR = BLK = NBLK = ROW = 0
P = ""


def configure(param):
    global N, NAME, LAZY, TAB_A, TAB_B, PINS, NET, LEVEL, NR, BLK, NBLK, ROW, P
    cfg = PARAMS[param]
    N = param
    P = f"ntruplus{param}_officialopt"
    NAME = f"{P}_ntt_ht"
    LAZY = f"{P}_ntt_caller_lazy"
    TAB_A = f"{P}_ht_zetas_a"
    TAB_B = f"{P}_ht_zetas_b"
    PINS = cfg["pins"]
    NET = cfg["net"]
    LEVEL = cfg["level"]
    NR = cfg["nr"]
    BLK = 16 * NR                 # coefficients per block
    NBLK = N // BLK
    ROW = N // 3                  # pass A row stride in bytes (N/6 coefficients)
    return cfg


configure(768)


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def is_bf(op):
    return op[0] == "BF"


def groups():
    """[(level distance, [net indices])] for the butterfly groups, in order."""
    out, k = [], 0
    while k < len(NET):
        if is_bf(NET[k]):
            g = []
            while k < len(NET) and is_bf(NET[k]) and len(g) < 4 and NET[k][3] == NET[k - len(g)][3]:
                g.append(k)
                k += 1
            out.append((NET[g[0]][3], g))
        else:
            k += 1
    return out


def renamed(r):
    """Logical registers after a stage on the pairs (i, i+3): lo -> 2i, hi -> 2i+1."""
    h = NR // 2
    new = [None] * NR
    for i in range(h):
        new[2 * i], new[2 * i + 1] = r[i], r[i + h]
    return new


# ------------------------------------------------------------------ lazy reference run
def run_lazy(F, lazy_text, syms):
    ex = SymExec(F, lazy_text, syms)
    B = ex.POLY
    for w in range(N):
        ex.mem[B + 2 * w] = F.input(w)
    zmap, zqmap, snap = {}, {}, {}

    def on_mul(op, data, consts):
        m = zmap if op == "vpmulhw" else zqmap
        for f, c in zip(data, consts):
            m.setdefault(f, set()).add(c)
    ex.on_mul = on_mul
    start = ex.labels[f"{P}_lazy_looptop_start_3456"]

    def take(e):
        if not snap:
            snap.update({w: e.mem[B + 2 * w] for w in range(N)})
    ex.hooks[start] = take
    ex.run(LAZY, {"rdi": B})
    out = [ex.mem[B + 2 * w] for w in range(N)]
    run_lazy.census = dict(sorted(ex.census.items()))
    return out, snap, zmap, zqmap


# ------------------------------------------------------------------ block network model
def model_block(F, snap, zmap, zqmap, b):
    """Run NET on block b symbolically; return per-butterfly (zr[16], zq[16]),
    the final register forms and the used lazy forms."""
    q = F.const(Q)
    r = [[snap[BLK * b + 16 * i + l] for l in range(16)] for i in range(NR)]
    tw = {}
    for k, op in enumerate(NET):
        if op == REN:
            r = renamed(r)
            continue
        kind, i, j = op[:3]
        a, c = r[i], r[j]
        if kind == "BF":
            zr, zq, lo_new, hi_new = [], [], [], []
            for l in range(16):
                f = c[l]
                if len(zmap.get(f, ())) != 1 or len(zqmap.get(f, ())) != 1:
                    raise ValueError(f"block {b} net {k} lane {l}: no unique lazy twiddle")
                z, zqv = next(iter(zmap[f])), next(iter(zqmap[f]))
                if s16(z * QINV) != zqv:
                    raise ValueError("twiddle companion mismatch")
                t = F.sub(F.mulhi(f, F.const(z)), F.mulhi(F.mullo(f, F.const(zqv)), q))
                lo_new.append(F.add(a[l], t))
                hi_new.append(F.sub(a[l], t))
                zr.append(z)
                zq.append(zqv)
            r[i], r[j] = lo_new, hi_new
            tw[k] = (tuple(zr), tuple(zq))
        elif kind == "PERM":
            r[i], r[j] = a[0:8] + c[0:8], a[8:16] + c[8:16]
        else:
            w = 1 if kind == "UNP16" else 2
            lo, hi = [], []
            for h in (0, 8):
                for s in range(0, 4, w):
                    lo += a[h + s:h + s + w] + c[h + s:h + s + w]
                    hi += a[h + 4 + s:h + 4 + s + w] + c[h + 4 + s:h + 4 + s + w]
            r[i], r[j] = lo, hi
    return tw, r


# ------------------------------------------------------------------ emission
def words_lines(words):
    return [".short " + ", ".join(str(v) for v in words[i:i + 16]) for i in range(0, len(words), 16)]


def header():
    if N == 768:
        return ["# GENERATED by common/official_opt_ht/tools/generate_forward_ht.py -- do not edit.",
                "# NTRU+768 Official AVX2 caller-lazy Forward, HT variant: pass A (level 0 +",
                "# radix-3 level 1, 6 vectors/iteration), Official level 2 (verbatim), one",
                "# levels-3..6 block pass per 128 coefficients with an unpack-only exchange",
                "# network.  Output bit-identical to ntruplus768_officialopt_ntt_caller_lazy",
                "# for every int16 input (symbolic proof in the generator); no terminal",
                "# Barrett, same caller contract."]
    return [f"# GENERATED by common/official_opt_ht/tools/generate_forward_ht.py --param {N} -- do not edit.",
            f"# NTRU+{N} Official AVX2 caller-lazy Forward, HT variant: pass A (level 0 +",
            "# radix-3 level 1, 6 vectors/iteration; restores the level-1 w/w*qinv registers),",
            "# Official radix-3 level 2 (verbatim), one levels-3..6 block pass per",
            f"# {BLK} coefficients with an unpack-only exchange network.  Output bit-identical",
            f"# to {LAZY} for every int16 input (symbolic proof in",
            "# the generator); no terminal Barrett, same caller contract."]


def emit(level2, slot_of, nslots, tab_b_words, tab_a_words, store, radix3_level2):
    o = []
    e = o.append
    o.extend(header())
    e(".text")
    e(".p2align 5")
    e(f".global {NAME}")
    e(f".type {NAME},@function")
    e(f"{NAME}:")
    e("vmovdqa _16xq(%rip), %ymm0")
    e("")
    e("#level0+1 (pass A)")
    e("vmovdqa _16xzeta1(%rip), %ymm15")
    e("vmovdqa _16xw(%rip), %ymm13")
    e("vmovdqa _16xwqinv(%rip), %ymm14")
    e(f"lea {TAB_A}(%rip), %rsi")
    e(f"lea {ROW}(%rdi), %r8")
    e("")
    e(".p2align 5")
    e(f"{P}_ht_looptop_a:")
    X = [f"%ymm{i}" for i in range(1, 7)]
    T = [f"%ymm{i}" for i in range(7, 13)]
    for b in range(6):
        e(f"vmovdqa {ROW * b}(%rdi), {X[b]}")
    for t in range(3):          # level 0: (A, B) = (row t, row t+3)
        A, Bv, m = X[t], X[t + 3], T[t]
        e(f"vpmullw %ymm15, {Bv}, {m}")
        e(f"vpsubw {m}, {A}, {T[t + 3]}")
        e(f"vpaddw {m}, {A}, {A}")
        e(f"vpaddw {Bv}, {T[t + 3]}, {Bv}")
    for be in range(2):         # level 1 radix-3 on rows 3be, 3be+1, 3be+2
        A, Bv, C = X[3 * be], X[3 * be + 1], X[3 * be + 2]
        a0, a1, a2 = T[0], T[1], T[2]
        off = 128 * be
        e(f"vpmullw {off + 32}(%rsi), {Bv}, {a0}")
        e(f"vpmullw {off + 96}(%rsi), {C}, {a1}")
        e(f"vpmulhw {off}(%rsi), {Bv}, {Bv}")
        e(f"vpmulhw {off + 64}(%rsi), {C}, {C}")
        e(f"vpmulhw %ymm0, {a0}, {a0}")
        e(f"vpmulhw %ymm0, {a1}, {a1}")
        e(f"vpsubw {a0}, {Bv}, {Bv}")        # Ba
        e(f"vpsubw {a1}, {C}, {C}")          # Ca^2
        e(f"vpsubw {C}, {Bv}, {a2}")         # Ba - Ca^2
        e(f"vpmullw %ymm14, {a2}, {a0}")
        e(f"vpmulhw %ymm13, {a2}, {a2}")
        e(f"vpmulhw %ymm0, {a0}, {a0}")
        e(f"vpsubw {a0}, {a2}, {a2}")        # w(Ba - Ca^2)
        e(f"vpaddw {Bv}, {A}, {a0}")         # A + Ba
        e(f"vpsubw {C}, {A}, {a1}")          # A - Ca^2
        e(f"vpsubw {Bv}, {A}, {Bv}")         # A - Ba
        e(f"vpaddw {C}, {a0}, {a0}")
        e(f"vpaddw {a2}, {a1}, {a1}")
        e(f"vpsubw {a2}, {Bv}, {Bv}")
        e(f"vmovdqa {a0}, {ROW * (3 * be)}(%rdi)")
        e(f"vmovdqa {a1}, {ROW * (3 * be + 1)}(%rdi)")
        e(f"vmovdqa {Bv}, {ROW * (3 * be + 2)}(%rdi)")
    e("")
    e("add $32, %rdi")
    e("cmp %r8, %rdi")
    e(f"jb  {P}_ht_looptop_a")
    e("")
    e(f"sub ${ROW}, %rdi")
    e("lea zetas(%rip), %rdx")
    e("add $32, %rdx")
    if radix3_level2:
        e("# the Official radix-3 level 2 reads w*qinv / w from ymm2 / ymm3 (level-1 prologue)")
        e("vmovdqa %ymm14, %ymm2")
        e("vmovdqa %ymm13, %ymm3")
    e("")
    o.extend(level2.rstrip("\n").splitlines())
    e("")
    e("#level3456 (block pass)")
    e(f"lea {TAB_B}(%rip), %rsi")
    e(f"lea {2 * N}(%rdi), %r8")
    e("")
    e(".p2align 5")
    e(f"{P}_ht_looptop_b:")
    reg = {i: f"%ymm{i + 1}" for i in range(NR)}
    free = [f"%ymm{i}" for i in range(NR + 1, 14)]
    for i in range(NR):
        e(f"vmovdqa {32 * i}(%rdi), {reg[i]}")
    k = 0
    while k < len(NET):
        if NET[k] == REN:
            reg = dict(enumerate(renamed([reg[i] for i in range(NR)])))
            k += 1
        elif is_bf(NET[k]):
            grp = []
            while k < len(NET) and is_bf(NET[k]) and len(grp) < 4 and \
                    (not grp or NET[k][3] == NET[grp[0]][3]):
                grp.append(k)
                k += 1
            e(f"#level{LEVEL[NET[grp[0]][3]]}")
            slots = {slot_of[g] for g in grp}
            if len(slots) == 1:
                s = slot_of[grp[0]]
                e(f"vmovdqa {64 * s}(%rsi), %ymm14")
                e(f"vmovdqa {64 * s + 32}(%rsi), %ymm15")
                ZR = {g: "%ymm14" for g in grp}
                ZQ = {g: "%ymm15" for g in grp}
            else:
                ZR = {g: f"{64 * slot_of[g]}(%rsi)" for g in grp}
                ZQ = {g: f"{64 * slot_of[g] + 32}(%rsi)" for g in grp}
            T4 = [free.pop(0) for _ in grp]
            for g, t in zip(grp, T4):
                e(f"vpmullw {ZQ[g]}, {reg[NET[g][2]]}, {t}")
            for g in grp:
                e(f"vpmulhw {ZR[g]}, {reg[NET[g][2]]}, {reg[NET[g][2]]}")
            for t in T4:
                e(f"vpmulhw %ymm0, {t}, {t}")
            for g, t in zip(grp, T4):
                e(f"vpsubw {t}, {reg[NET[g][2]]}, {reg[NET[g][2]]}")
            for g, t in zip(grp, T4):
                e(f"vpsubw {reg[NET[g][2]]}, {reg[NET[g][1]]}, {t}")
            for g in grp:
                e(f"vpaddw {reg[NET[g][2]]}, {reg[NET[g][1]]}, {reg[NET[g][1]]}")
            for g, t in zip(grp, T4):
                old = reg[NET[g][2]]
                reg[NET[g][2]] = t
                free.append(old)
        else:
            kind, i, j = NET[k]
            if k == 0 or NET[k - 1][0] != kind:
                e(f"#shuffle {kind.lower()}")
            k += 1
            a, bb, t = reg[i], reg[j], free.pop(0)
            if kind == "PERM":
                e(f"vperm2i128 $0x20, {bb}, {a}, {t}")
                e(f"vperm2i128 $0x31, {bb}, {a}, {bb}")
            else:
                sfx = "wd" if kind == "UNP16" else "dq"
                e(f"vpunpckl{sfx} {bb}, {a}, {t}")
                e(f"vpunpckh{sfx} {bb}, {a}, {bb}")
            reg[i] = t
            free.append(a)
    e("")
    e("#store")
    for i in range(NR):
        e(f"vmovdqa {reg[i]}, {32 * store[i]}(%rdi)")
    e("")
    e(f"add ${2 * BLK}, %rdi")
    e(f"add ${64 * nslots}, %rsi")
    e("cmp %r8, %rdi")
    e(f"jb  {P}_ht_looptop_b")
    e("")
    e("ret")
    e("")
    e(f".size {NAME},.-{NAME}")
    e("")
    e(".section .rodata")
    e(".p2align 5")
    e(f"{TAB_A}:  # pass A: per radix-3 group [zeta a, a*qinv, zeta a^2, a^2*qinv] x 16 lanes")
    o.extend(words_lines(tab_a_words))
    e(".p2align 5")
    e(f"{TAB_B}:  # block pass: per block {nslots} slots of [zeta x 16, zeta*qinv x 16]")
    o.extend(words_lines(tab_b_words))
    e("")
    e(".ifndef no_gnu_stack")
    e('.section .note.GNU-stack,"",@progbits')
    e(".endif")
    return "\n".join(o) + "\n"


# ------------------------------------------------------------------ main derivation
def reads_before_write(ins):
    """YMM registers an instruction list reads before writing them (AT&T: last operand = dest)."""
    written, read = set(), set()
    for l in ins:
        if l.endswith(":"):
            continue
        ops = [o.strip() for o in re.split(r",(?![^(]*\))", l.partition(" ")[2]) if o.strip()]
        regs = [o for o in ops if o.startswith("%ymm")]
        if not regs:
            continue
        srcs = ops[:-1] if ops[-1].startswith("%ymm") else ops
        for s in srcs:
            if s.startswith("%ymm") and s not in written:
                read.add(s)
        if ops[-1].startswith("%ymm"):
            written.add(ops[-1])
    return read


def extract_level2(lazy_text, radix3):
    end_line = f"sub ${2 * N}, %rdi\n"
    start = lazy_text.index("#level 2\n")
    end = lazy_text.index(end_line, start) + len(end_line)
    body = lazy_text[start:end]
    ins = [l.split("#")[0].strip() for l in body.splitlines()]
    ins = [l for l in ins if l and not l.startswith(".")]
    if not ins[0] == f"lea {2 * N}(%rdi), %r8" or ins[-1] != f"sub ${2 * N}, %rdi":
        raise ValueError("unexpected level-2 frame")
    if not radix3:
        if body.count(f"{P}_lazy_looptop_start_2") != 2 or \
                "vpbroadcastd  8(%rdx), %ymm15" not in body or "add $8,   %rdx" not in body:
            raise ValueError("unexpected level-2 body")
        labels = {f"{P}_lazy_looptop_start_2": f"{P}_ht_looptop_l2"}
    else:
        if body.count(f"{P}_lazy_looptop_start_2") != 2 or body.count(f"{P}_lazy_looptop_j_2") != 2 or \
                not re.search(r"vpbroadcastd +8\(%rdx\), %ymm4", body) or "add $16,  %rdx" not in body:
            raise ValueError("unexpected level-2 body")
        # the pass-A pitfall: level 2 must read nothing but q, w*qinv and w before writing
        if reads_before_write(ins) != {"%ymm0", "%ymm2", "%ymm3"}:
            raise ValueError(f"level-2 live-in registers {sorted(reads_before_write(ins))}")
        labels = {f"{P}_lazy_looptop_start_2": f"{P}_ht_looptop_l2",
                  f"{P}_lazy_looptop_j_2": f"{P}_ht_looptop_l2j"}
    ops = {}
    for l in ins:
        if not l.endswith(":"):
            ops[l.split()[0]] = ops.get(l.split()[0], 0) + 1
    for old, new in labels.items():
        body = body.replace(old, new)
    return body, ops


def derive(root, param=768):
    cfg = configure(param)
    for rel, pin in PINS.items():
        got = sha256((root / rel).read_bytes())
        if got != pin:
            raise ValueError(f"pinned input changed: {rel} {got}")
    up = root / "upstream/supercop-avx2"
    syms = parse_consts((up / "consts.c").read_text())
    lazy_text = (root / f"asm/{LAZY}.s").read_text()
    level2, level2_ops = extract_level2(lazy_text, cfg["radix3_level2"])
    F = Forms()
    out_l, snap, zmap, zqmap = run_lazy(F, lazy_text, syms)
    if len(snap) != N:
        raise ValueError("no level-3456 snapshot")

    # --- block network twiddles and final layout
    per_block, store = [], None
    for b in range(NBLK):
        tw, regs = model_block(F, snap, zmap, zqmap, b)
        per_block.append(tw)
        rows = {tuple(out_l[BLK * b + 16 * r:BLK * b + 16 * r + 16]): r for r in range(NR)}
        st = []
        for i in range(NR):
            if tuple(regs[i]) not in rows:
                raise ValueError(f"block {b} register {i} is not an Official output row")
            st.append(rows[tuple(regs[i])])
        if sorted(st) != list(range(NR)) or (store is not None and st != store):
            raise ValueError("non-uniform output layout")
        store = st
    # slot sharing: butterflies of one group share a slot iff their vectors are
    # equal in every block (so the code is uniform over blocks)
    slot_of, nslots, slot_members = {}, 0, []
    for dist, grp in groups():
        seen = []
        for g in grp:
            for s, rep in seen:
                if all(per_block[b][g] == per_block[b][rep] for b in range(NBLK)):
                    slot_of[g] = s
                    break
            else:
                slot_of[g] = nslots
                seen.append((nslots, g))
                slot_members.append(g)
                nslots += 1
    tab_b = []
    for b in range(NBLK):
        for g in slot_members:
            zr, zq = per_block[b][g]
            tab_b += list(zr) + list(zq)
    # --- pass A constants: the Official level-1 broadcast dwords, as vectors
    z = syms["zetas"]
    tab_a = []
    for be in range(2):
        base = 4 + 8 * be            # dword pairs at bytes 8/12/16/20 (+16 be) of zetas
        zq_a, zr_a = z[base:base + 2] * 8, z[base + 2:base + 4] * 8
        zq_a2, zr_a2 = z[base + 4:base + 6] * 8, z[base + 6:base + 8] * 8
        for zr, zq in ((zr_a, zq_a), (zr_a2, zq_a2)):
            if any(s16(x * QINV) != y for x, y in zip(zr, zq)):
                raise ValueError("pass A companion mismatch")
        tab_a += zr_a + zq_a + zr_a2 + zq_a2
    asm = emit(level2, slot_of, nslots, tab_b, tab_a, store, cfg["radix3_level2"])
    meta = verify(F, asm, syms, out_l)
    meta.update({
        "store_rows": store, "block_slots": nslots, "slot_of_butterfly": [slot_of[g] for g in sorted(slot_of)],
        "table_bytes": {"pass_a": 2 * len(tab_a), "block": 2 * len(tab_b)},
        "level2_verbatim_ops": level2_ops,
        "lazy_dynamic_instructions": sum(run_lazy.census.values()),
        "lazy_dynamic_census": run_lazy.census,
        "inputs_sha256": dict(PINS),
    })
    if N != 768:
        meta.update({"parameter": N, "blocks": NBLK, "block_coefficients": BLK,
                     "level2_live_in_restored": ["%ymm2 <- %ymm14 (w*qinv)", "%ymm3 <- %ymm13 (w)"]})
    return asm, meta


def census_block(asm):
    """Instruction census of one loop body (static) per pass."""
    passes, cur = {}, None
    for line in asm.splitlines():
        s = line.split("#")[0].strip()
        if s.endswith(":"):
            cur = s[:-1]
            continue
        if not s or s.startswith(".") or cur is None:
            continue
        op = s.split()[0]
        passes.setdefault(cur, {})
        passes[cur][op] = passes[cur].get(op, 0) + 1
    return passes


def verify(F, asm, syms, out_l):
    for bad in ("%rsp", "call", "vzeroupper", "%rbp", "push", "pop"):
        if re.search(rf"^\s*[^#.\s].*{re.escape(bad)}", asm, re.M):
            raise ValueError(f"forbidden {bad}")
    # entry, pass-A loop head, level-2 loop heads (1 for 768, 2 for 864/1152), block loop head, 2 tables
    if asm.count(".p2align 5") != (6 if N == 768 else 7):
        raise ValueError("alignment directives")
    ex = SymExec(F, asm, syms)
    B = ex.POLY
    for w in range(N):
        ex.mem[B + 2 * w] = F.input(w)
    ex.run(NAME, {"rdi": B})
    out_h = [ex.mem[B + 2 * w] for w in range(N)]
    if out_h != out_l:
        diff = sum(a != b for a, b in zip(out_h, out_l))
        raise ValueError(f"HT output forms differ from lazy on {diff} words")
    if not ex.stores <= {B + 2 * w for w in range(N)}:
        raise ValueError("store outside the polynomial")
    for ln, op, ops in ex.prog:
        for o in ops:
            m = re.fullmatch(r"(-?\d*)\((%r\w+)\)", o)
            if op != "vpbroadcastd" and m and m.group(2) != "%rip" and int(m.group(1) or 0) % 32:
                raise ValueError(f"line {ln}: memory operand not 32-byte aligned: {o}")
    c = census_block(asm)
    return {"output_words_equal_lazy_forms": N, "distinct_output_forms": len(set(out_h)),
            "dynamic_instructions": sum(ex.census.values()),
            "dynamic_census": dict(sorted(ex.census.items())),
            "static_loop_census": {k: dict(sorted(v.items())) for k, v in c.items()},
            "shuffle_uops_per_block": sum(v for k, v in c[f"{P}_ht_looptop_b"].items()
                                          if k.startswith(("vperm", "vpunpck")))}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--param", type=int, choices=sorted(PARAMS), default=768)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--meta", type=Path)
    args = ap.parse_args()
    root = args.experiment.resolve()
    asm, meta = derive(root, args.param)
    if (asm, json.dumps(meta, sort_keys=True)) != (lambda a, m: (a, json.dumps(m, sort_keys=True)))(
            *derive(root, args.param)):
        raise ValueError("non-deterministic generation")
    path = root / f"asm/{NAME}.s"
    meta["output_sha256"] = sha256(asm.encode())
    if args.check:
        if not path.exists() or path.read_text() != asm:
            print(f"MISMATCH vs regeneration: {path}", file=sys.stderr)
            return 1
        print(f"ok {path.relative_to(root)} sha256={meta['output_sha256']}")
    else:
        path.write_text(asm)
        print(f"wrote {path.relative_to(root)} sha256={meta['output_sha256']}")
    print(f"proof: {meta['output_words_equal_lazy_forms']} output words have the lazy Forward's forms; "
          f"shuffle uops/block {meta['shuffle_uops_per_block']}; slots/block {meta['block_slots']}")
    if args.meta:
        args.meta.parent.mkdir(parents=True, exist_ok=True)
        args.meta.write_text(json.dumps(meta, indent=1, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
