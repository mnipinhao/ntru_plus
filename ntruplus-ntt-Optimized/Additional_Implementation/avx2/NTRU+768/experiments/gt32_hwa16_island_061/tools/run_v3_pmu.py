#!/usr/bin/env python3
"""Collect region-scoped V3 core cycles and retired instructions."""

from __future__ import annotations

import json
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN = ROOT / "build" / "bench_v3"
VARIANTS = ("tile4", "m40a", "m40b", "m40c")
COMPONENTS = ("forward", "basemul", "inverse", "island")
ITERATIONS = {"forward": 1_000_000, "basemul": 1_000_000,
              "inverse": 1_000_000, "island": 300_000}
result: dict[str, dict[str, dict[str, float]]] = {}

for variant in VARIANTS:
    result[variant] = {}
    for component in COMPONENTS:
        samples = {"cycles": [], "instructions": []}
        for _ in range(7):
            proc = subprocess.run([
                "perf", "stat", "-j",
                "-e", "cpu_core/cycles/,cpu_core/instructions/",
                str(BIN), "--pmu", variant, component,
            ], text=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
               check=True)
            for line in proc.stderr.splitlines():
                if not line.startswith("{"):
                    continue
                row = json.loads(line)
                value = float(row["counter-value"]) / ITERATIONS[component]
                if "instructions" in row["event"]:
                    samples["instructions"].append(value)
                elif "cycles" in row["event"]:
                    samples["cycles"].append(value)
        result[variant][component] = {
            key + "_per_call": statistics.median(values)
            for key, values in samples.items()
        }

for component in COMPONENTS:
    base = result["tile4"][component]
    for variant in VARIANTS[1:]:
        row = result[variant][component]
        row["delta_cycles"] = row["cycles_per_call"] - base["cycles_per_call"]
        row["delta_instructions"] = (row["instructions_per_call"]
                                     - base["instructions_per_call"])

out = ROOT / "results" / "v3-pmu.json"
out.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
