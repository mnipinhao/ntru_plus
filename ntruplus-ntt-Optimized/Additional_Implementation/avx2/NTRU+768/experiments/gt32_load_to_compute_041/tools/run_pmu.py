#!/usr/bin/env python3
"""Collect region-dominated PMU counts and normalize per kernel call."""
from __future__ import annotations
import argparse
import json
import os
import statistics
import subprocess
from pathlib import Path

ITERATIONS = 200000
EVENTS = ("cpu_core/cycles/,cpu_core/instructions/,"
          "cpu_core/mem_inst_retired.all_loads/")

def one(binary: Path, region: str, cpu: int) -> dict[str, float]:
    cmd = ["perf", "stat", "-x,", "-e", EVENTS, "--",
           "taskset", "-c", str(cpu), str(binary.resolve()), region]
    done = subprocess.run(cmd, check=True, capture_output=True, text=True)
    values = {}
    for line in done.stderr.splitlines():
        fields = line.split(",")
        if len(fields) >= 3 and fields[0].strip().isdigit():
            name = fields[2].strip()
            if "cpu_core/" not in name:
                continue
            if "/cycles/" in name:
                key = "cycles"
            elif "/instructions/" in name:
                key = "instructions"
            elif "mem_inst_retired.all_loads" in name:
                key = "mem_inst_retired.all_loads"
            else:
                continue
            values[key] = int(fields[0].strip()) / ITERATIONS
    return values

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--launches", type=int, default=8)
    args = parser.parse_args()
    cpu = sorted(os.sched_getaffinity(0))[0]
    rows = []
    regions = ("pack_control", "pack_candidate", "b3_control", "b3_candidate")
    for launch in range(args.launches):
        order = regions if launch % 2 == 0 else tuple(reversed(regions))
        row = {"launch": launch + 1}
        for region in order:
            row[region] = one(args.binary, region, cpu)
        rows.append(row)
    summary = {}
    for base in ("pack", "b3"):
        for event in ("cycles", "instructions", "mem_inst_retired.all_loads"):
            deltas = [row[base + "_candidate"][event] -
                      row[base + "_control"][event] for row in rows]
            summary[base + "_" + event] = {
                "median_delta_per_call": statistics.median(deltas),
                "all_deltas": deltas,
            }
    result = {"schema": "gt32-load-to-compute-041-pmu-v1",
              "cpu": cpu, "iterations_per_region": ITERATIONS,
              "summary": summary, "launches": rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
