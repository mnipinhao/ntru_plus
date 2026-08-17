/* GT-N32-BM-ISLAND-004: half-native B=33 leaf order, benchmark-only. */

	.text
	.p2align 5
	.globl gt32_n32_basemul_half_r1u_asm
	.type gt32_n32_basemul_half_r1u_asm,@function
gt32_n32_basemul_half_r1u_asm:
	leaq .Ln32_bm_lambda(%rip), %rcx
	leaq .Ln32_bm_lambda_qinv(%rip), %r8
	vmovdqa .Ln32_bm_d0(%rip), %ymm0
	vmovdqa .Ln32_bm_d1(%rip), %ymm1
	vmovdqa .Ln32_bm_d2(%rip), %ymm2
	vmovdqa .Ln32_bm_d3(%rip), %ymm3
	vmovdqa .Ln32_bm_pack_c01(%rip), %ymm4
	vmovdqa .Ln32_bm_pack_c23(%rip), %ymm5
	vmovdqa .Ln32_bm_qinv(%rip), %ymm14
	vmovdqa .Ln32_bm_q(%rip), %ymm15
	movl $48, %eax
	.p2align 5
.Ln32_bm_loop:
	vmovdqu (%rdx), %ymm12
	vmovdqu (%rsi), %ymm13

	/* lambda*b in the half-native physical leaf order. */
	vpmullw (%r8), %ymm12, %ymm10
	vpmulhw (%rcx), %ymm12, %ymm11
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm11, %ymm11

	/* Same qword-local D0..D3 arithmetic as qualified R1-U. */
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

	/* Bit-exact unsigned REDC16. */
	vpmullw %ymm14, %ymm9, %ymm10
	vpmullw %ymm14, %ymm8, %ymm11
	vpmulhuw %ymm15, %ymm10, %ymm10
	vpmulhuw %ymm15, %ymm11, %ymm11
	vpsrad $16, %ymm9, %ymm9
	vpsrad $16, %ymm8, %ymm8
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm11, %ymm8, %ymm8

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
	jne .Ln32_bm_loop
	vzeroupper
	ret
	.size gt32_n32_basemul_half_r1u_asm,.-gt32_n32_basemul_half_r1u_asm

	.section .rodata
#include "../generated/tile4_n32_gt_bm_island_constants.inc"

	.section .note.GNU-stack,"",@progbits
