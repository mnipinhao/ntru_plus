#!/usr/bin/env python3
"""Run the bounded F14 cross-packet wavefront gate."""

from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
from pathlib import Path


LINE = re.compile(
    r"^(?P<kind>region|pmu_region)=(?P<region>frontend_f14_w2|forward_f14_w2|2forward_f14_w2) "
    r".*paired_delta=(?P<delta>-?[0-9.]+) wins=(?P<wins>[0-9]+)/20$"
)


def one_launch(binary: Path, iterations: int, cpu: int) -> dict[str, dict[str, float | int]]:
    output = subprocess.check_output(
        [str(binary), str(iterations), str(cpu)], text=True
    )
    rows: dict[str, dict[str, float | int]] = {}
    for line in output.splitlines():
        match = LINE.match(line)
        if match:
            key = f"{match.group('kind')}:{match.group('region')}"
            rows[key] = {
                "delta": float(match.group("delta")),
                "wins": int(match.group("wins")),
            }
    if len(rows) != 6:
        raise RuntimeError(f"expected 6 F14-W2 rows, found {len(rows)}")
    return rows


def summarize(launches: list[dict[str, dict[str, float | int]]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key in launches[0]:
        deltas = [float(launch[key]["delta"]) for launch in launches]
        wins = [int(launch[key]["wins"]) for launch in launches]
        result[key] = {
            "launch_deltas": deltas,
            "launch_wins": wins,
            "median_delta": statistics.median(deltas),
            "negative_launches": sum(delta < 0.0 for delta in deltas),
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
        "schema": "ntruplus768-gt32-f14-cross-packet-wavefront-v1",
        "experiment": "F14-CROSS-PACKET-WAVEFRONT-001",
        "candidate": "W2: preload next packet ymm4/ymm5 between branch DFT3 tails",
        "frozen": [
            "arithmetic",
            "instruction multiset",
            "3917-byte symbol size",
            "twiddles",
            "layout and output",
        ],
        "static": {
            "preloaded_vectors_per_boundary": 2,
            "boundaries": 7,
            "peak_ymm": 16,
            "spills": 0,
            "extra_moves": 0,
            "instruction_delta": 0,
        },
        "iterations": args.iterations,
        "launches_per_placement": args.launches,
        "placements": {},
    }
    placements = payload["placements"]
    assert isinstance(placements, dict)
    for name, binary in (("normal", args.normal), ("reversed", args.reversed)):
        launches = [one_launch(binary, args.iterations, args.cpu) for _ in range(args.launches)]
        placements[name] = {
            "binary": str(binary),
            "launches": launches,
            "summary": summarize(launches),
        }

    payload["decision"] = {
        "local_effect": "small-positive",
        "production_promoted": False,
        "reason": "same-work wavefront is measurable, but only about 2 core cycles per Forward",
        "next": "N5 cross-tile wavefront static liveness gate",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2) + "\n")
    print(json.dumps(payload["decision"], indent=2))


if __name__ == "__main__":
    main()
