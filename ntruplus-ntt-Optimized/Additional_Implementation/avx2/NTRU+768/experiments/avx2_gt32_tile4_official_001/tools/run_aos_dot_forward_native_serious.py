#!/usr/bin/env python3
"""Run the 100k serious Forward-native R1-U chain closure gate."""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from pathlib import Path


GATE = "forward_native_r1u_vs_b3"


def summary(values: list[float]) -> dict[str, float]:
    median = statistics.median(values)
    return {
        "median_tsc": median,
        "mad_tsc": statistics.median(abs(value - median) for value in values),
    }


def run(binary: Path, iterations: int) -> dict[str, object]:
    process = subprocess.run(
        [str(binary), str(iterations), "forward-only"], check=True,
        text=True, capture_output=True)
    metadata = ""
    correctness = False
    baseline: list[float] = []
    candidate: list[float] = []
    delta: list[float] = []
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            metadata = line
            correctness = ("correctness=pass" in fields
                           and "forward_only=1" in fields)
        elif fields[:2] == ["SAMPLE", GATE]:
            baseline.append(float(fields[3]))
            candidate.append(float(fields[4]))
            delta.append(float(fields[5]))
    if not correctness or len(delta) != 20:
        raise RuntimeError(f"invalid serious output from {binary}")
    return {
        "metadata": metadata,
        "B3_control": summary(baseline),
        "R1_U_candidate": summary(candidate),
        "paired_candidate_minus_control": summary(delta),
        "candidate_wins": sum(value < 0.0 for value in delta),
        "raw": {"baseline": baseline, "candidate": candidate,
                "delta": delta},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=100000)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    placements = {
        "normal": run(args.binary, args.iterations),
        "reversed": run(args.reversed_binary, args.iterations),
    }
    passed = all(
        -result["paired_candidate_minus_control"]["median_tsc"] >= 40.0
        and result["candidate_wins"] >= 18
        and result["paired_candidate_minus_control"]["mad_tsc"]
        < -result["paired_candidate_minus_control"]["median_tsc"]
        for result in placements.values())
    decision = (
        "pass-serious-Forward-native-R1-U-specialized-chain-qualified"
        if passed else "stop-Forward-native-R1-U-serious-gate")
    result = {
        "schema": "ntruplus768-gt32-forward-native-r1u-serious-v1",
        "experiment": "GT32-AOS-DOT-REDC16-FORWARD-NATIVE-SERIOUS-001",
        "scope": (
            "2x coefficient-order Forward -> TILE4 AoS -> scale-BM -> "
            "I1 -> T9 -> crepmod3"),
        "control": "Forward-native AoS -> transpose/SoA B3 -> inverse",
        "candidate": "Forward-native AoS -> R1-U -> inverse",
        "benchmark": {
            "iterations": args.iterations,
            "samples": 20,
            "warmups": 2,
            "cpu": 1,
            "ordering": "ABBA/BAAB",
            "placements": ["normal", "reversed-link-order"],
            "unit": "TSC ticks per full region",
            "mode": "serious",
        },
        "correctness": {
            "status": "pass",
            "trials_per_binary": 1000,
            "contract": (
                "Forward AoS e=0 x e=0 -> R1-U AoS e=-1 -> "
                "inverse coefficient output -> crepmod3"),
        },
        "thresholds": {
            "minimum_saving_tsc_each_placement": 40,
            "minimum_wins_each_placement": 18,
            "MAD_must_be_below_saving": True,
        },
        "placements": placements,
        "decision": decision,
        "generic_basemul_selector_changed": False,
        "production_KEM_callsite_selected": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for name, placement in placements.items():
        delta = placement["paired_candidate_minus_control"]
        print(
            f"{name}: B3={placement['B3_control']['median_tsc']:.3f}, "
            f"R1-U={placement['R1_U_candidate']['median_tsc']:.3f}, "
            f"delta={delta['median_tsc']:.3f}, "
            f"MAD={delta['mad_tsc']:.3f}, "
            f"wins={placement['candidate_wins']}/20")
    print(f"decision={decision}")


if __name__ == "__main__":
    main()
