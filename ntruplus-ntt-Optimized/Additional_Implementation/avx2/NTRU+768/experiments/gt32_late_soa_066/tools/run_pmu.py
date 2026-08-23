#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLACEMENTS = ("normal", "reversed")
VARIANTS = ("control", "candidate")
COMPONENTS = ("post_i1", "crep", "decode_crep", "recover", "trace", "full")
ITERATIONS = {
    "post_i1": 450000,
    "crep": 240000,
    "decode_crep": 160000,
    "recover": 100000,
    "trace": 90000,
    "full": 80000,
}
PRIMARY = (
    "cpu_core/cycles/,cpu_core/instructions/,"
    "cpu_core/mem_inst_retired.all_loads/,"
    "cpu_core/mem_inst_retired.all_stores/,cpu_core/branches/"
)
FRONTEND = "cpu_core/idq_uops_not_delivered.core/"


def perf(binary: Path, variant: str, component: str, events: str) -> list[dict]:
    proc = subprocess.run(
        ["perf", "stat", "-j", "-e", events, str(binary),
         "--pmu", variant, component],
        text=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True,
    )
    return [json.loads(line) for line in proc.stderr.splitlines()
            if line.startswith("{")]


def one_counter_set(binary: Path, variant: str, component: str,
                    events: str) -> dict[str, float]:
    result = {}
    for row in perf(binary, variant, component, events):
        value = float(row["counter-value"]) / ITERATIONS[component]
        event = row["event"]
        if "instructions" in event:
            result["instructions"] = value
        elif "all_loads" in event:
            result["loads"] = value
        elif "all_stores" in event:
            result["stores"] = value
        elif "branches" in event:
            result["branches"] = value
        elif "cycles" in event:
            result["cycles"] = value
        elif "idq_uops_not_delivered" in event:
            result["idq_not_delivered"] = value
    return result


def paired_sample(binary: Path, component: str) -> tuple[dict, dict, dict]:
    metrics = ("cycles", "instructions", "loads", "stores", "branches",
               "idq_not_delivered")
    values = {variant: {metric: [] for metric in metrics}
              for variant in VARIANTS}
    paired = {metric: [] for metric in metrics}
    for pair in range(9):
        order = VARIANTS if pair % 2 == 0 else tuple(reversed(VARIANTS))
        rows = {}
        for variant in order:
            row = one_counter_set(binary, variant, component, PRIMARY)
            row.update(one_counter_set(binary, variant, component, FRONTEND))
            rows[variant] = row
            for metric in metrics:
                values[variant][metric].append(row[metric])
        for metric in metrics:
            paired[metric].append(
                rows["candidate"][metric] - rows["control"][metric])
    medians = {
        variant: {metric + "_per_call": statistics.median(series)
                  for metric, series in values[variant].items()}
        for variant in VARIANTS
    }
    deltas = {"delta_" + metric: statistics.median(series)
              for metric, series in paired.items()}
    return medians["control"], medians["candidate"], deltas


result = {}
for placement in PLACEMENTS:
    binary = ROOT / "build" / f"bench_{placement}"
    measured = {variant: {} for variant in VARIANTS}
    for component in COMPONENTS:
        control, candidate, deltas = paired_sample(binary, component)
        candidate.update(deltas)
        measured["control"][component] = control
        measured["candidate"][component] = candidate
    measured["candidate"]["integration_tax_vs_crep_cycles"] = (
        measured["candidate"]["full"]["delta_cycles"]
        - measured["candidate"]["crep"]["delta_cycles"]
    )
    result[placement] = measured

out = {
    "method": {
        "paired_runs_per_counter_set": 9,
        "delta_definition": "Late-SoA_candidate_minus_current_control",
        "core_cycles_primary": True,
        "region_scoped": True,
    },
    "placements": result,
}
(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "results" / "pmu.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps(out, indent=2))
