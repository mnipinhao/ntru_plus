#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN = ROOT / "build/bench"
result = {}
for variant in ("p0", "p1", "p2"):
    samples = {"cycles": [], "instructions": []}
    for _ in range(7):
        proc = subprocess.run([
            "perf", "stat", "-j",
            "-e", "cpu_core/cycles/,cpu_core/instructions/",
            str(BIN), "--pmu", variant,
        ], text=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
           check=True)
        for line in proc.stderr.splitlines():
            if not line.startswith("{"):
                continue
            row = json.loads(line)
            value = float(row["counter-value"]) / 1_000_000
            if "instructions" in row["event"]:
                samples["instructions"].append(value)
            elif "cycles" in row["event"]:
                samples["cycles"].append(value)
    result[variant] = {
        key + "_per_call": statistics.median(values)
        for key, values in samples.items()
    }
base = result["p0"]
for variant in ("p1", "p2"):
    result[variant]["delta_cycles"] = (
        result[variant]["cycles_per_call"] - base["cycles_per_call"])
    result[variant]["delta_instructions"] = (
        result[variant]["instructions_per_call"]
        - base["instructions_per_call"])
(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "results/pmu.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
