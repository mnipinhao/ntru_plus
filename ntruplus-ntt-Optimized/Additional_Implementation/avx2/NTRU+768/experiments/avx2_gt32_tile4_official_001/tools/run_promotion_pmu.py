#!/usr/bin/env python3
"""Collect non-multiplexed promotion PMU event groups on CPU 1."""

import argparse
import hashlib
import json
import statistics
import subprocess
from pathlib import Path

from report_promotion_symbols import sections, symbols


GROUPS = {
    "cycles_instructions": [
        "cpu_core/cycles/", "cpu_core/instructions/",
    ],
    "branches": [
        "cpu_core/branches/", "cpu_core/branch-misses/",
    ],
    "l1_data": [
        "cpu_core/L1-dcache-loads/", "cpu_core/L1-dcache-load-misses/",
    ],
    "topdown": [
        "cpu_core/topdown-fe-bound/", "cpu_core/topdown-be-bound/",
        "cpu_core/topdown-retiring/", "cpu_core/topdown-bad-spec/",
    ],
}


def parse_perf(stderr: str, iterations: int) -> list[dict[str, object]]:
    records = []
    for line in stderr.splitlines():
        fields = line.split(";")
        if len(fields) < 5 or not fields[0].strip().isdigit():
            continue
        count = int(fields[0].strip())
        event = fields[2].strip()
        time_running_ns = int(fields[3].strip())
        running_percent = float(fields[4].strip())
        records.append({
            "event": event,
            "count": count,
            "count_per_call": count / iterations,
            "time_running_ns": time_running_ns,
            "running_percent": running_percent,
            "scaling_factor": 100.0 / running_percent,
        })
    return records


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--iterations", type=int, default=1000000)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    gates = ("bm", "bm_i1_t9", "full", "full_crep")
    backends = ("official", "tile4")
    result = {
        "binary": str(args.binary),
        "binary_sha256": hashlib.sha256(args.binary.read_bytes()).hexdigest(),
        "binary_sections": sections(args.binary),
        "binary_symbols": symbols(args.binary),
        "cpu": 1,
        "iterations": args.iterations,
        "repeats": args.repeats,
        "groups": {},
    }
    for group, events in GROUPS.items():
        group_result = {}
        for gate in gates:
            gate_result = {}
            for backend in backends:
                repetitions = []
                for _ in range(args.repeats):
                    command = [
                        "perf", "stat", "-x", ";", "-e", ",".join(events),
                        "--", str(args.binary), str(args.iterations), "0",
                        "pmu", gate, backend,
                    ]
                    process = subprocess.run(
                        command, check=True, text=True, capture_output=True)
                    repetitions.append(parse_perf(process.stderr, args.iterations))
                event_names = sorted({record["event"]
                                      for repeat in repetitions
                                      for record in repeat})
                medians = {}
                for event in event_names:
                    values = [record["count_per_call"]
                              for repeat in repetitions for record in repeat
                              if record["event"] == event]
                    medians[event] = statistics.median(values)
                gate_result[backend] = {
                    "repetitions": repetitions,
                    "median_count_per_call": medians,
                }
            group_result[gate] = gate_result
        result["groups"][group] = group_result
    args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
