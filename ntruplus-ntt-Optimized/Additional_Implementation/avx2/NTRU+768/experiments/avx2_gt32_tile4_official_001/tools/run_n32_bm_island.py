#!/usr/bin/env python3
"""Run the bounded half-native R1-U landing benchmark."""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from pathlib import Path


def summary(values: list[float]) -> dict[str, float]:
    median = statistics.median(values)
    return {
        "median_tsc": median,
        "mad_tsc": statistics.median(abs(value - median) for value in values),
    }


def run(binary: Path, iterations: int) -> dict[str, object]:
    result = subprocess.run(
        [str(binary), str(iterations)], check=True, text=True,
        capture_output=True)
    baseline: list[float] = []
    candidate: list[float] = []
    delta: list[float] = []
    for line in result.stdout.splitlines():
        fields = line.split(",")
        if fields[0] != "SAMPLE":
            continue
        baseline.append(float(fields[3]))
        candidate.append(float(fields[4]))
        delta.append(float(fields[5]))
    if len(delta) != 20:
        raise RuntimeError(f"missing samples from {binary}")
    return {
        "control_standard_R1U": summary(baseline),
        "candidate_half_native_R1U": summary(candidate),
        "paired_candidate_minus_control": summary(delta),
        "candidate_wins": sum(value < 0.0 for value in delta),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=5000)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    placements = {
        "normal": run(args.binary, args.iterations),
        "reversed": run(args.reversed_binary, args.iterations),
    }
    deltas = [
        value["paired_candidate_minus_control"]["median_tsc"]
        for value in placements.values()
    ]
    result = {
        "schema": "ntruplus768-gt32-n32-bm-island-short-v1",
        "experiment": "GT-N32-BM-ISLAND-004",
        "benchmark": {
            "iterations": args.iterations,
            "samples": 20,
            "warmups": 2,
            "ordering": "paired-AB-BA",
            "placements": ["normal", "reversed-link-order"],
            "serious": False,
        },
        "scope": "BM landing only; producer and inverse are not timed",
        "correctness": "separate 1000-trial exact and alias test passed",
        "placements": placements,
        "decision": (
            "half-native-BM-landing-cycle-parity-pass"
            if max(abs(value) for value in deltas) <= 10.0
            else "half-native-BM-landing-placement-cost-needs-attribution"
        ),
        "full_island_qualified": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for placement, value in placements.items():
        delta = value["paired_candidate_minus_control"]
        print(
            f"{placement}: delta={delta['median_tsc']:.3f} TSC "
            f"MAD={delta['mad_tsc']:.3f} wins={value['candidate_wins']}/20"
        )
    print(f"decision={result['decision']}")


if __name__ == "__main__":
    main()
