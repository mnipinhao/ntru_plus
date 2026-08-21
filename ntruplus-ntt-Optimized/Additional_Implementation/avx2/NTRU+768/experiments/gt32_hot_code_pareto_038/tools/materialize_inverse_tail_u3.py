#!/usr/bin/env python3
"""Emit a caged U3x2+U2 inverse-tail probe beside the unmodified control."""

from __future__ import annotations

import re
from pathlib import Path


HERE = Path(__file__).resolve().parent
EXPERIMENT = HERE.parent
BASE = Path("/home/nuc/src/exports/crypto_kem/ntruplus768/avx2-gt32-clean-033b-transform/invntt.s")
OUTPUT = EXPERIMENT / "generated/inverse_tail_u3/invntt_u3.s"


def macro_body(text: str, name: str) -> list[str]:
    lines = text.splitlines()
    start = next(i for i, line in enumerate(lines)
                 if re.match(rf"^\.macro\s+{re.escape(name)}(?:\s|$)", line))
    result = []
    for line in lines[start + 1:]:
        if line.strip() == ".endm":
            return result
        result.append(line)
    raise ValueError(name)


def matrix_ptr(text: str) -> str:
    body = macro_body(text, "MATRIX3_TRIPLE")
    rendered = []
    for line in body:
        line = re.sub(r"\.Ltail_matrix3_qinv\+\\base\+(\d+)\(%rip\)", r"\1(%rdx)", line)
        line = re.sub(r"\.Ltail_matrix3_factor\+\\base\+(\d+)\(%rip\)", r"\1(%rcx)", line)
        line = re.sub(r"\\final_op (.*),\\out_group$", r"FINAL_CENTER_STORE \1,0", line)
        rendered.append(line)
    return ".macro MATRIX3_TRIPLE_PTR a0,a1,b0,b1,c0,c1\n" + "\n".join(rendered) + "\n.endm\n"


def candidate(text: str) -> str:
    helpers = matrix_ptr(text) + r"""
.macro LOAD_RAW_PTR
 vmovdqu 0(%rsi), %ymm0
 vmovdqu 512(%rsi), %ymm1
 vmovdqu 1024(%rsi), %ymm2
 vmovdqu 256(%rsi), %ymm3
 vmovdqu 768(%rsi), %ymm4
 vmovdqu 1280(%rsi), %ymm5
.endm
.macro TAIL_GROUP_T8_PTR a0,a1,b0,b1,c0,c1
 LOAD_RAW_PTR
 vmovdqa .Ltail_w_factor(%rip), %ymm11
 IDFT3_V2 %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8,%ymm9
 IDFT3_V2 %ymm3,%ymm4,%ymm5,%ymm6,%ymm7,%ymm8,%ymm9
 BLEND3_OUT %ymm0,%ymm1,%ymm2,%ymm6,%ymm7,%ymm8
 BLEND3_OUT %ymm3,%ymm4,%ymm5,%ymm0,%ymm1,%ymm2
 vmovdqa %ymm6, %ymm3
 vmovdqa %ymm7, %ymm4
 vmovdqa %ymm8, %ymm5
 MATRIX3_TRIPLE_PTR \a0,\a1,\b0,\b1,\c0,\c1
.endm
.macro ADVANCE_TAIL_PTRS
 addq $32, %rsi
 addq $32, %rdi
 addq $288, %rdx
 addq $288, %rcx
.endm
.section .text.gt32_invntt_tail_u3_avx2,"ax",@progbits
.p2align 5
.globl gt32_invntt_tail_u3_avx2
.type gt32_invntt_tail_u3_avx2,@function
gt32_invntt_tail_u3_avx2:
.L038_inv_u3_begin:
 vmovdqa .Ltail_q(%rip), %ymm15
 vmovdqa .Ltail_center10(%rip), %ymm14
 vmovdqa .Ltail_w_qinv(%rip), %ymm12
 vmovdqa .Ltail_w_factor(%rip), %ymm11
 leaq .Ltail_matrix3_qinv(%rip), %rdx
 leaq .Ltail_matrix3_factor(%rip), %rcx
 movl $2, %r8d
.L038_inv_u3_loop:
 TAIL_GROUP_T8_PTR %ymm3,%ymm0,%ymm4,%ymm1,%ymm5,%ymm2
 ADVANCE_TAIL_PTRS
 TAIL_GROUP_T8_PTR %ymm5,%ymm2,%ymm3,%ymm0,%ymm4,%ymm1
 ADVANCE_TAIL_PTRS
 TAIL_GROUP_T8_PTR %ymm4,%ymm1,%ymm5,%ymm2,%ymm3,%ymm0
 ADVANCE_TAIL_PTRS
 decl %r8d
 jnz .L038_inv_u3_loop
 TAIL_GROUP_T8_PTR %ymm3,%ymm0,%ymm4,%ymm1,%ymm5,%ymm2
 ADVANCE_TAIL_PTRS
 TAIL_GROUP_T8_PTR %ymm5,%ymm2,%ymm3,%ymm0,%ymm4,%ymm1
 vzeroupper
 ret
 .org .L038_inv_u3_begin + 5578, 0x90
.size gt32_invntt_tail_u3_avx2,.-gt32_invntt_tail_u3_avx2
"""
    marker = ".p2align 5\n.globl ntruplus768_invntt_tail_avx2"
    if text.count(marker) != 1:
        raise ValueError("inverse-tail insertion marker")
    return text.replace(marker, helpers + "\n" + marker, 1)


def main() -> int:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(candidate(BASE.read_text()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
