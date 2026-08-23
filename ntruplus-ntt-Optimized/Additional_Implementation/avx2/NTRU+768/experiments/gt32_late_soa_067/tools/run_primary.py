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
LAUNCHES = 32
CPU = 1


def bootstrap_ci(values: list[float]) -> list[float]:
    rng = random.Random(0x067)
    boot = sorted(statistics.median(rng.choices(values, k=len(values)))
                  for _ in range(30000))
    return [boot[749], boot[29249]]


def launch(binary: Path) -> dict[str, object]:
    completed = subprocess.run(
        [str(binary.resolve())], text=True, capture_output=True, check=True,
        preexec_fn=lambda: os.sched_setaffinity(0, {CPU}),
    )
    return json.loads(completed.stdout.strip())


rows: dict[str, list[dict[str, object]]] = {name: [] for name in PLACEMENTS}
for block in range(LAUNCHES):
    order = PLACEMENTS if block % 2 == 0 else tuple(reversed(PLACEMENTS))
    for placement in order:
        row = launch(ROOT / "build" / f"bench_{placement}")
        row["launch"] = block
        rows[placement].append(row)

summary = {}
for placement in PLACEMENTS:
    values = [float(row["delta_tsc"]) for row in rows[placement]]
    interval = bootstrap_ci(values)
    favorable = sum(value < 0 for value in values)
    summary[placement] = {
        "median_delta_tsc": statistics.median(values),
        "negative_launches": favorable,
        "launches": LAUNCHES,
        "bootstrap_95_ci": interval,
        "ci_pass": interval[1] < 0,
        "near_all_launch_target_pass": favorable >= 28,
    }

output = {
    "schema": "gt32-late-soa-067-production-paired-v1",
    "method": {
        "cpu": CPU,
        "aslr": "enabled",
        "launches_per_placement": LAUNCHES,
        "paired_samples_per_launch": 61,
        "iterations_per_variant_per_sample": 350,
        "placement_order": "NR/RN alternating",
        "variant_order": "control/candidate alternating in each launch",
        "delta": "candidate_minus_control",
    },
    "summary": summary,
    "rows": rows,
}
(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "results" / "primary.json").write_text(
    json.dumps(output, indent=2) + "\n")
print(json.dumps(summary, indent=2))
