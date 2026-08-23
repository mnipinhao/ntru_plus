#!/usr/bin/env python3
"""Pinned region PMU comparison for experiment 068."""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from pathlib import Path


EVENTS = [
    "cpu_core/cycles/", "cpu_core/instructions/", "cpu_core/branches/",
    "cpu_core/branch-misses/", "cpu_core/L1-dcache-loads/",
    "cpu_core/L1-dcache-stores/", "cpu_core/idq_uops_not_delivered.core/",
    "cpu_core/idq.dsb_uops/", "cpu_core/idq.mite_uops/",
    "cpu_core/uops_dispatched.port_5_11/",
]


def one(binary: Path, profile: str, iterations: int, cpu: int) -> dict:
    command = ["perf", "stat", "-x,", "-e", ",".join(EVENTS),
               "taskset", "-c", str(cpu), str(binary), profile, str(iterations)]
    completed = subprocess.run(command, text=True, capture_output=True, check=True)
    values: dict[str, float] = {}
    for line in completed.stderr.splitlines():
        fields = line.split(",")
        if len(fields) < 3 or not fields[0].strip().isdigit():
            continue
        event = fields[2].removesuffix("/u")
        values[event] = int(fields[0]) / iterations
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=500000)
    parser.add_argument("--samples", type=int, default=5)
    parser.add_argument("--cpu", type=int, default=1)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    raw = {profile: [one(args.binary, profile, args.iterations, args.cpu)
                     for _ in range(args.samples)]
           for profile in ("control", "reference", "candidate", "inline")}
    summary = {
        profile: {event: statistics.median(row[event] for row in rows)
                  for event in rows[0]}
        for profile, rows in raw.items()
    }
    result = {
        "schema": "ntruplus768-gt32-encap-consumer-abi-068-pmu-v1",
        "cpu": args.cpu, "iterations": args.iterations,
        "samples": args.samples, "summary_per_call": summary, "raw": raw,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
