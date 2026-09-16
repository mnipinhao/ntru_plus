#!/usr/bin/env python3
"""Exact CF5-E B3-connectivity, leaf-basis, weight, and range proof."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

Q = 3457
GENERATOR = 7
THETA = 9
ORDER = Q - 1
ROWS = 9
COLUMNS = 16
B0 = 26306
B12 = (3 * Q) // 2
INT32_MAX = 2**31 - 1
TOPS = (("alpha", 1, 9, 1), ("beta", 5, 3, 27))

ROOT = Path(__file__).resolve().parent
DAG_SOURCE = ROOT.parent / "gt_friso2_scaled_ntt9_search" / "search_scaled_dag.py"
SPEC = importlib.util.spec_from_file_location("cf5e_dag", DAG_SOURCE)
assert SPEC and SPEC.loader
DAG_MODEL = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = DAG_MODEL
SPEC.loader.exec_module(DAG_MODEL)


class UnionFind:
    def __init__(self, values):
        self.parent = {value: value for value in values}

    def find(self, value):
        while self.parent[value] != value:
            self.parent[value] = self.parent[self.parent[value]]
            value = self.parent[value]
        return value

    def union(self, left, right):
        left, right = self.find(left), self.find(right)
        if left != right:
            self.parent[right] = left


def order(value: int) -> int:
    result = 1
    cursor = value % Q
    while cursor != 1:
        cursor = cursor * value % Q
        result += 1
    return result


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def old_basis_product(i: int, j: int, z: int):
    degree = i + j
    return (degree - 3, z) if degree >= 3 else (degree, 1)


def new_basis_product(i: int, j: int, weight: int):
    degree = i + j
    return (degree - 3, weight) if degree >= 3 else (degree, 1)


def accumulator_bounds(weight_abs: int):
    return {
        "c0": B0 * B0 + 2 * weight_abs * B12 * B12,
        "c1": 2 * B0 * B12 + weight_abs * B12 * B12,
        "c2": 2 * B0 * B12 + B12 * B12,
    }


def best_row_coset(base: int):
    best = None
    # Multiplying u by gamma divides every weight by the public cube gamma^3.
    for gamma in range(1, Q):
        cube_inverse = pow(pow(gamma, 3, Q), -1, Q)
        values = [centered(base * pow(THETA, 96 * row, Q) * cube_inverse)
                  for row in range(ROWS)]
        candidate = (max(map(abs, values)), gamma, values)
        if best is None or candidate[0] < best[0]:
            best = candidate
    assert best is not None
    return best


def main():
    theta_order = order(THETA)
    row_generator_order = order(pow(THETA, 96, Q))
    assert theta_order == 864 and row_generator_order == 9

    dag, inputs, outputs = DAG_MODEL.build_dag()
    union = UnionFind(dag.nodes)
    for add in dag.adds:
        # Zero post-add rescaling requires output, left, and right to carry the
        # same representation scale.
        union.union(add.output, add.left)
        union.union(add.output, add.right)
    output_components = {union.find(node) for node in outputs}
    all_components = {union.find(node) for node in dag.nodes}
    assert len(output_components) == 1
    assert len(all_components) == 1

    common_scale_slopes = [h for h in range(theta_order)
                           if pow(THETA, h, Q) == 1]
    constant_weight_slopes = [h for h in range(theta_order)
                              if pow(THETA, 96 - 3 * h, Q) == 1]
    assert common_scale_slopes == [0]
    assert constant_weight_slopes == [32, 320, 608]
    assert not set(common_scale_slopes) & set(constant_weight_slopes)

    weights = set()
    homomorphism_checks = 0
    default_rows = {}
    for top, residue, base, kappa in TOPS:
        branch = []
        for row in range(ROWS):
            for column in range(COLUMNS):
                z = pow(THETA, residue + 6 * column + 96 * row, Q)
                u = kappa * pow(THETA, 2 * column, Q) % Q
                weight = z * pow(pow(u, 3, Q), -1, Q) % Q
                assert weight == base * pow(THETA, 96 * row, Q) % Q
                weights.add(weight)
                if column == 0:
                    branch.append(centered(weight))
                for i in range(3):
                    for j in range(3):
                        old_degree, old_factor = old_basis_product(i, j, z)
                        new_degree, new_factor = new_basis_product(i, j, weight)
                        lhs = old_factor * pow(u, old_degree, Q) % Q
                        rhs = pow(u, i + j, Q) * new_factor % Q
                        assert old_degree == new_degree and lhs == rhs
                        homomorphism_checks += 1
        default_rows[top] = branch
    assert len(weights) == 18
    assert homomorphism_checks == 288 * 9

    c0_limit = (INT32_MAX - B0 * B0) // (2 * B12 * B12)
    c1_limit = (INT32_MAX - 2 * B0 * B12) // (B12 * B12)
    strict_weight_limit = min(c0_limit, c1_limit)
    optimized = {}
    for top, _, base, _ in TOPS:
        maximum, gamma, values = best_row_coset(base)
        bounds = accumulator_bounds(maximum)
        assert maximum > strict_weight_limit
        assert bounds["c0"] > INT32_MAX and bounds["c1"] > INT32_MAX
        optimized[top] = {
            "best_public_gamma": gamma,
            "row_weights_centered": values,
            "minimum_possible_maximum_abs_weight": maximum,
            "accumulator_bounds_at_worst_weight": bounds,
            "direct_wide_int32": "fail",
        }

    # With a nonzero column slope 2*c, no input twist becomes identity.  All
    # ten existing rho/eta products remain nonidentity because the add graph is
    # one common scale component.
    forward_mulmods = {}
    for component in (1, 2):
        target_a = DAG_MODEL.LOG_THETA * 2 * component % ORDER
        zero_inputs = [s for s in range(9)
                       if (target_a + DAG_MODEL.LOG_THETA * 6 * s) % ORDER == 0]
        assert zero_inputs == []
        forward_mulmods[f"component{component}"] = {
            "input_twist_mulmods": 9,
            "rho_eta_mulmods": 10,
            "total": 19,
        }

    print(json.dumps({
        "gate": "M5U-CF5-E",
        "status": "pass_proof_reject_candidate",
        "theta_order": theta_order,
        "row_generator_order": row_generator_order,
        "B3_DAG_nodes": len(dag.nodes),
        "B3_adds": len(dag.adds),
        "zero_postadd_scale_components": len(all_components),
        "zero_postadd_output_scale_components": len(output_components),
        "common_scale_row_slopes_mod_864": common_scale_slopes,
        "two_constant_BaseMul_row_slopes_mod_864": constant_weight_slopes,
        "slope_intersection": [],
        "hybrid_basis_homomorphism_checks": homomorphism_checks,
        "hybrid_unique_BaseMul_weights": len(weights),
        "default_hybrid_row_weights": default_rows,
        "direct_wide_weight_limits": {"c0": c0_limit, "c1": c1_limit,
                                      "strict": strict_weight_limit},
        "best_cube_rescaled_row_cosets": optimized,
        "hybrid_forward_mulmods_per_block": forward_mulmods,
        "FR0_forward_mulmods_per_block": 18,
        "extra_mulmods_per_forward": 8,
        "extra_Algorithm10_instructions_for_two_Forwards": 48,
        "BaseMul_widening_reductions_deleted": 0,
        "inverse_penalty_assumed_for_screen": 0,
        "assembly_authorized": False,
        "production_linked": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
