#!/usr/bin/env python3
"""Preserve and normalize Round 3 grouped perf-stat CSV counters."""

from __future__ import annotations

import csv
import json
from pathlib import Path


CALLS = 22_000_000
PREFIX = "round3-pmu-"


def parse_number(value: str) -> float | None:
    try:
        return float(value.strip())
    except ValueError:
        return None


def parse(path: Path) -> dict:
    events = {}
    with path.open(newline="", encoding="utf-8") as stream:
        rows = csv.reader(line for line in stream if not line.startswith("#"))
        for row in rows:
            if len(row) < 3 or "not supported" in row[0] or "not counted" in row[0]:
                continue
            raw = parse_number(row[0])
            if raw is None:
                continue
            name = (row[2].strip().removeprefix("cpu_core/")
                    .removesuffix("/u").removesuffix("/"))
            running_ns = parse_number(row[3]) if len(row) > 3 else None
            running_percent = parse_number(row[4].rstrip("%")) if len(row) > 4 else None
            enabled_ns = None
            scale = None
            if running_ns is not None and running_percent not in (None, 0.0):
                enabled_ns = running_ns / (running_percent / 100.0)
                scale = enabled_ns / running_ns
            events[name] = {
                "raw_count": raw,
                "unit": row[1].strip(),
                "per_call": raw / CALLS,
                "time_running_ns": running_ns,
                "time_enabled_ns": enabled_ns,
                "running_percent": running_percent,
                "scaling_factor": scale,
            }
    return events


def main() -> None:
    measurements = {}
    for path in sorted(Path("results").glob(f"{PREFIX}*-g[1-4].csv")):
        stem = path.stem.removeprefix(PREFIX)
        body, group_text = stem.rsplit("-g", 1)
        candidate, backend = body.rsplit("-", 1)
        key = f"{candidate}:{backend}"
        entry = measurements.setdefault(key, {"candidate": candidate,
                                               "backend": backend,
                                               "groups": {}})
        entry["groups"][group_text] = {
            "artifact": str(path),
            "events": parse(path),
        }
    output = {
        "schema_version": 1,
        "cpu": 1,
        "calls_per_event": CALLS,
        "event_groups": {
            "1": ["cycles", "instructions"],
            "2": ["uops_retired.slots", "mem_inst_retired.all_loads",
                  "mem_inst_retired.all_stores"],
            "3": ["mem_load_retired.l1_miss", "branches", "branch-misses"],
            "4": ["slots", "topdown-fe-bound", "topdown-be-bound"],
        },
        "measurements": measurements,
    }
    Path("results/round3-symmetric-pmu.json").write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
