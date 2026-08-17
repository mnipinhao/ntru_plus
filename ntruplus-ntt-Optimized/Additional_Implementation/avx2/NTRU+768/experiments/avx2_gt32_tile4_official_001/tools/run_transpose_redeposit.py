#!/usr/bin/env python3
"""Run the short GT32 transpose/redeposit T0-vs-T1 gate."""

from __future__ import annotations

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


def run_one(binary: Path, iterations: int, alignment: int) -> dict:
    run = subprocess.run(
        [str(binary), str(iterations), str(alignment)],
        check=True, text=True, capture_output=True)
    raw: dict[str, dict[str, list[float]]] = {}
    correctness = False
    for line in run.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            correctness = "correctness=pass" in fields
        if fields[0] != "SAMPLE":
            continue
        gate = raw.setdefault(fields[1], {"baseline": [], "candidate": [],
                                          "delta": []})
        gate["baseline"].append(float(fields[3]))
        gate["candidate"].append(float(fields[4]))
        gate["delta"].append(float(fields[5]))
    if not correctness or not raw:
        raise RuntimeError(f"missing valid output from {binary}")
    return {
        name: {
            "T0_baseline": stats(values["baseline"]),
            "T1_candidate": stats(values["candidate"]),
            "paired_candidate_minus_baseline": stats(values["delta"]),
            "T1_wins": sum(value < 0.0 for value in values["delta"]),
        }
        for name, values in raw.items()
    }


def packed_gate_passes(run: dict) -> bool:
    one = run["forward_bm"]
    two = run["two_forward_bm"]
    full = run["decap_polynomial_slice"]
    return (
        one["paired_candidate_minus_baseline"]["median_tsc"] <= -10.0
        and one["T1_wins"] >= 18
        and two["paired_candidate_minus_baseline"]["median_tsc"] <= -15.0
        and two["T1_wins"] >= 18
        and full["paired_candidate_minus_baseline"]["median_tsc"] < 0.0
        and full["T1_wins"] >= 18
    )


def aos_gate_passes(run: dict) -> bool:
    one = run["aos_transpose_plus_bm"]
    two = run["aos_two_transpose_bm"]
    return (
        one["paired_candidate_minus_baseline"]["median_tsc"] <= -10.0
        and one["T1_wins"] >= 18
        and two["paired_candidate_minus_baseline"]["median_tsc"] <= -15.0
        and two["T1_wins"] >= 18
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--static-gate", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    placements = {}
    for name, binary in (("normal", args.binary),
                         ("reversed", args.reversed_binary)):
        placements[name] = {
            "alignment_64": run_one(binary, args.iterations, 64),
            "alignment_32": run_one(binary, args.iterations, 32),
        }
    packed_pass = all(packed_gate_passes(run)
                      for placement in placements.values()
                      for run in placement.values())
    aos_pass = all(aos_gate_passes(run)
                   for placement in placements.values()
                   for run in placement.values())
    decision = ("pass-short-await-serious-authorization"
                if packed_pass or aos_pass else
                "stop-T1-no-stable-producer-consumer-advantage")
    static_gate = json.loads(args.static_gate.read_text())
    result = {
        "schema": "ntruplus768-gt32-transpose-redeposit-benchmark-v1",
        "experiment": "GT32-TRANSPOSE-REDEPOSIT-001",
        "benchmark": {
            "iterations": args.iterations,
            "samples": 20,
            "warmups": 2,
            "cpu": 1,
            "ordering": "paired-AB-BA",
            "placements": ["T1-before-T0", "T0-before-T1"],
            "scratch_alignments": [64, 32],
            "serious_benchmark": False,
        },
        "correctness": {
            "status": "pass",
            "random_trials_per_binary_alignment": 1000,
            "checks": [
                "T1-terminal-bit-exact-to-T0",
                "T1-AoS-transpose-bit-exact-to-T0",
                "T1-AoS-transpose-plus-BM-bit-exact-to-T0",
                "T1-two-forward-BM-I1-T9-crepmod3-bit-exact-to-T0",
            ],
        },
        "static_gate_decision": static_gate["decision_before_benchmark"],
        "placements": placements,
        "thresholds": {
            "one_forward_plus_BM_min_saving_tsc": 10,
            "two_forward_plus_BM_min_saving_tsc": 15,
            "decap_slice_must_improve": True,
            "minimum_wins_each_required_region": 18,
            "must_pass_both_alignments_and_placements": True,
        },
        "decision": decision,
        "candidate_decisions": {
            "packed_stage5_to_SoA": ("pass" if packed_pass else "stop"),
            "AoS_to_SoA": ("pass" if aos_pass else "stop"),
        },
        "production_integration": False,
        "pmu_run": False,
        "serious_run": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for placement, aligned in placements.items():
        for alignment, runs in aligned.items():
            one = runs["forward_bm"]["paired_candidate_minus_baseline"]
            two = runs["two_forward_bm"]["paired_candidate_minus_baseline"]
            aos_one = runs["aos_transpose_plus_bm"][
                "paired_candidate_minus_baseline"]
            aos_two = runs["aos_two_transpose_bm"][
                "paired_candidate_minus_baseline"]
            full = runs["decap_polynomial_slice"][
                "paired_candidate_minus_baseline"]
            print(f"{placement}/{alignment}: packed-one={one['median_tsc']:.3f}, "
                  f"packed-two={two['median_tsc']:.3f}, "
                  f"aos-one={aos_one['median_tsc']:.3f}, "
                  f"aos-two={aos_two['median_tsc']:.3f}, "
                  f"full={full['median_tsc']:.3f}")
    print(f"decision={decision}")


if __name__ == "__main__":
    main()
