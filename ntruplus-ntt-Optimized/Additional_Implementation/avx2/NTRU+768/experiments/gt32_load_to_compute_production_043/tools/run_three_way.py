#!/usr/bin/env python3
"""Three-way fresh-launch SUPERcop exact-image campaign."""

from __future__ import annotations

import argparse
import hashlib
import json
import random
import re
import statistics
import subprocess
from pathlib import Path

IMPLEMENTATIONS = ("official", "gt_clean", "gt_db")
OPERATIONS = ("keypair", "enc", "dec")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


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
    return [sum(expanded[count + 2 * count * index:
                         count + 2 * count * (index + 1)]) / (2 * count)
            for index in range(3)]


def bootstrap_ci(values: list[float], seed: int) -> list[float]:
    rng = random.Random(seed)
    samples = sorted(statistics.median(rng.choices(values, k=len(values)))
                     for _ in range(30000))
    return [samples[749], samples[29249]]


def launch(binary: Path, cpu: int) -> tuple[str, dict[str, list[int]]]:
    completed = subprocess.run(["taskset", "-c", str(cpu), str(binary.resolve())],
                               text=True, capture_output=True)
    if completed.returncode:
        raise RuntimeError(completed.stdout + completed.stderr)
    return completed.stdout, observations(completed.stdout)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--official", type=Path, required=True)
    parser.add_argument("--gt-clean", type=Path, required=True)
    parser.add_argument("--gt-db", type=Path, required=True)
    parser.add_argument("--cpu", type=int, default=1)
    parser.add_argument("--blocks", type=int, default=16)
    parser.add_argument("--warmup-launches", type=int, default=4)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    binaries = {name: getattr(args, name).resolve()
                for name in IMPLEMENTATIONS}
    raw = args.output / "raw"
    raw.mkdir(parents=True, exist_ok=False)

    # SUPERcop's short measure process can begin before the pinned core has
    # reached its steady performance state.  Warm every exact ELF equally and
    # discard these launches before collecting the balanced blocks.
    for _ in range(args.warmup_launches):
        for implementation in IMPLEMENTATIONS:
            launch(binaries[implementation], args.cpu)

    rotations = (
        ("official", "gt_clean", "gt_db", "gt_db", "gt_clean", "official"),
        ("gt_clean", "gt_db", "official", "official", "gt_db", "gt_clean"),
        ("gt_db", "official", "gt_clean", "gt_clean", "official", "gt_db"),
    )
    launches = []
    run = 0
    for block in range(1, args.blocks + 1):
        order = rotations[(block - 1) % len(rotations)]
        for position, implementation in enumerate(order, 1):
            run += 1
            text, measured = launch(binaries[implementation], args.cpu)
            path = raw / f"run-{run:03d}-block-{block:02d}-pos-{position}-{implementation}.out"
            path.write_text(text)
            launches.append({"run": run, "block": block, "position": position,
                             "implementation": implementation,
                             "raw": str(path), "observations": measured,
                             "launch_q2": {op: stabilized_quartiles(measured[op])[1]
                                           for op in OPERATIONS}})

    aggregate = {}
    for implementation in IMPLEMENTATIONS:
        aggregate[implementation] = {}
        selected = [row for row in launches if row["implementation"] == implementation]
        for operation in OPERATIONS:
            values = [value for row in selected for value in row["observations"][operation]]
            quartiles = stabilized_quartiles(values)
            aggregate[implementation][operation] = {
                "observations": len(values), "launches": len(selected),
                "stabilized_quartiles": quartiles, "q2_cycles": quartiles[1]}

    comparisons = {}
    for operation_index, operation in enumerate(OPERATIONS):
        block_values = {name: [] for name in IMPLEMENTATIONS}
        for block in range(1, args.blocks + 1):
            selected = [row for row in launches if row["block"] == block]
            for name in IMPLEMENTATIONS:
                block_values[name].append(statistics.fmean(
                    row["launch_q2"][operation] for row in selected
                    if row["implementation"] == name))
        comparisons[operation] = {}
        for label, control in (("gt_db_minus_gt_clean", "gt_clean"),
                               ("gt_db_minus_official", "official")):
            deltas = [candidate - base for candidate, base in
                      zip(block_values["gt_db"], block_values[control])]
            comparisons[operation][label] = {
                "aggregate_delta": aggregate["gt_db"][operation]["q2_cycles"]
                                   - aggregate[control][operation]["q2_cycles"],
                "paired_block_median_delta": statistics.median(deltas),
                "favorable_blocks": sum(delta < 0 for delta in deltas),
                "bootstrap_95_ci": bootstrap_ci(
                    deltas, 20260820 + 10 * operation_index + len(label)),
                "block_deltas": deltas,
            }

    result = {
        "schema": "gt32-load-to-compute-production-043-v1",
        "cpu": args.cpu, "aslr": "enabled", "blocks": args.blocks,
        "discarded_warmup_launches_per_implementation": args.warmup_launches,
        "sequence": "balanced three-way mirrored rotations",
        "binaries": {name: {"path": str(path), "sha256": sha256(path)}
                     for name, path in binaries.items()},
        "aggregate": aggregate, "comparisons": comparisons,
        "launches": launches,
    }
    (args.output / "benchmark.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(comparisons, indent=2))


if __name__ == "__main__":
    main()
