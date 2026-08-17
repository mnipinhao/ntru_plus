#!/usr/bin/env python3
"""Measure whether Keygen's extra retired loads create cache/load stalls."""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from pathlib import Path


EVENT_GROUPS = {
    "cache": [
        "cpu_core/cycles/",
        "cpu_core/mem_inst_retired.all_loads/",
        "cpu_core/mem_load_retired.l1_miss/",
        "cpu_core/mem_load_retired.l2_miss/",
    ],
    "branch": [
        "cpu_core/cycles/",
        "cpu_core/instructions/",
        "cpu_core/branch-instructions/",
        "cpu_core/branch-misses/",
    ],
    "load_pressure": [
        "cpu_core/cycles/",
        "cpu_core/l1d_pend_miss.pending_cycles/",
        "cpu_core/memory_activity.stalls_l1d_miss/",
    ],
}


def run_one(binary: Path, backend: str, iterations: int, events: list[str]) -> dict[str, float]:
    command = [
        "perf", "stat", "-x,", "-e", ",".join(events), "--",
        str(binary), str(iterations), "g1", backend, "nocheck",
    ]
    process = subprocess.run(command, check=True, capture_output=True, text=True)
    counters: dict[str, float] = {}
    for line in process.stderr.splitlines():
        fields = line.split(",")
        if len(fields) < 3 or not fields[0] or fields[0].startswith("<"):
            continue
        try:
            value = float(fields[0]) / iterations
        except ValueError:
            continue
        event = fields[2].replace("cpu_core/", "").replace("/u", "").replace("/", "")
        counters[event] = value
    return counters


def summarize(samples: list[float]) -> dict[str, float]:
    return {
        "median": statistics.median(samples),
        "minimum": min(samples),
        "maximum": max(samples),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--repeats", type=int, default=12)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    placements: dict[str, object] = {}
    for placement, binary in (
        ("normal", args.binary),
        ("reversed", args.reversed_binary),
    ):
        placement_result: dict[str, object] = {}
        for group_name, events in EVENT_GROUPS.items():
            paired = []
            for repeat in range(args.repeats):
                order = ("official", "gt32-prod") if repeat % 2 == 0 else ("gt32-prod", "official")
                sample = {
                    backend: run_one(binary, backend, args.iterations, events)
                    for backend in order
                }
                paired.append(sample)
            event_names = sorted(set().union(*(sample["official"] for sample in paired)))
            summary = {}
            for event in event_names:
                official = [sample["official"][event] for sample in paired]
                gt = [sample["gt32-prod"][event] for sample in paired]
                delta = [candidate - control for candidate, control in zip(gt, official)]
                summary[event] = {
                    "official": summarize(official),
                    "gt": summarize(gt),
                    "delta_gt_minus_official": summarize(delta),
                    "gt_wins": sum(value < 0 for value in delta),
                    "pairs": len(delta),
                }
            placement_result[group_name] = {"summary": summary, "samples": paired}
        placements[placement] = placement_result

    result = {
        "schema": "ntruplus768-keygen-load-provenance-pmu-v1",
        "iterations": args.iterations,
        "repeats": args.repeats,
        "placements": placements,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
