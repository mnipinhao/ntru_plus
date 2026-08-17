#!/usr/bin/env python3
"""Run and summarize the bounded Forward-to-BaseInv landing probe."""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--cpu", type=int, default=2)
    parser.add_argument("--output", type=Path,
                        default=Path("results/tile4-forward-landing-baseinv-short.json"))
    args = parser.parse_args()

    completed = subprocess.run(
        [str(args.binary), str(args.iterations), str(args.cpu)],
        check=True, text=True, capture_output=True)
    regions: dict[str, list[dict]] = {}
    correctness = None
    for line in completed.stdout.splitlines():
        fields = dict(item.split("=", 1) for item in line.split()[1:]
                      if "=" in item)
        if line.startswith("correctness "):
            correctness = {
                "trials": int(fields["trials"]),
                "maximum_frontend_abs": int(fields["maximum_frontend_abs"]),
                "maximum_control_abs": int(fields["maximum_control_abs"]),
                "maximum_candidate_abs": int(fields["maximum_candidate_abs"]),
            }
        elif line.startswith("sample "):
            regions.setdefault(fields["region"], []).append({
                "index": int(fields["index"]),
                "control_tsc": float(fields["control"]),
                "candidate_tsc": float(fields["candidate"]),
                "delta_tsc": float(fields["delta"]),
            })
    assert correctness is not None
    summary = {}
    for name, samples in regions.items():
        deltas = [sample["delta_tsc"] for sample in samples]
        summary[name] = {
            "control_median_tsc": statistics.median(
                sample["control_tsc"] for sample in samples),
            "candidate_median_tsc": statistics.median(
                sample["candidate_tsc"] for sample in samples),
            "paired_delta_median_tsc": statistics.median(deltas),
            "paired_delta_mad_tsc": statistics.median(
                abs(value - statistics.median(deltas)) for value in deltas),
            "candidate_wins": sum(value < 0 for value in deltas),
            "samples": samples,
        }
    full = summary["full"]
    decision = ("continue-to-SoA-BaseInv-consumer-gate"
                if full["paired_delta_median_tsc"] <= 20.0
                else "stop-forward-checkpoint-cost-exceeds-budget")
    result = {
        "schema": "ntruplus768-gt32-forward-landing-baseinv-short-v1",
        "experiment": "GT32-FWD-LANDING-BASEINV-001",
        "iterations_per_sample": args.iterations,
        "samples": 20,
        "correctness": correctness,
        "regions": summary,
        "gate": {
            "maximum_allowed_full_forward_regression_tsc": 20.0,
            "decision": decision,
        },
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "correctness": correctness,
        "core": {key: value for key, value in summary["core"].items()
                 if key != "samples"},
        "full": {key: value for key, value in summary["full"].items()
                 if key != "samples"},
        "decision": decision,
    }, indent=2))


if __name__ == "__main__":
    main()
