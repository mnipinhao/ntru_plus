#!/usr/bin/env python3
"""Summarize SUPERCOP delta-encoded cycle measurements as stabilized quartiles."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


DELTA_RE = re.compile(r"([+-])(\d+)")
METRICS = ("keypair_cycles", "enc_cycles", "dec_cycles")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("data", type=Path)
    parser.add_argument("--scheme", required=True)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def stabilized_quartiles(values: list[int]) -> list[float]:
    if not values:
        raise ValueError("cannot summarize an empty sample")
    count = len(values)
    expanded = sorted(values * 8)
    return [
        sum(expanded[offset * count : (offset + 2) * count]) / (2 * count)
        for offset in (1, 3, 5)
    ]


def decode_measurement(line: str, metric: str) -> list[int] | None:
    marker = f" {metric} - "
    if marker not in line:
        return None
    encoded = line.split(marker, 1)[1]
    base_text, deltas = encoded.split(" ", 1)
    base = int(base_text)
    return [
        base + (int(value) if sign == "+" else -int(value))
        for sign, value in DELTA_RE.findall(deltas)
    ]


def main() -> int:
    args = parse_args()
    primitive = f" {args.scheme}/timingleaks "
    lines = [
        line for line in args.data.read_text().splitlines() if primitive in line
    ]
    metrics: dict[str, object] = {}
    for metric in METRICS:
        runs = [
            decoded
            for line in lines
            if (decoded := decode_measurement(line, metric)) is not None
        ]
        values = [value for run in runs for value in run]
        metrics[metric] = {
            "runs": len(runs),
            "samples_per_run": [len(run) for run in runs],
            "samples": len(values),
            "run_stabilized_medians": [
                stabilized_quartiles(run)[1] for run in runs
            ],
            "aggregate_stabilized_quartiles": stabilized_quartiles(values),
            "minimum": min(values),
            "maximum": max(values),
        }
    rendered = json.dumps(
        {
            "scheme": args.scheme,
            "data": str(args.data.resolve()),
            "metrics": metrics,
        },
        indent=2,
        sort_keys=True,
    )
    if args.output:
        args.output.write_text(rendered + "\n")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
