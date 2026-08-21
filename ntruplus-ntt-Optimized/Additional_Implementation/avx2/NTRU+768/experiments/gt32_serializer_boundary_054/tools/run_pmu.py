#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
from pathlib import Path

TARGETS = ("r_official", "r_gt", "c_official", "c_gt")
EVENTS = (
    "cpu_core/cycles/",
    "cpu_core/instructions/",
    "cpu_core/mem_inst_retired.all_loads/",
    "cpu_core/mem_inst_retired.all_stores/",
)
ITERATIONS = 200000

def measure(binary, target, event, cpu, repetitions):
    command = ["perf", "stat", "-x,", "-r", str(repetitions), "-e", event,
               "taskset", "-c", str(cpu), str(binary.resolve()), target]
    result = subprocess.run(command, stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE, text=True, check=True)
    for line in result.stderr.splitlines():
        fields = line.split(",")
        if len(fields) >= 3 and fields[2].startswith(event[:-1]):
            return float(fields[0].replace(" ", ""))
    raise RuntimeError((event, target, result.stderr))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--cpu", type=int, default=1)
    parser.add_argument("--repetitions", type=int, default=11)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    totals = {target: {} for target in TARGETS}
    per_call = {target: {} for target in TARGETS}
    for target in TARGETS:
        for event in EVENTS:
            value = measure(args.binary, target, event, args.cpu,
                            args.repetitions)
            short = event.removeprefix("cpu_core/").removesuffix("/")
            totals[target][short] = value
            per_call[target][short] = value / ITERATIONS

    deltas = {}
    for site, official, gt in (("rhat", "r_official", "r_gt"),
                               ("ciphertext", "c_official", "c_gt")):
        deltas[site + "_gt_minus_official"] = {
            event: per_call[gt][event] - per_call[official][event]
            for event in per_call[gt]
        }
    output = {
        "schema": "gt32-serializer-boundary-054-pmu-v1",
        "cpu": args.cpu,
        "repetitions": args.repetitions,
        "iterations": ITERATIONS,
        "per_call": per_call,
        "deltas": deltas,
        "totals": totals,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({"per_call": per_call, "deltas": deltas}, indent=2))

if __name__ == "__main__":
    main()
