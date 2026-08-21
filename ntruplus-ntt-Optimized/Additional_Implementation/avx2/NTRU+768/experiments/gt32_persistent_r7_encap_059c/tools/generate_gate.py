#!/usr/bin/env python3
"""Exact late-recombination gate for a persistent symmetric R7 Encap ABI."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


Q = 3457
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PRIOR = REPO / "experiments/avx2_gt32_tile4_official_001"
SOURCE059B = REPO / "experiments/gt32_quartic_tensor_lowering_059b/generated/quartic_tensor_lowering_059b.json"
LAMBDA_INC = PRIOR / "generated/tile4_basemul_constants.inc"
OUT = ROOT / "generated/persistent_r7_encap_059c.json"
POINTS = [0, 1, -1, 2, -2, 4, -4]


def inv(value: int) -> int:
    return pow(value % Q, Q - 2, Q)


def balanced(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def matmul(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    return [[sum(x * y for x, y in zip(row, column)) % Q
             for column in zip(*b)] for row in a]


def matvec(a: list[list[int]], x: list[int]) -> list[int]:
    return [sum(left * right for left, right in zip(row, x)) % Q
            for row in a]


def invert_square(matrix: list[list[int]]) -> list[list[int]]:
    n = len(matrix)
    work = [[value % Q for value in row]
            + [int(i == j) for j in range(n)]
            for i, row in enumerate(matrix)]
    for column in range(n):
        pivot = next(row for row in range(column, n)
                     if work[row][column])
        work[column], work[pivot] = work[pivot], work[column]
        scale = inv(work[column][column])
        work[column] = [(value * scale) % Q for value in work[column]]
        for row in range(n):
            if row == column:
                continue
            scale = work[row][column]
            work[row] = [(value - scale * pivot_value) % Q
                         for value, pivot_value
                         in zip(work[row], work[column])]
    return [row[n:] for row in work]


def parse_lambdas() -> list[int]:
    text = LAMBDA_INC.read_text().split(".Ltile4_bm_lambda:", 1)[1] \
        .split(".Ltile4_bm_lambda_qinv:", 1)[0]
    values = [int(token) % Q
              for line in text.splitlines() if ".short" in line
              for token in re.findall(r"[-+]?\d+", line.split(".short", 1)[1])]
    assert len(values) == 192
    return values


def coefficient_stats(matrix: list[list[int]]) -> dict:
    supports = [sum(value % Q != 0 for value in row) for row in matrix]
    values = [balanced(value) for row in matrix for value in row]
    return {
        "supports": supports,
        "nonzero": sum(value != 0 for value in values),
        "unit": sum(abs(value) == 1 for value in values),
        "general_constant": sum(value != 0 and abs(value) != 1
                                for value in values),
        "add_lower_bound": sum(max(0, support - 1) for support in supports),
        "max_balanced_abs": max(abs(value) for value in values),
    }


def main() -> None:
    lambdas = parse_lambdas()
    # E maps four quartic coefficients to the seven symmetric evaluations.
    e = [[pow(point % Q, degree, Q) for degree in range(4)]
         for point in POINTS]
    d = [[pow(point % Q, degree, Q) for degree in range(7)]
         for point in POINTS]
    d_inv = invert_square(d)

    # Unnormalised late representation:
    # [P0,S1,D1,S2,D2,S4,D4].  Divisions by 2t are deferred into K_lambda.
    h = [[1, 0, 0, 0, 0, 0, 0]]
    for plus, minus in ((1, 2), (3, 4), (5, 6)):
        sum_row = [0] * 7
        diff_row = [0] * 7
        sum_row[plus] = sum_row[minus] = 1
        diff_row[plus] = 1
        diff_row[minus] = Q - 1
        h.extend((sum_row, diff_row))
    h_inv = invert_square(h)

    w_by_lambda = []
    k_by_lambda = []
    checks = 0
    for lam in lambdas:
        reduction = [[1, 0, 0, 0, lam, 0, 0],
                     [0, 1, 0, 0, 0, lam, 0],
                     [0, 0, 1, 0, 0, 0, lam],
                     [0, 0, 0, 1, 0, 0, 0]]
        w = matmul(reduction, d_inv)
        k = matmul(w, h_inv)
        assert matmul(k, h) == w
        w_by_lambda.append(w)
        k_by_lambda.append(k)

        # Product contribution: B3 leaves seven pointwise products live.
        for ai in range(4):
            for bi in range(4):
                a = [int(index == ai) for index in range(4)]
                b = [int(index == bi) for index in range(4)]
                eval_a = matvec(e, a)
                eval_b = matvec(e, b)
                products = [x * y % Q for x, y in zip(eval_a, eval_b)]
                late = matvec(h, products)
                got = matvec(k, late)
                expected = [0, 0, 0, 0]
                degree = ai + bi
                expected[degree if degree < 4 else degree - 4] = \
                    1 if degree < 4 else lam
                assert got == expected
                checks += 1

        # Message contribution: H*E(m) can be added to H*product before K.
        for mi in range(4):
            m = [int(index == mi) for index in range(4)]
            late_m = matvec(h, matvec(e, m))
            got = matvec(k, late_m)
            assert got == m
            checks += 1

    assert checks == 192 * 20

    k_stats = [coefficient_stats(k) for k in k_by_lambda]
    source_supports = [sum(value % Q != 0 for value in row) for row in e]
    # Shared evaluation DAG per 16 leaves:
    # t=1,2,4 each forms even=a0+t^2*a2 and odd=t*a1+t^3*a3,
    # followed by even+/-odd.  Six shifts cover t=2/4 powers.
    producer_dag = {
        "source_planes": 4,
        "output_evaluation_planes": 7,
        "t_values": [1, 2, 4],
        "vector_add_sub": 12,
        "power_of_two_vector_shifts": 6,
        "general_constant_Montgomery": 0,
        "blocks_per_polynomial": 12,
        "instructions_per_polynomial_lowering_proxy": 216,
        "note": "Forward-native formation may absorb part of this DAG; no credit is assumed here",
    }
    report = {
        "schema": "ntruplus768-gt32-persistent-r7-encap-059c-v1",
        "experiment": "GT32-PERSISTENT-R7-LATE-RECOMBINATION-059C",
        "status": "research-continue",
        "production_modified": False,
        "source_hashes": {
            SOURCE059B.name: hashlib.sha256(SOURCE059B.read_bytes()).hexdigest(),
            LAMBDA_INC.name: hashlib.sha256(LAMBDA_INC.read_bytes()).hexdigest(),
        },
        "abi": {
            "input_operands": "raw E7 evaluations P(0),P(+/-1),P(+/-2),P(+/-4)",
            "terminal_product": "unnormalised P0,S1,D1,S2,D2,S4,D4",
            "message": "same H*E7 representation",
            "late_exit": "K_lambda followed directly by canonical reduction and Q24 routing",
            "scale_exponent": "must be selected jointly with pointwise Montgomery and late REDC",
        },
        "exactness": {
            "lambda_entries": len(lambdas),
            "product_basis_checks": len(lambdas) * 16,
            "message_basis_checks": len(lambdas) * 4,
            "total": checks,
            "identity": "K_lambda*(H*(E(a)*E(b)) + H*E(m)) = a*b mod (x^4-lambda) + m",
        },
        "producer": {
            "E_matrix_balanced": [[balanced(value) for value in row] for row in e],
            "form_supports": source_supports,
            "shared_AVX2_DAG": producer_dag,
            "representation_words": 7 * 192,
            "representation_bytes": 7 * 192 * 2,
            "current_quartic_bytes": 4 * 192 * 2,
            "expansion_bytes": 3 * 192 * 2,
        },
        "B3_and_add": {
            "pointwise_variable_product_chains_per_16_leaves": 7,
            "current_algebraic_variable_products": 9,
            "product_to_terminal_add_sub_per_16_leaves": 6,
            "message_adds_per_16_leaves": 7,
            "quartic_recombination_inside_B3": 0,
            "quartic_output_materialization": 0,
            "standalone_quartic_poly_add": 0,
            "terminal_planes": 7,
        },
        "late_K_Q24": {
            "K_lambda_nonzero_mean": sum(item["nonzero"] for item in k_stats) / len(k_stats),
            "K_lambda_nonzero_min": min(item["nonzero"] for item in k_stats),
            "K_lambda_nonzero_max": max(item["nonzero"] for item in k_stats),
            "K_lambda_general_constants_mean":
                sum(item["general_constant"] for item in k_stats) / len(k_stats),
            "K_lambda_supports_first_lambda": k_stats[0]["supports"],
            "pair_dot_lower_bound_first_lambda":
                sum((support + 1) // 2 for support in k_stats[0]["supports"]),
            "candidate_lowering": (
                "pair-pack the seven terminal channels and use vpmaddwd/i32 "
                "accumulators so interpolation and canonical reduction share one REDC32 exit"
            ),
            "current_Q24_reducer_absorption": "open and required for executable credit",
        },
        "liveness_and_materialization": {
            "producer_native_E7_persistent_planes": 7,
            "B3_stream_inputs_at_once": 2,
            "pointwise_product_temp": 1,
            "late_terminal_store_planes": 7,
            "estimated_B3_stream_peak_YMM": 11,
            "spill_free_B3_feasible": True,
            "late_K_Q24_peak": "unproved; four i32 accumulators plus pair-packed sources",
            "mandatory_new_materialization": "seven planes unless B3+late-exit streaming is later selected",
        },
        "operation_class_changes": {
            "deleted": [
                "two quartic algebraic variable products",
                "B3-local W_lambda quartic recombination",
                "quartic B3 output materialization",
                "standalone four-plane add(m) pass",
            ],
            "added": [
                "three redundant producer planes",
                "six product sum/difference operations",
                "seven-plane message add",
                "late K_lambda/Q24 dot-product exit",
            ],
        },
        "research_decision": {
            "decision": "continue-to-059C-AVX2-late-exit-lowering",
            "reason": (
                "the exact late-domain identity deletes quartic recombination/materialization "
                "and standalone add as operation classes; producer and late-exit costs remain open"
            ),
            "production_promotion": False,
            "no_cycle_threshold": True,
        },
        "next": [
            "construct pair-packed K_lambda+Q24 REDC32 DAG",
            "prove bounds for pointwise products plus E(m)",
            "prove late-exit peak YMM and spill behavior",
            "test whether Forward terminal can emit E7 with less than the standalone 12-add/6-shift DAG",
        ],
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "exact_checks": checks,
        "K_nonzero_mean": report["late_K_Q24"]["K_lambda_nonzero_mean"],
        "B3_products": 7,
        "representation_bytes": report["producer"]["representation_bytes"],
        "decision": report["research_decision"]["decision"],
    }, indent=2))


if __name__ == "__main__":
    main()
