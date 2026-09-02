#!/usr/bin/env python3
"""Exact representation-map, basis-product, coset, and feasibility proof."""

from __future__ import annotations

import hashlib
import json

Q = 3457
THETA = 9
ROWS = 9
COLUMNS = 16
TOPS = (("alpha", 1, 9, 1), ("beta", 5, 3, 27))


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def old_basis_product(i: int, j: int, z: int) -> tuple[int, int]:
    degree = i + j
    return (degree - 3, z) if degree >= 3 else (degree, 1)


def new_basis_product(i: int, j: int, z0: int) -> tuple[int, int]:
    degree = i + j
    return (degree - 3, z0) if degree >= 3 else (degree, 1)


def main() -> None:
    character_counts: dict[int, int] = {}
    rows = []
    basis_checks = 0
    roots = set()
    taus = set()

    for top, residue, z0, kappa in TOPS:
        expected_character = pow(z0, (Q - 1) // 3, Q)
        assert expected_character != 1
        for row in range(ROWS):
            for column in range(COLUMNS):
                z = pow(THETA, residue + 6 * column + 96 * row, Q)
                tau = kappa * pow(THETA, 2 * column + 32 * row, Q) % Q
                assert pow(tau, 3, Q) * z0 % Q == z
                character = pow(z, (Q - 1) // 3, Q)
                assert character == expected_character
                character_counts[character] = character_counts.get(character, 0) + 1
                roots.add(z)
                taus.add((top, tau))

                # Bilinearity makes the nine basis pairs a complete proof that
                # phi_tau(a*b)=phi_tau(a)*phi_tau(b).
                for i in range(3):
                    for j in range(3):
                        old_degree, old_factor = old_basis_product(i, j, z)
                        new_degree, new_factor = new_basis_product(i, j, z0)
                        lhs = old_factor * pow(tau, old_degree, Q) % Q
                        rhs = pow(tau, i + j, Q) * new_factor % Q
                        assert old_degree == new_degree and lhs == rhs
                        basis_checks += 1
                rows.append((top, row, column, z, z0, tau,
                             tau * tau % Q, character))

    assert len(roots) == 288
    assert sorted(character_counts.values()) == [144, 144]
    assert basis_checks == 288 * 9

    # No diagonal three-coordinate basis can make two of the three wrap
    # constants simultaneously one: any such pair of equations implies that z
    # has a cube root, contradicted by the character check above.
    diagonal_min_nontrivial_constants = 2

    b0 = 26306  # M5R-D largest component-0/new-node bound.
    b12 = (3 * Q) // 2  # Algorithm-10 strict bound is < 3q/2.
    range_by_branch = {}
    for top, _, z0, _ in TOPS:
        bounds = {
            "c0": b0 * b0 + 2 * z0 * b12 * b12,
            "c1": 2 * b0 * b12 + z0 * b12 * b12,
            "c2": 2 * b0 * b12 + b12 * b12,
        }
        assert max(bounds.values()) < 2**31
        range_by_branch[top] = bounds

    ledger = "\n".join(",".join(map(str, row)) for row in rows)
    print(json.dumps({
        "gate": "gt864_friso2_leaf_basis_abi",
        "status": "pass",
        "leaf_count": len(rows),
        "unique_leaf_roots": len(roots),
        "cube_character_counts": character_counts,
        "branch_moduli": {"alpha": "Y^3-9", "beta": "Y^3-3"},
        "tau_formula": {
            "alpha": "theta^(2*column+32*row)",
            "beta": "27*theta^(2*column+32*row)",
        },
        "basis_pair_homomorphism_checks": basis_checks,
        "diagonal_basis_minimum_nontrivial_wrap_constants":
            diagonal_min_nontrivial_constants,
        "m5rd_component0_bound_used": b0,
        "algorithm10_component12_bound_used": b12,
        "direct_int32_accumulator_feasibility": range_by_branch,
        "all_direct_accumulators_fit_int32": True,
        "ledger_sha256": hashlib.sha256(ledger.encode()).hexdigest(),
        "codegen_claim": False,
        "production_linked": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
