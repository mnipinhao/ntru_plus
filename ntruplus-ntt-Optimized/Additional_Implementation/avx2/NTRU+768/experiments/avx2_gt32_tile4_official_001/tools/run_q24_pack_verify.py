#!/usr/bin/env python3
"""Launch-level two-placement gate for lazy Q24 GT-pack-and-verify."""

import argparse
import json
import math
import random
import statistics
import subprocess
from pathlib import Path


def median_mad(values: list[float]) -> dict[str, float]:
    median = statistics.median(values)
    return {
        "median": median,
        "mad": statistics.median(abs(value - median) for value in values),
    }


def bootstrap_ci(values: list[float], seed: int,
                 resamples: int = 20000) -> list[float]:
    rng = random.Random(seed)
    medians = sorted(statistics.median([rng.choice(values) for _ in values])
                     for _ in range(resamples))
    return [medians[int(0.025 * (resamples - 1))],
            medians[int(0.975 * (resamples - 1))]]


def run_launch(binary: Path, iterations: int) -> dict[str, list[float]]:
    process = subprocess.run([str(binary), str(iterations)], check=True,
                             text=True, capture_output=True)
    valid = False
    regions: dict[str, list[float]] = {
        "pack_verify": [],
        "n5_pack_verify": [],
    }
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            valid = ("scope=lazy10788-q24-pack-and-verify" in line
                     and "materialized-candidate=0" in line
                     and "n5=unchanged" in line)
        elif fields[0] == "SAMPLE" and fields[1] in regions:
            regions[fields[1]].append(float(fields[5]))
    if not valid or any(len(values) != 20 for values in regions.values()):
        raise RuntimeError(f"invalid benchmark output from {binary}")
    return regions


def summarize(binary: Path, iterations: int, launches: int,
              seed: int) -> dict:
    raw = [run_launch(binary, iterations) for _ in range(launches)]
    result = {"binary": str(binary), "regions": {}}
    for index, name in enumerate(("pack_verify", "n5_pack_verify")):
        launch_values = [launch[name] for launch in raw]
        pooled = [value for launch in launch_values for value in launch]
        launch_medians = [statistics.median(launch) for launch in launch_values]
        result["regions"][name] = {
            "paired_delta": median_mad(pooled),
            "wins": sum(value < 0 for value in pooled),
            "samples": len(pooled),
            "launch_medians": launch_medians,
            "negative_launch_medians": sum(value < 0
                                             for value in launch_medians),
            "launches": launches,
            "launch_median_bootstrap_95_ci": bootstrap_ci(
                launch_medians, seed + index),
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--launches", type=int, default=16)
    parser.add_argument("--output", type=Path,
                        default=Path("results/tile4-q24-pack-verify-short.json"))
    args = parser.parse_args()

    placements = {
        "normal": summarize(args.binary, args.iterations, args.launches,
                            0x24F100),
        "reversed": summarize(args.reversed_binary, args.iterations,
                              args.launches, 0x24F200),
    }
    minimum_negative = math.ceil(0.90 * args.launches)
    passed = all(
        -value["regions"]["n5_pack_verify"]["paired_delta"]["median"]
            >= 30.0
        and value["regions"]["n5_pack_verify"]["negative_launch_medians"]
            >= minimum_negative
        and value["regions"]["n5_pack_verify"]
            ["launch_median_bootstrap_95_ci"][1] < 0.0
        for value in placements.values())
    result = {
        "schema": "ntruplus768-gt32-q24-pack-verify-v1",
        "experiment": "GT32-Q24-PACK-VERIFY-001",
        "control": "N5 -> lazy10788 Q24 GT-pack -> 1152-byte buffer -> verify",
        "candidate": "N5 -> lazy10788 Q24 packet -> direct compare",
        "method": {
            "iterations_per_sample": args.iterations,
            "samples_per_launch": 20,
            "launches_per_placement": args.launches,
            "order": "paired AB/BA",
            "primary_unit": "launch median",
            "candidate_materialized_bytes": 0,
            "n5_path": "unchanged",
        },
        "placements": placements,
        "continuation_gate": {
            "minimum_n5_region_saving_tsc": 30.0,
            "minimum_negative_launch_medians": minimum_negative,
            "bootstrap_upper_must_be_negative": True,
            "pass": passed,
        },
        "decision": ("continue-full-decap-integration" if passed
                     else "stop-pack-verify-below-local-gate"),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for placement, value in placements.items():
        region = value["regions"]["n5_pack_verify"]
        print(f"{placement}: delta={region['paired_delta']['median']:.3f} "
              f"wins={region['wins']}/{region['samples']} "
              f"launches={region['negative_launch_medians']}/"
              f"{region['launches']} "
              f"CI={region['launch_median_bootstrap_95_ci']}")
    print(f"decision={result['decision']}")


if __name__ == "__main__":
    main()
