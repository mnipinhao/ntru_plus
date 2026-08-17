#!/usr/bin/env python3
"""Summarize the bounded Priority-1/2 executable gates."""

from __future__ import annotations

import json
import statistics
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_i112(binary: str) -> dict[str, object]:
    text = subprocess.run([str(ROOT / binary), "5000"], check=True,
                          text=True, capture_output=True).stdout
    values: dict[str, str] = {}
    for line in text.splitlines():
        key, value = line.split()
        values[key] = value
    return {
        "control_tsc": float(values["control"]),
        "candidate_tsc": float(values["candidate"]),
        "delta_tsc": float(values["delta"]),
        "wins": values["wins"],
    }


def run_half(binary: str) -> dict[str, object]:
    text = subprocess.run([str(ROOT / binary), "5000"], check=True,
                          text=True, capture_output=True).stdout
    rows = []
    for line in text.splitlines():
        fields = line.split(",")
        if len(fields) == 6 and fields[0] == "SAMPLE":
            rows.append({
                "sample": int(fields[2]),
                "control_tsc": float(fields[3]),
                "candidate_tsc": float(fields[4]),
                "delta_tsc": float(fields[5]),
            })
    assert len(rows) == 20
    # The first timed call occasionally carries a one-off environment event;
    # retain all samples in the artifact and use the robust median as primary.
    deltas = [float(row["delta_tsc"]) for row in rows]
    return {
        "samples": rows,
        "median_control_tsc": statistics.median(
            float(row["control_tsc"]) for row in rows),
        "median_candidate_tsc": statistics.median(
            float(row["candidate_tsc"]) for row in rows),
        "median_delta_tsc": statistics.median(deltas),
        "candidate_wins": sum(delta < 0 for delta in deltas),
        "mad_delta_tsc": statistics.median(
            abs(delta - statistics.median(deltas)) for delta in deltas),
    }


def main() -> None:
    result = {
        "schema": "ntruplus768-gt32-priority12-executable-v1",
        "priority1_i112": {
            "correctness": (
                "1000-trial M<->I112, bounded entry, and BM+inverse common-"
                "AoS endpoint pass"
            ),
            "placements": {
                "normal": run_i112("build/bench_i112"),
                "reversed": run_i112("build/bench_i112_reversed"),
            },
            "decision": "cycle-hard-stop",
            "reason": (
                "the generated zero-instruction inverse-consumer assertion was "
                "not executable; the exact entry needs four half permutes per "
                "tile and the candidate is slower in both placements"
            ),
        },
        "priority2_n5_half_terminal": {
            "correctness": "1000-trial exact N5-to-half-native route pass",
            "route": {
                "vperm2i128": 32,
                "source_loads": 48,
                "destination_stores": 48,
                "reason_materialized": (
                    "N5 completes one 8-vector (k3,branch) tile at a time; "
                    "half-native output needs three k3 tiles, or 24 live data YMM"
                ),
            },
            "placements": {
                "normal": run_half("build/bench_n5_half_chain"),
                "reversed": run_half("build/bench_n5_half_chain_reversed"),
            },
            "decision": "cycle-hard-stop",
        },
    }
    path = ROOT / "results/tile4-priority12-executable-short.json"
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(path)


if __name__ == "__main__":
    main()
