#!/usr/bin/env python3
"""Fresh-launch SUPERcop-style comparison of independent Official and GT ELFs."""

from __future__ import annotations

import json
import pathlib
import random
import re
import statistics
import subprocess

EXP = pathlib.Path(__file__).resolve().parents[1]
BUILD = EXP / "build"
RESULTS = EXP / "results"
RAW = RESULTS / "raw"
BINARIES = {
    "official": BUILD / "official-measure",
    "gt_clean": BUILD / "gt-clean-measure",
}
OPERATIONS = ("keypair", "enc", "dec")


def decode_line(line: str) -> list[int]:
    fields = line.split()
    base = int(fields[-2])
    deviations = [int(item) for item in re.findall(r"[+-]\d+", fields[-1])]
    return [base + item for item in deviations]


def observations(text: str) -> dict[str, list[int]]:
    result = {operation: [] for operation in OPERATIONS}
    for line in text.splitlines():
        for operation in OPERATIONS:
            if f" {operation}_cycles " in f" {line} ":
                result[operation].extend(decode_line(line))
    if any(len(values) < 96 for values in result.values()):
        raise RuntimeError({key: len(value) for key, value in result.items()})
    return result


def stabilized_quartiles(values: list[int]) -> list[float]:
    expanded = sorted(value for value in values for _ in range(8))
    count = len(values)
    return [
        sum(expanded[count + 2 * count * index:
                     count + 2 * count * (index + 1)]) / (2 * count)
        for index in range(3)
    ]


def bootstrap_ci(values: list[float], seed: int) -> list[float]:
    generator = random.Random(seed)
    medians = []
    for _ in range(30000):
        sample = [values[generator.randrange(len(values))] for _ in values]
        medians.append(statistics.median(sample))
    medians.sort()
    return [medians[int(0.025 * len(medians))],
            medians[int(0.975 * len(medians))]]


def launch(binary: pathlib.Path) -> tuple[str, dict[str, list[int]]]:
    completed = subprocess.run(
        ["taskset", "-c", "1", str(binary.resolve())],
        text=True, capture_output=True,
    )
    if completed.returncode:
        raise RuntimeError(completed.stdout + completed.stderr)
    return completed.stdout, observations(completed.stdout)


def main() -> None:
    blocks = 16
    RAW.mkdir(parents=True, exist_ok=True)
    launches = []
    run_number = 0
    for block in range(blocks):
        sequence = ("official", "gt_clean", "gt_clean", "official")
        if block & 1:
            sequence = tuple(reversed(sequence))
        for position, implementation in enumerate(sequence, 1):
            run_number += 1
            output, measured = launch(BINARIES[implementation])
            raw_path = RAW / f"run-{run_number:03d}-block-{block + 1:02d}-pos-{position}-{implementation}.out"
            raw_path.write_text(output)
            launches.append({
                "run": run_number,
                "block": block + 1,
                "position": position,
                "implementation": implementation,
                "raw": str(raw_path),
                "observations": measured,
                "launch_q2": {
                    operation: stabilized_quartiles(measured[operation])[1]
                    for operation in OPERATIONS
                },
            })

    aggregate = {}
    for implementation in BINARIES:
        aggregate[implementation] = {}
        selected = [entry for entry in launches
                    if entry["implementation"] == implementation]
        for operation in OPERATIONS:
            values = [value for entry in selected
                      for value in entry["observations"][operation]]
            quartiles = stabilized_quartiles(values)
            launch_q2 = [entry["launch_q2"][operation] for entry in selected]
            aggregate[implementation][operation] = {
                "observations": len(values),
                "launches": len(selected),
                "stabilized_quartiles": quartiles,
                "q2_cycles": quartiles[1],
                "launch_q2_min": min(launch_q2),
                "launch_q2_median": statistics.median(launch_q2),
                "launch_q2_max": max(launch_q2),
            }

    blocks_encoded = []
    for block in range(1, blocks + 1):
        selected = [entry for entry in launches if entry["block"] == block]
        operations = {}
        for operation in OPERATIONS:
            q2 = {implementation: statistics.mean(
                entry["launch_q2"][operation] for entry in selected
                if entry["implementation"] == implementation
            ) for implementation in BINARIES}
            operations[operation] = {
                **q2,
                "gt_minus_official": q2["gt_clean"] - q2["official"],
            }
        blocks_encoded.append({"block": block, "operations": operations})

    comparisons = {}
    for index, operation in enumerate(OPERATIONS):
        official = aggregate["official"][operation]["q2_cycles"]
        gt = aggregate["gt_clean"][operation]["q2_cycles"]
        deltas = [entry["operations"][operation]["gt_minus_official"]
                  for entry in blocks_encoded]
        comparisons[operation] = {
            "official_q2_cycles": official,
            "gt_q2_cycles": gt,
            "aggregate_gt_minus_official": gt - official,
            "relative_percent": 100.0 * (gt - official) / official,
            "paired_block_median_delta": statistics.median(deltas),
            "favorable_blocks": sum(value < 0 for value in deltas),
            "blocks": blocks,
            "bootstrap_95_ci": bootstrap_ci(deltas, 20260820 + index),
            "block_deltas": deltas,
        }

    result = {
        "schema": "ntruplus768-supercop-clean-fresh-launch-v1",
        "date": "2026-08-20",
        "cpu": 1,
        "aslr": "enabled",
        "sequence": "OGGO / GOOG alternating",
        "estimator": "SUPERcop stabilized quartiles; Q2 primary",
        "binaries": {key: str(value.resolve()) for key, value in BINARIES.items()},
        "aggregate": aggregate,
        "comparisons": comparisons,
        "blocks_detail": blocks_encoded,
        "launches": launches,
    }
    destination = RESULTS / "supercop_style_aslr_on.json"
    destination.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(comparisons, indent=2))


if __name__ == "__main__":
    main()
