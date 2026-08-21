#!/usr/bin/env python3
"""Coverage/lower-bound gate for an Encap-native quartic basis.

This gate deliberately does not claim to search arbitrary GL(4,q) bases or
new bilinear multiplication tensors.  It closes the structured ternary basis
class already used by the terminal Karatsuba search, after adding the missing
WIRE12/Encap consumer-graph accounting.
"""

from __future__ import annotations

import hashlib
import itertools
import json
from fractions import Fraction
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
LEGACY = REPO / "experiments/avx2_gt32_tile4_official_001/generated"
OUT = ROOT / "generated/encap_tensor_basis_058.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inverse(matrix: list[list[int]]) -> list[list[Fraction]] | None:
    size = len(matrix)
    work = [
        [Fraction(value) for value in row]
        + [Fraction(index == column) for column in range(size)]
        for index, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next((row for row in range(column, size)
                      if work[row][column]), None)
        if pivot is None:
            return None
        work[column], work[pivot] = work[pivot], work[column]
        divisor = work[column][column]
        work[column] = [value / divisor for value in work[column]]
        for row in range(size):
            if row == column:
                continue
            multiplier = work[row][column]
            work[row] = [value - multiplier * pivot_value
                         for value, pivot_value
                         in zip(work[row], work[column])]
    return [row[size:] for row in work]


def multiply(left: list[list[int]], right: list[list[Fraction]]) \
        -> list[list[Fraction]]:
    return [[sum(Fraction(a) * b for a, b in zip(row, column))
             for column in zip(*right)] for row in left]


def synthesis_cost(rows: list[list[Fraction]]) -> int | None:
    """Reuse the deliberately optimistic prior K2 lowering model."""
    if any(value.denominator != 1 or abs(value) > 1
           for row in rows for value in row):
        return None
    support = max(sum(value != 0 for value in row) for row in rows)
    return 2 * support - 1


def main() -> None:
    prior_basis_path = LEGACY / "tile4_terminal_karatsuba_basis_gate.json"
    mixed_path = LEGACY / "tile4_encap_h_d01_mixed_tmvp_gate.json"
    rep_path = LEGACY / "tile4_encap_representation_architecture_gate.json"
    pprime_path = LEGACY / "tile4_p_prime_joint_abi_survey.json"
    prior_basis = json.loads(prior_basis_path.read_text())
    mixed = json.loads(mixed_path.read_text())
    representation = json.loads(rep_path.read_text())
    pprime = json.loads(pprime_path.read_text())

    k2_forms = [
        [1, 0, 0, 0], [0, 1, 0, 0], [1, 1, 0, 0],
        [0, 0, 1, 0], [0, 0, 0, 1], [0, 0, 1, 1],
        [1, 0, 1, 0], [0, 1, 0, 1],
    ]
    possible_rows: list[list[int]] = []
    for row in itertools.product((-1, 0, 1), repeat=4):
        if row == (0, 0, 0, 0):
            continue
        if next(value for value in row if value) < 0:
            continue
        possible_rows.append(list(row))
    assert len(possible_rows) == 40

    rank_four = 0
    k2_eligible = 0
    monomial_up_to_order = 0
    best_total = None
    best_nonmonomial = None
    for indexes in itertools.combinations(range(40), 4):
        basis = [possible_rows[index] for index in indexes]
        inv = inverse(basis)
        if inv is None:
            continue
        rank_four += 1
        coordinates = multiply(k2_forms, inv)
        c0 = synthesis_cost(coordinates[:4])
        c1 = synthesis_cost(coordinates[4:])
        if c0 is None or c1 is None:
            continue
        k2_eligible += 1
        monomial = all(sum(value != 0 for value in row) == 1
                       for row in basis)
        if monomial:
            monomial_up_to_order += 1
            formation = 0
        else:
            formation = synthesis_cost(
                [[Fraction(value) for value in row] for row in basis])
            assert formation is not None
        total = formation + c0 + c1
        best_total = total if best_total is None else min(best_total, total)
        if not monomial:
            best_nonmonomial = total if best_nonmonomial is None \
                else min(best_nonmonomial, total)

    prior_search = prior_basis["compact_basis_search"]
    assert rank_four == prior_search["rank_four_bases"] == 72780
    assert k2_eligible == \
        prior_search["bases_with_integral_unit-coefficient_K2_synthesis"] \
        == 979
    assert best_total == 6
    assert best_nonmonomial == 9
    assert monomial_up_to_order == 1
    assert prior_search["selected_is_existing_monomial_basis"]
    assert mixed["gate_A_decoder"]["net_edge_representation_saving"] == 0
    assert mixed["gate_B_complete_mixed_B3"]["edge_instructions"] \
        ["candidate_minus_current"] == 96
    assert representation["best_distinct_P"] \
        ["total_representation_instruction_delta"] == 7
    assert pprime["search_space"]["q_axis_permutations"] == 120

    report = {
        "schema": "ntruplus768-gt32-encap-tensor-basis-coverage-v1",
        "experiment": "GT32-ENCAP-TENSOR-BASIS-058",
        "scope": (
            "generator-only WIRE12-aware coverage and lower-bound gate for "
            "the current quartic algebra and structured ternary basis class"
        ),
        "production_modified": False,
        "question": (
            "Does a structured quartic degree basis already covered by the "
            "K2 search become attractive after accounting for the complete "
            "Encap WIRE12 consumer graph?"
        ),
        "frozen": [
            "Good-Thomas factorization and current quartic leaves",
            "current K2/TMVP multiplication tensor",
            "WIRE12 semantics and canonical bytes",
            "current CBD and SOTP coefficient producers",
            "AVX2 with sixteen YMM registers",
        ],
        "source_artifacts": {
            prior_basis_path.name: sha256(prior_basis_path),
            mixed_path.name: sha256(mixed_path),
            rep_path.name: sha256(rep_path),
            pprime_path.name: sha256(pprime_path),
        },
        "coverage": {
            "sign_normalized_ternary_rows": len(possible_rows),
            "rank_four_bases": rank_four,
            "K2_eligible_bases": k2_eligible,
            "zero_arithmetic_wire_bases_up_to_lane_order":
                monomial_up_to_order,
            "physical_q_axis_permutations_separately_surveyed":
                pprime["search_space"]["q_axis_permutations"],
            "mixed_Q24_D01_x_M_TMVP_separately_gated": True,
        },
        "wire_basis_proof": {
            "wire_coordinates": "quartic monomial coefficients c0,c1,c2,c3",
            "zero_arithmetic_linear_conversion_condition": (
                "each output selects one existing coordinate; invertibility "
                "therefore forces a permutation matrix"
            ),
            "lane_permutations": (
                "optimistically treated as absorbable into existing Q24 "
                "shuffle masks"
            ),
            "nonmonomial_basis": (
                "requires at least one add/sub operation and cannot be formed "
                "by byte/lane routing alone"
            ),
            "signed_monomial_note": (
                "a negative coordinate is not free at WIRE12 because canonical "
                "q-x correction is arithmetic; the sign-normalized zero-cost "
                "class contains the ordinary monomial basis"
            ),
        },
        "encap_graph": {
            "wire_to_basis": ["Decode(h)"],
            "coefficient_producer_to_basis": ["CBD(r)->Forward", "SOTP(m)->Forward"],
            "basis_to_wire": ["serialize(r-hat)", "serialize(ciphertext)"],
            "basis_preserving": ["B3", "add(m)"],
            "potential_nonmonomial_boundary_crossings": 5,
            "accounting_rule": (
                "a candidate receives no credit for moving basis formation "
                "between these edges; it must delete work from the complete graph"
            ),
        },
        "structured_basis_result": {
            "current_monomial_formation_plus_K2_lower_bound": best_total,
            "best_nonmonomial_formation_plus_K2_lower_bound": best_nonmonomial,
            "nonmonomial_K2_operand_synthesis_improvement": 0,
            "wire_boundary_cost_direction": "strictly worse than monomial",
            "dominance": (
                "within this class, no nonmonomial basis lowers K2 operand "
                "synthesis, while every nonmonomial basis adds arithmetic at "
                "one or more producer/wire boundaries"
            ),
        },
        "independent_negative_controls": {
            "Q24_D01_decoder_saving":
                mixed["gate_A_decoder"]["decoder_saving_per_polynomial"],
            "Q24_D01_representation_net":
                mixed["gate_A_decoder"]["net_edge_representation_saving"],
            "mixed_D01xM_TMVP_complete_edge_delta_instructions":
                mixed["gate_B_complete_mixed_B3"]["edge_instructions"]
                ["candidate_minus_current"],
            "best_distinct_P_complete_representation_delta_instructions":
                representation["best_distinct_P"]
                ["total_representation_instruction_delta"],
            "interpretation": (
                "wire-proximate physical grouping and leaf-order relabeling "
                "have already failed to delete a complete B3 operation class"
            ),
        },
        "decision": "close-structured-current-tensor-basis-repack-space",
        "assembly_emitted": False,
        "benchmark_run": False,
        "claim_boundary": {
            "closed": [
                "same GT leaves plus current K2/TMVP tensor plus a rank-four sign-normalized ternary degree basis",
                "Q24 D01 mixed TMVP that repairs the representation inside B3",
                "monomial leaf-order/P-like variants that only relabel lambda or move shuffles",
            ],
            "not_closed": [
                "arbitrary GL(4,q) bases",
                "a genuinely different bilinear multiplication tensor/decomposition",
                "a different leaf degree or Good-Thomas factorization",
                "producer-native redundant forms that delete a complete consumer operation",
            ],
        },
        "reopen_only_if": [
            "a new bilinear tensor deletes a vector multiply or complete REDC/recombination class",
            "a producer emits the new tensor operands without a separate basis transform",
            "the consumer remains nonmonomial through a later protocol boundary and avoids wire repair",
            "the transform factorization or quartic leaf algebra itself changes",
        ],
        "next_research_unit": (
            "search a new quartic bilinear tensor with explicit AVX2 lowering "
            "and full Encap graph credit, or move to I1 transform/leaf redesign"
        ),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "rank_four_bases": rank_four,
        "K2_eligible_bases": k2_eligible,
        "best_current": best_total,
        "best_nonmonomial": best_nonmonomial,
        "decision": report["decision"],
    }, indent=2))


if __name__ == "__main__":
    main()
