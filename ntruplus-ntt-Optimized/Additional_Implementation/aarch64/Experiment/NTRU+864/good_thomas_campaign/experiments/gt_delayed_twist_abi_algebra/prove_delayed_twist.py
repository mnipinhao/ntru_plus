#!/usr/bin/env python3
"""Prove which pending twist states are diagonal/permutation leaf ABIs."""

from __future__ import annotations

import json

Q = 3457
THETA = 9
ETA = pow(THETA, 96, Q)


def matrix(lam: int) -> list[list[int]]:
    return [[pow(lam * pow(ETA, k, Q) % Q, s, Q) for s in range(9)]
            for k in range(9)]


def diagonal_permutation(source: list[list[int]], target: list[list[int]]):
    matches = []
    for k, target_row in enumerate(target):
        row_matches = []
        for p, source_row in enumerate(source):
            # Column zero is one in both transforms, so any diagonal d must be 1.
            d = target_row[0] * pow(source_row[0], -1, Q) % Q
            if all(target_row[s] == d * source_row[s] % Q for s in range(9)):
                row_matches.append((p, d))
        matches.append(row_matches)
    if all(len(row) == 1 for row in matches):
        permutation = [row[0][0] for row in matches]
        if len(set(permutation)) == 9:
            return permutation, [row[0][1] for row in matches]
    return None


def main() -> None:
    untwisted = matrix(1)
    rejected = []
    rotations = 0
    for top, residue in enumerate((1, 5)):
        for column in range(16):
            lam = pow(THETA, residue + 6 * column, Q)
            ordinary = matrix(lam)
            assert diagonal_permutation(ordinary, untwisted) is None
            rejected.append((top, column, lam))
            for a in range(9):
                shifted = matrix(lam * pow(ETA, a, Q) % Q)
                relation = diagonal_permutation(ordinary, shifted)
                assert relation is not None
                permutation, factors = relation
                assert permutation == [(k + a) % 9 for k in range(9)]
                assert factors == [1] * 9
                rotations += 1
    eta_subgroup = {pow(ETA, a, Q) for a in range(9)}
    assert all(lam not in eta_subgroup for _, _, lam in rejected)
    print(json.dumps({
        "status": "pass-with-rejected-general-delayed-scalar-ABI",
        "lambda_leaves_checked": len(rejected),
        "untwisted_diagonal_permutation_matches": 0,
        "lambda_eta_row_rotations_checked": rotations,
        "basis_columns_per_matrix": 9,
        "reason": "lambda is outside <eta>, so removing lambda^s changes evaluation coset rather than multiplying or rotating leaf outputs",
        "surviving_ABI": "lambda -> lambda*eta^a is pure row rotation",
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
