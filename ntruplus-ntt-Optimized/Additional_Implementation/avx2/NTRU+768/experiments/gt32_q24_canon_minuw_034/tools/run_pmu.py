#!/usr/bin/env python3
"""Region-dominant PMU corroboration for full Encap 034."""

from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
from pathlib import Path


EVENTS = ["cycles", "instructions", "branches", "branch-misses",
          "mem_inst_retired.all_loads", "mem_inst_retired.all_stores",
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
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--launches", type=int, default=8)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    cpu = sorted(os.sched_getaffinity(0))[0]
    launches = []
    for launch in range(args.launches):
        order = ["CONTROL", "CANDIDATE"] if launch % 2 == 0 else ["CANDIDATE", "CONTROL"]
        measurements: dict[str, dict[str, float]] = {}
        for variant in order:

            def pin() -> None:
                os.sched_setaffinity(0, {cpu})

            completed = subprocess.run(
                ["perf", "stat", "-x,", "-e", ",".join(EVENTS), "--",
                 str(args.binary.resolve()), "PMU_" + variant],
                check=True, capture_output=True, text=True, preexec_fn=pin)
            measurements[variant] = parse(completed.stderr)
        launches.append({
            "launch": launch + 1,
            "order": order,
            "candidate_minus_control_per_call": {
                event: measurements["CANDIDATE"][event] - measurements["CONTROL"][event]
                for event in EVENTS
            },
        })
    summary = {
        event: statistics.median(entry["candidate_minus_control_per_call"][event]
                                 for entry in launches)
        for event in EVENTS
    }
    result = {"schema": "gt32-q24-034-full-pmu-v1", "cpu": cpu,
              "calls_per_measurement": CALLS,
              "median_candidate_minus_control_per_call": summary,
              "launch_results": launches}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

