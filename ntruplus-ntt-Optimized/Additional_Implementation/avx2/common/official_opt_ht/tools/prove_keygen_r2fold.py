#!/usr/bin/env python3
"""Algebraic proof record for the NTRU+768 / 864 / 1152 keygen R^2 fold (exact, no timing).

Notation: q = 3457, R = 2^16, qinv = q^-1 mod R, s16 = signed 16-bit wrap.
fqmul(a, b) = mulhi(a, b) - mulhi(q, mullo(a, b*qinv)) (poly.c:16-22, and the
same instruction pattern in basemul.s/baseinv.s).

 (M) Montgomery identity.  For all int16 a, b: with m = s16(a*b*qinv),
     a*b - m*q == 0 (mod 2^16), so floor(a*b/2^16) - floor(m*q/2^16)
     == (a*b - m*q)/2^16 exactly, i.e. fqmul(a, b) * R == a*b (mod q).
     Checked here exhaustively over all a for every constant the fold uses and
     on 2^22 random (a, b) pairs; the step itself is the textbook argument.
 (F) fqinv (768/1152 poly.c:52-83, 864 poly.c:68-99; the same text) is a fixed chain of fqsqr/fqmul, so for every int16
     x: fqinv(x) == x^(q-2) * R^-k (mod q) for one constant k; checked
     exhaustively over all 65536 x (k is reported).  Hence for a unit u,
     fqinv(u x) == u^-1 fqinv(x) (mod q), and fqinv(x) == 0 (mod q) iff x == 0.
 (B) BaseInv.  fqinv_batch + poly_baseinv_2 (poly.c:100-322) contain no
     addition or subtraction outside fqmul/fqsqr/fqmul_neg (audited on the
     generated source below): every output coefficient is +- a Montgomery
     product in which `inv` (the fqinv output) occurs exactly once, with every
     other factor independent of the R3 constant.  (NTRU+864: poly_baseinv_2 multiplies
     three rows per base by the inverse denominator with fqmul; 768/1152: four rows with
     fqmul / fqmul_neg; the audit below is the same.)  Official: inv = fqinv(fqmul(P, R3)),
     fold: inv' = fqinv(fqmul(P, R2)); by (M) fqmul(P, R2) == R^-1 fqmul(P, R3),
     so by (F) inv' == R inv, and every BaseInv output finv' == R * finv (mod q).
     The zero check runs on the product chain before this point and is unchanged,
     so both return the same status; on failure both zero the output.
 (P) Keygen product.  Official poly_basemul(a, b) = mont_R2(core(a, b)) with
     core bilinear and core(a, b) == a (.) b * R^-1 (mod q) by (M) (zetas are
     stored times R); mont_R2(c) = fqmul(c, R2) == c * R.  So
     basemul_nor2(a, finv') = core(a, R finv) == R core(a, finv) == poly_basemul(a, finv) (mod q)
     in every coefficient (core = the BaseMul loop that basemul_nor2 keeps verbatim).
 (T) poly_tobytes (and the 2-op-freeze variant) maps every int16 to its
     canonical residue, so pk = tobytes(h') == tobytes(h) and
     sk = tobytes(f) || tobytes(f (.) ginv') || hash_f(pk) are byte-identical.
 Bounds: finv' is an fqmul output (|x| <= 18112 for any int16 operands), and
 the interval replay (range_proof_ht/prove_ht.py) of basemul_nor2 on
 (keygen f_hat/g_hat of the lazy / HT Forward, BaseInv envelope) has no
 signed-word overflow (NTRU+768 output [-10446, 10448]; 864/1152 in their
 ht-range-proof-summary.json); tests/test_keygen_r2fold.c checks all of this
 on the real code.

  prove_keygen_r2fold.py [--param N] --experiment . --output proof.json
"""
import argparse
import json
import random
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import generate_keygen_r2fold as G  # noqa: E402
from generate_keygen_r2fold import constants, sha256  # noqa: E402

Q, QINV, R = 3457, 12929, 1 << 16


def s16(x):
    return ((x + 0x8000) & 0xFFFF) - 0x8000


def fqmul(a, b):
    return ((a * b) >> 16) - ((s16(a * s16(b * QINV)) * Q) >> 16)


def fqinv(a):   # poly.c:52-83, same chain
    t0 = fqmul(a, a); t0 = fqmul(t0, t0); t0 = fqmul(t0, t0); t0 = fqmul(t0, t0)
    t1 = fqmul(t0, a)
    t0 = fqmul(t0, t0); t0 = fqmul(t0, t0); t0 = fqmul(t0, t0)
    t1 = fqmul(t0, t1)
    t0 = fqmul(t0, t1)
    t1 = fqmul(t0, t1)
    t1 = fqmul(t1, t0)
    t0 = fqmul(t1, t1); t0 = fqmul(t0, t0)
    return fqmul(t0, t1)


def body_of(text, name):
    i = re.search(rf"^[^\n]*\b{name}\([^\n]*\n\{{", text, re.M).start()
    j = text.index("\n}\n", i)
    return text[i:j]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--param", type=int, choices=sorted(G.PARAMS), default=768)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    root = args.experiment.resolve()
    G.configure(args.param)
    BASEINV, PINS = G.BASEINV, G.PINS
    up = root / "upstream/supercop-avx2"
    k, checks = constants((up / "consts.c").read_text(), (up / "poly.c").read_text())
    rinv = pow(R, -1, Q)

    # (M) Montgomery identity
    consts = [k["R2"], k["R3"], 1, -1, 1728, -1728, 3456, -3456]
    m_fail = 0
    for b in consts:
        for a in range(-32768, 32768):
            if (fqmul(a, b) * R - a * b) % Q:
                m_fail += 1
    rng = random.Random(0x7682)
    for _ in range(1 << 22):
        a, b = rng.randint(-32768, 32767), rng.randint(-32768, 32767)
        if (fqmul(a, b) * R - a * b) % Q:
            m_fail += 1
    if m_fail:
        raise SystemExit("Montgomery identity failed")

    # (F) fqinv monomial, exhaustive
    kset = set()
    zero_ok = True
    fold_ok = True
    for x in range(-32768, 32768):
        y = fqinv(x)
        if x % Q == 0:
            zero_ok &= (y % Q == 0)
            continue
        # y * x^(q-2)^-1 = y * x == R^-k  =>  record (y * x) mod q
        kset.add((y * x) % Q)
        inv3, inv2 = fqinv(fqmul(x, k["R3"])), fqinv(fqmul(x, k["R2"]))
        fold_ok &= ((inv2 - R * inv3) % Q == 0)
    if len(kset) != 1 or not zero_ok or not fold_ok:
        raise SystemExit(f"fqinv monomial/fold check failed {len(kset)} {zero_ok} {fold_ok}")
    c = kset.pop()
    kexp = next(e for e in range(64) if pow(rinv, e, Q) == c)

    # (B) structural audit of the generated BaseInv source
    src = (root / f"src/{BASEINV}.c").read_text()
    # the Python fqmul/fqinv model above is the NTRU+768 poly.c chain; the generated source of
    # every parameter must carry exactly that text (fqmul, fqsqr, fqinv are byte-identical)
    model_text = {}
    for fn, pin in (("fqmul", "fec3e3441b99cd16"), ("fqsqr", "9dfe36d1aa7d6e1f"), ("fqinv", "1a5bfa465ffaddbf")):
        i = re.search(rf"^static inline __m256i {fn}\(", src, re.M).start()
        h = sha256(src[i:src.index("\n}\n", i) + 3].encode())
        if not h.startswith(pin):
            raise SystemExit(f"{fn}: source text differs from the modelled NTRU+768 chain")
        model_text[fn] = h
    audit = {}
    for fn in ("fqinv_batch", "poly_baseinv_2", BASEINV):
        b = body_of(src, fn)
        audit[fn] = {"add_sub_intrinsics": len(re.findall(r"_mm256_(?:add|sub)_epi16", b)),
                     "fqmul_calls": len(re.findall(r"\bfqmul(?:_neg)?\(", b)),
                     "R2FOLD_uses": b.count("NTRUPLUS_R2FOLD"), "R3_uses": b.count("NTRUPLUS_R3")}
        if audit[fn]["add_sub_intrinsics"]:
            raise SystemExit(f"{fn}: additive operation outside fqmul")
    if audit["fqinv_batch"]["R2FOLD_uses"] != 2 or sum(a["R3_uses"] for a in audit.values()) != 0:
        raise SystemExit("unexpected fold constant use")
    uses = re.findall(r"^.*\bR3_const\b.*$", body_of(src, "fqinv_batch"), re.M)
    if len(uses) != 2 or "fqmul(pc2[2], R3_const, R3qinv_const, q)" not in uses[1]:
        raise SystemExit("fold constant must feed exactly the fqinv input scaling")

    out = {
        "class": "exact algebraic proof record (Phase A; no timing)",
        "parameter": f"NTRU+{args.param}", "verdict": "pass",
        "constants": k, "constant_checks": checks,
        "montgomery_identity": {"exhaustive_constants": consts, "random_pairs": 1 << 22, "failures": 0},
        "fqinv": {"exhaustive_int16": 65536, "form": f"fqinv(x) == x^(q-2) * R^-{kexp} (mod q)",
                  "zero_iff_zero": True, "fold_relation_fqinv(fqmul(x,R2)) == R*fqinv(fqmul(x,R3))": True},
        "baseinv_source_audit": audit,
        "conclusion": ["finv' == R * finv (mod q), same BaseInv status and failure output",
                       "basemul_nor2(a, finv') == poly_basemul(a, finv) (mod q) per coefficient",
                       "pk/sk byte-identical through canonical poly_tobytes"],
        "inputs_sha256": {**PINS, f"src/{BASEINV}.c": sha256(src.encode())},
    }
    if args.param != 768:   # (the NTRU+768 record predates this check; it passes there too)
        out["modelled_function_text_sha256"] = model_text
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, indent=1) + "\n")
    print(f"R^2 fold proof PASS: fqinv(x) == x^(q-2) R^-{kexp}; fold relation exhaustive over int16 -> {args.output}")


if __name__ == "__main__":
    main()
