#!/usr/bin/env python3
"""Two-placement 100k paired production-shaped keygen benchmark."""

import argparse
import json
import re
import statistics
import subprocess
from pathlib import Path


def one(binary: Path, iterations: int, backend: str) -> float:
    process = subprocess.run(
        [str(binary), str(iterations), "g1", backend], check=True,
        text=True, capture_output=True)
    match = re.search(r"tsc_per_call=([0-9.]+)", process.stdout)
    if match is None or "correctness=pass" not in process.stdout:
        raise RuntimeError(f"invalid keygen output from {binary}")
    return float(match.group(1))


def run(binary: Path, iterations: int, pairs: int) -> dict:
    official = []
    gt = []
    for pair in range(pairs):
        order = (("official", "gt32-prod") if pair % 2 == 0
                 else ("gt32-prod", "official"))
        values = {backend: one(binary, iterations, backend)
                  for backend in order}
        official.append(values["official"])
        gt.append(values["gt32-prod"])
    delta = [candidate - control for control, candidate
             in zip(official, gt, strict=True)]
    median = statistics.median(delta)
    return {
        "binary": str(binary),
        "official_median_tsc": statistics.median(official),
        "gt_median_tsc": statistics.median(gt),
        "paired_delta_median_tsc": median,
        "paired_delta_mad_tsc": statistics.median(
            abs(value - median) for value in delta),
        "gt_wins": sum(value < 0 for value in delta),
        "pairs": pairs,
        "deltas": delta,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=100000)
    parser.add_argument("--pairs", type=int, default=20)
    parser.add_argument("--output", type=Path,
                        default=Path("results/tile4-keygen-full-serious-100k.json"))
    args = parser.parse_args()
    placements = {
        "normal": run(args.binary, args.iterations, args.pairs),
        "reversed": run(args.reversed_binary, args.iterations, args.pairs),
    }
    result = {
        "schema": "ntruplus768-gt32-keygen-full-serious-v1",
        "gate": "G1 deterministic single-attempt production-shaped caller",
        "iterations_per_pair": args.iterations,
        "pairs_per_placement": args.pairs,
        "correctness": "1024 shared scenarios plus targeted failure gate",
        "placements": placements,
        "decision": ("pass" if all(
            value["paired_delta_median_tsc"] < 0
            and value["gt_wins"] >= 18
            for value in placements.values()) else "not-promoted"),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    for name, value in placements.items():
        print(f"{name}: official={value['official_median_tsc']:.3f} "
              f"gt={value['gt_median_tsc']:.3f} "
              f"delta={value['paired_delta_median_tsc']:+.3f} "
              f"wins={value['gt_wins']}/{value['pairs']}")
    print(f"decision={result['decision']}")


if __name__ == "__main__":
    main()
