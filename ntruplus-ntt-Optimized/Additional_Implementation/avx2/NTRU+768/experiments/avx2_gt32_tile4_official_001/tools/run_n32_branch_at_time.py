#!/usr/bin/env python3
"""Run the one-wave conjugated branch-at-a-time scheduling gate."""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from pathlib import Path


def run(binary: Path, iterations: int) -> dict[str, object]:
    completed = subprocess.run(
        [str(binary.resolve()), str(iterations)], check=True,
        text=True, capture_output=True)
    samples = []
    for line in completed.stdout.splitlines():
        fields = line.split(",")
        if len(fields) == 5 and fields[0] == "SAMPLE":
            samples.append({
                "sample": int(fields[1]),
                "control_tsc": float(fields[2]),
                "branch_at_time_tsc": float(fields[3]),
                "delta_tsc": float(fields[4]),
            })
    assert len(samples) == 20
    deltas = [float(sample["delta_tsc"]) for sample in samples]
    median = statistics.median(deltas)
    return {
        "binary": str(binary),
        "samples": samples,
        "median_control_tsc": statistics.median(
            float(sample["control_tsc"]) for sample in samples),
        "median_branch_at_time_tsc": statistics.median(
            float(sample["branch_at_time_tsc"]) for sample in samples),
        "median_delta_tsc": median,
        "candidate_wins": sum(delta < 0.0 for delta in deltas),
        "mad_delta_tsc": statistics.median(abs(delta - median) for delta in deltas),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=10000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = {
        "schema": "ntruplus768-gt32-n32-branch-at-time-short-v1",
        "experiment": "GT-N32-CONJ-BRANCH-AT-A-TIME-019",
        "iterations": args.iterations,
        "scope": "one complete wave: shared top split plus conjugated S1-S3",
        "static_tradeoff_per_wave": {
            "Montgomery_chains_delta": 0,
            "extra_32byte_stores": 7,
            "extra_32byte_loads": 7,
            "extra_L1_bytes": 448,
            "branch0_schedule": "twelve serial-source macros to three four-way stages",
            "q": "one register-resident load for both branches",
        },
        "placements": {
            "normal": run(args.binary, args.iterations),
            "reversed": run(args.reversed_binary, args.iterations),
        },
    }
    normal = result["placements"]["normal"]
    reversed_result = result["placements"]["reversed"]
    passed = (
        normal["median_delta_tsc"] <= -2.0
        and reversed_result["median_delta_tsc"] <= -2.0
        and normal["candidate_wins"] >= 18
        and reversed_result["candidate_wins"] >= 18
    )
    result["decision"] = (
        "pass-expand-to-complete-forward" if passed
        else "stop-branch-at-a-time-producer-schedule"
    )
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(args.output)
    for placement, record in result["placements"].items():
        print(placement, record["median_control_tsc"],
              record["median_branch_at_time_tsc"], record["median_delta_tsc"],
              f"{record['candidate_wins']}/20", "MAD", record["mad_delta_tsc"])
    print(result["decision"])


if __name__ == "__main__":
    main()
