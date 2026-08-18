#!/usr/bin/env python3
"""Generate a timing-only clone of the frozen Official inverse.

The generated assembly is ephemeral.  Arithmetic instructions and tables come from
the frozen source; this script only renames the entry/local labels and inserts five
serialized timestamp checkpoints at accepted logical boundaries.
"""

from argparse import ArgumentParser
from pathlib import Path


TRACE_MACRO = r"""
.macro OFFICIAL_TRACE slot, preserve_rdx=1
    .if \preserve_rdx
        pushq %rdx
    .endif
    rdtscp
    shlq $32, %rdx
    orq %rdx, %rax
    movq %rax, official_invntt_trace+8*\slot(%rip)
    .if \preserve_rdx
        popq %rdx
    .endif
.endm

.bss
.p2align 5
.globl official_invntt_trace
.type official_invntt_trace,@object
.size official_invntt_trace,40
official_invntt_trace:
    .zero 40

.text
.p2align 5
.globl official_invntt_trace_calibrate
.type official_invntt_trace_calibrate,@function
official_invntt_trace_calibrate:
    OFFICIAL_TRACE 0, 0
    OFFICIAL_TRACE 1
    OFFICIAL_TRACE 2
    OFFICIAL_TRACE 3
    OFFICIAL_TRACE 4
    ret
.size official_invntt_trace_calibrate,.-official_invntt_trace_calibrate

"""


def generate(source: str) -> str:
    text = source
    text = text.replace(".global poly_invntt_scale\n", "")
    text = text.replace(
        "poly_invntt_scale:\n",
        ".text\n.p2align 5\n.globl official_invntt_instrumented\n"
        ".type official_invntt_instrumented,@function\n"
        "official_invntt_instrumented:\n    OFFICIAL_TRACE 0, 0\n",
        1,
    )
    text = text.replace("_looptop", ".Lofficial_trace_looptop")
    text = text.replace(
        "#level2\n",
        "OFFICIAL_TRACE 1\n\n#level2\n",
        1,
    )
    text = text.replace(
        "#level1\n",
        "OFFICIAL_TRACE 2\n\n#level1\n",
        1,
    )
    text = text.replace(
        "#level 0\n",
        "OFFICIAL_TRACE 3\n\n#level 0\n",
        1,
    )
    text = text.replace(
        "ret\n\n.ifndef no_gnu_stack",
        "OFFICIAL_TRACE 4\n    ret\n"
        ".size official_invntt_instrumented,.-official_invntt_instrumented\n\n"
        ".ifndef no_gnu_stack",
        1,
    )
    if text.count("OFFICIAL_TRACE") != 5:
        raise SystemExit("checkpoint injection count mismatch")
    return "/* Generated timing-only clone; do not edit. */\n" + TRACE_MACRO + text


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(generate(args.source.read_text(encoding="utf-8")),
                           encoding="utf-8")


if __name__ == "__main__":
    main()
