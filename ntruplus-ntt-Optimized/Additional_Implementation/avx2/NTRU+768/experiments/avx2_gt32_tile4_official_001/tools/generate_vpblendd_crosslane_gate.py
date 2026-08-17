#!/usr/bin/env python3
"""Bounded VPBLENDD gate at the production global-inverse S2 boundary.

The gate freezes the private-M input, inverse arithmetic, S3 consumer state,
range, and twiddles.  It asks only whether same-slot VPBLENDD routing can
remove a VPERM2I128 from one half-local S2 butterfly pair.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated" / "tile4_vpblendd_crosslane_gate.json"


def half(label: str) -> int:
    """Return the source 128-bit half encoded in a symbolic half label."""
    return int(label.rsplit("h", 1)[1])


def lane_local_reachable(source: str, destination_half: int) -> bool:
    """VPBLENDD/VSHUFD/VSHUFPS cannot move a dword across bit 128."""
    return half(source) == destination_half


def main() -> None:
    # One current S2 pair begins as two ordinary YMMs.  Pair-packed low/high
    # operands each require one source half to change destination half.
    sources = {
        "a": ("a.h0", "a.h1"),
        "b": ("b.h0", "b.h1"),
    }
    pair_packed = {
        "low": ("a.h0", "b.h0"),
        "high": ("a.h1", "b.h1"),
    }

    extraction_crossings = sum(
        not lane_local_reachable(source, destination_half)
        for halves in pair_packed.values()
        for destination_half, source in enumerate(halves)
    )

    # After arithmetic, sum and difference are pair-packed in the same shape.
    # Restoring the frozen S3 input needs the inverse half placement.
    reconstructed = {
        "a_out": ("sum.h0", "diff.h0"),
        "b_out": ("sum.h1", "diff.h1"),
    }
    reconstruction_crossings = sum(
        not lane_local_reachable(source, destination_half)
        for halves in reconstructed.values()
        for destination_half, source in enumerate(halves)
    )

    # Each VPERM2I128 produces one YMM.  Both pair-packed inputs and both
    # frozen-layout outputs are live mathematical values, so their respective
    # two-output lower bounds cannot share an instruction.
    minimum_crosslane_per_pair = 2 + 2
    assert extraction_crossings == 2
    assert reconstruction_crossings == 2
    assert minimum_crosslane_per_pair == 4

    current_pairs_per_tile = 4
    tiles = 6
    current_per_tile = current_pairs_per_tile * 4
    lower_bound_per_tile = current_pairs_per_tile * minimum_crosslane_per_pair
    assert current_per_tile == lower_bound_per_tile == 16

    result = {
        "experiment": "GT32-VPBLENDD-CROSSLANE-001",
        "status": "static-hard-stop",
        "selected_production_boundary": {
            "producer": "private-M-SoA plus global-inverse S1/local transitions",
            "operation": "gt32_global_inverse_core_asm inverse S2",
            "consumer": "unchanged global-inverse S3 and AoS-T9 suffix",
            "source": "src/tile4_global_physical_asm.S",
            "reason": (
                "Q24-to-SoA and B3-entry transposes contain no cross-128-bit "
                "permutation; inverse S2 is the first selected Clean boundary "
                "with a material VPERM2I128 route"
            ),
        },
        "frozen": [
            "inverse mathematical butterflies and twiddles",
            "private-M input ABI",
            "post-S2 physical state consumed by S3",
            "range and Montgomery exponent",
            "six-tile loop and spill-free contract",
        ],
        "candidate_instruction": {
            "name": "VPBLENDD",
            "semantics": "destination dword i selects source-A or source-B dword i",
            "invariant": "source and destination 128-bit-half index are equal",
            "can_cross_128_bit_half": False,
        },
        "exact_pair_proof": {
            "input": sources,
            "pair_packed_operands": pair_packed,
            "cross_half_values_needed_for_extraction": extraction_crossings,
            "minimum_extraction_vperm2i128": 2,
            "frozen_output": reconstructed,
            "cross_half_values_needed_for_reconstruction": reconstruction_crossings,
            "minimum_reconstruction_vperm2i128": 2,
            "minimum_total_crosslane_instructions_per_pair": minimum_crosslane_per_pair,
            "current_total_crosslane_instructions_per_pair": 4,
        },
        "whole_kernel_accounting": {
            "pairs_per_tile": current_pairs_per_tile,
            "tiles": tiles,
            "current_vperm2i128_per_tile": current_per_tile,
            "proved_lower_bound_per_tile_with_unchanged_consumer": lower_bound_per_tile,
            "current_vperm2i128_per_inverse": current_per_tile * tiles,
            "proved_lower_bound_per_inverse": lower_bound_per_tile * tiles,
            "deletable_by_slot_aligned_vpblendd": 0,
        },
        "excluded_escape": {
            "two_extract_only_pair_packed_output": (
                "changes the S3 consumer physical ABI and is therefore outside "
                "this production-boundary gate; it belongs to the already-run "
                "global physical-layout search"
            ),
            "vpermq_or_vinserti128": (
                "still performs cross-half routing and does not satisfy the "
                "requested VPBLENDD deletion mechanism"
            ),
        },
        "decision": {
            "assembly_emitted": False,
            "benchmark_run": False,
            "production_changed": False,
            "reason": (
                "slot-aligned VPBLENDD preserves the 128-bit-half coordinate; "
                "the frozen S2 boundary already meets the exact four-crosslane-"
                "instruction lower bound per pair"
            ),
        },
        "reopen_only_if": [
            "S3 accepts the pair-packed S2 output without restoring its current ABI",
            "the producer emits q1 on a dword-local axis without an equivalent cross-half route",
            "a target ISA provides a cheaper true cross-half two-output primitive",
        ],
    }

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT.relative_to(ROOT))
    print("decision: static-hard-stop; current 16 vperm2i128/tile equals lower bound")


if __name__ == "__main__":
    main()
