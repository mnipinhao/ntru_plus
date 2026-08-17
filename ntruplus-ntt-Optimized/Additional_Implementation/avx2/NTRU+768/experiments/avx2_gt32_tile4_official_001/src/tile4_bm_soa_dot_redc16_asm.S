/*
 * GT32-BM-SOA-DOT-REDC16-001, benchmark-only.
 *
 * Persistent private SoA e=0 x SoA e=0 -> private SoA e=-1.  Each quartic
 * coefficient is accumulated exactly with four signed int16 products in two
 * vpmaddwd chains, then reduced once with R1-U's high-word REDC16.  Inputs,
 * output, and lambda streams all use the existing corrected physical-Q order.
 */

	.text

	.macro SOA_DOT_LAMBDA dst,src
	vpmullw (%r9), \src, %ymm11
	vpmulhw (%r8), \src, \dst
	vpmulhw .Lsoa_dot_q(%rip), %ymm11, %ymm11
	vpsubw %ymm11, \dst, \dst
	.endm

	.macro SOA_DOT_HALF unpack,ap0,ap1,b00,b01,b10,b11,dst
	\unpack \b01, \b00, %ymm11
	vpmaddwd %ymm11, \ap0, %ymm12
	\unpack \b11, \b10, %ymm11
	vpmaddwd %ymm11, \ap1, %ymm13
	vpaddd %ymm13, %ymm12, %ymm12

	/* Unsigned-low-word Montgomery finalizer, identical to R1-U. */
	vpmullw .Lsoa_dot_qinv(%rip), %ymm12, %ymm13
	vpmulhuw .Lsoa_dot_q(%rip), %ymm13, %ymm13
	vpsrad $16, %ymm12, %ymm12
	vpsubw %ymm13, %ymm12, %ymm12

	/* Extract eight valid even words into one XMM result half. */
	vpshufb .Lsoa_dot_compact_even(%rip), %ymm12, %ymm12
	vpermq $0xd8, %ymm12, %ymm12
	vmovdqa %ymm12, \dst
	.endm

	.macro SOA_DOT_COEFFICIENT outoff,b00,b01,b10,b11
	/* L/H unpack results are [0..3,8..11] and [4..7,12..15]. */
	SOA_DOT_HALF vpunpcklwd,%ymm0,%ymm2,\b00,\b01,\b10,\b11,%ymm14
	SOA_DOT_HALF vpunpckhwd,%ymm1,%ymm3,\b00,\b01,\b10,\b11,%ymm15
	vpunpcklqdq %ymm15, %ymm14, %ymm11
	vpunpckhqdq %ymm15, %ymm14, %ymm13
	vperm2i128 $0x20, %ymm13, %ymm11, %ymm12
	vmovdqu %ymm12, \outoff(%rdi)
	.endm

	.p2align 5
	.globl gt32_tile4_bm_soa_dot_redc16_asm
	.type gt32_tile4_bm_soa_dot_redc16_asm,@function
gt32_tile4_bm_soa_dot_redc16_asm:
	leaq .Ltile4_bm_lambda(%rip), %r8
	leaq .Ltile4_bm_lambda_qinv(%rip), %r9
	movl $12, %ecx
	.p2align 5
.Lsoa_dot_loop:
	/* Four A planes -> reusable A01/A23 low/high word pairs. */
	vmovdqu   0(%rsi), %ymm11
	vmovdqu  32(%rsi), %ymm12
	vmovdqu  64(%rsi), %ymm13
	vmovdqu  96(%rsi), %ymm14
	vpunpcklwd %ymm12, %ymm11, %ymm0
	vpunpckhwd %ymm12, %ymm11, %ymm1
	vpunpcklwd %ymm14, %ymm13, %ymm2
	vpunpckhwd %ymm14, %ymm13, %ymm3

	/* B0..B3 and the three wrapped lambda*B planes. */
	vmovdqu   0(%rdx), %ymm4
	vmovdqu  32(%rdx), %ymm5
	vmovdqu  64(%rdx), %ymm6
	vmovdqu  96(%rdx), %ymm7
	SOA_DOT_LAMBDA %ymm8,%ymm5
	SOA_DOT_LAMBDA %ymm9,%ymm6
	SOA_DOT_LAMBDA %ymm10,%ymm7

	/*
	 * c0: A01.[B0,LB3] + A23.[LB2,LB1]
	 * c1: A01.[B1,B0]  + A23.[LB3,LB2]
	 * c2: A01.[B2,B1]  + A23.[B0,LB3]
	 * c3: A01.[B3,B2]  + A23.[B1,B0]
	 */
	SOA_DOT_COEFFICIENT   0,%ymm4,%ymm10,%ymm9,%ymm8
	SOA_DOT_COEFFICIENT  32,%ymm5,%ymm4,%ymm10,%ymm9
	SOA_DOT_COEFFICIENT  64,%ymm6,%ymm5,%ymm4,%ymm10
	SOA_DOT_COEFFICIENT  96,%ymm7,%ymm6,%ymm5,%ymm4

	addq $128, %rsi
	addq $128, %rdx
	addq $128, %rdi
	addq $32, %r8
	addq $32, %r9
	decl %ecx
	jne .Lsoa_dot_loop
	vzeroupper
	ret
	.size gt32_tile4_bm_soa_dot_redc16_asm,.-gt32_tile4_bm_soa_dot_redc16_asm

	.section .rodata
	.p2align 5
.Lsoa_dot_q:
	.rept 16
	.short 3457
	.endr
.Lsoa_dot_qinv:
	.rept 16
	.short 12929
	.endr
.Lsoa_dot_compact_even:
	.byte 0,1,4,5,8,9,12,13,128,128,128,128,128,128,128,128
	.byte 0,1,4,5,8,9,12,13,128,128,128,128,128,128,128,128
#include "../generated/tile4_basemul_constants.inc"

	.section .note.GNU-stack,"",@progbits
