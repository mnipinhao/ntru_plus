#!/usr/bin/env python3
"""Run four launches of both matched-cage placements and aggregate JSON."""

from __future__ import annotations

import json
import statistics
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent


def run(binary: Path) -> dict:
    return json.loads(subprocess.check_output([str(binary)], text=True))


def main() -> None:
    placements = {}
    for name in ("normal", "reversed"):
        launches = [run(ROOT / "build" / f"bench_{name}") for _ in range(4)]
        deltas = [record["atomic_minus_control_median_tsc"] for record in launches]
        placements[name] = {
            "launches": launches,
            "launch_median_delta_tsc": statistics.median(deltas),
            "negative_launches": sum(value < 0 for value in deltas),
            "sample_wins": sum(record["atomic_wins"] for record in launches),
            "sample_total": sum(record["samples"] for record in launches),
        }
    result = {
        "experiment": "GT32-QBM-ATOMIC-ASM-024",
        "placements": placements,
        "decision": "cycle_hard_stop_four_factor_atomic_expanded_packet",
    }
    output = ROOT / "results" / "qbm-atomic-short.json"
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(output)


if __name__ == "__main__":
    main()
