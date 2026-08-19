#!/usr/bin/env python3
"""Generate matched current-B3 and final-store-add-m functions from GT Clean."""

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
    if macro.count(q_load) != 1:
        raise ValueError("unexpected B3 q-load shape")
    macro = macro.replace(q_load, q_load + " movq %rcx, %r10\n", 1)
    out_advance = " addq $128, %rdi\n"
    if macro.count(out_advance) != 1:
        raise ValueError("unexpected B3 output advance shape")
    macro = macro.replace(out_advance,
                          out_advance + " addq $128, %r10\n", 1)
    return macro


def generate(source: str) -> str:
    if source.count(SCALE) != 1 or source.count(GENERAL) != 1:
        raise ValueError("selected GT Clean B3 instantiations changed")
    macro = addm_macro(source)
    instantiations = "\n".join([
        " /* 032 matched symbol cage: control then candidate. */",
        " TILE4_BASEMUL_B3_FUNCTION gt32_032_b3_control_normal, TILE4_OUTPUT_SOA_LATE_RSQ,TILE4_INPUT_A_SOA,TILE4_INPUT_B_SOA",
        " TILE4_BASEMUL_B3_ADDM_FUNCTION gt32_032_b3_addm_normal, TILE4_OUTPUT_SOA_LATE_RSQ_ADD_M,TILE4_INPUT_A_SOA,TILE4_INPUT_B_SOA",
        " /* Reversed cage: candidate then control. */",
        " TILE4_BASEMUL_B3_ADDM_FUNCTION gt32_032_b3_addm_reversed, TILE4_OUTPUT_SOA_LATE_RSQ_ADD_M,TILE4_INPUT_A_SOA,TILE4_INPUT_B_SOA",
        " TILE4_BASEMUL_B3_FUNCTION gt32_032_b3_control_reversed, TILE4_OUTPUT_SOA_LATE_RSQ,TILE4_INPUT_A_SOA,TILE4_INPUT_B_SOA",
    ])
    source = source.replace(SCALE, "", 1)
    source = source.replace(GENERAL, instantiations, 1)
    source = source.replace("ntruplus768_basemul_f0_j1_avx2",
                            "gt32_032_unused_basemul_f0_j1")
    insertion = source.index(instantiations)
    source = source[:insertion] + macro + "\n" + source[insertion:]
    return "/* Generated from GT Clean basemul.s; do not edit. */\n" + source


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    result = generate(args.source.read_text())
    if args.check:
        if args.output.read_text() != result:
            raise SystemExit("generated B3 source is stale")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(result)


if __name__ == "__main__":
    main()
