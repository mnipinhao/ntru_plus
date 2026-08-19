#!/usr/bin/env python3
"""Region-dominant perf attribution for representative 033 cage offsets."""

from __future__ import annotations

import argparse
import json
import os
import statistics
import subprocess
from pathlib import Path


EVENTS = [
    "cycles",
    "instructions",
    "branches",
    "branch-misses",
    "l1-icache-load-misses",
    "itlb-load-misses",
    "idq_uops_not_delivered.core",
]
CALLS = 10000


def parse(stderr: str) -> dict[str, float]:
    result: dict[str, float] = {}
    for line in stderr.splitlines():
        fields = line.split(",")
        if len(fields) < 3 or fields[0] == "<not counted>":
            continue
        event_field = fields[2]
        if "cpu_core/" not in event_field:
            continue
        for event in EVENTS:
            if f"/{event}/" in event_field:
                result[event] = float(fields[0]) / CALLS
    missing = sorted(set(EVENTS) - set(result))
    if missing:
        raise RuntimeError(f"missing perf events {missing}: {stderr}")
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--prefix", default="pmu_offset_")
    parser.add_argument("--launches", type=int, default=8)
    parser.add_argument("offsets", nargs="+", type=int)
    args = parser.parse_args()
    allowed = sorted(os.sched_getaffinity(0))
    cpu = allowed[0]
    variants: dict[str, object] = {}
    for offset in args.offsets:
        binary = (args.build / f"{args.prefix}{offset}").resolve()
        launches = []
        for launch in range(args.launches):
            order = ["B", "C"] if launch % 2 == 0 else ["C", "B"]
            measurements: dict[str, dict[str, float]] = {}
            for variant in order:

                def pin() -> None:
                    os.sched_setaffinity(0, {cpu})

                completed = subprocess.run(
                    ["perf", "stat", "-x,", "-e", ",".join(EVENTS),
                     "--", str(binary), f"PMU_{variant}"],
                    check=True, capture_output=True, text=True,
                    preexec_fn=pin)
                measurements[variant] = parse(completed.stderr)
            launches.append({
                "launch": launch + 1,
                "order": order,
                "B_per_call": measurements["B"],
                "C_per_call": measurements["C"],
                "C_minus_B_per_call": {
                    event: measurements["C"][event]
                    - measurements["B"][event] for event in EVENTS
                },
            })
        variants[str(offset)] = {
            "median_C_minus_B_per_call": {
                event: statistics.median(
                    entry["C_minus_B_per_call"][event] for entry in launches)
                for event in EVENTS
            },
            "launch_results": launches,
        }
    result = {
        "schema": "gt32-encap-delivery-033-pmu-v1",
        "pinned_cpu": cpu,
        "calls_per_measurement": CALLS,
        "launches_per_offset": args.launches,
        "events": EVENTS,
        "variants": variants,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({offset: data["median_C_minus_B_per_call"]
                      for offset, data in variants.items()},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
