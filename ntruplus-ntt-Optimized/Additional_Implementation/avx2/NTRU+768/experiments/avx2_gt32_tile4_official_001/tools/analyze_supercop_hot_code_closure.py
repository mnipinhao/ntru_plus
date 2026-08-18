#!/usr/bin/env python3
"""Analyze the palindromic O/G0/Gc SUPERcop hot-closure matrix."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from analyze_supercop_matrix import OPS, parse_result, stabilized_quartiles


LABELS = {
    "avx2": "O",
    "avx2-gt-hotclosure-g0-unpruned": "G0",
    "avx2-gt-hotclosure-gc-pruned": "Gc",
}


def implementation(path: Path) -> str:
    stem = path.name.split("-2026", 1)[0].removeprefix("ntruplus768-")
    if stem not in LABELS:
        raise ValueError(f"unknown implementation in {path}")
    return LABELS[stem]


def q2(values: list[int]) -> float:
    return stabilized_quartiles(values)[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_logs", nargs="+", type=Path)
    parser.add_argument("--supercop", type=Path, default=Path("/home/nuc/supercop-20260627"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    path_blocks: list[list[Path]] = []
    expected = ["O", "G0", "Gc", "Gc", "G0", "O"]
    for run_log in args.run_logs:
        pending: tuple[int, str] | None = None
        grouped: dict[int, list[Path]] = {}
        for line in run_log.read_text().splitlines():
            header = re.match(r"HOTCLOSURE block=(\d+) implementation=(\S+)", line)
            if header:
                pending = (int(header.group(1)), header.group(2))
                continue
            completed = re.match(r"Benchmark complete:\s+(results/\S+)", line)
            if completed and pending is not None:
                block_index, _ = pending
                path = Path(completed.group(1))
                grouped.setdefault(block_index, []).append(path if path.is_absolute() else args.supercop / path)
                pending = None
        for block_index in sorted(grouped):
            candidate = grouped[block_index]
            if len(candidate) == 6 and [implementation(path) for path in candidate] == expected:
                path_blocks.append(candidate)
    if not path_blocks:
        raise ValueError("no complete O/G0/Gc/Gc/G0/O blocks")

    blocks: list[dict[str, object]] = []
    pooled = {label: {op: [] for op in OPS} for label in LABELS.values()}
    for block_paths in path_blocks:
        actual = [implementation(path) for path in block_paths]
        if actual != expected:
            raise ValueError(f"bad block order: {actual}")
        values = {label: {op: [] for op in OPS} for label in LABELS.values()}
        for label, path in zip(actual, block_paths):
            parsed = parse_result(path)
            for op in OPS:
                observations = parsed["measurements"][op]
                values[label][op].extend(observations)
                pooled[label][op].extend(observations)
        operation_report: dict[str, object] = {}
        for op in OPS:
            medians = {label: q2(values[label][op]) for label in ("O", "G0", "Gc")}
            operation_report[op] = {
                "q2_cycles": medians,
                "g0_minus_o": medians["G0"] - medians["O"],
                "gc_minus_o": medians["Gc"] - medians["O"],
                "gc_minus_g0": medians["Gc"] - medians["G0"],
            }
        blocks.append({"index": len(blocks) + 1, "result_dirs": [str(path) for path in block_paths], "operations": operation_report})

    pooled_report: dict[str, object] = {}
    for op in OPS:
        medians = {label: q2(pooled[label][op]) for label in ("O", "G0", "Gc")}
        block_closure = [float(block["operations"][op]["gc_minus_g0"]) for block in blocks]
        pooled_report[op] = {
            "q2_cycles": medians,
            "g0_minus_o": medians["G0"] - medians["O"],
            "gc_minus_o": medians["Gc"] - medians["O"],
            "gc_minus_g0": medians["Gc"] - medians["G0"],
            "closure_block_deltas": block_closure,
            "closure_wins": sum(delta < 0 for delta in block_closure),
        }
    report = {
        "schema": "ntruplus768-supercop-hot-code-closure-v1",
        "method": "O/G0/Gc/Gc/G0/O per block; BENCH_CPU=1; O3+function/data sections+gc-sections",
        "blocks": blocks,
        "pooled": pooled_report,
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
