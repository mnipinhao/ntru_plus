#!/usr/bin/env python3
"""Proof that the NTRU+864 / 1152 fused inverse (Inverse D) equals Official
poly_crepmod3(poly_invntt_scale(x)) word for word on the Decap domain.

The Decap domain is kem.c's `poly_basemul_scale(&m, &c, &f)` output with c and f from
poly_frombytes (canonical, [0, q-1]); that call stays unchanged in every candidate.
Steps, all fatal:

  0. generate_invntt_crep.derive(): the committed asm is the regeneration, and the
     symbolic facts hold (candidate == nosplit == crep5(pre), word for word, for every
     input; levels 6..2 == Official).  pre = the candidate without its crep5 ops.
  1. emulator == machine: the interval emulator (range_proof/avx2emu.py, via EmuHT) in
     concrete wrap mode equals the real assembled pre and Official invntt on random
     inputs.
  2. interval replay on the Decap domain (per lane): Official invntt and pre have zero
     signed-word failures, and every multiply of both is consumed by a Montgomery-by-
     constant or rounding-Barrett idiom (no high/low product is used as an integer).
     Every instruction is then exact mod q (Montgomery: r*2^16 = x*c - q*m exactly;
     Barrett: x - q*k; add/sub without overflow), so each program is, on the domain,
     a Z_q-linear map of the input: out = L(x) mod q.
  3. basis: pre(e_i) == Official(e_i) mod q for every unit vector e_i (native run of
     the assembled code), hence L_pre == L_Official and pre(x) == invntt(x) mod q on
     the whole domain; pre's output range (interval) is recorded.
  4. crep5 domain: crep5(x) == cmod3(cmod_q(x)) exactly on an interval I5 (exhaustive
     over int16, instruction semantics), and pre's output range lies in I5; Official
     poly_crepmod3 (native, all int16) == cmod3(cmod_q(x)) on an interval I0 containing
     Official's invntt output range on the domain.  cmod3(cmod_q(.)) depends on x mod q
     only, so candidate(x) = crep5(pre(x)) = crepmod3(invntt(x)) for every Decap input.

  prove_invntt_crep.py --param 864|1152 --experiment . --build build/invcrep_proof --output out.json
"""
import argparse
import ctypes
import json
import random
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
AVX2 = HERE.parents[3]
LAZY_RP = AVX2 / "common/official_opt_lazy/range_proof"
HT_RP = AVX2 / "common/official_opt_ht/range_proof_ht"
sys.path[:0] = [str(LAZY_RP), str(HT_RP), str(AVX2 / "common/official_opt_ht/tools"), str(HERE.parent)]

import avx2emu  # noqa: E402
from avx2emu import HI, HQ, LO, RS, RSQ, Q, Val  # noqa: E402
import common  # noqa: E402
from common import BASE_A, CFG, aligned_poly, configure, load_consts, sha  # noqa: E402
import ledger  # noqa: E402
import prove_ht  # noqa: E402
import generate_invntt_crep as G  # noqa: E402


def fail(msg):
    raise SystemExit(f"INVNTT-CREP PROOF FAILURE: {msg}")


def w16(x):
    return ((x + 32768) & 0xFFFF) - 32768


def ideal(x):
    """cmod3 of the centred representative of x mod q, in {-1, 0, 1}."""
    c = x % Q
    if c > Q // 2:
        c -= Q
    r = c % 3
    return -1 if r == 2 else r


def crep5(x):
    t = (x * G.CREP["k"]) >> 16
    k = w16((t * G.CREP["r"] + (1 << 14)) >> 15)
    y = w16(x - k)
    w = w16(y * G.CREP["i"])
    return w16((w * G.CREP["m"] + (1 << 14)) >> 15)


def exact_interval(f):
    """Maximal interval containing 0 on which f(x) == ideal(x), x in int16."""
    lo = 0
    while lo - 1 >= -32768 and f(lo - 1) == ideal(lo - 1):
        lo -= 1
    hi = 0
    while hi + 1 <= 32767 and f(hi + 1) == ideal(hi + 1):
        hi += 1
    return [lo, hi]


class EmuLin(prove_ht.EmuHT):
    """EmuHT that records any product atom used as an integer (non mod-q-linear use)."""

    def __init__(self, *a, **kw):
        super().__init__(*a, **kw)
        self.nonlinear = []

    def as_val(self, x, ln):
        if isinstance(x, (LO, HI, HQ, RS, RSQ)):
            self.nonlinear.append((ln, type(x).__name__))
        return super().as_val(x, ln)


def emu_run(path, entry, lanes, **kw):
    z, zi, rip = load_consts()
    e = EmuLin(str(path), z, zi, rip, **kw)
    e.set_poly(BASE_A, lanes)
    e.run(entry, {"rdi": BASE_A})
    return e, e.get_poly(BASE_A, CFG["n"])


def kinds(e):
    return sorted({v[2] for k, v in e.stats.items() if isinstance(k, int)})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--param", type=int, choices=(768, 864, 1152), required=True)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--build", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--diff-trials", type=int, default=16)
    ap.add_argument("--emit-box", type=Path, help="only write the per-lane Decap-domain box as a C header")
    args = ap.parse_args()
    n = args.param
    configure(n, args.experiment, args.build)
    if args.emit_box:
        info, m_in = ledger.basemul([Val(0, Q - 1)] * n, [Val(0, Q - 1)] * n, entry="poly_basemul_scale")
        if info["failures"]:
            fail("basemul_scale replay failure")
        rows = ",\n".join("  {%d, %d}" % (v.lo, v.hi) for v in m_in)
        args.emit_box.write_text(
            "/* GENERATED by prove_invntt_crep.py --emit-box: per-lane interval of kem.c Decap's\n"
            " * poly_basemul_scale(c, f) output, c and f canonical (interval emulator). */\n"
            f"static const int16_t decap_box[{n}][2] = {{\n{rows}\n}};\n")
        print(f"[{n}] wrote {args.emit_box} (range {ledger.rng(m_in)})")
        return
    root, build, up = CFG["experiment"], CFG["build"], CFG["upstream"]
    nm = G.Names(n)
    cand = root / f"asm/{nm.entry}.s"

    # 0. regeneration + symbolic facts
    texts, gmeta = G.derive(root, n)
    if cand.read_text() != texts["cand"]:
        fail(f"{cand} is not the generator's output")
    for v in G.VARIANTS[n]:
        if v != "cand":
            (build / f"{n}_{v}.s").write_text(texts[v])
    pre = build / f"{n}_pre.s"
    pre_entry = nm.entry + "_pre"

    # 1. emulator == machine (wrap mode), pre and Official invntt
    so = build / "invcrep_kernels.so"
    subprocess.run(["cc", "-O1", "-mavx2", "-shared", "-fPIC", "-I", str(up), "-o", str(so), str(up / "consts.c"),
                    str(up / "invntt.s"), str(up / "crepmod3.s"), str(pre), str(cand)], check=True)
    L = ctypes.CDLL(str(so))
    rng = random.Random(0x1ABC + n)
    calls = 0
    for t in range(args.diff_trials):
        x = [rng.randint(-32768, 32767) if t % 2 else rng.randint(-7000, 7700) for _ in range(n)]
        for path, entry in ((pre, pre_entry), (up / "invntt.s", "poly_invntt_scale")):
            b, arr, addr = aligned_poly(n, x)
            getattr(L, entry)(ctypes.c_void_p(addr))
            _, got = emu_run(path, entry, [Val(v, v) for v in x], wrap_mode=True)
            if list(arr) != [v.lo for v in got]:
                fail(f"emulator != machine on {entry} trial {t}")
            calls += 1
    print(f"[{n}] emulator == machine: {calls} runs (pre, Official invntt)")

    # 2. interval replay on the Decap domain
    canon = [Val(0, Q - 1)] * n
    bm_info, m_in = ledger.basemul(canon, canon, entry="poly_basemul_scale")
    if bm_info["failures"]:
        fail("basemul_scale replay failure")
    eo, oo = emu_run(up / "invntt.s", "poly_invntt_scale", m_in)
    ep, op_ = emu_run(pre, pre_entry, m_in)
    rep = {}
    for name, e, out in (("official_invntt", eo, oo), ("pre", ep, op_)):
        k = kinds(e)
        rep[name] = {"failures": len(e.failures), "output_range": ledger.rng(out), "value_kinds": k,
                     "nonlinear_product_uses": len(e.nonlinear), "levels": ledger.level_summary(e)}
        if e.failures:
            fail(f"{name}: signed-word failures {e.failures[:3]}")
        if e.nonlinear:
            fail(f"{name}: product used as an integer at lines {sorted({l for l, _ in e.nonlinear})[:5]}")
        if not set(k) <= {"add", "sub", "mont_const", "mont_const_neg", "barrett_in"}:
            fail(f"{name}: unexpected value kinds {k}")
    print(f"[{n}] Decap domain {ledger.rng(m_in)}: Official invntt out {rep['official_invntt']['output_range']}, "
          f"pre out {rep['pre']['output_range']}; 0 failures, all multiplies Montgomery/Barrett")

    # 3. basis: pre(e_i) == Official(e_i) mod q
    mism = 0
    for i in range(n):
        e_i = [0] * n
        e_i[i] = 1
        b1, a1, p1 = aligned_poly(n, e_i)
        b2, a2, p2 = aligned_poly(n, e_i)
        L.poly_invntt_scale(ctypes.c_void_p(p1))
        getattr(L, pre_entry)(ctypes.c_void_p(p2))
        mism += sum((x - y) % Q != 0 for x, y in zip(a1, a2))
    # random Decap-domain inputs as a sanity check of the linear argument (per-lane box)
    rnd = 0
    for t in range(2000):
        x = [rng.randint(v.lo, v.hi) for v in m_in]
        b1, a1, p1 = aligned_poly(n, x)
        b2, a2, p2 = aligned_poly(n, x)
        L.poly_invntt_scale(ctypes.c_void_p(p1))
        getattr(L, pre_entry)(ctypes.c_void_p(p2))
        rnd += sum((u - v) % Q != 0 for u, v in zip(a1, a2))
    if mism or rnd:
        fail(f"pre != Official mod q: basis {mism}, random {rnd}")
    print(f"[{n}] basis: pre(e_i) == Official(e_i) mod q for all {n} unit vectors ({n * n} words); "
          f"2000 random box inputs agree mod q")

    # 4. crep5 domain and Official crepmod3 domain
    i5 = exact_interval(crep5)
    vals = list(range(-32768, 32768))
    table = {}
    for s in range(0, len(vals), n):
        chunk = vals[s:s + n] + [0] * (n - len(vals[s:s + n]))
        b, arr, addr = aligned_poly(n, chunk)
        L.poly_crepmod3(ctypes.c_void_p(addr))
        for x, r in zip(chunk, arr):
            table.setdefault(x, r)
    i0 = exact_interval(lambda x: table[x])
    pr, orr = rep["pre"]["output_range"], rep["official_invntt"]["output_range"]
    if not (i5[0] <= pr[0] and pr[1] <= i5[1]):
        fail(f"pre range {pr} not inside the crep5 exact domain {i5}")
    if not (i0[0] <= orr[0] and orr[1] <= i0[1]):
        fail(f"Official invntt range {orr} not inside the Official crepmod3 exact domain {i0}")
    # crep5 of the machine: candidate == crep5(pre) on the native code too (random domain inputs)
    cm = 0
    for t in range(2000):
        x = [rng.randint(v.lo, v.hi) for v in m_in]
        b1, a1, p1 = aligned_poly(n, x)
        b2, a2, p2 = aligned_poly(n, x)
        getattr(L, pre_entry)(ctypes.c_void_p(p1))
        getattr(L, nm.entry)(ctypes.c_void_p(p2))
        cm += sum(crep5(u) != v for u, v in zip(a1, a2))
    if cm:
        fail(f"native candidate != crep5(native pre) on {cm} words")
    print(f"[{n}] crep5 exact on {i5} (pre range {pr}); Official crepmod3 exact on {i0} "
          f"(Official invntt range {orr}); native candidate == crep5(pre) on 2000 inputs")

    summary = {
        "class": "Inverse D proof: symbolic + interval + mod-q basis + crep domain (Phase A; no timing)",
        "parameter": f"NTRU+{n}", "verdict": "pass",
        "candidate_asm": str(cand.relative_to(root)), "candidate_asm_sha256": sha(cand),
        "generator": {"symbolic": gmeta["proof_symbolic"], "sigma": {k: v for k, v in gmeta["sigma"].items()
                                                                     if k != "table_words"},
                      "proof_variant_sha256": gmeta["proof_variant_sha256"]},
        "sources_sha256": {f: sha(up / f) for f in ("invntt.s", "crepmod3.s", "consts.c", "basemul.s")},
        "tool_sha256": {p.name: sha(p) for p in [*sorted(LAZY_RP.glob("*.py")), LAZY_RP / "images.c",
                                                 HT_RP / "prove_ht.py", HERE,
                                                 HERE.parent / "generate_invntt_crep.py",
                                                 HERE.parent / "symexec_ext.py"]},
        "emulator_machine_differential_runs": calls,
        "decap_domain": {"input": "poly_basemul_scale(c, f), c and f from poly_frombytes: [0, q-1] (kem.c Decap)",
                         "input_range": ledger.rng(m_in)},
        "interval": {k: {x: v[x] for x in ("failures", "output_range", "value_kinds", "nonlinear_product_uses")}
                     for k, v in rep.items()},
        "interval_levels_pre": rep["pre"]["levels"],
        "basis_mod_q": {"unit_vectors": n, "mismatching_words": 0, "random_box_inputs": 2000},
        "crep5": {"exact_domain": i5, "pre_output_range": pr},
        "official_crepmod3": {"exact_domain": i0, "official_invntt_output_range": orr},
        "native_candidate_equals_crep5_of_pre_inputs": 2000,
        "conclusion": "ntruplus%d_officialopt_invntt_crep(x) == poly_crepmod3(poly_invntt_scale(x)) for every "
                      "Decap input x (every per-lane value of poly_basemul_scale(c, f) with canonical c, f)" % n,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=1, default=str) + "\n")
    print(f"[{n}] Inverse D proof PASS -> {args.output}")


if __name__ == "__main__":
    main()
