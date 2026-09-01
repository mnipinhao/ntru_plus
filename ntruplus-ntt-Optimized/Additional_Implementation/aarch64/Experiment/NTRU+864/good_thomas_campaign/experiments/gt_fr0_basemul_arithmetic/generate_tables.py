#!/usr/bin/env python3
"""Generate FR-0 zetas and the exact legacy leaf permutation."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

Q = 3457
R = (1 << 16) % Q
THETA = 9


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def reference_legacy_zetas(path: Path) -> list[int]:
    text = path.read_text()
    match = re.search(
        r"const\s+int16_t\s+zetas\s*\[\s*288\s*\]\s*=\s*\{(.*?)\};",
        text, re.S)
    assert match
    values = [int(x) for x in re.findall(r"-?\d+", match.group(1))]
    assert len(values) == 288
    leaf_half = values[144:]
    result = []
    for value in leaf_half:
        result.extend((value, -value))
    assert len(result) == 288
    return result


def emit_header(path: Path, zetas: list[list[int]],
                physical_to_legacy: list[int], legacy_zetas: list[int]) -> None:
    lines = [
        "#ifndef GT864_FR0_BASEMUL_TABLES_H",
        "#define GT864_FR0_BASEMUL_TABLES_H",
        "",
        "#include <stdint.h>",
        "",
        "static const int16_t gt864_fr0_zetas_mul[36][8] = {",
    ]
    lines.extend("    {" + ",".join(map(str, row)) + "}," for row in zetas)
    lines.extend(["};", "", "static const uint16_t gt864_fr0_physical_to_legacy[288] = {"])
    for start in range(0, 288, 16):
        lines.append("    " + ",".join(map(str, physical_to_legacy[start:start + 16])) + ",")
    lines.extend(["};", "", "static const int16_t gt864_legacy_zetas_mul[288] = {"])
    for start in range(0, 288, 16):
        lines.append("    " + ",".join(map(str, legacy_zetas[start:start + 16])) + ",")
    lines.extend(["};", "", "#endif", ""])
    path.write_text("\n".join(lines))


def main() -> None:
    repo = Path(__file__).resolve().parents[8]
    reference = repo / "ntruplus-ntt-Optimized/Reference_Implementation/NTRU+864/ntt.c"
    legacy_zetas = reference_legacy_zetas(reference)
    rinv = pow(R, -1, Q)
    legacy_normal = [value * rinv % Q for value in legacy_zetas]
    root_to_legacy = {root: leaf for leaf, root in enumerate(legacy_normal)}
    assert len(root_to_legacy) == 288

    zetas = [[0] * 8 for _ in range(36)]
    physical_to_legacy = [-1] * 288
    rows = []
    for top, residue in enumerate((1, 5)):
        for row in range(9):
            for column in range(16):
                group = top * 18 + row * 2 + column // 8
                lane = column % 8
                physical = group * 8 + lane
                exponent = residue + 6 * column + 96 * row
                root = pow(THETA, exponent, Q)
                zetas[group][lane] = centered(root * R)
                physical_to_legacy[physical] = root_to_legacy[root]
                rows.append((physical, root_to_legacy[root], top, row,
                             column, exponent, root))

    assert sorted(physical_to_legacy) == list(range(288))
    for physical, legacy in enumerate(physical_to_legacy):
        assert zetas[physical // 8][physical % 8] == legacy_zetas[legacy]

    if len(sys.argv) == 3 and sys.argv[1] == "--header":
        emit_header(Path(sys.argv[2]), zetas, physical_to_legacy,
                    legacy_zetas)

    mapping = "\n".join(",".join(map(str, row)) for row in rows)
    constants = ",".join(str(x) for row in zetas for x in row)
    print(json.dumps({
        "gate": "gt864_fr0_basemul_table_map",
        "status": "pass",
        "physical_leaf_count": 288,
        "legacy_permutation_bijective": True,
        "physical_zeta_equals_mapped_legacy_zeta": True,
        "mapping_sha256": hashlib.sha256(mapping.encode()).hexdigest(),
        "zetas_sha256": hashlib.sha256(constants.encode()).hexdigest(),
        "production_linked": False,
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
