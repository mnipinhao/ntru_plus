/* Benchmark-only NTT32 core: TILE4 scratch -> private BM coefficient planes. */

	.text

	.macro FR_MONT_CROSS4 l0,h0,l1,h1,l2,h2,l3,h3,qinv,factor
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

	/* Standard 12-shuffle plane network, with outputs placed for streaming BM. */
	.macro FR_PACKED_TO_BM_REGS v0,v1,v2,v3
	vpshufb %ymm14, \v0, \v0
	vpshufb %ymm14, \v1, \v1
	vpshufb %ymm14, \v2, \v2
	vpshufb %ymm14, \v3, \v3
	vpunpckldq \v2, \v0, %ymm4
	vpunpckhdq \v2, \v0, %ymm5
	vpunpckldq \v3, \v1, %ymm6
	vpunpckhdq \v3, \v1, %ymm7
	vpunpcklqdq %ymm6, %ymm4, %ymm9
	vpunpckhqdq %ymm6, %ymm4, %ymm10
	vpunpcklqdq %ymm7, %ymm5, %ymm11
	vpunpckhqdq %ymm7, %ymm5, %ymm12
	.endm

	.macro FR_STREAM_MONT_FIRST a,aq,b
	vpmullw \aq, \b, %ymm13
	vpmulhw \a, \b, %ymm0
	vpmulhw %ymm15, %ymm13, %ymm13
	vpsubw %ymm13, %ymm0, %ymm0
	.endm

	.macro FR_STREAM_MONT_ADD a,aq,b
	vpmullw \aq, \b, %ymm13
	vpmulhw \a, \b, %ymm14
	vpmulhw %ymm15, %ymm13, %ymm13
	vpsubw %ymm13, %ymm14, %ymm14
	vpaddw %ymm14, %ymm0, %ymm0
	.endm

	.macro FR_STREAM_MONT_LAMBDA
	vpmullw (%r9), %ymm0, %ymm13
	vpmulhw (%r8), %ymm0, %ymm14
	vpmulhw %ymm15, %ymm13, %ymm13
	vpsubw %ymm13, %ymm14, %ymm0
	.endm

	/* A planes are loaded; B planes are already resident in ymm9..ymm12. */
	.macro FR_STREAM_BM_BLOCK
	vmovdqu   0(%rsi), %ymm1
	vmovdqu  32(%rsi), %ymm2
	vmovdqu  64(%rsi), %ymm3
	vmovdqu  96(%rsi), %ymm4
	vpmullw .Lfr_stream_qinv(%rip), %ymm1, %ymm5
	vpmullw .Lfr_stream_qinv(%rip), %ymm2, %ymm6
	vpmullw .Lfr_stream_qinv(%rip), %ymm3, %ymm7
	vpmullw .Lfr_stream_qinv(%rip), %ymm4, %ymm8

	FR_STREAM_MONT_FIRST %ymm2,%ymm6,%ymm12
	FR_STREAM_MONT_ADD %ymm3,%ymm7,%ymm11
	FR_STREAM_MONT_ADD %ymm4,%ymm8,%ymm10
	FR_STREAM_MONT_LAMBDA
	FR_STREAM_MONT_ADD %ymm1,%ymm5,%ymm9
	vmovdqu %ymm0, 0(%rdi)

	FR_STREAM_MONT_FIRST %ymm3,%ymm7,%ymm12
	FR_STREAM_MONT_ADD %ymm4,%ymm8,%ymm11
	FR_STREAM_MONT_LAMBDA
	FR_STREAM_MONT_ADD %ymm1,%ymm5,%ymm10
	FR_STREAM_MONT_ADD %ymm2,%ymm6,%ymm9
	vmovdqu %ymm0, 32(%rdi)

	FR_STREAM_MONT_FIRST %ymm4,%ymm8,%ymm12
	FR_STREAM_MONT_LAMBDA
	FR_STREAM_MONT_ADD %ymm1,%ymm5,%ymm11
	FR_STREAM_MONT_ADD %ymm2,%ymm6,%ymm10
	FR_STREAM_MONT_ADD %ymm3,%ymm7,%ymm9
	vmovdqu %ymm0, 64(%rdi)

	FR_STREAM_MONT_FIRST %ymm1,%ymm5,%ymm12
	FR_STREAM_MONT_ADD %ymm2,%ymm6,%ymm11
	FR_STREAM_MONT_ADD %ymm3,%ymm7,%ymm10
	FR_STREAM_MONT_ADD %ymm4,%ymm8,%ymm9
	vpmulhrsw .Lfr_stream_center10(%rip), %ymm0, %ymm14
	vpmullw %ymm15, %ymm14, %ymm14
	vpsubw %ymm14, %ymm0, %ymm0
	vmovdqu %ymm0, 96(%rdi)
	.endm

	/* Destructive four-way schedule: odd inputs become Montgomery temporaries. */
	.macro FR_MONT_QWORD_PACKED4
	vpunpckhqdq %ymm1, %ymm0, %ymm8
	vpunpckhqdq %ymm3, %ymm2, %ymm9
	vpunpckhqdq %ymm5, %ymm4, %ymm10
	vpunpckhqdq %ymm7, %ymm6, %ymm11
	vpunpcklqdq %ymm1, %ymm0, %ymm0
	vpunpcklqdq %ymm3, %ymm2, %ymm2
	vpunpcklqdq %ymm5, %ymm4, %ymm4
	vpunpcklqdq %ymm7, %ymm6, %ymm6
	vpmullw .Ltile4_fwd_s5_pair_qinv+0(%rip), %ymm8, %ymm1
	vpmullw .Ltile4_fwd_s5_pair_qinv+32(%rip), %ymm9, %ymm3
	vpmullw .Ltile4_fwd_s5_pair_qinv+64(%rip), %ymm10, %ymm5
	vpmullw .Ltile4_fwd_s5_pair_qinv+96(%rip), %ymm11, %ymm7
	vpmulhw .Ltile4_fwd_s5_pair_factor+0(%rip), %ymm8, %ymm8
	vpmulhw .Ltile4_fwd_s5_pair_factor+32(%rip), %ymm9, %ymm9
	vpmulhw .Ltile4_fwd_s5_pair_factor+64(%rip), %ymm10, %ymm10
	vpmulhw .Ltile4_fwd_s5_pair_factor+96(%rip), %ymm11, %ymm11
	vpmulhw %ymm15, %ymm1, %ymm1
	vpmulhw %ymm15, %ymm3, %ymm3
	vpmulhw %ymm15, %ymm5, %ymm5
	vpmulhw %ymm15, %ymm7, %ymm7
	vpsubw %ymm1, %ymm8, %ymm8
	vpsubw %ymm3, %ymm9, %ymm9
	vpsubw %ymm5, %ymm10, %ymm10
	vpsubw %ymm7, %ymm11, %ymm11
	vpsubw %ymm8, %ymm0, %ymm1
	vpsubw %ymm9, %ymm2, %ymm3
	vpsubw %ymm10, %ymm4, %ymm5
	vpsubw %ymm11, %ymm6, %ymm7
	vpaddw %ymm8, %ymm0, %ymm0
	vpaddw %ymm9, %ymm2, %ymm2
	vpaddw %ymm10, %ymm4, %ymm4
	vpaddw %ymm11, %ymm6, %ymm6
	.endm

	.macro FR_RAW_CROSS4 l0,h0,l1,h1,l2,h2,l3,h3
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

	.macro FR_MONT_HALF_PAIR v0,v1,offset
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

	/* Leave pair-packed sum/difference instead of reconstructing two AoS vectors. */
	.macro FR_MONT_QWORD_PACKED v0,v1,offset
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

	/* Four packed S/D vectors -> four coefficient planes in twelve shuffles. */
	.macro FR_PACKED_TO_PLANES v0,v1,v2,v3,outoff
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
	.globl gt32_tile4_attr_forward_all_bm_soa_asm
	.type gt32_tile4_attr_forward_all_bm_soa_asm,@function
gt32_tile4_attr_forward_all_bm_soa_asm:
	vmovdqa .Lfr_q(%rip), %ymm15
	vmovdqa .Lfr_plane_pshufb(%rip), %ymm14
	movl $6, %ecx
	.p2align 5
.Lfr_core_loop:
	vmovdqu   0(%rsi), %ymm0
	vmovdqu  32(%rsi), %ymm1
	vmovdqu  64(%rsi), %ymm2
	vmovdqu  96(%rsi), %ymm3
	vmovdqu 128(%rsi), %ymm4
	vmovdqu 160(%rsi), %ymm5
	vmovdqu 192(%rsi), %ymm6
	vmovdqu 224(%rsi), %ymm7
	FR_RAW_CROSS4 %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7
	FR_MONT_CROSS4 %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, .Ltile4_fwd_s2_qinv,.Ltile4_fwd_s2_factor
	FR_MONT_CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, .Ltile4_fwd_s3_qinv,.Ltile4_fwd_s3_factor
	FR_MONT_HALF_PAIR %ymm0,%ymm1,0
	FR_MONT_HALF_PAIR %ymm2,%ymm3,32
	FR_MONT_HALF_PAIR %ymm4,%ymm5,64
	FR_MONT_HALF_PAIR %ymm6,%ymm7,96
	FR_MONT_QWORD_PACKED %ymm0,%ymm1,0
	FR_MONT_QWORD_PACKED %ymm2,%ymm3,32
	FR_PACKED_TO_PLANES %ymm0,%ymm1,%ymm2,%ymm3,0
	FR_MONT_QWORD_PACKED %ymm4,%ymm5,64
	FR_MONT_QWORD_PACKED %ymm6,%ymm7,96
	FR_PACKED_TO_PLANES %ymm4,%ymm5,%ymm6,%ymm7,128
	addq $256, %rsi
	addq $256, %rdi
	decl %ecx
	jne .Lfr_core_loop
	vzeroupper
	ret
	.size gt32_tile4_attr_forward_all_bm_soa_asm,.-gt32_tile4_attr_forward_all_bm_soa_asm

	.p2align 5
	.globl gt32_tile4_attr_forward_all_bm_soa_s5x4_asm
	.type gt32_tile4_attr_forward_all_bm_soa_s5x4_asm,@function
gt32_tile4_attr_forward_all_bm_soa_s5x4_asm:
	vmovdqa .Lfr_q(%rip), %ymm15
	vmovdqa .Lfr_plane_pshufb(%rip), %ymm14
	movl $6, %ecx
	.p2align 5
.Lfr_s5x4_loop:
	vmovdqu   0(%rsi), %ymm0
	vmovdqu  32(%rsi), %ymm1
	vmovdqu  64(%rsi), %ymm2
	vmovdqu  96(%rsi), %ymm3
	vmovdqu 128(%rsi), %ymm4
	vmovdqu 160(%rsi), %ymm5
	vmovdqu 192(%rsi), %ymm6
	vmovdqu 224(%rsi), %ymm7
	FR_RAW_CROSS4 %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7
	FR_MONT_CROSS4 %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, .Ltile4_fwd_s2_qinv,.Ltile4_fwd_s2_factor
	FR_MONT_CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, .Ltile4_fwd_s3_qinv,.Ltile4_fwd_s3_factor
	FR_MONT_HALF_PAIR %ymm0,%ymm1,0
	FR_MONT_HALF_PAIR %ymm2,%ymm3,32
	FR_MONT_HALF_PAIR %ymm4,%ymm5,64
	FR_MONT_HALF_PAIR %ymm6,%ymm7,96
	FR_MONT_QWORD_PACKED4
	FR_PACKED_TO_PLANES %ymm0,%ymm1,%ymm2,%ymm3,0
	FR_PACKED_TO_PLANES %ymm4,%ymm5,%ymm6,%ymm7,128
	addq $256, %rsi
	addq $256, %rdi
	decl %ecx
	jne .Lfr_s5x4_loop
	vzeroupper
	ret
	.size gt32_tile4_attr_forward_all_bm_soa_s5x4_asm,.-gt32_tile4_attr_forward_all_bm_soa_s5x4_asm

	/*
	 * A is materialized private SoA.  B enters as post-frontend TILE4 rows.
	 * Only the inactive post-stage3 half touches the 128-byte scratch buffer.
	 */
	.p2align 5
	.globl gt32_tile4_attr_forward_b_stream_bm_soa_asm
	.type gt32_tile4_attr_forward_b_stream_bm_soa_asm,@function
gt32_tile4_attr_forward_b_stream_bm_soa_asm:
	vmovdqa .Lfr_q(%rip), %ymm15
	leaq .Ltile4_bm_lambda(%rip), %r8
	leaq .Ltile4_bm_lambda_qinv(%rip), %r9
	movl $6, %r10d
	.p2align 5
.Lfr_stream_bm_loop:
	vmovdqu   0(%rdx), %ymm0
	vmovdqu  32(%rdx), %ymm1
	vmovdqu  64(%rdx), %ymm2
	vmovdqu  96(%rdx), %ymm3
	vmovdqu 128(%rdx), %ymm4
	vmovdqu 160(%rdx), %ymm5
	vmovdqu 192(%rdx), %ymm6
	vmovdqu 224(%rdx), %ymm7
	FR_RAW_CROSS4 %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7
	FR_MONT_CROSS4 %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, .Ltile4_fwd_s2_qinv,.Ltile4_fwd_s2_factor
	FR_MONT_CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, .Ltile4_fwd_s3_qinv,.Ltile4_fwd_s3_factor

	vmovdqu %ymm4,  0(%rcx)
	vmovdqu %ymm5, 32(%rcx)
	vmovdqu %ymm6, 64(%rcx)
	vmovdqu %ymm7, 96(%rcx)
	FR_MONT_HALF_PAIR %ymm0,%ymm1,0
	FR_MONT_HALF_PAIR %ymm2,%ymm3,32
	FR_MONT_QWORD_PACKED %ymm0,%ymm1,0
	FR_MONT_QWORD_PACKED %ymm2,%ymm3,32
	vmovdqa .Lfr_plane_pshufb(%rip), %ymm14
	FR_PACKED_TO_BM_REGS %ymm0,%ymm1,%ymm2,%ymm3
	FR_STREAM_BM_BLOCK

	vmovdqu  0(%rcx), %ymm0
	vmovdqu 32(%rcx), %ymm1
	vmovdqu 64(%rcx), %ymm2
	vmovdqu 96(%rcx), %ymm3
	FR_MONT_HALF_PAIR %ymm0,%ymm1,64
	FR_MONT_HALF_PAIR %ymm2,%ymm3,96
	FR_MONT_QWORD_PACKED %ymm0,%ymm1,64
	FR_MONT_QWORD_PACKED %ymm2,%ymm3,96
	vmovdqa .Lfr_plane_pshufb(%rip), %ymm14
	FR_PACKED_TO_BM_REGS %ymm0,%ymm1,%ymm2,%ymm3
	addq $128, %rsi
	addq $128, %rdi
	addq $32, %r8
	addq $32, %r9
	FR_STREAM_BM_BLOCK

	addq $128, %rsi
	addq $128, %rdi
	addq $32, %r8
	addq $32, %r9
	addq $256, %rdx
	decl %r10d
	jne .Lfr_stream_bm_loop
	vzeroupper
	ret
	.size gt32_tile4_attr_forward_b_stream_bm_soa_asm,.-gt32_tile4_attr_forward_b_stream_bm_soa_asm

	.section .rodata
	.p2align 5
.Lfr_q:
	.rept 16
	.short 3457
	.endr
/* Interleave matching words from the two packed 64-bit quartics per lane. */
.Lfr_plane_pshufb:
	.byte 0,1,8,9,2,3,10,11,4,5,12,13,6,7,14,15
	.byte 0,1,8,9,2,3,10,11,4,5,12,13,6,7,14,15
	.p2align 5
.Lfr_stream_qinv:
	.rept 16
	.short 12929
	.endr
.Lfr_stream_center10:
	.rept 16
	.short 10
	.endr

#include "../generated/tile4_basemul_constants.inc"
#include "../generated/tile4_constants.inc"

	.section .note.GNU-stack,"",@progbits
