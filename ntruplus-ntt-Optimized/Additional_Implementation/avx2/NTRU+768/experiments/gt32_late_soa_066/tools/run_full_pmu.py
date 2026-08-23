#!/usr/bin/env python3
from __future__ import annotations

import json
import random
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ITERATIONS = 80000
PAIRS = 17


def perf(binary: Path, variant: str, events: str) -> dict[str, float]:
    proc = subprocess.run(
        ["perf", "stat", "-j", "-e", events, str(binary),
         "--pmu", variant, "full"],
        text=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True,
    )
    result = {}
    for line in proc.stderr.splitlines():
        if not line.startswith("{"):
            continue
        row = json.loads(line)
        value = float(row["counter-value"]) / ITERATIONS
        if "instructions" in row["event"]:
            result["instructions"] = value
        elif "cycles" in row["event"]:
            result["cycles"] = value
        elif "idq_uops_not_delivered" in row["event"]:
            result["idq_not_delivered"] = value
    return result


def bootstrap_ci(values: list[float]) -> list[float]:
    rng = random.Random(0x066)
    boot = sorted(statistics.median(rng.choices(values, k=len(values)))
                  for _ in range(20000))
    return [boot[499], boot[19499]]


out = {
    "method": {
        "scope": "full Decap only",
        "paired_process_launches": PAIRS,
        "iterations_per_process": ITERATIONS,
        "deterministic_key_ciphertext": True,
        "alternating_order": True,
    },
    "placements": {},
}
for placement in ("normal", "reversed"):
    binary = ROOT / "build" / f"bench_{placement}"
    rows = []
    for pair in range(PAIRS):
        order = ("control", "candidate") if pair % 2 == 0 else (
            "candidate", "control")
        values = {}
        for variant in order:
            row = perf(binary, variant,
                       "cpu_core/cycles/,cpu_core/instructions/")
            row.update(perf(binary, variant,
                            "cpu_core/idq_uops_not_delivered.core/"))
            values[variant] = row
        delta = {key: values["candidate"][key] - values["control"][key]
                 for key in ("cycles", "instructions", "idq_not_delivered")}
        rows.append({"pair": pair, "order": order, "values": values,
                     "delta": delta})
    summary = {}
    for metric in ("cycles", "instructions", "idq_not_delivered"):
        values = [row["delta"][metric] for row in rows]
        summary[metric] = {
            "paired_median_delta": statistics.median(values),
            "negative_pairs": sum(value < 0 for value in values),
            "bootstrap_95_ci": bootstrap_ci(values),
        }
    out["placements"][placement] = {"summary": summary, "rows": rows}

(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "results" / "full_pmu.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({name: row["summary"]
                  for name, row in out["placements"].items()}, indent=2))
