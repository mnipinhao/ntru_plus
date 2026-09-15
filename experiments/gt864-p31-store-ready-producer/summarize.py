#!/usr/bin/env python3
"""Summarize alternating Pi 5 paired-PMU runs for P31."""

import csv
import json
import statistics
from pathlib import Path

HERE = Path(__file__).resolve().parent


def percentile(values, fraction):
    ordered = sorted(values)
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def summarize(paths):
    groups, pairs, rows = {}, {}, []
    correctness_runs = 0
    for path in paths:
        file_rows = []
        with path.open() as stream:
            for raw in stream:
                if raw.startswith("correctness=pass"):
                    correctness_runs += 1
                    continue
                row = next(csv.reader([raw]))
                if not row or row[0] not in {"full", "component"}:
                    continue
                key = (row[0], row[1])
                values = tuple(float(value) for value in row[3:6])
                groups.setdefault(key, {}).setdefault(row[2], []).append(values)
                file_rows.append((key, row[2], values))
        for offset in range(0, len(file_rows), 2):
            first, second = file_rows[offset:offset + 2]
            if first[0] != second[0] or {first[1], second[1]} != {"baseline", "candidate"}:
                raise RuntimeError(f"bad paired rows in {path}: {first}, {second}")
            by_name = {first[1]: first[2], second[1]: second[2]}
            pairs.setdefault(first[0], []).append(
                tuple(c - b for b, c in zip(by_name["baseline"], by_name["candidate"]))
            )
    result = {"correctness_runs": correctness_runs, "operations": {}}
    for key in sorted(groups):
        samples, deltas = groups[key], pairs[key]
        baseline = [statistics.median(row[i] for row in samples["baseline"]) for i in range(3)]
        candidate = [statistics.median(row[i] for row in samples["candidate"]) for i in range(3)]
        cycle_deltas = [row[0] for row in deltas]
        result["operations"]["/".join(key)] = {
            "samples_per_side": len(samples["baseline"]),
            "baseline_median": baseline,
            "candidate_median": candidate,
            "paired_delta_median": [statistics.median(row[i] for row in deltas) for i in range(3)],
            "cycle_delta_iqr": [percentile(cycle_deltas, q) for q in (0.25, 0.75)],
            "candidate_cycle_wins": sum(value < 0 for value in cycle_deltas),
            "baseline_ipc": baseline[1] / baseline[0],
            "candidate_ipc": candidate[1] / candidate[0],
        }
    return result


result = {
    "metric_order": ["cycles", "instructions", "branches"],
    "production_vs_p31": summarize(sorted((HERE / "pi-results").glob("prod-p31-*.csv"))),
    "p29_vs_p31": summarize(sorted((HERE / "pi-results").glob("p29-p31-*.csv"))),
}
(HERE / "results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
