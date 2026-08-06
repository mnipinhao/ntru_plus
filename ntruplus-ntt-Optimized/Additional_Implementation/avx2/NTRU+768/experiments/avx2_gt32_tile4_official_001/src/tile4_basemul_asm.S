/*
 * Native TILE4 quartic basemul, e=0 x e=0 -> e=-1.
 *
 * Four adjacent TILE4 vectors are transposed entirely in registers into four
 * 16-lane coefficient planes.  The arithmetic is the proven Frozen quartic
 * schedule, but the input and final output ABI remain TILE4.  Four result
 * planes temporarily occupy the destination block before the self-inverse
 * transpose overwrites them with final TILE4 data.  Consequently this first
 * candidate requires out != a && out != b.
 */

	.text

	/* Self-inverse transpose of 16 quartics x four int16 coefficients. */
	.macro TILE4_TRANSPOSE s0,s1,s2,s3,t0,t1,t2,t3
	vpunpcklwd %\s1, %\s0, %\t0
	vpunpckhwd %\s1, %\s0, %\t1
	vpunpcklwd %\s3, %\s2, %\t2
	vpunpckhwd %\s3, %\s2, %\t3

	vpunpckldq %\t2, %\t0, %\s0
	vpunpckhdq %\t2, %\t0, %\s1
	vpunpckldq %\t3, %\t1, %\s2
	vpunpckhdq %\t3, %\t1, %\s3

	vpunpcklqdq %\s2, %\s0, %\t0
	vpunpckhqdq %\s2, %\s0, %\t1
	vpunpcklqdq %\s3, %\s1, %\t2
	vpunpckhqdq %\s3, %\s1, %\t3
	.endm

	.macro TILE4_MONT_FIRST a,aq,b
	vpmullw %\aq, %\b, %ymm13
	vpmulhw %\a,  %\b, %ymm15
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw  %ymm13, %ymm15, %ymm15
	.endm

	.macro TILE4_MONT_ADD a,aq,b
	vpmullw %\aq, %\b, %ymm13
	vpmulhw %\a,  %\b, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw  %ymm13, %ymm14, %ymm14
	vpaddw  %ymm14, %ymm15, %ymm15
	.endm

	.macro TILE4_MONT_LAMBDA
	vpmullw (%r9), %ymm15, %ymm13
	vpmulhw (%r8), %ymm15, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw  %ymm13, %ymm14, %ymm15
	.endm

	.macro TILE4_CENTER_RMINUS1
	vpmulhrsw .Ltile4_bm_center10(%rip), %ymm15, %ymm14
	vpmullw  %ymm0, %ymm14, %ymm14
	vpsubw   %ymm14, %ymm15, %ymm15
	.endm

	/* e=-1 times R^2 through Mont gives the general-ABI e=0 output. */
	.macro TILE4_MONT_RSQ
	vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm15, %ymm13
	vpmulhw .Ltile4_bm_rsq(%rip), %ymm15, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw  %ymm13, %ymm14, %ymm15
	.endm

	.macro TILE4_OUTPUT_AOS
	/* Four coefficient planes -> final native TILE4 output. */
	vmovdqu   0(%rdi), %ymm1
	vmovdqu  32(%rdi), %ymm2
	vmovdqu  64(%rdi), %ymm3
	vmovdqu  96(%rdi), %ymm4
	TILE4_TRANSPOSE ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,ymm8
	vmovdqu %ymm5,   0(%rdi)
	vmovdqu %ymm6,  32(%rdi)
	vmovdqu %ymm7,  64(%rdi)
	vmovdqu %ymm8,  96(%rdi)
	.endm

	/* Private consumer island keeps the four coefficient planes as stored. */
	.macro TILE4_OUTPUT_SOA_PRIVATE
	.endm

	.macro TILE4_BASEMUL_FUNCTION name,finalizer,output
	.p2align 5
	.globl \name
	.type \name,@function
\name:
	leaq .Ltile4_bm_lambda(%rip), %r8
	leaq .Ltile4_bm_lambda_qinv(%rip), %r9
	vmovdqa .Ltile4_bm_q(%rip), %ymm0
	movl $12, %ecx

	.p2align 5
.Ltile4_bm_loop\@:
	/* b AoS -> b0..b3 in ymm9..ymm12. */
	vmovdqu   0(%rdx), %ymm1
	vmovdqu  32(%rdx), %ymm2
	vmovdqu  64(%rdx), %ymm3
	vmovdqu  96(%rdx), %ymm4
	TILE4_TRANSPOSE ymm1,ymm2,ymm3,ymm4,ymm9,ymm10,ymm11,ymm12

	/* a AoS -> a0..a3 in ymm1..ymm4. */
	vmovdqu   0(%rsi), %ymm5
	vmovdqu  32(%rsi), %ymm6
	vmovdqu  64(%rsi), %ymm7
	vmovdqu  96(%rsi), %ymm8
	TILE4_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4

	/* Hoist a_i*qinv for all sixteen Montgomery products. */
	vpmullw .Ltile4_bm_qinv(%rip), %ymm1, %ymm5
	vpmullw .Ltile4_bm_qinv(%rip), %ymm2, %ymm6
	vpmullw .Ltile4_bm_qinv(%rip), %ymm3, %ymm7
	vpmullw .Ltile4_bm_qinv(%rip), %ymm4, %ymm8

	/* c0 = a0*b0 + lambda*(a1*b3 + a2*b2 + a3*b1). */
	TILE4_MONT_FIRST ymm2,ymm6,ymm12
	TILE4_MONT_ADD   ymm3,ymm7,ymm11
	TILE4_MONT_ADD   ymm4,ymm8,ymm10
	TILE4_MONT_LAMBDA
	TILE4_MONT_ADD   ymm1,ymm5,ymm9
	\finalizer
	vmovdqu %ymm15, 0(%rdi)

	/* c1 = a0*b1 + a1*b0 + lambda*(a2*b3 + a3*b2). */
	TILE4_MONT_FIRST ymm3,ymm7,ymm12
	TILE4_MONT_ADD   ymm4,ymm8,ymm11
	TILE4_MONT_LAMBDA
	TILE4_MONT_ADD   ymm1,ymm5,ymm10
	TILE4_MONT_ADD   ymm2,ymm6,ymm9
	\finalizer
	vmovdqu %ymm15, 32(%rdi)

	/* c2 = a0*b2 + a1*b1 + a2*b0 + lambda*a3*b3. */
	TILE4_MONT_FIRST ymm4,ymm8,ymm12
	TILE4_MONT_LAMBDA
	TILE4_MONT_ADD   ymm1,ymm5,ymm11
	TILE4_MONT_ADD   ymm2,ymm6,ymm10
	TILE4_MONT_ADD   ymm3,ymm7,ymm9
	\finalizer
	vmovdqu %ymm15, 64(%rdi)

	/* c3 = a0*b3 + a1*b2 + a2*b1 + a3*b0. */
	TILE4_MONT_FIRST ymm1,ymm5,ymm12
	TILE4_MONT_ADD   ymm2,ymm6,ymm11
	TILE4_MONT_ADD   ymm3,ymm7,ymm10
	TILE4_MONT_ADD   ymm4,ymm8,ymm9
	\finalizer
	vmovdqu %ymm15, 96(%rdi)

	\output

	addq $128, %rsi
	addq $128, %rdx
	addq $128, %rdi
	addq $32, %r8
	addq $32, %r9
	decl %ecx
	jne .Ltile4_bm_loop\@
	vzeroupper
	ret
	.size \name,.-\name
	.endm

	TILE4_BASEMUL_FUNCTION gt32_tile4_basemul_b2_asm, \
		TILE4_CENTER_RMINUS1, TILE4_OUTPUT_AOS
	TILE4_BASEMUL_FUNCTION gt32_tile4_basemul_scale_soa_private_asm, \
		TILE4_CENTER_RMINUS1, TILE4_OUTPUT_SOA_PRIVATE
	TILE4_BASEMUL_FUNCTION gt32_tile4_basemul_general_b2_asm, \
		TILE4_MONT_RSQ, TILE4_OUTPUT_AOS

	.section .rodata
	.p2align 5
.Ltile4_bm_q:
	.rept 16
	.short 3457
	.endr
.Ltile4_bm_qinv:
	.rept 16
	.short 12929
	.endr
.Ltile4_bm_center10:
	.rept 16
	.short 10
	.endr
.Ltile4_bm_rsq:
	.rept 16
	.short 867
	.endr
.Ltile4_bm_rsq_qinv:
	.rept 16
	.short 2787
	.endr

#include "../generated/tile4_basemul_constants.inc"

	.section .note.GNU-stack,"",@progbits
