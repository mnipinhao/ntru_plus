#!/usr/bin/env python3
"""Extract the qualified GLOBAL-PHYSICAL-001 S2--S5 control as one tile."""

import argparse
from pathlib import Path


HERE = Path(__file__).resolve().parent
LEGACY = HERE.parent.parent / "avx2_gt32_tile4_official_001"
SOURCE = LEGACY / "src" / "tile4_global_physical_asm.S"
CONSTANTS = LEGACY / "generated" / "tile4_global_physical_constants.inc"


def between(text: str, start: str, end: str) -> str:
    begin = text.index(start)
    finish = text.index(end, begin)
    return text[begin:finish]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = SOURCE.read_text()
    function = between(
        source,
        ".globl gt32_global_forward_core_asm",
        ".size gt32_global_forward_core_asm,.-gt32_global_forward_core_asm",
    )
    suffix = between(
        function,
        "\t/* forward S2: q3 at physical bit 4 */",
        "\taddq $256,%rsi",
    ).rstrip()
    constants = CONSTANTS.read_text()
    forward_constants = between(
        constants,
        ".Lgp_forward_s2_qinv:",
        ".Lgp_forward_suffix_p_s2_qinv:",
    ).rstrip()
    encoded = f"""/* Extracted exact GLOBAL-PHYSICAL-001 progressive control. */
.text
.p2align 5
.globl gt32_plane_n16_progressive_control_asm
.type gt32_plane_n16_progressive_control_asm,@function
gt32_plane_n16_progressive_control_asm:
\tvmovdqa .Lgp_q(%rip),%ymm15
\tvmovdqu 0(%rsi),%ymm0
\tvmovdqu 32(%rsi),%ymm2
\tvmovdqu 64(%rsi),%ymm1
\tvmovdqu 96(%rsi),%ymm3
\tvmovdqu 128(%rsi),%ymm8
\tvmovdqu 160(%rsi),%ymm9
\tvmovdqu 192(%rsi),%ymm10
\tvmovdqu 224(%rsi),%ymm11
{suffix}
\tvzeroupper
\tret
.size gt32_plane_n16_progressive_control_asm,.-gt32_plane_n16_progressive_control_asm

.section .rodata
.p2align 5
.Lgp_q:
\t.rept 16
\t.short 3457
\t.endr
.p2align 5
{forward_constants}
.section .note.GNU-stack,"",@progbits
"""
    args.output.write_text(encoded)


if __name__ == "__main__":
    main()
