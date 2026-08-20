#!/usr/bin/env python3
"""Generate GT forward constants and an offline Official component oracle."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

Q = 3457
QINV = 12929
R = pow(2, 16, Q)
RINV = pow(R, -1, Q)
GENERATOR = 7
ROOT144_EXPONENT = 24
BRANCH_OFFSETS = (20, 4)


def signed16(value: int) -> int:
    value %= 65536
    return value - 65536 if value >= 32768 else value


def centered(value: int) -> int:
    value %= Q
    return value - Q if value > Q // 2 else value


def montgomery(value: int) -> int:
    return centered(value * R)


def c_array(text: str, declaration: str) -> list[int]:
    begin = text.index(declaration)
    opening = text.index("{", begin)
    closing = text.index("};", opening)
    return [int(value) for value in re.findall(r"(?<![A-Za-z_])-?\d+", text[opening + 1:closing])]


def bit_reverse4(value: int) -> int:
    return int(f"{value:04b}"[::-1], 2)


def ternary_reverse2(value: int) -> int:
    return (value % 3) * 3 + value // 3


def official_branch_transform(source: list[int], branch: int, zetas: list[int], omega: int) -> list[int]:
    values = [value % Q for value in source]
    for distance, groups, start in ((48, 1, 2 + 2 * branch), (16, 3, 6 + 6 * branch)):
        before = values[:]
        for group in range(groups):
            zeta1, zeta2 = zetas[start + 2 * group:start + 2 * group + 2]
            base = 3 * distance * group
            for lane in range(distance):
                index = base + lane
                t1 = zeta1 * before[index + distance] % Q
                t2 = zeta2 * before[index + 2 * distance] % Q
                t3 = omega * (t1 - t2) % Q
                values[index] = (before[index] + t1 + t2) % Q
                values[index + distance] = (before[index] - t2 + t3) % Q
                values[index + 2 * distance] = (before[index] - t1 - t3) % Q
    for distance, start in ((8, 18 + 9 * branch), (4, 36 + 18 * branch),
                            (2, 72 + 36 * branch), (1, 144 + 72 * branch)):
        before = values[:]
        for group in range(144 // (2 * distance)):
            zeta = zetas[start + group]
            base = 2 * distance * group
            for lane in range(distance):
                index = base + lane
                product = zeta * before[index + distance] % Q
                values[index] = (before[index] + product) % Q
                values[index + distance] = (before[index] - product) % Q
    return values


def emit_1d(name: str, values: list[int]) -> str:
    lines = ["  " + ", ".join(str(value) for value in values[i:i + 12])
             for i in range(0, len(values), 12)]
    return f"static const int16_t {name}[{len(values)}] = {{\n" + ",\n".join(lines) + "\n};\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    experiment = Path(__file__).resolve().parents[1]
    repo = experiment.parents[5]
    scalar_path = repo / "ntruplus-ntt-Optimized/Reference_Implementation/NTRU+1152/ntt.c"
    text = scalar_path.read_text(encoding="utf-8")
    layout_path = experiment / "generated/official-avx2-layout-probe.json"
    layout = json.loads(layout_path.read_text(encoding="utf-8"))
    if len(layout.get("positions", [])) != 1152:
        raise SystemExit("Official AVX2 layout probe must contain 1152 positions")
    official_position = {}
    for entry in layout["positions"]:
        key = (entry["terminal_coefficient"], entry["factor_exponent_base_g"])
        if key in official_position:
            raise SystemExit(f"duplicate Official AVX2 layout key {key}")
        official_position[key] = entry["position"]
    zetas_mont = c_array(text, "const int16_t zetas[288]")
    zetas = [(value * RINV) % Q for value in zetas_mont]
    omega = (-886 * RINV) % Q
    logs = {pow(GENERATOR, exponent, Q): exponent for exponent in range(Q - 1)}

    root16 = pow(GENERATOR, ROOT144_EXPONENT * 9, Q)
    root9_relabelled = pow(GENERATOR, ROOT144_EXPONENT * 16 * 5, Q)
    ntt16_twiddles = []
    for distance in (8, 4, 2, 1):
        ntt16_twiddles.append([
            pow(root16, bit_reverse4(group * 2 * distance) * distance, Q)
            for group in range(16 // (2 * distance))
        ])
    ntt9_stage1 = [1, 1]
    ntt9_stage2 = []
    for group in range(3):
        ntt9_stage2.extend((pow(root9_relabelled, group, Q),
                            pow(root9_relabelled, 2 * group, Q)))

    twists = []
    components = []
    for branch, offset in enumerate(BRANCH_OFFSETS):
        twists.append([montgomery(pow(GENERATOR, offset * index, Q)) for index in range(144)])
        impulse0 = official_branch_transform([1] + [0] * 143, branch, zetas, omega)
        impulse1 = official_branch_transform([0, 1] + [0] * 142, branch, zetas, omega)
        if impulse0 != [1] * 144:
            raise SystemExit("Official branch transform failed impulse-zero normalization")
        official_exponents = [logs[value] for value in impulse1]
        if len(set(official_exponents)) != 144 or {value % 24 for value in official_exponents} != {offset}:
            raise SystemExit("Official factor/root extraction failed")
        exponent_to_component = {value: index for index, value in enumerate(official_exponents)}
        branch_components = []
        for row in range(9):
            p = ternary_reverse2(row)
            for lane in range(16):
                q = bit_reverse4(lane)
                k = (64 * p + 9 * q) % 144
                exponent = (offset + ROOT144_EXPONENT * k) % (Q - 1)
                branch_components.append({
                    "branch": branch,
                    "gt_row": row,
                    "ntt9_frequency_p": p,
                    "ntt16_lane": lane,
                    "ntt16_frequency_q": q,
                    "root144_frequency_k": k,
                    "factor_exponent_base_g": exponent,
                    "factor_mod_q": pow(GENERATOR, exponent, Q),
                    "official_component": exponent_to_component[exponent],
                    "official_avx2_positions": [
                        official_position[(coefficient, exponent)] for coefficient in range(4)
                    ],
                })
        components.append(branch_components)

    document = {
        "parameter": 1152,
        "component_degree": 4,
        "q": Q,
        "field_generator": GENERATOR,
        "root144_exponent": ROOT144_EXPONENT,
        "branch_offsets": list(BRANCH_OFFSETS),
        "ntt16_lane_order": "four-bit-reversed; intentionally not canonicalized",
        "ntt9_row_order": "two-trit-reversed; intentionally not canonicalized",
        "source_scalar": str(scalar_path.relative_to(repo)),
        "source_official_avx2_layout": str(layout_path.relative_to(repo)),
        "components": components,
    }
    json_text = json.dumps(document, indent=2, sort_keys=True) + "\n"

    mont_stages = [[montgomery(value) for value in stage] for stage in ntt16_twiddles]
    qinv_stages = [[signed16(value * QINV) for value in stage] for stage in mont_stages]
    ntt9_mont = [montgomery(value) for value in ntt9_stage1 + ntt9_stage2]
    official_map = [[entry["official_component"] for entry in branch] for branch in components]
    official_avx2_map = [[position for entry in branch for position in entry["official_avx2_positions"]]
                         for branch in components]
    header = """#ifndef NTRUPLUS1152_EXP001_FULL_FORWARD_TABLES_H
#define NTRUPLUS1152_EXP001_FULL_FORWARD_TABLES_H

#include <stdint.h>

/* Generated offline; NTT16 lanes and NTT9 rows remain digit-reversed. */
"""
    for branch in range(2):
        header += emit_1d(f"ntruplus1152_exp001_twist_branch{branch}", twists[branch])
    names = ("stage8", "stage4", "stage2", "stage1")
    for name, values, qinvs in zip(names, mont_stages, qinv_stages):
        header += emit_1d(f"ntruplus1152_exp001_gt_{name}_zeta", values)
        header += emit_1d(f"ntruplus1152_exp001_gt_{name}_qinv", qinvs)
    header += emit_1d("ntruplus1152_exp001_ntt9_zeta", ntt9_mont)
    for branch in range(2):
        header += emit_1d(f"ntruplus1152_exp001_official_component_branch{branch}", official_map[branch])
        header += emit_1d(f"ntruplus1152_exp001_official_avx2_position_branch{branch}",
                          official_avx2_map[branch])
    header += "\n#endif\n"

    if args.check:
        if (not args.json.is_file() or args.json.read_text(encoding="utf-8") != json_text or
                not args.header.is_file() or args.header.read_text(encoding="utf-8") != header):
            raise SystemExit("generated full-forward tables are stale")
        return 0
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.header.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json_text, encoding="utf-8")
    args.header.write_text(header, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
