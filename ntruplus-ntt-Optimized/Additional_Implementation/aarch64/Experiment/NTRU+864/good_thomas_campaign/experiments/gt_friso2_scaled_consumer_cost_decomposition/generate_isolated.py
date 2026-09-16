#!/usr/bin/env python3
"""Generate benchmark-only isolated M5R-D/CF5-B bank functions."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
M5RD = ROOT.parent / "gt_forward_level2_one_mul_b3/gt864_forward_six_bank_all_one_mul_b3.S"
CF5B = ROOT.parent / "gt_friso2_code_size_faithful_forward/gt864_forward_six_bank_cf5b.S"
BUILD = ROOT / "build"
ASM = BUILD / "isolated-banks.S"
HEADER = BUILD / "bank_offsets.h"
CASES = ((0, 1, "t0c1"), (0, 2, "t0c2"), (1, 1, "t1c1"), (1, 2, "t1c2"))


def case_section(text: str, top: int, component: int) -> str:
    marker = f"    // top={top}, component={component}, bank={3 * top + component}\n"
    start = text.index(marker)
    end = text.find("    // top=", start + len(marker))
    if end < 0:
        end = text.index("    mov x30, x16", start)
    return text[start:end]


def setup(text: str, function: str) -> str:
    alias = f"_{function}:\n"
    start = text.index(alias) + len(alias)
    end = text.index("    // top=0, component=0, bank=0")
    return text[start:end]


def unit(kind: str, case: str, top: int, component: int, source: str) -> str:
    original_function = ("gt864_forward_six_bank_pass2_all_one_mul_b3"
                         if kind == "base" else "gt864_forward_six_bank_pass2_cf5b")
    symbol = f"gt864_cf5c_{kind}_{case}"
    common = source.index(".Lgt864_m5rd_common:")
    if kind == "base":
        helper_start = source.index(".Lgt864_m5rd_one_bank:")
    else:
        helper_start = source.index(".Lgt864_cf5_shared_producer:")
    helper = source[helper_start:common]
    data = source[common:]
    body = [".text", ".p2align 2", f".global {symbol}", f"{symbol}:",
            setup(source, original_function).rstrip(),
            case_section(source, top, component).rstrip(),
            "    mov x30, x16", "    ret", helper.rstrip(), data.rstrip()]
    result = "\n".join(body) + "\n"
    result = result.replace(".Lgt864_", f".Lcf5c_{kind}_{case}_")
    result = result.replace(f"{original_function}_end",
                            f"gt864_cf5c_{kind}_{case}_body_end")
    return result


def offsets(text: str, top: int, component: int) -> list[int]:
    section = case_section(text, top, component)
    byte_offsets = [int(value) for value in re.findall(
        r"(?m)^    str q(?:[0-9]|[12][0-9]|3[01]), \[x6, #([0-9]+)\]$", section)]
    assert len(byte_offsets) == 18
    return [byte // 2 + lane for byte in byte_offsets for lane in range(8)]


def main() -> None:
    BUILD.mkdir(exist_ok=True)
    base = M5RD.read_text(encoding="utf-8")
    cand = CF5B.read_text(encoding="utf-8")
    chunks = ["/* Generated benchmark-only CF5-C isolated banks. */"]
    rows = []
    for top, component, case in CASES:
        assert offsets(base, top, component) == offsets(cand, top, component)
        rows.append(offsets(cand, top, component))
        chunks.append(unit("base", case, top, component, base))
        chunks.append(unit("cand", case, top, component, cand))
    ASM.write_text("\n".join(chunks), encoding="utf-8")
    lines = ["#ifndef GT864_CF5C_BANK_OFFSETS_H",
             "#define GT864_CF5C_BANK_OFFSETS_H",
             "static const unsigned gt864_cf5c_bank_indices[4][144] = {"]
    for row in rows:
        lines.append("    {" + ",".join(map(str, row)) + "},")
    lines.extend(["};", "#endif"])
    HEADER.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"generated_functions={2 * len(CASES)}")
    print("generated_case_indices=4x144")


if __name__ == "__main__":
    main()
