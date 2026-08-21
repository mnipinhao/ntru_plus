#!/usr/bin/env python3
"""Balanced SUPERcop-style fine prefix-frontier campaign."""

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


CHECKPOINTS = ("A1", "A2", "A3", "B1", "B2", "B3", "D", "T0", "T1", "E")
OPS = ("keypair", "enc", "dec")


def expand(line: str) -> list[int]:
    fields = line.split()
    base = int(fields[-2])
    return [base + int(x) for x in re.findall(r"[+-]\d+", fields[-1])]


def stq2(values: list[int]) -> float:
    expanded = sorted(value for value in values for _ in range(8))
    count = len(values)
    return sum(expanded[3 * count:5 * count]) / (2 * count)


def launch(path: Path, cpu: int) -> dict[str, float]:
    def pin() -> None: os.sched_setaffinity(0, {cpu})
    done = subprocess.run([str(path.resolve())], text=True, capture_output=True,
                          preexec_fn=pin)
    if done.returncode: raise RuntimeError(done.stdout + done.stderr)
    values = {op: [] for op in OPS}
    for line in done.stdout.splitlines():
        for op in OPS:
            if f" {op}_cycles " in f" {line} ": values[op].extend(expand(line))
    if any(len(row) < 96 for row in values.values()):
        raise RuntimeError({key: len(row) for key, row in values.items()})
    return {op: stq2(row) for op, row in values.items()}


def bootstrap(values: list[float], seed: int) -> list[float]:
    rng = random.Random(seed)
    samples = sorted(statistics.median(rng.choices(values, k=len(values)))
                     for _ in range(30000))
    return [samples[749], samples[29249]]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", type=Path, required=True)
    parser.add_argument("--cpu", type=int, default=1)
    parser.add_argument("--blocks", type=int, default=256)
    parser.add_argument("--warmup", type=int, default=4)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    names = tuple(f"{impl}-{point}" for point in CHECKPOINTS
                  for impl in ("official", "gt"))
    binaries = {name: args.build / name for name in names}
    for name in names:
        for _ in range(args.warmup): launch(binaries[name], args.cpu)
    rows = []
    for block in range(args.blocks):
        offset = block % len(CHECKPOINTS)
        points = CHECKPOINTS[offset:] + CHECKPOINTS[:offset]
        if (block // len(CHECKPOINTS)) & 1: points = tuple(reversed(points))
        order = []
        for index, point in enumerate(points):
            pair = [f"official-{point}", f"gt-{point}"]
            if (block + index) & 1: pair.reverse()
            order.extend(pair)
        values = {name: launch(binaries[name], args.cpu) for name in order}
        rows.append({"block": block + 1, "order": order, "values": values})
    frontier, control = {}, {}
    for index, point in enumerate(CHECKPOINTS):
        deltas = [row["values"][f"gt-{point}"]["enc"]
                  - row["values"][f"official-{point}"]["enc"] for row in rows]
        frontier[point] = {"paired_median_gt_minus_official": statistics.median(deltas),
                           "favorable_blocks": sum(x < 0 for x in deltas),
                           "bootstrap_95_ci": bootstrap(deltas, 0x0500 + index),
                           "block_deltas": deltas}
        keypair = [row["values"][f"gt-{point}"]["keypair"]
                   - row["values"][f"official-{point}"]["keypair"] for row in rows]
        control[point] = {"paired_median_gt_minus_official": statistics.median(keypair),
                          "bootstrap_95_ci": bootstrap(keypair, 0x1500 + index)}
    result = {"schema": "gt32-encap-fine-prefix-frontier-050-v1",
              "cpu": args.cpu, "aslr": "enabled", "blocks": args.blocks,
              "warmup_launches_per_image": args.warmup,
              "warning": "Adjacent frontier changes are not component costs.",
              "binaries": {name: {"path": str(path.resolve()),
                           "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                           for name, path in binaries.items()},
              "frontier": frontier, "keypair_geometry_control": control,
              "rows": rows}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({point: {"median": row["paired_median_gt_minus_official"],
          "wins": row["favorable_blocks"], "ci": row["bootstrap_95_ci"]}
          for point, row in frontier.items()}, indent=2))


if __name__ == "__main__": main()
