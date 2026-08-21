#!/usr/bin/env python3
"""Run and summarize normal/reversed compact frontend measurements."""

from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
from pathlib import Path


LINE = re.compile(
    r"^(?P<kind>region|pmu_region)=(?P<region>frontend|forward|2forward) "
    r".*paired_delta=(?P<delta>-?[0-9.]+) wins=(?P<wins>[0-9]+)/20$"
)


def launch(binary: Path, iterations: int, cpu: int) -> dict[str, dict[str, float | int]]:
    output = subprocess.check_output([str(binary), str(iterations), str(cpu)], text=True)
    rows: dict[str, dict[str, float | int]] = {}
    for line in output.splitlines():
        match = LINE.match(line)
        if match:
            rows[f"{match.group('kind')}:{match.group('region')}"] = {
                "delta": float(match.group("delta")),
                "wins": int(match.group("wins")),
            }
    if len(rows) != 6:
        raise RuntimeError(f"expected six rows, found {len(rows)}")
    return rows


def summarize(rows: list[dict[str, dict[str, float | int]]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key in rows[0]:
        deltas = [float(row[key]["delta"]) for row in rows]
        wins = [int(row[key]["wins"]) for row in rows]
        result[key] = {
            "launch_deltas": deltas,
            "launch_wins": wins,
            "median_delta": statistics.median(deltas),
            "negative_launches": sum(delta < 0 for delta in deltas),
        }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--normal", type=Path, required=True)
    parser.add_argument("--reversed", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=4000)
    parser.add_argument("--launches", type=int, default=8)
    parser.add_argument("--cpu", type=int, default=1)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    payload: dict[str, object] = {
        "schema": "ntruplus768-gt32-compact-frontend-executable-v1",
        "experiment": "GT32-COMPACT-FRONTEND-036",
        "iterations": args.iterations,
        "launches_per_placement": args.launches,
        "placements": {},
    }
    placements = payload["placements"]
    assert isinstance(placements, dict)
    for name, binary in (("normal", args.normal), ("reversed", args.reversed)):
        rows = [launch(binary, args.iterations, args.cpu) for _ in range(args.launches)]
        placements[name] = {"binary": str(binary), "launches": rows,
                            "summary": summarize(rows)}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(placements, indent=2))


if __name__ == "__main__":
    main()
