#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN = ROOT / "build" / "bench"
variants = ("c0", "c1", "late")
components = ("suffix2", "bmi2", "full")
iterations = {"suffix2": 2_000_000, "bmi2": 2_000_000, "full": 1_000_000}
result = {}
for variant in variants:
    result[variant] = {}
    for component in components:
        samples = {"cycles": [], "instructions": []}
        for _ in range(7):
            proc = subprocess.run([
                "perf", "stat", "-j",
                "-e", "cpu_core/cycles/,cpu_core/instructions/",
                str(BIN), "--pmu", variant, component,
            ], text=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
            for line in proc.stderr.splitlines():
                if not line.startswith("{"):
                    continue
                row = json.loads(line)
                value = float(row["counter-value"]) / iterations[component]
                if "instructions" in row["event"]:
                    samples["instructions"].append(value)
                elif "cycles" in row["event"]:
                    samples["cycles"].append(value)
        result[variant][component] = {
            key + "_per_call": statistics.median(values)
            for key, values in samples.items()
        }
for component in components:
    base = result["c0"][component]
    for variant in ("c1", "late"):
        row = result[variant][component]
        row["delta_cycles"] = row["cycles_per_call"] - base["cycles_per_call"]
        row["delta_instructions"] = row["instructions_per_call"] - base["instructions_per_call"]
(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "results" / "pmu.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
