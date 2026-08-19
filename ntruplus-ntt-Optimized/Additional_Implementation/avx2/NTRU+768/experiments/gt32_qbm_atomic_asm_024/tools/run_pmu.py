#!/usr/bin/env python3
"""Collect process-scoped PMU counters for both matched-cage placements."""

from __future__ import annotations

import json
import statistics
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPEATS = 5
ITERATIONS = 1_000_000
EVENT_GROUPS = (
    (
        "cpu_core/cycles/u",
        "cpu_core/instructions/u",
        "cpu_core/uops_retired.slots/u",
    ),
    (
        "cpu_core/uops_dispatched.port_0/u",
        "cpu_core/uops_dispatched.port_1/u",
        "cpu_core/uops_dispatched.port_5_11/u",
        "cpu_core/uops_dispatched.port_2_3_10/u",
    ),
)


def collect(binary: Path, mode: str, events: tuple[str, ...]) -> dict[str, float]:
    command = [
        "perf", "stat", "-x,", "-e", ",".join(events), "--",
        str(binary), mode,
    ]
    completed = subprocess.run(command, text=True, capture_output=True, check=True)
    counters: dict[str, float] = {}
    for line in completed.stderr.splitlines():
        fields = line.split(",")
        if len(fields) < 3 or not fields[0].isdigit():
            continue
        counters[fields[2]] = int(fields[0]) / ITERATIONS
    missing = set(events) - set(counters)
    if missing:
        raise RuntimeError(f"missing PMU counters: {sorted(missing)}")
    return counters


def median_records(records: list[dict[str, float]]) -> dict[str, float]:
    return {
        event: statistics.median(record[event] for record in records)
        for event in records[0]
    }


def main() -> None:
    placements = {}
    for placement in ("normal", "reversed"):
        binary = ROOT / "build" / f"pmu_{placement}"
        modes = {}
        for mode in ("control", "atomic"):
            per_repeat = []
            for _ in range(REPEATS):
                merged = {}
                for events in EVENT_GROUPS:
                    merged.update(collect(binary, mode, events))
                per_repeat.append(merged)
            modes[mode] = {
                "per_repeat_per_call": per_repeat,
                "median_per_call": median_records(per_repeat),
            }
        control = modes["control"]["median_per_call"]
        atomic = modes["atomic"]["median_per_call"]
        placements[placement] = {
            "modes": modes,
            "atomic_minus_control_per_call": {
                event: atomic[event] - control[event] for event in control
            },
        }
    result = {
        "experiment": "GT32-QBM-ATOMIC-ASM-024",
        "iterations_per_process": ITERATIONS,
        "repeats": REPEATS,
        "scope": "process-scoped; driver pinned to first available CPU",
        "placements": placements,
    }
    output = ROOT / "results" / "qbm-atomic-pmu.json"
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(output)


if __name__ == "__main__":
    main()
