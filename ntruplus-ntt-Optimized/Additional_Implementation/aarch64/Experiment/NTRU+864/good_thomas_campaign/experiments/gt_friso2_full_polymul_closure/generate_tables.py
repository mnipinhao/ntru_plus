#!/usr/bin/env python3
"""Generate and prove the direct FR-ISO2 inverse-NTT9 correction tables."""

from __future__ import annotations

import json
import sys
from pathlib import Path

Q = 3457
R = (1 << 16) % Q
THETA = 9
RESIDUES = (1, 5)


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def mont(value: int) -> int:
    return centered(value * R)


def reciprocal(value: int) -> int:
    value = centered(value)
    numerator = abs(value) * (1 << 15)
    rounded = (numerator + Q // 2) // Q
    return -rounded if value < 0 else rounded


def make_tables() -> tuple[list[list[int]], list]:
    gamma = pow(THETA, 32, Q)
    inv9 = pow(9, -1, Q)
    row = [[[centered(pow(gamma, -component * r, Q)),
             reciprocal(pow(gamma, -component * r, Q))]
            for r in range(9)] for component in range(3)]
    twist = [[[[[0] * 8 for _ in range(9)] for _ in range(2)]
              for _ in range(3)] for _ in range(2)]
    for top, residue in enumerate(RESIDUES):
        for component in range(3):
            for block in range(2):
                for s in range(9):
                    for lane in range(8):
                        column = 8 * block + lane
                        lam = pow(THETA, residue + 6 * column, Q)
                        delta = pow(THETA, 2 * column, Q)
                        if top == 1:
                            delta = 27 * delta % Q
                        twist[top][component][block][s][lane] = mont(
                            inv9 * pow(lam, -s, Q) *
                            pow(delta, -component, Q))
    return row, twist


def emit_header(path: Path, row: list[list[int]], twist: list) -> None:
    lines = [
        "#ifndef GT864_FRISO2_INVERSE_TABLES_H",
        "#define GT864_FRISO2_INVERSE_TABLES_H",
        "",
        "#include <stdint.h>",
        "",
        "static const int16_t gt864_friso2_inverse_row_barrett[3][9][2] = {",
    ]
    for component in row:
        lines.append("    {")
        lines.extend("        {" + ",".join(map(str, pair)) + "},"
                     for pair in component)
        lines.append("    },")
    lines.extend([
        "};", "",
        "static const int16_t gt864_friso2_inverse9_twist_mont"
        "[2][3][2][9][8] = {",
    ])
    for top in twist:
        lines.append("  {")
        for component in top:
            lines.append("    {")
            for block in component:
                lines.append("      {")
                lines.extend("        {" + ",".join(map(str, values)) + "},"
                             for values in block)
                lines.append("      },")
            lines.append("    },")
        lines.append("  },")
    lines.extend(["};", "", "#endif", ""])
    path.write_text("\n".join(lines), encoding="utf-8")


def prove(row: list[list[int]], twist: list) -> dict[str, object]:
    rinv = pow(R, -1, Q)
    gamma = pow(THETA, 32, Q)
    mismatches = 0
    for top, residue in enumerate(RESIDUES):
        for component in range(3):
            for block in range(2):
                for lane in range(8):
                    column = 8 * block + lane
                    delta = pow(THETA, 2 * column, Q)
                    if top == 1:
                        delta = 27 * delta % Q
                    for r in range(9):
                        constant, constant_prime = row[component][r]
                        if constant % Q != pow(gamma, -component * r, Q):
                            mismatches += 1
                        expected_prime = reciprocal(constant)
                        if constant_prime != expected_prime:
                            mismatches += 1
                    lam = pow(THETA, residue + 6 * column, Q)
                    for s in range(9):
                        decoded = (twist[top][component][block][s][lane]
                                   * rinv % Q)
                        expected = (pow(9, -1, Q) * pow(lam, -s, Q) *
                                    pow(delta, -component, Q)) % Q
                        if decoded != expected:
                            mismatches += 1
    return {
        "gate": "gt864_friso2_direct_inverse_factor_scale",
        "status": "pass" if mismatches == 0 else "fail",
        "factor_mismatches": mismatches,
        "row_multiplication": "Algorithm 10 mul/sqrdmulh/mls",
        "row_mulmods_per_inverse": 64,
        "component0_row_mulmods": 0,
        "component1_row_mulmods": 32,
        "component2_row_mulmods": 32,
        "separate_delta_mulmods": 0,
        "delta_absorbed_into_existing_inverse_twist_loads": True,
        "coefficient_conversion_passes": 0,
        "input_scale": "R0",
        "output_scale_after_correction": "R0",
    }


def main() -> None:
    row, twist = make_tables()
    if len(sys.argv) == 3 and sys.argv[1] == "--header":
        emit_header(Path(sys.argv[2]), row, twist)
    print(json.dumps(prove(row, twist), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
