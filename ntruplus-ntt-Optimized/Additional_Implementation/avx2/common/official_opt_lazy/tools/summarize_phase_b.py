#!/usr/bin/env python3
"""Summarise Phase-B Native and fixed-ELF paired evidence for one parameter.

Reads the committed curated files (native stq-summary.json/metadata.json and
fixed-lazy-paired summary.json/manifest.json) plus, when present locally, the
untracked per-launch Native output to add per-launch StQ2 medians.  Applies
the 768 decision rule per operation: a robust research win needs a negative
pooled Native delta AND all four paired 95% CIs entirely below zero.
Writes results/phase-b-summary-<tag>.json.
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
    out = {op: [] for op in OPS}
    for path in launches:
        text = path.read_text(errors="replace")
        for op in OPS:
            out[op].append(stabilized_quartiles(decode_observations(text, op))[1])
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--param", type=int, choices=(864, 1152), required=True)
    parser.add_argument("--experiment", type=Path, required=True)
    parser.add_argument("--tag", default="20260923")
    args = parser.parse_args()
    results = args.experiment.resolve() / "results"
    native = {}
    for role in ("official", "candidate"):
        d = results / f"native-lazy-qual-{role}-{args.tag}"
        stq = json.loads((d / "stq-summary.json").read_text())
        meta = json.loads((d / "metadata.json").read_text())
        native[role] = {"stq": stq, "meta": meta, "launch": per_launch(d)}
    paired = json.loads((results / f"fixed-lazy-paired-{args.tag}/summary.json").read_text())
    rows = {(r["setting"], r["operation"]): r for r in paired["rows"]}
    out = {"schema": "ntruplus-caller-lazy-phase-b/v1", "parameter": str(args.param),
           "native": {}, "paired": {}, "decision": {}}
    for role in native:
        m = native[role]["meta"]
        out["native"][role] = {
            "implementation": m["implementation"],
            "compiler": native[role]["stq"]["measure_identity"]["compiler"],
            "measure_elf_sha256": m["measure_elf_sha256"],
            "fresh_process_launches": m["fresh_process_launches"],
            "host_hygiene_contaminated": m["host_hygiene"]["contaminated"]}
    for op in OPS:
        o = native["official"]["stq"]["operations"][op]["stq2"]
        c = native["candidate"]["stq"]["operations"][op]["stq2"]
        entry = {"official_stq2": o, "candidate_stq2": c, "delta": c - o,
                 "delta_percent": 100 * (c - o) / o}
        lo, lc = native["official"]["launch"], native["candidate"]["launch"]
        if lo and lc:
            entry["official_launch_stq2_median"] = statistics.median(lo[op])
            entry["candidate_launch_stq2_median"] = statistics.median(lc[op])
            entry["candidate_launches_below_official_median"] = sum(
                v < statistics.median(lo[op]) for v in lc[op])
        out["native"][op] = entry
        cis = {}
        for s in SETTINGS:
            r = rows[(s, op)]
            cis[s] = {"mean": r["paired_mean_delta_cycles"], "median": r["paired_median_delta_cycles"],
                      "ci95": [r["bootstrap_ci95_low"], r["bootstrap_ci95_high"]],
                      "favorable_blocks": r["favorable_blocks"], "blocks": r["blocks"]}
        out["paired"][op] = cis
        all_below = all(v["ci95"][1] < 0 for v in cis.values())
        all_above = all(v["ci95"][0] > 0 for v in cis.values())
        win = entry["delta"] < 0 and all_below
        out["decision"][op] = {
            "native_pooled_negative": entry["delta"] < 0,
            "paired_all_ci_below_zero": all_below,
            "paired_all_ci_above_zero": all_above,
            "paired_ci_below_zero_count": sum(v["ci95"][1] < 0 for v in cis.values()),
            "paired_ci_above_zero_count": sum(v["ci95"][0] > 0 for v in cis.values()),
            "robust_research_win": win,
            "verdict": ("robust-research-win" if win else
                        "robust-regression" if entry["delta"] > 0 and all_above else
                        "not-robust")}
    path = results / f"phase-b-summary-{args.tag}.json"
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n")
    print(json.dumps(out["decision"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
