#!/usr/bin/env python3
import argparse
import json
import os
import random
import statistics
import subprocess
from pathlib import Path

NAMES = ("r_official", "r_gt", "c_official", "c_gt")

def launch(binary, cpu):
    result = subprocess.run([str(binary.resolve())], capture_output=True,
                            text=True, check=True,
                            preexec_fn=lambda: os.sched_setaffinity(0, {cpu}))
    values = {}
    addresses = {}
    for line in result.stdout.splitlines():
        key, value = line.split()
        if key.endswith("_address"):
            addresses[key] = value
        else:
            values[key] = int(value)
    if set(values) != set(NAMES):
        raise RuntimeError((values, result.stderr))
    return values, addresses

def bootstrap_ci(values, seed):
    rng = random.Random(seed)
    medians = sorted(statistics.median(rng.choices(values, k=len(values)))
                     for _ in range(20000))
    return [medians[499], medians[19499]]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--blocks", type=int, default=256)
    parser.add_argument("--warmup", type=int, default=4)
    parser.add_argument("--cpu", type=int, default=1)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    for _ in range(args.warmup):
        launch(args.binary, args.cpu)
    rows = []
    addresses = None
    for index in range(args.blocks):
        values, current_addresses = launch(args.binary, args.cpu)
        addresses = current_addresses
        rows.append({"launch": index + 1, "values": values})

    summary = {"absolute_medians": {
        name: statistics.median(row["values"][name] for row in rows)
        for name in NAMES}}
    for index, (site, official, gt) in enumerate((
            ("rhat", "r_official", "r_gt"),
            ("ciphertext", "c_official", "c_gt"))):
        deltas = [row["values"][gt] - row["values"][official]
                  for row in rows]
        summary[site + "_gt_minus_official"] = {
            "median": statistics.median(deltas),
            "ci95": bootstrap_ci(deltas, 0x540 + index),
            "positive_launches": sum(value > 0 for value in deltas),
            "negative_launches": sum(value < 0 for value in deltas),
            "zero_launches": sum(value == 0 for value in deltas),
        }

    output = {
        "schema": "gt32-serializer-boundary-054-v1",
        "cpu": args.cpu,
        "blocks": args.blocks,
        "addresses_last_launch": addresses,
        "summary": summary,
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()

