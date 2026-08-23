#!/usr/bin/env python3
"""Collect median region-scoped core cycles/instructions from perf stat."""

from __future__ import annotations

import json
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN = ROOT / "build" / "bench"
variants = ("tile4", "hwa-v1", "hwa-v2")
components = ("forward", "basemul", "inverse", "island")
iterations = {"forward": 1_000_000, "basemul": 1_000_000,
              "inverse": 1_000_000, "island": 300_000}
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
            ], text=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
               check=True)
            for line in proc.stderr.splitlines():
                if not line.startswith("{"):
                    continue
                row = json.loads(line)
                event = row["event"]
                value = float(row["counter-value"]) / iterations[component]
                if "instructions" in event:
                    samples["instructions"].append(value)
                elif "cycles" in event:
                    samples["cycles"].append(value)
        result[variant][component] = {
            key + "_per_call": statistics.median(values)
            for key, values in samples.items()
        }

for component in components:
    base = result["tile4"][component]
    for variant in ("hwa-v1", "hwa-v2"):
        row = result[variant][component]
        row["delta_cycles"] = row["cycles_per_call"] - base["cycles_per_call"]
        row["delta_instructions"] = (row["instructions_per_call"]
                                     - base["instructions_per_call"])

out = ROOT / "results" / "pmu.json"
out.write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
