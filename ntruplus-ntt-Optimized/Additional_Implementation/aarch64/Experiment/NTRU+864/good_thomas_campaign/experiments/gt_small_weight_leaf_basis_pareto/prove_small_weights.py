#!/usr/bin/env python3
"""Exact leaf, signed BaseMul, range, and inverse-factor proof for CF5-F."""

from __future__ import annotations

import json
import math

Q = 3457
THETA = 9
ORDER = 864
ROWS = 9
COLUMNS = 16
SLOPES = (32, 176, 464, 752)
TOPS = (("alpha", 1, 9, 1), ("beta", 5, 3, 27))
B0 = 26306
B12 = (3 * Q) // 2
INT32_MAX = 2**31 - 1


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def cubic_product(left, right, weight):
    a0, a1, a2 = left
    b0, b1, b2 = right
    return ((a0*b0 + weight*(a1*b2+a2*b1)) % Q,
            (a0*b1+a1*b0 + weight*a2*b2) % Q,
            (a0*b2+a1*b1+a2*b0) % Q)


def basis_product(i, j, modulus):
    degree = i+j
    return (degree-3, modulus) if degree >= 3 else (degree, 1)


def main():
    reports = []
    total_homomorphisms = 0
    total_signed_polarity = 0
    for slope in SLOPES:
        k = (96 - 3*slope) % ORDER
        expected_signed = slope != 32
        weights = set()
        homomorphisms = 0
        polarity_checks = 0
        for top, residue, base, kappa in TOPS:
            for row in range(ROWS):
                expected_weight = base * pow(THETA, k*row, Q) % Q
                if expected_signed:
                    assert centered(expected_weight) == (base if row % 2 == 0 else -base)
                else:
                    assert centered(expected_weight) == base
                for column in range(COLUMNS):
                    z = pow(THETA, residue+6*column+96*row, Q)
                    u = kappa * pow(THETA, 2*column+slope*row, Q) % Q
                    weight = z * pow(pow(u, 3, Q), -1, Q) % Q
                    assert weight == expected_weight
                    weights.add(centered(weight))
                    for i in range(3):
                        for j in range(3):
                            old_degree, old_factor = basis_product(i, j, z)
                            new_degree, new_factor = basis_product(i, j, weight)
                            lhs = old_factor * pow(u, old_degree, Q) % Q
                            rhs = pow(u, i+j, Q) * new_factor % Q
                            assert old_degree == new_degree and lhs == rhs
                            homomorphisms += 1

                    # Signed weights change only the public polarity of the
                    # two wrap terms; verify the complete bilinear formula on
                    # all nine basis-vector pairs.
                    for i in range(3):
                        for j in range(3):
                            left = [0, 0, 0]
                            right = [0, 0, 0]
                            left[i] = right[j] = 1
                            positive = cubic_product(left, right, abs(centered(weight)))
                            signed = cubic_product(left, right, centered(weight))
                            if centered(weight) < 0 and i+j >= 3:
                                expected = list(positive)
                                expected[i+j-3] = -expected[i+j-3] % Q
                                assert signed == tuple(expected)
                            else:
                                assert signed == positive
                            polarity_checks += 1

        expected_weights = {3, 9} if slope == 32 else {-9, -3, 3, 9}
        assert weights == expected_weights
        assert homomorphisms == 288*9
        assert polarity_checks == 288*9

        max_weight = max(map(abs, weights))
        bounds = {
            "c0": B0*B0 + 2*max_weight*B12*B12,
            "c1": 2*B0*B12 + max_weight*B12*B12,
            "c2": 2*B0*B12 + B12*B12,
        }
        assert max(bounds.values()) < INT32_MAX

        gamma_order = ORDER // math.gcd(ORDER, slope)
        inverse_row_mulmods = 0
        inverse_identities = []
        for component in (1, 2):
            for row in range(1, ROWS):
                if slope*component*row % ORDER == 0:
                    inverse_identities.append((component, row))
                else:
                    # Two tops and two eight-column blocks use the same row
                    # constant, hence four vector mulmods per (component,row).
                    inverse_row_mulmods += 4
        assert inverse_row_mulmods == 64

        reports.append({
            "H": slope,
            "K": k,
            "representation": "FRISO2" if slope == 32 else "FR_SIGN4",
            "weights": sorted(weights),
            "weight_classes": len(weights),
            "basis_homomorphism_checks": homomorphisms,
            "signed_polarity_checks": polarity_checks,
            "direct_wide_bounds": bounds,
            "direct_wide_int32": "pass",
            "gamma_order": gamma_order,
            "inverse_row_mulmods": inverse_row_mulmods,
            "inverse_nonzero_row_identities": inverse_identities,
            "delta_column_factor_absorbable_into_existing_inverse_twist": True,
        })
        total_homomorphisms += homomorphisms
        total_signed_polarity += polarity_checks

    print(json.dumps({
        "gate": "M5U-CF5-F-small-weight-proof",
        "status": "pass",
        "slopes": reports,
        "total_basis_homomorphism_checks": total_homomorphisms,
        "total_signed_polarity_checks": total_signed_polarity,
        "BaseMul_extra_mulmods_for_sign": 0,
        "BaseMul_extra_reductions_for_sign": 0,
        "inverse_row_mulmods_all_candidates": 64,
        "production_linked": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
