#!/usr/bin/env python3
"""Run the benchmark-only crepmod3 sidecar-tap gate."""

import argparse
import json
import random
import statistics
import subprocess
from pathlib import Path


GATES = (
    "producer_s1", "producer_s2", "sotp",
    "crep_sotp_s1", "crep_sotp_s2",
    "crep_n5_sotp_s1", "crep_n5_sotp_s2",
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
            valid = ("correctness=crep-sidecar-byte-exact" in line
                     and "full_m_materialized=1" in line
                     and "n5_path=unchanged" in line)
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
                        default=Path("results/tile4-crep-sidecar-short.json"))
    args = parser.parse_args()

    placements = {
        "normal": summarize(args.binary, args.iterations, args.launches,
                            args.bootstrap_resamples, 0xc2a200),
        "reversed": summarize(args.reversed_binary, args.iterations,
                              args.launches, args.bootstrap_resamples,
                              0xc2a300),
    }
    candidates = ("crep_n5_sotp_s1", "crep_n5_sotp_s2")
    continuation = []
    for candidate in candidates:
        passed = []
        for placement in ("normal", "reversed"):
            gate = placements[placement]["gates"][candidate]
            saving = -gate["paired_delta"]["median"]
            upper = gate["launch_median_bootstrap_95_ci"][1]
            producer_name = "producer_s1" if candidate.endswith("s1") \
                else "producer_s2"
            producer = placements[placement]["gates"][producer_name]
            producer_cost = producer["paired_delta"]["median"]
            passed.append(saving >= 30.0 and upper < 0.0
                          and producer_cost < 50.0)
        if all(passed):
            continuation.append(candidate)

    result = {
        "schema": "ntruplus768-gt32-crep-sidecar-benchmark-v1",
        "experiment": "GT32-CREPMOD3-SIDECAR-TAP-001",
        "method": {
            "iterations_per_sample": args.iterations,
            "samples_per_launch": 20,
            "launches_per_placement": args.launches,
            "order": "paired AB/BA",
            "primary_unit": "launch median",
            "full_m_materialized": True,
            "n5_path": "unchanged",
        },
        "placements": placements,
        "continuation_gate": {
            "minimum_full_region_saving_tsc": 30.0,
            "maximum_producer_cost_tsc": 50.0,
            "engineering_target_producer_cost_tsc": 40.0,
            "bootstrap_upper_must_be_negative": True,
            "passing_candidates": continuation,
        },
        "decision": ("continue-full-decap-integration" if continuation
                     else "hard-stop-below-sidecar-tap-gate"),
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
