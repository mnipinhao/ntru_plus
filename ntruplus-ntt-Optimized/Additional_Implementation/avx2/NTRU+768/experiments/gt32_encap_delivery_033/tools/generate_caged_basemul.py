#!/usr/bin/env python3
"""Generate one fixed-size B3 add-m cage at a selected page offset."""

from __future__ import annotations

import argparse
from pathlib import Path


GENERAL = (
    " TILE4_BASEMUL_B3_FUNCTION ntruplus768_basemul_general_m_avx2, "
    "TILE4_OUTPUT_SOA_LATE_RSQ,TILE4_INPUT_A_SOA,TILE4_INPUT_B_SOA"
)
SCALE = (
    " TILE4_BASEMUL_B3_FUNCTION ntruplus768_basemul_scale_m_avx2, "
    "TILE4_OUTPUT_SOA_LATE_C3CENTER,TILE4_INPUT_A_SOA,TILE4_INPUT_B_SOA"
)


def addm_macro(source: str) -> str:
    start = source.index(" .macro TILE4_BASEMUL_B3_FUNCTION")
    end = source.index(" .endm", start) + len(" .endm")
    macro = source[start:end]
    macro = macro.replace("TILE4_BASEMUL_B3_FUNCTION",
                          "TILE4_BASEMUL_B3_ADDM_FUNCTION", 1)
    q_load = " vmovdqa .Ltile4_bm_q(%rip), %ymm0\n"
    macro = macro.replace(q_load, q_load + " movq %rcx, %r10\n", 1)
    macro = macro.replace(" addq $128, %rdi\n",
                          " addq $128, %rdi\n addq $128, %r10\n", 1)
    return macro


def generate(source: str, offset: int) -> str:
    if offset % 32 != 0 or not 0 <= offset <= 224:
        raise ValueError("offset must be one of 0,32,...,224")
    if source.count(SCALE) != 1 or source.count(GENERAL) != 1:
        raise ValueError("selected production B3 instantiations changed")
    macro = addm_macro(source)
    cage = "\n".join([
        " .section .text.gt033.50_b3_cage,\"ax\",@progbits",
        " .p2align 12",
        ".Lgt033_b3_cage_begin:",
        f" .org .Lgt033_b3_cage_begin + {offset}, 0x90",
        " TILE4_BASEMUL_B3_ADDM_FUNCTION gt32_033_b3_addm, TILE4_OUTPUT_SOA_LATE_RSQ_ADD_M,TILE4_INPUT_A_SOA,TILE4_INPUT_B_SOA",
        " .org .Lgt033_b3_cage_begin + 4096, 0x90",
        " .text",
    ])
    source = source.replace(SCALE, "", 1)
    source = source.replace(GENERAL, cage, 1)
    source = source.replace("ntruplus768_basemul_f0_j1_avx2",
                            "gt32_033_unused_basemul_f0_j1")
    insertion = source.index(cage)
    source = source[:insertion] + macro + "\n" + source[insertion:]
    return (f"/* Generated 033 cage, candidate page offset {offset}; do not edit. */\n"
            + source)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--offset", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = generate(args.source.read_text(), args.offset)
    if args.check:
        if args.output.read_text() != data:
            raise SystemExit("generated caged B3 is stale")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(data)


if __name__ == "__main__":
    main()
