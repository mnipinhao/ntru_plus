#!/usr/bin/env python3
"""Multi-launch whole-only runner for the global physical-layout probe."""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from pathlib import Path


METRICS = ("tsc", "core_cycles", "instructions", "ref_cycles")


def robust(values: list[float]) -> dict[str, float]:
    median = statistics.median(values)
    return {
        "median": median,
        "mad": statistics.median(abs(value - median) for value in values),
    }


def launch(binary: Path, iterations: int) -> dict[str, object]:
    process = subprocess.run([str(binary), str(iterations)], check=True,
                             text=True, capture_output=True)
    deltas = {metric: [] for metric in METRICS}
    controls = {metric: [] for metric in METRICS}
    candidates = {metric: [] for metric in METRICS}
    pmu = "unknown"
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            for field in fields[1:]:
                if field.startswith("pmu="):
                    pmu = field.split("=", 1)[1]
        if fields[0] != "SAMPLE":
            continue
        values = [float(value) for value in fields[3:]]
        for index, metric in enumerate(METRICS):
            controls[metric].append(values[3 * index])
            candidates[metric].append(values[3 * index + 1])
            deltas[metric].append(values[3 * index + 2])
    if any(len(values) != 20 for values in deltas.values()):
        raise RuntimeError(f"incomplete launch: {binary}")
    return {
        "pmu": pmu,
        "metrics": {metric: robust(values) for metric, values in deltas.items()},
        "control_metrics": {
            metric: robust(values) for metric, values in controls.items()},
        "candidate_metrics": {
            metric: robust(values) for metric, values in candidates.items()},
        "candidate_wins_tsc": sum(value < 0 for value in deltas["tsc"]),
        "candidate_wins_core_cycles": sum(
            value < 0 for value in deltas["core_cycles"]),
    }


def placement(binary: Path, launches: int, iterations: int) -> dict[str, object]:
    records = [launch(binary, iterations) for _ in range(launches)]
    launch_medians = {
        metric: [record["metrics"][metric]["median"] for record in records]
        for metric in METRICS
    }
    control_launch_medians = {
        metric: [record["control_metrics"][metric]["median"]
                 for record in records]
        for metric in METRICS
    }
    candidate_launch_medians = {
        metric: [record["candidate_metrics"][metric]["median"]
                 for record in records]
        for metric in METRICS
    }
    return {
        "binary": str(binary),
        "launches": records,
        "launch_median_summary": {
            metric: robust(values) for metric, values in launch_medians.items()
        },
        "control_launch_median_summary": {
            metric: robust(values)
            for metric, values in control_launch_medians.items()
        },
        "candidate_launch_median_summary": {
            metric: robust(values)
            for metric, values in candidate_launch_medians.items()
        },
        "negative_launch_medians": {
            metric: sum(value < 0 for value in values)
            for metric, values in launch_medians.items()
        },
        "aggregate_candidate_wins_tsc": sum(
            record["candidate_wins_tsc"] for record in records),
        "aggregate_candidate_wins_core_cycles": sum(
            record["candidate_wins_core_cycles"] for record in records),
        "total_paired_samples": 20 * launches,
        "all_launches_at_least_18_of_20_tsc_wins": all(
            record["candidate_wins_tsc"] >= 18 for record in records),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=5000)
    parser.add_argument("--launches", type=int, default=4)
    parser.add_argument("--comparison", choices=("current-gt", "official-main"),
                        default="current-gt")
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    placements = {
        "normal": placement(args.binary, args.launches, args.iterations),
        "reversed": placement(args.reversed_binary, args.launches,
                              args.iterations),
    }
    tsc_pass = all(
        result["launch_median_summary"]["tsc"]["median"] <= -20.0
        and result["negative_launch_medians"]["tsc"] == args.launches
        and result["aggregate_candidate_wins_tsc"]
            >= int(0.9 * result["total_paired_samples"])
        for result in placements.values())
    pmu_available = all(
        launch_result["pmu"] == "core"
        for result in placements.values()
        for launch_result in result["launches"])
    core_pass = pmu_available and all(
        result["launch_median_summary"]["core_cycles"]["median"] < 0.0
        and result["negative_launch_medians"]["core_cycles"] == args.launches
        for result in placements.values())
    if tsc_pass and core_pass:
        decision = ("serious-qualified-private-caller-integration"
                    if args.iterations >= 100000 else
                    "continue-to-100k-serious")
    else:
        decision = "stop-global-physical-architecture"
    output = {
        "schema": "ntruplus768-gt32-global-physical-whole-short-v1",
        "experiment": "GT32-GLOBAL-PHYSICAL-001",
        "scope": "coefficient-input 2F+B3+inverse-core+T9 coefficient-output; whole-only",
        "control": ("Official Main poly_ntt x2 + basemul_scale + invntt_scale"
                    if args.comparison == "official-main" else
                    "frontend + production private-SoA Forward x2 + B3-to-AoS + I1 AoS + T9"),
        "candidate": ("typed GT frontend + global Forward-to-M x2 + B3-to-M + global inverse M-to-AoS + T9"
                      if args.comparison == "official-main" else
                      "same frontend + global Forward-to-M x2 + same B3-to-M + global inverse M-to-AoS + T9"),
        "comparison": args.comparison,
        "benchmark": {
            "iterations": args.iterations,
            "samples_per_launch": 20,
            "launches": args.launches,
            "ordering": "paired AB/BA",
            "placements": ["normal", "reversed-link-order"],
            "primary": "region-scoped core cycles when perf_event is available",
            "secondary": "TSC",
            "hierarchical_gate": "all launch medians negative, aggregate paired wins >=90%, placement median saving >=20 TSC",
        },
        "correctness": "1000-trial exact Forward/inverse/core-whole and alias pass; each benchmark launch checks exact coefficient output",
        "placements": placements,
        "decision": decision,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    for name, result in placements.items():
        summaries = result["launch_median_summary"]
        print(f"{name}: TSC={summaries['tsc']['median']:.3f} "
              f"MAD={summaries['tsc']['mad']:.3f}; "
              f"core={summaries['core_cycles']['median']:.3f}; "
              f"instructions={summaries['instructions']['median']:.3f}; "
              f"18/20-all={result['all_launches_at_least_18_of_20_tsc_wins']}")
        print(f"  control/candidate TSC="
              f"{result['control_launch_median_summary']['tsc']['median']:.3f}/"
              f"{result['candidate_launch_median_summary']['tsc']['median']:.3f}")
    print(f"decision={decision}")


if __name__ == "__main__":
    main()
