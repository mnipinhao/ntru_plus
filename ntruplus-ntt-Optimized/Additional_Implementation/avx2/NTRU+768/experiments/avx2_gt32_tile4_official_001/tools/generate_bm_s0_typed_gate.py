#!/usr/bin/env python3
"""Priority-3 gate: raw BM accumulators -> inverse S0 -> typed packet.

This deliberately reuses the exact A2-F arithmetic/range proof.  The new
question is whether terminating in the measured I-112 packet changes the
allocation or reduction lower bound enough to justify assembly.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"


def main() -> None:
    a2f = json.loads((GENERATED / "tile4_a2f_dag.json").read_text())
    measured = json.loads(
        (ROOT / "results/tile4-priority12-executable-short.json").read_text())

    f1 = a2f["proof_gate_A2_F1"]
    f2 = a2f["proof_gate_A2_F2_direct_weighting"]
    folded = a2f["fold_tau_into_dynamic_B_control"]
    registers = a2f["register_gate"]
    assert f1["signed_int32_safe"] and f1["signed_int16_narrow_safe"]
    assert not f2["signed_int32_safe"]
    assert folded["reduction_chain_saving"] == 0
    assert registers["one_pass"]["minimum_live_ymm"] == 16
    assert not registers["one_pass"]["spill_free_with_constants"]

    i112 = measured["priority1_i112"]
    assert i112["decision"] == "cycle-hard-stop"

    result = {
        "schema": "ntruplus768-gt32-bm-s0-typed-gate-v1",
        "experiment": "GT32-BM-S0-TYPED-003",
        "candidate": "R1-U raw i32 accumulators -> inverse S0 -> I-112-like packet",
        "frozen": [
            "N5 arithmetic and TILE4 leaf semantics",
            "R1-U vpmaddwd quartic formulas",
            "inverse stages after S0",
            "Montgomery exponent e=-1 at the typed boundary",
        ],
        "exact_range_proof": {
            "raw_leaf_abs_bound": f1["raw_leaf_abs_bound"],
            "U_plus_or_minus_V_abs_bound":
                f1["wide_stage0_U_plus_or_minus_V_abs_bound"],
            "REDC_numerator_abs_bound": f1["redc_numerator_abs_bound"],
            "REDC_output_abs_bound": f1["redc_output_abs_bound"],
            "int32_safe_through_S0": True,
            "int16_safe_after_REDC": True,
        },
        "next_twiddle_limit": {
            "weighted_raw_abs_bound": f2["weighted_raw_abs_bound"],
            "int32_safe": False,
            "therefore_terminal_must_be_after": "inverse S0 and before nontrivial S1 twiddle",
        },
        "reduction_accounting": {
            "baseline_chains_per_four_leaves":
                folded["baseline_reduction_chains_per_four_leaves"],
            "safe_folded_chains_per_four_leaves":
                folded["folded_reduction_chains_per_four_leaves"],
            "chain_saving": 0,
            "conclusion": "fusion moves REDC/twiddle work but deletes no chain",
        },
        "typed_packet_update": {
            "old_static_assumption": "I-112 inverse consumer needs zero route instructions",
            "executable_result": (
                "false for the qualified inverse topology; exact entry restores "
                "the M frontier with four vperm2i128 per tile (24 total)"
            ),
            "normal_delta_tsc": i112["placements"]["normal"]["delta_tsc"],
            "reversed_delta_tsc": i112["placements"]["reversed"]["delta_tsc"],
            "packet_does_not_remove_inverse_entry_debt": True,
        },
        "allocation": {
            "one_pass": registers["one_pass"],
            "split_control": registers["split_control"],
            "typed_terminal_changes_peak": False,
            "reason": (
                "packet formation happens only after the wide arithmetic; it "
                "does not create the q/constant slot missing during the 16-YMM frontier"
            ),
        },
        "assembly_eligible": False,
        "assembly_emitted": False,
        "decision": "static-hard-stop-current-DAG",
        "failed_requirements": [
            "no Montgomery/reduction-chain saving",
            "one-pass wide frontier consumes all 16 YMM before constants",
            "spill-free split rebuilds the A1/D operand vectors",
            "measured I-112 packet still pays a 24-permute inverse entry",
        ],
        "reopen_only_if": [
            "a pair-streaming schedule proves <=15 live YMM including q/constants",
            "one dynamic pre-twiddle serves more than one required reduction",
            "a typed packet is consumed without restoring the M frontier",
            "a wider SIMD/register domain is targeted",
        ],
    }
    path = GENERATED / "tile4_bm_s0_typed_gate.json"
    path.write_text(json.dumps(result, indent=2) + "\n")
    print(path)


if __name__ == "__main__":
    main()
