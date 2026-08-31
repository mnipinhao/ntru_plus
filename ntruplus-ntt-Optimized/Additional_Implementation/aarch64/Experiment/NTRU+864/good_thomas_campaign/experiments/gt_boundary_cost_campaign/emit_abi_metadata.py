#!/usr/bin/env python3
"""Emit exact GT864 physical/logical tile maps for M4 survivors."""

from __future__ import annotations

import hashlib
import json

ROTATION = (0, 1, 2, 1, 2, 1, 1, 0, 1, 2, 0, 2, 0, 2, 2, 1)


def leaf(top: int, physical_row: int, column: int, logical_row: int,
         lane: int) -> dict[str, int]:
    return {
        "top": top,
        "physical_row": physical_row,
        "logical_row": logical_row,
        "column": column,
        "lane": lane,
    }


def fixed_row(rotations: tuple[int, ...]) -> list[dict[str, object]]:
    groups = []
    for top in range(2):
        for physical_row in range(9):
            for block in range(2):
                leaves = []
                for lane in range(8):
                    column = block * 8 + lane
                    leaves.append(leaf(
                        top, physical_row, column,
                        (physical_row + rotations[column]) % 9, lane))
                groups.append({"group": len(groups), "leaves": leaves})
    return groups


def fixed_column() -> list[dict[str, object]]:
    groups = []
    for top in range(2):
        for column in range(16):
            groups.append({
                "group": len(groups),
                "leaves": [leaf(top, row, column, row, row)
                           for row in range(8)],
            })
        for block in range(2):
            groups.append({
                "group": len(groups),
                "leaves": [leaf(top, 8, block * 8 + lane, 8, lane)
                           for lane in range(8)],
            })
    return groups


def validate(groups: list[dict[str, object]]) -> str:
    leaves = [entry for group in groups for entry in group["leaves"]]
    assert len(groups) == 36 and len(leaves) == 288
    logical = {(entry["top"], entry["logical_row"], entry["column"])
               for entry in leaves}
    assert len(logical) == 288
    for group in groups:
        for component in range(3):
            for entry in group["leaves"]:
                offset = 24 * group["group"] + 8 * component + entry["lane"]
                assert 0 <= offset < 864
    text = json.dumps(groups, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(text.encode()).hexdigest()


def main() -> None:
    candidates = {
        "FR-0": fixed_row((0,) * 16),
        "FR-lane-0": fixed_row(ROTATION),
        "FC-0": fixed_column(),
    }
    payload = {
        "schema": 1,
        "component_offset": "24*group + 8*component + lane",
        "input_contract": {
            "main": "in[(((top*3+component)*16+column)*8)+s], s=0..7",
            "tail": "in[768+column*8+top*3+component], s=8",
        },
        "inverse_obligation": (
            "consume each candidate's exact physical-to-logical map; "
            "FR-lane-0 logical_row=(physical_row+a_c) mod 9"
        ),
        "candidates": {
            name: {"map_sha256": validate(groups), "groups": groups}
            for name, groups in candidates.items()
        },
        "production_linked": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
