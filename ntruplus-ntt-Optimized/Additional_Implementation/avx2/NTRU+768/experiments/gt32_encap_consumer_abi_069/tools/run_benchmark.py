#!/usr/bin/env python3
"""Pinned paired multi-launch benchmark for clustered gate 069."""

from __future__ import annotations

import argparse
import json
import random
import statistics
import subprocess
from pathlib import Path


def bootstrap_ci(values: list[float], seed: int,
                 samples: int = 100000) -> list[float]:
    rng = random.Random(seed)
    medians = sorted(statistics.median(rng.choices(values, k=len(values)))
                     for _ in range(samples))
    return [medians[int(0.025 * samples)], medians[int(0.975 * samples)]]


def one(binary: Path, placement: str, order: str, cpu: int) -> dict:
    output = subprocess.check_output(
        ["taskset", "-c", str(cpu), str(binary), placement, order], text=True)
    cycles: dict[str, list[int]] = {}
    addresses: dict[str, str] = {}
    for line in output.splitlines():
        fields = line.split()
        if not fields:
            continue
        if fields[0].endswith("_cycles"):
            cycles[fields[0][:-7]] = [int(value) for value in fields[1:]]
        elif fields[0].endswith("_address"):
            addresses[fields[0][:-8]] = fields[1]
    return {
        "placement": placement,
        "order": order,
        "medians": {name: statistics.median(values)
                    for name, values in cycles.items()},
        "addresses": addresses,
    }


def summarize(rows: list[dict], placement: str) -> dict:
    selected = [row for row in rows if row["placement"] == placement]
    comparisons = {
        "reference-control": ("reference", "control"),
        "shared-reference": ("shared", "reference"),
        "inline-reference": ("inline", "reference"),
        "cluster3-reference": ("cluster3", "reference"),
        "cluster4-reference": ("cluster4", "reference"),
    }
    result = {}
    for index, (name, (candidate, control)) in enumerate(comparisons.items()):
        values = [row["medians"][candidate] - row["medians"][control]
                  for row in selected]
        result[name] = {
            "launch_deltas": values,
            "median": statistics.median(values),
            "wins": sum(value < 0 for value in values),
            "launches": len(values),
            "bootstrap_95_ci": bootstrap_ci(values, 0x069000 + index),
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--launches", type=int, default=16)
    parser.add_argument("--cpu", type=int, default=1)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    rows = []
    for launch in range(args.launches):
        order = "012345" if launch % 2 == 0 else "543210"
        for placement in ("normal", "reversed"):
            rows.append(one(args.binary, placement, order, args.cpu))
    result = {
        "schema": "ntruplus768-gt32-encap-consumer-abi-069-benchmark-v1",
        "cpu": args.cpu,
        "launches_per_placement": args.launches,
        "summary": {placement: summarize(rows, placement)
                    for placement in ("normal", "reversed")},
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result["summary"], indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
