#!/usr/bin/env python3
"""Generate the PREPARED-F-B3-INVS1 static architecture gate.

This gate deliberately models the production global inverse, whose S1 is a
raw butterfly followed by layout routing.  There is no inverse-S1 twiddle or
Montgomery chain to fold.  The candidate forms the two leaf-half fixed dots,
does the raw S1 add/sub in int32, applies terminal REDC16, and emits the exact
post-S1 physical layout without materializing the B3 output ABI.
"""

from __future__ import annotations

import json
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "generated/tile4_prepared_f_b3_invs1_gate.json"

Q = 3457
FIXED_F_BOUND = 1728
DECODED_C_BOUND = Q - 1


def main() -> None:
    # Counts are for one natural 16-leaf M block.  The production B3 loop is
    # one block/iteration.  Global inverse S1 consumes two blocks/iteration,
    # hence half of its exact 40-instruction prefix is charged here.
    current_b3_loop = 114
    inverse_s1_per_32 = {
        "loads": 8,
        "word_unpacks": 8,
        "raw_add_sub": 8,
        "dword_unpacks": 8,
        "qword_unpacks": 8,
    }
    inverse_s1_total_32 = sum(inverse_s1_per_32.values())
    inverse_s1_amortized = inverse_s1_total_32 // 2
    current_total = current_b3_loop + inverse_s1_amortized

    # Exact executable schedule using the already-proven fixed-dot REDC16
    # geometry.  Four coefficient outputs each need two four-term half dots.
    # The two half accumulators are added/subtracted before REDC.  The 20-op
    # route is the known exact construction: reconstruct four post-word-S1
    # vectors (12) and apply the production dword/qword routes (8).
    candidate = {
        "dynamic_plane_loads": 4,
        "dynamic_pair_unpacks": 4,
        "vpmaddwd": 16,
        "dot_vpaddd": 8,
        "s1_vpaddd_vpsubd": 8,
        "terminal_REDC16": 32,
        "even_word_compaction": 16,
        "exact_post_s1_route": 20,
        "stores": 4,
        "loop_control": 5,
    }
    candidate_total = sum(candidate.values())
    saving = current_total - candidate_total
    saving_percent = 100.0 * saving / current_total

    # Each final S1 accumulator is an eight-term centered fixed dot.
    accumulator_bound = 8 * DECODED_C_BOUND * FIXED_F_BOUND
    redc_bound = math.ceil(accumulator_bound / (1 << 16)) + (Q - 1)
    assert accumulator_bound < 2**31
    assert redc_bound < 32768

    # A lower route bound of 12 would just cross the agreed 15--20% gate, but
    # no exact 12-op route is known.  It is recorded only as a reopen condition,
    # not used to qualify assembly.
    hypothetical_route = 12
    hypothetical_total = candidate_total - candidate["exact_post_s1_route"] + hypothetical_route
    hypothetical_saving_percent = 100.0 * (current_total - hypothetical_total) / current_total

    report = {
        "experiment": "PREPARED-F-B3-INVS1-STATIC-001",
        "production_path": {
            "basemul": "gt32_tile4_basemul_scale_soa_soa_to_m_private_asm",
            "inverse": "gt32_global_inverse_core_asm",
            "important_correction": (
                "production inverse S1 is a raw add/sub butterfly; it has no "
                "twiddle or Montgomery chain"
            ),
        },
        "current_per_16_leaves": {
            "B3_scale_loop_instructions": current_b3_loop,
            "inverse_S1_per_32_leaves": inverse_s1_per_32,
            "inverse_S1_instructions_per_32_leaves": inverse_s1_total_32,
            "inverse_S1_amortized_per_16_leaves": inverse_s1_amortized,
            "total_replaced_region": current_total,
        },
        "composite_per_16_leaves": {
            "instruction_accounting": candidate,
            "total": candidate_total,
            "vpmaddwd_count": candidate["vpmaddwd"],
            "logical_dot_shape": "four outputs x two four-term half dots",
            "intermediate_B3_representation_materialized": False,
            "peak_YMM": 14,
            "spill_required": False,
        },
        "reduction_analysis": {
            "candidate_terminal_REDC16_representatives": 8,
            "inverse_S1_REDC_removed": 0,
            "reason": "production inverse S1 contains no reduction",
            "fusion_specific_reduction_layer_eliminated": False,
            "note": (
                "REDC is delayed until after the raw S1 add/sub, but its count "
                "is the same eight representatives required by standalone fixed-dot output"
            ),
        },
        "range_proof": {
            "decoded_ciphertext_bound": DECODED_C_BOUND,
            "prepared_centered_f_bound": FIXED_F_BOUND,
            "eight_term_int32_accumulator_bound": accumulator_bound,
            "signed_int32_margin": 2**31 - accumulator_bound,
            "conservative_terminal_REDC16_bound": redc_bound,
            "int32_safe": True,
            "int16_output_safe": True,
        },
        "comparison": {
            "instruction_saving": saving,
            "instruction_saving_percent": saving_percent,
            "required_local_cycle_saving_percent": [15, 20],
            "known_exact_schedule_meets_static_filter": saving_percent >= 15.0,
            "hypothetical_12_route_total": hypothetical_total,
            "hypothetical_12_route_saving_percent": hypothetical_saving_percent,
        },
        "decision": {
            "status": "static-hard-stop",
            "emit_assembly": False,
            "reasons": [
                "the exact production inverse S1 has no twiddle/REDC chain to fold",
                "the known exact post-S1 route leaves only 12.7% static headroom",
                "this is below the precommitted 15-20% local core-cycle gate",
                "the fixed-dot dword compaction remains on the runtime path",
            ],
            "reopen_only_if": [
                "an exact post-S1 route uses at most 12 instructions instead of 20",
                "the producer supplies the dynamic operand in pair-packed dword form",
                "a wider ISA removes the even-word compaction or register constraint",
                "a later consumer accepts an earlier composite representation and deletes another full route",
            ],
        },
    }
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(OUT)


if __name__ == "__main__":
    main()
