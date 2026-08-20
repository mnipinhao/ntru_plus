#!/usr/bin/env python3
"""Scalar proofs/tests for the proposed AVX2-oriented 9x16 mapping."""

from __future__ import annotations

import random
import sys
import unittest
from pathlib import Path

COMMON = Path(__file__).resolve().parents[4] / "common" / "gt9x16"
sys.path.insert(0, str(COMMON))

from model import (  # noqa: E402
    GT_LANES,
    GT_ROWS,
    gt_input_index,
    gt_output_index,
    materialize_y_from_z,
    relabel_h_to_r,
    scalar_shear_z,
    scalar_y,
)

Q = 3457
N = 144


def prime_factors(value: int) -> set[int]:
    result = set()
    divisor = 2
    while divisor * divisor <= value:
        while value % divisor == 0:
            result.add(divisor)
            value //= divisor
        divisor += 1
    if value > 1:
        result.add(value)
    return result


def primitive_root(modulus: int) -> int:
    order = modulus - 1
    factors = prime_factors(order)
    for candidate in range(2, modulus):
        if all(pow(candidate, order // factor, modulus) != 1 for factor in factors):
            return candidate
    raise AssertionError("primitive root not found")


ROOT_144 = pow(primitive_root(Q), (Q - 1) // N, Q)


def direct_transform(source: list[int]) -> list[int]:
    return [sum(value * pow(ROOT_144, n * k, Q) for n, value in enumerate(source)) % Q
            for k in range(N)]


def factored_transform(source: list[int]) -> list[int]:
    result = [0] * N
    root9 = pow(ROOT_144, 16, Q)
    root16 = pow(ROOT_144, 9, Q)
    for p in range(GT_ROWS):
        for q in range(GT_LANES):
            value = 0
            for u in range(GT_ROWS):
                for v in range(GT_LANES):
                    value += (source[gt_input_index(u, v)] * pow(root9, u * p, Q)
                              * pow(root16, v * q, Q))
            result[gt_output_index(p, q)] = value % Q
    return result


class GT9x16OracleTest(unittest.TestCase):
    def test_root_has_exact_order_144(self) -> None:
        self.assertEqual(pow(ROOT_144, N, Q), 1)
        self.assertNotEqual(pow(ROOT_144, N // 2, Q), 1)
        self.assertNotEqual(pow(ROOT_144, N // 3, Q), 1)

    def test_crt_kernel_identity(self) -> None:
        for u in range(GT_ROWS):
            for v in range(GT_LANES):
                for p in range(GT_ROWS):
                    for q in range(GT_LANES):
                        n = gt_input_index(u, v)
                        k = gt_output_index(p, q)
                        self.assertEqual((n * k) % N, (16 * u * p + 9 * v * q) % N)

    def test_factored_transform_matches_direct(self) -> None:
        generator = random.Random(0x9_16_1152)
        vectors = [
            [0] * N,
            [1] + [0] * (N - 1),
            [(-1 if index & 1 else 1) % Q for index in range(N)],
            [generator.randrange(Q) for _ in range(N)],
        ]
        for source in vectors:
            self.assertEqual(factored_transform(source), direct_transform(source))

    def test_row_relabel_and_shear_invariant(self) -> None:
        generator = random.Random(0x5EA4)
        for _ in range(200):
            h_rows = [[generator.randrange(-32768, 32768) for _ in range(GT_LANES)]
                      for _ in range(GT_ROWS)]
            r_rows = relabel_h_to_r(h_rows)
            y_rows = scalar_y(r_rows)
            z_rows = scalar_shear_z(r_rows)
            for row in range(GT_ROWS):
                self.assertEqual(z_rows[row][:8], y_rows[row][:8])
                self.assertEqual(z_rows[row][8:], y_rows[(row + 1) % GT_ROWS][8:])
            self.assertEqual(materialize_y_from_z(z_rows), y_rows)


if __name__ == "__main__":
    unittest.main()
