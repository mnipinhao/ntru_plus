#!/usr/bin/env python3
"""Analyze fixed-ELF balanced ABBA/BAAB SUPERcop measure launches."""

from __future__ import annotations

import argparse
import json
import random
import re
import statistics
from pathlib import Path


OPS = ("keypair", "enc", "dec")


def stabilized_q2(values: list[int]) -> float:
    expanded = sorted(value for value in values for _ in range(8))
    n = len(values)
    return sum(expanded[3 * n:5 * n]) / (2 * n)


def parse_launch(path: Path) -> dict[str, float]:
    values = {op: [] for op in OPS}
    backend = None
    for line in path.read_text().splitlines():
        fields = line.split()
        if fields[:1] == ["cpucycles_implementation"]:
            backend = fields[1]
        for op in OPS:
            if fields[:2] == [f"{op}_cycles", "-"]:
                base = int(fields[2])
                values[op].extend(
                    base + int(delta)
                    for delta in re.findall(r"[+-]\d+", fields[3])
                )
    if backend != "default-perfevent":
        raise ValueError(f"unexpected cycle backend in {path}: {backend}")
    if any(len(values[op]) != 96 for op in OPS):
        raise ValueError(f"incomplete observations in {path}: "
                         f"{ {op: len(values[op]) for op in OPS} }")
    return {op: stabilized_q2(values[op]) for op in OPS}


def bootstrap_median_ci(values: list[float], seed: int = 20260813,
                        samples: int = 100000) -> list[float]:
    rng = random.Random(seed)
    n = len(values)
    estimates = sorted(statistics.median(rng.choices(values, k=n))
                       for _ in range(samples))
    return [estimates[int(samples * 0.025)], estimates[int(samples * 0.975)]]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input_dir", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    pattern = re.compile(r"run-(\d+)-block-(\d+)-pos-(\d+)-(official|gt)\.out$")
    launches = []
    for path in sorted(args.input_dir.glob("run-*.out")):
        match = pattern.search(path.name)
        if not match:
            continue
        launches.append({
            "path": str(path),
            "run": int(match.group(1)),
            "block": int(match.group(2)),
            "position": int(match.group(3)),
            "variant": match.group(4),
            "q2_cycles": parse_launch(path),
        })
    blocks_count = len(launches) // 4
    if not launches or len(launches) != blocks_count * 4:
        raise ValueError("incomplete block set")

    blocks = []
    for block_id in range(1, blocks_count + 1):
        group = [item for item in launches if item["block"] == block_id]
        group.sort(key=lambda item: item["position"])
        expected = (["official", "gt", "gt", "official"] if block_id % 2
                    else ["gt", "official", "official", "gt"])
        if [item["variant"] for item in group] != expected:
            raise ValueError(f"bad sequence in block {block_id}")
        operations = {}
        for op in OPS:
            official = statistics.mean(item["q2_cycles"][op] for item in group
                                       if item["variant"] == "official")
            gt = statistics.mean(item["q2_cycles"][op] for item in group
                                 if item["variant"] == "gt")
            operations[op] = {
                "official_q2_cycles": official,
                "gt_q2_cycles": gt,
                "gt_minus_official_cycles": gt - official,
                "gt_minus_official_percent": 100.0 * (gt - official) / official,
            }
        blocks.append({"block": block_id, "sequence": expected,
                       "operations": operations})

    summary = {}
    for op in OPS:
        deltas = [block["operations"][op]["gt_minus_official_cycles"]
                  for block in blocks]
        official = [block["operations"][op]["official_q2_cycles"]
                    for block in blocks]
        gt = [block["operations"][op]["gt_q2_cycles"] for block in blocks]
        median_delta = statistics.median(deltas)
        summary[op] = {
            "blocks": blocks_count,
            "observations_per_launch": 96,
            "official_block_median_q2_cycles": statistics.median(official),
            "gt_block_median_q2_cycles": statistics.median(gt),
            "paired_median_delta_cycles": median_delta,
            "paired_median_delta_percent": (
                100.0 * median_delta / statistics.median(official)),
            "paired_delta_mad_cycles": statistics.median(
                abs(value - median_delta) for value in deltas),
            "bootstrap_median_95ci_cycles": bootstrap_median_ci(deltas),
            "gt_favorable_blocks": sum(value < 0 for value in deltas),
            "block_deltas_cycles": deltas,
            "odd_abba_median_delta_cycles": statistics.median(deltas[0::2]),
            "even_baab_median_delta_cycles": statistics.median(deltas[1::2]),
        }

    result = {
        "schema": "ntruplus768-fixed-elf-supercop-serious-v1",
        "cycle_backend": "default-perfevent/PERF_COUNT_HW_CPU_CYCLES",
        "statistics_unit": "launch-level stabilized Q2; paired block delta",
        "launches": launches,
        "blocks": blocks,
        "summary": summary,
    }
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
