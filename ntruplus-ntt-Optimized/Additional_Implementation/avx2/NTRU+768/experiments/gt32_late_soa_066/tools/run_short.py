#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PLACEMENTS = ("normal", "reversed")
COMPONENTS = ("post_i1", "crep", "decode_crep", "recover", "trace", "full")


def one_placement(name: str) -> dict:
    binary = ROOT / "build" / f"bench_{name}"
    launches = []
    for launch in range(8):
        row = json.loads(subprocess.check_output([str(binary)], text=True).strip())
        row["launch"] = launch
        launches.append(row)
    aggregate = {}
    negative = {}
    for component in COMPONENTS:
        values = [row["delta_tsc"][component] for row in launches]
        aggregate[component] = statistics.median(values)
        negative[component] = sum(value < 0 for value in values)
    aggregate["integration_tax_vs_crep"] = aggregate["full"] - aggregate["crep"]
    return {
        "binary": str(binary.relative_to(ROOT)),
        "launches": launches,
        "aggregate_median_delta_tsc": aggregate,
        "negative_launches": negative,
    }


result = {
    "method": {
        "placements": list(PLACEMENTS),
        "launches_per_placement": 8,
        "paired_samples_per_launch": 41,
        "alternating_order": True,
        "delta_definition": "Late-SoA_candidate_minus_current_control",
        "full_is_primary": True,
    },
    "placements": {name: one_placement(name) for name in PLACEMENTS},
}
(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "results" / "short.json").write_text(json.dumps(result, indent=2) + "\n")
print(json.dumps(result, indent=2))
