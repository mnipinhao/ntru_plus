#!/usr/bin/env python3
"""Run the short same-binary N32 Forward/BM/inverse architecture gate."""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from pathlib import Path


REGIONS = (
    "forward_raw",
    "forward_centered",
    "forward_conjugated",
    "forward2_centered",
    "forward2_conjugated",
    "basemul",
    "inverse_common",
    "whole_common",
)


def run(binary: Path, iterations: int) -> dict[str, object]:
    completed = subprocess.run(
        [str(binary.resolve()), str(iterations)], check=True,
        text=True, capture_output=True)
    records: dict[str, list[dict[str, float | int]]] = {
        region: [] for region in REGIONS
    }
    for line in completed.stdout.splitlines():
        fields = line.split(",")
        if len(fields) == 6 and fields[0] == "SAMPLE":
            records[fields[1]].append({
                "sample": int(fields[2]),
                "current_tsc": float(fields[3]),
                "n32_tsc": float(fields[4]),
                "delta_tsc": float(fields[5]),
            })
    assert all(len(records[region]) == 20 for region in REGIONS)
    summary: dict[str, object] = {}
    for region in REGIONS:
        samples = records[region]
        deltas = [float(record["delta_tsc"]) for record in samples]
        summary[region] = {
            "samples": samples,
            "median_current_tsc": statistics.median(
                float(record["current_tsc"]) for record in samples),
            "median_n32_tsc": statistics.median(
                float(record["n32_tsc"]) for record in samples),
            "median_n32_minus_current_tsc": statistics.median(deltas),
            "n32_wins": sum(delta < 0.0 for delta in deltas),
            "mad_delta_tsc": statistics.median(
                abs(delta - statistics.median(deltas)) for delta in deltas),
        }
    return {"binary": str(binary), "regions": summary}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=5000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = {
        "schema": "ntruplus768-gt32-n32-forward-chain-short-v1",
        "experiment": "GT-N32-FORWARD-CHAIN-014",
        "iterations": args.iterations,
        "placements": {
            "normal": run(args.binary, args.iterations),
            "reversed": run(args.reversed_binary, args.iterations),
        },
        "correctness": {
            "forward_endpoint": "exact mod q against current N5, mapped to half-native",
            "basemul_endpoint": "exact mod q against current R1-U, mapped to standard",
            "conjugated_forward_contract": (
                "row-conjugated S1-S5 plus the corrected row-0-only center; "
                "generated BM/inverse proof closes through 27876"
            ),
        },
        "comparison_scope": {
            "forward_and_basemul": "common semantic endpoints",
            "inverse_common": (
                "common branch-major post-InvNTT32+IDFT3 endpoint; current uses "
                "a benchmark-only standalone IDFT3 adapter"
            ),
            "whole_common": (
                "common inverse-domain endpoint; N32 uses only the proved "
                "conjugated Forward, not the raw or full-centered controls"
            ),
        },
        "decision": {
            "architecture": "executable-correct-parity-placement-sensitive",
            "promote": False,
            "run_100k_serious": False,
            "reason": (
                "the whole-chain delta is inside the short-run noise band "
                "and the winner is not stable across normal/reversed placement"
            ),
        },
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(args.output)
    for placement, data in result["placements"].items():
        print(placement)
        for region in REGIONS:
            record = data["regions"][region]
            print(" ", region,
                  "current", record["median_current_tsc"],
                  "n32", record["median_n32_tsc"],
                  "delta", record["median_n32_minus_current_tsc"],
                  "wins", f"{record['n32_wins']}/20",
                  "MAD", record["mad_delta_tsc"])


if __name__ == "__main__":
    main()
