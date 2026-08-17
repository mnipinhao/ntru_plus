#!/usr/bin/env python3
"""Static end-to-end gate for decoded-SoA x Forward-AoS encapsulation."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ENCODE_GATE = ROOT / "generated/tile4_correct_semantic_encodeq_gate.json"
OUTPUT = ROOT / "generated/tile4_encap_mixed_aos_soa_gate.json"


def main() -> None:
    encode = json.loads(ENCODE_GATE.read_text())
    aos_route = encode["costs"]["aos"]["materialized_route_instructions"]
    soa_route = encode["soa_grouped_e1"]["instructions"]
    direct_soa_route = encode["soa_direct_pack_e2"]["routing_instructions"]

    quartic_blocks = 192 // 16
    transpose_layer = 12 * quartic_blocks
    # Grant the proposal every plausible complete 12-shuffle layer even
    # though a real asymmetric BM may not be able to remove all three.
    optimistic_transition_credit = 3 * transpose_layer
    encode_boundaries = 2  # Encodeq(rhat) for G and Encodeq(chat).
    conservative_wire_debt = encode_boundaries * (aos_route - soa_route)
    direct_wire_debt = encode_boundaries * (aos_route - direct_soa_route)
    optimistic_net = conservative_wire_debt - optimistic_transition_credit

    result = {
        "schema": "ntruplus768-gt32-encap-mixed-aos-soa-static-v1",
        "experiment": "GT32-ENCAP-MIXED-AOS-SOA-BM-001",
        "scope": (
            "Decodeq(h)->private-SoA; Forward(r,m)->TILE4-AoS; "
            "mixed general BM SoA x AoS -> AoS; add AoS; canonical Encodeq"),
        "frozen": [
            "correct Official-index to GT semantic mapping",
            "two spec-visible Encodeq boundaries: rhat and chat",
            "current quartic monomial basis and Montgomery contracts",
            "no global materialization pass in an eligible candidate",
        ],
        "provenance": {
            "h": "canonical bytes -> corrected-semantic private SoA e=0",
            "r": "CBD -> GT32 Forward TILE4 AoS e=0",
            "m": "SOTP -> GT32 Forward TILE4 AoS e=0",
        },
        "mandatory_wire_edges": [
            "Forward(rhat) -> Encodeq(rhat) -> G before BaseMul",
            "BMgeneral(hhat,rhat) + mhat -> Encodeq(chat)",
        ],
        "encode_route_costs_excluding_common_pack_arithmetic": {
            "TILE4_AoS_materialized_route_per_polynomial": aos_route,
            "private_SoA_grouped_materialized_route_per_polynomial": soa_route,
            "private_SoA_direct_pack_route_per_polynomial": direct_soa_route,
            "AoS_minus_grouped_SoA_per_polynomial": aos_route - soa_route,
            "AoS_minus_direct_SoA_per_polynomial": aos_route - direct_soa_route,
            "network_class": encode["network_class"],
        },
        "optimistic_accounting": {
            "quartic_blocks": quartic_blocks,
            "instructions_per_complete_transpose_layer_per_block": 12,
            "instructions_per_complete_transpose_layer_per_polynomial":
                transpose_layer,
            "credited_removed_layers": 3,
            "credited_removed_transition_instructions":
                optimistic_transition_credit,
            "AoS_wire_debt_vs_grouped_SoA_for_two_Encodeq":
                conservative_wire_debt,
            "AoS_wire_debt_vs_direct_SoA_for_two_Encodeq": direct_wire_debt,
            "optimistic_candidate_regression_vs_grouped_SoA": optimistic_net,
            "note": (
                "The three-layer credit deliberately over-favors the "
                "candidate; the existing mixed B3 still transposes its AoS "
                "operand internally and cannot claim all of this credit."),
        },
        "existing_mixed_symbol": {
            "symbol": "gt32_tile4_basemul_general_soa_aos_to_aos_asm",
            "mathematics_and_scale_match": True,
            "direct_AoS_dot_product": False,
            "AoS_operand_transposed_inside_B3": True,
            "eligible_as_new_acceleration_mechanism": False,
        },
        "static_gates": {
            "no_global_SoA_to_AoS_or_AoS_to_pack_pass": False,
            "alignment_at_most_four_extra_shuffles_per_block": False,
            "no_spill": "not_reached",
            "end_to_end_positive_after_two_Encodeq": False,
        },
        "decision": "static-hard-stop-before-assembly-AoS-wire-boundary-debt",
        "assembly_emitted": False,
        "benchmark_run": False,
        "production_integration": False,
        "reopen_only_with": [
            "Forward-r dual-use packet that is simultaneously BM-AoS and pack-native without duplication",
            "mixed general BM output directly in private-SoA or Official-pack-input P",
            "new AoS direct Encodeq network saving at least 1032 route instructions per encoded polynomial",
        ],
        "next_viable_typed_shape": (
            "Decodeq(h)->M; Forward(r)->typed dual-use M/P packet; "
            "BMgeneral(M,A/P)->P; add Forward(m)->P; unchanged pack"),
    }
    OUTPUT.write_text(json.dumps(result, indent=2) + "\n")
    print(f"wrote {OUTPUT}")
    print(f"decision={result['decision']}")


if __name__ == "__main__":
    main()
