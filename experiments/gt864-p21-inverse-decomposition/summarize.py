#!/usr/bin/env python3
"""Summarize P21 stage CSV files with empty-harness subtraction."""

import csv
import json
import statistics
import sys
from pathlib import Path

paths = [Path(arg) for arg in sys.argv[1:]]
rows = []
for path in paths:
    for row in csv.reader(path.read_text().splitlines()):
        if row and row[0] == "sample":
            rows.append((row[1], *map(float, row[3:])))

metrics = ["cycles", "instructions", "branches", "mem_access_rd", "mem_access_wr"]
summary = {}
for name in sorted({row[0] for row in rows}):
    values = [row[1:] for row in rows if row[0] == name]
    summary[name] = {metric: statistics.median(v[i] for v in values)
                     for i, metric in enumerate(metrics)}
    summary[name]["samples"] = len(values)
    summary[name]["ipc"] = summary[name]["instructions"] / summary[name]["cycles"]

empty = summary["empty"]
for name, result in summary.items():
    if name == "empty":
        continue
    result["net"] = {metric: result[metric] - empty[metric] for metric in metrics}
    result["net"]["ipc"] = result["net"]["instructions"] / result["net"]["cycles"]

main = summary["main_i16_x6"]["net"]
main_no = summary["main_i16_nostore_x6"]["net"]
tail = summary["tail_i16"]["net"]
tail_no = summary["tail_i16_nostore"]["net"]
summary["diagnostic_scatter_delta"] = {
    "main_x6": {m: main[m] - main_no[m] for m in metrics},
    "tail": {m: tail[m] - tail_no[m] for m in metrics},
}
full = summary["complete_inverse_to_ternary"]["net"]
parts = [summary[name]["net"] for name in
         ("inverse9_x12", "main_i16_x6", "tail_i16", "raw_to_ternary")]
summary["diagnostic_wrapper_residual"] = {
    m: full[m] - sum(part[m] for part in parts) for m in metrics
}
summary["interpretation"] = {
    "scatter_delta": "optimistic diagnostic ceiling; outputs still need a consumer",
    "wrapper_residual": "non-additive residual including wrapper setup, routing/control, scratch init/wipe, ABI save/restore, and isolated-call context differences",
}
print(json.dumps(summary, indent=2))
