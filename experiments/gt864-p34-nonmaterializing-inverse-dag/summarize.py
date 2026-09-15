#!/usr/bin/env python3
"""Summarize P34 stage PMU CSVs with empty-harness subtraction."""

import csv
import json
import statistics
import sys
from pathlib import Path

metrics = ["cycles", "instructions", "branches", "mem_access_rd", "mem_access_wr"]
rows = []
for path in map(Path, sys.argv[1:]):
    for row in csv.reader(path.read_text().splitlines()):
        if row and row[0] == "sample":
            rows.append((row[1], *map(float, row[3:])))

summary = {}
for name in sorted({row[0] for row in rows}):
    values = [row[1:] for row in rows if row[0] == name]
    result = {metric: statistics.median(v[i] for v in values)
              for i, metric in enumerate(metrics)}
    result["samples"] = len(values)
    summary[name] = result

empty = summary["empty"]
for name, result in summary.items():
    if name == "empty":
        continue
    result["net"] = {metric: result[metric] - empty[metric] for metric in metrics}
    result["net"]["ipc"] = result["net"]["instructions"] / result["net"]["cycles"]

full = summary["complete_inverse_to_ternary"]["net"]
parts = [summary[name]["net"] for name in
         ("inverse9_x12", "main_i16_x6", "tail_i16", "raw_to_ternary")]
summary["diagnostic_wrapper_residual"] = {
    metric: full[metric] - sum(part[metric] for part in parts)
    for metric in metrics
}
summary["diagnostic_wrapper_residual"]["note"] = (
    "non-additive: wrapper/control/init/wipe plus isolated-call cache context"
)
text = json.dumps(summary, indent=2) + "\n"
(Path(__file__).resolve().parent / "profile-results.json").write_text(text)
print(text, end="")
