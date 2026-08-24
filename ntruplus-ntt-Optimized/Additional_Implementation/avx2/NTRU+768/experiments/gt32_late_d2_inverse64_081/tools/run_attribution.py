#!/usr/bin/env python3
"""Fresh-process component attribution; report stable low-regime medians."""
from __future__ import annotations
import json
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
binary = ROOT / "build/measure"
modes = ("control-bm", "candidate-qbm", "control-inverse", "candidate-inverse",
         "control-cross", "control-norm", "candidate-naturalize",
         "candidate-inv64", "candidate-convert")
records = {}
for mode in modes:
    values = []
    for _ in range(16):
        output = subprocess.check_output(
            ["taskset", "-c", "1", str(binary), mode], text=True)
        raw = sorted(int(x) for x in output.split())
        q1 = statistics.median(raw[:len(raw)//2])
        q3 = statistics.median(raw[(len(raw)+1)//2:])
        values.append((q1 + q3) / 2)
    # The host exposes an exact ~5x frequency regime.  The lower half is the
    # stable high-frequency cluster and is used only for directional attribution.
    low = sorted(values)[:8]
    records[mode] = {"all_stq2": values, "low_cluster": low,
                     "low_cluster_median": statistics.median(low)}
report = {
    "schema": "081-component-attribution-v2",
    "cpu": 1,
    "method": "fresh process; 32 timings/process; StQ2; lower stable frequency-regime cluster",
    "records": records,
}
path = ROOT / "results/component_attribution_v2.json"
path.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({m: records[m]["low_cluster_median"] for m in modes}, indent=2))
