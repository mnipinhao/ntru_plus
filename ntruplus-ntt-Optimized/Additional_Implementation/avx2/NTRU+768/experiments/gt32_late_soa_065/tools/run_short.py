#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPONENTS = ("frontend2", "arithmetic", "tail", "full")
VARIANTS = ("c1", "late")


def one_placement(name: str) -> dict:
    binary = ROOT / "build" / f"bench_{name}"
    launches = []
    for launch in range(8):
        raw = subprocess.check_output([str(binary)], text=True)
        row = json.loads(raw.strip().splitlines()[-1])
        row["launch"] = launch
        launches.append(row)
    aggregate: dict[str, dict[str, float]] = {}
    negative: dict[str, dict[str, int]] = {}
    for variant in VARIANTS:
        aggregate[variant] = {}
        negative[variant] = {}
        for component in COMPONENTS:
            values = [row["delta_tsc"][variant][component] for row in launches]
            aggregate[variant][component] = statistics.median(values)
            negative[variant][component] = sum(value < 0 for value in values)
        aggregate[variant]["integration_closure"] = (
            aggregate[variant]["full"] - aggregate[variant]["arithmetic"]
        )
    return {
        "binary": str(binary.relative_to(ROOT)),
        "launches": launches,
        "aggregate_median_delta_tsc": aggregate,
        "negative_launches": negative,
    }


result = {
    "method": {
        "placements": ["normal", "reversed"],
        "launches_per_placement": 8,
        "paired_samples_per_launch": 41,
        "alternating_order": True,
        "delta_definition": "candidate_minus_C0",
        "integration_closure": "full_delta_minus_arithmetic_delta",
    },
    "placements": {
        "normal": one_placement("normal"),
        "reversed": one_placement("reversed"),
    },
}
(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "results" / "short.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
