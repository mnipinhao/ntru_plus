#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rows = []
for launch in range(8):
    raw = subprocess.check_output([str(ROOT / "build" / "bench")], text=True)
    row = json.loads(raw.strip().splitlines()[-1])
    row["launch"] = launch
    rows.append(row)

summary = {"launches": rows, "aggregate_median_delta_tsc": {}}
for variant in ("c1", "late"):
    summary["aggregate_median_delta_tsc"][variant] = {}
    for component in ("suffix2", "bmi2", "full"):
        summary["aggregate_median_delta_tsc"][variant][component] = statistics.median(
            row["delta_tsc"][variant][component] for row in rows
        )
(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "results" / "short.json").write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))
