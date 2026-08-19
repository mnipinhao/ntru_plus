#!/usr/bin/env python3
"""Inventory the AVX2 representation space beyond bit-axis permutations.

011 is deliberately a coverage gate, not a claim to enumerate arbitrary
linear representations.  It gives packet semantics, linear basis, 128-bit
half ownership, operand coupling, and lane width independent identities, and
then records which combinations have actually been tested by earlier GT32
experiments.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from pathlib import Path


Q = 3457
HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
EXPERIMENTS = EXPERIMENT.parent
LEGACY = EXPERIMENTS / "avx2_gt32_tile4_official_001"
S9 = EXPERIMENTS / "gt32_joint_transform_basis_009"
S10 = EXPERIMENTS / "gt32_joint_transform_superspace_010"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path: Path, decision_path: tuple[str, ...] = ()) -> dict:
    record = {"path": str(path.resolve()), "sha256": sha256(path)}
    if decision_path:
        value = json.loads(path.read_text())
        for key in decision_path:
            value = value[key]
        record["recorded_decision"] = value
    return record


def rank_mod(matrix: list[list[int]], modulus: int = Q) -> int:
    work = [[value % modulus for value in row] for row in matrix]
    rows = len(work)
    cols = len(work[0]) if rows else 0
    rank = 0
    for col in range(cols):
        pivot = next((row for row in range(rank, rows) if work[row][col]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][col], -1, modulus)
        work[rank] = [(value * inverse) % modulus for value in work[rank]]
        for row in range(rows):
            if row == rank or not work[row][col]:
                continue
            factor = work[row][col]
            work[row] = [
                (left - factor * right) % modulus
                for left, right in zip(work[row], work[rank])
            ]
        rank += 1
        if rank == rows:
            break
    return rank


def inverse_mod(matrix: list[list[int]], modulus: int = Q) -> list[list[int]]:
    size = len(matrix)
    assert size and all(len(row) == size for row in matrix)
    work = [
        [value % modulus for value in row]
        + [int(row_index == col) for col in range(size)]
        for row_index, row in enumerate(matrix)
    ]
    for col in range(size):
        pivot = next(row for row in range(col, size) if work[row][col])
        work[col], work[pivot] = work[pivot], work[col]
        inverse = pow(work[col][col], -1, modulus)
        work[col] = [(value * inverse) % modulus for value in work[col]]
        for row in range(size):
            if row == col:
                continue
            factor = work[row][col]
            work[row] = [
                (left - factor * right) % modulus
                for left, right in zip(work[row], work[col])
            ]
    return [row[size:] for row in work]


def matmul(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    return [
        [sum(a * b for a, b in zip(row, col)) % Q for col in zip(*right)]
        for row in left
    ]


def quartic_tensor_support(basis: list[list[int]]) -> dict:
    """Naive bilinear support after the same square basis on A/B/output.

    This is not tensor rank and is never used as a performance veto.  It is
    an exact diagnostic that stops a dense linear basis from being mistaken
    for a free coefficient permutation.
    """
    inverse = inverse_mod(basis)
    nonzero = 0
    lambda_weighted = 0
    by_output = []
    for out in range(4):
        output_terms = 0
        output_lambda = 0
        for lhs in range(4):
            for rhs in range(4):
                coefficient_plain = 0
                coefficient_lambda = 0
                for degree_a in range(4):
                    for degree_b in range(4):
                        degree = degree_a + degree_b
                        wrapped = degree >= 4
                        target = degree - 4 if wrapped else degree
                        term = basis[out][target] * inverse[degree_a][lhs]
                        term *= inverse[degree_b][rhs]
                        if wrapped:
                            coefficient_lambda += term
                        else:
                            coefficient_plain += term
                coefficient_plain %= Q
                coefficient_lambda %= Q
                if coefficient_plain:
                    nonzero += 1
                    output_terms += 1
                if coefficient_lambda:
                    nonzero += 1
                    lambda_weighted += 1
                    output_terms += 1
                    output_lambda += 1
        by_output.append({
            "output": out,
            "nonzero_tensor_coefficients": output_terms,
            "lambda_weighted": output_lambda,
        })
    return {
        "nonzero_tensor_coefficients": nonzero,
        "lambda_weighted": lambda_weighted,
        "by_output": by_output,
        "warning": "support count is exact but is not bilinear rank or an AVX2 instruction count",
    }


BASES = {
    "coeff": {
        "forms": [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
        "class": "monomial",
    },
    "pair01_sumdiff": {
        "forms": [[1, 1, 0, 0], [1, -1, 0, 0], [0, 0, 1, 1], [0, 0, 1, -1]],
        "class": "invertible_pair_evaluation",
    },
    "pair02_sumdiff": {
        "forms": [[1, 0, 1, 0], [1, 0, -1, 0], [0, 1, 0, 1], [0, 1, 0, -1]],
        "class": "invertible_pair_evaluation",
    },
    "pair03_sumdiff": {
        "forms": [[1, 0, 0, 1], [1, 0, 0, -1], [0, 1, 1, 0], [0, 1, -1, 0]],
        "class": "invertible_pair_evaluation",
    },
    "walsh4": {
        "forms": [[1, 1, 1, 1], [1, -1, 1, -1], [1, 1, -1, -1], [1, -1, -1, 1]],
        "class": "invertible_full_evaluation",
    },
    "K2_L01_expanded": {
        "forms": [
            [1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1],
            [1, 1, 0, 0], [0, 0, 1, 1], [1, 0, 1, 0], [0, 1, 0, 1],
            [1, 1, 1, 1],
        ],
        "class": "redundant_karatsuba_evaluation",
    },
}


PACKETS = {
    "current_packet": {
        "semantic": "four leaves times four quartic coefficients",
        "stored_forms_per_leaf": 4,
        "allowed_bases": ["coeff"],
        "half_modes": ["quartic_pair_halves"],
    },
    "plane_strip": {
        "semantic": "sixteen leaves of one coefficient plane",
        "stored_forms_per_leaf": 4,
        "allowed_bases": ["coeff"],
        "half_modes": ["leaf_subset_halves"],
    },
    "hybrid_strip": {
        "semantic": "eight leaves times two quartic components per vector",
        "stored_forms_per_leaf": 4,
        "allowed_bases": ["coeff", "pair01_sumdiff", "pair02_sumdiff", "pair03_sumdiff"],
        "half_modes": ["leaf_subset_halves", "component_pair_halves"],
    },
    "cross_R3_packet": {
        "semantic": "matching leaf subsets from distinct R3 branches in low/high halves",
        "stored_forms_per_leaf": 4,
        "allowed_bases": ["coeff", "pair01_sumdiff", "pair02_sumdiff", "pair03_sumdiff", "walsh4"],
        "half_modes": ["R3_branch_pair_halves"],
    },
    "BaseMul_pair_packet": {
        "semantic": "adjacent coefficient pairs prepared for bilinear operations",
        "stored_forms_per_leaf": 4,
        "allowed_bases": ["coeff", "pair01_sumdiff", "pair02_sumdiff", "pair03_sumdiff"],
        "half_modes": ["component_pair_halves", "even_odd_halves"],
    },
    "evaluation_packet": {
        "semantic": "linear evaluation forms rather than materialized monomial coefficients",
        "stored_forms_per_leaf": 9,
        "allowed_bases": ["K2_L01_expanded"],
        "half_modes": ["evaluation_class_halves"],
    },
}


def basis_library() -> dict:
    result = {}
    for name, basis in BASES.items():
        forms = basis["forms"]
        rank = rank_mod(forms)
        record = {
            "class": basis["class"],
            "forms": forms,
            "stored_forms": len(forms),
            "rank_mod_q": rank,
            "spans_quartic_coefficients": rank == 4,
            "redundant": len(forms) > 4,
        }
        if len(forms) == 4 and rank == 4:
            inverse = inverse_mod(forms)
            assert matmul(forms, inverse) == [
                [int(row == col) for col in range(4)] for row in range(4)
            ]
            record["inverse_mod_q"] = inverse
            record["quartic_tensor_support"] = quartic_tensor_support(forms)
        result[name] = record
    return result


def enumerate_states() -> list[dict]:
    states = []
    for packet_name, packet in PACKETS.items():
        for basis_name, half_mode, lane_width, coupling in itertools.product(
            packet["allowed_bases"], packet["half_modes"], (16, 32),
            ("single_poly", "lhs_rhs_pair")
        ):
            lanes = 256 // lane_width
            stored_forms = len(BASES[basis_name]["forms"])
            vectors_per_16_leaves = (16 * stored_forms + lanes - 1) // lanes
            two_operand_vectors = vectors_per_16_leaves * 2
            minimum_live_with_q_and_temp = two_operand_vectors + 2
            persistent_no_spill = minimum_live_with_q_and_temp <= 16
            state = {
                "id": f"{packet_name}/{basis_name}/i{lane_width}/{half_mode}/{coupling}",
                "packet": packet_name,
                "basis": basis_name,
                "lane_width": lane_width,
                "lanes_per_YMM": lanes,
                "half_semantics": half_mode,
                "operand_coupling": coupling,
                "vectors_per_16_leaves_per_poly": vectors_per_16_leaves,
                "two_operand_vectors_before_constants": two_operand_vectors,
                "minimum_live_with_q_and_one_temp": minimum_live_with_q_and_temp,
                "persistent_two_operand_no_spill_capacity": persistent_no_spill,
            }
            if lane_width == 32:
                state["width_observation"] = (
                    "coefficient storage doubles versus i16; AVX2 has eight dword lanes "
                    "and no packed 32-bit high-half multiply matching the current REDC16 path"
                )
            if coupling == "lhs_rhs_pair":
                state["coupling_observation"] = (
                    "placing lhs/rhs in opposite halves does not by itself feed vpmaddwd; "
                    "the instruction still requires two source operands"
                )
            state["coverage_class"] = classify_state(state)
            states.append(state)
    return states


def classify_state(state: dict) -> str:
    if state["lane_width"] == 32:
        return "not_globally_covered_lane_width"
    if state["operand_coupling"] == "lhs_rhs_pair":
        return "not_globally_covered_operand_coupling"
    packet = state["packet"]
    basis = state["basis"]
    if packet in ("current_packet", "plane_strip") and basis == "coeff":
        return "covered_control"
    if packet == "hybrid_strip":
        return "one_L01_trajectory_covered_family_open"
    if packet == "cross_R3_packet":
        return "narrow_R3_packets_covered_typed_halves_open"
    if packet == "BaseMul_pair_packet":
        return "algebra_and_posthoc_formation_covered_persistence_open"
    if packet == "evaluation_packet":
        return "terminal_forms_covered_persistent_stream_open"
    raise AssertionError(state)


def instruction_semantics() -> dict:
    return {
        "vperm2i128": {
            "unit": "128-bit half",
            "architecture_use": "exchange or select complete typed semantic objects",
        },
        "vpunpcklqdq_vpunpckhqdq": {
            "unit": "64-bit quartic/pair object within each half",
            "architecture_use": "pair qword objects without crossing 128-bit lanes",
        },
        "vpunpcklwd_vpunpckhwd": {
            "unit": "16-bit coefficient/form",
            "architecture_use": "interleave pair components or leaf subsets",
        },
        "vpunpckldq_vpunpckhdq": {
            "unit": "32-bit pair/accumulator",
            "architecture_use": "interleave widened pair results",
        },
        "vpblendd_vpblendw": {
            "unit": "selected dword/word lanes",
            "architecture_use": "merge typed packets when ownership is already aligned",
        },
        "vpshufb": {
            "unit": "bytes within independent 128-bit halves",
            "architecture_use": "local packet formation only; cannot cross halves",
        },
        "vshufps": {
            "unit": "32-bit lanes within independent 128-bit halves",
            "architecture_use": "two-source dword packet routing",
        },
        "vpmaddwd": {
            "unit": "adjacent signed-word pairs contracted to dwords",
            "architecture_use": "BaseMul-selected dot/pair packets",
        },
    }


def coverage_registry() -> dict:
    generated = LEGACY / "generated"
    return {
        "Level1_bit_permutation": {
            "status": "substantially_covered",
            "artifact": artifact(generated / "tile4_global_physical_layout_gate.json", ("decision",)),
            "scope": "fixed 128xi16 tensor with logical axes assigned to register/lane bits",
        },
        "Current_and_plane_packets": {
            "status": "covered_controls",
            "artifacts": [
                artifact(EXPERIMENTS / "gt32_plane_n16_stockham_stages_007/generated/plane_n16_stockham_gate.json"),
                artifact(EXPERIMENTS / "gt32_plane_n16_radix4_route_elim_008/generated/plane_n16_radix4_gate.json", ("decision", "status")),
            ],
        },
        "one_plane_Hybrid_L01": {
            "status": "one_family_covered_not_general_Hybrid",
            "artifact": artifact(S9 / "generated/joint_transform_basis_gate.json", ("gate_decision", "status")),
            "missing": "other pair partitions and a producer-native packet that persists through inverse",
        },
        "BaseMul_pair_and_K2": {
            "status": "algebra_and_posthoc_formation_covered",
            "artifacts": [
                artifact(generated / "tile4_pair_native_bm_gate.json"),
                artifact(generated / "tile4_pair02_exact_dag_tile_gate.json", ("decision",)),
                artifact(generated / "tile4_terminal_karatsuba_basis_gate.json", ("decision",)),
            ],
            "missing": "producer-born pair/evaluation packets with inverse-native output",
        },
        "Cross_R3_packets": {
            "status": "narrow_8_10_12YMM_and_relocation_gates_only",
            "artifact": artifact(S10 / "generated/joint_transform_superspace_gate.json"),
            "missing": "128-bit halves as independently typed R3 semantic objects across the whole island",
        },
        "i32_accumulation": {
            "status": "isolated_AoS_dot_REDC32_and_REDC16_evidence_only",
            "artifact": artifact(generated / "tile4_aos_dot_redc16_gate.json"),
            "missing": "a mixed-width producer/BM/inverse schedule; persistent i32 is capacity-blocked below",
        },
        "operand_coupled_packets": {
            "status": "not_globally_searched",
            "missing": "a two-runtime-operand packet whose coupling deletes a complete load/formation class",
        },
    }


def family_census(states: list[dict]) -> dict:
    census = {}
    for name, packet in PACKETS.items():
        members = [state for state in states if state["packet"] == name]
        census[name] = {
            "semantic": packet["semantic"],
            "states_enumerated": len(members),
            "basis_variants": packet["allowed_bases"],
            "half_modes": packet["half_modes"],
            "persistent_no_spill_states": sum(
                state["persistent_two_operand_no_spill_capacity"] for state in members
            ),
            "minimum_vectors_per_16_leaves_per_poly": min(
                state["vectors_per_16_leaves_per_poly"] for state in members
            ),
            "maximum_vectors_per_16_leaves_per_poly": max(
                state["vectors_per_16_leaves_per_poly"] for state in members
            ),
            "coverage_classes": sorted({state["coverage_class"] for state in members}),
        }
    return census


def width_gate(states: list[dict]) -> dict:
    monomial_i32 = [
        state for state in states
        if state["basis"] == "coeff" and state["lane_width"] == 32
    ]
    assert monomial_i32
    assert all(state["vectors_per_16_leaves_per_poly"] == 8 for state in monomial_i32)
    assert all(state["minimum_live_with_q_and_one_temp"] == 18 for state in monomial_i32)
    return {
        "persistent_full_block_i32": {
            "vectors_per_operand": 8,
            "two_operands": 16,
            "minimum_with_q_and_one_arithmetic_temp": 18,
            "available_YMM": 16,
            "decision": "static_stop_for_persistent_two_operand_full_block_without_spill_or_replay",
        },
        "transient_i32_accumulator": {
            "status": "conditional_open",
            "reason": "widening after packet formation may still win if it deletes multiple REDC16 chains before repacking",
            "required_mechanism": "delete a complete reduction class; width conversion alone is insufficient",
        },
    }


def open_frontier() -> list[dict]:
    return [
        {
            "priority": 1,
            "family": "cross_R3_packet",
            "state": "i16/coeff/R3_branch_pair_halves/single_poly",
            "why_new": "low/high 128-bit halves are typed branch objects, not two halves of one bit permutation",
            "next_exact_gate": "allocate Top->R3-paired packet->first complete R2 consumer and the symmetric inverse join",
            "hard_stop": "source replay, a six-array materialization, or no complete operation-class deletion",
        },
        {
            "priority": 2,
            "family": "evaluation_packet",
            "state": "i16/K2_L01_expanded/evaluation_class_halves/single_poly",
            "why_new": "stored words are redundant linear forms, not coefficients",
            "capacity_fact": "nine vectors per operand means eighteen before constants; a persistent two-operand block must stream",
            "next_exact_gate": "prove producer formation and BM consumption in one bounded stream, then synthesize inverse-native output",
            "hard_stop": "materialize all nine forms for both operands or reconstruct monomial output before inverse",
        },
        {
            "priority": 3,
            "family": "BaseMul_pair_packet",
            "state": "i16/pair03_sumdiff/component_pair_halves/single_poly",
            "why_new": "L03 persistent producer/inverse trajectory is not covered by the L01 Hybrid or Pair02 gates",
            "next_exact_gate": "tensor/range screen before any physical schedule",
            "hard_stop": "same 12/13-chain economics with an additional checkpoint or terminal repair",
        },
        {
            "priority": 4,
            "family": "mixed_width_transient",
            "state": "i16 producer -> i32 accumulator -> i16 inverse packet",
            "why_new": "lane width changes only inside the bilinear consumer",
            "next_exact_gate": "instruction-DAG comparison against selected B3 with pack/unpack and REDC charged",
            "hard_stop": "no reduction-chain deletion or any full-block persistent i32 state",
        },
    ]


def build() -> dict:
    bases = basis_library()
    assert all(record["spans_quartic_coefficients"] for record in bases.values())
    states = enumerate_states()
    # This count is a regression guard for the explicit grammar, not a claim
    # about the cardinality of arbitrary AVX2 representations.
    assert len(states) == 96
    return {
        "schema": "gt32-avx2-packing-superspace-v1",
        "experiment": "GT32-AVX2-PACKING-SUPERSPACE-011",
        "production_modified": False,
        "assembly_emitted": False,
        "scope_correction": {
            "old_state": "bijection from seven logical bits to register/lane bits over a fixed 128xi16 tensor",
            "new_independent_dimensions": [
                "semantic_packet", "linear_basis", "half_semantics",
                "operand_coupling", "lane_width",
            ],
            "non_claim": "the explicit grammar is a coverage census, not an exhaustive enumeration of arbitrary linear representations",
        },
        "representation_grammar": {
            "lane_width": [16, 32],
            "semantic_packet": list(PACKETS),
            "linear_basis": list(BASES),
            "half_semantics": sorted({
                mode for packet in PACKETS.values() for mode in packet["half_modes"]
            }),
            "operand_coupling": ["single_poly", "lhs_rhs_pair"],
            "state_count": len(states),
        },
        "AVX2_instruction_semantics": instruction_semantics(),
        "coverage_registry": coverage_registry(),
        "exact_basis_library": bases,
        "family_census": family_census(states),
        "lane_width_gate": width_gate(states),
        "states": states,
        "open_frontier": open_frontier(),
        "decision": {
            "status": "coverage_gap_confirmed_next_family_selected_no_asm",
            "Level1_permutation_search": "substantially covered",
            "Level2_packet_search": "partially covered",
            "Level3_algebraic_SIMD_basis": "only narrow L01/terminal gates covered",
            "first_next_gate": "cross_R3 i16 coefficient packet with independently typed 128-bit halves",
            "why_not_evaluation_first": "expanded K2 requires nine vectors per operand and therefore a streaming proof before it is executable",
            "reopen_i32_only_if": "a transient widened DAG deletes a complete reduction class including conversion cost",
            "GT_Clean_modified": False,
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
