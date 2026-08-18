#!/usr/bin/env python3
"""Emit the qualified current pair-packed S2--S5 plus plane deposit."""

import argparse
from pathlib import Path


HERE = Path(__file__).resolve().parent
LEGACY = HERE.parent.parent / "avx2_gt32_tile4_official_001"
SOURCE = LEGACY / "src" / "tile4_asm.S"
TRANSPOSE_SOURCE = LEGACY / "src" / "tile4_basemul_asm.S"
CONSTANTS = LEGACY / "generated" / "tile4_constants.inc"


def macro(text: str, name: str) -> str:
    start = text.index(f".macro {name}")
    end = text.index(".endm", start) + len(".endm")
    return text[start:end]


def table(text: str, label: str) -> str:
    start = text.index(label + ":")
    next_table = text.index(".p2align 5\n.L", start + len(label) + 1)
    return text[start:next_table].rstrip()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = SOURCE.read_text()
    transpose = TRANSPOSE_SOURCE.read_text()
    constants = CONSTANTS.read_text()
    macros = "\n\n".join([
        macro(source, "MONT_CROSS4"),
        macro(source, "MONT_LOCAL_HALF_PAIR"),
        macro(source, "MONT_LOCAL_QWORD_PAIR"),
        macro(transpose, "TILE4_TRANSPOSE"),
    ])
    labels = [
        ".Ltile4_fwd_s2_qinv", ".Ltile4_fwd_s2_factor",
        ".Ltile4_fwd_s3_qinv", ".Ltile4_fwd_s3_factor",
        ".Ltile4_fwd_s4_pair_qinv", ".Ltile4_fwd_s4_pair_factor",
        ".Ltile4_fwd_s5_pair_qinv", ".Ltile4_fwd_s5_pair_factor",
    ]
    tables = "\n.p2align 5\n".join(table(constants, label) for label in labels)
    body = f"""/* Extracted current pair-packed N16 control. */
.text
{macros}
.p2align 5
.globl gt32_plane_n16_pair_control_asm
.type gt32_plane_n16_pair_control_asm,@function
gt32_plane_n16_pair_control_asm:
\tvmovdqa .Lpair_q(%rip),%ymm15
\tvmovdqu 0(%rsi),%ymm0
\tvmovdqu 32(%rsi),%ymm1
\tvmovdqu 64(%rsi),%ymm2
\tvmovdqu 96(%rsi),%ymm3
\tvmovdqu 128(%rsi),%ymm4
\tvmovdqu 160(%rsi),%ymm5
\tvmovdqu 192(%rsi),%ymm6
\tvmovdqu 224(%rsi),%ymm7
\tMONT_CROSS4 %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, .Ltile4_fwd_s2_qinv, .Ltile4_fwd_s2_factor
\tMONT_CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, .Ltile4_fwd_s3_qinv, .Ltile4_fwd_s3_factor
\tMONT_LOCAL_HALF_PAIR %ymm0,%ymm1, .Ltile4_fwd_s4_pair_qinv,.Ltile4_fwd_s4_pair_factor, 0
\tMONT_LOCAL_HALF_PAIR %ymm2,%ymm3, .Ltile4_fwd_s4_pair_qinv,.Ltile4_fwd_s4_pair_factor, 32
\tMONT_LOCAL_HALF_PAIR %ymm4,%ymm5, .Ltile4_fwd_s4_pair_qinv,.Ltile4_fwd_s4_pair_factor, 64
\tMONT_LOCAL_HALF_PAIR %ymm6,%ymm7, .Ltile4_fwd_s4_pair_qinv,.Ltile4_fwd_s4_pair_factor, 96
\tMONT_LOCAL_QWORD_PAIR %ymm0,%ymm1, .Ltile4_fwd_s5_pair_qinv,.Ltile4_fwd_s5_pair_factor, 0
\tMONT_LOCAL_QWORD_PAIR %ymm2,%ymm3, .Ltile4_fwd_s5_pair_qinv,.Ltile4_fwd_s5_pair_factor, 32
\tMONT_LOCAL_QWORD_PAIR %ymm4,%ymm5, .Ltile4_fwd_s5_pair_qinv,.Ltile4_fwd_s5_pair_factor, 64
\tMONT_LOCAL_QWORD_PAIR %ymm6,%ymm7, .Ltile4_fwd_s5_pair_qinv,.Ltile4_fwd_s5_pair_factor, 96
\tTILE4_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm8,ymm9,ymm10,ymm11
\tvmovdqu %ymm8,0(%rdi)
\tvmovdqu %ymm9,32(%rdi)
\tvmovdqu %ymm10,64(%rdi)
\tvmovdqu %ymm11,96(%rdi)
\tTILE4_TRANSPOSE ymm4,ymm5,ymm6,ymm7,ymm0,ymm1,ymm2,ymm3
\tvmovdqu %ymm0,128(%rdi)
\tvmovdqu %ymm1,160(%rdi)
\tvmovdqu %ymm2,192(%rdi)
\tvmovdqu %ymm3,224(%rdi)
\tvzeroupper
\tret
.size gt32_plane_n16_pair_control_asm,.-gt32_plane_n16_pair_control_asm

.section .rodata
.p2align 5
.Lpair_q:
\t.rept 16
\t.short 3457
\t.endr
.p2align 5
{tables}
.section .note.GNU-stack,"",@progbits
"""
    args.output.write_text(body)


if __name__ == "__main__":
    main()
