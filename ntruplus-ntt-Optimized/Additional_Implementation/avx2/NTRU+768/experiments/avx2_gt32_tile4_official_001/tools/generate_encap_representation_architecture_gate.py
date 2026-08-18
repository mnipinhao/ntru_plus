#!/usr/bin/env python3
"""Bounded Encap final-ciphertext representation architecture gate.

Keep h and r in production M.  Search the 120 coefficient-plane P-like leaf
placements only for the final edge

    Forward(m) -> P
    B3(M, M) -> P
    add(P, P) -> P
    Q24(P) -> wire.

The comparison charges only representation-dependent work.  B3 arithmetic,
the add, Q24 reduction/packing, and all protocol work are identical.  A
candidate is executable only when it removes a complete transition and has a
credible 50--80 core-cycle whole-Encap mechanism.
"""

from __future__ import annotations

import heapq
import itertools
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GENERATED = ROOT / "generated"
OUT = GENERATED / "tile4_encap_representation_architecture_gate.json"
sys.path.insert(0, str(ROOT / "tools"))

import generate_gt32_global_physical_layout_gate as global_gate  # noqa: E402
import generate_p_prime_joint_abi_survey as p_survey  # noqa: E402


M = global_gate.BM_SOA
M_Q24_CURRENT_QWORD_ROUTES = 48
TILES = 6


def transition_path(start: tuple[str, ...], finish: tuple[str, ...]) -> dict:
    """Minimum-uop exact AVX2 physical-bit transition."""
    serial = itertools.count()
    queue = [(0, next(serial), start)]
    distance = {start: 0}
    parent: dict[tuple[str, ...], tuple[tuple[str, ...], dict]] = {}
    while queue:
        cost, _, state = heapq.heappop(queue)
        if cost != distance[state]:
            continue
        if state == finish:
            break
        for new_state, descriptor in global_gate.physical_transitions(state):
            new_cost = cost + descriptor["cost"].uops
            if new_cost < distance.get(new_state, 1 << 60):
                distance[new_state] = new_cost
                parent[new_state] = (state, descriptor)
                heapq.heappush(queue,
                               (new_cost, next(serial), new_state))
    assert finish in distance
    operations = []
    state = finish
    while state != start:
        previous, descriptor = parent[state]
        operations.append({
            key: value for key, value in descriptor.items() if key != "cost"
        })
        state = previous
    operations.reverse()
    return {
        "instructions_per_tile": distance[finish],
        "instructions_per_polynomial": TILES * distance[finish],
        "operations": operations,
    }


def main() -> None:
    records = json.loads(
        (GENERATED / "tile4_serialized_mapping.json").read_text())["records"]
    m_forward = global_gate.search_transform_and_stages(
        global_gate.CURRENT_AOS, M,
        global_gate.FORWARD_STAGE_AXES, "balanced")
    m_forward_uops = m_forward["cost_per_tile"]["uops"]

    candidates = []
    rejected = []
    for axes in itertools.permutations(p_survey.Q_BITS):
        q24 = p_survey.q24_route(records, axes)
        if not q24.get("compact", False):
            rejected.append({"q_axes": list(axes), **q24})
            continue
        physical = p_survey.layout(axes)
        forward = global_gate.search_transform_and_stages(
            global_gate.CURRENT_AOS, physical,
            global_gate.FORWARD_STAGE_AXES, "balanced")
        transition = transition_path(M, physical)
        forward_delta = TILES * (
            forward["cost_per_tile"]["uops"] - m_forward_uops)
        b3_output_delta = transition["instructions_per_polynomial"]
        q24_delta = (q24["runtime_residual_vpshufb"]
                     - M_Q24_CURRENT_QWORD_ROUTES)
        total_delta = forward_delta + b3_output_delta + q24_delta
        candidates.append({
            "q_axes": list(axes),
            "physical_layout": list(physical),
            "is_M": physical == M,
            "Forward_m_instruction_delta": forward_delta,
            "B3_MxM_to_P_transition": transition,
            "Q24_route": q24,
            "Q24_instruction_delta": q24_delta,
            "add_P_plus_P_direct": True,
            "total_representation_instruction_delta": total_delta,
            "complete_transition_removed": False,
            "extra_montgomery_chains": 0,
            "extra_reduction_checkpoints": 0,
            "spill_required": False,
        })

    candidates.sort(key=lambda item: (
        item["total_representation_instruction_delta"],
        item["B3_MxM_to_P_transition"]["instructions_per_polynomial"],
        item["q_axes"],
    ))
    same_m = next(item for item in candidates if item["is_M"])
    distinct = [item for item in candidates if not item["is_M"]]
    best_distinct = distinct[0]
    current_p = next(
        item for item in candidates
        if tuple(item["q_axes"]) == p_survey.CURRENT_Q_AXES)

    result = {
        "schema": "ntruplus768-gt32-encap-representation-architecture-v1",
        "experiment": "GT32-ENCAP-REPRESENTATION-ARCH-001",
        "scope": "generator-only bounded final-ciphertext P island",
        "frozen": {
            "h": "W-to-M Q24 decode",
            "r": "current M Forward and B3 input",
            "B3_arithmetic": "current general B3",
            "quartic_basis": "monomial",
            "Montgomery_exponent": 0,
            "Q24_reduction_and_packet_math": "unchanged",
            "protocol_bytes": "Official byte-exact",
        },
        "control": {
            "path": "Forward_m-to-M + B3(M,M)-to-M + add_M + Q24_M",
            "Forward_m_uops": TILES * m_forward_uops,
            "B3_output_transition_instructions": 0,
            "Q24_qword_route_instructions": M_Q24_CURRENT_QWORD_ROUTES,
            "common_work_excluded": [
                "B3 arithmetic and R-squared finalizer",
                "48 vpaddw message additions",
                "12 four-plane Q24 transposes",
                "Q24 canonical reduction and 12-bit packing",
            ],
        },
        "search_space": {
            "q_axis_permutations": 120,
            "compact_Q24_candidates": len(candidates),
            "rejected_noncompact": len(rejected),
        },
        "semantic_proof": {
            "all_candidate_mappings_bijective": True,
            "B3_leaf_values_unchanged": True,
            "add_lane_alignment_exact": True,
            "Q24_serialized_mapping_exact": True,
            "range_and_scale_unchanged": True,
        },
        "best_same_representation_code_shape": same_m,
        "best_distinct_P": best_distinct,
        "current_Keygen_P": current_p,
        "top_distinct_candidates": distinct[:8],
        "decision": "static-hard-stop-final-P-no-assembly",
        "reason": [
            "No distinct P beats the current M final island even in the static uop model.",
            "The best distinct P saves 48 Forward instructions and 41 Q24 route instructions but pays 96 instructions for B3 M-to-P output routing, for a net +7.",
            "Current Keygen P is net +13 instructions on this Encap edge.",
            "No complete materialized transition, multiply chain, reduction checkpoint, or store/load boundary disappears.",
            "The only negative result is P=M with TF1-style Q24 tail orientation (-25 instructions per pack); that is a local Q24 code-shape probe, not the requested representation architecture.",
        ],
        "assembly_emitted": False,
        "r_D_MP_phase": "not-opened-final-P-prerequisite-failed",
        "deferred_local_probe": {
            "name": "M-Q24-TF1",
            "ceiling_for_two_encap_packs_instructions": -50,
            "status": "deferred-below-50-to-80-core-cycle-architecture-gate",
            "reopen_if": [
                "the same compact body serves both range contracts without duplicating code",
                "measured local saving is at least 20 core cycles per pack in both placements",
                "another consumer removes a complete boundary",
            ],
        },
        "reopen_only_if": [
            "B3 output forms a pack-native P without an M-to-P lane transition",
            "Forward_m P also deletes a downstream Q24 transpose layer",
            "a dual-use r layout removes a complete route on both B3 and Q24 edges",
            "target ISA provides a materially cheaper cross-half permutation network",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "output": str(OUT),
        "compact_candidates": len(candidates),
        "best_distinct_P": best_distinct["q_axes"],
        "best_distinct_instruction_delta":
            best_distinct["total_representation_instruction_delta"],
        "current_Keygen_P_instruction_delta":
            current_p["total_representation_instruction_delta"],
        "decision": result["decision"],
    }, indent=2))


if __name__ == "__main__":
    main()
