#!/usr/bin/env python3
"""Audit rowpack Forward stage345 live-out shape before another v3 candidate.

This is a layout/DAG audit, not a benchmark.  It records the current rowpack v2
stage345 reduced-register order and the rowpack-ready plane vectors required by
plain vector stores.  Gate 6 already rejected st4/structured lane stores, so
this audit keeps store-form selection explicit.
"""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence


BLOCKS = [
    {
        "block": 0,
        "k32_base": 0,
        "semantic_order": ["v17", "v30", "v13", "v5", "v21", "v9", "v14", "v7"],
        "v2_source_order": ["v21", "v9", "v13", "v5", "v17", "v30", "v14", "v7"],
    },
    {
        "block": 1,
        "k32_base": 8,
        "semantic_order": ["v2", "v10", "v19", "v30", "v3", "v12", "v28", "v8"],
        "v2_source_order": ["v28", "v8", "v2", "v10", "v19", "v30", "v3", "v12"],
    },
    {
        "block": 2,
        "k32_base": 16,
        "semantic_order": ["v21", "v8", "v2", "v25", "v6", "v28", "v12", "v7"],
        "v2_source_order": ["v12", "v7", "v2", "v25", "v6", "v28", "v21", "v8"],
    },
    {
        "block": 3,
        "k32_base": 24,
        "semantic_order": ["v7", "v29", "v12", "v27", "v24", "v14", "v18", "v9"],
        "v2_source_order": ["v12", "v27", "v7", "v29", "v18", "v9", "v24", "v14"],
    },
]

PLANE_NAMES = [
    "branch0_lane0",
    "branch0_lane1",
    "branch0_lane2",
    "branch0_lane3",
    "branch1_lane0",
    "branch1_lane1",
    "branch1_lane2",
    "branch1_lane3",
]


def target_plane(block: dict[str, object], plane: int) -> list[str]:
    regs = block["semantic_order"]
    assert isinstance(regs, list)
    return [f"{reg}.h[{plane}]" for reg in regs]


def required_permutation(block: dict[str, object]) -> list[int]:
    semantic = block["semantic_order"]
    source = block["v2_source_order"]
    assert isinstance(semantic, list)
    assert isinstance(source, list)
    return [source.index(reg) for reg in semantic]


def build_report() -> dict[str, object]:
    blocks: list[dict[str, object]] = []
    for block in BLOCKS:
        block_report = {
            "block": block["block"],
            "k32_base": block["k32_base"],
            "current_stage345_liveout": {
                f"k32+{i}": reg
                for i, reg in enumerate(block["semantic_order"])
            },
            "v2_tail_source_order": block["v2_source_order"],
            "source_to_target_lane_permutation": required_permutation(block),
            "target_planes": {
                PLANE_NAMES[plane]: target_plane(block, plane)
                for plane in range(len(PLANE_NAMES))
            },
        }
        blocks.append(block_report)

    return {
        "gate": "Gate 7: rowpack Forward stage345 live-out audit",
        "status": "audit_only_no_candidate",
        "candidate_status": {
            "gate6_structured_store": "rejected",
            "forward_v3_register_order_direction": "still_open",
        },
        "store_policy": {
            "allowed_for_next_candidates": ["str qN, [public_offset]", "st1 {vN.8h}, [public_offset]"],
            "forbidden_for_next_candidates": ["st4 structured stores", "lane stores", "scalar strh scatter", "scalar GT-to-rowpack conversion"],
        },
        "cost_model": {
            "v2_final_permute_per_block": {"trn": 24, "vector_stores": 8},
            "v2_final_permute_full_ntt32_row": {"trn": 96, "vector_stores": 32},
            "gate6_structured_store_per_block": {"mov": 8, "address_add": 8, "st4_lane_store": 16},
            "gate6_result": "correctness pass, performance reject",
        },
        "blocks": blocks,
        "decision": {
            "gate7_result": "final store primitive is not the solution",
            "v3a": "final-permute-only may try to reduce the 24-trn-per-block network but must keep vector stores only",
            "v3b": "preferred: change stage345 arithmetic/register layout so target_planes are naturally live-out",
            "slothy_role": "schedule/register-allocate a chosen good DAG; do not choose layout/store primitive",
        },
    }


def emit_markdown(report: dict[str, object]) -> None:
    print(f"# {report['gate']}")
    print()
    print(f"status: `{report['status']}`")
    print()
    print("## Candidate Status")
    for key, value in report["candidate_status"].items():
        print(f"- `{key}`: `{value}`")
    print()
    print("## Store Policy")
    print("Allowed next candidate stores:")
    for item in report["store_policy"]["allowed_for_next_candidates"]:
        print(f"- `{item}`")
    print()
    print("Forbidden next candidate stores:")
    for item in report["store_policy"]["forbidden_for_next_candidates"]:
        print(f"- `{item}`")
    print()
    print("## Cost Model")
    cost = report["cost_model"]
    print(f"- v2 final permute per block: `{cost['v2_final_permute_per_block']}`")
    print(f"- v2 final permute per row: `{cost['v2_final_permute_full_ntt32_row']}`")
    print(f"- Gate 6 structured-store per block: `{cost['gate6_structured_store_per_block']}`")
    print(f"- Gate 6 result: `{cost['gate6_result']}`")
    print()
    print("## Stage345 Live-Out Blocks")
    for block in report["blocks"]:
        print(f"### Block {block['block']} k32={block['k32_base']}..{block['k32_base'] + 7}")
        print()
        print("Current arithmetic live-out semantics:")
        for k32, reg in block["current_stage345_liveout"].items():
            print(f"- `{k32}`: `{reg}`")
        print()
        print(f"v2 tail source order: `{block['v2_tail_source_order']}`")
        print(f"source->target lane permutation: `{block['source_to_target_lane_permutation']}`")
        print()
        print("Target rowpack plane vectors for plain vector stores:")
        for plane, lanes in block["target_planes"].items():
            print(f"- `{plane}`: `{lanes}`")
        print()
    print("## Decision")
    for key, value in report["decision"].items():
        print(f"- `{key}`: {value}")


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    report = build_report()
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        emit_markdown(report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
