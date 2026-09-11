#!/usr/bin/env python3
"""Summarize P6-E raw paired samples without retaining them in Git."""

from __future__ import annotations

import csv
import json
import pathlib
import statistics

HERE = pathlib.Path(__file__).resolve().parent
RAW = HERE / "pi-results"


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    position = fraction * (len(ordered) - 1)
    lo, hi = int(position), min(int(position) + 1, len(ordered) - 1)
    weight = position - lo
    return ordered[lo] * (1 - weight) + ordered[hi] * weight


result: dict[str, dict] = {}
for mode in ("full", "small"):
    paired: list[float] = []
    by_variant = {"baseline": [], "candidate": []}
    for reverse in (0, 1):
        rows: dict[int, dict[str, float]] = {}
        path = RAW / f"{mode}-{reverse}.csv"
        assert "correctness=pass" in path.read_text()
        for row in csv.reader(path.read_text().splitlines()):
            if row and row[0] == "sample":
                rows.setdefault(int(row[3]), {})[row[2]] = float(row[4])
                by_variant[row[2]].append(float(row[4]))
        assert len(rows) == 37 and all(set(x) == {"baseline", "candidate"} for x in rows.values())
        paired.extend(x["candidate"] - x["baseline"] for x in rows.values())
    result[mode] = {
        "paired_cycle_delta": {
            "samples": len(paired),
            "median": statistics.median(paired),
            "p10": percentile(paired, 0.10),
            "p90": percentile(paired, 0.90),
            "min": min(paired),
            "max": max(paired),
            "positive_samples": sum(x > 0 for x in paired),
        },
        "cycles": {
            variant: {
                "median": statistics.median(values),
                "mad": statistics.median(abs(x - statistics.median(values)) for x in values),
                "p10": percentile(values, 0.10),
                "p90": percentile(values, 0.90),
            }
            for variant, values in by_variant.items()
        },
    }

(HERE / "p6e-dispersion.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
