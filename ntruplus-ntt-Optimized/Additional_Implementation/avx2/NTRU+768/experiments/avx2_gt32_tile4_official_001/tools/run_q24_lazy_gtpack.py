#!/usr/bin/env python3
"""Hierarchical launch-level gate for the final-check lazy10788 GT-pack."""

import argparse
import json
import math
import random
import statistics
import subprocess
from pathlib import Path


def median_mad(values):
    median = statistics.median(values)
    return median, statistics.median(abs(value - median) for value in values)


def bootstrap_median_ci(values, resamples, seed):
    generator = random.Random(seed)
    count = len(values)
    estimates = sorted(statistics.median(
        values[generator.randrange(count)] for _ in range(count))
        for _ in range(resamples))
    return {
        "confidence": 0.95,
        "resamples": resamples,
        "seed": seed,
        "lower_tsc": estimates[max(0, math.floor(0.025 * resamples))],
        "upper_tsc": estimates[min(resamples - 1,
                                     math.ceil(0.975 * resamples) - 1)],
    }


def run_launch(binary, iterations):
    command = [str(binary), str(iterations), "lazy-pack"]
    process = subprocess.run(command, check=True, text=True,
                             capture_output=True)
    records = []
    valid = False
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            valid = ("correctness=byte-exact-valid-decap" in line
                     and "scope=final-check-lazy10788-q24-gt-pack" in line)
        elif fields[0] == "LAZY_GTPACK_SAMPLE":
            records.append({
                "sample": int(fields[1]),
                "centered_control_tsc": float(fields[2]),
                "lazy_candidate_tsc": float(fields[3]),
                "lazy_delta_tsc": float(fields[4]),
            })
    if not valid or len(records) != 20:
        raise RuntimeError(f"invalid lazy GT-pack output from {binary}")
    result = {"command": command, "raw": records}
    for field in ("centered_control_tsc", "lazy_candidate_tsc",
                  "lazy_delta_tsc"):
        median, mad = median_mad([record[field] for record in records])
        result[field] = {"median": median, "mad": mad}
    result["lazy_wins"] = sum(record["lazy_delta_tsc"] < 0
                              for record in records)
    return result


def summarize(launches, resamples, seed):
    launch_deltas = [launch["lazy_delta_tsc"]["median"]
                     for launch in launches]
    records = [record for launch in launches for record in launch["raw"]]
    summary = {"launches": len(launches), "samples": len(records)}
    for field in ("centered_control_tsc", "lazy_candidate_tsc",
                  "lazy_delta_tsc"):
        median, mad = median_mad([launch[field]["median"]
                                  for launch in launches])
        summary[field] = {"median": median, "mad": mad}
    summary.update({
        "negative_delta_launches": sum(value < 0 for value in launch_deltas),
        "negative_delta_launch_fraction": (
            sum(value < 0 for value in launch_deltas) / len(launch_deltas)),
        "launch_median_bootstrap_95ci": bootstrap_median_ci(
            launch_deltas, resamples, seed),
        "sample_wins": sum(record["lazy_delta_tsc"] < 0
                           for record in records),
    })
    return summary


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--launches", type=int, default=48)
    parser.add_argument("--bootstrap-resamples", type=int, default=100000)
    parser.add_argument("--bootstrap-seed", type=int, default=107880)
    parser.add_argument("--minimum-saving-tsc", type=float, default=30.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    placements = {}
    for index, (name, binary) in enumerate((
            ("normal", args.binary),
            ("reversed", args.reversed_binary))):
        launches = [run_launch(binary, args.iterations)
                    for _ in range(args.launches)]
        placements[name] = {
            "launch_data": launches,
            "summary": summarize(launches, args.bootstrap_resamples,
                                 args.bootstrap_seed + index),
        }
    passed = all(
        data["summary"]["negative_delta_launch_fraction"] >= 0.90
        and data["summary"]["lazy_delta_tsc"]["median"]
            <= -args.minimum_saving_tsc
        and data["summary"]["launch_median_bootstrap_95ci"]["upper_tsc"] < 0
        for data in placements.values())
    result = {
        "schema": "ntruplus768-gt32-q24-lazy10788-gtpack-hierarchical-v1",
        "experiment": "GT32-Q24-LAZY10788-GTPACK-001",
        "contract": {
            "input": "private BM SoA e=0, inclusive |word| <= 10788",
            "output": "Official canonical 1152-byte serialization",
            "control": "N5 private SoA -> Official grouped bridge -> pack",
            "candidate": "N5 private SoA -> fused reduce -> Q24 GT-pack",
            "centered_q24_gtpack_body_unchanged": True,
        },
        "benchmark": {
            "iterations_per_sample": args.iterations,
            "samples_per_launch": 20,
            "launches_per_placement": args.launches,
            "cpu": 1,
            "order": "same-binary paired AB/BA",
            "primary_unit": "process-launch paired median",
            "serious_100k": False,
        },
        "placements": placements,
        "promotion_gate": {
            "minimum_negative_launch_fraction": 0.90,
            "minimum_median_saving_tsc": args.minimum_saving_tsc,
            "bootstrap_95ci_upper_must_be_negative": True,
            "pmu_core_cycle_corroboration_required_separately": True,
            "tsc_gate_passed": passed,
        },
        "decision": "tsc-pass-pending-pmu" if passed else "do-not-promote",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for name, data in placements.items():
        summary = data["summary"]
        ci = summary["launch_median_bootstrap_95ci"]
        print(f"{name}: control={summary['centered_control_tsc']['median']:.3f} "
              f"lazy={summary['lazy_candidate_tsc']['median']:.3f} "
              f"delta={summary['lazy_delta_tsc']['median']:.3f} "
              f"negative-launches={summary['negative_delta_launches']}/"
              f"{summary['launches']} sample-wins={summary['sample_wins']}/"
              f"{summary['samples']} bootstrap95ci=[{ci['lower_tsc']:.3f},"
              f"{ci['upper_tsc']:.3f}]")
    print(f"decision={result['decision']}")


if __name__ == "__main__":
    main()
