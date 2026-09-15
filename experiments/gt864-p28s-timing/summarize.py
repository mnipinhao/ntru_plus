#!/usr/bin/env python3
"""Summarize alternating P28-S Pi 5 PMU samples and paired deltas."""

import csv
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent


def percentile(values, fraction):
    ordered = sorted(values)
    index = (len(ordered) - 1) * fraction
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    weight = index - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def summarize_pair(prefix):
    groups = {}
    paired = {}
    for path in sorted((HERE / "pi-run").glob(f"{prefix}-*.csv")):
        rows = []
        with path.open() as stream:
            for row in csv.reader(stream):
                if row and row[0] in {"full", "component"}:
                    key = (row[0], row[1])
                    values = tuple(float(value) for value in row[3:6])
                    groups.setdefault(key, {}).setdefault(row[2], []).append(values)
                    rows.append((key, row[2], values))
        for offset in range(0, len(rows), 2):
            first, second = rows[offset:offset + 2]
            if first[0] != second[0] or {first[1], second[1]} != {"baseline", "candidate"}:
                raise RuntimeError(f"bad paired rows in {path}: {first}, {second}")
            by_name = {first[1]: first[2], second[1]: second[2]}
            paired.setdefault(first[0], []).append(
                tuple(c - b for b, c in zip(by_name["baseline"], by_name["candidate"]))
            )

    result = {}
    for key, samples in groups.items():
        label = "/".join(key)
        medians = {
            name: [statistics.median(values[i] for values in rows) for i in range(3)]
            for name, rows in samples.items()
        }
        deltas = paired[key]
        result[label] = {
            "samples_per_side": len(samples["baseline"]),
            "baseline_median": medians["baseline"],
            "candidate_median": medians["candidate"],
            "paired_delta_median": [statistics.median(row[i] for row in deltas) for i in range(3)],
            "cycle_delta_iqr": [percentile([row[0] for row in deltas], q) for q in (0.25, 0.75)],
            "candidate_cycle_wins": sum(row[0] < 0 for row in deltas),
        }
    return result


def summarize_isolated(prefix):
    samples = {"baseline": [], "candidate": []}
    deltas = []
    for path in sorted((HERE / "pi-run").glob(f"isolated-{prefix}-*.csv")):
        rows = []
        with path.open() as stream:
            for row in csv.reader(stream):
                if row and row[0] == "p28":
                    values = tuple(float(value) for value in row[2:5])
                    samples[row[1]].append(values)
                    rows.append((row[1], values))
        for offset in range(0, len(rows), 2):
            pair = rows[offset:offset + 2]
            by_name = {name: values for name, values in pair}
            deltas.append(tuple(c - b for b, c in zip(by_name["baseline"], by_name["candidate"])))
    return {
        "samples_per_side": len(samples["baseline"]),
        "baseline_median": [statistics.median(row[i] for row in samples["baseline"]) for i in range(3)],
        "candidate_median": [statistics.median(row[i] for row in samples["candidate"]) for i in range(3)],
        "paired_delta_median": [statistics.median(row[i] for row in deltas) for i in range(3)],
        "cycle_delta_iqr": [percentile([row[0] for row in deltas], q) for q in (0.25, 0.75)],
        "candidate_cycle_wins": sum(row[0] < 0 for row in deltas),
    }


result = {
    "metric_order": ["cycles", "instructions", "branches"],
    "isolated_p28": summarize_isolated("p28"),
    "isolated_p28s": summarize_isolated("p28s"),
    "production_vs_p28s": summarize_pair("production-p28s"),
    "p28_vs_p28s": summarize_pair("p28-p28s"),
}
(HERE / "results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
