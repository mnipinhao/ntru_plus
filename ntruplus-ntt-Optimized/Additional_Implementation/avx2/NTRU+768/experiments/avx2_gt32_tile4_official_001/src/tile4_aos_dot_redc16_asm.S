/*
 * GT32-AOS-DOT-REDC16-001, benchmark-only.
 *
 * This keeps A1's TILE4 AoS D0..D3/vpmaddwd algebra and replaces only its
 * vpmulld Montgomery32 finalizer.  R1-U interprets m as uint16 and is
 * bit-exact to A1.  R1-S interprets m as int16 and returns A1 or A1+q.
 * Both symbols are leaf functions with fixed public addresses and loops.
 */

	.text

	.macro AOS_DOT_REDC16_FUNCTION name,mulhigh
	.p2align 5
	.globl \name
	.type \name,@function
\name:
	leaq .Laos_dot_lambda(%rip), %rcx
	leaq .Laos_dot_lambda_qinv(%rip), %r8
	vmovdqa .Laos_dot_d0(%rip), %ymm0
	vmovdqa .Laos_dot_d1(%rip), %ymm1
	vmovdqa .Laos_dot_d2(%rip), %ymm2
	vmovdqa .Laos_dot_d3(%rip), %ymm3
	vmovdqa .Laos_dot_pack_c01(%rip), %ymm4
	vmovdqa .Laos_dot_pack_c23(%rip), %ymm5
	vmovdqa .Laos_dot_qinv(%rip), %ymm14
	vmovdqa .Laos_dot_q(%rip), %ymm15
	movl $48, %eax
	.p2align 5
.Laos_dot_loop\@:
	vmovdqu (%rdx), %ymm12
	vmovdqu (%rsi), %ymm13

	/* lambda*b with precomputed lambda*qinv. */
	vpmullw (%r8), %ymm12, %ymm10
	vpmulhw (%rcx), %ymm12, %ymm11
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm11, %ymm11

	/* A1's exact D0..D3 qword-local dot-product construction. */
	vpblendw $0xee, %ymm11, %ymm12, %ymm10
	vpshufb %ymm0, %ymm10, %ymm9
	vpmaddwd %ymm9, %ymm13, %ymm9
	vpblendw $0xcc, %ymm10, %ymm12, %ymm8
	vpshufb %ymm1, %ymm8, %ymm8
	vpmaddwd %ymm8, %ymm13, %ymm8
	vphaddd %ymm8, %ymm9, %ymm9

	vpblendw $0x88, %ymm10, %ymm12, %ymm8
	vpshufb %ymm2, %ymm8, %ymm8
	vpmaddwd %ymm8, %ymm13, %ymm8
	vpshufb %ymm3, %ymm12, %ymm7
	vpmaddwd %ymm7, %ymm13, %ymm7
	vphaddd %ymm7, %ymm8, %ymm8

	/* Two parallel 32->16 high-word Montgomery reductions. */
	vpmullw %ymm14, %ymm9, %ymm10
	vpmullw %ymm14, %ymm8, %ymm11
	\mulhigh %ymm15, %ymm10, %ymm10
	\mulhigh %ymm15, %ymm11, %ymm11
	vpsrad $16, %ymm9, %ymm9
	vpsrad $16, %ymm8, %ymm8
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm11, %ymm8, %ymm8

	/* Compact only the valid even words directly into final AoS order. */
	vpshufb %ymm4, %ymm9, %ymm9
	vpshufb %ymm5, %ymm8, %ymm8
	vpor %ymm8, %ymm9, %ymm9
	vmovdqu %ymm9, (%rdi)

	addq $32, %rsi
	addq $32, %rdx
	addq $32, %rdi
	addq $32, %rcx
	addq $32, %r8
	decl %eax
	jne .Laos_dot_loop\@
	vzeroupper
	ret
	.size \name,.-\name
	.endm

	AOS_DOT_REDC16_FUNCTION gt32_tile4_basemul_aos_dot_r1u_asm,vpmulhuw
	/* Typed alias: both e=0 inputs must come directly from GT32 Forward. */
	.globl gt32_tile4_basemul_scale_ff_aos_r1u_asm
	.type gt32_tile4_basemul_scale_ff_aos_r1u_asm,@function
	.set gt32_tile4_basemul_scale_ff_aos_r1u_asm,gt32_tile4_basemul_aos_dot_r1u_asm
	.size gt32_tile4_basemul_scale_ff_aos_r1u_asm,.-gt32_tile4_basemul_aos_dot_r1u_asm
	AOS_DOT_REDC16_FUNCTION gt32_tile4_basemul_aos_dot_r1s_asm,vpmulhw

	.section .rodata
#include "../generated/tile4_aos_dot_redc16_constants.inc"

	.section .note.GNU-stack,"",@progbits
