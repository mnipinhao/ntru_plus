#!/usr/bin/env python3
"""Prove the NTRU+864 cubic-leaf root topology before GT implementation."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


Q = 3457
N = 864
LEAF_DEGREE = 3
POINTS = N // LEAF_DEGREE
GT_ROWS = 9
GT_COLUMNS = 32
MONTGOMERY_RADIX = 1 << 16


def prime_factors(value: int) -> list[int]:
    factors: list[int] = []
    divisor = 2
    remaining = value
    while divisor * divisor <= remaining:
        if remaining % divisor == 0:
            factors.append(divisor)
            while remaining % divisor == 0:
                remaining //= divisor
        divisor += 1
    if remaining > 1:
        factors.append(remaining)
    return factors


def smallest_generator(modulus: int) -> int:
    order = modulus - 1
    factors = prime_factors(order)
    for candidate in range(2, modulus):
        if all(pow(candidate, order // factor, modulus) != 1
               for factor in factors):
            return candidate
    raise AssertionError("finite-field generator not found")


def multiplicative_order(value: int, modulus: int) -> int:
    assert value % modulus != 0
    order = modulus - 1
    for factor in prime_factors(order):
        while order % factor == 0 and pow(value, order // factor, modulus) == 1:
            order //= factor
    return order


def parse_reference_zetas(source: Path) -> list[int]:
    text = source.read_text(encoding="utf-8")
    match = re.search(
        r"const\s+int16_t\s+zetas\s*\[\s*288\s*\]\s*=\s*\{(.*?)\};",
        text,
        re.DOTALL,
    )
    if match is None:
        raise AssertionError(f"could not locate zetas[288] in {source}")
    values = [int(token) for token in re.findall(r"-?\d+", match.group(1))]
    assert len(values) == POINTS, f"expected {POINTS} zetas, found {len(values)}"
    return values


def polynomial_p(value: int) -> int:
    return (pow(value, 288, Q) - pow(value, 144, Q) + 1) % Q


def polynomial_q(value: int) -> int:
    return (pow(value, 32, Q) - pow(value, 16, Q) + 1) % Q


def stable_mapping_hash(mapping: list[tuple[int, int]]) -> str:
    encoded = "\n".join(f"{row},{column}" for row, column in mapping)
    return hashlib.sha256(encoded.encode("ascii")).hexdigest()


def prove(source: Path) -> dict[str, object]:
    assert POINTS == GT_ROWS * GT_COLUMNS
    zetas = parse_reference_zetas(source)

    montgomery_r = MONTGOMERY_RADIX % Q
    montgomery_r_inverse = pow(montgomery_r, -1, Q)
    decoded = [(value * montgomery_r_inverse) % Q for value in zetas]

    legacy_leaf_roots: list[int] = []
    for index in range(POINTS // 2, POINTS):
        root = decoded[index]
        legacy_leaf_roots.extend((root, (-root) % Q))

    enumerated_p_roots = [value for value in range(1, Q)
                          if polynomial_p(value) == 0]

    generator = smallest_generator(Q)
    primitive_864_root = pow(generator, (Q - 1) // N, Q)
    primitive_9_root = pow(primitive_864_root, 96, Q)
    assert multiplicative_order(primitive_864_root, Q) == N
    assert multiplicative_order(primitive_9_root, Q) == GT_ROWS

    column_exponents = [exponent for exponent in range(96)
                        if exponent % 6 in (1, 5)]
    assert len(column_exponents) == GT_COLUMNS
    column_lambdas = [pow(primitive_864_root, exponent, Q)
                      for exponent in column_exponents]
    q_roots = [pow(value, GT_ROWS, Q) for value in column_lambdas]

    grid: list[list[int]] = []
    grid_lookup: dict[int, tuple[int, int]] = {}
    for row in range(GT_ROWS):
        row_values: list[int] = []
        eta_power = pow(primitive_9_root, row, Q)
        for column, column_lambda in enumerate(column_lambdas):
            value = column_lambda * eta_power % Q
            assert value not in grid_lookup
            grid_lookup[value] = (row, column)
            row_values.append(value)
        grid.append(row_values)

    legacy_to_grid = [grid_lookup[value] for value in legacy_leaf_roots]
    arithmetic_crt = [
        (64 * row + 225 * column) % POINTS
        for row in range(GT_ROWS)
        for column in range(GT_COLUMNS)
    ]

    preimage_counts = [
        sum(pow(root, GT_ROWS, Q) == q_root for root in enumerated_p_roots)
        for q_root in q_roots
    ]

    checks = {
        "parsed_zeta_count": len(zetas) == POINTS,
        "legacy_leaf_count": len(legacy_leaf_roots) == POINTS,
        "legacy_leaf_unique": len(set(legacy_leaf_roots)) == POINTS,
        "enumerated_p_root_count": len(enumerated_p_roots) == POINTS,
        "legacy_leaf_set_equals_p_roots": (
            set(legacy_leaf_roots) == set(enumerated_p_roots)
        ),
        "q_root_count": len(q_roots) == GT_COLUMNS,
        "q_roots_unique": len(set(q_roots)) == GT_COLUMNS,
        "all_q_roots_satisfy_q": all(polynomial_q(value) == 0
                                      for value in q_roots),
        "nine_preimages_per_q_root": set(preimage_counts) == {GT_ROWS},
        "grid_count": sum(len(row) for row in grid) == POINTS,
        "grid_unique": len(grid_lookup) == POINTS,
        "grid_set_equals_p_roots": set(grid_lookup) == set(enumerated_p_roots),
        "legacy_to_grid_bijection": len(set(legacy_to_grid)) == POINTS,
        "arithmetic_crt_is_permutation": len(set(arithmetic_crt)) == POINTS,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise AssertionError("failed checks: " + ", ".join(failed))

    return {
        "status": "pass",
        "source": str(source),
        "parameters": {
            "q": Q,
            "n": N,
            "leaf_degree": LEAF_DEGREE,
            "points": POINTS,
            "gt_rows": GT_ROWS,
            "gt_columns": GT_COLUMNS,
        },
        "field": {
            "smallest_generator": generator,
            "primitive_864_root": primitive_864_root,
            "primitive_9_root": primitive_9_root,
            "montgomery_r": montgomery_r,
            "montgomery_r_inverse": montgomery_r_inverse,
        },
        "topology": {
            "p_root_count": len(enumerated_p_roots),
            "q_root_count": len(set(q_roots)),
            "preimages_per_q_root": sorted(set(preimage_counts)),
            "column_exponents": column_exponents,
            "legacy_leaf_to_grid_sha256": stable_mapping_hash(legacy_to_grid),
            "legacy_leaf_to_grid_first_16": legacy_to_grid[:16],
        },
        "checks": checks,
        "interpretation": {
            "proved": "the current cubic-leaf roots admit the declared 9-by-32 grid",
            "not_proved": "the forward/inverse GT transform, scaling, ranges, or performance",
        },
    }


def default_source() -> Path:
    repo_root = Path(__file__).resolve().parents[8]
    return repo_root / "ntruplus-ntt-Optimized/Reference_Implementation/NTRU+864/ntt.c"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ntt-source", type=Path, default=default_source())
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    result = prove(args.ntt_source.resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
        return

    print("gt864_root_gate=pass")
    print(f"source={result['source']}")
    for name, passed in result["checks"].items():
        print(f"check,{name}={int(passed)}")
    topology = result["topology"]
    print(f"p_root_count={topology['p_root_count']}")
    print(f"q_root_count={topology['q_root_count']}")
    print(f"preimages_per_q_root={topology['preimages_per_q_root']}")
    print("legacy_leaf_to_grid_sha256="
          f"{topology['legacy_leaf_to_grid_sha256']}")
    print("scope=algebra_only,no_neon,no_benchmark,no_production_change")


if __name__ == "__main__":
    main()
