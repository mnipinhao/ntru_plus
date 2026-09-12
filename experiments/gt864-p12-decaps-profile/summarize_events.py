#!/usr/bin/env python3
"""Summarize P12 call-site retired-instruction and branch measurements."""

from pathlib import Path
import csv
import json
import statistics

HERE = Path(__file__).resolve().parent
rows = []
equivalence = []
for path in sorted((HERE / "raw").glob("event-*.csv")):
    for line in path.read_text().splitlines():
        if line.startswith("instrumentation_equivalence="):
            equivalence.append(line)
            continue
        row = next(csv.reader([line]))
        if row and row[0] == "profile_event":
            rows.append((row[1], row[2], row[3], row[4], float(row[5]), float(row[6]), float(row[7])))

if len(equivalence) != 24 or any("pass" not in line for line in equivalence):
    raise RuntimeError(f"incomplete instrumentation equivalence: {len(equivalence)}")

result = {}
for operation in ("keygen", "encaps", "decaps"):
    result[operation] = {}
    for implementation in ("official", "gt"):
        result[operation][implementation] = {}
        keys = sorted({(row[2], row[3]) for row in rows if row[:2] == (operation, implementation)})
        for group, metric in keys:
            values = [row[5] for row in rows if row[:4] == (operation, implementation, group, metric)]
            calls = [row[6] for row in rows if row[:4] == (operation, implementation, group, metric)]
            if len(values) != 126:
                raise RuntimeError(f"expected 126 rows for {operation}/{implementation}/{group}/{metric}, got {len(values)}")
            result[operation][implementation].setdefault(group, {})[metric] = {
                "median": statistics.median(values),
                "p25": sorted(values)[len(values)//4],
                "p75": sorted(values)[3*len(values)//4],
                "calls": statistics.median(calls),
            }

(HERE / "event-results.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
