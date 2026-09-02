#!/usr/bin/env python3
"""Exact FR-ISO2 factor and Algorithm-10 range proof for M5U-CF0."""

from __future__ import annotations

import json

from generate_candidate import Q, THETA, centered, reciprocal, tau

BOUND = 26306


def i16(value: int) -> int:
    value &= 0xFFFF
    return value - 0x10000 if value >= 0x8000 else value


def sqrdmulh(left: int, right: int) -> int:
    numerator = 2 * left * right + 32768
    if numerator >= 0:
        return numerator // 65536
    return -((-numerator + 65535) // 65536)


def algorithm10(value: int, factor: int) -> int:
    factor = centered(factor)
    quotient = sqrdmulh(value, reciprocal(factor))
    return i16(i16(value * factor) - i16(quotient * Q))


def main() -> None:
    checks = 0
    maximum = 0
    constants = set()
    for top in range(2):
        z0 = 9 if top == 0 else 3
        for row in range(9):
            for column in range(16):
                factor = tau(top, row, column)
                assert pow(factor, 3, Q) * z0 % Q == pow(
                    THETA, (1 if top == 0 else 5) + 6 * column + 96 * row, Q)
                for component in (1, 2):
                    scale = pow(factor, component, Q)
                    constants.add(centered(scale))
                    for value in range(-BOUND, BOUND + 1):
                        output = algorithm10(value, scale)
                        assert (output - value * scale) % Q == 0
                        maximum = max(maximum, abs(output))
                        checks += 1
    assert maximum < (3 * Q + 1) // 2
    result = {
        "status": "pass",
        "leaf_factor_identities": 288,
        "algorithm10_exhaustive_checks": checks,
        "distinct_centered_constants": len(constants),
        "input_absolute_bound": BOUND,
        "maximum_output_absolute_value": maximum,
        "strict_algorithm10_bound": "abs(output) < 3q/2",
        "scale": "R0_to_R0",
        "coefficient_memory_boundaries_added": 0,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
