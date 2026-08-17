#!/usr/bin/env python3
"""Run the benchmark-only C2 dual-consumer terminal gate."""

import argparse
import json
import random
import statistics
import subprocess
from pathlib import Path


GATES = (
    "producer", "producer_b2", "producer_b4", "sotp",
    "dual_terminal", "dual_terminal_b2", "dual_terminal_b4",
)


def median_mad(values: list[float]) -> dict[str, float]:
    median = statistics.median(values)
    return {
        "median": median,
        "mad": statistics.median(abs(value - median) for value in values),
    }


def bootstrap_ci(values: list[float], resamples: int, seed: int) -> list[float]:
    rng = random.Random(seed)
    medians = []
    for _ in range(resamples):
        sample = [rng.choice(values) for _ in values]
        medians.append(statistics.median(sample))
    medians.sort()
    return [
        medians[int(0.025 * (resamples - 1))],
        medians[int(0.975 * (resamples - 1))],
    ]


def run_launch(binary: Path, iterations: int) -> dict[str, list[float]]:
    process = subprocess.run(
        [str(binary), str(iterations)], check=True, text=True,
        capture_output=True)
    valid = False
    gates = {name: [] for name in GATES}
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            valid = ("correctness=dual-terminal-byte-exact" in line
                     and "full_m_materialized=0" in line)
        elif fields[0] == "SAMPLE":
            gates[fields[1]].append(float(fields[5]))
    if not valid or any(len(values) != 20 for values in gates.values()):
        raise RuntimeError(f"invalid output from {binary}")
    return gates


def summarize(binary: Path, iterations: int, launches: int,
              resamples: int, seed: int) -> dict:
    records = [run_launch(binary, iterations) for _ in range(launches)]
    gates = {}
    for gate_index, name in enumerate(GATES):
        all_deltas = [value for launch in records for value in launch[name]]
        launch_medians = [statistics.median(launch[name]) for launch in records]
        gates[name] = {
            "paired_delta": median_mad(all_deltas),
            "wins": sum(value < 0 for value in all_deltas),
            "samples": len(all_deltas),
            "launch_medians": launch_medians,
            "negative_launch_medians": sum(value < 0 for value in launch_medians),
            "launches": launches,
            "launch_median_bootstrap_95_ci": bootstrap_ci(
                launch_medians, resamples, seed + gate_index),
        }
    return {"binary": str(binary), "gates": gates}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--launches", type=int, default=8)
    parser.add_argument("--bootstrap-resamples", type=int, default=20000)
    parser.add_argument("--output", type=Path,
                        default=Path("results/tile4-dual-terminal-short.json"))
    args = parser.parse_args()

    placements = {
        "normal": summarize(args.binary, args.iterations, args.launches,
                            args.bootstrap_resamples, 0xd2a100),
        "reversed": summarize(args.reversed_binary, args.iterations,
                              args.launches, args.bootstrap_resamples,
                              0xd2a200),
    }
    candidates = ("dual_terminal_b2", "dual_terminal_b4")
    continuation = []
    for candidate in candidates:
        pass_placements = []
        for placement in ("normal", "reversed"):
            result = placements[placement]["gates"][candidate]
            saving = -result["paired_delta"]["median"]
            upper = result["launch_median_bootstrap_95_ci"][1]
            pass_placements.append(saving >= 30.0 and upper < 0.0)
        if all(pass_placements):
            continuation.append(candidate)

    result = {
        "schema": "ntruplus768-gt32-dual-terminal-benchmark-v1",
        "experiment": "GT32-C2-DUAL-CONSUMER-TERMINAL-001",
        "method": {
            "iterations_per_sample": args.iterations,
            "samples_per_launch": 20,
            "launches_per_placement": args.launches,
            "order": "paired AB/BA",
            "primary_unit": "launch median",
            "full_m_materialized": False,
        },
        "placements": placements,
        "continuation_gate": {
            "minimum_saving_tsc": 30.0,
            "bootstrap_upper_must_be_negative": True,
            "passing_candidates": continuation,
        },
        "decision": ("continue-pmu-and-caller-integration" if continuation
                     else "hard-stop-below-30-tsc-gate"),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "decision": result["decision"],
        "normal": {
            name: placements["normal"]["gates"][name]["paired_delta"]["median"]
            for name in candidates
        },
        "reversed": {
            name: placements["reversed"]["gates"][name]["paired_delta"]["median"]
            for name in candidates
        },
    }, indent=2))


if __name__ == "__main__":
    main()
