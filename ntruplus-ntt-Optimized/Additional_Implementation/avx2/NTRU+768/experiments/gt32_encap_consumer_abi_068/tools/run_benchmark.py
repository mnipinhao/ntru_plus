#!/usr/bin/env python3
"""Pinned, paired multi-launch directional benchmark for experiment 068."""

from __future__ import annotations

import argparse
import json
import random
import statistics
import subprocess
from pathlib import Path


def bootstrap_ci(values: list[float], seed: int, samples: int = 100000) -> list[float]:
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
        parts = line.split()
        if not parts:
            continue
        if parts[0].endswith("_cycles"):
            cycles[parts[0][:-7]] = [int(value) for value in parts[1:]]
        elif parts[0].endswith("_address"):
            addresses[parts[0][:-8]] = parts[1]
    medians = {name: statistics.median(values) for name, values in cycles.items()}
    return {"placement": placement, "order": order, "medians": medians,
            "addresses": addresses}


def summarize(rows: list[dict], placement: str) -> dict:
    selected = [row for row in rows if row["placement"] == placement]
    deltas: dict[str, list[float]] = {"reference-control": [],
                                     "shared-reference": [],
                                     "inline-reference": []}
    for row in selected:
        med = row["medians"]
        deltas["reference-control"].append(med["reference"] - med["control"])
        deltas["shared-reference"].append(med["shared"] - med["reference"])
        deltas["inline-reference"].append(med["inline"] - med["reference"])
    return {
        name: {"launch_deltas": values, "median": statistics.median(values),
               "wins": sum(value < 0 for value in values),
               "launches": len(values),
               "bootstrap_95_ci": bootstrap_ci(values, 0x068000 + index)}
        for index, (name, values) in enumerate(deltas.items())
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--launches", type=int, default=16)
    parser.add_argument("--cpu", type=int, default=1)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    rows = []
    for launch in range(args.launches):
        order = "0123" if launch % 2 == 0 else "3210"
        for placement in ("normal", "reversed"):
            rows.append(one(args.binary, placement, order, args.cpu))
    result = {
        "schema": "ntruplus768-gt32-encap-consumer-abi-068-benchmark-v1",
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
