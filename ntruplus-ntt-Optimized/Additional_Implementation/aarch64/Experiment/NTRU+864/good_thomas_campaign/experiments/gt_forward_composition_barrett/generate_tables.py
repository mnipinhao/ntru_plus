#!/usr/bin/env python3
"""Generate compile-time fixed-Barrett tables for fused GT864 Forward."""

from __future__ import annotations

import sys
from pathlib import Path

Q = 3457
THETA = 9
RESIDUES = (1, 5)


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def reciprocal(value: int) -> int:
    numerator = abs(value) * (1 << 15)
    rounded = (numerator + Q // 2) // Q
    return -rounded if value < 0 else rounded


def pair(value: int) -> tuple[int, int]:
    normal = centered(value)
    return normal, reciprocal(normal)


def emit(path: Path) -> None:
    omega16 = pow(THETA, 54, Q)
    eta = pow(THETA, 96, Q)
    rho = pow(eta, 3, Q)
    lines = [
        "#ifndef GT864_FORWARD_BARRETT_TABLES_H",
        "#define GT864_FORWARD_BARRETT_TABLES_H",
        "#include <stdint.h>",
        "typedef struct { int16_t b, bprime; } gt864_barrett_pair;",
        f"static const gt864_barrett_pair gt864_barrett_one = {{{pair(1)[0]},{pair(1)[1]}}};",
        f"static const gt864_barrett_pair gt864_barrett_rho = {{{pair(rho)[0]},{pair(rho)[1]}}};",
        f"static const gt864_barrett_pair gt864_barrett_rho2 = {{{pair(pow(rho, 2, Q))[0]},{pair(pow(rho, 2, Q))[1]}}};",
        f"static const gt864_barrett_pair gt864_barrett_eta = {{{pair(eta)[0]},{pair(eta)[1]}}};",
        f"static const gt864_barrett_pair gt864_barrett_eta_inv = {{{pair(pow(eta, -1, Q))[0]},{pair(pow(eta, -1, Q))[1]}}};",
        "static const gt864_barrett_pair gt864_forward16_twist[2][16] = {",
    ]
    for residue in RESIDUES:
        values = [pair(pow(THETA, 9 * residue * t, Q)) for t in range(16)]
        lines.append("  {" + ",".join(f"{{{b},{bp}}}" for b, bp in values) + "},")
    lines.extend(["};", "static const gt864_barrett_pair gt864_forward16_stage[4][8] = {"])
    for length in (2, 4, 8, 16):
        values = [pair(pow(omega16, j * 16 // length, Q))
                  for j in range(length // 2)]
        values.extend([(0, 0)] * (8 - len(values)))
        lines.append("  {" + ",".join(f"{{{b},{bp}}}" for b, bp in values) + "},")
    lines.extend(["};", "static const gt864_barrett_pair gt864_forward9_twist[2][2][9][8] = {"])
    for residue in RESIDUES:
        lines.append("  {")
        for block in range(2):
            lines.append("    {")
            for s in range(9):
                values = [pair(pow(THETA, (residue + 6 * (8 * block + lane)) * s, Q))
                          for lane in range(8)]
                lines.append("      {" + ",".join(f"{{{b},{bp}}}" for b, bp in values) + "},")
            lines.append("    },")
        lines.append("  },")
    lines.extend(["};", "#endif", ""])
    path.write_text("\n".join(lines))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: generate_tables.py OUTPUT")
    emit(Path(sys.argv[1]))
