#!/usr/bin/env python3
"""Two-placement 100k paired full-encapsulation benchmark."""

import argparse
import json
import statistics
import subprocess
from pathlib import Path


def run(binary: Path, iterations: int) -> dict:
    process = subprocess.run([str(binary), str(iterations)], check=True,
                             text=True, capture_output=True)
    valid = False
    official = []
    gt = []
    delta = []
    for line in process.stdout.splitlines():
        fields = line.split(",")
        if fields[0] == "META":
            valid = ("correctness=byte-exact-pass" in line
                     and f"iterations={iterations}" in line)
        elif fields[0:2] == ["FULL", "encap"]:
            official.append(float(fields[3]))
            gt.append(float(fields[4]))
            delta.append(float(fields[5]))
    if not valid or len(delta) != 20:
        raise RuntimeError(f"invalid full encap output from {binary}")
    median = statistics.median(delta)
    return {
        "binary": str(binary),
        "official_median_tsc": statistics.median(official),
        "gt_median_tsc": statistics.median(gt),
        "paired_delta_median_tsc": median,
        "paired_delta_mad_tsc": statistics.median(
            abs(value - median) for value in delta),
        "gt_wins": sum(value < 0 for value in delta),
        "samples": len(delta),
        "deltas": delta,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("binary", type=Path)
    parser.add_argument("--reversed-binary", required=True, type=Path)
    parser.add_argument("--iterations", type=int, default=100000)
    parser.add_argument("--output", type=Path,
                        default=Path("results/tile4-encap-full-serious.json"))
    args = parser.parse_args()
    placements = {
        "normal": run(args.binary, args.iterations),
        "reversed": run(args.reversed_binary, args.iterations),
    }
    result = {
        "schema": "ntruplus768-gt32-encap-full-serious-v1",
        "iterations_per_sample": args.iterations,
        "samples_per_placement": 20,
        "correctness": "byte-exact",
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
              f"wins={value['gt_wins']}/{value['samples']}")
    print(f"decision={result['decision']}")


if __name__ == "__main__":
    main()
