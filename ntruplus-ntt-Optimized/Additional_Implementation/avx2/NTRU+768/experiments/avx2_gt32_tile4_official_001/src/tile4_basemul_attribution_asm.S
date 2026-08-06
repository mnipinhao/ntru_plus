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

	/*
	 * Fuse coefficient-plane redeposit with inverse stages 0 and 1.
	 *
	 * The qword layer at the end of the 4x16 plane->AoS transpose is
	 * immediately inverted by RAW_LOCAL_QWORD_PAIR.  Starting from the four
	 * plane registers, the two operations collapse to two dq-unpack layers,
	 * four add/sub operations, and four final qword unpacks.  The result then
	 * feeds the pair-packed Montgomery half butterfly without an AoS store and
	 * reload boundary.
	 */
	.macro ATTR_REDEPOSIT_RAW_TO_HALF o0,o1
	/* First two levels of plane -> AoS transpose. */
	vpunpcklwd %ymm2, %ymm1, %ymm5
	vpunpckhwd %ymm2, %ymm1, %ymm6
	vpunpcklwd %ymm15, %ymm3, %ymm7
	vpunpckhwd %ymm15, %ymm3, %ymm8
	vpunpckldq %ymm7, %ymm5, %ymm1
	vpunpckhdq %ymm7, %ymm5, %ymm2
	vpunpckldq %ymm8, %ymm6, %ymm3
	vpunpckhdq %ymm8, %ymm6, %ymm4

	/* Combined transpose qword layer and raw inverse stage 0. */
	vpaddw %ymm3, %ymm1, %ymm9
	vpsubw %ymm3, %ymm1, %ymm10
	vpunpcklqdq %ymm10, %ymm9, %ymm5
	vpunpckhqdq %ymm10, %ymm9, %ymm6
	vpaddw %ymm4, %ymm2, %ymm9
	vpsubw %ymm4, %ymm2, %ymm10
	vpunpcklqdq %ymm10, %ymm9, %ymm7
	vpunpckhqdq %ymm10, %ymm9, %ymm8

	/* Pair-packed inverse stage 1; q is resident in ymm0. */
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

	.macro ATTR_BM_FUSED_BLOCK o0,o1
	vmovdqu   0(%rdx), %ymm1
	vmovdqu  32(%rdx), %ymm2
	vmovdqu  64(%rdx), %ymm3
	vmovdqu  96(%rdx), %ymm4
	ATTR_TRANSPOSE ymm1,ymm2,ymm3,ymm4,ymm9,ymm10,ymm11,ymm12
	vmovdqu   0(%rsi), %ymm5
	vmovdqu  32(%rsi), %ymm6
	vmovdqu  64(%rsi), %ymm7
	vmovdqu  96(%rsi), %ymm8
	ATTR_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4

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
	ATTR_CENTER_C3

	vmovdqu  0(%rdi), %ymm1
	vmovdqu 32(%rdi), %ymm2
	vmovdqu 64(%rdi), %ymm3
	ATTR_REDEPOSIT_RAW_TO_HALF \o0,\o1
	vmovdqu %ymm5,  0(%rdi)
	vmovdqu %ymm6, 32(%rdi)
	vmovdqu %ymm7, 64(%rdi)
	vmovdqu %ymm8, 96(%rdi)

	addq $128, %rsi
	addq $128, %rdx
	addq $128, %rdi
	addq $32, %r8
	addq $32, %r9
	.endm

	.p2align 5
	.globl gt32_tile4_attr_basemul_i1_stage01_fused_asm
	.type gt32_tile4_attr_basemul_i1_stage01_fused_asm,@function
gt32_tile4_attr_basemul_i1_stage01_fused_asm:
	leaq .Ltile4_bm_lambda(%rip), %r8
	leaq .Ltile4_bm_lambda_qinv(%rip), %r9
	vmovdqa .Lattr_q(%rip), %ymm0
	movl $6, %ecx
	.p2align 5
.Lattr_bm_i1_fused_loop:
	ATTR_BM_FUSED_BLOCK 0,32
	ATTR_BM_FUSED_BLOCK 64,96
	decl %ecx
	jne .Lattr_bm_i1_fused_loop
	vzeroupper
	ret
	.size gt32_tile4_attr_basemul_i1_stage01_fused_asm,.-gt32_tile4_attr_basemul_i1_stage01_fused_asm

	.macro ATTR_MONT_CROSS4 l0,h0,l1,h1,l2,h2,l3,h3,qinv,factor
	vpmullw \qinv+0(%rip), \h0, %ymm8
	vpmullw \qinv+32(%rip), \h1, %ymm9
	vpmullw \qinv+64(%rip), \h2, %ymm10
	vpmullw \qinv+96(%rip), \h3, %ymm11
	vpmulhw \factor+0(%rip), \h0, \h0
	vpmulhw \factor+32(%rip), \h1, \h1
	vpmulhw \factor+64(%rip), \h2, \h2
	vpmulhw \factor+96(%rip), \h3, \h3
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

	/* Consume the benchmark-only post-stage1 layout and finish I1 stages 2-4. */
	.p2align 5
	.globl gt32_tile4_attr_inverse_i1_cross3_asm
	.type gt32_tile4_attr_inverse_i1_cross3_asm,@function
gt32_tile4_attr_inverse_i1_cross3_asm:
	vmovdqa .Lattr_q(%rip), %ymm15
	movl $6, %ecx
	.p2align 5
.Lattr_i1_cross3_loop:
	vmovdqu   0(%rsi), %ymm0
	vmovdqu  32(%rsi), %ymm1
	vmovdqu  64(%rsi), %ymm2
	vmovdqu  96(%rsi), %ymm3
	vmovdqu 128(%rsi), %ymm4
	vmovdqu 160(%rsi), %ymm5
	vmovdqu 192(%rsi), %ymm6
	vmovdqu 224(%rsi), %ymm7
	ATTR_MONT_CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, .Ltile4_inv_s2_qinv,.Ltile4_inv_s2_factor
	ATTR_MONT_CROSS4 %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, .Ltile4_inv_s3_qinv,.Ltile4_inv_s3_factor
	ATTR_MONT_CROSS4 %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7, .Ltile4_inv_s4_qinv,.Ltile4_inv_s4_factor
	vmovdqu %ymm0,   0(%rdi)
	vmovdqu %ymm1,  32(%rdi)
	vmovdqu %ymm2,  64(%rdi)
	vmovdqu %ymm3,  96(%rdi)
	vmovdqu %ymm4, 128(%rdi)
	vmovdqu %ymm5, 160(%rdi)
	vmovdqu %ymm6, 192(%rdi)
	vmovdqu %ymm7, 224(%rdi)
	addq $256, %rsi
	addq $256, %rdi
	decl %ecx
	jne .Lattr_i1_cross3_loop
	vzeroupper
	ret
	.size gt32_tile4_attr_inverse_i1_cross3_asm,.-gt32_tile4_attr_inverse_i1_cross3_asm

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
#include "../generated/tile4_constants.inc"

	.section .note.GNU-stack,"",@progbits
