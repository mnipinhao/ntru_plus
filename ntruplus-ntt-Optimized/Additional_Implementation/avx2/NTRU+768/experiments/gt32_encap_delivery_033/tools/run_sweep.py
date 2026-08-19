#!/usr/bin/env python3
"""Run the fixed-address B3-cage sweep with rotating A/B/C order."""

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


def parse(text: str) -> dict[str, object]:
    result: dict[str, object] = {}
    for line in text.splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[0].endswith("_cycles"):
            result[fields[0]] = [int(value) for value in fields[1:]]
        elif fields[0] in {"cpucycles_implementation", "A_address",
                           "B_address", "C_address", "B3_address", "sink"}:
            result[fields[0]] = fields[1]
    if result.get("cpucycles_implementation") != "default-perfevent":
        raise RuntimeError(f"unexpected cpucycles backend: {result}")
    for name in "ABC":
        if len(result.get(f"{name}_cycles", [])) != 96:
            raise RuntimeError(f"incomplete {name}: {result}")
    return result


def delta_summary(values: list[float]) -> dict[str, object]:
    median = statistics.median(values)
    return {
        "paired_launch_median_core_cycles": median,
        "favorable_launches": sum(value < 0 for value in values),
        "mad_core_cycles": statistics.median(abs(value - median)
                                               for value in values),
        "bootstrap_median_95ci_core_cycles": bootstrap_median_ci(values),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--launches", type=int, default=16)
    parser.add_argument("offsets", nargs="+", type=int)
    args = parser.parse_args()
    allowed = sorted(os.sched_getaffinity(0))
    if not allowed:
        raise RuntimeError("no CPU available")
    cpu = allowed[0]
    orders = ["ABC", "BCA", "CAB"]
    launch_results: dict[int, list[dict[str, object]]] = {
        offset: [] for offset in args.offsets
    }
    for launch in range(args.launches):
        # Rotate the offset order every round so code address is not aliased
        # with wall-clock drift, temperature, or background load.
        shift = launch % len(args.offsets)
        round_offsets = args.offsets[shift:] + args.offsets[:shift]
        for offset in round_offsets:
            binary = (args.build / f"bench_offset_{offset}").resolve()
            order = orders[launch % len(orders)]

            def pin() -> None:
                os.sched_setaffinity(0, {cpu})

            completed = subprocess.run([str(binary), order], check=True,
                                       capture_output=True, text=True,
                                       preexec_fn=pin)
            parsed = parse(completed.stdout)
            q2 = {name: stabilized_q2(parsed[f"{name}_cycles"])
                  for name in "ABC"}
            launch_results[offset].append({
                "launch": launch + 1,
                "order": order,
                "A_q2_core_cycles": q2["A"],
                "B_q2_core_cycles": q2["B"],
                "C_q2_core_cycles": q2["C"],
                "B_minus_A_core_cycles": q2["B"] - q2["A"],
                "C_minus_B_core_cycles": q2["C"] - q2["B"],
                "C_minus_A_core_cycles": q2["C"] - q2["A"],
                "addresses": {name: parsed[f"{name}_address"]
                              for name in ("A", "B", "C", "B3")},
            })
    variants: dict[str, object] = {}
    for offset in args.offsets:
        launches = launch_results[offset]
        variants[str(offset)] = {
            "B_minus_A": delta_summary([
                entry["B_minus_A_core_cycles"] for entry in launches]),
            "C_minus_B": delta_summary([
                entry["C_minus_B_core_cycles"] for entry in launches]),
            "C_minus_A": delta_summary([
                entry["C_minus_A_core_cycles"] for entry in launches]),
            "launch_results": launches,
        }
    incremental = {
        offset: variants[str(offset)]["C_minus_B"]
        ["paired_launch_median_core_cycles"] for offset in args.offsets
    }
    result = {
        "schema": "gt32-encap-delivery-033-address-sweep-v1",
        "method": "fixed non-PIE ELFs; 4096-byte candidate cage; SUPERcop adjacent cpucycles stabilized Q2",
        "pinned_cpu": cpu,
        "launches_per_offset": args.launches,
        "observations_per_variant_per_launch": 96,
        "A": "current GT deterministic Encap",
        "B": "031 four-polynomial Encap",
        "C": "031 plus 032 B3 final-store add-m",
        "incremental_C_minus_B_median_range": [min(incremental.values()),
                                                max(incremental.values())],
        "incremental_C_minus_B_span_core_cycles": (
            max(incremental.values()) - min(incremental.values())),
        "variants": variants,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({offset: {
        "B-A": variants[str(offset)]["B_minus_A"],
        "C-B": variants[str(offset)]["C_minus_B"],
    } for offset in args.offsets}, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
