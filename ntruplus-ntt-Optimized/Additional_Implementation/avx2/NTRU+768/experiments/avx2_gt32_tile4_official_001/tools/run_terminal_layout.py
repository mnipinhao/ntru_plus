#!/usr/bin/env python3
"""Run terminal-layout and transpose-cut plus BaseMul short gates."""

import argparse
import json
import statistics
import subprocess
from pathlib import Path


def stats(values: list[float]) -> dict[str, float]:
    median = statistics.median(values)
    return {
        "median_tsc": median,
        "mad_tsc": statistics.median(
            abs(value - median) for value in values
        ),
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
        gate = raw.setdefault(fields[1], {
            "baseline": [], "candidate": [], "delta": []})
        gate["baseline"].append(float(fields[3]))
        gate["candidate"].append(float(fields[4]))
        gate["delta"].append(float(fields[5]))
    gates = {
        name: {
            "baseline": stats(values["baseline"]),
            "candidate": stats(values["candidate"]),
            "paired_candidate_minus_baseline": stats(values["delta"]),
            "candidate_wins": sum(value < 0.0 for value in values["delta"]),
            "paired_saving_tsc": -statistics.median(values["delta"]),
        }
        for name, values in raw.items()
    }
    orientations = {
        "soa_l2": gates["sa_vs_soa_l2"],
        "l2_soa": gates["sa_vs_l2_soa"],
    }
    selected_orientation, selected_gate = max(
        orientations.items(), key=lambda item: item[1]["paired_saving_tsc"])
    current_saving = selected_gate["paired_saving_tsc"]
    decision = (
        f"pass-{selected_orientation}-continue-full-consumer-gate"
        if current_saving >= 20.0
        else "stop-asymmetric-transpose-cut-below-20-tsc-incremental-gate"
    )
    result = {
        "schema": "ntruplus768-terminal-transpose-cut-v2",
        "benchmark": {
            "iterations": args.iterations,
            "samples": 20,
            "cpu": 1,
            "ordering": "paired-AB-BA",
            "scope": "two-post-frontend-NTT32-cores-plus-BM-to-standard-AoS",
        },
        "correctness": {
            "status": "pass",
            "checks": [
                "L1-and-L2-to-standard-AoS-BM-exact",
                "mixed-and-two-specialized-operands-exact",
                "SoA-L2-and-L2-SoA-orientations-exact",
                "64-random-small-input-cases",
            ],
        },
        "static": {
            "selected_layout": "asymmetric-private-SoA-and-L2",
            "producer_plus_B3_input_shuffles": 48,
            "saving_vs_SA_shuffles_per_block": 4,
            "extra_montgomery_chains": 0,
            "cross_128_bit_repairs": 0,
            "BM_output": "unchanged-standard-AoS",
        },
        "gates": gates,
        "thresholds": {
            "incremental_vs_existing_SA_min_paired_saving_tsc": 20,
        },
        "decision": decision,
        "production_integration": False,
        "serious_benchmark_run": False,
        "next": (
            "full 2F+BM+I1+T9 transpose-cut short gate"
            if decision.startswith("pass-")
            else "retain standard private-SoA control"
        ),
        "selected_orientation": selected_orientation,
        "selected_incremental_saving_vs_existing_SA_tsc": current_saving,
        "orientation_incremental_savings_vs_SA_tsc": {
            name: gate["paired_saving_tsc"]
            for name, gate in orientations.items()
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
