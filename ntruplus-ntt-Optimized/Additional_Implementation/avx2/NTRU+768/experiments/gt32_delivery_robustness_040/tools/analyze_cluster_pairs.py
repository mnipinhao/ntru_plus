#!/usr/bin/env python3
"""Summarize paired per-block relocation effects with deterministic bootstrap CIs."""

from __future__ import annotations

import json
import pathlib
import random
import statistics

EXP = pathlib.Path(__file__).resolve().parents[1]
SOURCE = EXP / "results/cluster_sensitivity_curve.json"
DESTINATION = EXP / "results/cluster_paired_summary.json"
OPERATIONS = ("keypair_cycles", "enc_cycles", "dec_cycles")


def bootstrap_ci(values: list[float], seed: int) -> list[float]:
    generator = random.Random(seed)
    medians = []
    for _ in range(20000):
        sample = [values[generator.randrange(len(values))] for _ in values]
        medians.append(statistics.median(sample))
    medians.sort()
    return [medians[int(0.025 * len(medians))],
            medians[int(0.975 * len(medians))]]


def main() -> None:
    source = json.loads(SOURCE.read_text())
    result = {"blocks": source["blocks"], "clusters": {}}
    for cluster_index, record in enumerate(source["records"]):
        points = {point["offset"]: point for point in record["points"]}
        baseline = points[0]
        comparisons = {}
        for offset in sorted(points):
            if offset == 0:
                continue
            comparisons[f"0x{offset:04x}-0x0000"] = {}
            for operation_index, operation in enumerate(OPERATIONS):
                control = baseline["launch_medians"][operation]
                candidate = points[offset]["launch_medians"][operation]
                deltas = [b - a for a, b in zip(control, candidate)]
                comparisons[f"0x{offset:04x}-0x0000"][operation] = {
                    "median_delta": statistics.median(deltas),
                    "negative_blocks": sum(value < 0 for value in deltas),
                    "positive_blocks": sum(value > 0 for value in deltas),
                    "zero_blocks": sum(value == 0 for value in deltas),
                    "bootstrap_95_ci": bootstrap_ci(
                        deltas, 4000 + cluster_index * 10 + operation_index
                        + offset
                    ),
                }
        result["clusters"][record["cluster"]] = comparisons
    DESTINATION.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
