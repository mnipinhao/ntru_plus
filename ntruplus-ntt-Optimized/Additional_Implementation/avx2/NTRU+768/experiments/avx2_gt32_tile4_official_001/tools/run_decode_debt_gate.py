#!/usr/bin/env python3
"""Run D0/D1/D2 Decode-debt attribution in both link orders."""

from __future__ import annotations

import argparse
import json
import re
import statistics
import subprocess
from pathlib import Path


LINE = re.compile(r"region=(\S+) metric=(\S+) value=([0-9.]+)")


def run(binary: Path, launches: int, iterations: int) -> dict[str, object]:
    results = []
    for launch in range(launches):
        process = subprocess.run(
            [str(binary), str(iterations), "1"], text=True,
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=True)
        metrics: dict[str, dict[str, float]] = {}
        for line in process.stdout.splitlines():
            match = LINE.fullmatch(line)
            if match:
                region, metric, value = match.groups()
                metrics.setdefault(region, {})[metric] = float(value)
        results.append({"launch": launch + 1, "metrics": metrics})
    summary = {}
    for region in ("d0_full", "d1_no_validation", "d2_unpack",
                   "d2_route", "d2_split"):
        summary[region] = {}
        for metric in ("tsc", "core_cycles", "instructions"):
            values = [entry["metrics"][region][metric] for entry in results]
            summary[region][metric] = statistics.median(values)
    for metric in ("tsc", "core_cycles", "instructions"):
        d0 = summary["d0_full"][metric]
        summary.setdefault("attribution", {})[metric] = {
            "validation_d0_minus_d1": d0 - summary["d1_no_validation"][metric],
            "unpack": summary["d2_unpack"][metric],
            "routing": summary["d2_route"][metric],
            "split_materialized_minus_d0": summary["d2_split"][metric] - d0,
        }
    return {"binary": str(binary), "launches": results, "summary": summary}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("normal", type=Path)
    parser.add_argument("reversed", type=Path)
    parser.add_argument("--launches", type=int, default=4)
    parser.add_argument("--iterations", type=int, default=4000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    static = json.loads(
        Path("generated/tile4_decode_debt_static.json").read_text())
    report = {
        "schema": "ntruplus768-gt32-r1-decode-debt-runtime-v1",
        "experiment": "R1-DECODE-DEBT-001",
        "method": "fixed CPU1, 20 medians per launch, four launches, PMU core cycles primary",
        "correctness": "1000 random valid, malformed rejection attribution, exact M output",
        "static_gate": static,
        "placements": {
            "normal": run(args.normal, args.launches, args.iterations),
            "reversed": run(args.reversed, args.launches, args.iterations),
        },
        "decision": "d3-static-hard-stop; retain-current-production-decoder",
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
