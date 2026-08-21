#!/usr/bin/env python3
"""Balanced SUPERcop-style exact-image Encap prefix-frontier benchmark."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import statistics
import subprocess
from pathlib import Path


CHECKPOINTS = ("A", "B", "C", "D", "E")
OPERATIONS = ("keypair", "enc", "dec")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def expand(line: str) -> list[int]:
    fields = line.split()
    base = int(fields[-2])
    return [base + int(x) for x in re.findall(r"[+-]\d+", fields[-1])]


def stq2(values: list[int]) -> float:
    expanded = sorted(value for value in values for _ in range(8))
    count = len(values)
    return sum(expanded[3 * count:5 * count]) / (2 * count)


def launch(path: Path, cpu: int) -> dict[str, float]:
    def pin() -> None:
        os.sched_setaffinity(0, {cpu})
    completed = subprocess.run([str(path.resolve())], text=True,
                               capture_output=True, preexec_fn=pin)
    if completed.returncode:
        raise RuntimeError(completed.stdout + completed.stderr)
    values = {operation: [] for operation in OPERATIONS}
    for line in completed.stdout.splitlines():
        for operation in OPERATIONS:
            if f" {operation}_cycles " in f" {line} ":
                values[operation].extend(expand(line))
    if any(len(row) < 96 for row in values.values()):
        raise RuntimeError({key: len(row) for key, row in values.items()})
    return {operation: stq2(row) for operation, row in values.items()}


def bootstrap(values: list[float], seed: int) -> list[float]:
    rng = random.Random(seed)
    samples = sorted(statistics.median(rng.choices(values, k=len(values)))
                     for _ in range(30000))
    return [samples[749], samples[29249]]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--cpu", type=int, default=1)
    parser.add_argument("--blocks", type=int, default=64)
    parser.add_argument("--warmup", type=int, default=2)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    names = tuple(f"{implementation}-{checkpoint}"
                  for checkpoint in CHECKPOINTS
                  for implementation in ("official", "gt"))
    binaries = {name: args.build / name for name in names}
    for name in names:
        for _ in range(args.warmup):
            launch(binaries[name], args.cpu)

    rows = []
    for block in range(args.blocks):
        # Rotate checkpoints, and mirror Official/GT order on alternating
        # blocks. Every checkpoint is represented once per block.
        offset = block % len(CHECKPOINTS)
        checkpoints = CHECKPOINTS[offset:] + CHECKPOINTS[:offset]
        if (block // len(CHECKPOINTS)) & 1:
            checkpoints = tuple(reversed(checkpoints))
        order = []
        for index, checkpoint in enumerate(checkpoints):
            pair = [f"official-{checkpoint}", f"gt-{checkpoint}"]
            if (block + index) & 1:
                pair.reverse()
            order.extend(pair)
        measured = {name: launch(binaries[name], args.cpu) for name in order}
        rows.append({"block": block + 1, "order": order, "values": measured})

    frontier = {}
    controls = {}
    for checkpoint_index, checkpoint in enumerate(CHECKPOINTS):
        deltas = [row["values"][f"gt-{checkpoint}"]["enc"]
                  - row["values"][f"official-{checkpoint}"]["enc"]
                  for row in rows]
        frontier[checkpoint] = {
            "paired_median_gt_minus_official": statistics.median(deltas),
            "favorable_blocks": sum(delta < 0 for delta in deltas),
            "bootstrap_95_ci": bootstrap(deltas, 0x0490 + checkpoint_index),
            "block_deltas": deltas,
        }
        # Keypair executes before Encap and must be invariant across all five
        # Encap patches. Decap executes after the deliberately partial A-D
        # ciphertext and is therefore not a neutral control.
        neutral = [row["values"][f"gt-{checkpoint}"]["keypair"]
                   - row["values"][f"official-{checkpoint}"]["keypair"]
                   for row in rows]
        controls[checkpoint] = {
            "paired_median_gt_minus_official": statistics.median(neutral),
            "bootstrap_95_ci": bootstrap(neutral, 0x1490 + checkpoint_index)}

    result = {
        "schema": "gt32-exact-production-prefix-frontier-049-v1",
        "method": "SUPERcop measurement executable, balanced paired fresh launches",
        "cpu": args.cpu, "aslr": "enabled", "blocks": args.blocks,
        "warmup_launches_per_image": args.warmup,
        "warning": "Adjacent checkpoint differences are not component costs.",
        "binaries": {name: {"path": str(path.resolve()), "sha256": sha256(path)}
                     for name, path in binaries.items()},
        "frontier": frontier, "keypair_geometry_control": controls,
        "rows": rows,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({checkpoint: {
        "median": row["paired_median_gt_minus_official"],
        "wins": row["favorable_blocks"], "ci": row["bootstrap_95_ci"]}
        for checkpoint, row in frontier.items()}, indent=2))


if __name__ == "__main__":
    main()
