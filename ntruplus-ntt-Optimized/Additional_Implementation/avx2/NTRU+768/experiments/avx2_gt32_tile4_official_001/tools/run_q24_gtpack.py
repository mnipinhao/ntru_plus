#!/usr/bin/env python3
"""Measure recovered-r centered-SoA Q24 GT-pack in the full decap caller."""

import argparse
import json
import math
import random
import statistics
import subprocess
from pathlib import Path


def median_mad(values: list[float]) -> tuple[float, float]:
    median = statistics.median(values)
    mad = statistics.median(abs(value - median) for value in values)
    return median, mad


def run_launch(binary: Path, iterations: int) -> dict[str, object]:
    command = [str(binary), str(iterations), "gtpack"]
    process = subprocess.run(command, check=True, text=True,
                             capture_output=True)
    records = []
    valid = False
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            valid = ("correctness=byte-exact-valid-decap" in line
                     and "scope=recovered-r-centered-soa-q24-gt-pack" in line)
        elif fields[0] == "GTPACK_SAMPLE":
            records.append({
                "sample": int(fields[1]),
                "unpack_only_tsc": float(fields[2]),
                "gt_unpack_pack_tsc": float(fields[3]),
                "gt_pack_delta_tsc": float(fields[4]),
            })
    if not valid or len(records) != 20:
        raise RuntimeError(f"invalid benchmark output from {binary}")
    result: dict[str, object] = {"command": command, "raw": records}
    for field in ("unpack_only_tsc", "gt_unpack_pack_tsc",
                  "gt_pack_delta_tsc"):
        median, mad = median_mad([record[field] for record in records])
        result[field] = {"median": median, "mad": mad}
    result["gt_pack_wins"] = sum(record["gt_pack_delta_tsc"] < 0
                                  for record in records)
    return result


def bootstrap_median_ci(values: list[float], resamples: int,
                        seed: int) -> dict[str, float | int]:
    generator = random.Random(seed)
    count = len(values)
    estimates = sorted(statistics.median(
        values[generator.randrange(count)] for _ in range(count))
        for _ in range(resamples))
    lower_index = max(0, math.floor(0.025 * resamples))
    upper_index = min(resamples - 1, math.ceil(0.975 * resamples) - 1)
    return {
        "confidence": 0.95,
        "resamples": resamples,
        "seed": seed,
        "lower_tsc": estimates[lower_index],
        "upper_tsc": estimates[upper_index],
    }


def summarize(launches: list[dict[str, object]], resamples: int,
              seed: int) -> dict[str, object]:
    launch_deltas = [launch["gt_pack_delta_tsc"]["median"]
                     for launch in launches]
    delta, delta_mad = median_mad(launch_deltas)
    control, control_mad = median_mad(
        [launch["unpack_only_tsc"]["median"] for launch in launches])
    candidate, candidate_mad = median_mad(
        [launch["gt_unpack_pack_tsc"]["median"] for launch in launches])
    records = [record for launch in launches for record in launch["raw"]]
    return {
        "hierarchical_launch_medians": {
            "unpack_only_tsc": {"median": control, "mad": control_mad},
            "gt_unpack_pack_tsc": {"median": candidate,
                                   "mad": candidate_mad},
            "gt_pack_delta_tsc": {"median": delta, "mad": delta_mad},
        },
        "negative_delta_launches": sum(value < 0 for value in launch_deltas),
        "negative_delta_launch_fraction": (
            sum(value < 0 for value in launch_deltas) / len(launch_deltas)),
        "launch_median_bootstrap_95ci": bootstrap_median_ci(
            launch_deltas, resamples, seed),
        "launches": len(launches),
        "sample_wins": sum(record["gt_pack_delta_tsc"] < 0
                           for record in records),
        "samples": len(records),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--launches", type=int, default=48)
    parser.add_argument("--bootstrap-resamples", type=int, default=100000)
    parser.add_argument("--bootstrap-seed", type=int, default=240768)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    placements = {}
    for placement_index, (name, binary) in enumerate((
            ("normal", args.binary),
            ("reversed", args.reversed_binary))):
        launches = [run_launch(binary, args.iterations)
                    for _ in range(args.launches)]
        placements[name] = {
            "launch_data": launches,
            "summary": summarize(launches, args.bootstrap_resamples,
                                 args.bootstrap_seed + placement_index),
        }
    passed = all(
        placement["summary"]["negative_delta_launch_fraction"] >= 0.90
        and placement["summary"]["hierarchical_launch_medians"]
            ["gt_pack_delta_tsc"]["median"] <= -50.0
        and placement["summary"]["launch_median_bootstrap_95ci"]
            ["upper_tsc"] < 0.0
        for placement in placements.values())
    result = {
        "schema": "ntruplus768-gt32-q24-recovered-r-gtpack-hierarchical-v2",
        "experiment": "GT32-Q24-RECOVERED-R-GTPACK-001",
        "contract": {
            "input": "centered-canonical private BM SoA e=0",
            "output": "1152 byte Official canonical serialization",
            "control": "SoA to Official grouped bridge then Official pack",
            "candidate": "direct Q24 GT-pack from private SoA",
        },
        "benchmark": {
            "iterations_per_sample": args.iterations,
            "samples_per_launch": 20,
            "launches_per_placement": args.launches,
            "cpu": 1,
            "unit": "TSC ticks per full decapsulation",
            "order": "same-binary paired AB/BA",
            "serious_100k": False,
            "primary_unit": "process launch paired median",
            "bootstrap_resamples": args.bootstrap_resamples,
        },
        "placements": placements,
        "continuation_gate": {
            "minimum_median_saving_tsc": 50,
            "minimum_negative_launch_fraction": 0.90,
            "bootstrap_95ci_upper_must_be_negative": True,
            "passed": passed,
        },
        "decision": ("promote-recovered-r-q24-gt-pack" if passed else
                     "do-not-promote-recovered-r-q24-gt-pack"),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for name, placement in placements.items():
        summary = placement["summary"]
        medians = summary["hierarchical_launch_medians"]
        print(f"{name}: unpack-only={medians['unpack_only_tsc']['median']:.3f} "
              f"GT-pack={medians['gt_unpack_pack_tsc']['median']:.3f} "
              f"delta={medians['gt_pack_delta_tsc']['median']:.3f} "
              f"negative-launches={summary['negative_delta_launches']}/"
              f"{summary['launches']} sample-wins={summary['sample_wins']}/"
              f"{summary['samples']} bootstrap95ci=["
              f"{summary['launch_median_bootstrap_95ci']['lower_tsc']:.3f},"
              f"{summary['launch_median_bootstrap_95ci']['upper_tsc']:.3f}]")
    print(f"decision={result['decision']}")


if __name__ == "__main__":
    main()
