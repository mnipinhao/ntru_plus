#!/usr/bin/env python3
"""Analyze fixed-layout A-B-B-A SUPERcop blocks."""

from __future__ import annotations

import argparse
import json
import statistics
from pathlib import Path

from analyze_supercop_matrix import OPS, parse_result, stabilized_quartiles


SEQUENCE = ("control", "candidate", "candidate", "control")


def variant(path: Path) -> str:
    if "fixed-control" in path.name:
        return "control"
    if "fixed-candidate" in path.name:
        return "candidate"
    raise ValueError(f"unrecognized result: {path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("result_dirs", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    launches = []
    for path in sorted(args.result_dirs, key=lambda item: item.name.rsplit("-", 1)[-1]):
        parsed = parse_result(path)
        launches.append(
            {
                "result_dir": str(path),
                "variant": variant(path),
                "operations": {
                    op: {
                        "observations": len(parsed["measurements"][op]),
                        "q2_cycles": stabilized_quartiles(parsed["measurements"][op])[1],
                    }
                    for op in OPS
                },
            }
        )
    if len(launches) % 4:
        raise ValueError("launch count is not divisible by four")

    blocks = []
    for start in range(0, len(launches), 4):
        group = launches[start : start + 4]
        actual = tuple(item["variant"] for item in group)
        if actual != SEQUENCE:
            raise ValueError(f"unexpected block sequence: {actual}")
        operations = {}
        for op in OPS:
            control = statistics.mean(
                (group[0]["operations"][op]["q2_cycles"],
                 group[3]["operations"][op]["q2_cycles"])
            )
            candidate = statistics.mean(
                (group[1]["operations"][op]["q2_cycles"],
                 group[2]["operations"][op]["q2_cycles"])
            )
            operations[op] = {
                "control_q2_cycles": control,
                "candidate_q2_cycles": candidate,
                "candidate_minus_control": candidate - control,
            }
        blocks.append({"block": start // 4 + 1, "operations": operations})

    summary = {}
    for op in OPS:
        control_values = [
            item["operations"][op]["q2_cycles"]
            for item in launches if item["variant"] == "control"
        ]
        candidate_values = [
            item["operations"][op]["q2_cycles"]
            for item in launches if item["variant"] == "candidate"
        ]
        block_deltas = [block["operations"][op]["candidate_minus_control"]
                        for block in blocks]
        summary[op] = {
            "control_pooled_q2_cycles": stabilized_quartiles(
                [value for item in launches if item["variant"] == "control"
                 for value in parse_result(Path(item["result_dir"]))["measurements"][op]
                ])[1],
            "candidate_pooled_q2_cycles": stabilized_quartiles(
                [value for item in launches if item["variant"] == "candidate"
                 for value in parse_result(Path(item["result_dir"]))["measurements"][op]
                ])[1],
            "control_launch_q2_cycles": control_values,
            "candidate_launch_q2_cycles": candidate_values,
            "block_deltas": block_deltas,
            "median_block_delta_cycles": statistics.median(block_deltas),
            "favorable_blocks": sum(delta < 0 for delta in block_deltas),
            "blocks": len(blocks),
        }
        summary[op]["pooled_delta_cycles"] = (
            summary[op]["candidate_pooled_q2_cycles"] -
            summary[op]["control_pooled_q2_cycles"]
        )

    output = {
        "schema": "ntruplus768-p-j1-fixed-layout-ab-v1",
        "sequence": list(SEQUENCE),
        "launches": launches,
        "blocks": blocks,
        "summary": summary,
    }
    args.output.write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
