#!/usr/bin/env python3
"""Analyze O-C-P-P-C-O SUPERcop blocks for a three-way comparison."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

from analyze_supercop_matrix import OPS, parse_result, stabilized_quartiles


SEQUENCE = ("official", "current", "candidate", "candidate", "current", "official")


def classify(path: Path, current_name: str, candidate_name: str) -> str:
    name = path.name.split("-2026", 1)[0].removeprefix("ntruplus768-")
    if name == "avx2":
        return "official"
    if name == current_name:
        return "current"
    if name == candidate_name:
        return "candidate"
    raise ValueError(f"unexpected implementation in {path}")


def mean_pair(left: float, right: float) -> float:
    return (left + right) / 2.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("result_dirs", nargs="+", type=Path)
    parser.add_argument("--current", required=True)
    parser.add_argument("--candidate", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    ordered = sorted(args.result_dirs, key=lambda path: path.name.rsplit("-", 1)[-1])
    if len(ordered) % len(SEQUENCE):
        raise ValueError("result count is not a multiple of six")

    launches = []
    for path in ordered:
        parsed = parse_result(path)
        variant = classify(path, args.current, args.candidate)
        launches.append(
            {
                "result_dir": str(path),
                "variant": variant,
                "operations": {
                    op: {
                        "observations": len(parsed["measurements"][op]),
                        "q2_cycles": stabilized_quartiles(parsed["measurements"][op])[1],
                    }
                    for op in OPS
                },
            }
        )

    blocks = []
    for offset in range(0, len(launches), len(SEQUENCE)):
        block_launches = launches[offset : offset + len(SEQUENCE)]
        actual = tuple(item["variant"] for item in block_launches)
        if actual != SEQUENCE:
            raise ValueError(f"block {offset // len(SEQUENCE) + 1}: {actual} != {SEQUENCE}")
        operations = {}
        for op in OPS:
            q2 = [item["operations"][op]["q2_cycles"] for item in block_launches]
            official = mean_pair(q2[0], q2[5])
            current = mean_pair(q2[1], q2[4])
            candidate = mean_pair(q2[2], q2[3])
            operations[op] = {
                "official_q2_cycles": official,
                "current_q2_cycles": current,
                "candidate_q2_cycles": candidate,
                "candidate_minus_official": candidate - official,
                "candidate_minus_current": candidate - current,
                "current_minus_official": current - official,
            }
        blocks.append(
            {
                "block": offset // len(SEQUENCE) + 1,
                "result_dirs": [item["result_dir"] for item in block_launches],
                "operations": operations,
            }
        )

    summary = {}
    for op in OPS:
        comparisons = {}
        for field in (
            "candidate_minus_official",
            "candidate_minus_current",
            "current_minus_official",
        ):
            values = [block["operations"][op][field] for block in blocks]
            comparisons[field] = {
                "block_deltas": values,
                "median_delta_cycles": statistics.median(values),
                "minimum_delta_cycles": min(values),
                "maximum_delta_cycles": max(values),
                "favorable_blocks": sum(value < 0 for value in values),
                "blocks": len(values),
            }
        summary[op] = comparisons

    output = {
        "schema": "ntruplus768-supercop-ocppco-blocks-v1",
        "sequence": list(SEQUENCE),
        "current": args.current,
        "candidate": args.candidate,
        "launches": launches,
        "blocks": blocks,
        "summary": summary,
    }
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
