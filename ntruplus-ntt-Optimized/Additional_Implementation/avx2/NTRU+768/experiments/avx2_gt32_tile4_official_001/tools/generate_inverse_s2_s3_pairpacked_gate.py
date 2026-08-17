#!/usr/bin/env python3
"""Exact S2-pair-packed -> S3 consumer gate for the production inverse.

This distinguishes a genuinely deleted permutation from merely moving the
same low/high-arm formation across the S2/S3 source-code boundary.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated" / "tile4_inverse_s2_s3_pairpacked_gate.json"


def source_half(label: str) -> int:
    return int(label.rsplit("h", 1)[1])


def crossings(output: tuple[str, str]) -> int:
    return sum(source_half(value) != destination for destination, value in enumerate(output))


def main() -> None:
    # S2 has completed while retaining its two pair-packed mathematical
    # results.  S and D are ordinary YMM registers with low/high halves.
    pairpacked = {
        "S": ("S.h0", "S.h1"),
        "D": ("D.h0", "D.h1"),
    }

    # These are not an arbitrary canonicalization.  They are exactly the two
    # logical arms consumed by the immediately following S3 butterfly.
    s3_low_arm = ("S.h0", "D.h0")
    s3_high_arm = ("S.h1", "D.h1")
    low_crossings = crossings(s3_low_arm)
    high_crossings = crossings(s3_high_arm)
    assert low_crossings == 1
    assert high_crossings == 1

    # A one-destination AVX2 cross-half instruction is required for each arm.
    # Lane-local table relabeling changes constants, not which values form the
    # two operands of an add/sub butterfly.
    lower_bound = 2
    current = 2
    assert lower_bound == current

    pairs_per_tile = 4
    tiles = 6
    current_per_tile = current * pairs_per_tile
    candidate_per_tile = lower_bound * pairs_per_tile

    result = {
        "experiment": "INV-S2-S3-PAIRPACKED-001",
        "status": "static-hard-stop",
        "production_symbol": "gt32_global_inverse_core_asm",
        "source": "src/tile4_global_physical_asm.S",
        "scope": {
            "input": "existing S2 arithmetic output S/D in pair-packed registers",
            "variable": [
                "S2 output ABI",
                "S3 register assignment",
                "S3 twiddle-vector physical ordering",
            ],
            "frozen": [
                "S2 arithmetic and input formation",
                "S3 mathematical butterfly",
                "post-S3 physical/semantic state",
                "range and Montgomery exponent",
            ],
        },
        "symbolic_state": {
            "pairpacked_S": pairpacked["S"],
            "pairpacked_D": pairpacked["D"],
            "S3_low_arm": s3_low_arm,
            "S3_high_arm": s3_high_arm,
        },
        "proof": {
            "current_two_output_reconstruction_is_S3_operand_formation": True,
            "low_arm_cross_half_values": low_crossings,
            "high_arm_cross_half_values": high_crossings,
            "minimum_cross_half_outputs": lower_bound,
            "current_vperm2i128": current,
            "twiddle_relabel_can_change_pairing_topology": False,
            "reason": (
                "S3 requires L=[S.low,D.low] and H=[S.high,D.high].  Each is "
                "a distinct YMM output with one half moved.  The current 0x20 "
                "and 0x31 VPERM2I128 instructions already form precisely L and H."
            ),
        },
        "accounting": {
            "pairs_per_tile": pairs_per_tile,
            "tiles": tiles,
            "current_crosshalf_between_S2_and_S3_per_tile": current_per_tile,
            "pairpacked_candidate_crosshalf_needed_by_S3_per_tile": candidate_per_tile,
            "current_crosshalf_per_inverse": current_per_tile * tiles,
            "candidate_crosshalf_per_inverse": candidate_per_tile * tiles,
            "net_deleted_vperm2i128": 0,
        },
        "candidate_interpretation": {
            "claimed_S2_output_reconstruction_deleted_per_inverse": 48,
            "S3_operand_formation_reintroduced_per_inverse": 48,
            "net": 0,
            "note": (
                "Performing S3 directly on S and D would make logical q2 a "
                "half-local butterfly.  It still needs the same two cross-half "
                "outputs; reordered twiddles cannot exchange data values."
            ),
        },
        "decision": {
            "assembly_emitted": False,
            "benchmark_run": False,
            "production_changed": False,
            "reason": "the proposed deletion only moves the same two arm-forming permutes into S3",
        },
        "next_bounded_question": (
            "search jointly from the post-S1/dword-transition state through "
            "S2 and S3, because only a producer layout that already supplies "
            "both S3 arms can lower this boundary"
        ),
        "reopen_only_if": [
            "post-S1 producer supplies both S3 arms without the same cross-half movement",
            "post-S3 consumer accepts a different physical state and total joint cost drops",
            "a dual-output cross-half ISA primitive becomes available",
        ],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT.relative_to(ROOT))
    print("decision: static-hard-stop; 48 removed at S2 are 48 reintroduced at S3")


if __name__ == "__main__":
    main()
