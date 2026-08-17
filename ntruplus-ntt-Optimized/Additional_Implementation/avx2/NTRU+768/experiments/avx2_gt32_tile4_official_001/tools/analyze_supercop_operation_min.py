#!/usr/bin/env python3
"""Analyze monolithic/minimal-image A-B-B-A SUPERcop blocks."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

from analyze_supercop_matrix import OPS, parse_result, stabilized_quartiles


SEQUENCE = ("monolithic", "minimal", "minimal", "monolithic")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--minimal-token", required=True)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("result_dirs", nargs="+", type=Path)
    args = parser.parse_args()

    paths = sorted(args.result_dirs, key=lambda path: path.name.rsplit("-", 1)[-1])
    launches = []
    for path in paths:
        parsed = parse_result(path)
        name = "minimal" if args.minimal_token in path.name else "monolithic"
        launches.append({
            "result_dir": str(path),
            "variant": name,
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
            monolithic = statistics.mean((group[0]["operations"][op]["q2_cycles"],
                                          group[3]["operations"][op]["q2_cycles"]))
            minimal = statistics.mean((group[1]["operations"][op]["q2_cycles"],
                                       group[2]["operations"][op]["q2_cycles"]))
            operations[op] = {
                "monolithic_q2_cycles": monolithic,
                "minimal_q2_cycles": minimal,
                "minimal_minus_monolithic": minimal - monolithic,
            }
        blocks.append({"block": start // 4 + 1, "operations": operations})

    summary = {}
    for op in OPS:
        pooled = {}
        launch_q2 = {}
        for variant in ("monolithic", "minimal"):
            selected = [item for item in launches if item["variant"] == variant]
            values = [value for item in selected
                      for value in parse_result(Path(item["result_dir"]))["measurements"][op]]
            pooled[variant] = stabilized_quartiles(values)[1]
            launch_q2[variant] = [item["operations"][op]["q2_cycles"] for item in selected]
        deltas = [block["operations"][op]["minimal_minus_monolithic"]
                  for block in blocks]
        summary[op] = {
            "monolithic_pooled_q2_cycles": pooled["monolithic"],
            "minimal_pooled_q2_cycles": pooled["minimal"],
            "pooled_delta_cycles": pooled["minimal"] - pooled["monolithic"],
            "monolithic_launch_q2_cycles": launch_q2["monolithic"],
            "minimal_launch_q2_cycles": launch_q2["minimal"],
            "block_deltas": deltas,
            "median_block_delta_cycles": statistics.median(deltas),
            "favorable_blocks": sum(delta < 0 for delta in deltas),
            "blocks": len(blocks),
        }

    output = {
        "schema": "ntruplus768-operation-minimal-abba-v1",
        "sequence": list(SEQUENCE),
        "minimal_token": args.minimal_token,
        "launches": launches,
        "blocks": blocks,
        "summary": summary,
    }
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
