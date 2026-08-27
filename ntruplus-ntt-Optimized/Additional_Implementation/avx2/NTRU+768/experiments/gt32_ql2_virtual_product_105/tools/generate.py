#!/usr/bin/env python3
"""Generate the bounded virtual-product B3+QL2 serializer."""

from pathlib import Path


EXP = Path(__file__).resolve().parents[1]
ROOT = EXP.parents[1]
E103 = ROOT / "experiments/gt32_ql2_shared_convergence_103/generated"
OUT = EXP / "generated"
OUT.mkdir(exist_ok=True)
(OUT / "ntt_ql2.s").write_text((E103 / "ntt_ql2.s").read_text())
(OUT / "pack_ql2.s").write_text((E103 / "pack_ql2.s").read_text())

tiles = {
    0: ([4, 3, 1, 2], [177, 75, 75, 75], 0),
    1: ([4, 3, 1, 2], [177, 75, 75, 75], 96),
    2: ([3, 4, 2, 1], [228, 228, 228, 30], 1056),
    3: ([1, 2, 3, 4], [228, 228, 228, 228], 960),
    4: ([2, 1, 4, 3], [30, 177, 30, 177], 384),
    5: ([2, 1, 4, 3], [30, 177, 30, 177], 480),
    6: ([4, 3, 1, 2], [177, 75, 75, 75], 768),
    7: ([4, 3, 1, 2], [177, 75, 75, 75], 864),
    8: ([3, 4, 2, 1], [228, 228, 228, 30], 288),
    9: ([1, 2, 3, 4], [228, 228, 228, 228], 192),
    10: ([2, 1, 4, 3], [30, 177, 30, 177], 672),
    11: ([3, 4, 2, 1], [30, 30, 30, 177], 576),
}
stubs = []
table = []
for tile in range(12):
    regs, perms, base = tiles[tile]
    table.append(f" .long .Lgt105_tile{tile}-.Lgt105_jump_table")
    lines = [f".Lgt105_tile{tile}:"]
    for packet, (reg, perm) in enumerate(zip(regs, perms)):
        # The original serializer visits ciphertext blocks in packet order,
        # so an over-wide final store is repaired by the next block.  B3
        # visits natural tile order; use the exact 12-byte tail whenever the
        # next ciphertext block was already emitted.
        safe = 1 if packet == 3 and tile in {2, 3, 7, 8, 9, 10, 11} else 0
        lines.append(f" GT105_ENCODE ymm{reg},xmm{reg},{perm},{base + 24 * packet},{safe}")
    lines.append(" jmp .Lgt105_footer")
    stubs.extend(lines)

base = (E103 / "basemul_ql2.s").read_text()
append = r'''
.macro GT105_FINALIZE_WD
 vmovdqu 0(%rdi), %ymm5
 vmovdqu 32(%rdi), %ymm6
 vmovdqu 64(%rdi), %ymm7
 vmovdqa %ymm15, %ymm8
 vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm5, %ymm1
 vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm6, %ymm2
 vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm7, %ymm3
 vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm8, %ymm4
 vpmulhw .Ltile4_bm_rsq(%rip), %ymm5, %ymm5
 vpmulhw .Ltile4_bm_rsq(%rip), %ymm6, %ymm6
 vpmulhw .Ltile4_bm_rsq(%rip), %ymm7, %ymm7
 vpmulhw .Ltile4_bm_rsq(%rip), %ymm8, %ymm8
 vpmulhw %ymm0, %ymm1, %ymm1
 vpmulhw %ymm0, %ymm2, %ymm2
 vpmulhw %ymm0, %ymm3, %ymm3
 vpmulhw %ymm0, %ymm4, %ymm4
 vpsubw %ymm1, %ymm5, %ymm5
 vpsubw %ymm2, %ymm6, %ymm6
 vpsubw %ymm3, %ymm7, %ymm7
 vpsubw %ymm4, %ymm8, %ymm8
 vpunpcklwd %ymm6, %ymm5, %ymm1
 vpunpckhwd %ymm6, %ymm5, %ymm2
 vpunpcklwd %ymm8, %ymm7, %ymm3
 vpunpckhwd %ymm8, %ymm7, %ymm4
 vpunpckldq %ymm3, %ymm1, %ymm5
 vpunpckhdq %ymm3, %ymm1, %ymm6
 vpunpckldq %ymm4, %ymm2, %ymm7
 vpunpckhdq %ymm4, %ymm2, %ymm8
.endm
.macro GT105_Q
 vpunpcklqdq %ymm7, %ymm5, %ymm1
 vpunpckhqdq %ymm7, %ymm5, %ymm2
 vpunpcklqdq %ymm8, %ymm6, %ymm3
 vpunpckhqdq %ymm8, %ymm6, %ymm4
.endm
.macro GT105_ENCODE src,srcx,perm,offset,safe
 vpmulhrsw %ymm13, %\src, %ymm14
 vpmullw %ymm15, %ymm14, %ymm14
 vpsubw %ymm14, %\src, %\src
 vpermq $\perm, %\src, %\src
 vpsraw $15, %\src, %ymm14
 vpand %ymm15, %ymm14, %ymm14
 vpaddw %ymm14, %\src, %\src
 vpmaddwd .Lgt105_pair(%rip), %\src, %\src
 vpshufb .Lgt105_mask(%rip), %\src, %\src
 vmovdqu %\srcx, \offset(%r11)
 vextracti128 $1, %\src, %xmm14
.if \safe
 vmovq %xmm14, \offset+12(%r11)
 vpextrd $2, %xmm14, \offset+20(%r11)
.else
 vmovdqu %xmm14, \offset+12(%r11)
.endif
.endm
.section .text.gt105_virtual_product,"ax",@progbits
.p2align 5
.globl gt105_b3_ql2_virtual_pack_avx2
.type gt105_b3_ql2_virtual_pack_avx2,@function
gt105_b3_ql2_virtual_pack_avx2:
 movq %r8, %r11
 movq %rcx, %r10
 vmovdqa .Ltile4_bm_q(%rip), %ymm0
 movl $12, %ecx
.p2align 5
.Lgt105_loop:
 movl $12, %eax
 subl %ecx, %eax
 shlq $5, %rax
 leaq .Ltile4_bm_lambda(%rip), %r8
 leaq .Ltile4_bm_lambda_qinv(%rip), %r9
 addq %rax, %r8
 addq %rax, %r9
 TILE4_INPUT_B_SOA
 TILE4_INPUT_A_SOA
 vpmullw .Ltile4_bm_qinv(%rip), %ymm1, %ymm5
 vpmullw .Ltile4_bm_qinv(%rip), %ymm2, %ymm6
 vpmullw .Ltile4_bm_qinv(%rip), %ymm3, %ymm7
 vpmullw .Ltile4_bm_qinv(%rip), %ymm4, %ymm8
 TILE4_MONT_FIRST ymm2,ymm6,ymm12
 TILE4_MONT_ADD ymm3,ymm7,ymm11
 TILE4_MONT_ADD ymm4,ymm8,ymm10
 TILE4_MONT_LAMBDA
 TILE4_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rdi)
 TILE4_MONT_FIRST ymm3,ymm7,ymm12
 TILE4_MONT_ADD ymm4,ymm8,ymm11
 TILE4_MONT_LAMBDA
 TILE4_MONT_ADD ymm1,ymm5,ymm10
 TILE4_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rdi)
 TILE4_MONT_FIRST ymm4,ymm8,ymm12
 TILE4_MONT_LAMBDA
 TILE4_MONT_ADD ymm1,ymm5,ymm11
 TILE4_MONT_ADD ymm2,ymm6,ymm10
 TILE4_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rdi)
 TILE4_MONT_FIRST ymm1,ymm5,ymm12
 TILE4_MONT_ADD ymm2,ymm6,ymm11
 TILE4_MONT_ADD ymm3,ymm7,ymm10
 TILE4_MONT_ADD ymm4,ymm8,ymm9
 GT105_FINALIZE_WD
 vpaddw 0(%r10), %ymm5, %ymm5
 vpaddw 32(%r10), %ymm6, %ymm6
 vpaddw 64(%r10), %ymm7, %ymm7
 vpaddw 96(%r10), %ymm8, %ymm8
 GT105_Q
 vmovdqa %ymm0, %ymm15
 vmovdqa .Lgt105_v(%rip), %ymm13
 movl $12, %eax
 subl %ecx, %eax
 leaq .Lgt105_jump_table(%rip), %r8
 movslq (%r8,%rax,4), %rax
 addq %r8, %rax
 jmp *%rax
'''
append += "\n".join(table) + "\n" if False else ""
append += "\n".join(stubs) + r'''
.Lgt105_footer:
 addq $128, %rsi
 addq $128, %rdx
 addq $128, %rdi
 addq $128, %r10
 decl %ecx
 jne .Lgt105_loop
 vzeroupper
 ret
.p2align 2
.Lgt105_jump_table:
'''
append += "\n".join(table) + r'''
.size gt105_b3_ql2_virtual_pack_avx2,.-gt105_b3_ql2_virtual_pack_avx2
/* V2: one direct-call tile core and twelve fall-through continuations. */
.p2align 5
.Lgt105_tile_core:
 TILE4_INPUT_B_SOA
 TILE4_INPUT_A_SOA
 vpmullw .Ltile4_bm_qinv(%rip), %ymm1, %ymm5
 vpmullw .Ltile4_bm_qinv(%rip), %ymm2, %ymm6
 vpmullw .Ltile4_bm_qinv(%rip), %ymm3, %ymm7
 vpmullw .Ltile4_bm_qinv(%rip), %ymm4, %ymm8
 TILE4_MONT_FIRST ymm2,ymm6,ymm12
 TILE4_MONT_ADD ymm3,ymm7,ymm11
 TILE4_MONT_ADD ymm4,ymm8,ymm10
 TILE4_MONT_LAMBDA
 TILE4_MONT_ADD ymm1,ymm5,ymm9
 vmovdqu %ymm15, 0(%rdi)
 TILE4_MONT_FIRST ymm3,ymm7,ymm12
 TILE4_MONT_ADD ymm4,ymm8,ymm11
 TILE4_MONT_LAMBDA
 TILE4_MONT_ADD ymm1,ymm5,ymm10
 TILE4_MONT_ADD ymm2,ymm6,ymm9
 vmovdqu %ymm15, 32(%rdi)
 TILE4_MONT_FIRST ymm4,ymm8,ymm12
 TILE4_MONT_LAMBDA
 TILE4_MONT_ADD ymm1,ymm5,ymm11
 TILE4_MONT_ADD ymm2,ymm6,ymm10
 TILE4_MONT_ADD ymm3,ymm7,ymm9
 vmovdqu %ymm15, 64(%rdi)
 TILE4_MONT_FIRST ymm1,ymm5,ymm12
 TILE4_MONT_ADD ymm2,ymm6,ymm11
 TILE4_MONT_ADD ymm3,ymm7,ymm10
 TILE4_MONT_ADD ymm4,ymm8,ymm9
 GT105_FINALIZE_WD
 ret
.p2align 5
.globl gt105_b3_ql2_virtual_pack_direct_avx2
.type gt105_b3_ql2_virtual_pack_direct_avx2,@function
gt105_b3_ql2_virtual_pack_direct_avx2:
 movq %r8, %r11
 movq %rcx, %r10
 leaq .Ltile4_bm_lambda(%rip), %r8
 leaq .Ltile4_bm_lambda_qinv(%rip), %r9
 vmovdqa .Ltile4_bm_q(%rip), %ymm0
'''
for tile in range(12):
    regs, perms, base_offset = tiles[tile]
    append += " call .Lgt105_tile_core\n"
    append += " vpaddw 0(%r10), %ymm5, %ymm5\n vpaddw 32(%r10), %ymm6, %ymm6\n vpaddw 64(%r10), %ymm7, %ymm7\n vpaddw 96(%r10), %ymm8, %ymm8\n GT105_Q\n vmovdqa %ymm0, %ymm15\n vmovdqa .Lgt105_v(%rip), %ymm13\n"
    for packet, (reg, perm) in enumerate(zip(regs, perms)):
        safe = 1 if packet == 3 and tile in {2, 3, 7, 8, 9, 10, 11} else 0
        append += f" GT105_ENCODE ymm{reg},xmm{reg},{perm},{base_offset + 24 * packet},{safe}\n"
    if tile != 11:
        append += " addq $128, %rsi\n addq $128, %rdx\n addq $128, %rdi\n addq $128, %r10\n addq $32, %r8\n addq $32, %r9\n"
append += r'''
 vzeroupper
 ret
.size gt105_b3_ql2_virtual_pack_direct_avx2,.-gt105_b3_ql2_virtual_pack_direct_avx2
.section .rodata.gt105,"a",@progbits
.p2align 5
.Lgt105_v:
 .rept 16
 .short 9
 .endr
.Lgt105_pair:
 .rept 8
 .short 1,4096
 .endr
.Lgt105_mask:
 .byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128
 .byte 0,1,2,4,5,6,8,9,10,12,13,14,128,128,128,128
.section .note.GNU-stack,"",@progbits
'''
(OUT / "basemul_fused.s").write_text(base + append)
