#!/usr/bin/env python3
"""Generate the NTRU+768 keygen R^2 fold (BaseMul R^2 pass folded into BaseInv).

Official keygen computes h = poly_basemul(g_hat, finv) and poly_basemul(f_hat,
ginv).  poly_basemul is a Montgomery core (every coefficient is congruent to
the true base product times R^-1, R = 2^16) followed by a separate pass that
multiplies every coefficient by R^2 in the Montgomery domain (basemul.s
`_reduce_R2_loop`: mont(c, R2) = c*R mod q), i.e. 48 Montgomery vectors per
call.  Both keygen products take a BaseInv output, and BaseInv's single field
inversion first scales its input by the constant R3 = R^3 mod q
(poly.c fqinv_batch: inv = fqmul(pc2[2], R3)).  Using R2 = R^2 there instead
scales the (multiplicative, addition-free) inversion input by R^-1, hence
every BaseInv output by R; the core product of such an inverse is then
congruent to the Official BaseMul output, and poly_tobytes (canonical for
every int16) makes pk/sk byte-identical.  Proof and bounds:
tools/prove_keygen_r2fold.py, tests/test_keygen_r2fold.c.

Outputs (experiment-relative):
  asm/ntruplus768_officialopt_basemul_nor2.s        Official poly_basemul without the R^2 pass
  src/ntruplus768_officialopt_baseinv_r2fold.c      Official poly_baseinv (poly.c:1-358) with R3 -> R2
  src/kem_lazy_r2fold.c                              src/kem_lazy.c with the 2 keygen BaseInv and the
                                                     2 keygen BaseMul calls rebound (enc/dec untouched)

  generate_keygen_r2fold.py --experiment . [--check] [--meta out.json]
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

Q, QINV, R = 3457, 12929, 1 << 16
BASEMUL = "ntruplus768_officialopt_basemul_nor2"
BASEINV = "ntruplus768_officialopt_baseinv_r2fold"
PINS = {
    "upstream/supercop-avx2/basemul.s": "60b614a0f85b4de2dc02a44da0c1823be8b6a43ca720b29ea14eb39ef71e3fbe",
    "upstream/supercop-avx2/poly.c": "cf8dc307c7acce70270f623ccc1ea8354e2580e307986b4e8fbabcbc6181d77b",
    "upstream/supercop-avx2/consts.c": "52649ae464c507e80169367621ea4e07ec11a25dc7f162467bf1dd96dc6fb080",
    # generate_forward_caller_lazy.py --param 768 output (its --check is a prerequisite)
    "src/kem_lazy.c": "ffd9165c36466c2ecc57e4a157a2a847dc9f19d1fc249ebbc9c1c46baa22fd7d",
}


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def s16(x):
    return ((x + 0x8000) & 0xFFFF) - 0x8000


def centred(x):
    x %= Q
    return x - Q if x > Q // 2 else x


def constants(consts_c, poly_c):
    d = dict(re.findall(r"#define\s+(\w+)\s+(-?\d+)\s*$", consts_c, re.M))
    p = dict(re.findall(r"#define\s+(\w+)\s+(-?\d+)\s*$", poly_c, re.M))
    r2, r2q, rinv = int(d["R2"]), int(d["R2qinv"]), int(d["Rinv"])
    r3, r3q = int(p["NTRUPLUS_R3"]), int(p["NTRUPLUS_R3_QINV"])
    checks = {
        "R2 == R^2 mod q": centred(R * R) == r2,
        "R3 == R^3 mod q": centred(R ** 3) == r3,
        "Rinv == R^-1 mod q": centred(pow(R, -1, Q)) == rinv,
        "R2 == R3 * R^-1 mod q": centred(r3 * pow(R, -1, Q)) == r2,
        "R2qinv == R2 * qinv mod 2^16": s16(r2 * QINV) == r2q,
        "R3qinv == R3 * qinv mod 2^16": s16(r3 * QINV) == r3q,
        "qinv * q == 1 mod 2^16": (QINV * Q) % R == 1,
    }
    if not all(checks.values()):
        raise ValueError(f"constant algebra failed: {checks}")
    return {"R2": r2, "R2qinv": r2q, "R3": r3, "R3qinv": r3q, "Rinv": rinv}, checks


def gen_basemul(src):
    entry = ".global poly_basemul\npoly_basemul:\n"
    if src.count(entry) != 1 or not src.startswith(entry):
        raise ValueError("unexpected basemul.s head")
    end_core = "jb  _looptop_basemul\n"
    r2_head = "\nmov %rdi, %r8\nsub $1536, %rdi\n\nvmovdqa _16xR2qinv(%rip), %ymm15\nvmovdqa _16xR2(%rip),     %ymm1\n"
    r2_tail = "jb  _reduce_R2_loop\n\nret\n"
    i = src.index(end_core) + len(end_core)
    j = src.index(r2_tail) + len(r2_tail)
    if src.count(end_core) != 1 or src.count(r2_tail) != 1 or not src[i:].startswith(r2_head):
        raise ValueError("unexpected R^2 pass frame")
    core, removed = src[len(entry):i], src[i:j]
    # the removed block: 12 iterations x 4 vectors of mont(x, R2) in place, nothing else
    ins = [l.split("#")[0].strip() for l in removed.splitlines()]
    ins = [l for l in ins if l and not l.startswith(".") and not l.endswith(":")]
    ops = {}
    for l in ins:
        ops[l.split()[0]] = ops.get(l.split()[0], 0) + 1
    expect = {"mov": 1, "sub": 1, "vmovdqa": 10, "vpmullw": 4, "vpmulhw": 8, "vpsubw": 4,
              "add": 1, "cmp": 1, "jb": 1, "ret": 1}
    if ops != expect:
        raise ValueError(f"unexpected R^2 pass body {ops}")
    for l in ins:
        if l.startswith(("vpmullw", "vpmulhw", "vpsubw")):
            m = re.fullmatch(r"(\w+)\s+(%ymm\d+),\s*(%ymm\d+),\s*(%ymm\d+)", l)
            if not m:
                raise ValueError(l)
    if "ret" in core or "_reduce_R2" in core or "%rsp" in core:
        raise ValueError("unexpected core content")
    labels = set(re.findall(r"^(\w+):", core, re.M))
    if labels != {"_looptop_basemul"}:
        raise ValueError(f"labels {labels}")
    core = core.replace("_looptop_basemul", f"{BASEMUL}_looptop")
    text = ("# GENERATED by common/official_opt_ht/tools/generate_keygen_r2fold.py -- do not edit.\n"
            "# Official NTRU+768 AVX2 poly_basemul (basemul.s:1-373) without its R^2 pass\n"
            "# (basemul.s:375-420, ret re-emitted): every output coefficient is the Montgomery core,\n"
            "# congruent to the base product times R^-1.  Keygen only, on an R-scaled\n"
            f"# BaseInv output ({BASEINV}); Encap/Decap keep poly_basemul.\n"
            f".text\n.p2align 5\n.global {BASEMUL}\n.type {BASEMUL},@function\n{BASEMUL}:\n"
            + core + "\nret\n\n" + f".size {BASEMUL},.-{BASEMUL}\n\n"
            ".ifndef no_gnu_stack\n.section .note.GNU-stack,\"\",@progbits\n.endif\n")
    return text, {"removed_R2_pass_ops_static": ops, "removed_mont_vectors_per_call": 48,
                  "core_lines_kept": core.count("\n")}


def gen_baseinv(poly_c, k):
    head_end = "int poly_baseinv(poly *r, const poly *a)\n{"
    if poly_c.count(head_end) != 1:
        raise ValueError("poly_baseinv definition")
    i = poly_c.index(head_end)
    j = poly_c.index("\n}\n", i) + 3
    body = poly_c[:j]
    funcs = re.findall(r"^(?:static inline )?\w[\w ]*?\b(\w+)\(", body, re.M)
    if funcs != ["fqmul", "fqmul_neg", "fqsqr", "fqinv", "fqinv_batch", "poly_baseinv_2", "poly_baseinv"]:
        raise ValueError(f"unexpected functions {funcs}")
    old_c = ("    const __m256i R3qinv_const = _mm256_set1_epi16(NTRUPLUS_R3_QINV);\n"
             "    const __m256i R3_const     = _mm256_set1_epi16(NTRUPLUS_R3);\n")
    use = "    __m256i inv = fqmul(pc2[2], R3_const, R3qinv_const, q);\n"
    if body.count(old_c) != 1 or body.count(use) != 1 or body.count("R3_const") != 2 or \
            body.count("NTRUPLUS_R3") != 4:
        raise ValueError("unexpected R3 use")
    new_c = ("    /* R^2 fold: R2 = R3 * R^-1 mod q scales this multiplicative inversion's input\n"
             "     * by R^-1, hence every BaseInv output by R (ntruplus768_officialopt_basemul_nor2). */\n"
             "    const __m256i R3qinv_const = _mm256_set1_epi16(NTRUPLUS_R2FOLD_QINV);\n"
             "    const __m256i R3_const     = _mm256_set1_epi16(NTRUPLUS_R2FOLD);\n")
    body = body.replace(old_c, new_c, 1)
    defs = "#define NTRUPLUS_R3_QINV  -16436\n"
    if body.count(defs) != 1:
        raise ValueError("R3 defines")
    body = body.replace(defs, defs + f"#define NTRUPLUS_R2FOLD       {k['R2']}   /* R^2 mod q = R3 * R^-1 */\n"
                        f"#define NTRUPLUS_R2FOLD_QINV  {k['R2qinv']}  /* R2FOLD * qinv mod 2^16 */\n", 1)
    body = body.replace(head_end, f"int {BASEINV}(poly *r, const poly *a);\n\n"
                        f"int {BASEINV}(poly *r, const poly *a)\n{{", 1)
    if body.count("poly_baseinv(") != 0:
        raise ValueError("residual poly_baseinv")
    text = ("/*\n * GENERATED by common/official_opt_ht/tools/generate_keygen_r2fold.py -- do not edit.\n"
            " * Official NTRU+768 AVX2 poly_baseinv (poly.c:1-358: fqmul .. poly_baseinv) as\n"
            f" * {BASEINV}: the only change is the fqinv input scale R3 -> R2,\n"
            " * so the output is the Official inverse times R (mod q), same bounds.\n */\n" + body)
    return text, {"slice_lines": body.count("\n"), "functions": funcs}


def function_span(text, signature):
    i = text.index(signature)
    j = text.index("\n}\n", i) + 3
    return i, j


def gen_kem(kem):
    if kem.count("poly_baseinv(") != 2 or kem.count("poly_basemul(") != 4:
        raise ValueError("unexpected Official keygen call graph")
    out = kem
    for sig, old, new in (
            ("static inline int genf_derand(", "return poly_baseinv(finv, f);", f"return {BASEINV}(finv, f);"),
            ("static inline int geng_derand(", "return poly_baseinv(ginv, g);", f"return {BASEINV}(ginv, g);"),
            ("static inline void crypto_kem_keypair_derand(", "poly_basemul(&h, g, finv);",
             f"{BASEMUL}(&h, g, finv);"),
            ("static inline void crypto_kem_keypair_derand(", "poly_basemul(&h, f, ginv);",
             f"{BASEMUL}(&h, f, ginv);")):
        i, j = function_span(out, sig)
        seg = out[i:j]
        if seg.count(old) != 1:
            raise ValueError(f"{sig}: {old}")
        out = out[:i] + seg.replace(old, new, 1) + out[j:]
    if out.count("poly_baseinv(") != 0 or out.count("poly_basemul(") != 2:
        raise ValueError("rebinding count")
    i, j = function_span(out, "static inline int crypto_kem_enc_derand(")
    k, m = function_span(out, "int crypto_kem_dec(")
    if out[i:j].count("poly_basemul(") != 1 or out[k:m].count("poly_basemul(") != 1:
        raise ValueError("Encap/Decap BaseMul must stay Official")
    anchor = "#ifdef SUPERCOP\n"
    if out.count(anchor) != 1:
        raise ValueError("anchor")
    out = out.replace(anchor, f"int {BASEINV}(poly *, const poly *);\n"
                      f"void {BASEMUL}(poly *, const poly *, const poly *);\n\n" + anchor, 1)
    head = ("/*\n * GENERATED by common/official_opt_ht/tools/generate_keygen_r2fold.py -- do not edit.\n"
            " * src/kem_lazy.c (caller-lazy KEM) with the keygen R^2 fold: genf/geng BaseInv ->\n"
            f" * {BASEINV}, the two keygen BaseMul -> {BASEMUL}.\n"
            " * Encap/Decap and every other line unchanged.\n */\n")
    return head + out


def derive(root):
    for rel, pin in PINS.items():
        got = sha256((root / rel).read_bytes())
        if got != pin:
            raise ValueError(f"pinned input changed: {rel} {got}")
    up = root / "upstream/supercop-avx2"
    k, checks = constants((up / "consts.c").read_text(), (up / "poly.c").read_text())
    bm, bm_meta = gen_basemul((up / "basemul.s").read_text())
    bi, bi_meta = gen_baseinv((up / "poly.c").read_text(), k)
    kem = gen_kem((root / "src/kem_lazy.c").read_text())
    outputs = {f"asm/{BASEMUL}.s": bm, f"src/{BASEINV}.c": bi, "src/kem_lazy_r2fold.c": kem}
    meta = {"constants": k, "constant_checks": checks, "basemul": bm_meta, "baseinv": bi_meta,
            "kem_rebound": {"keygen_baseinv": 2, "keygen_basemul": 2, "encap_decap_basemul_official": 2},
            "inputs_sha256": dict(PINS)}
    return outputs, meta


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--meta", type=Path)
    args = ap.parse_args()
    root = args.experiment.resolve()
    outputs, meta = derive(root)
    if (outputs, meta) != derive(root):
        raise ValueError("non-deterministic generation")
    bad = []
    for rel, text in outputs.items():
        path = root / rel
        meta.setdefault("output_sha256", {})[rel] = sha256(text.encode())
        if args.check:
            if not path.exists() or path.read_text() != text:
                bad.append(rel)
            else:
                print(f"ok {rel} sha256={sha256(text.encode())}")
        else:
            path.write_text(text)
            print(f"wrote {rel} sha256={sha256(text.encode())}")
    if bad:
        print("MISMATCH vs regeneration: " + ", ".join(bad), file=sys.stderr)
        return 1
    if args.meta:
        args.meta.parent.mkdir(parents=True, exist_ok=True)
        args.meta.write_text(json.dumps(meta, indent=1, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
