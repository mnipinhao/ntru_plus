#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BIN = ROOT / "build" / "bench"
variants = ("c0", "c1", "late")
components = ("forward2", "bmi2", "remaining", "complete")
iterations = {"forward2": 500000, "bmi2": 500000,
              "remaining": 500000, "complete": 250000}
result = {}
for variant in variants:
    result[variant] = {}
    for component in components:
        samples = {"cycles": [], "instructions": [], "loads": [],
                   "stores": [], "branches": []}
        for _ in range(7):
            proc = subprocess.run([
                "perf", "stat", "-j",
                "-e", "cpu_core/cycles/,cpu_core/instructions/,"
                      "cpu_core/mem_inst_retired.all_loads/,"
                      "cpu_core/mem_inst_retired.all_stores/,cpu_core/branches/",
                str(BIN), "--pmu", variant, component,
            ], text=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
            for line in proc.stderr.splitlines():
                if not line.startswith("{"):
                    continue
                row = json.loads(line)
                value = float(row["counter-value"]) / iterations[component]
                if "instructions" in row["event"]:
                    samples["instructions"].append(value)
                elif "all_loads" in row["event"]:
                    samples["loads"].append(value)
                elif "all_stores" in row["event"]:
                    samples["stores"].append(value)
                elif "branches" in row["event"]:
                    samples["branches"].append(value)
                elif "cycles" in row["event"]:
                    samples["cycles"].append(value)
        result[variant][component] = {
            key + "_per_call": statistics.median(values)
            for key, values in samples.items()
        }
    extra = {"l1d_pending": [], "idq_not_delivered": []}
    for _ in range(7):
        proc = subprocess.run([
            "perf", "stat", "-j", "-e",
            "cpu_core/l1d_pend_miss.pending/,"
            "cpu_core/idq_uops_not_delivered.core/",
            str(BIN), "--pmu", variant, "complete",
        ], text=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
           check=True)
        for line in proc.stderr.splitlines():
            if not line.startswith("{"):
                continue
            row = json.loads(line)
            value = float(row["counter-value"]) / iterations["complete"]
            if "l1d_pend_miss" in row["event"]:
                extra["l1d_pending"].append(value)
            elif "idq_uops_not_delivered" in row["event"]:
                extra["idq_not_delivered"].append(value)
    result[variant]["complete"].update({
        key + "_per_call": statistics.median(values)
        for key, values in extra.items()
    })
for component in components:
    base = result["c0"][component]
    for variant in ("c1", "late"):
        row = result[variant][component]
        row["delta_cycles"] = row["cycles_per_call"] - base["cycles_per_call"]
        row["delta_instructions"] = row["instructions_per_call"] - base["instructions_per_call"]
        row["delta_loads"] = row["loads_per_call"] - base["loads_per_call"]
        row["delta_stores"] = row["stores_per_call"] - base["stores_per_call"]
        row["delta_branches"] = row["branches_per_call"] - base["branches_per_call"]
        if component == "complete":
            row["delta_l1d_pending"] = (row["l1d_pending_per_call"]
                                         - base["l1d_pending_per_call"])
            row["delta_idq_not_delivered"] = (row["idq_not_delivered_per_call"]
                                               - base["idq_not_delivered_per_call"])
(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "results" / "pmu.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
