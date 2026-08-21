#!/usr/bin/env python3
import argparse
import json
import os
import random
import statistics
import subprocess
from pathlib import Path

ORDERS = ("012", "120", "201", "210", "021", "102")


def q2(values):
    expanded = sorted(value for value in values for _ in range(8))
    n = len(values)
    return sum(expanded[3*n:5*n]) / (2*n)


def bootstrap(values, seed):
    rng = random.Random(seed)
    samples = sorted(statistics.median(rng.choices(values, k=len(values)))
                     for _ in range(30000))
    return [samples[749], samples[29249]]


def launch(binary, order, cpu):
    done = subprocess.run([str(binary.resolve()), order], check=True, text=True,
                          capture_output=True,
                          preexec_fn=lambda: os.sched_setaffinity(0, {cpu}))
    result = {}
    for line in done.stdout.splitlines():
        fields = line.split()
        if fields and fields[0].startswith("p") and fields[0].endswith("_cycles"):
            result[fields[0][:-7]] = [int(value) for value in fields[1:]]
    if set(result) != {"p0", "p1", "p2"} or any(len(v) != 96 for v in result.values()):
        raise RuntimeError((result, done.stderr))
    return {key: q2(value) for key, value in result.items()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--launches", type=int, default=48)
    parser.add_argument("--warmup", type=int, default=3)
    parser.add_argument("--cpu", type=int, default=1)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    for i in range(args.warmup):
        launch(args.binary, ORDERS[i % len(ORDERS)], args.cpu)
    rows = []
    for i in range(args.launches):
        order = ORDERS[i % len(ORDERS)]
        rows.append({"launch": i + 1, "order": order,
                     "q2": launch(args.binary, order, args.cpu)})
    comparisons = {}
    for index, (name, candidate, control) in enumerate((
            ("b_minus_a", "p1", "p0"),
            ("c_minus_a", "p2", "p0"),
            ("c_minus_b", "p2", "p1"))):
        values = [row["q2"][candidate] - row["q2"][control]
                  for row in rows]
        comparisons[name] = {
            "median_delta_core_cycles": statistics.median(values),
            "ci95": bootstrap(values, 0x5700 + index),
            "favorable_launches": sum(value < 0 for value in values),
            "launches": len(values),
            "deltas": values,
        }
    output = {"schema": "gt32-encap-working-set-057-v1", "cpu": args.cpu,
              "launches": args.launches, "comparisons": comparisons,
              "rows": rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(comparisons, indent=2))


if __name__ == "__main__":
    main()
