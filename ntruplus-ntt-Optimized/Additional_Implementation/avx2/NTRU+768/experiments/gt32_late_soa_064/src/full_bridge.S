/* Reuse the measured 063 macros and fixed-island leaves verbatim. */
#include "../../gt32_late_soa_063/src/late_soa.S"

	.text
	.p2align 5
	.globl late_full_inverse_i2_asm
	.type late_full_inverse_i2_asm,@function
late_full_inverse_i2_asm:
	vmovdqa .Llate_q(%rip), %ymm15
	movl $6, %ecx
	.p2align 5
.Llate064_i2_loop:
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
	addq $256, %rsi
	addq $256, %rdi
	decl %ecx
	jne .Llate064_i2_loop
	vzeroupper
	ret
	.size late_full_inverse_i2_asm,.-late_full_inverse_i2_asm

	.p2align 5
	.globl late_soa_full_basemul_i2_fused_asm
	.type late_soa_full_basemul_i2_fused_asm,@function
late_soa_full_basemul_i2_fused_asm:
	leaq .Ltile4_bm_lambda(%rip), %r8
	leaq .Ltile4_bm_lambda_qinv(%rip), %r9
	vmovdqa .Llate_q(%rip), %ymm0
	movl $6, %ecx
	.p2align 5
.Llate064_bmi2_loop:
	LATE_SOA_BM_BLOCK 0,32
	LATE_SOA_BM_BLOCK 64,96
	decl %ecx
	jne .Llate064_bmi2_loop
	vzeroupper
	ret
	.size late_soa_full_basemul_i2_fused_asm,.-late_soa_full_basemul_i2_fused_asm
