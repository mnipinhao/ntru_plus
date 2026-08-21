#!/usr/bin/env python3
"""Search exact rank-7/8 evaluation tensors for quartic GT leaves."""

from __future__ import annotations

import hashlib
import itertools
import json
import re
from pathlib import Path


Q = 3457
ROOT = Path(__file__).resolve().parents[1]
REPO = ROOT.parents[1]
PRIOR = REPO / "experiments/avx2_gt32_tile4_official_001"
LAMBDA_INC = PRIOR / "generated/tile4_basemul_constants.inc"
PAIR_GATE = PRIOR / "generated/tile4_pair_native_bm_gate.json"
OUT = ROOT / "generated/quartic_tensor_059.json"
INF = "inf"


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
    work = [
        [value % Q for value in row]
        + [int(i == j) for j in range(n)]
        for i, row in enumerate(matrix)
    ]
    for column in range(n):
        pivot = next(row for row in range(column, n)
                     if work[row][column] % Q)
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


def eval4(point: int | str) -> list[int]:
    if point == INF:
        return [0, 0, 0, 1]
    return [pow(point % Q, degree, Q) for degree in range(4)]


def eval7(point: int | str) -> list[int]:
    if point == INF:
        return [0, 0, 0, 0, 0, 0, 1]
    return [pow(point % Q, degree, Q) for degree in range(7)]


def reduction_matrix(lam: int) -> list[list[int]]:
    # d0..d6 -> (d0+lambda*d4, d1+lambda*d5,
    #             d2+lambda*d6, d3)
    return [
        [1, 0, 0, 0, lam, 0, 0],
        [0, 1, 0, 0, 0, lam, 0],
        [0, 0, 1, 0, 0, 0, lam],
        [0, 0, 0, 1, 0, 0, 0],
    ]


def parse_lambdas() -> list[int]:
    text = LAMBDA_INC.read_text()
    section = text.split(".Ltile4_bm_lambda:", 1)[1] \
                  .split(".Ltile4_bm_lambda_qinv:", 1)[0]
    values = [int(token) % Q
              for line in section.splitlines() if ".short" in line
              for token in re.findall(r"[-+]?\d+", line.split(".short", 1)[1])]
    assert len(values) == 192
    assert all(values)
    return values


def coefficient_class(values: list[int]) -> dict:
    b = [balanced(value) for value in values]
    return {
        "zero": sum(value == 0 for value in b),
        "unit": sum(abs(value) == 1 for value in b),
        "small_shift_add": sum(abs(value) in (2, 3, 4, 8) for value in b),
        "general_constant": sum(value != 0 and abs(value) not in
                                (1, 2, 3, 4, 8) for value in b),
        "max_balanced_abs": max((abs(value) for value in b), default=0),
    }


def input_stats(rows: list[list[int]]) -> dict:
    flat = [value for row in rows for value in row]
    supports = [sum(value % Q != 0 for value in row) for row in rows]
    classes = coefficient_class(flat)
    return {
        "forms": len(rows),
        "form_supports": supports,
        "linear_add_lower_bound": sum(max(0, support - 1)
                                      for support in supports),
        "coefficient_classes": classes,
    }


def output_stats(weights_by_lambda: list[list[list[int]]]) -> dict:
    flat = [value for weights in weights_by_lambda
            for row in weights for value in row]
    classes = coefficient_class(flat)
    per_lambda_general = []
    per_lambda_nonzero = []
    for weights in weights_by_lambda:
        values = [balanced(value) for row in weights for value in row]
        per_lambda_general.append(sum(value != 0 and abs(value) not in
                                      (1, 2, 3, 4, 8)
                                      for value in values))
        per_lambda_nonzero.append(sum(value != 0 for value in values))
    return {
        "coefficient_classes_all_192_lambdas": classes,
        "general_constants_per_lambda_min": min(per_lambda_general),
        "general_constants_per_lambda_max": max(per_lambda_general),
        "general_constants_per_lambda_mean":
            sum(per_lambda_general) / len(per_lambda_general),
        "nonzero_coefficients_per_lambda_min": min(per_lambda_nonzero),
        "nonzero_coefficients_per_lambda_max": max(per_lambda_nonzero),
        "nonzero_coefficients_per_lambda_mean":
            sum(per_lambda_nonzero) / len(per_lambda_nonzero),
    }


def rank7_tensor(points: tuple[int, ...], lambdas: list[int]) -> dict:
    full_points: list[int | str] = [*points, INF]
    e4 = [eval4(point) for point in full_points]
    d = [eval7(point) for point in full_points]
    d_inv = invert_square(d)
    weights = [matmul(reduction_matrix(lam), d_inv) for lam in lambdas]
    return {
        "rank": 7,
        "points": list(points) + [INF],
        "U": e4,
        "V": e4,
        "weights_by_lambda": weights,
        "input": input_stats(e4),
        "output": output_stats(weights),
    }


def null_relation(d: list[list[int]]) -> tuple[list[list[int]], list[int]]:
    # The first seven rows are square.  Reconstruct coefficients from them,
    # then express the eighth evaluation as their linear combination.
    first_inv = invert_square(d[:7])
    reconstruction = [row + [0] for row in first_inv]
    relation_coeff = matmul([d[7]], first_inv)[0]
    null = [(-value) % Q for value in relation_coeff] + [1]
    assert all(sum(null[i] * d[i][j] for i in range(8)) % Q == 0
               for j in range(7))
    return reconstruction, null


def alpha_cost(row: list[int]) -> tuple[int, int, int, int]:
    values = [balanced(value) for value in row]
    general = sum(value != 0 and abs(value) not in (1, 2, 3, 4, 8)
                  for value in values)
    nonzero = sum(value != 0 for value in values)
    magnitude = sum(abs(value) for value in values)
    maximum = max(abs(value) for value in values)
    return general, nonzero, maximum, magnitude


def rank8_tensor(lambdas: list[int]) -> dict:
    # One concrete redundant evaluation family.  The eighth point supplies a
    # one-dimensional interpolation freedom that is optimized independently
    # for each output row and lambda.
    points: list[int | str] = [-3, -2, -1, 0, 1, 2, 3, INF]
    e4 = [eval4(point) for point in points]
    d = [eval7(point) for point in points]
    reconstruction, null = null_relation(d)
    weights_by_lambda: list[list[list[int]]] = []
    alphas_by_lambda: list[list[int]] = []
    for lam in lambdas:
        base = matmul(reduction_matrix(lam), reconstruction)
        chosen_rows = []
        chosen_alphas = []
        for row in base:
            best = min(
                ((alpha_cost([(value + alpha * n) % Q
                              for value, n in zip(row, null)]), alpha)
                 for alpha in range(Q)),
                key=lambda item: (item[0], item[1]),
            )
            alpha = best[1]
            chosen_alphas.append(alpha)
            chosen_rows.append([(value + alpha * n) % Q
                                for value, n in zip(row, null)])
        weights_by_lambda.append(chosen_rows)
        alphas_by_lambda.append(chosen_alphas)
    return {
        "rank": 8,
        "points": points,
        "U": e4,
        "V": e4,
        "weights_by_lambda": weights_by_lambda,
        "interpolation_null_vector": null,
        "selected_alphas_by_lambda": alphas_by_lambda,
        "input": input_stats(e4),
        "output": output_stats(weights_by_lambda),
    }


def verify_tensor(tensor: dict, lambdas: list[int]) -> int:
    checks = 0
    u = tensor["U"]
    v = tensor["V"]
    for lambda_index, lam in enumerate(lambdas):
        weights = tensor["weights_by_lambda"][lambda_index]
        for i in range(4):
            for j in range(4):
                products = [(row_u[i] * row_v[j]) % Q
                            for row_u, row_v in zip(u, v)]
                got = [sum(weight * product
                           for weight, product in zip(row, products)) % Q
                       for row in weights]
                expected = [0, 0, 0, 0]
                degree = i + j
                expected[degree if degree < 4 else degree - 4] = \
                    1 if degree < 4 else lam
                assert got == expected
                checks += 1
    return checks


def proxy_key(tensor: dict) -> tuple:
    output = tensor["output"]
    inp = tensor["input"]
    return (
        output["general_constants_per_lambda_mean"],
        output["nonzero_coefficients_per_lambda_mean"],
        inp["coefficient_classes"]["general_constant"],
        inp["linear_add_lower_bound"],
    )


def producer_scaling_variant(tensor: dict, lambdas: list[int]) -> dict:
    # Search a diagonal row-rescaling equivalence class.  U (Decode/h) stays
    # unchanged; each V (Forward/r) row may be scaled, with the inverse scale
    # folded into the corresponding output-table column.
    scale_set = [1, Q - 1, 2, Q - 2, inv(2), (-inv(2)) % Q]
    selected = []
    scaled_v = []
    for column, row in enumerate(tensor["V"]):
        choices = []
        for scale in scale_set:
            scaled_row = [(scale * value) % Q for value in row]
            inverse_scale = inv(scale)
            output_column = [
                (weights[out][column] * inverse_scale) % Q
                for weights in tensor["weights_by_lambda"]
                for out in range(4)
            ]
            row_classes = input_stats([scaled_row])["coefficient_classes"]
            out_classes = coefficient_class(output_column)
            cost = (row_classes["general_constant"]
                    + out_classes["general_constant"],
                    out_classes["general_constant"],
                    row_classes["general_constant"])
            choices.append((cost, scale, scaled_row))
        choice = min(choices, key=lambda item: (item[0], item[1]))
        selected.append(choice[1])
        scaled_v.append(choice[2])
    scaled_weights = []
    for weights in tensor["weights_by_lambda"]:
        scaled_weights.append([
            [(value * inv(selected[column])) % Q
             for column, value in enumerate(row)]
            for row in weights
        ])
    variant = {
        "description": "U_h unchanged; V_r rows diagonally rescaled",
        "row_scales": selected,
        "U": tensor["U"],
        "V": scaled_v,
        "weights_by_lambda": scaled_weights,
        "input_h": input_stats(tensor["U"]),
        "input_r": input_stats(scaled_v),
        "output": output_stats(scaled_weights),
    }
    assert verify_tensor(variant, lambdas) == len(lambdas) * 16
    return variant


def compact_tensor(tensor: dict) -> dict:
    return {
        "rank": tensor["rank"],
        "points": tensor["points"],
        "input_forms_balanced": [[balanced(value) for value in row]
                                 for row in tensor["U"]],
        "input_cost_proxy": tensor["input"],
        "output_cost_proxy": tensor["output"],
        "first_lambda_output_weights_balanced": [
            [balanced(value) for value in row]
            for row in tensor["weights_by_lambda"][0]
        ],
    }


def main() -> None:
    lambdas = parse_lambdas()
    pair_gate = json.loads(PAIR_GATE.read_text())
    current_variable_rank = len(
        pair_gate["exact_L02_nested_karatsuba"]["variable_scalar_products"])
    current_physical_chains = pair_gate["reduction_chains"] \
        ["LS5_native_L01"]["total"]
    assert current_variable_rank == 9
    assert current_physical_chains == 12
    candidates = []
    for points in itertools.combinations(range(-4, 5), 6):
        candidates.append(rank7_tensor(points, lambdas))
    assert len(candidates) == 84
    selected7 = min(candidates, key=proxy_key)
    rank7_checks = verify_tensor(selected7, lambdas)

    selected8 = rank8_tensor(lambdas)
    rank8_checks = verify_tensor(selected8, lambdas)
    asymmetric = producer_scaling_variant(selected7, lambdas)

    report = {
        "schema": "ntruplus768-gt32-quartic-tensor-redesign-059-v1",
        "experiment": "GT32-QUARTIC-BILINEAR-TENSOR-059",
        "status": "research-continue",
        "production_modified": False,
        "scope": "exact generator search over new quartic evaluation tensors",
        "algebra": "F_3457[x]/(x^4-lambda)",
        "source_hashes": {
            LAMBDA_INC.name: hashlib.sha256(LAMBDA_INC.read_bytes()).hexdigest(),
            PAIR_GATE.name: hashlib.sha256(PAIR_GATE.read_bytes()).hexdigest(),
        },
        "effective_lambda_stream": {
            "entries": len(lambdas),
            "unique": len(set(lambdas)),
            "all_nonzero": all(lambdas),
        },
        "search": {
            "rank7_family": (
                "six distinct finite points selected from -4..4 plus infinity"
            ),
            "rank7_point_sets": len(candidates),
            "rank8_family": (
                "fixed redundant points -3..3 plus infinity; one-dimensional "
                "interpolation freedom exhaustively optimized over F_3457"
            ),
            "rank8_alpha_values_per_output_and_lambda": Q,
            "asymmetric_family": (
                "rank7 diagonal row rescaling with U_h fixed and V_r scales "
                "chosen from +/-1, +/-2, +/-1/2"
            ),
            "selection_proxy_warning": (
                "coefficient sparsity is used only to select a candidate for "
                "lowering; it is not a production cycle decision"
            ),
        },
        "exactness": {
            "rank7_basis_products": rank7_checks,
            "rank8_basis_products": rank8_checks,
            "asymmetric_basis_products": len(lambdas) * 16,
            "expected_each": len(lambdas) * 16,
            "lambda_dependent_reduction":
                "d0+lambda*d4,d1+lambda*d5,d2+lambda*d6,d3",
        },
        "selected_rank7": compact_tensor(selected7),
        "selected_rank8": compact_tensor(selected8),
        "selected_asymmetric_rank7": {
            "description": asymmetric["description"],
            "row_scales_balanced": [balanced(value)
                                    for value in asymmetric["row_scales"]],
            "h_input_cost_proxy": asymmetric["input_h"],
            "r_input_cost_proxy": asymmetric["input_r"],
            "output_cost_proxy": asymmetric["output"],
        },
        "operation_classes": {
            "current_quartic_algebraic_variable_products":
                current_variable_rank,
            "rank7_algebraic_variable_products": 7,
            "rank8_algebraic_variable_products": 8,
            "rank7_bilinear_rank_delta": 7 - current_variable_rank,
            "rank8_bilinear_rank_delta": 8 - current_variable_rank,
            "current_selected_L01_full_width_Montgomery_chains_per_16_quartics":
                current_physical_chains,
            "rank7_pointwise_full_width_chains_before_W_lambda": 7,
            "rank8_pointwise_full_width_chains_before_W_lambda": 8,
            "physical_chain_comparison_warning": (
                "the current twelve chains already mix variable products and "
                "lambda work; rank7/rank8 W_lambda constant chains remain "
                "unlowered and must be added before a total comparison"
            ),
            "rank7_redundant_forms_per_operand": 7,
            "rank8_redundant_forms_per_operand": 8,
            "lambda_and_interpolation": (
                "already combined into one W_lambda table; no separate "
                "post-interpolation lambda step is assumed"
            ),
            "unresolved": [
                "AVX2 lowering of producer linear forms",
                "number and placement of constant-Montgomery chains in W_lambda",
                "range and checkpoint schedule",
                "register pressure for seven/eight live product streams",
                "whether Decode and Forward can emit evaluation forms natively",
                "whether recombination can feed add/Q24 without monomial materialization",
            ],
        },
        "research_gate": {
            "continuation_triggered_by": [
                "rank7 lowers algebraic variable-product rank from nine to seven",
                "rank8 lowers algebraic variable-product rank from nine to eight",
                "evaluation forms define a redundant producer-native contract",
                "asymmetric h/r row scaling is exact and output constants are foldable into W_lambda",
            ],
            "not_required_yet": [
                "negative total instruction delta",
                "20-cycle static margin",
                "production placement win",
            ],
            "decision": "continue-to-avx2-lowering-and-range-gate",
        },
        "next_gate": {
            "name": "GT32-QUARTIC-TENSOR-LOWERING-059B",
            "must_answer": [
                "form seven rank7 operands for h and r with explicit AVX2 DAGs",
                "schedule seven pointwise Montgomery products",
                "lower W_lambda with constants precombined with Montgomery scale",
                "prove i16/i32 bounds and count required REDC checkpoints",
                "compute peak YMM and spill-free feasibility",
                "identify producer-native Decode/Forward forms rather than charging all synthesis to B3",
            ],
            "close_only_if": (
                "all lowering families restore the same effective variable-product/REDC/"
                "recombination classes and add conversions, leaving no new mechanism"
            ),
        },
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({
        "rank7_point_sets": len(candidates),
        "selected_rank7_points": selected7["points"],
        "rank7_checks": rank7_checks,
        "rank8_checks": rank8_checks,
        "rank7_bilinear_rank_delta": 7 - current_variable_rank,
        "decision": report["research_gate"]["decision"],
    }, indent=2))


if __name__ == "__main__":
    main()
