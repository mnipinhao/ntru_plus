#!/usr/bin/env python3
import argparse
import json
import os
import random
import statistics
import subprocess
from pathlib import Path

PROFILES = ("p0", "p1", "p2")
REGIONS = ("cbd", "rprod", "b3", "full")
ORDERS = ("012", "120", "201", "210", "021", "102")


def stabilized_q2(values):
    expanded = sorted(value for value in values for _ in range(8))
    count = len(values)
    return sum(expanded[3 * count:5 * count]) / (2 * count)


def bootstrap(values, seed):
    rng = random.Random(seed)
    samples = sorted(statistics.median(rng.choices(values, k=len(values)))
                     for _ in range(30000))
    return [samples[749], samples[29249]]


def launch(binary, order, cpu):
    completed = subprocess.run([str(binary.resolve()), order], check=True,
                               text=True, capture_output=True,
                               preexec_fn=lambda: os.sched_setaffinity(0, {cpu}))
    result = {}
    for line in completed.stdout.splitlines():
        fields = line.split()
        if fields and fields[0].endswith("_cycles"):
            result[fields[0].removesuffix("_cycles")] = [int(x) for x in fields[1:]]
    expected = {f"{profile}_{region}" for profile in PROFILES for region in REGIONS}
    if set(result) != expected or any(len(values) != 96 for values in result.values()):
        raise RuntimeError((result.keys(), completed.stderr))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--launches", type=int, default=48)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--cpu", type=int, default=1)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    for index in range(args.warmup):
        launch(args.binary, ORDERS[index % len(ORDERS)], args.cpu)
    rows = []
    for index in range(args.launches):
        order = ORDERS[index % len(ORDERS)]
        values = launch(args.binary, order, args.cpu)
        rows.append({
            "launch": index + 1,
            "order": order,
            "q2": {key: stabilized_q2(value) for key, value in values.items()},
        })
    comparisons = {}
    for profile_index, profile in enumerate(("p1", "p2"), 1):
        comparisons[profile] = {}
        for region_index, region in enumerate(REGIONS):
            deltas = [row["q2"][f"{profile}_{region}"]
                      - row["q2"][f"p0_{region}"] for row in rows]
            comparisons[profile][region] = {
                "median_delta_core_cycles": statistics.median(deltas),
                "ci95": bootstrap(deltas, 0x5600 + 10 * profile_index + region_index),
                "favorable_launches": sum(value < 0 for value in deltas),
                "launches": len(deltas),
                "deltas": deltas,
            }
    output = {
        "schema": "gt32-encap-data-geometry-056-v1",
        "cpu": args.cpu,
        "launches": args.launches,
        "profiles": {
            "p0": {"h": 0, "r": 1, "m": 2, "c": 3, "work": 4},
            "p1": {"h": 0, "r": 1, "m": 2, "c": 4, "work": 3},
            "p2": {"h": 1, "r": 2, "m": 3, "c": 4, "work": 0},
        },
        "comparisons_vs_p0": comparisons,
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(comparisons, indent=2))


if __name__ == "__main__":
    main()
