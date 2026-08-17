/* Zero-spill BaseInv-terminal -> native-BaseMul executable gate.
 * rdi=product, rsi=other, rdx=pre-sign adjugate, rcx=inverted determinants. */
	.text

	/* Matched materializing control; fifth argument r8 is inverse scratch. */
	.p2align 5
	.globl gt32_p_baseinv_apply_inverse_bm_control_asm
	.type gt32_p_baseinv_apply_inverse_bm_control_asm,@function
gt32_p_baseinv_apply_inverse_bm_control_asm:
	movq %rdi, %r11
	movq %rsi, %r10
	movq %r8, %rax
	vmovdqa .Ledge_q(%rip), %ymm0
	movl $12, %r9d
	.p2align 5
.Ledge_control_finish:
	vmovdqu (%rcx), %ymm15
	vpmullw .Ledge_qinv(%rip), %ymm15, %ymm13
	vmovdqu 0(%rdx), %ymm9
	vpmullw %ymm13, %ymm9, %ymm14
	vpmulhw %ymm15, %ymm9, %ymm9
	vpmulhw %ymm0, %ymm14, %ymm14
	vpsubw %ymm14, %ymm9, %ymm9
	vmovdqu 32(%rdx), %ymm10
	vpmullw %ymm13, %ymm10, %ymm14
	vpmulhw %ymm15, %ymm10, %ymm10
	vpmulhw %ymm0, %ymm14, %ymm14
	vpsubw %ymm14, %ymm10, %ymm10
	vmovdqu 64(%rdx), %ymm11
	vpmullw %ymm13, %ymm11, %ymm14
	vpmulhw %ymm15, %ymm11, %ymm11
	vpmulhw %ymm0, %ymm14, %ymm14
	vpsubw %ymm14, %ymm11, %ymm11
	vmovdqu 96(%rdx), %ymm12
	vpmullw %ymm13, %ymm12, %ymm14
	vpmulhw %ymm15, %ymm12, %ymm12
	vpmulhw %ymm0, %ymm14, %ymm14
	vpsubw %ymm14, %ymm12, %ymm12
	vpxor %ymm14, %ymm14, %ymm14
	vpsubw %ymm10, %ymm14, %ymm10
	vpsubw %ymm12, %ymm14, %ymm12
	vmovdqu %ymm9, 0(%r8)
	vmovdqu %ymm10, 32(%r8)
	vmovdqu %ymm11, 64(%r8)
	vmovdqu %ymm12, 96(%r8)
	addq $128, %rdx
	addq $128, %r8
	addq $32, %rcx
	decl %r9d
	jne .Ledge_control_finish
	movq %r11, %rdi
	movq %r10, %rsi
	movq %rax, %rdx
	jmp gt_basemul_native_asm_avx2
	.size gt32_p_baseinv_apply_inverse_bm_control_asm,.-gt32_p_baseinv_apply_inverse_bm_control_asm

	.macro EDGE_MONT_FIRST a, aq, b
	vpmullw %\aq, %\b, %ymm13
	vpmulhw %\a, %\b, %ymm15
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw %ymm13, %ymm15, %ymm15
	.endm
	.macro EDGE_MONT_ADD a, aq, b
	vpmullw %\aq, %\b, %ymm13
	vpmulhw %\a, %\b, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw %ymm13, %ymm14, %ymm14
	vpaddw %ymm14, %ymm15, %ymm15
	.endm
	.macro EDGE_MONT_LAMBDA
	vpmullw (%r9), %ymm15, %ymm13
	vpmulhw (%r8), %ymm15, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw %ymm13, %ymm14, %ymm15
	.endm
	.macro EDGE_MONT_RSQ
	vpmullw .Ledge_rsq_qinv(%rip), %ymm15, %ymm13
	vpmulhw .Ledge_rsq(%rip), %ymm15, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw %ymm13, %ymm14, %ymm15
	.endm

	.p2align 5
	.globl gt32_p_baseinv_apply_inverse_bm_asm
	.type gt32_p_baseinv_apply_inverse_bm_asm,@function
gt32_p_baseinv_apply_inverse_bm_asm:
	leaq gt_native_lambda(%rip), %r8
	leaq gt_native_lambda_qinv(%rip), %r9
	vmovdqa .Ledge_q(%rip), %ymm0
	movl $12, %r10d
	.p2align 5
.Ledge_batch:
	vmovdqu 0(%rsi), %ymm1
	vmovdqu 32(%rsi), %ymm2
	vmovdqu 64(%rsi), %ymm3
	vmovdqu 96(%rsi), %ymm4

	/* Form the final inverse planes in their BM-resident registers. */
	vmovdqu (%rcx), %ymm15
	vpmullw .Ledge_qinv(%rip), %ymm15, %ymm13
	vmovdqu 0(%rdx), %ymm9
	vpmullw %ymm13, %ymm9, %ymm14
	vpmulhw %ymm15, %ymm9, %ymm9
	vpmulhw %ymm0, %ymm14, %ymm14
	vpsubw %ymm14, %ymm9, %ymm9
	vmovdqu 32(%rdx), %ymm10
	vpmullw %ymm13, %ymm10, %ymm14
	vpmulhw %ymm15, %ymm10, %ymm10
	vpmulhw %ymm0, %ymm14, %ymm14
	vpsubw %ymm14, %ymm10, %ymm10
	vmovdqu 64(%rdx), %ymm11
	vpmullw %ymm13, %ymm11, %ymm14
	vpmulhw %ymm15, %ymm11, %ymm11
	vpmulhw %ymm0, %ymm14, %ymm14
	vpsubw %ymm14, %ymm11, %ymm11
	vmovdqu 96(%rdx), %ymm12
	vpmullw %ymm13, %ymm12, %ymm14
	vpmulhw %ymm15, %ymm12, %ymm12
	vpmulhw %ymm0, %ymm14, %ymm14
	vpsubw %ymm14, %ymm12, %ymm12
	vpxor %ymm14, %ymm14, %ymm14
	vpsubw %ymm10, %ymm14, %ymm10
	vpsubw %ymm12, %ymm14, %ymm12

	vpmullw .Ledge_qinv(%rip), %ymm1, %ymm5
	vpmullw .Ledge_qinv(%rip), %ymm2, %ymm6
	vpmullw .Ledge_qinv(%rip), %ymm3, %ymm7
	vpmullw .Ledge_qinv(%rip), %ymm4, %ymm8

	EDGE_MONT_FIRST ymm2, ymm6, ymm12
	EDGE_MONT_ADD ymm3, ymm7, ymm11
	EDGE_MONT_ADD ymm4, ymm8, ymm10
	EDGE_MONT_LAMBDA
	EDGE_MONT_ADD ymm1, ymm5, ymm9
	EDGE_MONT_RSQ
	vmovdqu %ymm15, 0(%rdi)

	EDGE_MONT_FIRST ymm3, ymm7, ymm12
	EDGE_MONT_ADD ymm4, ymm8, ymm11
	EDGE_MONT_LAMBDA
	EDGE_MONT_ADD ymm1, ymm5, ymm10
	EDGE_MONT_ADD ymm2, ymm6, ymm9
	EDGE_MONT_RSQ
	vmovdqu %ymm15, 32(%rdi)

	EDGE_MONT_FIRST ymm4, ymm8, ymm12
	EDGE_MONT_LAMBDA
	EDGE_MONT_ADD ymm1, ymm5, ymm11
	EDGE_MONT_ADD ymm2, ymm6, ymm10
	EDGE_MONT_ADD ymm3, ymm7, ymm9
	EDGE_MONT_RSQ
	vmovdqu %ymm15, 64(%rdi)

	EDGE_MONT_FIRST ymm1, ymm5, ymm12
	EDGE_MONT_ADD ymm2, ymm6, ymm11
	EDGE_MONT_ADD ymm3, ymm7, ymm10
	EDGE_MONT_ADD ymm4, ymm8, ymm9
	EDGE_MONT_RSQ
	vmovdqu %ymm15, 96(%rdi)

	addq $128, %rdi
	addq $128, %rsi
	addq $128, %rdx
	addq $32, %rcx
	addq $32, %r8
	addq $32, %r9
	decl %r10d
	jne .Ledge_batch
	vzeroupper
	ret
	.size gt32_p_baseinv_apply_inverse_bm_asm,.-gt32_p_baseinv_apply_inverse_bm_asm

	.section .rodata
	.p2align 5
.Ledge_q:
	.rept 16
	.short 3457
	.endr
.Ledge_qinv:
	.rept 16
	.short 12929
	.endr
.Ledge_rsq:
	.rept 16
	.short 867
	.endr
.Ledge_rsq_qinv:
	.rept 16
	.short 2787
	.endr
	.section .note.GNU-stack,"",@progbits
