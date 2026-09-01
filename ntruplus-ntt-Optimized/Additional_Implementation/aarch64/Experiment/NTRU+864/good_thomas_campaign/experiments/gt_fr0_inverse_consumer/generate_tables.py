#!/usr/bin/env python3
"""Generate inverse FR-0/P8 tables and prove their coordinate closure."""

from __future__ import annotations

import hashlib
import json
import re
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


def reference_legacy_zetas(path: Path) -> list[int]:
    text = path.read_text()
    match = re.search(
        r"const\s+int16_t\s+zetas\s*\[\s*288\s*\]\s*=\s*\{(.*?)\};",
        text, re.S)
    assert match
    values = [int(x) for x in re.findall(r"-?\d+", match.group(1))]
    assert len(values) == 288
    out = []
    for value in values[144:]:
        out.extend((value, -value))
    return out


def make_tables(reference: Path) -> dict[str, object]:
    inv9 = pow(9, -1, Q)
    inv16 = pow(16, -1, Q)
    eta = pow(THETA, 96, Q)
    omega16 = pow(THETA, 54, Q)
    alpha = (-722) % Q
    beta = (1 - alpha) % Q
    delta_inv = pow((beta - alpha) % Q, -1, Q)

    inverse9 = [[[[0] * 8 for _ in range(9)] for _ in range(2)]
                for _ in range(2)]
    for top, residue in enumerate(RESIDUES):
        for block in range(2):
            for s in range(9):
                for lane in range(8):
                    column = 8 * block + lane
                    lam = pow(THETA, residue + 6 * column, Q)
                    inverse9[top][block][s][lane] = mont(
                        inv9 * pow(lam, -s, Q))

    inverse16_stage = [[0] * 8 for _ in range(4)]
    for stage, length in enumerate((2, 4, 8, 16)):
        for j in range(length // 2):
            inverse16_stage[stage][j] = mont(
                pow(omega16, -(j * 16 // length), Q))

    inverse16_main_scale = [[0] * 8 for _ in range(16)]
    inverse16_tail_scale = [[0] * 8 for _ in range(16)]
    for t in range(16):
        scales = [mont(inv16 * pow(pow(THETA, 9 * residue, Q), -t, Q))
                  for residue in RESIDUES]
        inverse16_main_scale[t] = [scales[0]] * 4 + [scales[1]] * 4
        inverse16_tail_scale[t] = [scales[0]] * 3 + [scales[1]] * 3 + [0, 0]

    legacy = reference_legacy_zetas(reference)
    rinv = pow(R, -1, Q)
    root_to_legacy = {(value * rinv) % Q: leaf
                      for leaf, value in enumerate(legacy)}
    physical_to_legacy = [-1] * 288
    rows = []
    for top, residue in enumerate(RESIDUES):
        for row in range(9):
            for column in range(16):
                physical = (top * 18 + row * 2 + column // 8) * 8 + column % 8
                root = pow(THETA, residue + 6 * column + 96 * row, Q)
                physical_to_legacy[physical] = root_to_legacy[root]
                rows.append((physical, root_to_legacy[root], top, row, column))
    assert sorted(physical_to_legacy) == list(range(288))

    return {
        "inverse9": inverse9,
        "inverse16_stage": inverse16_stage,
        "inverse16_main_scale": inverse16_main_scale,
        "inverse16_tail_scale": inverse16_tail_scale,
        "alpha_mont": mont(alpha),
        "delta_inv_mont": mont(delta_inv),
        "physical_to_legacy": physical_to_legacy,
        "rows": rows,
        "eta_inverse_identity": pow(eta, -1, Q),
    }


def emit_2d(lines: list[str], name: str, values: list[list[int]]) -> None:
    lines.append(f"static const int16_t {name}[{len(values)}][8] = {{")
    lines.extend("    {" + ",".join(map(str, row)) + "}," for row in values)
    lines.extend(["};", ""])


def emit_header(path: Path, tables: dict[str, object]) -> None:
    lines = [
        "#ifndef GT864_FR0_INVERSE_TABLES_H",
        "#define GT864_FR0_INVERSE_TABLES_H",
        "",
        "#include <stdint.h>",
        "",
        f"#define GT864_ALPHA_MONT ({tables['alpha_mont']})",
        f"#define GT864_DELTA_INV_MONT ({tables['delta_inv_mont']})",
        "#define GT864_R_MONT (-147)",
        "#define GT864_RHO_MONT (-886)",
        "#define GT864_RHO2_MONT (1033)",
        "#define GT864_ETA_MONT (708)",
        "#define GT864_ETA_INV_MONT (1510)",
        "",
        "static const int16_t gt864_inverse9_twist_mont[2][2][9][8] = {",
    ]
    inverse9 = tables["inverse9"]
    for top in inverse9:
        lines.append("  {")
        for block in top:
            lines.append("    {")
            lines.extend("      {" + ",".join(map(str, row)) + "}," for row in block)
            lines.append("    },")
        lines.append("  },")
    lines.extend(["};", ""])
    emit_2d(lines, "gt864_inverse16_stage_twiddle_mont",
            tables["inverse16_stage"])
    emit_2d(lines, "gt864_inverse16_main_scale_mont",
            tables["inverse16_main_scale"])
    emit_2d(lines, "gt864_inverse16_tail_scale_mont",
            tables["inverse16_tail_scale"])
    lines.append("static const uint16_t gt864_inverse_physical_to_legacy[288] = {")
    mapping = tables["physical_to_legacy"]
    for start in range(0, 288, 16):
        lines.append("    " + ",".join(map(str, mapping[start:start + 16])) + ",")
    lines.extend(["};", "", "#endif", ""])
    path.write_text("\n".join(lines))


def main() -> None:
    repo = Path(__file__).resolve().parents[8]
    reference = repo / "ntruplus-ntt-Optimized/Reference_Implementation/NTRU+864/ntt.c"
    tables = make_tables(reference)
    if len(sys.argv) == 3 and sys.argv[1] == "--header":
        emit_header(Path(sys.argv[2]), tables)

    map_text = "\n".join(",".join(map(str, row)) for row in tables["rows"])
    constants = json.dumps({k: v for k, v in tables.items()
                            if k not in ("rows", "physical_to_legacy")},
                           sort_keys=True)
    print(json.dumps({
        "gate": "gt864_fr0_inverse_coordinate_map",
        "status": "pass",
        "physical_leaf_count": 288,
        "physical_to_legacy_bijective": True,
        "inverse9_formula": "inv9*lambda_c^-s*sum_r(eta^-rs*F_r,c)",
        "inverse16_formula": "inv16*zeta_top^-t*sum_c(omega16^-ct*U_s,c)",
        "top_recombine_formula": "high=(beta-alpha)^-1*(B-A); low=A-alpha*high",
        "mapping_sha256": hashlib.sha256(map_text.encode()).hexdigest(),
        "constants_sha256": hashlib.sha256(constants.encode()).hexdigest(),
        "production_linked": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
