#!/usr/bin/env python3
"""Time identical shared Encap consumers after Official and GT predecessors."""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
from pathlib import Path

STAGES = ("shared_prework", "middle_glue", "shared_tail")


def one(binary: Path, stage: str, impl: str, iterations: int) -> float:
    command = [
        "setarch", "x86_64", "-R", str(binary),
        "--transition-tsc", stage, impl, str(iterations),
    ]
    proc = subprocess.run(command, check=True, capture_output=True, text=True)
    line = next(line for line in proc.stdout.splitlines()
                if line.startswith("TRANSITION,"))
    return float(line.split(",")[3])


def pair(binary: Path, stage: str, iterations: int, index: int) -> float:
    order = ("official", "gt", "gt", "official")
    if index & 1:
        order = tuple(reversed(order))
    rows = {"official": [], "gt": []}
    for impl in order:
        rows[impl].append(one(binary, stage, impl, iterations))
    return statistics.mean(rows["gt"]) - statistics.mean(rows["official"])


def summarize(values: list[float]) -> dict:
    return {
        "median_delta_tsc": statistics.median(values),
        "min": min(values),
        "max": max(values),
        "gt_favorable": sum(value < 0 for value in values),
        "pairs": len(values),
        "paired_deltas": values,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=10100)
    parser.add_argument("--pairs", type=int, default=8)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    placements = {}
    for placement, binary in (("normal", args.binary),
                              ("reversed", args.reversed_binary)):
        placements[placement] = {
            stage: summarize([
                pair(binary, stage, args.iterations, index)
                for index in range(args.pairs)
            ])
            for stage in STAGES
        }

    output = {
        "schema": "ntruplus768-gt32-encap-shared-transition-tsc-v1",
        "experiment": "SAME-ELF-ENCAP-SHARED-CONSUMER-CAUSAL-001",
        "aslr": "disabled-with-setarch-R",
        "cpu_affinity": 1,
        "pairing": "ABBA/BAAB across process launches",
        "measurement": (
            "median of 101 within-process batch means; TSC brackets only "
            "the identical shared noinline/noclone consumer"
        ),
        "iterations_requested": args.iterations,
        "pairs": args.pairs,
        "placements": placements,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    for placement, stages in placements.items():
        print(placement)
        for stage, result in stages.items():
            print(f"  {stage}: {result['median_delta_tsc']:+.3f} TSC "
                  f"({result['gt_favorable']}/{result['pairs']} GT wins)")


if __name__ == "__main__":
    main()
