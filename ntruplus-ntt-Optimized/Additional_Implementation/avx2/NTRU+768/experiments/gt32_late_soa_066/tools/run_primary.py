#!/usr/bin/env python3
from __future__ import annotations

import json
import random
import statistics
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPONENTS = ("post_i1", "crep", "full")


def ci(values: list[float]) -> list[float]:
    rng = random.Random(0x066)
    boot = sorted(statistics.median(rng.choices(values, k=len(values)))
                  for _ in range(20000))
    return [boot[499], boot[19499]]


out = {
    "method": {
        "decision_binary": "lean three-component same-ELF",
        "launches_per_placement": 16,
        "paired_samples_per_launch": 41,
        "deterministic_key_ciphertext": True,
        "delta_definition": "Late-SoA_candidate_minus_current_control",
    },
    "placements": {},
}
for placement in ("normal", "reversed"):
    binary = ROOT / "build" / f"primary_{placement}"
    launches = []
    for launch in range(16):
        row = json.loads(subprocess.check_output([str(binary)], text=True).strip())
        row["launch"] = launch
        launches.append(row)
    summary = {}
    for component in COMPONENTS:
        values = [row["delta_tsc"][component] for row in launches]
        summary[component] = {
            "median_delta_tsc": statistics.median(values),
            "negative_launches": sum(value < 0 for value in values),
            "bootstrap_95_ci": ci(values),
        }
    out["placements"][placement] = {"summary": summary, "launches": launches}

(ROOT / "results").mkdir(exist_ok=True)
(ROOT / "results" / "primary.json").write_text(json.dumps(out, indent=2) + "\n")
print(json.dumps({name: row["summary"]
                  for name, row in out["placements"].items()}, indent=2))
