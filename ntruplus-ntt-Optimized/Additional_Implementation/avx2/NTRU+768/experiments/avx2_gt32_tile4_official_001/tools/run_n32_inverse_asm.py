#!/usr/bin/env python3
"""Run the short, paired isolated N32 inverse attribution."""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from pathlib import Path


def run(binary: Path, iterations: int) -> dict[str, object]:
    completed = subprocess.run(
        [str(binary.resolve()), str(iterations)], check=True,
        text=True, capture_output=True)
    paired = []
    idft = []
    suffix = []
    for line in completed.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "SAMPLE" and fields[1] == "split_vs_combined":
            paired.append({
                "sample": int(fields[2]),
                "split_tsc": float(fields[3]),
                "combined_tsc": float(fields[4]),
                "delta_tsc": float(fields[5]),
            })
        elif fields[0] == "ABSOLUTE" and fields[1] == "components":
            idft.append(float(fields[3]))
            suffix.append(float(fields[4]))
    assert len(paired) == len(idft) == len(suffix) == 20
    deltas = [record["delta_tsc"] for record in paired]
    return {
        "binary": str(binary),
        "samples": paired,
        "median_split_tsc": statistics.median(
            record["split_tsc"] for record in paired),
        "median_combined_tsc": statistics.median(
            record["combined_tsc"] for record in paired),
        "median_candidate_minus_split_tsc": statistics.median(deltas),
        "candidate_wins": sum(value < 0 for value in deltas),
        "median_idft_l2_l4_tsc": statistics.median(idft),
        "median_l8_l32_tsc": statistics.median(suffix),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", type=Path, required=True)
    parser.add_argument("--iterations", type=int, default=5000)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    result = {
        "schema": "ntruplus768-gt32-n32-inverse-asm-short-v1",
        "experiment": "GT-N32-INVERSE-ASM-012",
        "iterations": args.iterations,
        "placements": {
            "normal": run(args.binary, args.iterations),
            "reversed": run(args.reversed_binary, args.iterations),
        },
        "decision_scope": (
            "isolated inverse attribution only; architecture decision remains "
            "deferred to executable 2F+B+I"
        ),
    }
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(args.output)
    for name, record in result["placements"].items():
        print(name,
              "combined", record["median_combined_tsc"],
              "delta", record["median_candidate_minus_split_tsc"],
              "wins", f"{record['candidate_wins']}/20",
              "idft", record["median_idft_l2_l4_tsc"],
              "suffix", record["median_l8_l32_tsc"])


if __name__ == "__main__":
    main()
