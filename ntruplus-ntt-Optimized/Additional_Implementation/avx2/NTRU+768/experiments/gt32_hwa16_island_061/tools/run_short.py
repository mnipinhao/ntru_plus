#!/usr/bin/env python3
"""Run a short multi-launch directional gate and aggregate medians."""

from __future__ import annotations

import json
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN = ROOT / "build" / "bench"
launches = []
for launch in range(8):
    raw = subprocess.check_output([str(BIN)], text=True)
    row = json.loads(raw.strip().splitlines()[-1])
    row["launch"] = launch
    launches.append(row)

summary = {"launches": launches, "aggregate_median_delta_tsc": {}}
for variant in ("v1", "v2"):
    summary["aggregate_median_delta_tsc"][variant] = {}
    for component in ("forward", "basemul", "inverse", "island"):
        values = [x["delta_tsc"][variant][component] for x in launches]
        summary["aggregate_median_delta_tsc"][variant][component] = statistics.median(values)

out = ROOT / "results" / "short.json"
out.write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2))

