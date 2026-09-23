"""Per-lane interval ledger: Official vs generated lazy Forward, and consumers.

Ported from the Phase-0 audit (ledger.py), restricted to the Forward
candidate: the inverse-NTT sections of the original audit are not part of
this candidate and were dropped.  Differences from the original:
  * the lazy Forward is replayed from the *generated* candidate ASM itself
    (asm/ntruplus{N}_officialopt_ntt_caller_lazy.s), and is additionally
    required to match, lane by lane, the Official replay with the terminal
    Barrett lines skipped (the method used by the original audit);
  * sources come from the experiment's imported upstream copy.
All bounds are interval replays of the .s files (avx2emu.py, validated by
difftest.py).  Montgomery-by-constant and Barrett images are exact per lane
interval; data*data Montgomery (basemul/baseinv) uses the sound envelope.
"""
from collections import OrderedDict, defaultdict

from common import CFG, BASE_A, BASE_B, BASE_C, BASE_D, emu
from avx2emu import Val, Q

WORD = 32768 * Q          # |a*b| < 32768*q  => Montgomery of a multiple of q is exactly 0
T_MAX = (32768 * 32768 + 32768 * Q) // 65536   # 18112: any fqmul output of int16 inputs


def mont_env(A, B):
    return (A * B + 32768 * Q) // 65536


def domains(n):
    return OrderedDict([
        ("asm_contract[-3,4]", [Val(-3, 4)] * n),          # ntt.s:9-10 comment
        ("keygen_f", [Val(-2, 4)] + [Val(-3, 3)] * (n - 1)),  # kem.c:68-72
        ("keygen_g", [Val(-3, 3)] * n),                      # kem.c:97-100
        ("decap_msg[-2,2]", [Val(-2, 2)] * n),               # kem.c:317-322 (crepmod3 all-word output)
        ("encap_r/m,reenc[-1,1]", [Val(-1, 1)] * n),         # kem.c:226-232, 335-336
    ])


def run(fname, entry, inputs, skip=(), out=(BASE_A, None)):
    e = emu(fname, skip_barrett_lines=skip)
    regs = {}
    for reg, base, lanes in inputs:
        e.set_poly(base, lanes)
        regs[reg] = base
    e.run(entry, regs)
    ob, olen = out
    return e, e.get_poly(ob, olen or CFG["n"])


def absmax(lanes):
    return max(max(abs(v.lo), abs(v.hi)) for v in lanes)


def rng(lanes):
    return [min(v.lo for v in lanes), max(v.hi for v in lanes)]


def level_summary(e):
    lv = OrderedDict()
    for ln in sorted(k for k in e.stats if isinstance(k, int)):
        lo, hi, kind = e.stats[ln]
        level, sub = e.section[ln]
        d = lv.setdefault(level, {"addsub_absmax": 0, "mont_out": None, "mont_vec": 0,
                                  "barrett_in": None, "barrett_out": None, "barrett_vec": 0,
                                  "raw_product": None})
        cnt = e.counts.get(ln, 0)
        m = max(abs(lo), abs(hi))
        if kind in ("add", "sub", "shl1"):
            d["addsub_absmax"] = max(d["addsub_absmax"], m)
        elif kind.startswith("mont"):
            d["mont_out"] = max(d["mont_out"] or 0, m)
            d["mont_vec"] += cnt
        elif kind in ("barrett_in", "barrett_skipped"):
            d["barrett_in"] = max(d["barrett_in"] or 0, m)
            if kind == "barrett_in":
                d["barrett_vec"] += cnt
                bo = e.stats[("bout", ln)]
                d["barrett_out"] = max(d["barrett_out"] or 0, abs(bo[0]), abs(bo[1]))
        elif kind == "raw_product":
            d["raw_product"] = max(d["raw_product"] or 0, m)
    for level, (lo, hi) in e.entering.items():
        if level in lv:
            lv[level]["entering_absmax"] = max(abs(lo), abs(hi))
    return lv


def opcode_census(e):
    census = OrderedDict()
    for ln, op, ops in e.prog:
        if not op.startswith("vp") or op.startswith("vpbroadcast"):
            continue
        c = census.setdefault(e.section[ln][0], defaultdict(int))
        c[op] += e.counts.get(ln, 0)
    return {k: dict(sorted(v.items())) for k, v in census.items()}


def crepmod3_accept():
    """crepmod3.s arithmetic on every int16 (864 and 1152 share the body)."""
    qp, qm, v2 = (Q + 1) // 2, (Q - 1) // 2, (32768 + 1) // 3

    def w(x):
        return ((x + 32768) & 0xFFFF) - 32768

    def f(x):
        t = w(x + (Q if x < 0 else 0))
        t = w(t - qp)
        t = w(t + (Q if t < 0 else 0))
        t = w(t - qm)
        return w(t - 3 * ((t * v2 + (1 << 14)) >> 15))

    outs = sorted({f(x) for x in range(-32768, 32768)})
    return {"output_values_all_words": [outs[0], outs[-1]]}


def tobytes_accept():
    """poly_tobytes Barrett + sign-fix (864: pack.s poly_ntt_pack; 1152: pack.s
    poly_tobytes) must be canonical for all int16.  The C differential test
    re-checks this exhaustively on the real linked code."""
    for x in range(-32768, 32768):
        v = x - Q * ((x * 9 + (1 << 14)) >> 15)
        assert -32768 <= v <= 32767
        c = v + (Q if v < 0 else 0)
        if not (0 <= c < Q and c == x % Q):
            return {"canonical_for_all_int16": False, "first_fail": x}
    return {"canonical_for_all_int16": True}


def forward():
    n = CFG["n"]
    e0 = emu("ntt.s")
    blines = [ln for ln, op, ops in e0.prog if op == "vpsubw" and e0.section[ln][1] == "reduce2"]
    res = OrderedDict()
    outs_o, outs_l = {}, {}
    for name, lanes in domains(n).items():
        eo, oo = run("ntt.s", "poly_ntt", [("rdi", BASE_A, lanes)])
        el, ol = run("LAZY", CFG["lazy_name"], [("rdi", BASE_A, lanes)])
        es, os_ = run("ntt.s", "poly_ntt", [("rdi", BASE_A, lanes)], skip=blines)
        same = all(a.lo == b.lo and a.hi == b.hi for a, b in zip(ol, os_))
        lazy_barrett = sum(1 for k, v in el.stats.items()
                           if isinstance(k, int) and v[2] == "barrett_in")
        res[name] = {
            "official": {"failures": len(eo.failures), "output_range": rng(oo)},
            "lazy_generated_asm": {"failures": len(el.failures), "output_range": rng(ol),
                                   "barrett_lines_executed": lazy_barrett},
            "lazy_equals_official_with_terminal_barrett_skipped_per_lane": same,
        }
        if name == "asm_contract[-3,4]":
            res[name]["official_levels"] = level_summary(eo)
            res[name]["lazy_levels"] = level_summary(el)
            res[name]["official_census"] = opcode_census(eo)
            res[name]["lazy_census"] = opcode_census(el)
        outs_o[name], outs_l[name] = oo, ol
    return res, outs_o, outs_l, blines


def baseinv_chain(a_lanes):
    n = CFG["n"]
    e, r = run("baseinv.s", "poly_baseinv_1",
               [("rdi", BASE_A, [Val(0, 0)] * n), ("rsi", BASE_D, [Val(0, 0)] * 288),
                ("rdx", BASE_C, a_lanes)])
    den = e.get_poly(BASE_D, 288)
    D = absmax(den)
    pc1 = mont_env(D, D)
    zero_exact = pc1 * D < WORD and D * D < WORD
    finv = [Val(-mont_env(max(abs(v.lo), abs(v.hi)), T_MAX),
                mont_env(max(abs(v.lo), abs(v.hi)), T_MAX)) for v in r]
    return {"failures": len(e.failures), "numerator_absmax": absmax(r), "den_absmax": D,
            "pc1_absmax_env": pc1, "zero_check_exact": zero_exact,
            "zero_margin": f"pc1*D={pc1 * D}, D^2={D * D} vs 32768q={WORD}",
            "finv_absmax_env": absmax(finv)}, finv


def basemul(a, b, entry="poly_basemul"):
    n = CFG["n"]
    e, out = run("basemul.s", entry,
                 [("rdi", BASE_A, [Val(0, 0)] * n), ("rsi", BASE_B, a), ("rdx", BASE_C, b)])
    return {"failures": len(e.failures), "fail_lines": sorted({f[0] for f in e.failures}),
            "output_range": rng(out)}, out


def consumers(outs):
    n = CFG["n"]
    canon = [Val(0, Q - 1)] * n
    rep = OrderedDict()
    f_hat, g_hat = outs["keygen_f"], outs["keygen_g"]
    bi_f, finv = baseinv_chain(f_hat)
    bi_g, ginv = baseinv_chain(g_hat)
    rep["keygen baseinv(f_hat)"] = bi_f
    rep["keygen baseinv(g_hat)"] = bi_g
    rep["keygen basemul(h,g_hat,finv)"] = basemul(g_hat, finv)[0]
    rep["keygen basemul(h,f_hat,ginv)"] = basemul(f_hat, ginv)[0]
    rep["keygen tobytes(sk,f_hat)"] = {"input_range": rng(f_hat), "ok": absmax(f_hat) <= 32767}
    r_hat = outs["encap_r/m,reenc[-1,1]"]
    bm, c = basemul(canon, r_hat)
    add = [Val(x.lo + y.lo, x.hi + y.hi) for x, y in zip(c, r_hat)]   # m_hat same domain as r_hat
    rep["encap basemul(c,h,r_hat)"] = bm
    rep["encap poly_add(c,m_hat)"] = {"range": rng(add), "ok": absmax(add) <= 32767}
    rep["encap tobytes(ct,r_hat) / reenc tobytes"] = {"input_range": rng(r_hat),
                                                       "ok": absmax(r_hat) <= 32767}
    m_hat = outs["decap_msg[-2,2]"]
    sub = [Val(0 - y.hi, Q - 1 - y.lo) for y in m_hat]       # c from poly_frombytes: [0,q-1]
    rep["decap poly_sub(c,f_hat)"] = {"range": rng(sub), "ok": absmax(sub) <= 32767}
    rep["decap basemul(f,c-f_hat,hinv)"] = basemul(sub, canon)[0]
    return rep


def consumers_ok(rep):
    for k, v in rep.items():
        if v.get("failures", 0) or v.get("ok") is False or v.get("zero_check_exact") is False:
            return False
    return True
