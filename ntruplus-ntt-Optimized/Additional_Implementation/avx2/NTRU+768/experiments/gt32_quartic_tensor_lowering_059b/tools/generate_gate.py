#!/usr/bin/env python3
"""Compare R7-A, symmetric R7-B, and quadratic-CRT R6 architectures."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path


Q = 3457
INF = "inf"
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PRIOR = REPO / "experiments/avx2_gt32_tile4_official_001"
TENSOR059 = REPO / "experiments/gt32_quartic_tensor_059/generated/quartic_tensor_059.json"
LAMBDA_INC = PRIOR / "generated/tile4_basemul_constants.inc"
OUT = ROOT / "generated/quartic_tensor_lowering_059b.json"


def inv(value: int) -> int:
    return pow(value % Q, Q - 2, Q)


def balanced(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def matmul(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    return [[sum(x * y for x, y in zip(row, column)) % Q
             for column in zip(*b)] for row in a]


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
    assert len(values) == 192 and len(set(values)) == 192
    return values


def sqrt_mod(value: int) -> int:
    """Tonelli-Shanks for the fixed odd prime Q."""
    value %= Q
    assert pow(value, (Q - 1) // 2, Q) == 1
    s = 0
    d = Q - 1
    while d % 2 == 0:
        s += 1
        d //= 2
    z = 2
    while pow(z, (Q - 1) // 2, Q) != Q - 1:
        z += 1
    x = pow(value, (d + 1) // 2, Q)
    t = pow(value, d, Q)
    c = pow(z, d, Q)
    m = s
    while t != 1:
        i = 1
        t2 = t * t % Q
        while t2 != 1:
            t2 = t2 * t2 % Q
            i += 1
        b = pow(c, 1 << (m - i - 1), Q)
        x = x * b % Q
        t = t * b * b % Q
        c = b * b % Q
        m = i
    assert x * x % Q == value
    return min((x, (-x) % Q), key=lambda item: abs(balanced(item)))


def eval_row(point: int | str, degree: int) -> list[int]:
    if point == INF:
        return [0] * (degree - 1) + [1]
    return [pow(point % Q, index, Q) for index in range(degree)]


def reduction_matrix(lam: int) -> list[list[int]]:
    return [[1, 0, 0, 0, lam, 0, 0],
            [0, 1, 0, 0, 0, lam, 0],
            [0, 0, 1, 0, 0, 0, lam],
            [0, 0, 0, 1, 0, 0, 0]]


def coefficient_stats(matrix: list[list[int]]) -> dict:
    values = [balanced(value) for row in matrix for value in row]
    supports = [sum(value % Q != 0 for value in row) for row in matrix]
    return {
        "rows": len(matrix),
        "supports": supports,
        "add_sub_lower_bound": sum(max(0, support - 1)
                                   for support in supports),
        "zero": sum(value == 0 for value in values),
        "unit": sum(abs(value) == 1 for value in values),
        "power_of_two": sum(value and abs(value) & (abs(value) - 1) == 0
                            and abs(value) != 1 for value in values),
        "general_constant": sum(value and abs(value) != 1
                                and abs(value) & (abs(value) - 1) != 0
                                for value in values),
        "max_balanced_abs": max(abs(value) for value in values),
    }


def direct_r7(points: list[int | str], lambdas: list[int]) -> dict:
    u = [eval_row(point, 4) for point in points]
    d = [eval_row(point, 7) for point in points]
    d_inv = invert_square(d)
    weights = [matmul(reduction_matrix(lam), d_inv) for lam in lambdas]
    return {"U": u, "V": u, "W": weights}


def symmetric_factorization(tensor: dict) -> dict:
    # Product order: P(0), P(1), P(-1), P(2), P(-2), P(4), P(-4).
    half = inv(2)
    h = [[1, 0, 0, 0, 0, 0, 0]]
    for plus, minus in ((1, 2), (3, 4), (5, 6)):
        row = [0] * 7
        row[plus] = half
        row[minus] = half
        h.append(row)
    for t, plus, minus in ((1, 1, 2), (2, 3, 4), (4, 5, 6)):
        row = [0] * 7
        row[plus] = inv(2 * t)
        row[minus] = (-inv(2 * t)) % Q
        h.append(row)
    h_inv = invert_square(h)
    k_by_lambda = [matmul(weights, h_inv) for weights in tensor["W"]]
    for weights, k in zip(tensor["W"], k_by_lambda):
        assert matmul(k, h) == weights
    return {"H_product_to_even_odd": h, "K_even_odd_to_output": k_by_lambda}


def r6_tensor(lam: int, mu: int) -> dict:
    plus = mu
    minus = (-mu) % Q
    u = [
        [1, 0, plus, 0], [0, 1, 0, plus], [1, 1, plus, plus],
        [1, 0, minus, 0], [0, 1, 0, minus], [1, 1, minus, minus],
    ]
    inv2 = inv(2)
    inv2mu = inv(2 * mu)
    # Product slots: p0+, p1+, p2+, p0-, p1-, p2-.
    cp0 = [1, mu, 0, 0, 0, 0]
    cp1 = [Q - 1, Q - 1, 1, 0, 0, 0]
    cm0 = [0, 0, 0, 1, (-mu) % Q, 0]
    cm1 = [0, 0, 0, Q - 1, Q - 1, 1]
    w = [
        [inv2 * (a + b) % Q for a, b in zip(cp0, cm0)],
        [inv2 * (a + b) % Q for a, b in zip(cp1, cm1)],
        [inv2mu * (a - b) % Q for a, b in zip(cp0, cm0)],
        [inv2mu * (a - b) % Q for a, b in zip(cp1, cm1)],
    ]
    return {"U": u, "V": u, "W": w, "mu": mu, "lambda": lam}


def verify(U: list[list[int]], V: list[list[int]], W: list[list[int]],
           lam: int) -> int:
    checks = 0
    for i in range(4):
        for j in range(4):
            products = [a[i] * b[j] % Q for a, b in zip(U, V)]
            got = [sum(weight * product for weight, product in zip(row, products)) % Q
                   for row in W]
            expected = [0, 0, 0, 0]
            degree = i + j
            expected[degree if degree < 4 else degree - 4] = \
                1 if degree < 4 else lam
            assert got == expected
            checks += 1
    return checks


def aggregate_w(weights: list[list[list[int]]]) -> dict:
    per_lambda = [coefficient_stats(weight) for weight in weights]
    return {
        "nonzero_mean": sum(4 * len(weights[0][0]) - item["zero"]
                            for item in per_lambda) / len(per_lambda),
        "general_constant_mean": sum(item["general_constant"]
                                     for item in per_lambda) / len(per_lambda),
        "general_constant_min": min(item["general_constant"] for item in per_lambda),
        "general_constant_max": max(item["general_constant"] for item in per_lambda),
        "max_balanced_abs": max(item["max_balanced_abs"] for item in per_lambda),
    }


def main() -> None:
    lambdas = parse_lambdas()
    tensor059 = json.loads(TENSOR059.read_text())
    points_a = tensor059["selected_rank7"]["points"]
    r7a = direct_r7(points_a, lambdas)
    points_b: list[int | str] = [0, 1, -1, 2, -2, 4, -4]
    r7b = direct_r7(points_b, lambdas)
    factored_b = symmetric_factorization(r7b)

    mus = [sqrt_mod(lam) for lam in lambdas]
    assert all(mu * mu % Q == lam for mu, lam in zip(mus, lambdas))
    assert all(pow(lam, (Q - 1) // 4, Q) == Q - 1 for lam in lambdas)
    r6 = [r6_tensor(lam, mu) for lam, mu in zip(lambdas, mus)]

    checks_a = sum(verify(r7a["U"], r7a["V"], w, lam)
                   for w, lam in zip(r7a["W"], lambdas))
    checks_b = sum(verify(r7b["U"], r7b["V"], w, lam)
                   for w, lam in zip(r7b["W"], lambdas))
    checks_6 = sum(verify(tensor["U"], tensor["V"], tensor["W"], lam)
                   for tensor, lam in zip(r6, lambdas))
    assert checks_a == checks_b == checks_6 == 3072

    report = {
        "schema": "ntruplus768-gt32-quartic-tensor-lowering-059b-v1",
        "experiment": "GT32-QUARTIC-TENSOR-LOWERING-059B",
        "status": "research-continue",
        "production_modified": False,
        "source_hashes": {
            TENSOR059.name: hashlib.sha256(TENSOR059.read_bytes()).hexdigest(),
            LAMBDA_INC.name: hashlib.sha256(LAMBDA_INC.read_bytes()).hexdigest(),
        },
        "field_and_leaf_proof": {
            "q": Q,
            "q_minus_1": Q - 1,
            "d2_required_root_order": 1152,
            "1152_divides_q_minus_1": (Q - 1) % 1152 == 0,
            "lambda_entries": len(lambdas),
            "all_lambda_are_squares": True,
            "all_lambda_are_not_fourth_powers": True,
            "factorization": "x^4-lambda=(x^2-mu)(x^2+mu)",
            "mu_unique_balanced_abs_max": max(abs(balanced(mu)) for mu in mus),
        },
        "exactness": {
            "R7_A_basis_products": checks_a,
            "R7_B_basis_products": checks_b,
            "R6_CRT_basis_products": checks_6,
            "expected_each": 3072,
        },
        "architectures": {
            "R7_A": {
                "points": points_a,
                "algebraic_variable_products": 7,
                "producer_form_stats": coefficient_stats(r7a["U"]),
                "direct_W_lambda_stats": aggregate_w(r7a["W"]),
                "producer_native_contract": "seven evaluation planes per operand",
                "consumer_exit": "dense W_lambda returns monomial quartic",
                "liveness": {
                    "on_the_fly_source_planes": 8,
                    "output_accumulators": 4,
                    "estimated_extra_form_product_temps": 4,
                    "on_the_fly_peak_lower_bound": 16,
                    "producer_native_streaming_peak_estimate": 9,
                    "status": "requires explicit schedule; producer-native form is favored",
                },
            },
            "R7_B_symmetric": {
                "points": points_b,
                "algebraic_variable_products": 7,
                "producer_form_stats": coefficient_stats(r7b["U"]),
                "direct_W_lambda_stats": aggregate_w(r7b["W"]),
                "even_odd_product_map_stats":
                    coefficient_stats(factored_b["H_product_to_even_odd"]),
                "even_odd_output_map_stats":
                    aggregate_w(factored_b["K_even_odd_to_output"]),
                "shared_mechanism": (
                    "three P(t)+P(-t) and three P(t)-P(-t) pairs split "
                    "interpolation into even and odd 3x3 systems"
                ),
                "producer_native_contract": "seven symmetric evaluation planes",
                "consumer_exit": "factored even/odd W_lambda returns monomial quartic",
                "liveness": {
                    "pair_products_before_even_odd_combine": 6,
                    "even_odd_channels": 6,
                    "status": "shared pair combine is explicit; AVX2 schedule pending",
                },
            },
            "R6_quadratic_CRT": {
                "algebraic_variable_products": 6,
                "factor_components": ["x^2-mu", "x^2+mu"],
                "current_quartic_boundary": {
                    "split_constant_Montgomery_per_operand": 2,
                    "split_add_sub_per_operand": 6,
                    "two_operands_split_constant_chains": 4,
                    "quadratic_branch_lambda_constant_chains": 2,
                    "quartic_CRT_merge_constant_chains": 4,
                    "quartic_CRT_merge_add_sub": 4,
                    "warning": "this is deliberately not the target architecture",
                },
                "native_d2_B3": {
                    "input_planes_per_operand": 4,
                    "variable_product_chains": 6,
                    "quadratic_mu_constant_chains": 2,
                    "total_B3_Montgomery_chain_classes": 8,
                    "output_add_sub": 6,
                    "quartic_split_inside_B3": 0,
                    "quartic_merge_inside_B3": 0,
                    "peak_YMM_estimate": 15,
                    "spill_free_feasibility": "plausible, not yet executable proof",
                },
                "producer_native_opportunity": [
                    "Q24 Decode(h) directly emits plus/minus quadratic planes",
                    "d2 Forward(r) and d2 Forward(m) terminate in quadratic planes",
                ],
                "consumer_native_opportunity": [
                    "add(m) is direct in the same d2 representation",
                    "Q24 serializer folds the final CRT merge into packet formation",
                ],
                "mu_stats": {
                    "unique": len(set(mus)),
                    "balanced_abs_max": max(abs(balanced(mu)) for mu in mus),
                    "first_eight": [balanced(mu) for mu in mus[:8]],
                },
                "first_lambda_tensor": {
                    "lambda": balanced(lambdas[0]),
                    "mu": balanced(mus[0]),
                    "U_balanced": [[balanced(value) for value in row]
                                   for row in r6[0]["U"]],
                    "W_balanced": [[balanced(value) for value in row]
                                   for row in r6[0]["W"]],
                },
            },
        },
        "pareto": {
            "current": {
                "algebraic_variable_products": 9,
                "selected_physical_Montgomery_chains": 12,
                "producer_native": True,
                "wire_native": "Q24-qualified M boundary",
            },
            "R7_A": {
                "algebraic_variable_products": 7,
                "producer_native_opportunity": True,
                "consumer_native_opportunity": "limited by dense W_lambda",
            },
            "R7_B": {
                "algebraic_variable_products": 7,
                "producer_native_opportunity": True,
                "consumer_native_opportunity": "even/odd factored W",
            },
            "R6_CRT": {
                "algebraic_variable_products": 6,
                "native_d2_B3_chain_classes": 8,
                "producer_native_opportunity": "very large",
                "consumer_native_opportunity": "very large",
            },
        },
        "research_decision": {
            "R7_A": "continue as tensor-lowering control",
            "R7_B": "continue to explicit even/odd AVX2 DAG",
            "R6_CRT": "promote to architecture research candidate 060",
            "production_promotion": False,
            "reason": (
                "all three change an operation class; R6 additionally admits "
                "a native d2 producer/consumer contract and removes split/merge from B3"
            ),
        },
        "unresolved": [
            "exact range and representative schedule for R7 and R6",
            "constant-Montgomery sharing and W_lambda lowering",
            "executable peak-YMM proof",
            "d2 Forward/Inverse transform tables and physical layout",
            "direct d2 Q24 decode/encode mapping and canonical rejection",
            "whole Encap consumer graph cost",
        ],
        "next": {
            "primary": "060 d2 / GT 3x64 quadratic-leaf Encap architecture gate",
            "parallel_control": "059C explicit R7-B even/odd lowering",
            "no_cycle_threshold_at_research_stage": True,
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "exact_checks_each": 3072,
        "R7_A_products": 7,
        "R7_B_products": 7,
        "R6_products": 6,
        "R6_native_d2_chain_classes": 8,
        "decision": report["research_decision"],
    }, indent=2))


if __name__ == "__main__":
    main()
