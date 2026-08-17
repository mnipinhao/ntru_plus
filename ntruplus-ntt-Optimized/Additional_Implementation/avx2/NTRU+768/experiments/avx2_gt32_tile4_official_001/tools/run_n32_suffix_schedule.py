#!/usr/bin/env python3
"""Run the bounded N32 conjugated-suffix scheduling gate."""

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
    records = {"s45_3way": [], "dft_dual": [], "mlkstyle": []}
    for line in completed.stdout.splitlines():
        fields = line.split(",")
        if len(fields) == 6 and fields[0] == "SAMPLE" and fields[1] in records:
            records[fields[1]].append({
                "sample": int(fields[2]),
                "serial_tsc": float(fields[3]),
                "three_way_tsc": float(fields[4]),
                "delta_tsc": float(fields[5]),
            })
    result: dict[str, object] = {"binary": str(binary), "regions": {}}
    for region, samples in records.items():
        assert len(samples) == 20
        deltas = [float(sample["delta_tsc"]) for sample in samples]
        median = statistics.median(deltas)
        result["regions"][region] = {
            "samples": samples,
            "median_serial_tsc": statistics.median(
                float(sample["serial_tsc"]) for sample in samples),
            "median_candidate_tsc": statistics.median(
                float(sample["three_way_tsc"]) for sample in samples),
            "median_candidate_minus_serial_tsc": median,
            "candidate_wins": sum(delta < 0.0 for delta in deltas),
            "mad_delta_tsc": statistics.median(
                abs(delta - median) for delta in deltas),
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=5000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = {
        "schema": "ntruplus768-gt32-n32-suffix-reschedule-short-v1",
        "experiment": "GT-N32-SUFFIX-RESCHEDULE-015",
        "iterations": args.iterations,
        "placements": {
            "normal": run(args.binary, args.iterations),
            "reversed": run(args.reversed_binary, args.iterations),
        },
        "comparison": (
            "bit-identical serial versus three-way S4/S5 schedule over the "
            "complete two-branch conjugated suffix"
        ),
    }
    decisions = {}
    for region in ("s45_3way", "dft_dual", "mlkstyle"):
        normal = result["placements"]["normal"]["regions"][region]
        reversed_result = result["placements"]["reversed"]["regions"][region]
        passed = (
            normal["median_candidate_minus_serial_tsc"] <= -5.0
            and reversed_result["median_candidate_minus_serial_tsc"] <= -5.0
            and normal["candidate_wins"] >= 18
            and reversed_result["candidate_wins"] >= 18
        )
        decisions[region] = "pass-expand-to-complete-forward" if passed else "stop"
    result["candidate_decisions"] = decisions
    result["decision"] = (
        "pass-one-or-more-suffix-candidates" if "pass-expand-to-complete-forward" in decisions.values()
        else "stop-suffix-reschedule-family"
    )
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(args.output)
    for placement, placement_record in result["placements"].items():
        for region, record in placement_record["regions"].items():
            print(placement, region, record["median_serial_tsc"],
                  record["median_candidate_tsc"],
                  record["median_candidate_minus_serial_tsc"],
                  f"{record['candidate_wins']}/20",
                  "MAD", record["mad_delta_tsc"])
    print(result["decision"])


if __name__ == "__main__":
    main()
