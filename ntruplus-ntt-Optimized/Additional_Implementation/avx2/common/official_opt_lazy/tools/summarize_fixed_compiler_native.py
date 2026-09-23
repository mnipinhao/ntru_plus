#!/usr/bin/env python3
"""Summarise the Phase-B follow-up fixed-compiler Native runs for one parameter.

Each run restricts SUPERCOP's compiler list (bench/<host>/bin/okc-amd64) to a
single entry via run_supercop_benchmark.py --compiler-wrapper
(common/official_opt_lazy/compilers/okc-native-gcc-<CC>-only.sh), with the
unmodified crypto_kem/measure.c and 9 fresh launches per implementation.

For every compiler tag it reports pooled StQ1/2/3 per role, candidate-official
deltas, per-launch StQ2 values, launch-level favourable counts (candidate
launches below the Official launch median, and the 9x9 pairwise count of
candidate launch < Official launch), then applies the Phase-B decision rule
using the committed fixed-ELF paired summary: robust research win iff the
pooled Native delta < 0 AND all four paired 95% CIs are below zero.

This is a controlled-compiler Native, not SUPERCOP's default selection.
Writes results/native-fixedcc-summary-<tag>.json.
"""

import argparse
import json
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve()
REPO = next(p for p in HERE.parents if (p / "bench/supercop.lock").is_file())
sys.path.insert(0, str(REPO / "scripts"))
from run_supercop_benchmark import decode_observations, stabilized_quartiles  # noqa: E402

OPS = ("keypair_cycles", "enc_cycles", "dec_cycles")
SETTINGS = ("normal-aslr-off", "normal-aslr-on", "reversed-aslr-off", "reversed-aslr-on")


def per_launch(result: Path):
    launches = sorted((result / "fresh-launches").glob("launch-*.out"))
    if not launches:
        return None
    return {op: [stabilized_quartiles(decode_observations(p.read_text(errors="replace"), op))[1]
                 for p in launches] for op in OPS}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--param", type=int, choices=(864, 1152), required=True)
    parser.add_argument("--experiment", type=Path, required=True)
    parser.add_argument("--compilers", nargs="+", default=["O3", "O2"])
    parser.add_argument("--tag", default="20260923")
    parser.add_argument("--phase-b-tag", default="20260923")
    args = parser.parse_args()
    results = args.experiment.resolve() / "results"
    paired = json.loads((results / f"fixed-lazy-paired-{args.phase_b_tag}/summary.json").read_text())
    rows = {(r["setting"], r["operation"]): r for r in paired["rows"]}
    phase_b = json.loads((results / f"phase-b-summary-{args.phase_b_tag}.json").read_text())
    out = {"schema": "ntruplus-caller-lazy-native-fixedcc/v1", "parameter": str(args.param),
           "evidence_class": "supercop-native-kem, controlled compiler (single-entry okc-amd64); "
                             "not SUPERCOP default compiler selection",
           "decision_rule": "robust research win iff pooled Native delta < 0 AND all four "
                            "fixed-ELF paired 95% CIs below zero",
           "phase_b_native_default_selection": {op: phase_b["native"][op]["delta"] for op in OPS},
           "compilers": {}}
    for cc in args.compilers:
        roles = {}
        for role in ("official", "candidate"):
            d = results / f"native-fixedcc-{cc}-{role}-{args.tag}"
            stq = json.loads((d / "stq-summary.json").read_text())
            meta = json.loads((d / "metadata.json").read_text())
            roles[role] = {"stq": stq, "meta": meta, "launch": per_launch(d), "dir": d.name}
        entry = {"roles": {}, "operations": {}, "decision": {}}
        for role, r in roles.items():
            m = r["meta"]
            entry["roles"][role] = {
                "result_dir": r["dir"], "implementation": m["implementation"],
                "compiler": r["stq"]["measure_identity"]["compiler"],
                "compiler_policy": m["compiler_policy"],
                "compiler_wrapper": Path(m["compiler_wrapper"]).name,
                "compiler_wrapper_sha256": m["compiler_wrapper_sha256"],
                "measure_elf_sha256": m["measure_elf_sha256"],
                "measure_source_sha256": m["measure_source_sha256"],
                "fresh_process_launches": m["fresh_process_launches"],
                "host_hygiene_contaminated": m["host_hygiene"]["contaminated"],
                "host_hygiene_attempt": m["host_hygiene"]["attempt"]}
        compilers = {v["compiler"] for v in entry["roles"].values()}
        if len(compilers) != 1:
            raise SystemExit(f"{cc}: roles used different compilers: {compilers}")
        for op in OPS:
            o = roles["official"]["stq"]["operations"][op]
            c = roles["candidate"]["stq"]["operations"][op]
            e = {q: {"official": o[q], "candidate": c[q], "delta": c[q] - o[q]}
                 for q in ("stq1", "stq2", "stq3")}
            e["delta_percent_stq2"] = 100 * (c["stq2"] - o["stq2"]) / o["stq2"]
            e["observations"] = [o["observations"], c["observations"]]
            lo, lc = roles["official"]["launch"], roles["candidate"]["launch"]
            if lo and lc:
                med_o = statistics.median(lo[op])
                e["launch_stq2"] = {"official": lo[op], "candidate": lc[op]}
                e["launch_stq2_median"] = {"official": med_o, "candidate": statistics.median(lc[op]),
                                           "delta": statistics.median(lc[op]) - med_o}
                e["candidate_launches_below_official_median"] = sum(v < med_o for v in lc[op])
                e["pairwise_candidate_below_official"] = sum(a < b for a in lc[op] for b in lo[op])
                e["pairwise_total"] = len(lc[op]) * len(lo[op])
            entry["operations"][op] = e
            cis = [rows[(s, op)] for s in SETTINGS]
            below = sum(r["bootstrap_ci95_high"] < 0 for r in cis)
            win = e["stq2"]["delta"] < 0 and below == 4
            entry["decision"][op] = {"native_pooled_negative": e["stq2"]["delta"] < 0,
                                     "paired_ci_below_zero_count": below,
                                     "robust_research_win": win,
                                     "verdict": "robust-research-win" if win else "not-robust"}
        out["compilers"][cc] = entry
    path = results / f"native-fixedcc-summary-{args.tag}.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    for cc, entry in out["compilers"].items():
        print(f"== {cc}: {entry['roles']['official']['compiler']}")
        for op in OPS:
            e = entry["operations"][op]
            print(f"  {op:15s} " + "  ".join(
                f"{q}:{e[q]['official']:.2f}->{e[q]['candidate']:.2f} ({e[q]['delta']:+.2f})"
                for q in ("stq1", "stq2", "stq3")) +
                f"  below-med {e.get('candidate_launches_below_official_median')}/9"
                f"  pairwise {e.get('pairwise_candidate_below_official')}/81"
                f"  -> {entry['decision'][op]['verdict']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
