#!/usr/bin/env python3
"""Generate the branch-1 T0 constants for the full persistent-AoS leaf."""
from __future__ import annotations

import argparse
import re
from pathlib import Path


def parse_words(text: str, label: str) -> list[int]:
    match = re.search(rf"^{re.escape(label)}:\n\s+\.short ([^\n]+)$", text,
                      re.MULTILINE)
    if not match:
        raise SystemExit(f"missing input constant {label}")
    values = [int(value) for value in match.group(1).split(",")]
    if len(values) != 16:
        raise SystemExit(f"bad input constant width for {label}")
    return values


def emit_vector(lines: list[str], label: str, values: list[int]) -> None:
    if len(values) != 16:
        raise SystemExit(f"bad generated vector width for {label}")
    lines.extend((".p2align 5", f"{label}:",
                  "  .word " + ", ".join(map(str, values))))


def packed(values: list[int], width: int) -> list[int]:
    return [value for value in values for _ in range(width)]


def write(path: Path, text: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--twist-constants", type=Path, required=True)
    parser.add_argument("--asm-constants", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    source = args.twist_constants.read_text(encoding="utf-8")
    lines = ["/* Generated GT9X16-PROD3-AOS branch-1 T0 constants. */",
             ".section .rodata"]
    for row in range(9):
        zeta = parse_words(source, f".Lf0_prod1_b1_r{row}_twist")
        qinv = parse_words(source, f".Lf0_prod1_b1_r{row}_twist_qinv")
        for block in range(4):
            begin = 4 * block
            emit_vector(lines, f".Lprod3_b1_r{row}_q{block}_twist",
                        packed(zeta[begin:begin + 4], 4))
            emit_vector(lines, f".Lprod3_b1_r{row}_q{block}_twist_qinv",
                        packed(qinv[begin:begin + 4], 4))
    write(args.asm_constants, "\n".join(lines) + "\n", args.check)
    print("GT9X16-PROD3-AOS branch-1 constants passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
