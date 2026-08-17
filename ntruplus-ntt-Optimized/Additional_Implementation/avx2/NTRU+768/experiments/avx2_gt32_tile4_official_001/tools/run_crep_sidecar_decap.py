#!/usr/bin/env python3
"""Measure the integrated crepmod3 sidecar candidate against its old GT control."""

import argparse
import json
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


def run_launch(binary: Path, iterations: int) -> list[float]:
    process = subprocess.run([str(binary), str(iterations), "sidecar"],
                             check=True, text=True, capture_output=True)
    valid = False
    deltas = []
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            valid = ("scope=crepmod3-sidecar-tap" in line
                     and "full-m-materialized=1" in line
                     and "n5-path=unchanged" in line)
        elif fields[0] == "SIDECAR_SAMPLE":
            deltas.append(float(fields[4]))
    if not valid or len(deltas) != 20:
        raise RuntimeError(f"invalid sidecar output from {binary}")
    return deltas


def summarize(binary: Path, iterations: int, launches: int,
              seed: int) -> dict:
    raw = [run_launch(binary, iterations) for _ in range(launches)]
    pooled = [value for launch in raw for value in launch]
    launch_medians = [statistics.median(launch) for launch in raw]
    return {
        "binary": str(binary),
        "paired_delta": median_mad(pooled),
        "wins": sum(value < 0 for value in pooled),
        "samples": len(pooled),
        "launch_medians": launch_medians,
        "negative_launch_medians": sum(value < 0 for value in launch_medians),
        "launches": launches,
        "launch_median_bootstrap_95_ci": bootstrap_ci(launch_medians, seed),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--launches", type=int, default=8)
    parser.add_argument("--output", type=Path,
                        default=Path("results/tile4-crep-sidecar-decap-short.json"))
    args = parser.parse_args()

    placements = {
        "normal": summarize(args.binary, args.iterations, args.launches,
                            0xc2a400),
        "reversed": summarize(args.reversed_binary, args.iterations,
                              args.launches, 0xc2a500),
    }
    passed = all(
        -value["paired_delta"]["median"] >= 30.0
        and value["launch_median_bootstrap_95_ci"][1] < 0.0
        for value in placements.values())
    result = {
        "schema": "ntruplus768-gt32-crep-sidecar-decap-v1",
        "experiment": "GT32-CREPMOD3-SIDECAR-TAP-001",
        "control": "qualified Q24 lazy10788 candidate with Official SOTP",
        "candidate": "same GT candidate with S1 crep sidecar and compact SOTP",
        "method": {
            "iterations_per_sample": args.iterations,
            "samples_per_launch": 20,
            "launches_per_placement": args.launches,
            "order": "paired AB/BA",
            "full_m_materialized": True,
            "n5_path": "unchanged",
        },
        "placements": placements,
        "continuation_gate": {
            "minimum_saving_tsc": 30.0,
            "bootstrap_upper_must_be_negative": True,
            "pass": passed,
        },
        "decision": ("sidecar-production-candidate-qualified" if passed
                     else "sidecar-full-decap-gate-failed"),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for name, value in placements.items():
        print(f"{name}: delta={value['paired_delta']['median']:.3f} "
              f"wins={value['wins']}/{value['samples']} "
              f"launches={value['negative_launch_medians']}/{value['launches']} "
              f"CI={value['launch_median_bootstrap_95_ci']}")
    print(f"decision={result['decision']}")


if __name__ == "__main__":
    main()
