#!/usr/bin/env python3
"""Bounded arithmetic-circuit gate for the qualified N5 wide frontend.

The physical ABI, packet traversal and scratch seam are frozen.  This gate
asks whether the per-branch map

    diag(t0,t1,t2) -> DFT3

can use fewer than the current four Montgomery chains, or retain four chains
while removing the twist->omega true multiply dependency.  The one-layer
search permits common signed add/sub wiring and lane-varying fixed constants.
"""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations, product
import json
from pathlib import Path

import generate_tile4 as gt


ROOT = Path(__file__).resolve().parent.parent
ASM = ROOT / "src" / "tile4_asm.S"
OUT = ROOT / "generated" / "tile4_n5_frontend_linear_circuit_gate.json"


def field_rank(rows: list[list[int]] | list[tuple[int, ...]]) -> int:
    work = [[value % gt.Q for value in row] for row in rows]
    rank = 0
    width = len(work[0]) if work else 0
    for column in range(width):
        pivot = next((index for index in range(rank, len(work))
                      if work[index][column]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        inverse = pow(work[rank][column], -1, gt.Q)
        work[rank] = [(value * inverse) % gt.Q
                      for value in work[rank]]
        for index in range(rank + 1, len(work)):
            factor = work[index][column]
            if factor:
                work[index] = [
                    (left - factor * right) % gt.Q
                    for left, right in zip(work[index], work[rank])
                ]
        rank += 1
        if rank == width:
            break
    return rank


def independent_basis(rows: list[list[int]]) -> list[list[int]]:
    basis: list[list[int]] = []
    for row in rows:
        if field_rank(basis + [row]) > len(basis):
            basis.append(row)
    return basis


def canonical_projective(vector: tuple[int, ...]) -> tuple[int, ...] | None:
    for value in vector:
        if value % gt.Q:
            inverse = pow(value % gt.Q, -1, gt.Q)
            return tuple((entry * inverse) % gt.Q for entry in vector)
    return None


def signed_vectors() -> list[tuple[int, int, int]]:
    result = []
    for vector in product((-1, 0, 1), repeat=3):
        if vector == (0, 0, 0):
            continue
        # Quotient the simultaneous sign change of the outer product.
        if next(value for value in vector if value) < 0:
            continue
        result.append(vector)
    return result


def signed_rank_one_matrices():
    vectors = signed_vectors()
    seen = set()
    result = []
    for output_fanout in vectors:
        for input_form in vectors:
            matrix = tuple(
                (output_fanout[row] * input_form[column]) % gt.Q
                for row in range(3) for column in range(3)
            )
            if matrix in seen:
                continue
            seen.add(matrix)
            result.append({
                "matrix": matrix,
                "output_fanout": output_fanout,
                "input_form": input_form,
            })
    return result


def main() -> None:
    asm = ASM.read_text()
    frontend = asm[asm.index(".macro FRONTEND_WIDE_ITER_BODY"):
                   asm.index(".macro FRONTEND_WIDE_E1_ITER_BODY")]
    assert frontend.count("GT_BLEND3") == 2
    assert frontend.count("MONT_WIDE3") == 2
    assert frontend.count("DFT3_WIDE_STORE") == 2
    assert frontend.count("vpmullw .Ltile4_frontend_zeta_top_raw") == 3

    inverse_r = pow(gt.R, -1, gt.Q)
    omega = (-886 * inverse_r) % gt.Q
    assert pow(omega, 3, gt.Q) == 1 and omega != 1
    assert (1 + omega + omega * omega) % gt.Q == 0
    dft = [
        [1, 1, 1],
        [1, omega, omega * omega % gt.Q],
        [1, omega * omega % gt.Q, omega],
    ]
    columns = [[dft[row][column] for row in range(3)]
               for column in range(3)]
    target_subspace = []
    for column, values in enumerate(columns):
        target_subspace.append([
            values[row] if index == column else 0
            for row in range(3) for index in range(3)
        ])
    assert field_rank(target_subspace) == 3

    matrix_records = []
    all_target_matrices = {0: [], 1: []}
    for branch, scale in enumerate(gt.BRANCH_SCALE):
        for q_index in range(32):
            twists = [
                pow(scale, -((64 * n3 + 33 * q_index) % 96), gt.Q)
                for n3 in range(3)
            ]
            matrix = [
                dft[row][column] * twists[column] % gt.Q
                for row in range(3) for column in range(3)
            ]
            all_target_matrices[branch].append(matrix)
            matrix_records.append({
                "branch": branch,
                "Q": q_index,
                "twist_ordinary": [gt.centered(value) for value in twists],
                "matrix_row_major": [gt.centered(value) for value in matrix],
            })
        assert field_rank(all_target_matrices[branch]) == 3

    # Verify both known circuits exactly as field-valued linear maps.
    for record in matrix_records:
        t0, t1, t2 = [value % gt.Q
                      for value in record["twist_ordinary"]]
        current = [
            t0, t1, t2,
            t0, omega * t1 % gt.Q, omega * omega * t2 % gt.Q,
            t0, omega * omega * t1 % gt.Q, omega * t2 % gt.Q,
        ]
        expected = [value % gt.Q for value in record["matrix_row_major"]]
        assert current == expected

        # Five independent first-layer products:
        # A=t0*x0, P=t1*x1, PW=omega*t1*x1,
        # Q=t2*x2, QW=omega*t2*x2.  omega^2*x=-x-omega*x.
        five_chain = [
            t0, t1, t2,
            t0, omega * t1 % gt.Q,
            (-t2 - omega * t2) % gt.Q,
            t0, (-t1 - omega * t1) % gt.Q, omega * t2 % gt.Q,
        ]
        assert five_chain == expected

    # A one-layer circuit has M_Q = C + sum_i c_i(Q) * a_i*b_i^T.
    # C is common signed free wiring; a_i and b_i are signed post/pre-add
    # vectors.  Enumerate all C and all unique signed rank-one directions.
    rank_one = signed_rank_one_matrices()
    assert len(rank_one) == 169

    def quotient(matrix: tuple[int, ...]) -> tuple[int, ...]:
        # Eliminate the first row of each column using its target DFT column.
        residual = []
        for column, values in enumerate(columns):
            coefficient = matrix[column] % gt.Q
            residual.extend((
                (matrix[3 + column] - coefficient * values[1]) % gt.Q,
                (matrix[6 + column] - coefficient * values[2]) % gt.Q,
            ))
        return tuple(residual)

    rank_one_by_quotient = defaultdict(list)
    for item in rank_one:
        signature = canonical_projective(quotient(item["matrix"]))
        rank_one_by_quotient[signature].append(item)

    affine_rank_histogram = defaultdict(int)
    rank4_exact_spans = 0
    rank3_free_matrices = []
    for free_values in product((-1, 0, 1), repeat=9):
        free_matrix = tuple(value % gt.Q for value in free_values)
        dimension = field_rank(target_subspace + [free_matrix])
        affine_rank_histogram[dimension] += 1
        if dimension == 3:
            rank3_free_matrices.append(free_values)
            continue
        assert dimension == 4
        signature = canonical_projective(quotient(free_matrix))
        candidates = (rank_one_by_quotient[None]
                      + rank_one_by_quotient.get(signature, []))
        if field_rank([item["matrix"] for item in candidates]) == 4:
            rank4_exact_spans += 1

    assert affine_rank_histogram == {3: 3, 4: 19680}
    assert rank4_exact_spans == 0
    assert rank3_free_matrices == [
        (-1, 0, 0, -1, 0, 0, -1, 0, 0),
        (0, 0, 0, 0, 0, 0, 0, 0, 0),
        (1, 0, 0, 1, 0, 0, 1, 0, 0),
    ]

    # For the three C already inside the target subspace, allow the four
    # signed rank-one gates to span a one-dimension-larger superspace.  All
    # selected gates must have one common projective quotient.  Exhaust every
    # subset of at most four gates in those small quotient classes.
    rank3_superspace_solutions = 0
    for signature, group in rank_one_by_quotient.items():
        candidates = rank_one_by_quotient[None] if signature is None else (
            rank_one_by_quotient[None] + group)
        for count in range(1, min(4, len(candidates)) + 1):
            for chosen in combinations(candidates, count):
                matrices = [item["matrix"] for item in chosen]
                gate_rank = field_rank(matrices)
                if gate_rank == field_rank(matrices + target_subspace):
                    rank3_superspace_solutions += 1
    assert rank3_superspace_solutions == 0

    # Exact representative-range comparison for the current four-chain DAG
    # and the constructive five-chain depth-one DAG.  The top split inputs are
    # independent small coefficients and therefore each contribution can be
    # bounded by its exact finite value set.
    small = range(-3, 5)
    top_sets = {
        0: sorted({low - 722 * high for low in small for high in small}),
        1: sorted({low + 723 * high for low in small for high in small}),
    }
    current_max = 0
    depth1_max = 0
    current_intermediate_max = 0
    depth1_intermediate_max = 0
    for branch, scale in enumerate(gt.BRANCH_SCALE):
        values = top_sets[branch]
        for q_index in range(32):
            twists_mont = [gt.centered(
                pow(scale, -((64 * n3 + 33 * q_index) % 96), gt.Q) * gt.R)
                for n3 in range(3)
            ]
            a_values = [gt.montgomery_fixed(value, twists_mont[0])
                        for value in values]
            p_values = [gt.montgomery_fixed(value, twists_mont[1])
                        for value in values]
            q_values = [gt.montgomery_fixed(value, twists_mont[2])
                        for value in values]
            pw_values = [gt.montgomery_fixed(
                value, gt.centered(twists_mont[1] * omega))
                for value in values]
            qw_values = [gt.montgomery_fixed(
                value, gt.centered(twists_mont[2] * omega))
                for value in values]

            current_max = max(current_max,
                              abs(min(a_values) + min(p_values) + min(q_values)),
                              abs(max(a_values) + max(p_values) + max(q_values)))
            for p_value in p_values:
                for q_value in q_values:
                    difference = p_value - q_value
                    current_intermediate_max = max(
                        current_intermediate_max, abs(difference))
                    omega_value = gt.montgomery_fixed(difference, -886)
                    current_max = max(
                        current_max,
                        max(abs(a - q_value + omega_value)
                            for a in (min(a_values), max(a_values))),
                        max(abs(a - p_value - omega_value)
                            for a in (min(a_values), max(a_values))),
                    )

            p_pairs = list(zip(p_values, pw_values))
            q_pairs = list(zip(q_values, qw_values))
            p_omega2 = [-p - pw for p, pw in p_pairs]
            q_omega2 = [-qv - qw for qv, qw in q_pairs]
            depth1_intermediate_max = max(
                depth1_intermediate_max,
                *(abs(value) for value in p_omega2),
                *(abs(value) for value in q_omega2),
            )
            depth1_max = max(
                depth1_max,
                abs(min(a_values) + min(p_values) + min(q_values)),
                abs(max(a_values) + max(p_values) + max(q_values)),
                abs(min(a_values) + min(pw_values) + min(q_omega2)),
                abs(max(a_values) + max(pw_values) + max(q_omega2)),
                abs(min(a_values) + min(p_omega2) + min(qw_values)),
                abs(max(a_values) + max(p_omega2) + max(qw_values)),
            )
    assert current_max < 32768 and depth1_max < 32768

    current = {
        "Montgomery_chains_per_branch": 4,
        "Montgomery_chains_per_packet": 8,
        "Montgomery_chains_per_Forward": 64,
        "raw_top_multiplies_per_packet": 3,
        "add_sub_per_branch_after_twist": 7,
        "true_multiply_depth": 2,
        "dependency": "twist -> (P-Q) -> omega3 Montgomery",
    }
    depth1 = {
        "Montgomery_chains_per_branch": 5,
        "Montgomery_chains_per_packet": 10,
        "Montgomery_chains_per_Forward": 80,
        "delta_chains_per_Forward": 16,
        "four_instruction_Montgomery_floor_delta": 64,
        "add_sub_per_branch": 8,
        "true_multiply_depth": 1,
        "construction": [
            "A=Mont(t0*x0)", "P=Mont(t1*x1)",
            "PW=Mont(omega*t1*x1)", "Q=Mont(t2*x2)",
            "QW=Mont(omega*t2*x2)",
            "omega^2*P=-P-PW", "omega^2*Q=-Q-QW",
        ],
    }

    result = {
        "schema": "ntruplus768-gt32-n5-frontend-linear-circuit-v1",
        "experiment": "N5-FRONTEND-LINEAR-CIRCUIT-001",
        "scope": {
            "frozen": [
                "six logical inputs and outputs", "packet-major ABI",
                "DFT3 scratch boundary", "M NTT32 S1-S5 core",
                "Good routing and physical layout",
            ],
            "searched": [
                "fixed-constant placement", "common signed subexpressions",
                "twist/DFT3 factorization", "multiply dependency depth",
            ],
        },
        "source_audit": {
            "GT_BLEND3_calls_per_packet": 2,
            "MONT_WIDE3_calls_per_packet": 2,
            "DFT3_WIDE_STORE_calls_per_packet": 2,
            "raw_top_multiplies_per_packet": 3,
            "frontend_YMM_peak": 16,
        },
        "field": {
            "q": gt.Q,
            "omega3_ordinary": gt.centered(omega),
            "omega3_order": 3,
            "identity": "1+omega+omega^2=0",
        },
        "exact_target_matrices": matrix_records,
        "current_circuit": current,
        "one_layer_exact_search": {
            "model": "M_Q=C+sum c_i(Q)*(signed-output-fanout outer signed-input-form)",
            "free_signed_matrices_enumerated": 3 ** 9,
            "unique_signed_rank_one_directions": len(rank_one),
            "target_family_dimension": 3,
            "affine_family_rank_histogram": {
                str(key): value for key, value in sorted(
                    affine_rank_histogram.items())
            },
            "rank4_exact_span_solutions": rank4_exact_spans,
            "rank3_to_rank4_superspace_solutions": rank3_superspace_solutions,
            "circuits_with_at_most_four_multipliers": 0,
            "minimum_multipliers": 5,
            "constructive_five_multiplier_circuit": depth1,
            "exact_all_branch_Q_matrix_check": "pass",
        },
        "representative_range": {
            "small_input_contract": [-3, 4],
            "top_split_value_ranges": {
                "branch0": [min(top_sets[0]), max(top_sets[0])],
                "branch1": [min(top_sets[1]), max(top_sets[1])],
            },
            "current_max_abs_intermediate": current_intermediate_max,
            "current_max_abs_output": current_max,
            "depth1_five_chain_max_abs_intermediate": depth1_intermediate_max,
            "depth1_five_chain_max_abs_output": depth1_max,
            "all_signed_i16_safe": True,
        },
        "gate": {
            "continue_if": [
                "fewer than eight Montgomery chains per packet",
                "or eight chains with shorter true multiply depth",
            ],
            "result": "fail",
            "reason": (
                "the current depth-two circuit uses eight chains per packet; "
                "every exact one-layer signed-wiring circuit needs at least "
                "ten, so table-folding omega into the twist increases work"
            ),
        },
        "assembly_emitted": False,
        "benchmark_run": False,
        "decision": "static-hard-stop-current-four-chain-per-branch-factorization-wins-bounded-search",
        "architecture_conclusion": {
            "DFT3_scratch": "necessary scheduling resource, not active debt",
            "seam_reopen_frontend_working_YMM_max": 10,
            "frontend_arithmetic": "freeze after this bounded linear-circuit gate",
        },
        "reopen_only_if": [
            "a scaled-output consumer absorbs a changed DFT3 ABI and deletes a complete chain",
            "a fixed-multiply primitive forms two required multiples for less than two chains",
            "a changed decomposition creates whole-vector identity or signed-related twist constants",
            "frontend waiting workset falls to at most ten YMM",
            "target ISA or microarchitecture changes",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT)
    print(json.dumps({
        "decision": result["decision"],
        "current_chains_per_packet": 8,
        "minimum_depth1_chains_per_packet": 10,
        "assembly_emitted": False,
    }, indent=2))


if __name__ == "__main__":
    main()
