#!/usr/bin/env python3
import argparse
import json
import random
import statistics
import subprocess
from pathlib import Path

EVENTS = (
    "cpu_core/cycles/",
    "cpu_core/instructions/",
    "cpu_core/idq_uops_not_delivered.core/",
    "cpu_core/l1d_pend_miss.pending_cycles/",
)
ITERATIONS = 20000


ORDERS = ((0, 1, 2, 2, 1, 0), (1, 2, 0, 0, 2, 1),
          (2, 0, 1, 1, 0, 2))


def measure(binary, profile, cpu):
    command = ["perf", "stat", "-x,"]
    for event in EVENTS:
        command += ["-e", event]
    command += ["taskset", "-c", str(cpu), str(binary.resolve()), str(profile)]
    completed = subprocess.run(command, stdout=subprocess.DEVNULL,
                               stderr=subprocess.PIPE, text=True, check=True)
    result = {}
    for line in completed.stderr.splitlines():
        fields = line.split(",")
        if len(fields) < 3:
            continue
        for event in EVENTS:
            if fields[2].startswith(event[:-1]):
                result[event] = float(fields[0].replace(" ", "")) / ITERATIONS
    if set(result) != set(EVENTS):
        raise RuntimeError((result, completed.stderr))
    return result


def bootstrap(values, seed):
    rng = random.Random(seed)
    samples = sorted(statistics.median(rng.choices(values, k=len(values)))
                     for _ in range(20000))
    return [samples[499], samples[19499]]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--cpu", type=int, default=1)
    parser.add_argument("--blocks", type=int, default=18)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    rows = []
    for block in range(args.blocks):
        order = ORDERS[block % len(ORDERS)]
        observed = {profile: [] for profile in range(3)}
        for profile in order:
            observed[profile].append(measure(args.binary, profile, args.cpu))
        row = {"block": block + 1, "order": list(order), "profiles": {}}
        for profile, repetitions in observed.items():
            row["profiles"][f"p{profile}"] = {
                event: statistics.fmean(value[event] for value in repetitions)
                for event in EVENTS
            }
        rows.append(row)
    per_call = {
        f"p{profile}": {
            event: statistics.median(
                row["profiles"][f"p{profile}"][event] for row in rows)
            for event in EVENTS
        }
        for profile in range(3)
    }
    deltas = {}
    for profile in (1, 2):
        deltas[f"p{profile}"] = {}
        for event_index, event in enumerate(EVENTS):
            values = [row["profiles"][f"p{profile}"][event]
                      - row["profiles"]["p0"][event] for row in rows]
            deltas[f"p{profile}"][event] = {
                "median": statistics.median(values),
                "ci95": bootstrap(values, 0x56F0 + 10 * profile + event_index),
                "favorable_blocks": sum(value < 0 for value in values),
                "values": values,
            }
    output = {
        "schema": "gt32-encap-data-geometry-056-pmu-v1",
        "cpu": args.cpu,
        "iterations": ITERATIONS,
        "blocks": args.blocks,
        "sequence": "balanced mirrored three-profile rotations",
        "per_call": per_call,
        "deltas_vs_p0": deltas,
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
