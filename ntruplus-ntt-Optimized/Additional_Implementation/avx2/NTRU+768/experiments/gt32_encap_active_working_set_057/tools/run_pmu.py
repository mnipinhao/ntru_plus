#!/usr/bin/env python3
import argparse
import json
import random
import statistics
import subprocess
from pathlib import Path

EVENTS = ("cpu_core/cycles/", "cpu_core/instructions/",
          "cpu_core/idq_uops_not_delivered.core/",
          "cpu_core/l1d_pend_miss.pending_cycles/")
ORDERS = ((0, 1, 2, 2, 1, 0), (1, 2, 0, 0, 2, 1),
          (2, 0, 1, 1, 0, 2))
ITERATIONS = 20000


def measure(binary, profile, cpu):
    command = ["perf", "stat", "-x,"]
    for event in EVENTS:
        command += ["-e", event]
    command += ["taskset", "-c", str(cpu), str(binary.resolve()), str(profile)]
    done = subprocess.run(command, stdout=subprocess.DEVNULL,
                          stderr=subprocess.PIPE, text=True, check=True)
    result = {}
    for line in done.stderr.splitlines():
        fields = line.split(",")
        if len(fields) < 3:
            continue
        for event in EVENTS:
            if fields[2].startswith(event[:-1]):
                result[event] = float(fields[0].replace(" ", "")) / ITERATIONS
    if set(result) != set(EVENTS):
        raise RuntimeError((result, done.stderr))
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
        profiles = {}
        for profile, repetitions in observed.items():
            profiles[f"p{profile}"] = {
                event: statistics.fmean(value[event] for value in repetitions)
                for event in EVENTS}
        rows.append({"block": block + 1, "order": list(order),
                     "profiles": profiles})
    deltas = {}
    for pair_index, (name, candidate, control) in enumerate((
            ("b_minus_a", "p1", "p0"),
            ("c_minus_a", "p2", "p0"),
            ("c_minus_b", "p2", "p1"))):
        deltas[name] = {}
        for index, event in enumerate(EVENTS):
            values = [row["profiles"][candidate][event]
                      - row["profiles"][control][event] for row in rows]
            deltas[name][event] = {
                "median": statistics.median(values),
                "ci95": bootstrap(values, 0x57f0 + 10*pair_index + index),
                "favorable_blocks": sum(value < 0 for value in values),
                "values": values}
    output = {"schema": "gt32-encap-working-set-057-pmu-v1",
              "cpu": args.cpu, "iterations": ITERATIONS,
              "blocks": args.blocks, "deltas_vs_a": deltas, "rows": rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps(deltas, indent=2))


if __name__ == "__main__":
    main()
