#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLACEMENTS = ("normal", "reversed")
VARIANTS = ("c0", "c1", "late")
COMPONENTS = ("frontend2", "arithmetic", "tail", "full")
ITERATIONS = {
    "frontend2": 400000,
    "arithmetic": 220000,
    "tail": 400000,
    "full": 150000,
}
EVENTS = (
    "cpu_core/cycles/,cpu_core/instructions/,"
    "cpu_core/mem_inst_retired.all_loads/,"
    "cpu_core/mem_inst_retired.all_stores/,cpu_core/branches/"
)
EXTRA_EVENTS = (
    "cpu_core/l1d_pend_miss.pending/,"
    "cpu_core/idq_uops_not_delivered.core/"
)


def perf(binary: Path, variant: str, component: str, events: str) -> list[dict]:
    proc = subprocess.run(
        ["perf", "stat", "-j", "-e", events, str(binary), "--pmu", variant, component],
        text=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        check=True,
    )
    return [json.loads(line) for line in proc.stderr.splitlines() if line.startswith("{")]


def primary_sample(binary: Path, variant: str, component: str) -> dict[str, float]:
    samples = {key: [] for key in ("cycles", "instructions", "loads", "stores", "branches")}
    for _ in range(5):
        for row in perf(binary, variant, component, EVENTS):
            value = float(row["counter-value"]) / ITERATIONS[component]
            event = row["event"]
            if "instructions" in event:
                samples["instructions"].append(value)
            elif "all_loads" in event:
                samples["loads"].append(value)
            elif "all_stores" in event:
                samples["stores"].append(value)
            elif "branches" in event:
                samples["branches"].append(value)
            elif "cycles" in event:
                samples["cycles"].append(value)
    return {key + "_per_call": statistics.median(values) for key, values in samples.items()}


def extra_sample(binary: Path, variant: str) -> dict[str, float]:
    samples = {"l1d_pending": [], "idq_not_delivered": []}
    for _ in range(5):
        for row in perf(binary, variant, "full", EXTRA_EVENTS):
            value = float(row["counter-value"]) / ITERATIONS["full"]
            if "l1d_pend_miss" in row["event"]:
                samples["l1d_pending"].append(value)
            elif "idq_uops_not_delivered" in row["event"]:
                samples["idq_not_delivered"].append(value)
    return {key + "_per_call": statistics.median(values) for key, values in samples.items()}


result: dict[str, dict] = {}
for placement in PLACEMENTS:
    binary = ROOT / "build" / f"bench_{placement}"
    measured: dict[str, dict] = {}
    for variant in VARIANTS:
        measured[variant] = {}
        for component in COMPONENTS:
            measured[variant][component] = primary_sample(binary, variant, component)
        measured[variant]["full"].update(extra_sample(binary, variant))
    for component in COMPONENTS:
        base = measured["c0"][component]
        for variant in ("c1", "late"):
            row = measured[variant][component]
            for metric in ("cycles", "instructions", "loads", "stores", "branches"):
                row["delta_" + metric] = row[metric + "_per_call"] - base[metric + "_per_call"]
            if component == "full":
                for metric in ("l1d_pending", "idq_not_delivered"):
                    row["delta_" + metric] = (
                        row[metric + "_per_call"] - base[metric + "_per_call"]
                    )
    for variant in ("c1", "late"):
        measured[variant]["integration_closure_delta_cycles"] = (
            measured[variant]["full"]["delta_cycles"]
            - measured[variant]["arithmetic"]["delta_cycles"]
        )
        measured[variant]["integration_closure_delta_instructions"] = (
            measured[variant]["full"]["delta_instructions"]
            - measured[variant]["arithmetic"]["delta_instructions"]
        )
    result[placement] = measured

out = {
    "method": {
        "runs_per_counter_set": 5,
        "delta_definition": "candidate_minus_C0",
        "core_cycles_primary": True,
    },
    "placements": result,
}
(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "results" / "pmu.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
