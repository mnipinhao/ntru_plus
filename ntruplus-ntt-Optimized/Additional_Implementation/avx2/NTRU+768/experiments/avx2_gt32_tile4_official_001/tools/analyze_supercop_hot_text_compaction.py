#!/usr/bin/env python3
"""Analyze O/Gc/Gcompact/Gcompact/Gc/O SUPERcop blocks."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from analyze_supercop_matrix import OPS, parse_result, stabilized_quartiles


LABELS = {
    "avx2": "O",
    "avx2-gt-hotclosure-gc-pruned": "Gc",
    "avx2-gt-hotcompact-c0": "Gcompact",
}


def implementation(path: Path) -> str:
    stem = path.name.split("-2026", 1)[0].removeprefix("ntruplus768-")
    return LABELS[stem]


def q2(values: list[int]) -> float:
    return stabilized_quartiles(values)[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_logs", nargs="+", type=Path)
    parser.add_argument("--supercop", type=Path, default=Path("/home/nuc/supercop-20260627"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    expected = ["O", "Gc", "Gcompact", "Gcompact", "Gc", "O"]
    path_blocks = []
    for run_log in args.run_logs:
        pending = None
        grouped: dict[int, list[Path]] = {}
        for line in run_log.read_text().splitlines():
            header = re.match(r"HOTCOMPACT block=(\d+) implementation=(\S+)", line)
            if header:
                pending = int(header.group(1))
                continue
            completed = re.match(r"Benchmark complete:\s+(results/\S+)", line)
            if completed and pending is not None:
                path = Path(completed.group(1))
                grouped.setdefault(pending, []).append(path if path.is_absolute() else args.supercop / path)
                pending = None
        for index in sorted(grouped):
            candidate = grouped[index]
            if len(candidate) == 6 and [implementation(path) for path in candidate] == expected:
                path_blocks.append(candidate)
    if not path_blocks:
        raise ValueError("no complete O/Gc/Gcompact/Gcompact/Gc/O blocks")

    pooled = {label: {op: [] for op in OPS} for label in LABELS.values()}
    blocks = []
    for paths in path_blocks:
        values = {label: {op: [] for op in OPS} for label in LABELS.values()}
        for label, path in zip(expected, paths):
            parsed = parse_result(path)
            for op in OPS:
                observations = parsed["measurements"][op]
                values[label][op].extend(observations)
                pooled[label][op].extend(observations)
        operations = {}
        for op in OPS:
            medians = {label: q2(values[label][op]) for label in LABELS.values()}
            operations[op] = {
                "q2_cycles": medians,
                "gcompact_minus_gc": medians["Gcompact"] - medians["Gc"],
                "gcompact_minus_o": medians["Gcompact"] - medians["O"],
            }
        blocks.append({"index": len(blocks) + 1, "result_dirs": [str(p) for p in paths], "operations": operations})

    pooled_report = {}
    for op in OPS:
        medians = {label: q2(pooled[label][op]) for label in LABELS.values()}
        deltas = [float(block["operations"][op]["gcompact_minus_gc"]) for block in blocks]
        pooled_report[op] = {
            "q2_cycles": medians,
            "gcompact_minus_gc": medians["Gcompact"] - medians["Gc"],
            "gcompact_minus_o": medians["Gcompact"] - medians["O"],
            "compaction_block_deltas": deltas,
            "compaction_wins": sum(delta < 0 for delta in deltas),
        }

    report = {
        "schema": "ntruplus768-supercop-reachable-hot-text-compaction-v1",
        "method": "O/Gc/Gcompact/Gcompact/Gc/O; four palindrome blocks; BENCH_CPU=1; O3GC",
        "blocks": blocks,
        "pooled": pooled_report,
    }
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
