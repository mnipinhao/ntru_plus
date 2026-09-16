#!/usr/bin/env python3
"""Derive P3B8 direct-immediate input loads from P3B6."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
P3B6 = HERE.parent / "gt_fr0_d1_input_once_tobytes"
CONTROL = P3B6 / "build/input_once_tobytes.c"


def main() -> None:
    subprocess.check_call(["python3", "prepare.py"], cwd=P3B6)
    source = CONTROL.read_text(encoding="utf-8")
    source = source.replace('#include "input_once_tobytes.h"',
                            '#include "direct_address_tobytes.h"')
    source = source.replace("gt864_fr0_input_once_tobytes",
                            "gt864_fr0_input_once_direct_address_tobytes")
    pattern = re.compile(
        r' __asm__ volatile\("ldr %q0, \[%1\]" : "=w"\(x\) : '
        r'"r"\(in\+([0-9]+)\) : "memory"\);')

    def direct(match: re.Match[str]) -> str:
        byte_offset = 2 * int(match.group(1))
        assert byte_offset % 16 == 0 and 0 <= byte_offset <= 65520
        return (f' __asm__ volatile("ldr %q0, [%1, #{byte_offset}]" : '
                f'"=w"(x) : "r"(in) : "memory");')

    source, count = pattern.subn(direct, source)
    assert count == 54
    build = HERE / "build"
    build.mkdir(exist_ok=True)
    (build / "direct_address_tobytes.c").write_text(source, encoding="utf-8")
    print("p3b8_generated direct_immediate_loads=54")


if __name__ == "__main__":
    main()
