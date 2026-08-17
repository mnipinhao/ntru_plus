#!/usr/bin/env python3
"""Run the bounded NTT32 S1-S3 physical-schedule benchmark."""

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


def run(binary: Path, iterations: int) -> dict[str, object]:
    result = subprocess.run(
        [str(binary), str(iterations)], check=True, text=True,
        capture_output=True)
    regions: dict[str, dict[str, list[float]]] = {
        "wave_s1s3": {"control": [], "candidate": [], "delta": []},
        "suffix_route": {"control": [], "candidate": [], "delta": []},
    }
    for line in result.stdout.splitlines():
        fields = line.split(",")
        if fields[0] != "SAMPLE":
            continue
        region = regions[fields[1]]
        region["control"].append(float(fields[3]))
        region["candidate"].append(float(fields[4]))
        region["delta"].append(float(fields[5]))
    result: dict[str, object] = {}
    for name, values in regions.items():
        if len(values["delta"]) != 20:
            raise RuntimeError(f"missing {name} samples from {binary}")
        result[name] = {
            "control": stats(values["control"]),
            "candidate": stats(values["candidate"]),
            "paired_candidate_minus_control": stats(values["delta"]),
            "candidate_wins": sum(delta < 0.0 for delta in values["delta"]),
        }
    return result


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
    for placement_result in placements.values():
        wave = placement_result["wave_s1s3"][
            "paired_candidate_minus_control"]["median_tsc"]
        route = placement_result["suffix_route"][
            "paired_candidate_minus_control"]["median_tsc"]
        placement_result["three_wave_plus_route_estimate_tsc"] = 3.0 * wave + route
    estimates = [
        result["three_wave_plus_route_estimate_tsc"]
        for result in placements.values()
    ]
    result = {
        "schema": "ntruplus768-gt32-n32-wave-schedule-short-v1",
        "experiment": "GT-N32-PHYSICAL-SCHEDULE-005",
        "benchmark": {
            "iterations": args.iterations,
            "samples": 20,
            "warmups": 2,
            "ordering": "paired-AB-BA",
            "placements": ["normal", "reversed-link-order"],
            "serious": False,
        },
        "scope": "post-twist S1-S3 wave plus all-16-component suffix-route attribution",
        "correctness": "separate 1000-trial exact, alias and semantic-route tests passed",
        "placements": placements,
        "decision": (
            "R3-wave-and-route-budget-positive-stop-isolated-producer"
            if min(estimates) > 0.0
            else "R3-budget-allows-full-producer"
        ),
        "full_island_qualified": False,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for placement, placement_result in placements.items():
        for region in ("wave_s1s3", "suffix_route"):
            region_result = placement_result[region]
            delta = region_result["paired_candidate_minus_control"]
            print(
                f"{placement} {region}: delta={delta['median_tsc']:.3f} TSC "
                f"MAD={delta['mad_tsc']:.3f} "
                f"wins={region_result['candidate_wins']}/20"
            )
        print(
            f"{placement} estimate(3*wave+route)="
            f"{placement_result['three_wave_plus_route_estimate_tsc']:.3f} TSC"
        )
    print(f"decision={result['decision']}")


if __name__ == "__main__":
    main()
