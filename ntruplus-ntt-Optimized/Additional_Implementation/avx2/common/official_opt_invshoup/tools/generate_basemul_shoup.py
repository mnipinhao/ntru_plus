#!/usr/bin/env python3
"""Generate the NTRU+768 / 864 / 1152 Shoup (Barrett-companion) BaseMul with lazy accumulation.

Outputs (both committed; the .s is what every KEM links, the .c is its derivation input):
  src/ntruplus<N>_officialopt_basemul_shoup.c   AVX2 intrinsics, static const zeta tables
  asm/ntruplus<N>_officialopt_basemul_shoup.s   the pinned-compiler output of that .c,
                                                 deterministically post-processed

  void ntruplus<N>_officialopt_basemul_shoup(poly *r, const poly *a, const poly *b)

computes r = a * b in Z_q[x]/(x^D - zeta_k) per base (Official coefficient-plane layout, D = 3
for NTRU+864, 4 for 768 / 1152), in the *canonical* scale (Official poly_basemul's output
scale, so no R^2 pass), with b the canonical operand (every b word in [0, q)) and a the lazy
operand (any int16 inside the proven caller envelope, prove_basemul_shoup.py).  Contract:
r must not overlap a or b (restrict), all three 32-byte aligned (vmovdqa).

Arithmetic, per 16-lane product a_i * b_j:
  companion  b'' = mulhu(16 b, 38825)          (38825 = ceil(2^27 / q); b'' ~ b 2^15 / q)
  term       lo16(a b) - lo16(q * mulhrs(a, b''))  == a b - q round(a b'' / 2^15)  (exact)
and every output word is  SUM lo16(a_i b_j) - lo16(q * SUM mulhrs(a_i, b''_j))  (+ the zeta
terms, with a precomputed (zeta, round(zeta 2^15 / q)) pair): the lo16 parts and the quotients
are accumulated lazily, one vpmullw(q) and one subtract per output.  Mod 2^16 this is exact,
so the output is the exact integer whenever that integer is an int16 (the range proof).

zeta tables: from the Official basemul zeta block (poly_basemul: `lea zetas(%rip), %rcx; add
$K, %rcx`, per two bases 64 bytes [zeta*R*qinv x16, zeta*R x16]): zeta = cmod_q(zeta*R * R^-1),
+zeta for the first base of each pair ("positive zeta"), -zeta for the second.

Pinned compiler: the .s is gcc output; --check recompiles with the pinned compiler and flags
(COMPILER below; any other compiler version is refused, not silently accepted) and requires
byte identity of both files.  Post-processing: the .file and .ident lines are dropped, the
function entry gets .p2align 5, a header comment is prepended.  The generator also executes
the .s symbolically (symexec_ext.py) and requires every output word to have the interned form
of the reference formula above (bit-identical for every input), stores only inside r, and
records the stack slots gcc uses (fixed offsets from the realigned %rsp, no data-dependent
address).

  generate_basemul_shoup.py --param N --experiment . [--check] [--meta out.json]
"""
import argparse
import hashlib
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "official_opt_ht/tools"))
sys.path.insert(0, str(HERE))
from symexec import parse_consts, s16  # noqa: E402
from symexec_ext import FormsX, SymExecX  # noqa: E402

Q, QINV = 3457, 12929
RINV = pow(1 << 16, -1, Q)
CU = -(-(1 << 27) // Q)                # 38825 = ceil(2^27 / q)
COMPILER = {"cc": "gcc", "version": "gcc (Ubuntu 15.2.0-16ubuntu1) 15.2.0",
            "flags": ["-O3", "-mavx2", "-mtune=alderlake", "-fschedule-insns", "-fsched-pressure",
                      "-fno-asynchronous-unwind-tables", "-fcf-protection=none", "-fno-stack-protector",
                      "-S"]}
PARAMS = {
    768: {"d": 4, "pins": {
        "upstream/supercop-avx2/consts.c": "52649ae464c507e80169367621ea4e07ec11a25dc7f162467bf1dd96dc6fb080",
        "upstream/supercop-avx2/basemul.s": "60b614a0f85b4de2dc02a44da0c1823be8b6a43ca720b29ea14eb39ef71e3fbe"}},
    864: {"d": 3, "pins": {
        "upstream/supercop-avx2/consts.c": "0c60897a0d2e8264a75f44b5b7ef49bbaa7a5f55cf3019ffc1b0ac9864534412",
        "upstream/supercop-avx2/basemul.s": "42b9639d4d619ba2214fba73b86f9029a078b1711c5e77bf7b4a26c770d0e761"}},
    1152: {"d": 4, "pins": {
        "upstream/supercop-avx2/consts.c": "0c60897a0d2e8264a75f44b5b7ef49bbaa7a5f55cf3019ffc1b0ac9864534412",
        "upstream/supercop-avx2/basemul.s": "966ce066ec26e0989ad11f83f2de3fbea990132ac2f7836c1c61a04fb987ca01"}},
}


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def cen(x):
    x %= Q
    return x - Q if x > Q // 2 else x


def comp_exact(z):
    """round(z * 2^15 / q), symmetric (q odd: no ties)."""
    num = z * 32768
    return (num + Q // 2) // Q if num >= 0 else -((-num + Q // 2) // Q)


def products(d):
    """Output k = SUM_{i+j=k} a_i b_j + zeta * s_k,  s_k = SUM_{i+j=k+d} a_i b_j (k < d-1)."""
    out = []
    for k in range(d):
        direct = [(i, k - i) for i in range(k + 1)]
        wrapped = [(i, k + d - i) for i in range(k + 1, d)] if k < d - 1 else []
        out.append((direct, wrapped))
    return out


def zeta_table(n, root):
    d = PARAMS[n]["d"]
    up = root / "upstream/supercop-avx2"
    bm = (up / "basemul.s").read_text()
    m = re.search(r"\.global poly_basemul\npoly_basemul:\n(?:.*\n)*?lea\s+zetas\(%rip\), %rcx\nadd\s+\$(\d+), %rcx\n", bm)
    if not m:
        raise ValueError("Official poly_basemul zeta block not found")
    k = int(m.group(1))
    body = bm[m.end():bm.index("_reduce_R2_loop")]
    if f"lea {2 * n}(%rsi), %r8" not in body or body.count("vmovdqa 32(%rcx),") != 2 or \
            not re.search(r"add \$64,\s+%rcx", body):
        raise ValueError("unexpected Official poly_basemul zeta access")
    z = parse_consts((up / "consts.c").read_text())["zetas"]
    nch = n // (16 * d)
    tab = []
    for it in range(nch // 2):
        zq = z[k // 2 + 32 * it:k // 2 + 32 * it + 16]
        zr = z[k // 2 + 32 * it + 16:k // 2 + 32 * it + 32]
        if any(s16(a * QINV) != b for a, b in zip(zr, zq)):
            raise ValueError("Official basemul zeta companion mismatch")
        zz = [cen(a * RINV) for a in zr]
        tab.append((zz, [comp_exact(v) for v in zz]))
        tab.append(([-v for v in zz], [-comp_exact(v) for v in zz]))
    return k, tab


def c_source(n, tab):
    d = PARAMS[n]["d"]
    fn = f"ntruplus{n}_officialopt_basemul_shoup"
    nch = len(tab)
    rows = []
    for zz, zc in tab:
        rows.append("  {{" + ", ".join(map(str, zz)) + "},\n   {" + ", ".join(map(str, zc)) + "}}")
    L = [f"/* GENERATED by common/official_opt_invshoup/tools/generate_basemul_shoup.py --param {n} -- do not edit.",
         f" * NTRU+{n} Shoup (Barrett-companion) BaseMul with lazy accumulation; derivation input of",
         f" * asm/{fn}.s (pinned compiler, see the generator).  r = a * b mod (x^{d} - zeta) per base,",
         " * canonical scale; b canonical ([0, q)), a lazy (proven caller envelope); r, a, b 32-byte",
         " * aligned and r not overlapping a or b. */",
         "#include <immintrin.h>", "#include <stdint.h>", '#include "params.h"', '#include "poly.h"', "",
         f"#if NTRUPLUS_N != {n}", "#error parameter", "#endif", "",
         f"/* per base: 16 x zeta (canonical scale, sign applied), 16 x round(zeta * 2^15 / q) */",
         f"static const int16_t {fn}_zt[{nch}][2][16] __attribute__((aligned(32))) = {{",
         ",\n".join(rows), "};", "",
         "#define LO(x, y) _mm256_mullo_epi16(x, y)", "#define QT(x, y) _mm256_mulhrs_epi16(x, y)",
         "#define ADD(x, y) _mm256_add_epi16(x, y)", "#define SUB(x, y) _mm256_sub_epi16(x, y)",
         "#define LD(p) _mm256_load_si256((const __m256i *)(p))",
         "#define ST(p, v) _mm256_store_si256((__m256i *)(p), v)",
         f"/* companion b'' = mulhu(16 b, {CU}) = floor(b * {CU} / 2^12), b in [0, q); {CU} = ceil(2^27 / q) */",
         "#define COMP(x) _mm256_mulhi_epu16(_mm256_slli_epi16(x, 4), cu)", "",
         f"void {fn}(poly *restrict r, const poly *restrict pa, const poly *restrict pb)", "{",
         f"    const __m256i q = _mm256_set1_epi16({Q}), cu = _mm256_set1_epi16((short){CU});",
         "    int16_t *c = r->coeffs;", "    const int16_t *a = pa->coeffs, *b = pb->coeffs;",
         f"    for (int k = 0; k < {nch}; k++, a += {16 * d}, b += {16 * d}, c += {16 * d}) {{",
         f"        const __m256i z = LD({fn}_zt[k][0]), zc = LD({fn}_zt[k][1]);"]
    L.append("        " + " ".join(f"__m256i a{i} = LD(a + {16 * i});" for i in range(d)))
    L.append("        " + " ".join(f"__m256i b{i} = LD(b + {16 * i});" for i in range(d)))
    L.append("        " + " ".join(f"__m256i p{i} = COMP(b{i});" for i in range(d)))

    def lsum(pairs):
        e = [f"LO(a{i}, b{j})" for i, j in pairs]
        return nest(e)

    def qsum(pairs):
        e = [f"QT(a{i}, p{j})" for i, j in pairs]
        return nest(e)
    for k, (direct, wrapped) in enumerate(products(d)):
        if wrapped:
            L.append(f"        __m256i s{k} = SUB({lsum(wrapped)}, LO({qsum(wrapped)}, q));")
    for k, (direct, wrapped) in enumerate(products(d)):
        lo = [f"LO(a{i}, b{j})" for i, j in direct] + ([f"LO(s{k}, z)"] if wrapped else [])
        hi = [f"QT(a{i}, p{j})" for i, j in direct] + ([f"QT(s{k}, zc)"] if wrapped else [])
        L.append(f"        __m256i l{k} = {nest(lo)}, h{k} = {nest(hi)};")
    for k in range(d):
        L.append(f"        ST(c + {16 * k}, SUB(l{k}, LO(h{k}, q)));")
    L += ["    }", "}", ""]
    return "\n".join(L)


def nest(e):
    """1: x; 2: ADD(x, y); 3: ADD(ADD(x, y), z); 4: ADD(ADD(w, x), ADD(y, z)) (the scratch shapes)."""
    if len(e) == 1:
        return e[0]
    if len(e) == 2:
        return f"ADD({e[0]}, {e[1]})"
    if len(e) == 3:
        return f"ADD({nest(e[:2])}, {e[2]})"
    if len(e) == 4:
        return f"ADD({nest(e[:2])}, {nest(e[2:])})"
    raise ValueError("more than 4 terms")


def compile_c(n, root, csrc):
    ver = subprocess.run([COMPILER["cc"], "--version"], capture_output=True, text=True, check=True).stdout.splitlines()[0]
    if ver != COMPILER["version"]:
        raise SystemExit(f"pinned compiler {COMPILER['version']!r} required, found {ver!r}; "
                         "the committed .s stays authoritative (see docs)")
    up = root / "upstream/supercop-avx2"
    with tempfile.TemporaryDirectory() as tmp:
        c = Path(tmp) / f"ntruplus{n}_officialopt_basemul_shoup.c"
        c.write_text(csrc)
        s = Path(tmp) / "out.s"
        subprocess.run([COMPILER["cc"], *COMPILER["flags"], "-I", str(up), "-o", str(s), str(c)], check=True)
        return s.read_text()


def postprocess(n, raw):
    fn = f"ntruplus{n}_officialopt_basemul_shoup"
    out = []
    for line in raw.splitlines():
        code = line.strip()
        if code.startswith((".file", ".ident")):
            continue
        out.append(line)
    text = "\n".join(out) + "\n"
    # function entry alignment: gcc's .p2align 4 before the .globl -> .p2align 5
    head = re.search(rf"\t\.p2align 4\n\t\.globl\t{fn}\n", text)
    if not head:
        raise ValueError("unexpected gcc function header")
    text = text[:head.start()] + f"\t.p2align 5\n\t.globl\t{fn}\n" + text[head.end():]
    if '.section\t.note.GNU-stack,"",@progbits' not in text:
        raise ValueError("gcc output lacks the GNU-stack note")
    hdr = [f"# GENERATED by common/official_opt_invshoup/tools/generate_basemul_shoup.py --param {n} -- do not edit.",
           f"# NTRU+{n} Shoup BaseMul: {COMPILER['version']} {' '.join(COMPILER['flags'])} output of",
           f"# src/{fn}.c (.file/.ident dropped, entry .p2align 5).  Canonical-scale a*b per base; b canonical,",
           "# a in the proven caller envelope (prove_basemul_shoup.py); r must not overlap a or b."]
    return "\n".join(hdr) + "\n" + text


def reference_forms(F, n, tab):
    d = PARAMS[n]["d"]
    q = F.const(Q)
    cu = F.const(s16(CU))
    out = []
    for ch, (zz, zc) in enumerate(tab):
        base = 16 * d * ch
        a = [[F.input(base + 16 * i + l) for l in range(16)] for i in range(d)]
        b = [[F.input(n + base + 16 * i + l) for l in range(16)] for i in range(d)]
        rows = [[None] * 16 for _ in range(d)]
        for l in range(16):
            p = [F.mulhu(F.scale(b[j][l], 16), cu) for j in range(d)]

            def lo(pairs):
                f = F.ZERO
                for i, j in pairs:
                    f = F.add(f, F.mullo(a[i][l], b[j][l]))
                return f

            def qt(pairs):
                f = F.ZERO
                for i, j in pairs:
                    f = F.add(f, F.mulhrs(a[i][l], p[j]))
                return f
            for k, (direct, wrapped) in enumerate(products(d)):
                lk, hk = lo(direct), qt(direct)
                if wrapped:
                    s = F.sub(lo(wrapped), F.mullo(qt(wrapped), q))
                    lk = F.add(lk, F.mullo(s, F.const(zz[l])))
                    hk = F.add(hk, F.mulhrs(s, F.const(zc[l])))
                rows[k][l] = F.sub(lk, F.mullo(hk, q))
        for k in range(d):
            out += rows[k]
    return out


def symbolic_check(n, asm, tab, F=None):
    F = F or FormsX()
    fn = f"ntruplus{n}_officialopt_basemul_shoup"
    text = re.sub(r"^\t\.value\t", "\t.short\t", asm, flags=re.M)
    ex = SymExecX(F, text, {})
    R, A, B = 0x100000, 0x200000, 0x300000
    for w in range(n):
        ex.mem[A + 2 * w] = F.input(w)
        ex.mem[B + 2 * w] = F.input(n + w)
    ex.run(fn, {"rdi": R, "rsi": A, "rdx": B})
    got = [ex.mem.get(R + 2 * w) for w in range(n)]
    ref = reference_forms(F, n, tab)
    bad = sum(g != r for g, r in zip(got, ref))
    if bad:
        raise ValueError(f"{fn}: {bad} output words differ from the reference formula")
    if not ex.stores <= {R + 2 * w for w in range(n)}:
        raise ValueError("store outside r")
    slots = {}
    for a in sorted(ex.stack):
        off = (a - ex.STACK) // 32 * 32
        kind = "constant" if F.value(ex.stack[a]) is not None else "data"
        if slots.setdefault(off, kind) != kind:
            slots[off] = "mixed"
    return {"output_words_equal_reference_forms": n, "dynamic_census": dict(sorted(ex.census.items())),
            "dynamic_instructions": sum(ex.census.values()),
            "stack_slot_offsets_from_entry_rsp": sorted(ex.stack_offsets),
            "stack_slot_contents": {str(k): v for k, v in sorted(slots.items())}}, F


def derive(root, n):
    cfg = PARAMS[n]
    for rel, pin in cfg["pins"].items():
        got = sha256((root / rel).read_bytes())
        if got != pin:
            raise ValueError(f"pinned input changed: {rel} {got}")
    k, tab = zeta_table(n, root)
    csrc = c_source(n, tab)
    asm = postprocess(n, compile_c(n, root, csrc))
    sym, _ = symbolic_check(n, asm, tab)
    fn = f"ntruplus{n}_officialopt_basemul_shoup"
    meta = {"parameter": n, "degree": cfg["d"], "bases": len(tab), "inputs_sha256": dict(cfg["pins"]),
            "official_zeta_block_byte_offset": k, "companion_constant": CU, "compiler": COMPILER,
            "zeta_table": [{"zeta": zz, "companion": zc} for zz, zc in tab[:2]] + ["..."],
            "symbolic": sym,
            "output_sha256": {f"src/{fn}.c": sha256(csrc.encode()), f"asm/{fn}.s": sha256(asm.encode())}}
    return {f"src/{fn}.c": csrc, f"asm/{fn}.s": asm}, meta


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--param", type=int, choices=(768, 864, 1152), required=True)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--meta", type=Path)
    args = ap.parse_args()
    root = args.experiment.resolve()
    files, meta = derive(root, args.param)
    f2, m2 = derive(root, args.param)
    if files != f2 or json.dumps(meta, sort_keys=True) != json.dumps(m2, sort_keys=True):
        raise ValueError("non-deterministic generation")
    bad = 0
    for rel, text in files.items():
        path = root / rel
        if args.check:
            if not path.exists() or path.read_text() != text:
                print(f"MISMATCH vs regeneration: {rel}", file=sys.stderr)
                bad += 1
            else:
                print(f"ok {rel} sha256={meta['output_sha256'][rel]}")
        else:
            path.write_text(text)
            print(f"wrote {rel}")
    s = meta["symbolic"]
    print(f"proof: {s['output_words_equal_reference_forms']} output words == reference Shoup formula; "
          f"dynamic instructions {s['dynamic_instructions']}; stack slots {s['stack_slot_offsets_from_entry_rsp']}")
    if args.meta:
        args.meta.parent.mkdir(parents=True, exist_ok=True)
        args.meta.write_text(json.dumps(meta, indent=1, sort_keys=True) + "\n")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
