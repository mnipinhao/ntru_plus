#!/usr/bin/env python3
"""Structural first-cut certificate for the degree-8 multiplication tensor."""

from __future__ import annotations

import hashlib
import json
from itertools import combinations
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
EXPERIMENTS = EXPERIMENT.parent
ALGEBRA = EXPERIMENTS / "gt32_degree8_incomplete_ntt_018"
STREAM = EXPERIMENTS / "gt32_streamed_lhs_rhs_evaluation_020"
Q = 3457


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def artifact(path: Path) -> dict[str, str]:
    return {"path": str(path.resolve()), "sha256": sha256(path)}


def rank(matrix: list[list[int]]) -> int:
    if not matrix:
        return 0
    work = [[value % Q for value in row] for row in matrix]
    rows, cols = len(work), len(work[0])
    pivot_row = 0
    for col in range(cols):
        pivot = next((row for row in range(pivot_row, rows)
                      if work[row][col]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = pow(work[pivot_row][col], -1, Q)
        work[pivot_row] = [value * scale % Q for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or work[row][col] == 0:
                continue
            scale = work[row][col]
            work[row] = [(left - scale * right) % Q
                         for left, right in zip(work[row], work[pivot_row])]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def poly_mul(left: list[int], right: list[int]) -> list[int]:
    out = [0] * (len(left) + len(right) - 1)
    for i, left_value in enumerate(left):
        for j, right_value in enumerate(right):
            out[i + j] = (out[i + j] + left_value * right_value) % Q
    return out


def input_forms(roots: list[int]) -> tuple[list[str], list[list[int]]]:
    names: list[str] = []
    rows: list[list[int]] = []
    for root_index, root in enumerate(roots):
        even = [pow(root, coefficient // 2, Q)
                if coefficient % 2 == 0 else 0 for coefficient in range(8)]
        odd = [pow(root, coefficient // 2, Q)
               if coefficient % 2 == 1 else 0 for coefficient in range(8)]
        names.extend([f"r{root_index}:E", f"r{root_index}:O",
                      f"r{root_index}:E+O"])
        rows.extend([even, odd,
                     [(left + right) % Q for left, right in zip(even, odd)]])
    return names, rows


def invert_matrix(matrix: list[list[int]]) -> list[list[int]]:
    size = len(matrix)
    work = [[value % Q for value in row] +
            [1 if row_index == col else 0 for col in range(size)]
            for row_index, row in enumerate(matrix)]
    for col in range(size):
        pivot = next(row for row in range(col, size) if work[row][col])
        work[col], work[pivot] = work[pivot], work[col]
        scale = pow(work[col][col], -1, Q)
        work[col] = [value * scale % Q for value in work[col]]
        for row in range(size):
            if row == col or work[row][col] == 0:
                continue
            scale = work[row][col]
            work[row] = [(left - scale * right) % Q
                         for left, right in zip(work[row], work[col])]
    return [row[size:] for row in work]


def output_matrix(roots: list[int]) -> list[list[int]]:
    vandermonde = [[pow(root, degree, Q) for degree in range(4)]
                   for root in roots]
    interpolation = invert_matrix(vandermonde)
    matrix = [[0] * 12 for _ in range(8)]
    for root_index, root in enumerate(roots):
        for degree in range(4):
            weight = interpolation[degree][root_index]
            matrix[2 * degree][3 * root_index] = weight
            matrix[2 * degree][3 * root_index + 1] = weight * root % Q
            matrix[2 * degree + 1][3 * root_index] = -weight % Q
            matrix[2 * degree + 1][3 * root_index + 1] = -weight % Q
            matrix[2 * degree + 1][3 * root_index + 2] = weight
    return matrix


def proportional(left: list[int], right: list[int]) -> bool:
    pivot = next((index for index, value in enumerate(left) if value % Q), None)
    if pivot is None:
        return all(value % Q == 0 for value in right)
    if right[pivot] % Q == 0:
        return False
    scale = right[pivot] * pow(left[pivot], -1, Q) % Q
    return all((scale * a - b) % Q == 0 for a, b in zip(left, right))


def crt_certificate(record: dict) -> dict:
    roots = record["quadratic_roots"]
    assert len(set(roots)) == 4
    assert all(pow(root, (Q - 1) // 2, Q) == Q - 1 for root in roots)
    product = [1]
    for root in roots:
        product = poly_mul(product, [-root % Q, 1])
    assert product == [-record["mu"] % Q, 0, 0, 0, 1]
    # In F_q[z]/(z^2-r), multiplication by u+v*z has matrix
    # [[u,r*v],[v,u]] and determinant u^2-r*v^2.  A nonsquare r
    # makes the determinant nonzero for every nonzero (u,v).
    return {
        "k3": record["k3"],
        "branch": record["branch"],
        "low_Q": record["low_Q"],
        "roots_distinct": True,
        "roots_nonsquare": True,
        "factor_product": product,
        "target_x8_polynomial_in_z": [-record["mu"] % Q, 0, 0, 0, 1],
        "quadratic_component_nonzero_multiplication_rank": 2,
    }


def build() -> dict:
    algebra_path = ALGEBRA / "generated/degree8_incomplete_ntt_gate.json"
    stream_path = STREAM / "generated/streamed_contraction_gate.json"
    algebra = json.loads(algebra_path.read_text())
    stream = json.loads(stream_path.read_text())
    records = algebra["exact_algebra"]["records"]
    assert len(records) == 96
    assert stream["input_streaming_pebble_gate"]\
        ["optimistic_all_order_DP_peak_YMM"] == 17

    certificates = [crt_certificate(record) for record in records]
    possible_ranks = [0, 2, 4, 6, 8]

    representative = records[0]
    names, forms = input_forms(representative["quadratic_roots"])
    matrix = output_matrix(representative["quadratic_roots"])
    assert rank(forms) == 8 and rank(matrix) == 8

    single_removal_ranks = []
    for term in range(12):
        remaining = [row for index, row in enumerate(forms) if index != term]
        single_removal_ranks.append(rank(remaining))
    assert set(single_removal_ranks) == {8}

    pair_census = []
    rank_drop_pairs = []
    for left, right in combinations(range(12), 2):
        remaining = [row for index, row in enumerate(forms)
                     if index not in (left, right)]
        remaining_rank = rank(remaining)
        columns = ([row[left] for row in matrix],
                   [row[right] for row in matrix])
        record = {
            "terms": [left, right],
            "names": [names[left], names[right]],
            "same_quadratic_component": left // 3 == right // 3,
            "remaining_input_rank": remaining_rank,
            "output_columns_proportional": proportional(*columns),
        }
        pair_census.append(record)
        if remaining_rank == 7:
            rank_drop_pairs.append(record)
    assert len(pair_census) == 66
    assert len(rank_drop_pairs) == 12
    assert all(item["same_quadratic_component"] for item in rank_drop_pairs)
    assert not any(item["output_columns_proportional"] for item in rank_drop_pairs)

    return {
        "schema": "ntruplus768-gt32-degree8-first-cut-impossibility-021-v1",
        "experiment": "GT32-DEG8-FIRST-CUT-IMPOSSIBILITY-021",
        "production_modified": False,
        "assembly_emitted": False,
        "evidence": [artifact(algebra_path), artifact(stream_path)],
        "crt_algebra_certificate": {
            "leaf_instances": len(certificates),
            "algebra": "product of four irreducible quadratic fields",
            "component_degree": 2,
            "component_multiplication_matrix": "[[u,r*v],[v,u]]",
            "component_determinant": "u^2-r*v^2",
            "nonzero_component_is_invertible_reason":
                "r is nonsquare, so u^2=r*v^2 has no nonzero solution",
            "possible_whole_multiplication_map_ranks": possible_ranks,
            "minimum_nonzero_multiplication_map_rank": 2,
            "certificates": certificates,
        },
        "arbitrary_rank1_decomposition_theorem": {
            "decomposition": "T=sum_j ell_j tensor r_j tensor w_j",
            "applies_to_number_of_terms": "arbitrary, including rank 12",
            "left_forms_span_full_dual_dimension": 8,
            "right_forms_span_full_dual_dimension": 8,
            "proof_steps": [
                "if all left forms annihilate nonzero a then M_a=0, contradicting minimum rank 2",
                "if removing ell_j lowers span, choose nonzero a annihilated by every other ell_i",
                "then M_a(b)=ell_j(a)*r_j(b)*w_j has linear rank at most 1",
                "minimum nonzero multiplication-map rank is 2, a contradiction",
                "the same argument applies to every right form",
            ],
            "conclusion": (
                "removing any single rank-1 term leaves both LHS and RHS form spans at rank 8"
            ),
            "single_term_stream_first_cut_YMM": 17,
            "first_cut_formula": "8 LHS + 8 RHS + 1 product/accumulator",
        },
        "current_rank12_cross_check": {
            "term_names": names,
            "single_removal_ranks": single_removal_ranks,
            "all_single_removals_rank_8": True,
        },
        "two_term_bridge_to_022": {
            "pair_count": len(pair_census),
            "rank_drop_pair_count": len(rank_drop_pairs),
            "rank_drop_pairs": rank_drop_pairs,
            "all_rank_drop_pairs_within_one_quadratic_component": True,
            "rank_after_atomic_pair_removal_per_operand": 7,
            "source_live_after_atomic_pair_removal_both_operands": 14,
            "rank_drop_pair_output_columns_proportional": False,
            "warning": (
                "the current Karatsuba terms cannot simply be summed into one scalar accumulator; "
                "their output recombination columns are not proportional"
            ),
            "next_question": (
                "whether pair-native schoolbook or lane-separated vpmaddwd can consume rank-2 "
                "work atomically while preserving both required output coordinates"
            ),
            "full_pair_census": pair_census,
        },
        "decision": {
            "status": "structural_proof_pass_single_rank1_streaming_impossible",
            "emit_ASM": False,
            "scope_closed": [
                "arbitrary rank-1 bilinear decompositions consumed one term at a time",
                "brute-force search for a rank-12 formula with a single-term 8-to-7 rank drop",
                "allocator or scheduling fixes for the 17-YMM first cut",
            ],
            "not_closed": [
                "atomic consumption of two or more bilinear terms",
                "rank-2 AVX2 hardware contractions such as vpmaddwd",
                "pair-native i32 accumulation and its reduction contract",
                "wider-register ISAs",
            ],
            "next_priority": "GT32-QBM-PAIR-MADDWD-022 generator-only algebra/range/resource gate",
        },
    }


def main() -> None:
    output = EXPERIMENT / "generated/first_cut_impossibility.json"
    output.write_text(json.dumps(build(), indent=2, sort_keys=True) + "\n")
    print(output)


if __name__ == "__main__":
    main()
