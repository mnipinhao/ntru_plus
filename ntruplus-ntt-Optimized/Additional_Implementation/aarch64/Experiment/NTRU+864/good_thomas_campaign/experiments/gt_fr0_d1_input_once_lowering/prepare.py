#!/usr/bin/env python3
"""Derive P3B7 lowering variants from the generated P3B6 control."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
P3B6 = HERE.parent / "gt_fr0_d1_input_once_tobytes"
CONTROL = P3B6 / "build/input_once_tobytes.c"


def l1_source(source: str, symbol: str) -> str:
    old = " return vaddq_s16(x,vandq_s16(vshrq_n_s16(x,15),q));"
    new = (" int16x8_t mask;\n"
           " __asm__ volatile(\"sshr %0.8h,%1.8h,#15\\n\\t\"\n"
           "                  \"mls %1.8h,%0.8h,%2.8h\"\n"
           "                  : \"=&w\"(mask),\"+w\"(x) : \"w\"(q));\n"
           " return x;")
    assert source.count(old) == 1
    result = source.replace('#include "input_once_tobytes.h"',
                            '#include "lowered_tobytes.h"')
    result = result.replace(old, new)
    result = result.replace("gt864_fr0_input_once_tobytes", symbol)
    return result


def add_l2(source: str) -> str:
    lines = source.splitlines()
    result: list[str] = []
    index = 0
    replacements = 0
    while index < len(lines):
        match = re.fullmatch(r" o([0-9]+)=vdupq_n_s16\(0\);", lines[index])
        if match:
            slot = match.group(1)
            assert index + 1 < len(lines)
            insert = re.fullmatch(
                rf" o{slot}=vsetq_lane_s16\(vgetq_lane_s16\(x,([0-7])\),"
                rf"o{slot},([0-7])\);", lines[index + 1])
            assert insert
            source_lane = insert.group(1)
            result.append(
                f' __asm__ volatile("dup %0.8h,%1.h[{source_lane}]" : '
                f'"=w"(o{slot}) : "w"(x));')
            replacements += 1
            index += 2
            continue
        result.append(lines[index])
        index += 1
    assert replacements == 54
    return "\n".join(result) + "\n"


def main() -> None:
    subprocess.check_call(["python3", "prepare.py"], cwd=P3B6)
    source = CONTROL.read_text(encoding="utf-8")
    l1 = l1_source(source, "gt864_fr0_input_once_l1_tobytes")
    l12 = add_l2(l1.replace("gt864_fr0_input_once_l1_tobytes",
                            "gt864_fr0_input_once_l12_tobytes"))
    build = HERE / "build"
    build.mkdir(exist_ok=True)
    (build / "l1_tobytes.c").write_text(l1, encoding="utf-8")
    (build / "l12_tobytes.c").write_text(l12, encoding="utf-8")
    print("p3b7_generated l1_sign_corrections=54 l12_first_lane_dups=54")


if __name__ == "__main__":
    main()
