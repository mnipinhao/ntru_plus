#!/usr/bin/env python3
"""Apply the 033A PMU event set to every 033B ordering pair."""

from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
from pathlib import Path


ORDERS = ["current", "transform", "q24", "arithmetic"]
EVENTS = ["cycles", "instructions", "branches", "branch-misses",
          "l1-icache-load-misses", "itlb-load-misses",
          "idq_uops_not_delivered.core"]
CALLS = 10000


def parse(stderr: str) -> dict[str, float]:
    result: dict[str, float] = {}
    for line in stderr.splitlines():
        fields = line.split(",")
        if len(fields) < 3 or fields[0] == "<not counted>":
            continue
        for event in EVENTS:
            if f"/{event}/" in fields[2]:
                result[event] = float(fields[0]) / CALLS
    missing = sorted(set(EVENTS) - set(result))
    if missing:
        raise RuntimeError(f"missing {missing}: {stderr}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--launches", type=int, default=8)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cpu = sorted(os.sched_getaffinity(0))[0]
    result: dict[str, object] = {"schema": "gt32-encap-delivery-033b-pmu-v1",
                                "cpu": cpu, "calls": CALLS, "orders": {}}
    for order in ORDERS:
        launches = []
        for launch in range(args.launches):
            sequence = ["control", "candidate"] if launch % 2 == 0 else ["candidate", "control"]
            measured = {}
            for variant in sequence:
                binary = (args.build / f"bench_{order}_{variant}").resolve()

                def pin() -> None:
                    os.sched_setaffinity(0, {cpu})

                completed = subprocess.run(
                    ["perf", "stat", "-x,", "-e", ",".join(EVENTS), "--",
                     str(binary), "PMU"], check=True, capture_output=True,
                    text=True, preexec_fn=pin)
                measured[variant] = parse(completed.stderr)
            launches.append({"launch": launch + 1, "order": sequence,
                             "candidate_minus_control_per_call": {
                                 event: measured["candidate"][event] - measured["control"][event]
                                 for event in EVENTS}})
        result["orders"][order] = {
            "median_candidate_minus_control_per_call": {
                event: statistics.median(
                    entry["candidate_minus_control_per_call"][event]
                    for entry in launches) for event in EVENTS},
            "launch_results": launches,
        }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({order: data["median_candidate_minus_control_per_call"]
                      for order, data in result["orders"].items()},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

