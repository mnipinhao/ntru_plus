#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import random
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLACEMENTS = ("normal", "reversed")
VARIANTS = ("control", "candidate")
CPU = 1
PAIRS = 17
ITERATIONS = 80000


def bootstrap_ci(values: list[float]) -> list[float]:
    rng = random.Random(0x067)
    boot = sorted(statistics.median(rng.choices(values, k=len(values)))
                  for _ in range(20000))
    return [boot[499], boot[19499]]


def perf(binary: Path, variant: str) -> dict[str, float]:
    events = "cpu_core/cycles/,cpu_core/instructions/"
    memory_events = ("cpu_core/mem_inst_retired.all_loads/,"
                     "cpu_core/mem_inst_retired.all_stores/")
    frontend_event = "cpu_core/idq_uops_not_delivered.core/"
    result: dict[str, float] = {}
    for requested in (events, memory_events, frontend_event):
        completed = subprocess.run(
            ["perf", "stat", "-j", "-e", requested,
             str(binary.resolve()), "--pmu", variant],
            text=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
            check=True, preexec_fn=lambda: os.sched_setaffinity(0, {CPU}),
        )
        for line in completed.stderr.splitlines():
            if not line.startswith("{"):
                continue
            row = json.loads(line)
            event = row["event"]
            value = float(row["counter-value"]) / ITERATIONS
            if "all_loads" in event:
                result["loads"] = value
            elif "all_stores" in event:
                result["stores"] = value
            elif "idq_uops_not_delivered" in event:
                result["idq_not_delivered"] = value
            elif "instructions" in event:
                result["instructions"] = value
            elif "cycles" in event:
                result["cycles"] = value
    return result


all_rows = {}
for placement in PLACEMENTS:
    binary = ROOT / "build" / f"bench_{placement}"
    rows = []
    for pair in range(PAIRS):
        order = VARIANTS if pair % 2 == 0 else tuple(reversed(VARIANTS))
        measured = {variant: perf(binary, variant) for variant in order}
        delta = {metric: measured["candidate"][metric]
                 - measured["control"][metric]
                 for metric in ("cycles", "instructions", "loads", "stores",
                                "idq_not_delivered")}
        rows.append({"pair": pair, "order": order, "values": measured,
                     "delta": delta})
    summary = {}
    for metric in ("cycles", "instructions", "loads", "stores",
                   "idq_not_delivered"):
        values = [row["delta"][metric] for row in rows]
        summary[metric] = {
            "paired_median_delta": statistics.median(values),
            "negative_pairs": sum(value < 0 for value in values),
            "bootstrap_95_ci": bootstrap_ci(values),
        }
    all_rows[placement] = {"summary": summary, "rows": rows}

output = {
    "schema": "gt32-late-soa-067-production-pmu-v1",
    "method": {"cpu": CPU, "pairs": PAIRS,
               "iterations_per_process": ITERATIONS,
               "delta": "candidate_minus_control"},
    "placements": all_rows,
}
(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "results" / "pmu.json").write_text(
    json.dumps(output, indent=2) + "\n")
print(json.dumps({name: row["summary"] for name, row in all_rows.items()},
                 indent=2))
