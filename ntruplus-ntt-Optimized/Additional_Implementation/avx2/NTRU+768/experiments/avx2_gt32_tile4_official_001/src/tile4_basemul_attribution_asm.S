/*
 * Benchmark-only decomposition of the TILE4 basemul path.
 *
 * These leaves deliberately expose materialization boundaries that the
 * production B3 kernel fuses.  They are not release candidates and must not
 * be called by the KEM.  All addresses and loop counts are public.
 */

	.text
	.p2align 5
	.globl gt32_tile4_attr_empty_asm
	.type gt32_tile4_attr_empty_asm,@function
gt32_tile4_attr_empty_asm:
	ret
	.size gt32_tile4_attr_empty_asm,.-gt32_tile4_attr_empty_asm

	.macro ATTR_TRANSPOSE s0,s1,s2,s3,t0,t1,t2,t3
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

	.macro ATTR_ONE_TRANSPOSE src,dst
	vmovdqu   0(\src), %ymm0
	vmovdqu  32(\src), %ymm1
	vmovdqu  64(\src), %ymm2
	vmovdqu  96(\src), %ymm3
	ATTR_TRANSPOSE ymm0,ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7
	vmovdqu %ymm4,   0(\dst)
	vmovdqu %ymm5,  32(\dst)
	vmovdqu %ymm6,  64(\dst)
	vmovdqu %ymm7,  96(\dst)
	.endm

	/* One AoS<->SoA materialization (the network is self-inverse). */
	.p2align 5
	.globl gt32_tile4_attr_transpose_one_asm
	.type gt32_tile4_attr_transpose_one_asm,@function
gt32_tile4_attr_transpose_one_asm:
	movl $12, %eax
	.p2align 5
.Lattr_t1:
	ATTR_ONE_TRANSPOSE %rsi,%rdi
	addq $128, %rsi
	addq $128, %rdi
	decl %eax
	jne .Lattr_t1
	vzeroupper
	ret
	.size gt32_tile4_attr_transpose_one_asm,.-gt32_tile4_attr_transpose_one_asm

	/* Two independent input materializations in one leaf. */
	.p2align 5
	.globl gt32_tile4_attr_transpose_two_asm
	.type gt32_tile4_attr_transpose_two_asm,@function
gt32_tile4_attr_transpose_two_asm:
	movl $12, %eax
	.p2align 5
.Lattr_t2:
	ATTR_ONE_TRANSPOSE %rdx,%rdi
	ATTR_ONE_TRANSPOSE %rcx,%rsi
	addq $128, %rdx
	addq $128, %rcx
	addq $128, %rdi
	addq $128, %rsi
	decl %eax
	jne .Lattr_t2
	vzeroupper
	ret
	.size gt32_tile4_attr_transpose_two_asm,.-gt32_tile4_attr_transpose_two_asm

	/* Two inputs plus one output materialization, with no arithmetic. */
	.p2align 5
	.globl gt32_tile4_attr_transpose_three_asm
	.type gt32_tile4_attr_transpose_three_asm,@function
gt32_tile4_attr_transpose_three_asm:
	movl $12, %eax
	.p2align 5
.Lattr_t3:
	ATTR_ONE_TRANSPOSE %rcx,%rdi
	ATTR_ONE_TRANSPOSE %r8,%rsi
	ATTR_ONE_TRANSPOSE %r9,%rdx
	addq $128, %rcx
	addq $128, %r8
	addq $128, %r9
	addq $128, %rdi
	addq $128, %rsi
	addq $128, %rdx
	decl %eax
	jne .Lattr_t3
	vzeroupper
	ret
	.size gt32_tile4_attr_transpose_three_asm,.-gt32_tile4_attr_transpose_three_asm

	.macro ATTR_MONT_FIRST a,aq,b
	vpmullw %\aq, %\b, %ymm13
	vpmulhw %\a,  %\b, %ymm15
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw  %ymm13, %ymm15, %ymm15
	.endm

	.macro ATTR_MONT_ADD a,aq,b
	vpmullw %\aq, %\b, %ymm13
	vpmulhw %\a,  %\b, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw  %ymm13, %ymm14, %ymm14
	vpaddw  %ymm14, %ymm15, %ymm15
	.endm

	.macro ATTR_MONT_LAMBDA
	vpmullw (%r9), %ymm15, %ymm13
	vpmulhw (%r8), %ymm15, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw  %ymm13, %ymm14, %ymm15
	.endm

	.macro ATTR_NO_CENTER
	.endm

	.macro ATTR_CENTER_C3
	vpmulhrsw .Lattr_center10(%rip), %ymm15, %ymm14
	vpmullw %ymm0, %ymm14, %ymm14
	vpsubw %ymm14, %ymm15, %ymm15
	.endm

	/* Both inputs and output are coefficient-plane SoA. */
	.macro ATTR_ARITH_FUNCTION name,finalize_c3
	.p2align 5
	.globl \name
	.type \name,@function
\name:
	leaq .Ltile4_bm_lambda(%rip), %r8
	leaq .Ltile4_bm_lambda_qinv(%rip), %r9
	vmovdqa .Lattr_q(%rip), %ymm0
	movl $12, %ecx
	.p2align 5
.Lattr_arith_loop\@:
	vmovdqu   0(%rdx), %ymm9
	vmovdqu  32(%rdx), %ymm10
	vmovdqu  64(%rdx), %ymm11
	vmovdqu  96(%rdx), %ymm12
	vmovdqu   0(%rsi), %ymm1
	vmovdqu  32(%rsi), %ymm2
	vmovdqu  64(%rsi), %ymm3
	vmovdqu  96(%rsi), %ymm4

	vpmullw .Lattr_qinv(%rip), %ymm1, %ymm5
	vpmullw .Lattr_qinv(%rip), %ymm2, %ymm6
	vpmullw .Lattr_qinv(%rip), %ymm3, %ymm7
	vpmullw .Lattr_qinv(%rip), %ymm4, %ymm8

	ATTR_MONT_FIRST ymm2,ymm6,ymm12
	ATTR_MONT_ADD ymm3,ymm7,ymm11
	ATTR_MONT_ADD ymm4,ymm8,ymm10
	ATTR_MONT_LAMBDA
	ATTR_MONT_ADD ymm1,ymm5,ymm9
	vmovdqu %ymm15, 0(%rdi)

	ATTR_MONT_FIRST ymm3,ymm7,ymm12
	ATTR_MONT_ADD ymm4,ymm8,ymm11
	ATTR_MONT_LAMBDA
	ATTR_MONT_ADD ymm1,ymm5,ymm10
	ATTR_MONT_ADD ymm2,ymm6,ymm9
	vmovdqu %ymm15, 32(%rdi)

	ATTR_MONT_FIRST ymm4,ymm8,ymm12
	ATTR_MONT_LAMBDA
	ATTR_MONT_ADD ymm1,ymm5,ymm11
	ATTR_MONT_ADD ymm2,ymm6,ymm10
	ATTR_MONT_ADD ymm3,ymm7,ymm9
	vmovdqu %ymm15, 64(%rdi)

	ATTR_MONT_FIRST ymm1,ymm5,ymm12
	ATTR_MONT_ADD ymm2,ymm6,ymm11
	ATTR_MONT_ADD ymm3,ymm7,ymm10
	ATTR_MONT_ADD ymm4,ymm8,ymm9
	\finalize_c3
	vmovdqu %ymm15, 96(%rdi)

	addq $128, %rsi
	addq $128, %rdx
	addq $128, %rdi
	addq $32, %r8
	addq $32, %r9
	decl %ecx
	jne .Lattr_arith_loop\@
	vzeroupper
	ret
	.size \name,.-\name
	.endm

	ATTR_ARITH_FUNCTION gt32_tile4_attr_basemul_raw_soa_asm,ATTR_NO_CENTER
	ATTR_ARITH_FUNCTION gt32_tile4_attr_basemul_c3_soa_asm,ATTR_CENTER_C3

	/* Standalone c3 repair, including its unavoidable explicit boundary. */
	.p2align 5
	.globl gt32_tile4_attr_center_c3_soa_asm
	.type gt32_tile4_attr_center_c3_soa_asm,@function
gt32_tile4_attr_center_c3_soa_asm:
	vmovdqa .Lattr_q(%rip), %ymm0
	movl $12, %eax
	.p2align 5
.Lattr_center_loop:
	vmovdqu   0(%rsi), %ymm1
	vmovdqu  32(%rsi), %ymm2
	vmovdqu  64(%rsi), %ymm3
	vmovdqu  96(%rsi), %ymm15
	vpmulhrsw .Lattr_center10(%rip), %ymm15, %ymm14
	vpmullw %ymm0, %ymm14, %ymm14
	vpsubw %ymm14, %ymm15, %ymm15
	vmovdqu %ymm1,   0(%rdi)
	vmovdqu %ymm2,  32(%rdi)
	vmovdqu %ymm3,  64(%rdi)
	vmovdqu %ymm15, 96(%rdi)
	addq $128, %rsi
	addq $128, %rdi
	decl %eax
	jne .Lattr_center_loop
	vzeroupper
	ret
	.size gt32_tile4_attr_center_c3_soa_asm,.-gt32_tile4_attr_center_c3_soa_asm

	.section .rodata
	.p2align 5
.Lattr_q:
	.rept 16
	.short 3457
	.endr
.Lattr_qinv:
	.rept 16
	.short 12929
	.endr
.Lattr_center10:
	.rept 16
	.short 10
	.endr

#include "../generated/tile4_basemul_constants.inc"

	.section .note.GNU-stack,"",@progbits
