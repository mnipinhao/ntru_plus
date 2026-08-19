#!/usr/bin/env python3
"""Emit the experiment-only qword-semantic frontend and M Forward core."""

from __future__ import annotations

import argparse
import importlib.util
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parent.parent
Q13_TOOL = (EXPERIMENTS / "gt32_cross_r3_qword_semantic_packet_013" /
            "tools/generate_qword_semantic_packet_gate.py")


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


G = load_module("qword013_for_asm016", Q13_TOOL)
GT = G.GT


def mont(value: int) -> int:
    return GT.centered(value * GT.R)


def factor_rows(multiplier: int) -> list[list[list[int]]]:
    # The five-stage core is DIF.  Its input phase is indexed by the input
    # column q; bit reversal describes the terminal location only.
    scales = [pow(G.W, multiplier * q, GT.Q) for q in range(32)]
    stages = []
    for stage in range(1, 6):
        factors = {}
        output = scales[:]
        for low, high in G.butterfly_pairs(stage):
            factor = G.ordinary_twiddle(stage, low) * scales[low] \
                * pow(scales[high], -1, GT.Q) % GT.Q
            factors[low] = mont(factor)
            output[low] = output[high] = scales[low]
        stages.append(factors)
        scales = output
    assert scales == [1] * 32

    rows = []
    # Cross-vector S1/S2/S3 tables, four high-arm chains each.
    for stage, lows in (
        (0, (range(0, 4), range(4, 8), range(8, 12), range(12, 16))),
        (1, (range(0, 4), range(4, 8), range(16, 20), range(20, 24))),
        (2, (range(0, 4), range(8, 12), range(16, 20), range(24, 28))),
    ):
        rows.append([[stages[stage][q] for q in lane for _ in range(4)]
                     for lane in lows])

    # Packed two-vector S4 tables.
    s4 = []
    for v0, v1 in ((0, 1), (2, 3), (4, 5), (6, 7)):
        q0, q1 = 4 * v0, 4 * v1
        order = (q0, q0 + 1, q1, q1 + 1)
        s4.append([stages[3][q] for q in order for _ in range(4)])
    rows.append(s4)

    # Packed two-vector S5 tables after vpunpck{l,h}qdq.
    s5 = []
    for v0, v1 in ((0, 1), (2, 3), (4, 5), (6, 7)):
        q0, q1 = 4 * v0, 4 * v1
        order = (q0, q1, q0 + 2, q1 + 2)
        s5.append([stages[4][q] for q in order for _ in range(4)])
    rows.append(s5)
    return rows


def emit_table(lines: list[str], label: str, values: list[list[list[int]]],
               transform) -> None:
    lines.extend([".p2align 5", f"{label}:"])
    for stage in values:
        for row in stage:
            lines.append(" .short " + ",".join(str(transform(x)) for x in row))


def frontend_tables() -> list[list[int]]:
    twists = [[GT.centered(pow(scale, -n, GT.Q) * GT.R)
               for n in range(96)] for scale in GT.BRANCH_SCALE]
    records = []
    for group in range(8):
        for branch in range(2):
            for source_row in range(3):
                vector = []
                # This table is consumed before the DIF NTT32.  Its qword
                # coordinate is therefore the input column, not the
                # bit-reversed physical output coordinate used by the 013
                # terminal proof.
                for column in range(4 * group, 4 * group + 4):
                    qmod3 = column % 3
                    twist_row = (qmod3 - source_row) % 3
                    n = (64 * twist_row + 33 * column) % 96
                    vector.extend([twists[branch][n]] * 4)
                records.append(vector)
    return records


ASM_HEAD = r'''
.text
.macro QW_MONT3 v0,v1,v2,off
 vpmullw .Lqw_front_qinv+\off+0(%rip), \v0, %ymm12
 vpmullw .Lqw_front_qinv+\off+32(%rip), \v1, %ymm13
 vpmullw .Lqw_front_qinv+\off+64(%rip), \v2, %ymm14
 vpmulhw .Lqw_front_factor+\off+0(%rip), \v0, \v0
 vpmulhw .Lqw_front_factor+\off+32(%rip), \v1, \v1
 vpmulhw .Lqw_front_factor+\off+64(%rip), \v2, \v2
 vpmulhw %ymm15, %ymm12, %ymm12
 vpmulhw %ymm15, %ymm13, %ymm13
 vpmulhw %ymm15, %ymm14, %ymm14
 vpsubw %ymm12, \v0, \v0
 vpsubw %ymm13, \v1, \v1
 vpsubw %ymm14, \v2, \v2
.endm
.macro QW_DFT3_STORE x0,x1,x2,o0,o1,o2
 vpsubw \x2, \x1, %ymm6
 vpmullw .Lqw_omega_qinv(%rip), %ymm6, %ymm7
 vpmulhw .Lqw_omega_factor(%rip), %ymm6, %ymm6
 vpmulhw %ymm15, %ymm7, %ymm7
 vpsubw %ymm7, %ymm6, %ymm6
 vpaddw \x1, \x0, %ymm7
 vpaddw \x2, %ymm7, %ymm7
 vpsubw \x2, \x0, %ymm8
 vpaddw %ymm6, %ymm8, %ymm8
 vpsubw \x1, \x0, %ymm9
 vpsubw %ymm6, %ymm9, %ymm9
 vmovdqu %ymm7, \o0(%rdi)
 vmovdqu %ymm8, \o1(%rdi)
 vmovdqu %ymm9, \o2(%rdi)
.endm
.macro QW_FRONT_ITER disp,tableoff
 vmovdqu 0+\disp(%rsi), %ymm0
 vmovdqu 256+\disp(%rsi), %ymm1
 vmovdqu 512+\disp(%rsi), %ymm2
 vmovdqu 768+\disp(%rsi), %ymm3
 vmovdqu 1024+\disp(%rsi), %ymm4
 vmovdqu 1280+\disp(%rsi), %ymm5
 vpmullw .Lqw_top_raw(%rip), %ymm3, %ymm6
 vpmullw .Lqw_top_raw(%rip), %ymm4, %ymm7
 vpmullw .Lqw_top_raw(%rip), %ymm5, %ymm8
 vpaddw %ymm0, %ymm3, %ymm3
 vpaddw %ymm1, %ymm4, %ymm4
 vpaddw %ymm2, %ymm5, %ymm5
 vpaddw %ymm6, %ymm0, %ymm0
 vpaddw %ymm7, %ymm1, %ymm1
 vpaddw %ymm8, %ymm2, %ymm2
 vpsubw %ymm6, %ymm3, %ymm3
 vpsubw %ymm7, %ymm4, %ymm4
 vpsubw %ymm8, %ymm5, %ymm5
 QW_MONT3 %ymm0,%ymm1,%ymm2,\tableoff
 QW_MONT3 %ymm3,%ymm4,%ymm5,\tableoff+96
 QW_DFT3_STORE %ymm0,%ymm1,%ymm2,0,1024,512
 QW_DFT3_STORE %ymm3,%ymm4,%ymm5,256,1280,768
 addq $32, %rdi
.endm
.p2align 5
.globl gt32_qword_ntt_frontend_avx2
.type gt32_qword_ntt_frontend_avx2,@function
gt32_qword_ntt_frontend_avx2:
 vmovdqa .Lqw_q(%rip), %ymm15
 QW_FRONT_ITER 0,0
 QW_FRONT_ITER 32,192
 QW_FRONT_ITER 64,384
 QW_FRONT_ITER 96,576
 QW_FRONT_ITER 128,768
 QW_FRONT_ITER 160,960
 QW_FRONT_ITER 192,1152
 QW_FRONT_ITER 224,1344
 vzeroupper
 ret
.size gt32_qword_ntt_frontend_avx2,.-gt32_qword_ntt_frontend_avx2

.macro QW_CROSS l0,h0,l1,h1,l2,h2,l3,h3,off
 vpmullw \off+0(%r8), \h0, %ymm8
 vpmullw \off+32(%r8), \h1, %ymm9
 vpmullw \off+64(%r8), \h2, %ymm10
 vpmullw \off+96(%r8), \h3, %ymm11
 vpmulhw \off+0(%r9), \h0, \h0
 vpmulhw \off+32(%r9), \h1, \h1
 vpmulhw \off+64(%r9), \h2, \h2
 vpmulhw \off+96(%r9), \h3, \h3
 vpmulhw %ymm15, %ymm8, %ymm8
 vpmulhw %ymm15, %ymm9, %ymm9
 vpmulhw %ymm15, %ymm10, %ymm10
 vpmulhw %ymm15, %ymm11, %ymm11
 vpsubw %ymm8, \h0, \h0
 vpsubw %ymm9, \h1, \h1
 vpsubw %ymm10, \h2, \h2
 vpsubw %ymm11, \h3, \h3
 vpsubw \h0, \l0, %ymm8
 vpsubw \h1, \l1, %ymm9
 vpsubw \h2, \l2, %ymm10
 vpsubw \h3, \l3, %ymm11
 vpaddw \h0, \l0, \l0
 vpaddw \h1, \l1, \l1
 vpaddw \h2, \l2, \l2
 vpaddw \h3, \l3, \l3
 vmovdqa %ymm8, \h0
 vmovdqa %ymm9, \h1
 vmovdqa %ymm10, \h2
 vmovdqa %ymm11, \h3
.endm
.macro QW_RAW l0,h0,l1,h1,l2,h2,l3,h3
 vpsubw \h0, \l0, %ymm8
 vpsubw \h1, \l1, %ymm9
 vpsubw \h2, \l2, %ymm10
 vpsubw \h3, \l3, %ymm11
 vpaddw \h0, \l0, \l0
 vpaddw \h1, \l1, \l1
 vpaddw \h2, \l2, \l2
 vpaddw \h3, \l3, \l3
 vmovdqa %ymm8, \h0
 vmovdqa %ymm9, \h1
 vmovdqa %ymm10, \h2
 vmovdqa %ymm11, \h3
.endm
.macro QW_HALF_PAIR v0,v1,off
 vperm2i128 $0x20, \v1, \v0, %ymm8
 vperm2i128 $0x31, \v1, \v0, %ymm9
 vpmullw 384+\off(%r8), %ymm9, %ymm10
 vpmulhw 384+\off(%r9), %ymm9, %ymm9
 vpmulhw %ymm15, %ymm10, %ymm10
 vpsubw %ymm10, %ymm9, %ymm9
 vpsubw %ymm9, %ymm8, %ymm10
 vpaddw %ymm9, %ymm8, %ymm8
 vperm2i128 $0x20, %ymm10, %ymm8, \v0
 vperm2i128 $0x31, %ymm10, %ymm8, \v1
.endm
.macro QW_QWORD_PAIR v0,v1,off
 vpunpcklqdq \v1, \v0, %ymm8
 vpunpckhqdq \v1, \v0, %ymm9
 vpmullw 512+\off(%r8), %ymm9, %ymm10
 vpmulhw 512+\off(%r9), %ymm9, %ymm9
 vpmulhw %ymm15, %ymm10, %ymm10
 vpsubw %ymm10, %ymm9, %ymm9
 vpsubw %ymm9, %ymm8, %ymm10
 vpaddw %ymm9, %ymm8, \v0
 vmovdqa %ymm10, \v1
.endm
.macro QW_PLANES v0,v1,v2,v3,off
 vpshufb %ymm14, \v0, \v0
 vpshufb %ymm14, \v1, \v1
 vpshufb %ymm14, \v2, \v2
 vpshufb %ymm14, \v3, \v3
 vpunpckldq \v2, \v0, %ymm8
 vpunpckhdq \v2, \v0, %ymm9
 vpunpckldq \v3, \v1, %ymm10
 vpunpckhdq \v3, \v1, %ymm11
 vpunpcklqdq %ymm10, %ymm8, \v0
 vpunpckhqdq %ymm10, %ymm8, \v1
 vpunpcklqdq %ymm11, %ymm9, \v2
 vpunpckhqdq %ymm11, %ymm9, \v3
 vmovdqu \v0, \off+0(%rdi)
 vmovdqu \v1, \off+32(%rdi)
 vmovdqu \v2, \off+64(%rdi)
 vmovdqu \v3, \off+96(%rdi)
.endm
.macro QW_LOAD
 vmovdqu 0(%rsi), %ymm0
 vmovdqu 32(%rsi), %ymm1
 vmovdqu 64(%rsi), %ymm2
 vmovdqu 96(%rsi), %ymm3
 vmovdqu 128(%rsi), %ymm4
 vmovdqu 160(%rsi), %ymm5
 vmovdqu 192(%rsi), %ymm6
 vmovdqu 224(%rsi), %ymm7
.endm
.macro QW_REST
 QW_CROSS %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7,128
 QW_CROSS %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7,256
 QW_HALF_PAIR %ymm0,%ymm1,0
 QW_HALF_PAIR %ymm2,%ymm3,32
 QW_HALF_PAIR %ymm4,%ymm5,64
 QW_HALF_PAIR %ymm6,%ymm7,96
 QW_QWORD_PAIR %ymm0,%ymm1,0
 QW_QWORD_PAIR %ymm2,%ymm3,32
 QW_PLANES %ymm0,%ymm1,%ymm2,%ymm3,0
 QW_QWORD_PAIR %ymm4,%ymm5,64
 QW_QWORD_PAIR %ymm6,%ymm7,96
 QW_PLANES %ymm4,%ymm5,%ymm6,%ymm7,128
 addq $256, %rsi
 addq $256, %rdi
.endm
.p2align 5
.globl gt32_qword_ntt_m_avx2
.type gt32_qword_ntt_m_avx2,@function
gt32_qword_ntt_m_avx2:
 vmovdqa .Lqw_q(%rip), %ymm15
 vmovdqa .Lqw_plane_shuffle(%rip), %ymm14
 leaq .Lqw_core_qinv_row0(%rip), %r8
 leaq .Lqw_core_factor_row0(%rip), %r9
 movl $2, %ecx
.Lqw_raw_loop:
 QW_LOAD
 QW_RAW %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7
 QW_REST
 decl %ecx
 jne .Lqw_raw_loop
 leaq .Lqw_core_qinv_row2(%rip), %r8
 leaq .Lqw_core_factor_row2(%rip), %r9
 movl $2, %r10d
.Lqw_weight_row:
 movl $2, %ecx
.Lqw_weight_loop:
 QW_LOAD
 QW_CROSS %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7,0
 QW_REST
 decl %ecx
 jne .Lqw_weight_loop
 decl %r10d
 je .Lqw_weight_done
 leaq .Lqw_core_qinv_row1(%rip), %r8
 leaq .Lqw_core_factor_row1(%rip), %r9
 jmp .Lqw_weight_row
.Lqw_weight_done:
 vzeroupper
 ret
.size gt32_qword_ntt_m_avx2,.-gt32_qword_ntt_m_avx2
'''


def build() -> str:
    lines = [ASM_HEAD, ".section .rodata", ".p2align 5", ".Lqw_q:",
             " .rept 16", f" .short {GT.Q}", " .endr", ".Lqw_top_raw:",
             " .rept 16", " .short -722", " .endr", ".Lqw_omega_qinv:",
             " .rept 16", f" .short {GT.factor_qinv(-886)}", " .endr",
             ".Lqw_omega_factor:", " .rept 16", " .short -886", " .endr",
             ".Lqw_plane_shuffle:",
             " .byte 0,1,8,9,2,3,10,11,4,5,12,13,6,7,14,15",
             " .byte 0,1,8,9,2,3,10,11,4,5,12,13,6,7,14,15"]
    front = frontend_tables()
    lines.extend([".p2align 5", ".Lqw_front_factor:"])
    lines.extend(" .short " + ",".join(map(str, row)) for row in front)
    lines.extend([".p2align 5", ".Lqw_front_qinv:"])
    lines.extend(" .short " + ",".join(str(GT.factor_qinv(x)) for x in row)
                 for row in front)
    # Physical tile order after the swapped DFT stores is row0,row2,row1.
    for name, multiplier in (("row0", 0), ("row2", 2), ("row1", 1)):
        values = factor_rows(multiplier)
        emit_table(lines, f".Lqw_core_factor_{name}", values, lambda x: x)
        emit_table(lines, f".Lqw_core_qinv_{name}", values, GT.factor_qinv)
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(build())


if __name__ == "__main__":
    main()
