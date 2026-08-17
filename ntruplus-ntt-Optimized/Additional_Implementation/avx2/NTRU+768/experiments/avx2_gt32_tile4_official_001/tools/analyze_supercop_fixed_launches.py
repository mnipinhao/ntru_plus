#!/usr/bin/env python3
"""Summarize matched TF1/SP1 SUPERcop launches and ABBA block deltas."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from analyze_supercop_matrix import OPS, parse_result, stabilized_quartiles


def median(values: list[float]) -> float:
    ordered = sorted(values)
    size = len(ordered)
    middle = size // 2
    if size % 2:
        return ordered[middle]
    return (ordered[middle - 1] + ordered[middle]) / 2


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("result_dirs", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    launches: list[dict[str, object]] = []
    for result_dir in sorted(args.result_dirs, key=lambda path: path.name):
        parsed = parse_result(result_dir)
        compiler = str(parsed["compiler"])
        optimization = "O3" if "_-O3_" in compiler else "O2"
        variant = "sp1" if "q24-sp1-fixed" in result_dir.name else "tf1"
        operations = {}
        for operation in OPS:
            values = parsed["measurements"][operation]
            operations[operation] = {
                "observations": len(values),
                "q2_cycles": stabilized_quartiles(values)[1],
            }
        launches.append(
            {
                "result_dir": str(result_dir),
                "optimization": optimization,
                "variant": variant,
                "operations": operations,
            }
        )

    summary: dict[str, object] = {}
    for optimization in ("O2", "O3"):
        cells = [item for item in launches if item["optimization"] == optimization]
        variants = {}
        for variant in ("tf1", "sp1"):
            selected = [item for item in cells if item["variant"] == variant]
            variants[variant] = {
                operation: {
                    "launches": len(selected),
                    "launch_q2_cycles": [
                        item["operations"][operation]["q2_cycles"] for item in selected
                    ],
                    "median_launch_q2_cycles": median(
                        [item["operations"][operation]["q2_cycles"] for item in selected]
                    ),
                }
                for operation in OPS
            }
        deltas = {}
        for operation in OPS:
            tf1 = variants["tf1"][operation]["median_launch_q2_cycles"]
            sp1 = variants["sp1"][operation]["median_launch_q2_cycles"]
            deltas[operation] = sp1 - tf1
        summary[optimization] = {"variants": variants, "sp1_minus_tf1": deltas}

    output = {
        "schema": "gt32-q24-fixed-geometry-launches-v1",
        "estimator": "median of per-launch SUPERcop stabilized Q2",
        "launches": launches,
        "summary": summary,
    }
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
