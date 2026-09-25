#!/usr/bin/env python3
"""Generate the NTRU+864 / NTRU+1152 fused inverse NTT + crepmod3 ("Inverse D").

Output: asm/ntruplus<N>_officialopt_invntt_crep.s, entry
ntruplus<N>_officialopt_invntt_crep(poly *), a drop-in for the Decap pair

    poly_invntt_scale(&m); poly_crepmod3(&m);

derived textually from the pinned Official invntt.s (every instruction of
levels 6..2 is verbatim; only labels are renamed), with three changes:

  (C) sigma fold.  sigma = Ns * R^-1 (Ns = NINV_SCALE of consts.c) is folded
      into the level-1 radix-3 twiddles: every alpha^-1 / alpha^-2 word z of
      the Official level-1 broadcast dwords becomes cmod_q(z * Ns * R^-1) with
      its z*qinv companion (a new 32-byte table), and the level-1 X+Y+Z
      Barrett becomes a Montgomery multiply by Ns.  All three level-1 outputs
      are then scaled by Ns*R^-1, so level 0 needs no scale multiply:
  8-op level 0.  t = mont(A-B, z0); out_a = A+B-t; out_b = t+t
      (Official: out_a = mont(A+B-t, Ns), out_b = mont(t, 2Ns)).
  crep5, fused into level 0 before the stores (5 ops per vector):
      k = mulhrs(mulhw(x, 4853), 128); y = x - k; r = mulhrs(mullw(y, -21845), -1).
  (B) split block pass.  The Official levels-6..3 block loop is split into two
      memory passes, (L6, L5) and (L4, L3); arithmetic and layout unchanged.

Variants written only with --emit-proof-variants DIR (proof inputs, never linked
into a KEM): <N>_pre.s (the candidate without the crep5 ops: the "pre-crep"
values) and <N>_nosplit.s (the candidate without the block-pass split).

Gates inside the generator (all fatal): pinned input sha256; exact textual
anchors and counts; symbolic execution (common/official_opt_ht/tools/symexec.py)
of the candidate, both proof variants and Official:
  * candidate == nosplit, all N output words the same interned form (B is
    bit-identical for every input);
  * candidate == crep5(pre) word for word (the fused crep5 is exactly the
    5-op formula on the pre-crep value);
  * pre's levels 6..2 are Official's (same forms at the start of level 1);
  * stores only inside the polynomial, no stack/call/vzeroupper.
The mod-q equivalence, the interval range proof on the Decap domain and the
crep5 domain check are prove_invntt_crep.py.

  generate_invntt_crep.py --param 864|1152 --experiment . [--check] [--meta out.json]
      [--emit-proof-variants DIR]
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "official_opt_ht/tools"))
sys.path.insert(0, str(HERE))
from symexec import parse_consts, s16  # noqa: E402
from symexec_ext import FormsX as Forms, SymExecX as SymExec  # noqa: E402

Q, QINV = 3457, 12929
RINV = pow(1 << 16, -1, Q)
CREP = {"k": 4853, "r": 128, "i": -21845, "m": -1}
PARAMS = {
    864: {"nr": 6, "zoff": 1728, "pins": {
        # imported, never-edited SUPERCOP 20260831 crypto_kem/ntruplus864/avx2
        "upstream/supercop-avx2/invntt.s": "2da75c486e34432e9b9759c0627541f3cee71e7ad7f177108bb1b7ed4c460078",
        "upstream/supercop-avx2/crepmod3.s": "3a77881752003f2483330aa1177870ea5d862cb7816a98227073ad914ae89ac1",
        "upstream/supercop-avx2/consts.c": "0c60897a0d2e8264a75f44b5b7ef49bbaa7a5f55cf3019ffc1b0ac9864534412"}},
    1152: {"nr": 8, "zoff": 1728, "pins": {
        # imported, never-edited SUPERCOP 20260831 crypto_kem/ntruplus1152/avx2
        "upstream/supercop-avx2/invntt.s": "129d462f9053839d817355dcf366555f0100ccee6620a72b0ecb4cea8f4ac37c",
        "upstream/supercop-avx2/crepmod3.s": "6e60a465409f262fb57fc217708eddcf8c60be0042be8293985177d305ede2ce",
        "upstream/supercop-avx2/consts.c": "0c60897a0d2e8264a75f44b5b7ef49bbaa7a5f55cf3019ffc1b0ac9864534412"}},
}
# NTRU+768: the source of levels 6..2 is the current-best HT inverse (its block pass fuses the
# radix-2 level 2); only its verbatim Official levels 1 and 0 change (sigma fold, 8-op level 0,
# crep5).  No split: the HT block pass is one pass by design.
PARAMS[768] = {"nr": 8, "zoff": 1152, "source": "asm/ntruplus768_officialopt_invntt_ht.s", "pins": {
    # imported, never-edited SUPERCOP 20260831 crypto_kem/ntruplus768/avx2
    "upstream/supercop-avx2/invntt.s": "991f13a75de92a1e33c5141aa81849f9619073606989a49b9c4627ea3d852b70",
    "upstream/supercop-avx2/crepmod3.s": "87334090de02e4e451d36162870c357646d7bba095470fbc6ff106f29b5f5cd1",
    "upstream/supercop-avx2/consts.c": "52649ae464c507e80169367621ea4e07ec11a25dc7f162467bf1dd96dc6fb080",
    # common/official_opt_ht/tools/generate_inverse_ht.py output (its --check is a prerequisite)
    "asm/ntruplus768_officialopt_invntt_ht.s": "999388bbad8f3fbf0ea35d40c9c88fa50104a97af44a92b13994f6f13106b499"}}
HTINV768 = "ntruplus768_officialopt_invntt_ht"
OFFICIAL = "poly_invntt_scale"
VARIANTS = {768: ("cand", "pre"), 864: ("cand", "pre", "nosplit"), 1152: ("cand", "pre", "nosplit")}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def cen(x):
    x %= Q
    return x - Q if x > Q // 2 else x


class Names:
    def __init__(self, n):
        self.n = n
        self.p = f"ntruplus{n}_officialopt"
        self.entry = f"{self.p}_invntt_crep"
        self.lab = f"{self.p}_invcrep_looptop"
        self.sig = f"{self.p}_invcrep_l1sigma"
        self.crep = {k: f"{self.p}_invcrep_16x{v}" for k, v in
                     (("k", "4853"), ("r", "128"), ("i", "inv3"), ("m", "m1"))}


def once(text, old, new, what):
    if text.count(old) != 1:
        raise ValueError(f"anchor {what!r} occurs {text.count(old)} times")
    return text.replace(old, new)


def sections(text):
    """Official invntt.s -> (block pass, level 2, level 1, level 0 up to the final ret)."""
    i2, i1, i0 = text.index("#level2\n"), text.index("#level1\n"), text.index("#level 0\n")
    ir = re.compile(r"\n *ret\n").search(text, i0).start()
    head = text[:i2]
    if not head.startswith(f".global {OFFICIAL}\n{OFFICIAL}:\n"):
        raise ValueError("unexpected Official entry")
    return head[len(f".global {OFFICIAL}\n{OFFICIAL}:\n"):], text[i2:i1], text[i1:i0], text[i0:ir]


def sections_768(text):
    """HT inverse -> (block pass incl. level 2 and the level-1 setup, level 1, level 0, .rodata tables)."""
    head = f".global {HTINV768}\n.type {HTINV768},@function\n{HTINV768}:\n"
    s = text.index(head) + len(head)
    i1, i0 = text.index("#level1\n"), text.index("#level 0\n")
    ir = re.compile(r"\n *ret\n").search(text, i0)
    t0 = text.index(".section .rodata\n")
    t1 = text.index(".ifndef no_gnu_stack")
    ren = lambda x: x.replace("ntruplus768_officialopt_htinv_", "ntruplus768_officialopt_invcrep_")
    return ren(text[s:i1]), ren(text[i1:i0]), ren(text[i0:ir.start()]), ren(text[t0:t1])


def crep_ops(xs, ts, c):
    """crep5 on registers xs with temporaries ts; c: operand of each constant."""
    o = [f"vpmulhw   {c['k']}, {x}, {t}" for x, t in zip(xs, ts)]
    o += [f"vpmulhrsw {c['r']}, {t}, {t}" for t in ts]
    o += [f"vpsubw    {t}, {x}, {x}" for x, t in zip(xs, ts)]
    o += [f"vpmullw   {c['i']}, {x}, {x}" for x in xs]
    o += [f"vpmulhrsw {c['m']}, {x}, {x}" for x in xs]
    return o


def split_block(block, nm, n, nr):
    """Split the levels-6..3 block loop before #level4 into two memory passes."""
    regs = [f"%ymm{4 + i}" for i in range(6)] if n == 864 else [f"%ymm{3 + i}" for i in range(8)]
    step = 32 * nr
    # the loop close of the Official block pass
    close = (f"add ${step}, %rdi\nadd $64,  %rdx\ncmp %r8,  %rdi\n"
             f"jb {'' if n == 1152 else ' '}{nm.lab}_6543\n")
    block = once(block, close, f"add ${step}, %rdi\nadd $64,  %rdx\ncmp %r8,  %rdi\njb  {nm.lab}_43\n",
                 "block-pass loop close")
    # every block register is live across the split point, nothing else is
    ins = ["#split: store after level 5, second memory pass for levels 4 and 3"]
    ins += [f"vmovdqa {r}, {32 * j}(%rdi)" for j, r in enumerate(regs)]
    ins += [f"add ${step}, %rdi", "add $64,  %rdx", "cmp %r8,  %rdi", f"jb  {nm.lab}_6543",
            f"sub ${2 * n}, %rdi", f"sub ${64 * (2 * n // step)}, %rdx", "", ".p2align 5", f"{nm.lab}_43:"]
    ins += [f"vmovdqa {32 * j}(%rdi), {r}" for j, r in enumerate(regs)]
    return once(block, "#level4\n", "\n".join(ins) + "\n\n#level4\n", "#level4")


def emit(n, nr, parts, variant):
    """variant: 'cand' (split + crep5), 'pre' (split, no crep5), 'nosplit' (crep5, no split)."""
    nm = Names(n)
    zoff = PARAMS[n]["zoff"]
    if n == 768:
        block, l1, l0, _ = parts
        l2 = ""
        ren = [("ntruplus768_officialopt_invcrep_looptop_start_1", f"{nm.lab}_1"),
               ("ntruplus768_officialopt_invcrep_looptop_j_1", f"{nm.lab}_j1")]
    else:
        block, l2, l1, l0 = parts
        ren = [("_looptop_start_6543", f"{nm.lab}_6543"), ("_looptop_start_2", f"{nm.lab}_2"),
               ("_looptop_j_2", f"{nm.lab}_j2"), ("_looptop_start_1", f"{nm.lab}_1"),
               ("_looptop_j_1", f"{nm.lab}_j1")]

    def rename(t):
        for a, b in ren:
            t = re.sub(rf"\b{a}\b", b, t)
        return t
    block, l2, l1 = rename(block), rename(l2), rename(l1)
    if variant != "nosplit" and n != 768:
        block = split_block(block, nm, n, nr)
    # level 1: sigma twiddles from the new table, X+Y+Z Barrett -> Montgomery by Ns
    l1 = once(l1, "#level1\n", f"#level1\nvmovdqa _16xNinv_scale(%rip), %ymm1\nlea {nm.sig}(%rip), %rcx\n",
              "#level1")
    for d, reg, what in ((0, 4, "z^-1qinv"), (8, 5, "z^-2qinv"), (4, 6, "z^-1"), (12, 7, "z^-2")):
        l1 = once(l1, f"vpbroadcastd {zoff + d}(%rdx), %ymm{reg} #{what}\n",
                  f"vpbroadcastd {d or ''}(%rcx), %ymm{reg} #sigma*{what}\n", f"level-1 {what}")
    l1 = once(l1, "#reduce2\nvpmulhrsw %ymm1, %ymm11, %ymm14\nvpmullw %ymm0,  %ymm14, %ymm14\n"
                  "vpsubw  %ymm14, %ymm11, %ymm11\n",
              "#montns (X+Y+Z times Ns*R^-1)\nvpmullw _16xNinv_scaleqinv(%rip), %ymm11, %ymm14\n"
              "vpmulhw %ymm1, %ymm11, %ymm11\nvpmulhw %ymm0, %ymm14, %ymm14\nvpsubw  %ymm14, %ymm11, %ymm11\n",
              "level-1 X+Y+Z Barrett")
    l1 = once(l1, "add $16,  %rdx\n", "add $16,  %rdx\nadd $16,  %rcx\n", "level-1 zeta advance")
    if l1.count("vpbroadcastd") != 4 or "(%rdx)" in l1:
        raise ValueError("level-1 twiddle rebinding incomplete")
    # the Official level-0 prologue loads the zetas at zoff/zoff+4 (%rdx) (qinv companion first)
    if not re.search(rf"vpbroadcastd {zoff}\(%rdx\), %ymm2\s*#\(z-z\^5\)\^-1\nvpbroadcastd {zoff + 4}\(%rdx\), %ymm3", l0):
        raise ValueError("unexpected Official level-0 zeta loads")
    h = n                                      # level-0 partner offset in bytes (N/2 words)
    c = {"k": "%ymm3", "r": "%ymm4", "i": "%ymm5", "m": "%ymm6"}
    L = ["#level 0 (8-op; sigma folded into level 1; crep5 fused)",
         f"vpbroadcastd {zoff}(%rdx), %ymm1 #(z-z^5)^-1 qinv", f"vpbroadcastd {zoff + 4}(%rdx), %ymm2 #(z-z^5)^-1"]
    if variant != "pre":
        L += [f"vmovdqa {nm.crep[k]}(%rip), {c[k]}" for k in ("k", "r", "i", "m")]
    L += [f"lea {h}(%rdi), %r8", "", ".p2align 5", f"{nm.lab}_0:",
          "vmovdqa   (%rdi), %ymm7", "vmovdqa 32(%rdi), %ymm8", "vmovdqa 64(%rdi), %ymm9",
          f"vmovdqa {h}(%rdi), %ymm10", f"vmovdqa {h + 32}(%rdi), %ymm11", f"vmovdqa {h + 64}(%rdi), %ymm12",
          "", "#update",
          "vpsubw %ymm10, %ymm7, %ymm13", "vpsubw %ymm11, %ymm8, %ymm14", "vpsubw %ymm12, %ymm9, %ymm15",
          "vpaddw %ymm10, %ymm7, %ymm7", "vpaddw %ymm11, %ymm8, %ymm8", "vpaddw %ymm12, %ymm9, %ymm9",
          "", "#mul",
          "vpmullw %ymm1, %ymm13, %ymm10", "vpmullw %ymm1, %ymm14, %ymm11", "vpmullw %ymm1, %ymm15, %ymm12",
          "vpmulhw %ymm2, %ymm13, %ymm13", "vpmulhw %ymm2, %ymm14, %ymm14", "vpmulhw %ymm2, %ymm15, %ymm15",
          "", "#reduce",
          "vpmulhw %ymm0, %ymm10, %ymm10", "vpmulhw %ymm0, %ymm11, %ymm11", "vpmulhw %ymm0, %ymm12, %ymm12",
          "vpsubw %ymm10, %ymm13, %ymm13", "vpsubw %ymm11, %ymm14, %ymm14", "vpsubw %ymm12, %ymm15, %ymm15",
          "", "#combine: out_a = A+B-t, out_b = 2t",
          "vpsubw %ymm13, %ymm7, %ymm7", "vpsubw %ymm14, %ymm8, %ymm8", "vpsubw %ymm15, %ymm9, %ymm9",
          "vpaddw %ymm13, %ymm13, %ymm13", "vpaddw %ymm14, %ymm14, %ymm14", "vpaddw %ymm15, %ymm15, %ymm15"]
    if variant != "pre":
        L += ["", "#crep5"] + crep_ops(["%ymm7", "%ymm8", "%ymm9"], ["%ymm10", "%ymm11", "%ymm12"], c) \
            + crep_ops(["%ymm13", "%ymm14", "%ymm15"], ["%ymm10", "%ymm11", "%ymm12"], c)
    L += ["", "#store", "vmovdqa %ymm7,   (%rdi)", "vmovdqa %ymm8, 32(%rdi)", "vmovdqa %ymm9, 64(%rdi)",
          f"vmovdqa %ymm13, {h}(%rdi)", f"vmovdqa %ymm14, {h + 32}(%rdi)", f"vmovdqa %ymm15, {h + 64}(%rdi)",
          "", "add $96, %rdi", "cmp %r8, %rdi", f"jb  {nm.lab}_0", "", "ret"]
    what = {"cand": "", "pre": " [PROOF VARIANT pre: no crep5; never linked into a KEM]",
            "nosplit": " [PROOF VARIANT nosplit: no block-pass split; never linked into a KEM]"}[variant]
    entry = nm.entry + {"cand": "", "pre": "_pre", "nosplit": "_nosplit"}[variant]
    if n == 768:
        desc = ["# NTRU+768 Official AVX2 fused inverse NTT + crepmod3: replaces the Decap pair",
                "# poly_invntt_scale(&m); poly_crepmod3(&m) (current best: ntruplus768_officialopt_invntt_ht).",
                "# Levels 6..2 are the HT inverse block pass (verbatim); sigma = Ns*R^-1 folded into the",
                "# level-1 twiddles and the level-1 X+Y+Z Montgomery; 8-op level 0 with the 5-op crepmod3",
                "# fused before the stores.  Output == crepmod3(invntt(x)) of Official on the Decap domain",
                "# (prove_invntt_crep.py); not a general-input poly_invntt_scale."]
    else:
        desc = [f"# NTRU+{n} Official AVX2 fused inverse NTT + crepmod3 (Inverse D): replaces the Decap pair",
                "# poly_invntt_scale(&m); poly_crepmod3(&m).  Levels 6..2 are Official (verbatim, the",
                "# block pass split into (L6,L5) and (L4,L3) memory passes); sigma = Ns*R^-1 folded into",
                "# the level-1 twiddles and the level-1 X+Y+Z Montgomery; 8-op level 0 with the 5-op",
                "# crepmod3 fused before the stores.  Output == crepmod3(invntt(x)) of Official on the",
                "# Decap domain (prove_invntt_crep.py); not a general-input poly_invntt_scale."]
    top = [f"# GENERATED by common/official_opt_invshoup/tools/generate_invntt_crep.py --param {n} "
           f"-- do not edit.{what}", *desc,
           ".text", ".p2align 5", f".global {entry}", f".type {entry},@function", f"{entry}:"]
    body = block + l2 + l1 + "\n".join(L) + "\n"
    return "\n".join(top) + "\n" + body + f".size {entry},.-{entry}\n"


def tables(n, sig, extra=""):
    nm = Names(n)
    t = [""] + ([extra.rstrip("\n")] if extra else [".section .rodata"]) + [".p2align 5",
         f"{nm.sig}:  # level 1: per iteration [z^-1 qinv, z^-1, z^-2 qinv, z^-2] dwords, each z = cmod_q(z_off*Ns*R^-1)"]
    t += [".short " + ", ".join(str(v) for v in sig[i:i + 8]) for i in range(0, len(sig), 8)]
    for k in ("k", "r", "i", "m"):
        t += [".p2align 5", f"{nm.crep[k]}:", ".short " + ", ".join([str(CREP[k])] * 16)]
    t += ["", ".ifndef no_gnu_stack", '.section .note.GNU-stack,"",@progbits', ".endif", ""]
    return "\n".join(t)


def official_run(F, text, syms, n):
    ex = SymExec(F, text, syms)
    B = ex.POLY
    for w in range(n):
        ex.mem[B + 2 * w] = F.input(w)
    rdx, snap = {}, {}

    def at(label):
        def hook(e):
            if label not in rdx:
                rdx[label] = e.regs["rdx"] - e.syms["zetas_inv"]
                if label == "_looptop_start_1":
                    snap.update({w: e.mem[B + 2 * w] for w in range(n)})
        return hook
    for label in ("_looptop_start_1", "_looptop_start_0"):
        ex.hooks[ex.labels[label]] = at(label)
    ex.run(OFFICIAL, {"rdi": B})
    return [ex.mem[B + 2 * w] for w in range(n)], snap, rdx, dict(sorted(ex.census.items()))


def run_variant(F, text, syms, n, entry, level1_label=None):
    ex = SymExec(F, text, syms)
    B = ex.POLY
    for w in range(n):
        ex.mem[B + 2 * w] = F.input(w)
    snap = {}
    if level1_label:
        def take(e):
            if not snap:
                snap.update({w: e.mem[B + 2 * w] for w in range(n)})
        ex.hooks[ex.labels[level1_label]] = take
    ex.run(entry, {"rdi": B})
    if not ex.stores <= {B + 2 * w for w in range(n)}:
        raise ValueError(f"{entry}: store outside the polynomial")
    return [ex.mem[B + 2 * w] for w in range(n)], snap, dict(sorted(ex.census.items()))


def crep_forms(F, x):
    k = F.mulhrs(F.mulhi(x, F.const(CREP["k"])), F.const(CREP["r"]))
    y = F.sub(x, k)
    return F.mulhrs(F.mullo(y, F.const(CREP["i"])), F.const(CREP["m"]))


def check_text(asm):
    for bad in ("%rsp", "call", "vzeroupper", "%rbp", "push", "pop"):
        if re.search(rf"^\s*[^#.\s].*{re.escape(bad)}", asm, re.M):
            raise ValueError(f"forbidden {bad}")
    lines = [l.split("#", 1)[0].strip() for l in asm.splitlines()]
    lines = [l for l in lines if l]
    for i, l in enumerate(lines):          # entry, every loop head and every table is 32-byte aligned
        if l.endswith(":") and lines[i - 1] != ".p2align 5" and not lines[i - 1].startswith(".type"):
            raise ValueError(f"label {l} not preceded by .p2align 5")
    for line in asm.splitlines():
        code = line.split("#", 1)[0].strip()
        m = re.search(r"(?:^|[\s,])(-?\d*)\((%r\w+)\)", code)
        if m and not code.startswith(("vpbroadcastd", "lea")) and m.group(2) != "%rip" and int(m.group(1) or 0) % 32:
            raise ValueError(f"memory operand not 32-byte aligned: {code}")


def derive(root, n):
    cfg = PARAMS[n]
    nm = Names(n)
    for rel, pin in cfg["pins"].items():
        got = sha256((root / rel).read_bytes())
        if got != pin:
            raise ValueError(f"pinned input changed: {rel} {got}")
    up = root / "upstream/supercop-avx2"
    ctext = (up / "consts.c").read_text()
    syms = parse_consts(ctext)
    ns = int(re.search(r"#define NINV_SCALE (-?\d+)\n", ctext).group(1))
    nsq = int(re.search(r"#define NINV_SCALE_QINV (-?\d+)\n", ctext).group(1))
    if s16(ns * QINV) != nsq or syms["_16xNinv_scale"] != [ns] * 16 or syms["_16xNinv_scaleqinv"] != [nsq] * 16:
        raise ValueError("NINV_SCALE / companion")
    otext = (up / "invntt.s").read_text()
    parts = sections_768((root / cfg["source"]).read_text()) if n == 768 else sections(otext)
    F = Forms()
    out_o, snap_o, rdx, census_o = official_run(F, otext, syms, n)
    r1, r0 = rdx["_looptop_start_1"], rdx["_looptop_start_0"]
    zi = syms["zetas_inv"]
    iters = (r0 - r1) // 16
    sig = []
    for it in range(iters):
        base = (r1 + cfg["zoff"] + 16 * it) // 2
        zq1, z1, zq2, z2 = zi[base:base + 2], zi[base + 2:base + 4], zi[base + 4:base + 6], zi[base + 6:base + 8]
        for zz, zq in ((z1, zq1), (z2, zq2)):
            if any(s16(a * QINV) != b for a, b in zip(zz, zq)):
                raise ValueError("Official level-1 companion mismatch")
        n1 = [cen(a * ns * RINV) for a in z1]
        n2 = [cen(a * ns * RINV) for a in z2]
        sig += [s16(a * QINV) for a in n1] + n1 + [s16(a * QINV) for a in n2] + n2
    tab = tables(n, sig, parts[3] if n == 768 else "")
    texts = {v: emit(n, cfg["nr"], parts, v) + tab for v in VARIANTS[n]}
    for v, t in texts.items():
        check_text(t)
    syms_c = dict(syms)
    out_c, snap_c, census_c = run_variant(F, texts["cand"], syms_c, n, nm.entry, f"{nm.lab}_1")
    out_p, snap_p, census_p = run_variant(F, texts["pre"], syms_c, n, nm.entry + "_pre", f"{nm.lab}_1")
    if n != 768:
        out_s, _, census_s = run_variant(F, texts["nosplit"], syms_c, n, nm.entry + "_nosplit")
        if out_c != out_s:
            raise ValueError(f"split changes {sum(a != b for a, b in zip(out_c, out_s))} output forms")
    if out_c != [crep_forms(F, x) for x in out_p]:
        raise ValueError("fused crep5 != crep5(pre) on some word")
    if [snap_c[w] for w in range(n)] != [snap_o[w] for w in range(n)] or \
            [snap_p[w] for w in range(n)] != [snap_o[w] for w in range(n)]:
        raise ValueError("levels 6..2 differ from Official")
    meta = {
        "parameter": n, "entry": nm.entry,
        "inputs_sha256": dict(cfg["pins"]),
        "sigma": {"Ns": ns, "Ns_qinv": nsq, "Rinv_mod_q": RINV, "sigma_mod_q": cen(ns * RINV),
                  "level1_iterations": iters, "official_level1_zetas_inv_byte_offset": r1 + cfg["zoff"],
                  "official_level0_zetas_inv_byte_offset": r0 + cfg["zoff"], "table_words": sig},
        "crep5_constants": CREP,
        "proof_symbolic": {
            "candidate_equals_crep5_of_pre_all_words": n,
            "levels_6_to_2_equal_official_at_level1_entry_words": n},
        "dynamic_instructions": {"candidate": sum(census_c.values()), "pre": sum(census_p.values()),
                                 "official_invntt": sum(census_o.values())},
        "dynamic_census": {"candidate": census_c, "official_invntt": census_o},
        "output_sha256": {f"asm/{nm.entry}.s": sha256(texts["cand"].encode())},
        "proof_variant_sha256": {f"{n}_{v}.s": sha256(texts[v].encode()) for v in VARIANTS[n] if v != "cand"},
    }
    if n != 768:
        meta["proof_symbolic"]["candidate_equals_nosplit_all_words"] = n
        meta["dynamic_instructions"]["nosplit"] = sum(census_s.values())
    else:
        meta["source_levels_6_to_2"] = cfg["source"]
    return texts, meta


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--param", type=int, choices=(768, 864, 1152), required=True)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--meta", type=Path)
    ap.add_argument("--emit-proof-variants", type=Path, help="write <N>_pre.s and <N>_nosplit.s here")
    args = ap.parse_args()
    root = args.experiment.resolve()
    texts, meta = derive(root, args.param)
    t2, m2 = derive(root, args.param)
    if texts != t2 or json.dumps(meta, sort_keys=True) != json.dumps(m2, sort_keys=True):
        raise ValueError("non-deterministic generation")
    nm = Names(args.param)
    path = root / f"asm/{nm.entry}.s"
    if args.check:
        if not path.exists() or path.read_text() != texts["cand"]:
            print(f"MISMATCH vs regeneration: {path}", file=sys.stderr)
            return 1
        print(f"ok {path.relative_to(root)} sha256={meta['output_sha256'][f'asm/{nm.entry}.s']}")
    else:
        path.write_text(texts["cand"])
        print(f"wrote {path.relative_to(root)}")
    if args.emit_proof_variants:
        args.emit_proof_variants.mkdir(parents=True, exist_ok=True)
        for v in VARIANTS[args.param]:
            if v != "cand":
                (args.emit_proof_variants / f"{args.param}_{v}.s").write_text(texts[v])
    d = meta["dynamic_instructions"]
    print(f"proof: candidate == crep5(pre){'' if args.param == 768 else ' and == nosplit'} on all {args.param} words; "
          f"levels 6..2 == Official; "
          f"dynamic instructions {d['candidate']} (Official invntt {d['official_invntt']})")
    if args.meta:
        args.meta.parent.mkdir(parents=True, exist_ok=True)
        args.meta.write_text(json.dumps(meta, indent=1, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
