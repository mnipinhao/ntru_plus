#!/usr/bin/env python3
"""Generate the Natural-Q MA2 scale-4 boundary used by direct H1."""

from __future__ import annotations

import argparse
from pathlib import Path

SOURCE_SYMBOL = "ntruplus1152_exp001_f0_ma2_planes_natural_q"
TARGET_SYMBOL = "ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4"
INV4 = "  MA1_MONT_CONST 8,8,.Lma1_inv4,.Lma1_inv4_qinv,11\n"


def write(path: Path, data: str, check: bool) -> None:
    if check:
        if not path.is_file() or path.read_text(encoding="utf-8") != data:
            raise SystemExit(f"generated file is stale: {path}")
    else:
        path.write_text(data, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--asm", type=Path, required=True)
    parser.add_argument("--header", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    text = args.source.read_text(encoding="utf-8")
    start = text.index(f".globl {SOURCE_SYMBOL}")
    end_marker = f".size {SOURCE_SYMBOL}, .-{SOURCE_SYMBOL}\n"
    end = text.index(end_marker, start) + len(end_marker)
    segment = text[start:end]
    if segment.count(INV4) != 72:
        raise SystemExit("Natural-Q MA2 inv4 count changed")
    segment = segment.replace(INV4, "")
    segment = segment.replace(SOURCE_SYMBOL, TARGET_SYMBOL)

    macro_start = text.index(".macro MA1_CENTER")
    macro_end = text.index(f".globl ntruplus1152_exp001_project_h_natural_q")
    macros = text[macro_start:macro_end]
    asm = (
        "/* Generated cumulative Natural-Q MA2 scale-4 boundary. */\n"
        ".intel_syntax noprefix\n.text\n" + macros + segment +
        "\n.section .rodata,\"a\",@progbits\n"
        "#include \"generated/f0-ma2-constants.inc\"\n"
        "#include \"generated/gt9x16-prod3-ma2-qorder-natural-constants.inc\"\n"
        "\n.section .note.GNU-stack,\"\",@progbits\n"
    )
    header = (
        "#ifndef NTRUPLUS1152_EXP001_PROD3_CUMULATIVE_MA2_H\n"
        "#define NTRUPLUS1152_EXP001_PROD3_CUMULATIVE_MA2_H\n"
        "#include <stdint.h>\n"
        f"void {TARGET_SYMBOL}(int16_t out[1152], const int16_t r[1152], "
        "const int16_t m[1152], const int16_t h[1152]);\n"
        "#endif\n"
    )
    write(args.asm, asm, args.check)
    write(args.header, header, args.check)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
