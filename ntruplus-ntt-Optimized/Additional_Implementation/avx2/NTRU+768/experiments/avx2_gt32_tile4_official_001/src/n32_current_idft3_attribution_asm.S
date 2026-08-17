/* Benchmark-only current-I1 -> IDFT3 common-endpoint adapter. */

	.text

	.macro CURRENT_IDFT3_DUAL
	vpaddw %ymm2, %ymm1, %ymm6
	vpsubw %ymm2, %ymm1, %ymm7
	vpaddw %ymm5, %ymm4, %ymm8
	vpsubw %ymm5, %ymm4, %ymm9
	vpmulhrsw %ymm14, %ymm6, %ymm10
	vpmulhrsw %ymm14, %ymm8, %ymm13
	vpsubw %ymm1, %ymm0, %ymm1
	vpsubw %ymm2, %ymm0, %ymm2
	vpsubw %ymm4, %ymm3, %ymm4
	vpsubw %ymm5, %ymm3, %ymm5
	vpmullw %ymm15, %ymm10, %ymm10
	vpmullw %ymm15, %ymm13, %ymm13
	vpsubw %ymm10, %ymm6, %ymm6
	vpsubw %ymm13, %ymm8, %ymm8
	vpmullw %ymm12, %ymm7, %ymm10
	vpmullw %ymm12, %ymm9, %ymm13
	vpmulhw %ymm11, %ymm7, %ymm7
	vpmulhw %ymm11, %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpmulhw %ymm15, %ymm13, %ymm13
	vpsubw %ymm10, %ymm7, %ymm7
	vpsubw %ymm13, %ymm9, %ymm9
	vpsubw %ymm7, %ymm1, %ymm1
	vpaddw %ymm7, %ymm2, %ymm2
	vpsubw %ymm9, %ymm4, %ymm4
	vpaddw %ymm9, %ymm5, %ymm5
	vpaddw %ymm6, %ymm0, %ymm0
	vpaddw %ymm8, %ymm3, %ymm3
	.endm

	.section .text.gt32_current_idft3_branch_row_asm,"ax",@progbits
	.p2align 5
	.globl gt32_current_idft3_branch_row_asm
	.type gt32_current_idft3_branch_row_asm,@function
gt32_current_idft3_branch_row_asm:
	vmovdqa .Ln32_current_idft_q(%rip), %ymm15
	vmovdqa .Ln32_current_idft_center10(%rip), %ymm14
	vmovdqa .Ln32_current_idft_w_qinv(%rip), %ymm12
	vmovdqa .Ln32_current_idft_w_factor(%rip), %ymm11
	movl $8, %ecx
.Ln32_current_idft_loop:
	/* Current I1 is (k3,branch,group); output is (branch,row,group). */
	vmovdqu    0(%rsi), %ymm0
	vmovdqu  512(%rsi), %ymm1
	vmovdqu 1024(%rsi), %ymm2
	vmovdqu  256(%rsi), %ymm3
	vmovdqu  768(%rsi), %ymm4
	vmovdqu 1280(%rsi), %ymm5
	CURRENT_IDFT3_DUAL
	/* Reach the same typed endpoint as N32: low halves are rows 1/2,
	 * high halves are reflected to rows 2/1. */
	vperm2i128 $0x30, %ymm2, %ymm1, %ymm6
	vperm2i128 $0x30, %ymm1, %ymm2, %ymm7
	vperm2i128 $0x30, %ymm5, %ymm4, %ymm8
	vperm2i128 $0x30, %ymm4, %ymm5, %ymm9
	vmovdqu %ymm0,    0(%rdi)
	vmovdqu %ymm6,  256(%rdi)
	vmovdqu %ymm7,  512(%rdi)
	vmovdqu %ymm3,  768(%rdi)
	vmovdqu %ymm8, 1024(%rdi)
	vmovdqu %ymm9, 1280(%rdi)
	addq $32, %rsi
	addq $32, %rdi
	decl %ecx
	jne .Ln32_current_idft_loop
	vzeroupper
	ret
	.size gt32_current_idft3_branch_row_asm,.-gt32_current_idft3_branch_row_asm

	.section .rodata
	.p2align 5
.Ln32_current_idft_q:
	.rept 16
	.short 3457
	.endr
	.p2align 5
.Ln32_current_idft_center10:
	.rept 16
	.short 10
	.endr
	.p2align 5
.Ln32_current_idft_w_qinv:
	.rept 16
	.short 13706
	.endr
	.p2align 5
.Ln32_current_idft_w_factor:
	.rept 16
	.short -886
	.endr

	.section .note.GNU-stack,"",@progbits
