#!/usr/bin/env python3
"""Extract callable T0/T3x3/T2^4 and exact combined-body Official diagnostics."""

from __future__ import annotations

import argparse
from pathlib import Path


PROLOGUE = """vmovdqa _16xq(%rip), %ymm0
vmovdqa _16xv(%rip), %ymm1
lea     zetas(%rip), %rdx
"""


def function(name: str, body: str) -> str:
    return f""".global {name}
.type {name},@function
{name}:
{body.rstrip()}
ret
.size {name}, .-{name}

"""


def render(source: str) -> str:
    entry = source.index("poly_ntt:\n") + len("poly_ntt:\n")
    level1 = source.index("#level 1\n")
    level2 = source.index("#level 2\n")
    level3456 = source.index("lea 2304(%rdi), %r8\n", level2)
    # The first occurrence belongs to level 2; the second starts levels 3--6.
    level3456 = source.index("lea 2304(%rdi), %r8\n", level3456 + 1)
    final_ret = source.index("\nret\n", level3456)

    top = source[entry:level1]
    radix3 = PROLOGUE + source[level1:level3456]
    # level 1 advances zetas by 32 bytes and level 2 by another 96 bytes.
    radix2 = PROLOGUE + "add $128, %rdx\n\n" + source[level3456:final_ret]
    combined = PROLOGUE + source[level1:final_ret].replace("_looptop_", "_combined_looptop_")
    return (
        "/* Generated verbatim from pinned upstream ntt.s; do not hand-edit. */\n"
        ".text\n\n"
        + function("ntruplus1152_exp001_official_t0", top)
        + function("ntruplus1152_exp001_official_t3x3", radix3)
        + function("ntruplus1152_exp001_official_t2x4", radix2)
        + function("ntruplus1152_exp001_official_t3x3_t2x4", combined)
        + '.section .note.GNU-stack,"",@progbits\n'
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = render(args.source.read_text(encoding="utf-8"))
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit("generated Official stage partitions are stale")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(rendered, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
