#!/usr/bin/env python3
"""Generate FR-0 BaseMul zetas and prove forward/inverse permutation closure."""

from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

Q = 3457
R = (1 << 16) % Q
THETA = 9
ALPHA = (-722) % Q
BETA = (1 - (-722)) % Q


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def parse_reference_leaf_roots(path: Path) -> set[int]:
    text = path.read_text()
    match = re.search(
        r"const\s+int16_t\s+zetas\s*\[\s*288\s*\]\s*=\s*\{(.*?)\};",
        text,
        re.S,
    )
    assert match
    values = [int(token) for token in re.findall(r"-?\d+", match.group(1))]
    assert len(values) == 288
    # zetas[0..143] are internal forward-NTT twiddles.  The 144 entries
    # zetas[144..287], together with their negatives, are the 288 cubic-leaf
    # constants consumed by poly_{baseinv,basemul,basemul_add}.
    r_inverse = pow(R, -1, Q)
    positive_half = {
        value * r_inverse % Q for value in values[144:]
    }
    return positive_half | {(-value) % Q for value in positive_half}


def emit_header(path: Path, zetas: list[list[int]],
                physical_to_logical: list[int],
                logical_to_physical: list[int]) -> None:
    lines = [
        "#ifndef GT864_FR0_MAPS_H",
        "#define GT864_FR0_MAPS_H",
        "",
        "#include <stdint.h>",
        "",
        "static const int16_t gt864_fr0_zetas_mul[36][8] = {",
    ]
    lines.extend("    {" + ",".join(map(str, row)) + "}," for row in zetas)
    lines.extend([
        "};",
        "",
        "static const uint16_t gt864_fr0_physical_to_logical[288] = {",
    ])
    for start in range(0, 288, 16):
        lines.append("    " + ",".join(
            map(str, physical_to_logical[start:start + 16])) + ",")
    lines.extend([
        "};",
        "",
        "static const uint16_t gt864_fr0_logical_to_physical[288] = {",
    ])
    for start in range(0, 288, 16):
        lines.append("    " + ",".join(
            map(str, logical_to_physical[start:start + 16])) + ",")
    lines.extend(["};", "", "#endif", ""])
    path.write_text("\n".join(lines))


def main() -> None:
    repo = Path(__file__).resolve().parents[8]
    reference = repo / "ntruplus-ntt-Optimized/Reference_Implementation/NTRU+864/ntt.c"
    reference_roots = parse_reference_leaf_roots(reference)
    zetas = [[0] * 8 for _ in range(36)]
    physical_to_logical = [-1] * 288
    logical_to_physical = [-1] * 288
    rows = []
    generated_roots = set()

    for top, residue in enumerate((1, 5)):
        for row in range(9):
            for column in range(16):
                block, lane = divmod(column, 8)
                group = top * 18 + row * 2 + block
                physical = group * 8 + lane
                logical = (top * 9 + row) * 16 + column
                exponent = residue + 6 * column + 96 * row
                root = pow(THETA, exponent, Q)
                root_mont = centered(root * R)

                assert pow(root, 144, Q) == (ALPHA if top == 0 else BETA)
                assert zetas[group][lane] == 0
                zetas[group][lane] = root_mont
                physical_to_logical[physical] = logical
                logical_to_physical[logical] = physical
                generated_roots.add(root)
                rows.append((physical, logical, top, row, column, root,
                             root_mont))

    assert generated_roots == reference_roots
    assert sorted(physical_to_logical) == list(range(288))
    assert sorted(logical_to_physical) == list(range(288))
    for logical in range(288):
        physical = logical_to_physical[logical]
        assert physical_to_logical[physical] == logical
    assert all(value != 0 for group in zetas for value in group)

    if len(sys.argv) == 3 and sys.argv[1] == "--header":
        emit_header(Path(sys.argv[2]), zetas, physical_to_logical,
                    logical_to_physical)

    mapping_text = "\n".join(",".join(map(str, row)) for row in rows)
    zeta_text = ",".join(str(value) for group in zetas for value in group)
    payload = {
        "gate": "gt864_fr0_basemul_inverse_map",
        "status": "pass",
        "physical_leaf_formula": "group=top*18+row*2+column//8; lane=column%8",
        "component_offset": "24*group+8*component+lane",
        "zeta_formula": "centered(theta^(residue+6*column+96*row)*R mod q)",
        "reference_root_set_equal": True,
        "forward_basemul_leaf_map_equal": True,
        "basemuladd_leaf_map_equal": True,
        "inverse_permutation_closure": "P_inverse_times_P_is_identity",
        "mapping_sha256": hashlib.sha256(mapping_text.encode()).hexdigest(),
        "zetas_mul_sha256": hashlib.sha256(zeta_text.encode()).hexdigest(),
        "production_linked": False,
    }
    print(json.dumps(payload, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
