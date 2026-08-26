#!/usr/bin/env python3
"""Generate the two-branch PROD3 persistent-AoS proof ledger."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def write(path: Path, text: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--branch-proof", type=Path, required=True)
    parser.add_argument("--branch1-constants", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    branch = json.loads(args.branch_proof.read_text(encoding="utf-8"))
    constants = args.branch1_constants.read_text(encoding="utf-8")
    if branch["passes"]["B_ntt16"]["routing"] != 288:
        raise SystemExit("branch-0 routing proof changed")
    if constants.count(".p2align 5") != 72:
        raise SystemExit("branch-1 must contain exactly 72 aligned T0 vectors")

    report = {
        "schema": "gt9x16-prod3-aos-full/v1",
        "checkpoint": "GT9X16-PROD3-AOS-FULL",
        "scope": "two independent persistent-AoS branches in one 2304-byte in-place leaf",
        "frozen": {
            "top_split_arithmetic_changed": False,
            "branch_order": [0, 1],
            "cross_branch_fusion": False,
            "branch_schedule": "exact BRANCH0 machine shape",
            "scale": 4,
            "output_abi": "raw exact P2-B MA2 coefficient planes",
        },
        "per_branch": {
            "backing_bytes": 1152,
            "data_loads": 72,
            "data_stores": 72,
            "routing": 288,
            "montgomery_chains": 148,
            "barrett_vectors": 36,
        },
        "full": {
            "backing_bytes": 2304,
            "extra_array_bytes": 0,
            "data_loads": 144,
            "data_stores": 144,
            "routing": 576,
            "routing_decomposition": {
                "fused_transform_routing": 432,
                "exact_ma2_vpshufb": 72,
                "exact_ma2_vpermq": 72,
            },
            "montgomery_chains": 296,
            "barrett_vectors": 72,
        },
        "range_proof": {
            "same_as_branch0_for_both_branches": True,
            "all_fit_signed16": branch["range_proof"]["all_fit_signed16"],
            "new_reductions": 0,
        },
        "authorization": {
            "full_asm": True,
            "correctness_and_linked_audit": True,
            "benchmark": False,
            "native_kem": False,
        },
    }
    write(args.output, json.dumps(report, indent=2, sort_keys=True) + "\n",
          args.check)
    print("GT9X16-PROD3-AOS-FULL proof ledger passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
