#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
rows = []
for launch in range(8):
    row = json.loads(subprocess.check_output([str(ROOT / "build/bench")],
                                             text=True))
    row["launch"] = launch
    rows.append(row)
result = {
    "launches": rows,
    "aggregate_median_delta_tsc": {
        key: statistics.median(row["delta_tsc"][key] for row in rows)
        for key in ("p1", "p2")
    },
    "aggregate_median_normal_delta_tsc": {
        key: statistics.median(row["normal_delta_tsc"][key] for row in rows)
        for key in ("p1", "p2")
    },
    "aggregate_median_reversed_delta_tsc": {
        key: statistics.median(row["reversed_delta_tsc"][key] for row in rows)
        for key in ("p1", "p2")
    },
}
(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "results/short.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
