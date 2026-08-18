#!/usr/bin/env python3
"""Analyze H0/H1/H2 palindromic SUPERcop blocks."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from analyze_supercop_matrix import OPS, parse_result, stabilized_quartiles


def q2(values: list[int]) -> float:
    return stabilized_quartiles(values)[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_log", type=Path)
    parser.add_argument("--supercop", type=Path, default=Path("/home/nuc/supercop-20260627"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    grouped: dict[int, list[tuple[str, Path]]] = {}
    pending: tuple[int, str] | None = None
    for line in args.run_log.read_text().splitlines():
        header = re.match(r"HOTGROUP block=(\d+) label=(H[012]) ", line)
        if header:
            pending = (int(header.group(1)), header.group(2))
            continue
        complete = re.match(r"Benchmark complete:\s+(results/\S+)", line)
        if complete and pending:
            path = Path(complete.group(1))
            grouped.setdefault(pending[0], []).append((pending[1], args.supercop / path))
            pending = None
    expected = ["H0", "H1", "H2", "H2", "H1", "H0"]
    blocks = []
    pooled = {label: {op: [] for op in OPS} for label in ("H0", "H1", "H2")}
    for index in sorted(grouped):
        entries = grouped[index]
        if [label for label, _ in entries] != expected:
            continue
        values = {label: {op: [] for op in OPS} for label in pooled}
        for label, path in entries:
            parsed = parse_result(path)
            for op in OPS:
                values[label][op].extend(parsed["measurements"][op])
                pooled[label][op].extend(parsed["measurements"][op])
        operations = {}
        for op in OPS:
            medians = {label: q2(values[label][op]) for label in pooled}
            operations[op] = {
                "q2_cycles": medians,
                "H1_minus_H0": medians["H1"] - medians["H0"],
                "H2_minus_H0": medians["H2"] - medians["H0"],
                "H2_minus_H1": medians["H2"] - medians["H1"],
            }
        blocks.append({"index": len(blocks) + 1, "operations": operations, "result_dirs": [str(path) for _, path in entries]})
    if not blocks:
        raise ValueError("no complete H0/H1/H2 blocks")
    summary = {}
    for op in OPS:
        medians = {label: q2(pooled[label][op]) for label in pooled}
        h1 = [block["operations"][op]["H1_minus_H0"] for block in blocks]
        h2 = [block["operations"][op]["H2_minus_H0"] for block in blocks]
        summary[op] = {
            "q2_cycles": medians,
            "H1_minus_H0": medians["H1"] - medians["H0"],
            "H2_minus_H0": medians["H2"] - medians["H0"],
            "H2_minus_H1": medians["H2"] - medians["H1"],
            "H1_block_deltas": h1, "H1_wins": sum(x < 0 for x in h1),
            "H2_block_deltas": h2, "H2_wins": sum(x < 0 for x in h2),
        }
    report = {
        "schema": "ntruplus768-supercop-hot-function-grouping-v1",
        "method": "H0/H1/H2/H2/H1/H0; BENCH_CPU=1; bodies frozen",
        "blocks": blocks,
        "pooled": summary,
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
