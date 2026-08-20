#!/usr/bin/env python3
"""Derive GT-logical distance-8 constants from current scalar/AVX2 NTT tables."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

QINV = 12929


def signed16(value: int) -> int:
    return ((value + 32768) % 65536) - 32768


def c_array(text: str, declaration: str) -> list[int]:
    begin = text.index(declaration)
    opening = text.index("{", begin)
    closing = text.index("};", opening)
    return [int(value) for value in re.findall(r"(?<![A-Za-z_])-?\d+", text[opening + 1:closing])]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", type=Path, required=True)
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    experiment = Path(__file__).resolve().parents[1]
    repo = experiment.parents[5]
    scalar_path = repo / "ntruplus-ntt-Optimized" / "Reference_Implementation" / "NTRU+1152" / "ntt.c"
    avx_path = experiment / "upstream" / "supercop-avx2" / "consts.c"
    scalar = c_array(scalar_path.read_text(encoding="utf-8"), "const int16_t zetas[288]")
    expanded = c_array(avx_path.read_text(encoding="utf-8"), "const int16_t zetas[1232]")
    stage = scalar[18:36]
    if len(stage) != 18:
        raise SystemExit("failed to extract 18 scalar distance-8 twiddles")

    # AVX2 consumes 64 int16 entries before level3. Each 256-byte block then
    # stores two 8-lane qinv constants followed by two 8-lane zeta constants.
    for index, zeta in enumerate(stage):
        block, half = divmod(index, 2)
        qinv_start = 64 + 32 * block + 16 + 8 * half
        zeta_start = 64 + 32 * block + 32 + 8 * half
        expected_qinv = signed16(zeta * QINV)
        if expanded[qinv_start:qinv_start + 8] != [expected_qinv] * 8:
            raise SystemExit(f"expanded qinv mismatch at scalar zeta index {18 + index}")
        if expanded[zeta_start:zeta_start + 8] != [zeta] * 8:
            raise SystemExit(f"expanded zeta mismatch at scalar zeta index {18 + index}")

    tables = []
    for branch in range(2):
        branch_table = []
        for logical_row in range(9):
            physical_row = (5 * logical_row) % 9
            scalar_index = 18 + branch * 9 + physical_row
            zeta = scalar[scalar_index]
            global_row = branch * 9 + physical_row
            branch_table.append({
                "logical_row": logical_row,
                "physical_h_row": physical_row,
                "scalar_zetas_index": scalar_index,
                "zeta_montgomery": zeta,
                "zeta_qinv_signed16": signed16(zeta * QINV),
                "distance4": [scalar[36 + 2 * global_row + group] for group in range(2)],
                "distance2": [scalar[72 + 4 * global_row + group] for group in range(4)],
                "distance1": [scalar[144 + 8 * global_row + group] for group in range(8)],
            })
        tables.append(branch_table)
    document = {
        "parameter": 1152,
        "q": 3457,
        "qinv_mod_2_16": QINV,
        "source_scalar": str(scalar_path.relative_to(repo)),
        "source_avx2": str(avx_path.relative_to(repo)),
        "stage": "first radix-2 layer; coefficient step 32 / component distance 8",
        "status": "source-derived-ntt16-test-table-not-yet-full-gt-qualified",
        "branches": tables,
    }
    json_text = json.dumps(document, indent=2, sort_keys=True) + "\n"
    zetas = [[entry["zeta_montgomery"] for entry in branch] for branch in tables]
    qinvs = [[entry["zeta_qinv_signed16"] for entry in branch] for branch in tables]
    stage4 = [[[entry["distance4"][group] for group in range(2)] for entry in branch]
              for branch in tables]
    stage2 = [[[entry["distance2"][group] for group in range(4)] for entry in branch]
              for branch in tables]
    stage1 = [[[entry["distance1"][group] for group in range(8)] for entry in branch]
              for branch in tables]

    def format_3d(name: str, values: list[list[list[int]]], width: int) -> str:
        branches = []
        for branch in values:
            rows = ["    {" + ", ".join(str(value) for value in row) + "}" for row in branch]
            branches.append("  {\n" + ",\n".join(rows) + "\n  }")
        return f"static const int16_t {name}[2][9][{width}] = {{\n" + ",\n".join(branches) + "\n};\n"

    stage4_qinv = [[[signed16(value * QINV) for value in row] for row in branch] for branch in stage4]
    stage2_qinv = [[[signed16(value * QINV) for value in row] for row in branch] for branch in stage2]
    stage1_qinv = [[[signed16(value * QINV) for value in row] for row in branch] for branch in stage1]
    header_text = """#ifndef NTRUPLUS1152_EXP001_STAGE8_TABLES_H
#define NTRUPLUS1152_EXP001_STAGE8_TABLES_H

#include <stdint.h>

/* Generated from current scalar and pinned AVX2 tables; do not hand-edit. */
static const int16_t ntruplus1152_exp001_stage8_zeta[2][9] = {
  {%s},
  {%s}
};
static const int16_t ntruplus1152_exp001_stage8_qinv[2][9] = {
  {%s},
  {%s}
};

""" % tuple(", ".join(str(value) for value in row) for row in (*zetas, *qinvs))
    header_text += format_3d("ntruplus1152_exp001_stage4_zeta", stage4, 2)
    header_text += format_3d("ntruplus1152_exp001_stage4_qinv", stage4_qinv, 2)
    header_text += format_3d("ntruplus1152_exp001_stage2_zeta", stage2, 4)
    header_text += format_3d("ntruplus1152_exp001_stage2_qinv", stage2_qinv, 4)
    header_text += format_3d("ntruplus1152_exp001_stage1_zeta", stage1, 8)
    header_text += format_3d("ntruplus1152_exp001_stage1_qinv", stage1_qinv, 8)
    header_text += "\n#endif\n"
    if args.check:
        if (not args.json.is_file() or args.json.read_text(encoding="utf-8") != json_text or
                not args.header.is_file() or args.header.read_text(encoding="utf-8") != header_text):
            raise SystemExit("generated stage8 tables are stale")
        return 0
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.header.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(json_text, encoding="utf-8")
    args.header.write_text(header_text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
