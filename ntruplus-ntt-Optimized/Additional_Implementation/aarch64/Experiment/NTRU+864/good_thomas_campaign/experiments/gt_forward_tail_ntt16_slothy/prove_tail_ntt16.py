#!/usr/bin/env python3
"""Prove M5L coordinate flow and Algorithm-10 equivalence."""

from __future__ import annotations

import json
import random

Q = 3457
THETA = 9
OMEGA = pow(THETA, 54, Q)
RESIDUES = (1, 5)
BR4 = (0, 8, 4, 12, 2, 10, 6, 14, 1, 9, 5, 13, 3, 11, 7, 15)
RAW_MAP = (0, 4, 2, 6, 1, 5, 3, 7)
STAGE_EXPONENTS = (
    (0, 0, 0, 0, 4, 4, 4, 4),
    (0, 0, 4, 4, 2, 2, 6, 6),
    (0, 4, 2, 6, 1, 5, 3, 7),
)
BITREV3_BYTES = (0, 1, 8, 9, 4, 5, 12, 13, 2, 3, 10, 11, 6, 7, 14, 15)


def centered(x: int) -> int:
    x %= Q
    return x - Q if x > Q // 2 else x


def reciprocal(b: int) -> int:
    n = (abs(b) * (1 << 15) + Q // 2) // Q
    return -n if b < 0 else n


def alg10(a: int, b: int) -> int:
    bp = reciprocal(b)
    quotient = (2 * a * bp + (1 << 15)) >> 16
    value = a * b - quotient * Q
    assert -32768 <= value <= 32767
    return value


def scalar_reference(values: list[int], residue: int) -> list[int]:
    state = [0] * 16
    for t, value in enumerate(values):
        twist = centered(pow(THETA, 9 * residue * t, Q))
        state[BR4[t]] = alg10(value, twist)
    for length in (2, 4, 8, 16):
        half = length // 2
        for start in range(0, 16, length):
            for j in range(half):
                left, right = start + j, start + j + half
                product = alg10(state[right], centered(pow(OMEGA, j * 16 // length, Q)))
                u = state[left]
                state[left], state[right] = u + product, u - product
    return state


def trn(a: list[int], b: list[int], unit: int) -> tuple[list[int], list[int]]:
    ac = [a[i:i + unit] for i in range(0, 8, unit)]
    bc = [b[i:i + unit] for i in range(0, 8, unit)]
    lo = sum((ac[i] + bc[i] for i in range(0, len(ac), 2)), [])
    hi = sum((ac[i] + bc[i] for i in range(1, len(ac), 2)), [])
    return lo, hi


def packed_candidate(values: list[int], residue: int) -> list[int]:
    twisted = [alg10(v, centered(pow(THETA, 9 * residue * t, Q)))
               for t, v in enumerate(values)]
    first_products = [alg10(twisted[i + 8], 1) for i in range(8)]
    left = [twisted[i] + first_products[i] for i in range(8)]
    right = [twisted[i] - first_products[i] for i in range(8)]
    for unit, exponents in zip((4, 2, 1), STAGE_EXPONENTS):
        left, right = trn(left, right, unit)
        products = [alg10(v, centered(pow(OMEGA, e, Q)))
                    for v, e in zip(right, exponents)]
        left, right = ([u + v for u, v in zip(left, products)],
                       [u - v for u, v in zip(left, products)])
    out = [0] * 16
    for lane, column in enumerate(RAW_MAP):
        out[column] = left[lane]
        out[8 + column] = right[lane]
    return out


def main() -> None:
    rng = random.Random(0x8645A11)
    cases = [[0] * 16]
    cases += [[1 if i == j else 0 for i in range(16)] for j in range(16)]
    cases += [[rng.randint(-15752, 15752) for _ in range(16)] for _ in range(20000)]
    max_abs = 0
    for residue in RESIDUES:
        for values in cases:
            reference = scalar_reference(values, residue)
            candidate = packed_candidate(values, residue)
            assert candidate == reference
            max_abs = max(max_abs, *(abs(x) for x in candidate))
    report = {
        "gate": "pass",
        "top_residues": list(RESIDUES),
        "tested_vectors_per_top": len(cases),
        "basis_vectors": 16,
        "random_vectors_per_top": 20000,
        "tail_addresses": [768 + 8 * t for t in range(16)],
        "tail_byte_stride": 16,
        "tail_pointer_advance_bytes": 256,
        "raw_lane_to_column": list(RAW_MAP),
        "bitrev3_byte_table": list(BITREV3_BYTES),
        "stage_exponents": [list(x) for x in STAGE_EXPONENTS],
        "sampled_max_abs": max_abs,
        "range_oracle": "M5G exact DAG maximum 9342",
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
