#!/usr/bin/env python3
"""Launch-level KEM gate for the global-physical M-native inverse edge."""

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
    medians = sorted(
        statistics.median([rng.choice(values) for _ in values])
        for _ in range(resamples)
    )
    return [
        medians[int(0.025 * (resamples - 1))],
        medians[int(0.975 * (resamples - 1))],
    ]


def run_launch(binary: Path, iterations: int) -> dict[str, list[float]]:
    process = subprocess.run(
        [str(binary), str(iterations), "global-inverse"],
        check=True, text=True, capture_output=True)
    valid = False
    deltas = {"vs_current_q24": [], "vs_official": []}
    absolutes = {"official": [], "current_q24": [], "global_inverse": []}
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            valid = ("correctness=byte-exact-valid-decap" in line
                     and "scope=full-decap-global-inverse" in line)
        elif fields[0] == "GLOBAL_SAMPLE":
            absolutes["official"].append(float(fields[2]))
            absolutes["current_q24"].append(float(fields[3]))
            absolutes["global_inverse"].append(float(fields[4]))
            deltas["vs_current_q24"].append(float(fields[5]))
            deltas["vs_official"].append(float(fields[6]))
    if (not valid
            or any(len(values) != 20 for values in deltas.values())
            or any(len(values) != 20 for values in absolutes.values())):
        raise RuntimeError(f"invalid benchmark output from {binary}")
    return {"deltas": deltas, "absolutes": absolutes}


def summarize(binary: Path, iterations: int, launches: int,
              seed: int) -> dict:
    raw = [run_launch(binary, iterations) for _ in range(launches)]
    result = {"binary": str(binary), "deltas": {}, "absolutes": {}}
    for index, name in enumerate(("vs_current_q24", "vs_official")):
        launch_values = [launch["deltas"][name] for launch in raw]
        pooled = [value for launch in launch_values for value in launch]
        launch_medians = [statistics.median(launch) for launch in launch_values]
        result["deltas"][name] = {
            "paired_delta_tsc": median_mad(pooled),
            "wins": sum(value < 0 for value in pooled),
            "samples": len(pooled),
            "launch_medians": launch_medians,
            "negative_launch_medians": sum(value < 0
                                             for value in launch_medians),
            "launches": launches,
            "launch_median_bootstrap_95_ci": bootstrap_ci(
                launch_medians, seed + index),
        }
    for name in ("official", "current_q24", "global_inverse"):
        launch_medians = [statistics.median(launch["absolutes"][name])
                          for launch in raw]
        result["absolutes"][name] = {
            "launch_median_tsc": median_mad(launch_medians),
            "launch_medians": launch_medians,
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=10000)
    parser.add_argument("--launches", type=int, default=8)
    parser.add_argument("--output", type=Path,
                        default=Path(
                            "results/tile4-global-inverse-decap-short.json"))
    args = parser.parse_args()

    placements = {
        "normal": summarize(args.binary, args.iterations, args.launches,
                            0x61A100),
        "reversed": summarize(args.reversed_binary, args.iterations,
                              args.launches, 0x61A200),
    }
    current = [value["deltas"]["vs_current_q24"]
               for value in placements.values()]
    passed = all(
        result["paired_delta_tsc"]["median"] < 0.0
        and result["launch_median_bootstrap_95_ci"][1] < 0.0
        for result in current
    )
    result = {
        "schema": "ntruplus768-gt32-global-inverse-kem-v1",
        "experiment": "GT32-GLOBAL-PHYSICAL-KEM-DECAP-001",
        "control": "promoted Q24 decap with B3 SoA-to-AoS plus I1",
        "candidate": "Q24 decap with B3 SoA-to-M plus global M-to-AoS inverse",
        "method": {
            "iterations_per_sample": args.iterations,
            "samples_per_launch": 20,
            "launches_per_placement": args.launches,
            "order": "paired ABC/CBA",
            "primary_unit": "process-launch paired median",
        },
        "placements": placements,
        "continuation_gate": {
            "both_placements_negative": True,
            "bootstrap_upper_must_be_negative": True,
            "pass": passed,
        },
        "decision": ("continue-correctness-and-pmu-gate" if passed
                     else "keep-opt-in-no-kem-promotion"),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for placement, value in placements.items():
        current_delta = value["deltas"]["vs_current_q24"]
        official_delta = value["deltas"]["vs_official"]
        print(
            f"{placement}: vs-current="
            f"{current_delta['paired_delta_tsc']['median']:.3f} TSC "
            f"wins={current_delta['wins']}/{current_delta['samples']} "
            f"launches={current_delta['negative_launch_medians']}/"
            f"{current_delta['launches']} "
            f"CI={current_delta['launch_median_bootstrap_95_ci']}; "
            f"vs-official={official_delta['paired_delta_tsc']['median']:.3f} TSC"
        )
    print(f"decision={result['decision']}")


if __name__ == "__main__":
    main()
