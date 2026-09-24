#!/usr/bin/env python3
"""Range / consumer proof for the NTRU+768 HT Forward and the keygen R^2 fold.

Re-uses the lazy-Forward range-proof tools (common/official_opt_lazy/range_proof,
read only, unchanged) through a thin emulator extension (EmuHT) that adds the
two instruction forms the HT asm uses and the old tool does not know
(vpunpck{l,h}wd, vpunpck{l,h}dq) plus the asm-local RIP tables (.short data).
Steps, all fatal on failure:
  1. emulator (concrete/wrap mode) == machine on the real assembled HT Forward
     and the no-R^2 BaseMul (random full-int16 inputs);
  2. per-lane interval replay of the lazy and the HT Forward on every caller
     domain: zero signed-word failures, lane-by-lane identical intervals, HT
     output range == the proven lazy bound (EXPECTED_LAZY[768]);
  3. consumer envelopes on the HT outputs (identical to the lazy ones);
  5. HT inverse (optional item): interval replay of Official poly_invntt_scale
     and of the HT inverse on the Decap domain (poly_basemul_scale of the
     canonical c and f from poly_frombytes): zero failures and
     lane-by-lane identical intervals (the output feeds crepmod3, which is
     total on int16);
  4. keygen R^2 fold: interval replay of ntruplus768_officialopt_basemul_nor2
     on (keygen f_hat/g_hat, BaseInv output envelope), zero failures; the
     BaseInv output envelope is the ledger's any-fqmul-output envelope, which
     the fold (a constant change inside a fqmul chain) does not affect;
     poly_tobytes canonical on all int16.
"""
import argparse
import ctypes
import json
import random
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAZY_RP = HERE.parents[1] / "official_opt_lazy/range_proof"
sys.path.insert(0, str(LAZY_RP))
sys.path.insert(0, str(HERE.parent / "tools"))

import avx2emu  # noqa: E402
import common  # noqa: E402
from common import BASE_A, BASE_B, BASE_C, CFG, aligned_poly, configure, load_consts, sha  # noqa: E402
from avx2emu import Q  # noqa: E402
import ledger  # noqa: E402
from prove_forward_lazy import EXPECTED_LAZY, EXPECTED_CONSUMERS  # noqa: E402
from symexec import parse_asm  # noqa: E402

HT = "ntruplus768_officialopt_ntt_ht"
NOR2 = "ntruplus768_officialopt_basemul_nor2"
HTINV = "ntruplus768_officialopt_invntt_ht"


class EmuHT(avx2emu.Emu):
    """avx2emu.Emu + word/dword unpacks + asm-local .short tables."""

    def __init__(self, path, *a, **kw):
        super().__init__(path, *a, **kw)
        base = 0x900000
        for name, words in parse_asm(Path(path).read_text())[2].items():
            self.syms[name] = base
            for i, v in enumerate(words):
                self.mem[base + 2 * i] = avx2emu.Val(v, v, True)
            base += 0x10000

    def vec(self, op, ops, ln):
        if op in ("vpunpcklwd", "vpunpckhwd", "vpunpckldq", "vpunpckhdq"):
            s2, s1 = self.src(ops[0]), self.src(ops[1])   # AT&T: b, a -> a interleave b
            w = 1 if op.endswith("wd") else 2
            base = 4 if op[7] == "h" else 0
            out = []
            for h in (0, 8):
                for i in range(0, 4, w):
                    out += s1[h + base + i:h + base + i + w] + s2[h + base + i:h + base + i + w]
            self.ymm[int(ops[-1][4:])] = out
            return
        super().vec(op, ops, ln)


def emu_file(path, **kw):
    z, zi, rip = load_consts()
    return EmuHT(str(path), z, zi, rip, **kw)


def run(path, entry, inputs, out=(BASE_A, None), **kw):
    e = emu_file(path, **kw)
    regs = {}
    for reg, base, lanes in inputs:
        e.set_poly(base, lanes)
        regs[reg] = base
    e.run(entry, regs)
    return e, e.get_poly(out[0], out[1] or CFG["n"])


def machine_lib(ht_asm, nor2_asm, inv_asm, build):
    out = build / "ht_kernels.so"
    up = CFG["upstream"]
    subprocess.run(["cc", "-O1", "-mavx2", "-shared", "-fPIC", "-I", str(up), "-o", str(out),
                    str(up / "consts.c"), str(ht_asm), str(nor2_asm), str(inv_asm)], check=True)
    return ctypes.CDLL(str(out))


def fail(msg):
    raise SystemExit(f"HT RANGE PROOF FAILURE: {msg}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--build", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--diff-trials", type=int, default=24)
    args = ap.parse_args()
    n = 768
    configure(n, args.experiment, args.build)
    exp = CFG["experiment"]
    ht_asm, nor2_asm, inv_asm = exp / f"asm/{HT}.s", exp / f"asm/{NOR2}.s", exp / f"asm/{HTINV}.s"
    V = avx2emu.Val

    # 1. emulator == machine (wrap mode)
    L = machine_lib(ht_asm, nor2_asm, inv_asm, CFG["build"])
    rng = random.Random(0x768)
    calls = {HT: 0, NOR2: 0, HTINV: 0}
    for t in range(args.diff_trials):
        x = [rng.randint(-32768, 32767) if t % 2 else rng.randint(-3, 4) for _ in range(n)]
        b, arr, addr = aligned_poly(n, x)
        getattr(L, HT)(ctypes.c_void_p(addr))
        _, got = run(ht_asm, HT, [("rdi", BASE_A, [V(v, v) for v in x])], wrap_mode=True)
        if list(arr) != [v.lo for v in got]:
            fail(f"emulator != machine on {HT} trial {t}")
        calls[HT] += 1
        a1 = [rng.randint(-32768, 32767) for _ in range(n)]
        a2 = [rng.randint(-32768, 32767) for _ in range(n)]
        ba, aa, pa = aligned_poly(n, a1)
        bb, ab, pb = aligned_poly(n, a2)
        br, ar, pr = aligned_poly(n, [0] * n)
        getattr(L, NOR2)(ctypes.c_void_p(pr), ctypes.c_void_p(pa), ctypes.c_void_p(pb))
        _, got = run(nor2_asm, NOR2, [("rdi", BASE_A, [V(0, 0)] * n), ("rsi", BASE_B, [V(v, v) for v in a1]),
                                      ("rdx", BASE_C, [V(v, v) for v in a2])], wrap_mode=True)
        if list(ar) != [v.lo for v in got]:
            fail(f"emulator != machine on {NOR2} trial {t}")
        calls[NOR2] += 1
        b, arr, addr = aligned_poly(n, a1)
        getattr(L, HTINV)(ctypes.c_void_p(addr))
        _, got = run(inv_asm, HTINV, [("rdi", BASE_A, [V(v, v) for v in a1])], wrap_mode=True)
        if list(arr) != [v.lo for v in got]:
            fail(f"emulator != machine on {HTINV} trial {t}")
        calls[HTINV] += 1
    print(f"[768] emulator == machine: {calls}")

    # 2. interval replay, lazy vs HT, every caller domain
    fwd, outs_h = {}, {}
    for dom, lanes in ledger.domains(n).items():
        el, ol = ledger.run("LAZY", CFG["lazy_name"], [("rdi", BASE_A, lanes)])
        eh, oh = run(ht_asm, HT, [("rdi", BASE_A, lanes)])
        same = all(a.lo == b.lo and a.hi == b.hi for a, b in zip(ol, oh))
        barrett = sum(1 for k, v in eh.stats.items() if isinstance(k, int) and v[2] == "barrett_in")
        r = {"lazy": {"failures": len(el.failures), "output_range": ledger.rng(ol)},
             "ht": {"failures": len(eh.failures), "output_range": ledger.rng(oh),
                    "barrett_lines_executed": barrett},
             "ht_equals_lazy_per_lane_interval": same}
        if r["ht"]["failures"] or r["lazy"]["failures"]:
            fail(f"signed-word failure in {dom}")
        if not same:
            fail(f"HT interval replay differs from lazy in {dom}")
        if barrett:
            fail("HT executes a Barrett")
        if r["ht"]["output_range"] != EXPECTED_LAZY[n][dom]:
            fail(f"HT bound drift in {dom}: {r['ht']['output_range']}")
        if dom == "asm_contract[-3,4]":
            r["ht_levels"] = ledger.level_summary(eh)
            r["ht_census"] = ledger.opcode_census(eh)
        fwd[dom] = r
        outs_h[dom] = oh
        print(f"[768] {dom:24s} lazy={r['lazy']['output_range']} ht={r['ht']['output_range']} per-lane equal")

    # 3. consumers on the HT outputs (Official BaseMul / BaseInv / add / sub)
    cons = ledger.consumers(outs_h)
    if not ledger.consumers_ok(cons):
        fail("consumer envelope failure")
    for k, v in EXPECTED_CONSUMERS[n].items():
        if cons[k]["range"] != v:
            fail(f"consumer drift {k}: {cons[k]['range']}")

    # 4. keygen R^2 fold: core-only BaseMul on (f_hat/g_hat, BaseInv envelope)
    fold = {}
    for name, a_dom, inv_dom in (("keygen nor2(h, g_hat, finv)", "keygen_g", "keygen_f"),
                                 ("keygen nor2(h, f_hat, ginv)", "keygen_f", "keygen_g")):
        bi, inv = ledger.baseinv_chain(outs_h[inv_dom])
        e, out = run(nor2_asm, NOR2, [("rdi", BASE_A, [V(0, 0)] * n), ("rsi", BASE_B, outs_h[a_dom]),
                                      ("rdx", BASE_C, inv)])
        off, _ = ledger.basemul(outs_h[a_dom], inv)
        fold[name] = {"failures": len(e.failures), "output_range": ledger.rng(out),
                      "baseinv_output_envelope": bi["finv_absmax_env"],
                      "official_basemul_same_inputs": off}
        if e.failures or off["failures"]:
            fail(f"{name}: signed-word failure")
        if max(abs(v) for v in fold[name]["output_range"]) > 32767:
            fail(f"{name}: output outside int16")
        print(f"[768] {name}: output {fold[name]['output_range']} (Official BaseMul "
              f"{off['output_range']}), BaseInv envelope |x| <= {bi['finv_absmax_env']}")
    # 5. HT inverse on the Decap domain
    canon = [V(0, Q - 1)] * n
    _, m_in = ledger.basemul(canon, canon, entry="poly_basemul_scale")   # kem.c: c, f from frombytes
    eo, oo = run(CFG["upstream"] / "invntt.s", "poly_invntt_scale", [("rdi", BASE_A, m_in)])
    ei, oi = run(inv_asm, HTINV, [("rdi", BASE_A, m_in)])
    same = all(a.lo == b.lo and a.hi == b.hi for a, b in zip(oo, oi))
    inverse = {"input": "poly_basemul_scale(c, f), c and f from poly_frombytes: [0,q-1] (kem.c Decap)",
               "input_range": ledger.rng(m_in),
               "official": {"failures": len(eo.failures), "output_range": ledger.rng(oo)},
               "ht": {"failures": len(ei.failures), "output_range": ledger.rng(oi)},
               "ht_equals_official_per_lane_interval": same,
               "consumer": "poly_crepmod3 (output in [-2,2] for every int16 input)"}
    if eo.failures or ei.failures or not same:
        fail(f"HT inverse replay {inverse}")
    print(f"[768] invntt decap domain: input {inverse['input_range']} official={inverse['official']['output_range']} "
          f"ht={inverse['ht']['output_range']} per-lane equal")
    tob = ledger.tobytes_accept()
    if not tob["canonical_for_all_int16"]:
        fail("tobytes not canonical on all int16")

    summary = {
        "class": "per-lane interval range proof + consumer envelopes (Phase A; no timing)",
        "parameter": "NTRU+768", "verdict": "pass",
        "ht_asm_sha256": sha(ht_asm), "nor2_asm_sha256": sha(nor2_asm),
        "lazy_asm_sha256": sha(CFG["lazy_asm"]),
        "sources_sha256": {f: sha(CFG["upstream"] / f) for f in ("ntt.s", "basemul.s", "baseinv.s",
                                                                  "consts.c", "pack.s")},
        "tool_sha256": {p.name: sha(p) for p in sorted(LAZY_RP.glob("*.py")) + [LAZY_RP / "images.c",
                                                                               Path(__file__).resolve()]},
        "emulator_machine_differential_calls": calls,
        "forward": {d: {k: v for k, v in r.items() if k not in ("ht_levels", "ht_census")}
                    for d, r in fwd.items()},
        "forward_levels_asm_contract_ht": fwd["asm_contract[-3,4]"]["ht_levels"],
        "forward_census_asm_contract_ht": fwd["asm_contract[-3,4]"]["ht_census"],
        "consumers_ht": cons,
        "keygen_r2fold": fold,
        "inverse_ht": inverse,
        "crepmod3": ledger.crepmod3_accept(),
        "htinv_asm_sha256": sha(inv_asm),
        "tobytes": tob,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=1, default=str) + "\n")
    print(f"[768] HT/R2-fold range proof PASS -> {args.output}")


if __name__ == "__main__":
    main()
