#!/usr/bin/env python3
"""Range/consumer proof for the generated caller-lazy Forward (NTRU+768/864/1152).

Driver for the ported Phase-0 reduction audit tools (avx2emu.py, difftest.py,
ledger.py).  Steps, all fatal on failure:
  1. build images.c and the real kernels (Official + generated lazy ASM);
  2. cross-check the C exact-image helpers against the Python reference;
  3. emulator-vs-machine differential on poly_ntt, the lazy entry,
     poly_basemul and poly_baseinv_1;
  4. per-lane interval replay of Official and of the generated lazy ASM on
     every caller domain; lazy must equal the Official replay with the terminal
     Barrett skipped, lane by lane, with zero signed-word failures;
  5. consumer envelopes (BaseInv incl. exact zero check, BaseMul, poly_add,
     poly_sub, tobytes) on the lazy outputs, crepmod3 output domain;
  6. compare against the bounds proven by the Phase-0 audit (drift = failure)
     and write a curated summary JSON.
"""
import argparse
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import common  # noqa: E402
from common import configure, sha, src  # noqa: E402
import avx2emu  # noqa: E402
import difftest  # noqa: E402
import ledger  # noqa: E402

# Bounds proven by the Phase-0 read-only audit (identical for 864 and 1152
# except the poly_add envelope, which depends on the BaseMul output range).
EXPECTED_LAZY_864_1152 = {
    "asm_contract[-3,4]": [-17961, 17957],
    "keygen_f": [-17193, 17194],
    "keygen_g": [-17193, 17193],
    "decap_msg[-2,2]": [-16382, 16385],
    "encap_r/m,reenc[-1,1]": [-15580, 15580],
}
# NTRU+768 (different zetas, one level fewer): the keygen/encap/decap maxima
# equal the independent NTRU+768 avx2_official_opt_001 round-4 lane proof
# (pre_barrett_max_abs 15252 / 15251 / 13636 / 14449, ciphertext_minus_message
# 17905); the asm_contract[-3,4] envelope is this tool's own result.
EXPECTED_LAZY = {
    768: {
        "asm_contract[-3,4]": [-16058, 16035],
        "keygen_f": [-15251, 15252],
        "keygen_g": [-15251, 15251],
        "decap_msg[-2,2]": [-14449, 14449],
        "encap_r/m,reenc[-1,1]": [-13636, 13636],
    },
    864: EXPECTED_LAZY_864_1152,
    1152: EXPECTED_LAZY_864_1152,
}
EXPECTED_CONSUMERS = {
    768: {"encap poly_add(c,m_hat)": [-15483, 15483], "decap poly_sub(c,f_hat)": [-14449, 17905]},
    864: {"encap poly_add(c,m_hat)": [-17404, 17404], "decap poly_sub(c,f_hat)": [-16385, 19838]},
    1152: {"encap poly_add(c,m_hat)": [-17436, 17436], "decap poly_sub(c,f_hat)": [-16385, 19838]},
}


def fail(msg):
    raise SystemExit(f"RANGE PROOF FAILURE: {msg}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--param", type=int, choices=(768, 864, 1152), required=True)
    ap.add_argument("--experiment", type=Path, required=True)
    ap.add_argument("--build", type=Path, required=True)
    ap.add_argument("--output", type=Path, required=True)
    ap.add_argument("--diff-trials", type=int, default=32)
    args = ap.parse_args()
    n = args.param
    configure(n, args.experiment, args.build)

    rnd = random.Random(0x1A2)
    for _ in range(40):
        lo = rnd.randint(-32768, 32000)
        hi = min(32767, lo + rnd.randint(0, 600))
        c = rnd.choice([-1665, -33, 1, 17, 1729, 3000, -3456])
        if avx2emu.mont_const_image(lo, hi, c) != avx2emu.mont_const_image_py(lo, hi, c):
            fail("C/Python Montgomery image mismatch")
        if avx2emu.barrett_image(lo, hi) != avx2emu.barrett_image_py(lo, hi):
            fail("C/Python Barrett image mismatch")

    diff = difftest.check(args.diff_trials, seed=n)
    print(f"[{n}] emulator == machine: {diff}")

    fwd, outs_o, outs_l, blines = ledger.forward()
    for dom, r in fwd.items():
        if r["official"]["failures"] or r["lazy_generated_asm"]["failures"]:
            fail(f"signed-word failure in {dom}")
        if not r["lazy_equals_official_with_terminal_barrett_skipped_per_lane"]:
            fail(f"generated lazy ASM replay differs from skip-replay in {dom}")
        if r["lazy_generated_asm"]["barrett_lines_executed"]:
            fail(f"generated lazy ASM still executes Barrett in {dom}")
        if r["lazy_generated_asm"]["output_range"] != EXPECTED_LAZY[n][dom]:
            fail(f"lazy bound drift in {dom}: {r['lazy_generated_asm']['output_range']}")
        print(f"[{n}] {dom:24s} official={r['official']['output_range']} "
              f"lazy={r['lazy_generated_asm']['output_range']}")
    cons_l = ledger.consumers(outs_l)
    cons_o = ledger.consumers(outs_o)
    if not ledger.consumers_ok(cons_l) or not ledger.consumers_ok(cons_o):
        fail("consumer envelope failure")
    for k, v in EXPECTED_CONSUMERS[n].items():
        if cons_l[k]["range"] != v:
            fail(f"consumer drift {k}: {cons_l[k]['range']}")
    for k, v in cons_l.items():
        print(f"[{n}] lazy consumer {k:40s} {v}")
    crep = ledger.crepmod3_accept()
    if crep["output_values_all_words"] != [-2, 2]:
        fail("crepmod3 output domain is not [-2,2]")
    tob = ledger.tobytes_accept()
    if not tob["canonical_for_all_int16"]:
        fail("tobytes not canonical on all int16")

    here = Path(__file__).resolve().parent
    contract = fwd["asm_contract[-3,4]"]
    summary = {
        "class": "per-lane interval range proof + consumer envelopes (Phase A; no timing)",
        "parameter": f"NTRU+{n}",
        "verdict": "pass",
        "sources_sha256": {f: sha(src(f)) for f in ("ntt.s", "basemul.s", "baseinv.s",
                                                     "consts.c", "crepmod3.s", "pack.s")},
        "lazy_asm": str(common.CFG["lazy_asm"].relative_to(common.CFG["experiment"])),
        "lazy_asm_sha256": sha(common.CFG["lazy_asm"]),
        "tool_sha256": {p.name: sha(p) for p in sorted(here.glob("*.py")) + [here / "images.c"]},
        "emulator_machine_differential_calls": diff,
        "official_terminal_barrett_vpsubw_lines": blines,
        "forward": {dom: {k: v for k, v in r.items() if not k.endswith(("levels", "census"))}
                    for dom, r in fwd.items()},
        "forward_levels_asm_contract": {
            "official": contract["official_levels"], "lazy": contract["lazy_levels"]},
        "forward_census_asm_contract": {
            "official": contract["official_census"], "lazy": contract["lazy_census"]},
        "lazy_output_envelope": [min(v[0] for v in EXPECTED_LAZY[n].values()),
                                 max(v[1] for v in EXPECTED_LAZY[n].values())],
        "consumers_lazy": cons_l,
        "consumers_official": cons_o,
        "crepmod3": crep,
        "tobytes": tob,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=1, default=str) + "\n")
    print(f"[{n}] range proof PASS -> {args.output}")


if __name__ == "__main__":
    main()
