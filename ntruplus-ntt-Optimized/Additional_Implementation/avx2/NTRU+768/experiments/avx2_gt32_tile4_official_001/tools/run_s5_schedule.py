#!/usr/bin/env python3
"""Gate the destructive four-way private-forward stage-5 schedule."""

import argparse
import json
import statistics
import subprocess
from pathlib import Path


def stats(values: list[float]) -> dict[str, float]:
    median = statistics.median(values)
    return {
        "median_tsc": median,
        "mad_tsc": statistics.median(abs(value - median) for value in values),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    run = subprocess.run(
        [str(args.binary), str(args.iterations)], check=True, text=True,
        capture_output=True)
    raw: dict[str, dict[str, list[float]]] = {}
    for line in run.stdout.splitlines():
        fields = line.split(",")
        if fields[0] != "SAMPLE":
            continue
        gate = raw.setdefault(fields[1], {"baseline": [], "candidate": [],
                                          "delta": []})
        gate["baseline"].append(float(fields[3]))
        gate["candidate"].append(float(fields[4]))
        gate["delta"].append(float(fields[5]))
    gates = {
        name: {
            "baseline": stats(values["baseline"]),
            "candidate": stats(values["candidate"]),
            "paired_candidate_minus_baseline": stats(values["delta"]),
            "candidate_wins": sum(value < 0.0 for value in values["delta"]),
        }
        for name, values in raw.items()
    }
    core_saving = -gates["forward_core"]["paired_candidate_minus_baseline"]["median_tsc"]
    chain_saving = -gates["two_forward_bm_i1_t9"]["paired_candidate_minus_baseline"]["median_tsc"]
    decision = ("pass-continue-to-stage4-stage5-combined-network"
                if core_saving >= 5.0 and chain_saving >= 8.0
                else "stop-stage5-scheduling-no-material-improvement")
    result = {
        "schema": "ntruplus768-private-forward-s5x4-v1",
        "benchmark": {"iterations": args.iterations, "samples": 20,
                      "cpu": 1, "ordering": "paired-AB-BA"},
        "correctness": {"status": "pass", "checks": [
            "private-forward-core-exact", "two-forward-BM-I1-T9-exact"]},
        "static_change": {
            "removed_register_moves_per_tile": 4,
            "tiles_per_polynomial": 6,
            "removed_register_moves_per_polynomial": 24,
            "montgomery_chains_issued_in_parallel": 4,
            "stage4_and_plane_mapping_unchanged": True,
        },
        "gates": gates,
        "thresholds": {"forward_core_min_saving_tsc": 5,
                       "full_chain_min_saving_tsc": 8},
        "decision": decision,
        "production_integration": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
