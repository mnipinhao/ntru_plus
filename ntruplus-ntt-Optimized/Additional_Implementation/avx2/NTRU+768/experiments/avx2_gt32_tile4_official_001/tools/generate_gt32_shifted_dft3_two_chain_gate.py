#!/usr/bin/env python3
"""Search two-chain circuits for DFT3*diag(1,a,a^2).

The circuit model is

  m0 = C0 * (alpha dot x)
  m1 = C1 * (b dot x + beta*m0)
  y  = Gamma*x + u*m0 + v*m1

where C0/C1 are arbitrary field constants.  G1 restricts every cheap
coefficient to 0,+/-1.  G2 exhaustively permits 0,+/-1,+/-2.  This includes a
dependency from the second Montgomery chain to the first and arbitrary small
coefficient output reconstruction; it is broader than an x1+/-x2 Winograd
probe.
"""

from __future__ import annotations

import itertools
import json
from collections import defaultdict

import generate_tile4 as gt


OUT = gt.GENERATED / "tile4_shifted_dft3_two_chain_gate.json"
RHO = (-723) % gt.Q
BRANCH_A = (867, 1886)


def scale(constant, vector):
    return tuple(constant * value % gt.Q for value in vector)


def normalize(vector):
    vector = tuple(value % gt.Q for value in vector)
    if not any(vector):
        return None
    index = next(index for index, value in enumerate(vector) if value)
    inverse = pow(vector[index], -1, gt.Q)
    return tuple(value * inverse % gt.Q for value in vector)


def proportional_constant(destination, source):
    if normalize(destination) != normalize(source) or normalize(source) is None:
        return None
    index = next(index for index, value in enumerate(source) if value)
    return destination[index] * pow(source[index] % gt.Q, -1, gt.Q) % gt.Q


def target_matrix(a):
    a2 = a * a % gt.Q
    rho2 = RHO * RHO % gt.Q
    return (
        (1, a, a2),
        (1, RHO * a % gt.Q, rho2 * a2 % gt.Q),
        (1, rho2 * a % gt.Q, RHO * a2 % gt.Q),
    )


def g1_search(matrix):
    small = (-1, 0, 1)
    raw = list(itertools.product(small, repeat=3))
    forms = [form for form in raw if any(form)]
    m0_values = {}
    for alpha in forms:
        for constant in range(1, gt.Q):
            m0_values.setdefault(scale(constant, alpha), (alpha, constant))

    checked = 0
    for m0, (alpha, c0) in m0_values.items():
        output_maps = []
        output_free = []
        for target in matrix:
            candidates = {}
            free = False
            for gamma in raw:
                for d0 in small:
                    residual = tuple(
                        (target[index] - gamma[index] - d0 * m0[index]) % gt.Q
                        for index in range(3)
                    )
                    free |= not any(residual)
                    candidates.setdefault(residual, (gamma, d0, 1))
                    candidates.setdefault(tuple(-value % gt.Q for value in residual),
                                          (gamma, d0, -1))
            output_maps.append(candidates)
            output_free.append(free)

        constrained = [output_maps[index] for index in range(3)
                       if not output_free[index]]
        if constrained:
            common = set(constrained[0])
            for candidates in constrained[1:]:
                common.intersection_update(candidates)
        else:
            common = {(1, 0, 0)}

        for m1 in common:
            for b in raw:
                for beta in small:
                    source = tuple(
                        (b[index] + beta * m0[index]) % gt.Q
                        for index in range(3)
                    )
                    c1 = proportional_constant(m1, source)
                    if c1 is not None:
                        return {
                            "found": True, "alpha": alpha, "C0": c0,
                            "b": b, "beta": beta, "C1": c1,
                        }
        checked += 1
    return {
        "found": False,
        "unique_first_chain_results_checked": checked,
        "projective_first_input_lines": len({normalize(form) for form in forms}),
    }


def cross(left, right):
    return (
        (left[1] * right[2] - left[2] * right[1]) % gt.Q,
        (left[2] * right[0] - left[0] * right[2]) % gt.Q,
        (left[0] * right[1] - left[1] * right[0]) % gt.Q,
    )


def determinant(matrix):
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2]
                        - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2]
                          - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1]
                          - matrix[1][1] * matrix[2][0])
    ) % gt.Q


def solve_basis(u, v, residual):
    pivot = None
    for first in range(3):
        for second in range(first + 1, 3):
            det = (u[first] * v[second] - u[second] * v[first]) % gt.Q
            if det:
                pivot = first, second, det
                break
        if pivot:
            break
    assert pivot is not None
    first, second, det = pivot
    inverse = pow(det, -1, gt.Q)
    m0 = []
    m1 = []
    for column in range(3):
        x = residual[first][column]
        y = residual[second][column]
        p = (x * v[second] - y * v[first]) * inverse % gt.Q
        q = (u[first] * y - u[second] * x) * inverse % gt.Q
        if any((u[row] * p + v[row] * q - residual[row][column]) % gt.Q
               for row in range(3)):
            return None
        m0.append(p)
        m1.append(q)
    return tuple(m0), tuple(m1)


def g2_search(matrix):
    small = tuple(range(-2, 3))
    forms = list(itertools.product(small, repeat=3))
    nonzero = [form for form in forms if any(form)]

    planes = defaultdict(list)
    for u in nonzero:
        for v in nonzero:
            normal = normalize(cross(u, v))
            if normal is not None:
                planes[normal].append((u, v))
    alpha_lines = {}
    for alpha in nonzero:
        alpha_lines.setdefault(normalize(alpha), alpha)

    singular_residuals = 0
    rank_at_most_one = 0
    basis_tests = 0
    for flat_gamma in itertools.product(small, repeat=9):
        residual = tuple(tuple(
            (matrix[row][column] - flat_gamma[3 * row + column]) % gt.Q
            for column in range(3)) for row in range(3))
        if determinant(residual):
            continue
        columns = [tuple(residual[row][column] for row in range(3))
                   for column in range(3)]
        normal = None
        for first in range(3):
            for second in range(first + 1, 3):
                normal = normalize(cross(columns[first], columns[second]))
                if normal is not None:
                    break
            if normal is not None:
                break
        if normal is None:
            rank_at_most_one += 1
            continue
        singular_residuals += 1

        for u, v in planes.get(normal, ()):
            basis_tests += 1
            solution = solve_basis(u, v, residual)
            if solution is None:
                continue
            m0, m1 = solution
            alpha = alpha_lines.get(normalize(m0))
            if alpha is None:
                continue
            c0 = proportional_constant(m0, alpha)
            for beta in small:
                for b in forms:
                    source = tuple(
                        (b[index] + beta * m0[index]) % gt.Q
                        for index in range(3)
                    )
                    c1 = proportional_constant(m1, source)
                    if c1 is not None:
                        return {
                            "found": True, "Gamma": flat_gamma,
                            "u": u, "v": v, "alpha": alpha, "C0": c0,
                            "b": b, "beta": beta, "C1": c1,
                        }
    return {
        "found": False,
        "small_Gamma_matrices_checked": 5 ** 9,
        "singular_rank2_residuals": singular_residuals,
        "rank_at_most_one_residuals": rank_at_most_one,
        "small_projective_input_lines": len(alpha_lines),
        "small_output_planes": len(planes),
        "ordered_small_plane_bases": sum(len(values) for values in planes.values()),
        "basis_factorizations_checked": basis_tests,
    }


def main():
    assert BRANCH_A[0] * BRANCH_A[1] % gt.Q == 1
    assert tuple(a * a % gt.Q for a in BRANCH_A) == (1520, 3200)
    branches = []
    for branch, a in enumerate(BRANCH_A):
        matrix = target_matrix(a)
        g1 = g1_search(matrix)
        g2 = g2_search(matrix)
        assert not g1["found"]
        assert not g2["found"]
        branches.append({
            "branch": branch,
            "a": a,
            "a_squared": a * a % gt.Q,
            "matrix": matrix,
            "G1_coefficients_0_pm1": g1,
            "G2_coefficients_0_pm1_pm2": g2,
        })

    result = {
        "experiment": "GT32-SHIFTED-DFT3-TWO-CHAIN-001",
        "status": "two-chain-small-coefficient-hard-stop",
        "transform": "DFT3 * diag(1,a,a^2)",
        "rho": RHO,
        "branch_a_constants": list(BRANCH_A),
        "branch_constants_are_inverses": True,
        "circuit_model": {
            "m0": "C0*(alpha dot x)",
            "m1": "C1*(b dot x + beta*m0)",
            "outputs": "Gamma*x + u*m0 + v*m1",
            "C0_C1": "arbitrary nonzero F_q constants",
            "G1_cheap_coefficients": [0, 1, -1],
            "G2_cheap_coefficients": [0, 1, -1, 2, -2],
            "second_chain_may_depend_on_first": True,
        },
        "branches": branches,
        "decision": {
            "assembly_emitted": False,
            "benchmark_run": False,
            "stage_gauge_status": "arithmetic-route-paused",
            "reason": (
                "neither branch has a two-chain circuit in the exhaustive "
                "0,+/-1 or 0,+/-1,+/-2 linear circuit models; the known "
                "three-chain A-scale-plus-DFT3 schedule remains"
            ),
        },
        "scope_limit": (
            "this is not an unrestricted multiplicative-complexity theorem; "
            "it is exhaustive for the stated AVX2-relevant small-coefficient "
            "sequential two-chain model"
        ),
        "reopen_only_if": [
            "a symbolic identity outside the small-coefficient circuit model is supplied",
            "the raw-stage ratio folds into an independently required producer multiply",
            "a different representation changes the shifted-DFT3 matrix",
        ],
    }
    OUT.write_text(json.dumps(result, indent=2) + "\n")
    print(OUT.relative_to(gt.ROOT))
    print("decision: no two-chain shifted DFT3 in G1 or G2 for either branch")


if __name__ == "__main__":
    main()
