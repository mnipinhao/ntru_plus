/* Gate 135: qword-local QL2 x QL2 -> QL2 general BaseMul, e=0. */
	.text
	.p2align 5
	.globl gt135_basemul_general_ql2_native_e0
	.type gt135_basemul_general_ql2_native_e0,@function
gt135_basemul_general_ql2_native_e0:
	leaq .Lgt135_ql2_lambda(%rip), %rcx
	leaq .Lgt135_ql2_lambda_qinv(%rip), %r8
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
.Lgt135_loop:
	vmovdqu (%rdx), %ymm12
	vmovdqu (%rsi), %ymm13

	/* lambda*b in e=0. */
	vpmullw (%r8), %ymm12, %ymm10
	vpmulhw (%rcx), %ymm12, %ymm11
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm11, %ymm11

	/* Four qword-local quartic dot products. */
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

	/* Exact unsigned 32->16 Montgomery reduction: e=0 x e=0 -> e=-1. */
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

	/* Mandatory general-B3 scale repayment: Mont(R^2), e=-1 -> e=0. */
	vpmullw .Lgt135_rsq_qinv(%rip), %ymm9, %ymm10
	vpmulhw .Lgt135_rsq(%rip), %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vmovdqu %ymm9, (%rdi)

	addq $32, %rsi
	addq $32, %rdx
	addq $32, %rdi
	addq $32, %rcx
	addq $32, %r8
	decl %eax
	jne .Lgt135_loop
	vzeroupper
	ret
	.size gt135_basemul_general_ql2_native_e0,.-gt135_basemul_general_ql2_native_e0

	.section .rodata
#include "../../avx2_gt32_tile4_official_001/generated/tile4_aos_dot_redc16_constants.inc"
#include "../generated/ql2_lambda.inc"
	.p2align 5
.Lgt135_rsq:
	.rept 16
	.short 867
	.endr
.Lgt135_rsq_qinv:
	.rept 16
	.short 2787
	.endr
	.section .note.GNU-stack,"",@progbits
