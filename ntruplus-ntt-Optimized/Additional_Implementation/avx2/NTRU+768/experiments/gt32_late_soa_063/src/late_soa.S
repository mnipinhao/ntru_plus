/*
 * GT32-LATE-SOA-063: fixed post-S3 -> post-inverse-stage1 island.
 *
 * This is intentionally not a KEM implementation.  It composes two mechanisms
 * that older gates measured separately: Forward S4/S5 directly forming the
 * private coefficient planes, and coefficient-plane BM redeposit fused with
 * inverse stages 0/1.
 */

	.text

	.macro LATE_MONT_HALF v0,v1,offset
	vperm2i128 $0x20, \v1, \v0, %ymm8
	vperm2i128 $0x31, \v1, \v0, %ymm9
	vpmullw .Ltile4_fwd_s4_pair_qinv+\offset(%rip), %ymm9, %ymm10
	vpmulhw .Ltile4_fwd_s4_pair_factor+\offset(%rip), %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vperm2i128 $0x20, %ymm10, %ymm8, \v0
	vperm2i128 $0x31, %ymm10, %ymm8, \v1
	.endm

	.macro LATE_MONT_QWORD v0,v1,offset
	vpunpcklqdq \v1, \v0, %ymm8
	vpunpckhqdq \v1, \v0, %ymm9
	vpmullw .Ltile4_fwd_s5_pair_qinv+\offset(%rip), %ymm9, %ymm10
	vpmulhw .Ltile4_fwd_s5_pair_factor+\offset(%rip), %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vpunpcklqdq %ymm10, %ymm8, \v0
	vpunpckhqdq %ymm10, %ymm8, \v1
	.endm

	/* Same S5 arithmetic, but leave packed sum/difference for plane formation. */
	.macro LATE_MONT_QWORD_PACKED v0,v1,offset
	vpunpcklqdq \v1, \v0, %ymm8
	vpunpckhqdq \v1, \v0, %ymm9
	vpmullw .Ltile4_fwd_s5_pair_qinv+\offset(%rip), %ymm9, %ymm10
	vpmulhw .Ltile4_fwd_s5_pair_factor+\offset(%rip), %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, \v0
	vmovdqa %ymm10, \v1
	.endm

	.macro LATE_LOAD8
	vmovdqu   0(%rsi), %ymm0
	vmovdqu  32(%rsi), %ymm1
	vmovdqu  64(%rsi), %ymm2
	vmovdqu  96(%rsi), %ymm3
	vmovdqu 128(%rsi), %ymm4
	vmovdqu 160(%rsi), %ymm5
	vmovdqu 192(%rsi), %ymm6
	vmovdqu 224(%rsi), %ymm7
	.endm

	.macro LATE_STORE8
	vmovdqu %ymm0,   0(%rdi)
	vmovdqu %ymm1,  32(%rdi)
	vmovdqu %ymm2,  64(%rdi)
	vmovdqu %ymm3,  96(%rdi)
	vmovdqu %ymm4, 128(%rdi)
	vmovdqu %ymm5, 160(%rdi)
	vmovdqu %ymm6, 192(%rdi)
	vmovdqu %ymm7, 224(%rdi)
	.endm

	.p2align 5
	.globl late_suffix_aos_asm
	.type late_suffix_aos_asm,@function
late_suffix_aos_asm:
	vmovdqa .Llate_q(%rip), %ymm15
	LATE_LOAD8
	LATE_MONT_HALF %ymm0,%ymm1,0
	LATE_MONT_HALF %ymm2,%ymm3,32
	LATE_MONT_HALF %ymm4,%ymm5,64
	LATE_MONT_HALF %ymm6,%ymm7,96
	LATE_MONT_QWORD %ymm0,%ymm1,0
	LATE_MONT_QWORD %ymm2,%ymm3,32
	LATE_MONT_QWORD %ymm4,%ymm5,64
	LATE_MONT_QWORD %ymm6,%ymm7,96
	LATE_STORE8
	vzeroupper
	ret
	.size late_suffix_aos_asm,.-late_suffix_aos_asm

	.macro LATE_PACKED_TO_PLANES v0,v1,v2,v3,outoff
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
	vmovdqu \v0, \outoff+0(%rdi)
	vmovdqu \v1, \outoff+32(%rdi)
	vmovdqu \v2, \outoff+64(%rdi)
	vmovdqu \v3, \outoff+96(%rdi)
	.endm

	.p2align 5
	.globl late_suffix_soa_asm
	.type late_suffix_soa_asm,@function
late_suffix_soa_asm:
	vmovdqa .Llate_q(%rip), %ymm15
	vmovdqa .Llate_plane_pshufb(%rip), %ymm14
	LATE_LOAD8
	LATE_MONT_HALF %ymm0,%ymm1,0
	LATE_MONT_HALF %ymm2,%ymm3,32
	LATE_MONT_HALF %ymm4,%ymm5,64
	LATE_MONT_HALF %ymm6,%ymm7,96
	LATE_MONT_QWORD_PACKED %ymm0,%ymm1,0
	LATE_MONT_QWORD_PACKED %ymm2,%ymm3,32
	LATE_PACKED_TO_PLANES %ymm0,%ymm1,%ymm2,%ymm3,0
	LATE_MONT_QWORD_PACKED %ymm4,%ymm5,64
	LATE_MONT_QWORD_PACKED %ymm6,%ymm7,96
	LATE_PACKED_TO_PLANES %ymm4,%ymm5,%ymm6,%ymm7,128
	vzeroupper
	ret
	.size late_suffix_soa_asm,.-late_suffix_soa_asm

	.macro LATE_TRANSPOSE s0,s1,s2,s3,t0,t1,t2,t3
	vpunpcklwd \s1, \s0, \t0
	vpunpckhwd \s1, \s0, \t1
	vpunpcklwd \s3, \s2, \t2
	vpunpckhwd \s3, \s2, \t3
	vpunpckldq \t2, \t0, \s0
	vpunpckhdq \t2, \t0, \s1
	vpunpckldq \t3, \t1, \s2
	vpunpckhdq \t3, \t1, \s3
	vpunpcklqdq \s2, \s0, \t0
	vpunpckhqdq \s2, \s0, \t1
	vpunpcklqdq \s3, \s1, \t2
	vpunpckhqdq \s3, \s1, \t3
	.endm

	.p2align 5
	.globl late_aos_to_soa_asm
	.type late_aos_to_soa_asm,@function
late_aos_to_soa_asm:
	vmovdqu   0(%rsi), %ymm0
	vmovdqu  32(%rsi), %ymm1
	vmovdqu  64(%rsi), %ymm2
	vmovdqu  96(%rsi), %ymm3
	LATE_TRANSPOSE %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7
	vmovdqu %ymm4,   0(%rdi)
	vmovdqu %ymm5,  32(%rdi)
	vmovdqu %ymm6,  64(%rdi)
	vmovdqu %ymm7,  96(%rdi)
	vmovdqu 128(%rsi), %ymm0
	vmovdqu 160(%rsi), %ymm1
	vmovdqu 192(%rsi), %ymm2
	vmovdqu 224(%rsi), %ymm3
	LATE_TRANSPOSE %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7
	vmovdqu %ymm4, 128(%rdi)
	vmovdqu %ymm5, 160(%rdi)
	vmovdqu %ymm6, 192(%rdi)
	vmovdqu %ymm7, 224(%rdi)
	vzeroupper
	ret
	.size late_aos_to_soa_asm,.-late_aos_to_soa_asm

	.macro LATE_RAW_QWORD v0,v1
	vpunpcklqdq \v1, \v0, %ymm8
	vpunpckhqdq \v1, \v0, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vpunpcklqdq %ymm10, %ymm8, \v0
	vpunpckhqdq %ymm10, %ymm8, \v1
	.endm

	.macro LATE_INV_HALF v0,v1,offset
	vperm2i128 $0x20, \v1, \v0, %ymm8
	vperm2i128 $0x31, \v1, \v0, %ymm9
	vpmullw .Ltile4_inv_s1_pair_qinv+\offset(%rip), %ymm9, %ymm10
	vpmulhw .Ltile4_inv_s1_pair_factor+\offset(%rip), %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vperm2i128 $0x20, %ymm10, %ymm8, \v0
	vperm2i128 $0x31, %ymm10, %ymm8, \v1
	.endm

	.p2align 5
	.globl late_inverse_i2_asm
	.type late_inverse_i2_asm,@function
late_inverse_i2_asm:
	vmovdqa .Llate_q(%rip), %ymm15
	LATE_LOAD8
	LATE_RAW_QWORD %ymm0,%ymm1
	LATE_RAW_QWORD %ymm2,%ymm3
	LATE_RAW_QWORD %ymm4,%ymm5
	LATE_RAW_QWORD %ymm6,%ymm7
	LATE_INV_HALF %ymm0,%ymm1,0
	LATE_INV_HALF %ymm2,%ymm3,32
	LATE_INV_HALF %ymm4,%ymm5,64
	LATE_INV_HALF %ymm6,%ymm7,96
	LATE_STORE8
	vzeroupper
	ret
	.size late_inverse_i2_asm,.-late_inverse_i2_asm

	.macro LATE_BM_FIRST a,aq,b
	vpmullw \aq, \b, %ymm13
	vpmulhw \a, \b, %ymm15
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw %ymm13, %ymm15, %ymm15
	.endm

	.macro LATE_BM_ADD a,aq,b
	vpmullw \aq, \b, %ymm13
	vpmulhw \a, \b, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw %ymm13, %ymm14, %ymm14
	vpaddw %ymm14, %ymm15, %ymm15
	.endm

	.macro LATE_BM_LAMBDA
	vpmullw (%r9), %ymm15, %ymm13
	vpmulhw (%r8), %ymm15, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw %ymm13, %ymm14, %ymm15
	.endm

	/* Planes are ymm1..4 (A) and ymm9..12 (B); result planes are 1,2,3,15. */
	.macro LATE_BM_ARITH
	vpmullw .Llate_qinv(%rip), %ymm1, %ymm5
	vpmullw .Llate_qinv(%rip), %ymm2, %ymm6
	vpmullw .Llate_qinv(%rip), %ymm3, %ymm7
	vpmullw .Llate_qinv(%rip), %ymm4, %ymm8
	LATE_BM_FIRST %ymm2,%ymm6,%ymm12
	LATE_BM_ADD %ymm3,%ymm7,%ymm11
	LATE_BM_ADD %ymm4,%ymm8,%ymm10
	LATE_BM_LAMBDA
	LATE_BM_ADD %ymm1,%ymm5,%ymm9
	vmovdqu %ymm15, 0(%rdi)
	LATE_BM_FIRST %ymm3,%ymm7,%ymm12
	LATE_BM_ADD %ymm4,%ymm8,%ymm11
	LATE_BM_LAMBDA
	LATE_BM_ADD %ymm1,%ymm5,%ymm10
	LATE_BM_ADD %ymm2,%ymm6,%ymm9
	vmovdqu %ymm15, 32(%rdi)
	LATE_BM_FIRST %ymm4,%ymm8,%ymm12
	LATE_BM_LAMBDA
	LATE_BM_ADD %ymm1,%ymm5,%ymm11
	LATE_BM_ADD %ymm2,%ymm6,%ymm10
	LATE_BM_ADD %ymm3,%ymm7,%ymm9
	vmovdqu %ymm15, 64(%rdi)
	LATE_BM_FIRST %ymm1,%ymm5,%ymm12
	LATE_BM_ADD %ymm2,%ymm6,%ymm11
	LATE_BM_ADD %ymm3,%ymm7,%ymm10
	LATE_BM_ADD %ymm4,%ymm8,%ymm9
	vpmulhrsw .Llate_center10(%rip), %ymm15, %ymm14
	vpmullw %ymm0, %ymm14, %ymm14
	vpsubw %ymm14, %ymm15, %ymm15
	vmovdqu  0(%rdi), %ymm1
	vmovdqu 32(%rdi), %ymm2
	vmovdqu 64(%rdi), %ymm3
	.endm

	/* Plane redeposit with the qword transpose layer cancelled by inverse I0. */
	.macro LATE_REDEPOSIT_I01 o0,o1
	vpunpcklwd %ymm2, %ymm1, %ymm5
	vpunpckhwd %ymm2, %ymm1, %ymm6
	vpunpcklwd %ymm15, %ymm3, %ymm7
	vpunpckhwd %ymm15, %ymm3, %ymm8
	vpunpckldq %ymm7, %ymm5, %ymm1
	vpunpckhdq %ymm7, %ymm5, %ymm2
	vpunpckldq %ymm8, %ymm6, %ymm3
	vpunpckhdq %ymm8, %ymm6, %ymm4
	vpaddw %ymm3, %ymm1, %ymm9
	vpsubw %ymm3, %ymm1, %ymm10
	vpunpcklqdq %ymm10, %ymm9, %ymm5
	vpunpckhqdq %ymm10, %ymm9, %ymm6
	vpaddw %ymm4, %ymm2, %ymm9
	vpsubw %ymm4, %ymm2, %ymm10
	vpunpcklqdq %ymm10, %ymm9, %ymm7
	vpunpckhqdq %ymm10, %ymm9, %ymm8

	vperm2i128 $0x20, %ymm6, %ymm5, %ymm9
	vperm2i128 $0x31, %ymm6, %ymm5, %ymm10
	vpmullw .Ltile4_inv_s1_pair_qinv+\o0(%rip), %ymm10, %ymm11
	vpmulhw .Ltile4_inv_s1_pair_factor+\o0(%rip), %ymm10, %ymm10
	vpmulhw %ymm0, %ymm11, %ymm11
	vpsubw %ymm11, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm11
	vpaddw %ymm10, %ymm9, %ymm9
	vperm2i128 $0x20, %ymm11, %ymm9, %ymm5
	vperm2i128 $0x31, %ymm11, %ymm9, %ymm6

	vperm2i128 $0x20, %ymm8, %ymm7, %ymm9
	vperm2i128 $0x31, %ymm8, %ymm7, %ymm10
	vpmullw .Ltile4_inv_s1_pair_qinv+\o1(%rip), %ymm10, %ymm11
	vpmulhw .Ltile4_inv_s1_pair_factor+\o1(%rip), %ymm10, %ymm10
	vpmulhw %ymm0, %ymm11, %ymm11
	vpsubw %ymm11, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm11
	vpaddw %ymm10, %ymm9, %ymm9
	vperm2i128 $0x20, %ymm11, %ymm9, %ymm7
	vperm2i128 $0x31, %ymm11, %ymm9, %ymm8
	.endm

	.macro LATE_STORE_I2
	vmovdqu %ymm5,   0(%rdi)
	vmovdqu %ymm6,  32(%rdi)
	vmovdqu %ymm7,  64(%rdi)
	vmovdqu %ymm8,  96(%rdi)
	.endm

	.macro LATE_AOS_BM_BLOCK o0,o1
	vmovdqu   0(%rdx), %ymm1
	vmovdqu  32(%rdx), %ymm2
	vmovdqu  64(%rdx), %ymm3
	vmovdqu  96(%rdx), %ymm4
	LATE_TRANSPOSE %ymm1,%ymm2,%ymm3,%ymm4,%ymm9,%ymm10,%ymm11,%ymm12
	vmovdqu   0(%rsi), %ymm5
	vmovdqu  32(%rsi), %ymm6
	vmovdqu  64(%rsi), %ymm7
	vmovdqu  96(%rsi), %ymm8
	LATE_TRANSPOSE %ymm5,%ymm6,%ymm7,%ymm8,%ymm1,%ymm2,%ymm3,%ymm4
	LATE_BM_ARITH
	LATE_REDEPOSIT_I01 \o0,\o1
	LATE_STORE_I2
	addq $128, %rsi
	addq $128, %rdx
	addq $128, %rdi
	addq $32, %r8
	addq $32, %r9
	.endm

	.macro LATE_SOA_BM_BLOCK o0,o1
	vmovdqu   0(%rdx), %ymm9
	vmovdqu  32(%rdx), %ymm10
	vmovdqu  64(%rdx), %ymm11
	vmovdqu  96(%rdx), %ymm12
	vmovdqu   0(%rsi), %ymm1
	vmovdqu  32(%rsi), %ymm2
	vmovdqu  64(%rsi), %ymm3
	vmovdqu  96(%rsi), %ymm4
	LATE_BM_ARITH
	LATE_REDEPOSIT_I01 \o0,\o1
	LATE_STORE_I2
	addq $128, %rsi
	addq $128, %rdx
	addq $128, %rdi
	addq $32, %r8
	addq $32, %r9
	.endm

	.p2align 5
	.globl late_aos_basemul_i2_fused_asm
	.type late_aos_basemul_i2_fused_asm,@function
late_aos_basemul_i2_fused_asm:
	leaq .Ltile4_bm_lambda(%rip), %r8
	leaq .Ltile4_bm_lambda_qinv(%rip), %r9
	vmovdqa .Llate_q(%rip), %ymm0
	LATE_AOS_BM_BLOCK 0,32
	LATE_AOS_BM_BLOCK 64,96
	vzeroupper
	ret
	.size late_aos_basemul_i2_fused_asm,.-late_aos_basemul_i2_fused_asm

	.p2align 5
	.globl late_soa_basemul_i2_fused_asm
	.type late_soa_basemul_i2_fused_asm,@function
late_soa_basemul_i2_fused_asm:
	leaq .Ltile4_bm_lambda(%rip), %r8
	leaq .Ltile4_bm_lambda_qinv(%rip), %r9
	vmovdqa .Llate_q(%rip), %ymm0
	LATE_SOA_BM_BLOCK 0,32
	LATE_SOA_BM_BLOCK 64,96
	vzeroupper
	ret
	.size late_soa_basemul_i2_fused_asm,.-late_soa_basemul_i2_fused_asm

	.section .rodata
	.p2align 5
.Llate_q:
	.rept 16
	.short 3457
	.endr
.Llate_qinv:
	.rept 16
	.short 12929
	.endr
.Llate_center10:
	.rept 16
	.short 10
	.endr
.Llate_plane_pshufb:
	.byte 0,1,8,9,2,3,10,11,4,5,12,13,6,7,14,15
	.byte 0,1,8,9,2,3,10,11,4,5,12,13,6,7,14,15

#include "../../avx2_gt32_tile4_official_001/generated/tile4_constants.inc"
#include "../../avx2_gt32_tile4_official_001/generated/tile4_basemul_constants.inc"

	.section .note.GNU-stack,"",@progbits
