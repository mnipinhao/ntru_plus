#!/usr/bin/env python3
"""Range and mod-q proof of the NTRU+768 / 864 / 1152 Shoup BaseMul on its two KEM callers.

Callers (kem.c; the keygen nor2 BaseMuls and the Decap poly_basemul_scale are unchanged):
  Encap   basemul_shoup(&c, &r, &h)       a = r_hat (HT Forward of cbd1, [-1,1]), b = h from pk
  Decap   basemul_shoup(&f, &c, &hinv)    a = c - f_hat (c canonical ciphertext poly, f_hat = HT
                                          Forward of the crepmod3 output), b = hinv from sk
b is canonical in both (poly_frombytes); a's per-lane envelopes are the HT (= lazy) Forward
interval replays of common/official_opt_ht/range_proof_ht/prove_ht.py (ledger domains
"encap_r/m,reenc[-1,1]" and "decap_msg[-2,2]", minus [0, q-1] for the Decap poly_sub).
Steps, all fatal:

  1. symbolic: the committed asm computes, for every input, exactly the reference Shoup formula
     (generate_basemul_shoup.symbolic_check) with the zeta table derived from the pinned Official
     basemul/consts; every output word depends only on the inputs of its own base and lane;
  2. evaluator == machine: the symbolic forms evaluated on random full-int16 inputs equal the
     real assembled asm (validates the vpmulhuw / vpmulhrsw / vpmullw modelling);
  3. exhaustive per-term bounds (tools/shoup_bounds.c, instruction semantics): every data term
     a*b - q*mulhrs(a, b'') over the caller's whole a envelope x b in [0, q), and every zeta term
     over the triangle-bounded s range for each (zeta, companion) of the table;
  4. triangle bounds for every s_k and output word; all true values are int16, so the lazy
     mod-2^16 accumulation returns the exact integer, which is == a*b (mod q) per base;
     consumers: Encap poly_add(c, m_hat) stays int16 (m_hat = the same HT Forward domain),
     Decap tobytes is canonical on every int16 (Barrett + sign fix);
  5. mod q vs Official: native basemul_shoup(e_i, e_j) == poly_basemul(e_i, e_j) (mod q) for
     all D^2 unit-coefficient patterns (all bases and lanes at once); with the bilinearity of
     both maps mod q (step 4 / Official's Montgomery arithmetic) and step 1's per-base/lane
     support this is equality mod q on the whole caller domain; plus random caller-domain
     inputs natively.

  prove_basemul_shoup.py --param N --experiment . --build build/shoup_proof --output out.json
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

import common  # noqa: E402
from common import BASE_A, CFG, aligned_poly, configure, sha  # noqa: E402
from avx2emu import Q, Val  # noqa: E402
import ledger  # noqa: E402
import prove_ht  # noqa: E402
import generate_basemul_shoup as G  # noqa: E402
from symexec_ext import FormsX  # noqa: E402


def fail(msg):
    raise SystemExit(f"SHOUP PROOF FAILURE: {msg}")


def support(F, fid, memo):
    """Set of input word indices a form depends on."""
    if fid in memo:
        return memo[fid]
    s = set()
    for a in F.forms[fid]:
        k = F.atoms[a]
        if k[0] == "IN":
            s.add(k[1])
        elif k[0] != "ONE":
            s |= support(F, k[1], memo) | support(F, k[2], memo)
    memo[fid] = frozenset(s)
    return memo[fid]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--param", type=int, choices=(768, 864, 1152), required=True)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--build", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--emit-env", type=Path, help="also write the proven envelopes as a C header (C test)")
    args = ap.parse_args()
    n = args.param
    d = G.PARAMS[n]["d"]
    configure(n, args.experiment, args.build)
    root, build, up = CFG["experiment"], CFG["build"], CFG["upstream"]
    fn = f"ntruplus{n}_officialopt_basemul_shoup"
    asm_path, c_path = root / f"asm/{fn}.s", root / f"src/{fn}.c"
    for rel, pin in G.PARAMS[n]["pins"].items():
        if sha(root / rel) != pin:
            fail(f"pinned input changed: {rel}")

    # 1. symbolic identity with the reference formula on the committed asm
    k, tab = G.zeta_table(n, root)
    if G.c_source(n, tab) != c_path.read_text():
        fail(f"{c_path} is not the generator's C source")
    asm = asm_path.read_text()
    sym, F = G.symbolic_check(n, asm, tab)
    ref = G.reference_forms(F, n, tab)
    memo = {}
    for w in range(n):
        base, lane = w // (16 * d), w % 16
        allowed = {base * 16 * d + 16 * i + lane for i in range(d)}
        allowed |= {n + x for x in allowed}
        if not support(F, ref[w], memo) <= allowed:
            fail(f"output word {w} depends on inputs outside its base/lane")
    print(f"[{n}] symbolic: {n} output words == reference formula; per-base/lane support; "
          f"stack slots {sym['stack_slot_offsets_from_entry_rsp']}")

    # 2. evaluator == machine
    so = build / "shoup_kernels.so"
    subprocess.run(["cc", "-O1", "-mavx2", "-shared", "-fPIC", "-I", str(up), "-o", str(so), str(up / "consts.c"),
                    str(up / "basemul.s"), str(asm_path)], check=True)
    L = ctypes.CDLL(str(so))
    rng = random.Random(0x5400 + n)
    for t in range(12):
        a = [rng.randint(-32768, 32767) for _ in range(n)]
        b = [rng.randint(-32768, 32767) if t % 2 else rng.randint(0, Q - 1) for _ in range(n)]
        ba, aa, pa = aligned_poly(n, a)
        bb, ab, pb = aligned_poly(n, b)
        br, ar, pr = aligned_poly(n, [0] * n)
        getattr(L, fn)(ctypes.c_void_p(pr), ctypes.c_void_p(pa), ctypes.c_void_p(pb))
        want = F.evaluate(ref, {**{w: a[w] for w in range(n)}, **{n + w: b[w] for w in range(n)}})
        if list(ar) != want:
            fail(f"symbolic evaluation != machine, trial {t}")
    print(f"[{n}] evaluator == machine on 12 random inputs")

    # caller envelopes from the HT Forward interval replay (prove_ht / ledger domains)
    ht_asm = root / f"asm/ntruplus{n}_officialopt_ntt_ht.s"
    doms = ledger.domains(n)
    _, r_hat = prove_ht.run(ht_asm, f"ntruplus{n}_officialopt_ntt_ht", [("rdi", BASE_A, doms["encap_r/m,reenc[-1,1]"])])
    _, f_hat = prove_ht.run(ht_asm, f"ntruplus{n}_officialopt_ntt_ht", [("rdi", BASE_A, doms["decap_msg[-2,2]"])])
    sub = [Val(0 - y.hi, Q - 1 - y.lo) for y in f_hat]
    callers = {"encap": ledger.rng(r_hat), "decap": ledger.rng(sub)}

    # 3./4. exhaustive term bounds + triangle
    tool = build / "shoup_bounds"
    subprocess.run(["cc", "-O2", "-o", str(tool), str(HERE.parent / "shoup_bounds.c")], check=True)
    zpairs = sorted({(z, c) for zz, zc in tab for z, c in zip(zz, zc)})
    report = {}
    for caller, (alo, ahi) in callers.items():
        cmds = f"B {alo} {ahi} {G.CU}\n"
        res = subprocess.run([str(tool)], input=cmds, capture_output=True, text=True, check=True).stdout.split()
        tmin, tmax, ov = int(res[1]), int(res[2]), int(res[3])
        if ov:
            fail(f"{caller}: data term outside int16")
        prods = G.products(d)
        srange = {kk: (len(w) * tmin, len(w) * tmax) for kk, (dr, w) in enumerate(prods) if w}
        zres = {}
        cmds = "".join(f"Z {srange[kk][0]} {srange[kk][1]} {z} {c}\n" for kk in srange for z, c in zpairs)
        out = subprocess.run([str(tool)], input=cmds, capture_output=True, text=True, check=True).stdout.split("\n")
        i = 0
        for kk in srange:
            lo_, hi_ = 1 << 30, -(1 << 30)
            for z, c in zpairs:
                _, mn, mx, zov = out[i].split()
                i += 1
                if int(zov):
                    fail(f"{caller}: zeta term outside int16")
                lo_, hi_ = min(lo_, int(mn)), max(hi_, int(mx))
            zres[kk] = (lo_, hi_)
        outs = []
        for kk, (dr, w) in enumerate(prods):
            lo_ = len(dr) * tmin + (zres[kk][0] if w else 0)
            hi_ = len(dr) * tmax + (zres[kk][1] if w else 0)
            outs.append([lo_, hi_])
        allr = [min(o[0] for o in outs), max(o[1] for o in outs)]
        for kk, (slo, shi) in srange.items():
            if slo < -32768 or shi > 32767:
                fail(f"{caller}: s{kk} outside int16")
        if allr[0] < -32768 or allr[1] > 32767:
            fail(f"{caller}: output outside int16 {allr}")
        report[caller] = {"a_envelope": [alo, ahi], "b": [0, Q - 1], "data_term": [tmin, tmax],
                          "s_ranges": {f"s{kk}": list(v) for kk, v in srange.items()},
                          "zeta_term_ranges": {f"s{kk}": list(v) for kk, v in zres.items()},
                          "output_ranges": {f"c{kk}": o for kk, o in enumerate(outs)}, "output_range": allr}
        print(f"[{n}] {caller}: a {[alo, ahi]}, |term| in [{tmin}, {tmax}], output {allr}")
    m_rng = ledger.rng(r_hat)
    add = [report["encap"]["output_range"][0] + m_rng[0], report["encap"]["output_range"][1] + m_rng[1]]
    if add[0] < -32768 or add[1] > 32767:
        fail(f"encap poly_add(c, m_hat) {add} outside int16")
    tob = ledger.tobytes_accept()
    if not tob["canonical_for_all_int16"]:
        fail("tobytes not canonical on all int16")
    print(f"[{n}] encap poly_add(c, m_hat) in {add}; tobytes canonical on all int16")

    # 5. mod q vs Official poly_basemul: basis patterns + random caller inputs
    mism = 0
    for i in range(d):
        for j in range(d):
            a = [1 if (w // 16) % d == i else 0 for w in range(n)]
            b = [1 if (w // 16) % d == j else 0 for w in range(n)]
            ba, aa, pa = aligned_poly(n, a)
            bb, ab, pb = aligned_poly(n, b)
            b1, a1, p1 = aligned_poly(n, [0] * n)
            b2, a2, p2 = aligned_poly(n, [0] * n)
            getattr(L, fn)(ctypes.c_void_p(p1), ctypes.c_void_p(pa), ctypes.c_void_p(pb))
            L.poly_basemul(ctypes.c_void_p(p2), ctypes.c_void_p(pa), ctypes.c_void_p(pb))
            mism += sum((x - y) % Q != 0 for x, y in zip(a1, a2))
    rnd = 0
    for t in range(4000):
        env = r_hat if t % 2 == 0 else sub
        a = [rng.randint(v.lo, v.hi) for v in env]
        b = [rng.randint(0, Q - 1) for _ in range(n)]
        ba, aa, pa = aligned_poly(n, a)
        bb, ab, pb = aligned_poly(n, b)
        b1, a1, p1 = aligned_poly(n, [0] * n)
        b2, a2, p2 = aligned_poly(n, [0] * n)
        getattr(L, fn)(ctypes.c_void_p(p1), ctypes.c_void_p(pa), ctypes.c_void_p(pb))
        L.poly_basemul(ctypes.c_void_p(p2), ctypes.c_void_p(pa), ctypes.c_void_p(pb))
        rnd += sum((x - y) % Q != 0 for x, y in zip(a1, a2))
    if mism or rnd:
        fail(f"Shoup != Official poly_basemul mod q: basis {mism}, random {rnd}")
    print(f"[{n}] mod q: {d * d} basis patterns and 4000 random caller-domain inputs == Official poly_basemul")

    summary = {
        "class": "Shoup BaseMul proof: symbolic + exhaustive per-term + triangle + mod-q basis (Phase A; no timing)",
        "parameter": f"NTRU+{n}", "verdict": "pass",
        "asm": str(asm_path.relative_to(root)), "asm_sha256": sha(asm_path),
        "c_source": str(c_path.relative_to(root)), "c_source_sha256": sha(c_path),
        "sources_sha256": {f: sha(up / f) for f in ("consts.c", "basemul.s", "ntt.s")},
        "ht_forward_sha256": sha(ht_asm),
        "tool_sha256": {p.name: sha(p) for p in [*sorted(LAZY_RP.glob("*.py")), LAZY_RP / "images.c",
                                                 HT_RP / "prove_ht.py", HERE, HERE.parent / "shoup_bounds.c",
                                                 HERE.parent / "generate_basemul_shoup.py",
                                                 HERE.parent / "symexec_ext.py"]},
        "symbolic": {k: v for k, v in sym.items() if k != "dynamic_census"},
        "per_base_lane_support": True,
        "companion_constant": G.CU, "zeta_pairs": len(zpairs),
        "callers": report,
        "encap_poly_add_c_m_hat": add, "tobytes": tob,
        "mod_q_basis_patterns": d * d, "mod_q_random_caller_inputs": 4000,
        "conclusion": f"{fn}(a, b) is the exact int16 a*b (mod q, canonical scale) per base for every a in the "
                      "Encap/Decap caller envelopes and canonical b, == Official poly_basemul (mod q)",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=1) + "\n")
    if args.emit_env:
        e, dd = report["encap"], report["decap"]
        args.emit_env.write_text(
            "/* GENERATED by prove_basemul_shoup.py --emit-env: proven Shoup caller envelopes. */\n"
            f"#define SHOUP_ENCAP_A_LO {e['a_envelope'][0]}\n#define SHOUP_ENCAP_A_HI {e['a_envelope'][1]}\n"
            f"#define SHOUP_DECAP_A_LO {dd['a_envelope'][0]}\n#define SHOUP_DECAP_A_HI {dd['a_envelope'][1]}\n"
            f"#define SHOUP_ENCAP_OUT_LO {e['output_range'][0]}\n#define SHOUP_ENCAP_OUT_HI {e['output_range'][1]}\n"
            f"#define SHOUP_DECAP_OUT_LO {dd['output_range'][0]}\n#define SHOUP_DECAP_OUT_HI {dd['output_range'][1]}\n")
    print(f"[{n}] Shoup proof PASS -> {args.output}")


if __name__ == "__main__":
    main()
