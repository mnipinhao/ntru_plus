#!/usr/bin/env python3
"""Normalize perf stat CSV output to per-stage, per-call metrics."""

import csv
import json
from pathlib import Path


CALLS = 22_000_000  # two warmups plus twenty measured samples
PREFIX = "cpu_core/"


def read_csv(path: Path) -> dict[str, float]:
    result = {}
    with path.open(newline="", encoding="utf-8") as stream:
        for row in csv.reader(line for line in stream if not line.startswith("#")):
            if len(row) < 3 or not row[0].strip() or "not supported" in row[0]:
                continue
            event = row[2].removeprefix(PREFIX).removesuffix("/u")
            try:
                result[event] = float(row[0])
            except ValueError:
                continue
    return result


def main() -> None:
    stages = {}
    for path in sorted(Path("results").glob("round2-*-perf.csv")):
        stage = path.name.removeprefix("round2-").removesuffix("-perf.csv")
        raw = read_csv(path)
        slots = raw.get("slots", 0.0)
        stages[stage] = {
            "calls": CALLS,
            "core_cycles_per_call": raw.get("cycles", 0.0) / CALLS,
            "instructions_per_call": raw.get("instructions", 0.0) / CALLS,
            "uops_retired_slots_per_call":
                raw.get("uops_retired.slots", 0.0) / CALLS,
            "loads_per_call": raw.get("mem_inst_retired.all_loads", 0.0)
                              / CALLS,
            "stores_per_call": raw.get("mem_inst_retired.all_stores", 0.0)
                               / CALLS,
            "l1_load_misses_per_call":
                raw.get("mem_load_retired.l1_miss", 0.0) / CALLS,
            "branches_per_call": raw.get("branches", 0.0) / CALLS,
            "branch_misses_per_call": raw.get("branch-misses", 0.0) / CALLS,
            "topdown_fe_bound_fraction":
                raw.get("topdown-fe-bound", 0.0) / slots if slots else 0.0,
            "topdown_be_bound_fraction":
                raw.get("topdown-be-bound", 0.0) / slots if slots else 0.0,
        }
    output = {"schema_version": 1, "pmu": "cpu_core", "stages": stages}
    Path("results/round2-stage-pmu.json").write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
