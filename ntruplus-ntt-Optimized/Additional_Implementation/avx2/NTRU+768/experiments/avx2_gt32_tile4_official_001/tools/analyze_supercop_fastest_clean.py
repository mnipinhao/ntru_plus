#!/usr/bin/env python3
"""Analyze Official/CleanGT A-B-B-A SUPERcop blocks."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

from analyze_supercop_matrix import OPS, parse_result, stabilized_quartiles

SEQUENCE = ("official", "clean_gt", "clean_gt", "official")


def variant(path: Path) -> str:
    return "clean_gt" if "fastest-clean" in path.name else "official"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("result_dirs", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    paths = sorted(args.result_dirs, key=lambda item: item.name.rsplit("-", 1)[-1])
    launches = []
    for path in paths:
        parsed = parse_result(path)
        launches.append({
            "result_dir": str(path),
            "variant": variant(path),
            "operations": {
                op: {
                    "observations": len(parsed["measurements"][op]),
                    "q2_cycles": stabilized_quartiles(parsed["measurements"][op])[1],
                } for op in OPS
            },
        })
    if len(launches) % 4:
        raise ValueError("launch count is not divisible by four")

    blocks = []
    for start in range(0, len(launches), 4):
        group = launches[start:start + 4]
        actual = tuple(item["variant"] for item in group)
        if actual != SEQUENCE:
            raise ValueError(f"unexpected block sequence: {actual}")
        operations = {}
        for op in OPS:
            official = statistics.mean((group[0]["operations"][op]["q2_cycles"],
                                        group[3]["operations"][op]["q2_cycles"]))
            clean = statistics.mean((group[1]["operations"][op]["q2_cycles"],
                                     group[2]["operations"][op]["q2_cycles"]))
            operations[op] = {
                "official_q2_cycles": official,
                "clean_gt_q2_cycles": clean,
                "clean_gt_minus_official": clean - official,
            }
        blocks.append({"block": start // 4 + 1, "operations": operations})

    summary = {}
    for op in OPS:
        by_variant = {}
        for name in ("official", "clean_gt"):
            values = [value for launch in launches if launch["variant"] == name
                      for value in parse_result(Path(launch["result_dir"]))["measurements"][op]]
            by_variant[name] = stabilized_quartiles(values)[1]
        deltas = [block["operations"][op]["clean_gt_minus_official"] for block in blocks]
        summary[op] = {
            "official_pooled_q2_cycles": by_variant["official"],
            "clean_gt_pooled_q2_cycles": by_variant["clean_gt"],
            "pooled_delta_cycles": by_variant["clean_gt"] - by_variant["official"],
            "pooled_delta_percent": 100.0 * (by_variant["clean_gt"] - by_variant["official"]) / by_variant["official"],
            "block_deltas": deltas,
            "median_block_delta_cycles": statistics.median(deltas),
            "favorable_blocks": sum(delta < 0 for delta in deltas),
            "blocks": len(blocks),
        }

    output = {
        "schema": "ntruplus768-fastest-clean-abba-v1",
        "sequence": list(SEQUENCE),
        "launches": launches,
        "blocks": blocks,
        "summary": summary,
    }
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
