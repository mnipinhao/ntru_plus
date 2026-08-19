#!/usr/bin/env python3
"""Run normal/reversed same-ELF SUPERcop-style 032 gates."""

from __future__ import annotations

import argparse
import json
import os
import random
import statistics
import subprocess
from pathlib import Path


def stabilized_q2(values: list[int]) -> float:
    expanded = sorted(value for value in values for _ in range(8))
    n = len(values)
    return sum(expanded[3 * n:5 * n]) / (2 * n)


def bootstrap_median_ci(values: list[float], samples: int = 100000) -> list[float]:
    rng = random.Random(20260819)
    estimates = sorted(statistics.median(rng.choices(values, k=len(values)))
                       for _ in range(samples))
    return [estimates[int(samples * 0.025)], estimates[int(samples * 0.975)]]


def parse_output(text: str) -> dict[str, object]:
    result: dict[str, object] = {}
    scalar = {"cpucycles_implementation", "placement",
              "local_control_address", "local_candidate_address",
              "full_control_address", "full_candidate_address", "sink"}
    for line in text.splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[0].endswith("_cycles"):
            result[fields[0]] = [int(value) for value in fields[1:]]
        elif fields[0] in scalar:
            result[fields[0]] = fields[1]
    if result.get("cpucycles_implementation") != "default-perfevent":
        raise RuntimeError(f"unexpected cycle backend: {result}")
    for region in ("local", "full"):
        for variant in ("control", "candidate"):
            key = f"{region}_{variant}_cycles"
            if len(result.get(key, [])) != 96:
                raise RuntimeError(f"incomplete {key}: {result}")
    return result


def summarize(entries: list[dict[str, object]], region: str) -> dict[str, object]:
    deltas = [float(entry[f"{region}_delta_core_cycles"]) for entry in entries]
    median_delta = statistics.median(deltas)
    control = statistics.median(
        float(entry[f"{region}_control_q2_core_cycles"]) for entry in entries)
    return {
        "control_median_q2_core_cycles": control,
        "candidate_median_q2_core_cycles": statistics.median(
            float(entry[f"{region}_candidate_q2_core_cycles"])
            for entry in entries),
        "paired_launch_median_delta_core_cycles": median_delta,
        "paired_launch_median_delta_percent": 100.0 * median_delta / control,
        "paired_delta_mad_core_cycles": statistics.median(
            abs(value - median_delta) for value in deltas),
        "bootstrap_median_95ci_core_cycles": bootstrap_median_ci(deltas),
        "candidate_favorable_launches": sum(value < 0 for value in deltas),
        "ab_median_delta_core_cycles": statistics.median(deltas[0::2]),
        "ba_median_delta_core_cycles": statistics.median(deltas[1::2]),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--launches", type=int, default=16)
    args = parser.parse_args()
    allowed = sorted(os.sched_getaffinity(0))
    if not allowed:
        raise RuntimeError("no CPU available for affinity pinning")
    cpu = allowed[0]
    all_results: dict[str, object] = {}
    for placement in ("normal", "reversed"):
        entries = []
        for launch in range(args.launches):
            order = "AB" if launch % 2 == 0 else "BA"

            def pin() -> None:
                os.sched_setaffinity(0, {cpu})

            completed = subprocess.run(
                [str(args.binary.resolve()), placement, order], check=True,
                capture_output=True, text=True, preexec_fn=pin)
            parsed = parse_output(completed.stdout)
            entry: dict[str, object] = {"launch": launch + 1, "order": order}
            for region in ("local", "full"):
                control = stabilized_q2(parsed[f"{region}_control_cycles"])
                candidate = stabilized_q2(parsed[f"{region}_candidate_cycles"])
                entry[f"{region}_control_q2_core_cycles"] = control
                entry[f"{region}_candidate_q2_core_cycles"] = candidate
                entry[f"{region}_delta_core_cycles"] = candidate - control
            for key in ("local_control_address", "local_candidate_address",
                        "full_control_address", "full_candidate_address"):
                entry[key] = parsed[key]
            entries.append(entry)
        all_results[placement] = {
            "local": summarize(entries, "local"),
            "full": summarize(entries, "full"),
            "launch_results": entries,
        }
    result = {
        "schema": "gt32-encap-b3-addm-032-supercop-style-v1",
        "method": "33 consecutive cpucycles timestamps; 32 adjacent differences; 3 loops; stabilized Q2",
        "cycle_backend": "default-perfevent/PERF_COUNT_HW_CPU_CYCLES",
        "pinned_cpu": cpu,
        "fixed_elf": str(args.binary.resolve()),
        "launches_per_placement": args.launches,
        "observations_per_variant_per_launch": 96,
        "placements": all_results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({name: {region: data[region]
                             for region in ("local", "full")}
                      for name, data in all_results.items()},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
