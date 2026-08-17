#!/usr/bin/env python3
"""Two-placement launch-level gate for Q24 Decode2 -> scale-B3 streaming."""

import argparse
import json
import math
import random
import statistics
import subprocess
from pathlib import Path


def median_mad(values: list[float]) -> dict[str, float]:
    median = statistics.median(values)
    return {"median": median,
            "mad": statistics.median(abs(value - median)
                                     for value in values)}


def bootstrap_ci(values: list[float], seed: int,
                 resamples: int = 20000) -> list[float]:
    rng = random.Random(seed)
    medians = sorted(statistics.median([rng.choice(values)
                                        for _ in values])
                     for _ in range(resamples))
    return [medians[int(0.025 * (resamples - 1))],
            medians[int(0.975 * (resamples - 1))]]


def run_launch(binary: Path, iterations: int) -> list[float]:
    process = subprocess.run([str(binary), str(iterations)], check=True,
                             text=True, capture_output=True)
    valid = False
    values: list[float] = []
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            valid = ("scope=q24-decode2-b3-frontier" in line
                     and "materialized-inputs-candidate=0" in line
                     and "b3-arithmetic=unchanged" in line)
        elif fields[0] == "SAMPLE" and fields[1] == "decode2_b3":
            values.append(float(fields[5]))
    if not valid or len(values) != 20:
        raise RuntimeError(f"invalid benchmark output from {binary}")
    return values


def summarize(binary: Path, iterations: int, launches: int,
              seed: int) -> dict:
    launch_values = [run_launch(binary, iterations) for _ in range(launches)]
    pooled = [value for launch in launch_values for value in launch]
    launch_medians = [statistics.median(launch) for launch in launch_values]
    return {
        "binary": str(binary),
        "paired_delta": median_mad(pooled),
        "wins": sum(value < 0 for value in pooled),
        "samples": len(pooled),
        "launch_medians": launch_medians,
        "negative_launch_medians": sum(value < 0
                                         for value in launch_medians),
        "launches": launches,
        "launch_median_bootstrap_95_ci": bootstrap_ci(launch_medians, seed),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--launches", type=int, default=16)
    parser.add_argument("--output", type=Path,
                        default=Path("results/tile4-q24-b3-frontier-short.json"))
    args = parser.parse_args()

    placements = {
        "normal": summarize(args.binary, args.iterations, args.launches,
                            0xc1f100),
        "reversed": summarize(args.reversed_binary, args.iterations,
                              args.launches, 0xc1f200),
    }
    minimum_negative = math.ceil(0.90 * args.launches)
    passed = all(
        -value["paired_delta"]["median"] >= 30.0
        and value["negative_launch_medians"] >= minimum_negative
        and value["launch_median_bootstrap_95_ci"][1] < 0.0
        for value in placements.values()
    )
    result = {
        "schema": "ntruplus768-gt32-q24-b3-frontier-benchmark-v1",
        "experiment": "GT32-Q24-DECODE2-B3-FRONTIER-001",
        "control": "Q24 Decode(c,f) -> two full private-SoA stores -> scale-B3 reload",
        "candidate": "four Q24 packets per operand -> register SoA block -> unchanged scale-B3",
        "method": {
            "iterations_per_sample": args.iterations,
            "samples_per_launch": 20,
            "launches_per_placement": args.launches,
            "order": "paired AB/BA",
            "primary_unit": "launch median",
        },
        "placements": placements,
        "continuation_gate": {
            "minimum_saving_tsc": 30.0,
            "minimum_negative_launch_medians": minimum_negative,
            "bootstrap_upper_must_be_negative": True,
            "pass": passed,
        },
        "decision": ("continue-first-product-consumer-gate" if passed else
                     "hard-stop-decap-micro-optimization-shift-keygen-encap"),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for placement, value in placements.items():
        print(f"{placement}: delta={value['paired_delta']['median']:.3f} "
              f"wins={value['wins']}/{value['samples']} "
              f"launches={value['negative_launch_medians']}/"
              f"{value['launches']} "
              f"CI={value['launch_median_bootstrap_95_ci']}")
    print(f"decision={result['decision']}")


if __name__ == "__main__":
    main()
