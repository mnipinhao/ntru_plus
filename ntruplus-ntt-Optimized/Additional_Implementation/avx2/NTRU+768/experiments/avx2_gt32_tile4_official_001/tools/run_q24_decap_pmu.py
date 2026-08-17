#!/usr/bin/env python3
"""Collect non-multiplexed PMU groups for the Q24 decode-only decap gate."""

import argparse
import json
import subprocess
from pathlib import Path


GROUPS = {
    "cycles_instructions": [
        "cpu_core/cycles/u",
        "cpu_core/instructions/u",
    ],
    "retired_uops_memory": [
        "cpu_core/uops_retired.slots/u",
        "cpu_core/mem_inst_retired.all_loads/u",
        "cpu_core/mem_inst_retired.all_stores/u",
    ],
    "cache_branches": [
        "cpu_core/l1-dcache-loads/u",
        "cpu_core/l1-dcache-load-misses/u",
        "cpu_core/branches/u",
        "cpu_core/branch-misses/u",
    ],
    "topdown": [
        "cpu_core/topdown-fe-bound/u",
        "cpu_core/topdown-be-bound/u",
        "cpu_core/topdown-retiring/u",
        "cpu_core/topdown-bad-spec/u",
    ],
}


def parse_count(value: str) -> int | float:
    result = float(value)
    return int(result) if result.is_integer() else result


def collect(binary: Path, variant: str, group: list[str], iterations: int,
            repeats: int) -> dict[str, object]:
    event_group = "{" + ",".join(group) + "}"
    process = subprocess.run([
        "perf", "stat", "--no-big-num", "-x,", "-r", str(repeats),
        "-e", event_group, str(binary), str(iterations), variant,
    ], check=True, text=True, capture_output=True)
    if "correctness=byte-exact-valid-decap" not in process.stdout:
        raise RuntimeError(f"missing correctness marker from {binary}")
    events = {}
    for line in process.stderr.splitlines():
        fields = line.split(",")
        if len(fields) < 6 or not fields[2].startswith("cpu_core/"):
            continue
        if fields[0].startswith("<"):
            raise RuntimeError(f"PMU event was not counted: {line}")
        events[fields[2]] = {
            "count": parse_count(fields[0]),
            "repeat_stddev_percent": (float(fields[3].rstrip("%"))
                                      if fields[3] else None),
            "time_running_ns": (int(fields[4]) if fields[4] else None),
            "running_percent": (float(fields[5].rstrip("%"))
                                if fields[5] else None),
        }
    if not events:
        raise RuntimeError(f"no PMU events parsed from {binary}")
    return {"events": events}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=2000)
    parser.add_argument("--repeats", type=int, default=3)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    placements = {}
    for placement, binary in (("normal", args.binary),
                              ("reversed", args.reversed_binary)):
        variants = {}
        for variant in ("control", "q24"):
            variants[variant] = {
                name: collect(binary, variant, events, args.iterations,
                              args.repeats)
                for name, events in GROUPS.items()
            }
        deltas = {}
        for group_name in GROUPS:
            control = variants["control"][group_name]["events"]
            q24 = variants["q24"][group_name]["events"]
            deltas[group_name] = {}
            for event in control.keys() & q24.keys():
                control_count = control[event]["count"]
                q24_count = q24[event]["count"]
                deltas[group_name][event] = {
                    "q24_minus_control": q24_count - control_count,
                    "q24_minus_control_percent":
                        100.0 * (q24_count - control_count) / control_count,
                }
        placements[placement] = {
            "variants": variants,
            "q24_minus_control": deltas,
        }

    result = {
        "schema": "ntruplus768-gt32-q24-decap-pmu-v1",
        "experiment": "GT32-Q24-DECAP-DECODE-ONLY-PMU-001",
        "benchmark": {
            "iterations_per_sample": args.iterations,
            "samples_per_process": 20,
            "perf_repeats": args.repeats,
            "cpu": 1,
            "scope": "full-decap-single-variant-per-process",
            "event_groups_are_separate_runs": True,
        },
        "placements": placements,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for placement, data in placements.items():
        print(placement)
        for group in ("cycles_instructions", "retired_uops_memory",
                      "cache_branches", "topdown"):
            for event, delta in data["q24_minus_control"][group].items():
                print(f"  {event}: {delta['q24_minus_control_percent']:+.3f}%")


if __name__ == "__main__":
    main()
