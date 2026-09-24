#!/usr/bin/env python3
"""Generate the NTRU+768 "HT" inverse NTT (Hwang-style data movement), optional item.

Output: asm/ntruplus768_officialopt_invntt_ht.s, a drop-in replacement for
Official poly_invntt_scale (invntt.s, pinned): same GS butterflies, twiddle
representatives, Barrett points and N^-1 scaling, only two passes:

  block    levels 6..2 of each 128-coefficient block (distances 4, 8, 16, 32,
           64) in one pass, from the Official NTT-domain layout (register r
           of block b = coefficients 128b + 8l + r) to natural order, with the
           unpack-only network found by the scratch search_inv.py:
             L(d=4, Barrett on sums), vpunpck{l,h}wd on register bit 1,
             vpunpck{l,h}wd on bit 0, vpunpck{l,h}qdq on bit 2,
             L(d=8), L(d=16), L(d=32, Barrett on sums), vperm2i128 on bit 2, L(d=64);
           32 shuffle uops per block (Official: 48) and no separate level-2 pass.
  pass A   levels 1 (radix-3, Barrett on X+Y+Z) and 0 (with the N^-1 scale)
           fused, 6 vectors per iteration.

Twiddles and constants are the ones Official applies to the same data
(symbolic operand matching, tools/symexec.py); the emitted asm is executed
symbolically and every output word must have the same interned form as the
Official poly_invntt_scale output word, i.e. bit-identical for every input.

  generate_inverse_ht.py --experiment . [--check] [--meta out.json]
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from symexec import Forms, SymExec, parse_consts, s16  # noqa: E402
from generate_forward_ht import census_block, words_lines  # noqa: E402

N = 768
Q, QINV = 3457, 12929
NAME = "ntruplus768_officialopt_invntt_ht"
OFFICIAL = "poly_invntt_scale"
TAB_A = "ntruplus768_officialopt_htinv_zetas_a"
TAB_B = "ntruplus768_officialopt_htinv_zetas_b"
PINS = {
    "upstream/supercop-avx2/consts.c": "52649ae464c507e80169367621ea4e07ec11a25dc7f162467bf1dd96dc6fb080",
    "upstream/supercop-avx2/invntt.s": "991f13a75de92a1e33c5141aa81849f9619073606989a49b9c4627ea3d852b70",
}
# ('BF', lo, hi, distance, barrett_on_sum) / ('UNP16'|'UNP64'|'PERM', i, j)
NET = [("BF", 0, 4, 4, True), ("BF", 1, 5, 4, True), ("BF", 2, 6, 4, True), ("BF", 3, 7, 4, True),
       ("UNP16", 0, 2), ("UNP16", 1, 3), ("UNP16", 4, 6), ("UNP16", 5, 7),
       ("UNP16", 0, 1), ("UNP16", 2, 3), ("UNP16", 4, 5), ("UNP16", 6, 7),
       ("UNP64", 0, 4), ("UNP64", 1, 5), ("UNP64", 2, 6), ("UNP64", 3, 7),
       ("BF", 0, 4, 8, False), ("BF", 1, 5, 8, False), ("BF", 2, 6, 8, False), ("BF", 3, 7, 8, False),
       ("BF", 0, 1, 16, False), ("BF", 2, 3, 16, False), ("BF", 4, 5, 16, False), ("BF", 6, 7, 16, False),
       ("BF", 0, 2, 32, True), ("BF", 1, 3, 32, True), ("BF", 4, 6, 32, True), ("BF", 5, 7, 32, True),
       ("PERM", 0, 4), ("PERM", 1, 5), ("PERM", 2, 6), ("PERM", 3, 7),
       ("BF", 0, 4, 64, False), ("BF", 1, 5, 64, False), ("BF", 2, 6, 64, False), ("BF", 3, 7, 64, False)]
LEVEL = {4: 6, 8: 5, 16: 4, 32: 3, 64: 2}
V = ((1 << 15) + Q // 2) // Q


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def groups():
    out, k = [], 0
    while k < len(NET):
        if NET[k][0] == "BF":
            g = [k]
            k += 1
            while k < len(NET) and NET[k][0] == "BF" and len(g) < 4 and NET[k][3] == NET[g[0]][3]:
                g.append(k)
                k += 1
            out.append(g)
        else:
            k += 1
    return out


def run_official(F, text, syms):
    ex = SymExec(F, text, syms)
    B = ex.POLY
    for w in range(N):
        ex.mem[B + 2 * w] = F.input(w)
    zmap, zqmap, snap, rdx = {}, {}, {}, {}

    def on_mul(op, data, consts):
        m = zmap if op == "vpmulhw" else zqmap
        for f, c in zip(data, consts):
            m.setdefault(f, set()).add(c)
    ex.on_mul = on_mul

    def at(label):
        def hook(e):
            if label not in rdx:
                rdx[label] = e.regs["rdx"] - e.syms["zetas_inv"]
                if label == "_looptop_start_1":
                    snap.update({w: e.mem[B + 2 * w] for w in range(N)})
        return hook
    for label in ("_looptop_start_1", "_looptop_start_0"):
        ex.hooks[ex.labels[label]] = at(label)
    ex.run(OFFICIAL, {"rdi": B})
    out = [ex.mem[B + 2 * w] for w in range(N)]
    return out, snap, zmap, zqmap, rdx, dict(sorted(ex.census.items()))


def model_block(F, zmap, zqmap, b):
    q, v = F.const(Q), F.const(V)
    r = [[F.input(128 * b + 16 * i + l) for l in range(16)] for i in range(8)]
    tw = {}
    for k, op in enumerate(NET):
        kind, i, j = op[:3]
        a, c = r[i], r[j]
        if kind == "BF":
            zr, zq, lo, hi = [], [], [], []
            for l in range(16):
                d = F.sub(a[l], c[l])
                s = F.add(a[l], c[l])
                if len(zmap.get(d, ())) != 1 or len(zqmap.get(d, ())) != 1:
                    raise ValueError(f"block {b} net {k} lane {l}: no unique Official twiddle")
                z, zqv = next(iter(zmap[d])), next(iter(zqmap[d]))
                if s16(z * QINV) != zqv:
                    raise ValueError("twiddle companion mismatch")
                m = F.sub(F.mulhi(d, F.const(z)), F.mulhi(F.mullo(d, F.const(zqv)), q))
                if op[4]:
                    s = F.sub(s, F.mullo(F.mulhrs(s, v), q))
                lo.append(s)
                hi.append(m)
                zr.append(z)
                zq.append(zqv)
            r[i], r[j] = lo, hi
            tw[k] = (tuple(zr), tuple(zq))
        elif kind == "PERM":
            r[i], r[j] = a[0:8] + c[0:8], a[8:16] + c[8:16]
        else:
            w = 1 if kind == "UNP16" else 4
            lo, hi = [], []
            for h in (0, 8):
                for s_ in range(0, 4, w):
                    lo += a[h + s_:h + s_ + w] + c[h + s_:h + s_ + w]
                    hi += a[h + 4 + s_:h + 4 + s_ + w] + c[h + 4 + s_:h + 4 + s_ + w]
            r[i], r[j] = lo, hi
    return tw, r


class Regs:
    def __init__(self, names):
        self.free = list(names)

    def get(self):
        return self.free.pop(0)

    def put(self, *r):
        self.free.extend(r)


def emit(slot_of, nslots, tab_b, tab_a, store, tail, fused):
    o = []
    e = o.append
    e("# GENERATED by common/official_opt_ht/tools/generate_inverse_ht.py -- do not edit.")
    e("# NTRU+768 Official AVX2 inverse NTT (poly_invntt_scale), HT variant: one")
    e("# levels-6..2 block pass per 128 coefficients with an unpack-only exchange")
    e("# network, then levels 1+0 (radix-3 + N^-1 scale) fused, 6 vectors per")
    e("# iteration.  Output bit-identical to Official poly_invntt_scale for every")
    e("# int16 input (symbolic proof in the generator).")
    e(".text")
    e(".p2align 5")
    e(f".global {NAME}")
    e(f".type {NAME},@function")
    e(f"{NAME}:")
    e("vmovdqa _16xq(%rip), %ymm0")
    e("")
    e("#level65432 (block pass)")
    e("vmovdqa _16xv(%rip), %ymm13")
    e(f"lea {TAB_B}(%rip), %rsi")
    e("lea 1536(%rdi), %r8")
    e("")
    e(".p2align 5")
    e("ntruplus768_officialopt_htinv_looptop_b:")
    reg = {i: f"%ymm{i + 1}" for i in range(8)}
    pool = Regs(["%ymm9", "%ymm10", "%ymm11", "%ymm12"])
    for i in range(8):
        e(f"vmovdqa {32 * i}(%rdi), {reg[i]}")
    k = 0
    gi = {g[0]: g for g in groups()}
    while k < len(NET):
        if NET[k][0] == "BF":
            grp = gi[k]
            k += len(grp)
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
            S = {g: pool.get() for g in grp}
            for g in grp:
                e(f"vpaddw {reg[NET[g][2]]}, {reg[NET[g][1]]}, {S[g]}")
            for g in grp:
                e(f"vpsubw {reg[NET[g][2]]}, {reg[NET[g][1]]}, {reg[NET[g][2]]}")
            T = {g: reg[NET[g][1]] for g in grp}     # lo registers are free now
            for g in grp:
                e(f"vpmullw {ZQ[g]}, {reg[NET[g][2]]}, {T[g]}")
            for g in grp:
                e(f"vpmulhw {ZR[g]}, {reg[NET[g][2]]}, {reg[NET[g][2]]}")
            for g in grp:
                e(f"vpmulhw %ymm0, {T[g]}, {T[g]}")
            for g in grp:
                e(f"vpsubw {T[g]}, {reg[NET[g][2]]}, {reg[NET[g][2]]}")
            if NET[grp[0]][4]:
                for g in grp:
                    e(f"vpmulhrsw %ymm13, {S[g]}, {T[g]}")
                for g in grp:
                    e(f"vpmullw %ymm0, {T[g]}, {T[g]}")
                for g in grp:
                    e(f"vpsubw {T[g]}, {S[g]}, {S[g]}")
            for g in grp:
                pool.put(T[g])
                reg[NET[g][1]] = S[g]
        else:
            kind, i, j = NET[k]
            if k == 0 or NET[k - 1][0] != kind or (kind == "UNP16" and NET[k - 1][1:] == (6, 7)):
                e(f"#shuffle {kind.lower()}")
            k += 1
            a, bb, t = reg[i], reg[j], pool.get()
            if kind == "PERM":
                e(f"vperm2i128 $0x20, {bb}, {a}, {t}")
                e(f"vperm2i128 $0x31, {bb}, {a}, {bb}")
            else:
                sfx = "wd" if kind == "UNP16" else "qdq"
                e(f"vpunpckl{sfx} {bb}, {a}, {t}")
                e(f"vpunpckh{sfx} {bb}, {a}, {bb}")
            reg[i] = t
            pool.put(a)
    e("")
    e("#store")
    for i in range(8):
        e(f"vmovdqa {reg[i]}, {32 * store[i]}(%rdi)")
    e("")
    e("add $256, %rdi")
    e(f"add ${64 * nslots}, %rsi")
    e("cmp %r8, %rdi")
    e("jb  ntruplus768_officialopt_htinv_looptop_b")
    e("")
    e("sub $1536, %rdi")
    e("")
    if fused:
        e("#level1+0 (pass A)")
        e("vmovdqa _16xw(%rip), %ymm13")
        e("vmovdqa _16xwqinv(%rip), %ymm14")
        e(f"lea {TAB_A}(%rip), %rsi")
        e("lea 256(%rdi), %r8")
        e("")
        e(".p2align 5")
        e("ntruplus768_officialopt_htinv_looptop_a:")
        pool = Regs([f"%ymm{i}" for i in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 15)])
        rows = [pool.get() for _ in range(6)]
        for b in range(6):
            e(f"vmovdqa {256 * b}(%rdi), {rows[b]}")
        out = [None] * 6
        # radix-3 of the two groups and level 0 of the three pairs are emitted
        # step-interleaved (independent chains side by side).
        seqs = []
        for be in range(2):
            X, Y, Z = rows[3 * be:3 * be + 3]
            off = 128 * be
            t0, t1, t2 = pool.get(), pool.get(), pool.get()
            seqs.append([
                f"vpsubw {Z}, {Y}, {t0}",                  # Y - Z
                f"vpmullw %ymm14, {t0}, {t1}",
                f"vpmulhw %ymm13, {t0}, {t0}",
                f"vpmulhw %ymm0, {t1}, {t1}",
                f"vpsubw {t1}, {t0}, {t0}",                # w(Y - Z)
                f"vpsubw {Y}, {X}, {t1}",                  # X - Y
                f"vpsubw {Z}, {X}, {t2}",                  # X - Z
                f"vpsubw {t0}, {t1}, {t1}",                # X - Y - w(Y - Z)
                f"vpaddw {t0}, {t2}, {t2}",                # X - Z + w(Y - Z)
                f"vpaddw {Y}, {X}, {X}",
                f"vpaddw {Z}, {X}, {X}",                   # X + Y + Z
                f"vpmullw {off + 32}(%rsi), {t1}, {Y}",
                f"vpmullw {off + 96}(%rsi), {t2}, {Z}",
                f"vpmulhw {off}(%rsi), {t1}, {t1}",
                f"vpmulhw {off + 64}(%rsi), {t2}, {t2}",
                f"vpmulhw %ymm0, {Y}, {Y}",
                f"vpmulhw %ymm0, {Z}, {Z}",
                f"vpsubw {Y}, {t1}, {t1}",                 # alpha^-1 (...)
                f"vpsubw {Z}, {t2}, {t2}",                 # alpha^-2 (...)
                f"vpmulhrsw _16xv(%rip), {X}, {Y}",
                f"vpmullw %ymm0, {Y}, {Y}",
                f"vpsubw {Y}, {X}, {X}"])                  # Barrett(X + Y + Z)
            out[3 * be:3 * be + 3] = [X, t1, t2]
            seqs[-1].append((Y, Z, t0))
        for step in zip(*[q[:-1] for q in seqs]):
            o.extend(step)
        for q in seqs:
            pool.put(*q[-1])
        seqs = []
        for t in range(3):                               # level 0: rows t, t + 3
            A, Bv = out[t], out[t + 3]
            d, m = pool.get(), pool.get()
            seqs.append([
                f"vpsubw {Bv}, {A}, {d}",
                f"vpaddw {Bv}, {A}, {A}",
                f"vpmullw 288(%rsi), {d}, {m}",
                f"vpmulhw 256(%rsi), {d}, {d}",
                f"vpmulhw %ymm0, {m}, {m}",
                f"vpsubw {m}, {d}, {d}",                   # mont(A - B, (z - z^5)^-1)
                f"vpsubw {d}, {A}, {A}",
                f"vpmullw 352(%rsi), {A}, {m}",
                f"vpmulhw 320(%rsi), {A}, {A}",
                f"vpmulhw %ymm0, {m}, {m}",
                f"vpsubw {m}, {A}, {A}",                   # N^-1 scale
                f"vpmullw 416(%rsi), {d}, {Bv}",
                f"vpmulhw 384(%rsi), {d}, {d}",
                f"vpmulhw %ymm0, {Bv}, {Bv}",
                f"vpsubw {Bv}, {d}, {d}",                  # 2 N^-1 scale
                f"vmovdqa {A}, {256 * t}(%rdi)",
                f"vmovdqa {d}, {256 * (t + 3)}(%rdi)"])
        for step in zip(*seqs):
            o.extend(step)
        e("")
        e("add $32, %rdi")
        e("cmp %r8, %rdi")
        e("jb  ntruplus768_officialopt_htinv_looptop_a")
        e("")
    else:
        # Official levels 1 and 0, verbatim (invntt.s `#level1` .. before `ret`),
        # with the zetas_inv pointer and _16xv register they expect.
        e("vmovdqa _16xv(%rip), %ymm1")
        e("lea zetas_inv(%rip), %rdx")
        e(f"add ${tail['rdx']}, %rdx")
        e("")
        o.extend(tail["text"].rstrip("\n").splitlines())
        e("")
    e("ret")
    e("")
    e(f".size {NAME},.-{NAME}")
    e("")
    e(".section .rodata")
    if fused:
        e(".p2align 5")
        e(f"{TAB_A}:  # per radix-3 group [z^-1, z^-1 qinv, z^-2, z^-2 qinv]; [(z-z^5)^-1, qinv]; [Ninv, qinv]; [2 Ninv, qinv]")
        o.extend(words_lines(tab_a))
    e(".p2align 5")
    e(f"{TAB_B}:  # per block {nslots} slots of [zeta x 16, zeta*qinv x 16]")
    o.extend(words_lines(tab_b))
    e("")
    e(".ifndef no_gnu_stack")
    e('.section .note.GNU-stack,"",@progbits')
    e(".endif")
    return "\n".join(o) + "\n"


def derive(root):
    for rel, pin in PINS.items():
        got = sha256((root / rel).read_bytes())
        if got != pin:
            raise ValueError(f"pinned input changed: {rel} {got}")
    up = root / "upstream/supercop-avx2"
    syms = parse_consts((up / "consts.c").read_text())
    F = Forms()
    out_o, snap, zmap, zqmap, rdx, census_o = run_official(F, (up / "invntt.s").read_text(), syms)
    per_block, store = [], None
    for b in range(6):
        tw, regs = model_block(F, zmap, zqmap, b)
        per_block.append(tw)
        rows = {tuple(snap[128 * b + 16 * r + l] for l in range(16)): r for r in range(8)}
        st = []
        for i in range(8):
            if tuple(regs[i]) not in rows:
                raise ValueError(f"block {b} register {i} is not an Official level-2 output row")
            st.append(rows[tuple(regs[i])])
        if sorted(st) != list(range(8)) or (store is not None and st != store):
            raise ValueError("non-uniform output layout")
        store = st
    slot_of, nslots, members = {}, 0, []
    for grp in groups():
        seen = []
        for g in grp:
            for s, rep in seen:
                if all(per_block[b][g] == per_block[b][rep] for b in range(6)):
                    slot_of[g] = s
                    break
            else:
                slot_of[g] = nslots
                seen.append((nslots, g))
                members.append(g)
                nslots += 1
    tab_b = []
    for b in range(6):
        for g in members:
            zr, zq = per_block[b][g]
            tab_b += list(zr) + list(zq)
    zi = syms["zetas_inv"]

    def dword(byte):
        if byte % 4:
            raise ValueError("unaligned dword")
        return zi[byte // 2:byte // 2 + 2] * 8
    r1, r0 = rdx["_looptop_start_1"], rdx["_looptop_start_0"]
    tab_a = []
    for be in range(2):
        base = r1 + 16 * be
        tab_a += dword(base + 1156) + dword(base + 1152) + dword(base + 1164) + dword(base + 1160)
    tab_a += dword(r0 + 1156) + dword(r0 + 1152)
    ninv, ninvq = syms["_16xNinv_scale"], syms["_16xNinv_scaleqinv"]
    tab_a += ninv + ninvq + [s16(2 * x) for x in ninv] + [s16(2 * x) for x in ninvq]
    for i in range(0, len(tab_a), 32):
        zr, zq = tab_a[i:i + 16], tab_a[i + 16:i + 32]
        if any(s16(x * QINV) != y for x, y in zip(zr, zq)):
            raise ValueError("pass A companion mismatch")
    tail = extract_levels10((up / "invntt.s").read_text())
    tail["rdx"] = r1
    asm = emit(slot_of, nslots, tab_b, tab_a, store, tail, fused=False)
    fused = emit(slot_of, nslots, tab_b, tab_a, store, tail, fused=True)
    meta = verify(F, asm, syms, out_o, 6)
    meta["rejected_fused_pass_a"] = {k: v for k, v in verify(F, fused, syms, out_o, 5).items()
                                     if k in ("output_words_equal_official_forms", "dynamic_instructions")}
    meta["official_levels_1_0_verbatim_ops"] = tail["ops"]
    meta.update({"store_rows": store, "block_slots": nslots,
                 "slot_of_butterfly": [slot_of[g] for g in sorted(slot_of)],
                 "table_bytes": {"pass_a": 2 * len(tab_a), "block": 2 * len(tab_b)},
                 "official_zetas_inv_offsets": rdx,
                 "official_dynamic_instructions": sum(census_o.values()),
                 "official_dynamic_census": census_o, "inputs_sha256": dict(PINS)})
    return asm, meta, fused


def extract_levels10(text):
    start = text.index("#level1\n")
    end = text.rindex("\nret\n")
    body = text[start:end + 1]
    labels = set(re.findall(r"^(\w+):", body, re.M))
    if labels != {"_looptop_start_1", "_looptop_j_1", "_looptop_start_0"} or "#level 0" not in body:
        raise ValueError(f"unexpected Official level-1/0 frame {labels}")
    ins = [l.split("#")[0].strip() for l in body.splitlines()]
    ins = [l for l in ins if l and not l.startswith(".") and not l.endswith(":")]
    if "ret" in ins or any("%rsp" in l for l in ins):
        raise ValueError("unexpected Official level-1/0 body")
    ops = {}
    for l in ins:
        ops[l.split()[0]] = ops.get(l.split()[0], 0) + 1
    body = re.sub(r"\b_looptop_(start_1|j_1|start_0)\b", r"ntruplus768_officialopt_htinv_looptop_\1", body)
    return {"text": body, "ops": ops}


def verify(F, asm, syms, out_o, p2align):
    for bad in ("%rsp", "call", "vzeroupper", "%rbp", "push", "pop"):
        if re.search(rf"^\s*[^#.\s].*{re.escape(bad)}", asm, re.M):
            raise ValueError(f"forbidden {bad}")
    if asm.count(".p2align 5") != p2align:
        raise ValueError("alignment directives")
    ex = SymExec(F, asm, syms)
    B = ex.POLY
    for w in range(N):
        ex.mem[B + 2 * w] = F.input(w)
    ex.run(NAME, {"rdi": B})
    out_h = [ex.mem[B + 2 * w] for w in range(N)]
    if out_h != out_o:
        raise ValueError(f"HT inverse output forms differ from Official on "
                         f"{sum(a != b for a, b in zip(out_h, out_o))} words")
    if not ex.stores <= {B + 2 * w for w in range(N)}:
        raise ValueError("store outside the polynomial")
    for ln, op, ops in ex.prog:
        for o in ops:
            m = re.fullmatch(r"(-?\d*)\((%r\w+)\)", o)
            if op != "vpbroadcastd" and m and m.group(2) != "%rip" and int(m.group(1) or 0) % 32:
                raise ValueError(f"line {ln}: memory operand not 32-byte aligned: {o}")
    c = census_block(asm)
    return {"output_words_equal_official_forms": N, "dynamic_instructions": sum(ex.census.values()),
            "dynamic_census": dict(sorted(ex.census.items())),
            "static_loop_census": {k: dict(sorted(v.items())) for k, v in c.items()},
            "shuffle_uops_per_block": sum(v for k, v in c["ntruplus768_officialopt_htinv_looptop_b"].items()
                                          if k.startswith(("vperm", "vpunpck")))}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--meta", type=Path)
    ap.add_argument("--emit-rejected-fused", type=Path,
                    help="also write the rejected fused level-1+0 variant (re-measurement only)")
    args = ap.parse_args()
    root = args.experiment.resolve()
    asm, meta, fused = derive(root)
    a2, m2, f2 = derive(root)
    if (asm, fused, json.dumps(meta, sort_keys=True)) != (a2, f2, json.dumps(m2, sort_keys=True)):
        raise ValueError("non-deterministic generation")
    if args.emit_rejected_fused:
        args.emit_rejected_fused.write_text(fused.replace(NAME, NAME + "_fused"))
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
    print(f"proof: {meta['output_words_equal_official_forms']} output words have the Official inverse's forms; "
          f"shuffle uops/block {meta['shuffle_uops_per_block']}; slots/block {meta['block_slots']}; "
          f"dynamic instructions {meta['dynamic_instructions']} (Official {meta['official_dynamic_instructions']})")
    if args.meta:
        args.meta.parent.mkdir(parents=True, exist_ok=True)
        args.meta.write_text(json.dumps(meta, indent=1, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
