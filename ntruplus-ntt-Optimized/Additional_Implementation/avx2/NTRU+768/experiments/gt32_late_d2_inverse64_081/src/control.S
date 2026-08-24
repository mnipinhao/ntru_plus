	.text
	.macro CROSS4 l0,h0,l1,h1,l2,h2,l3,h3,qinv,factor
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

	.p2align 5
	.globl control_inverse_cross3_asm
	.type control_inverse_cross3_asm,@function
control_inverse_cross3_asm:
	vmovdqa .Lctl_q(%rip), %ymm15
	vmovdqu   0(%rsi), %ymm0
	vmovdqu  32(%rsi), %ymm1
	vmovdqu  64(%rsi), %ymm2
	vmovdqu  96(%rsi), %ymm3
	vmovdqu 128(%rsi), %ymm4
	vmovdqu 160(%rsi), %ymm5
	vmovdqu 192(%rsi), %ymm6
	vmovdqu 224(%rsi), %ymm7
	CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7,.Ltile4_inv_s2_qinv,.Ltile4_inv_s2_factor
	CROSS4 %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7,.Ltile4_inv_s3_qinv,.Ltile4_inv_s3_factor
	CROSS4 %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7,.Ltile4_inv_s4_qinv,.Ltile4_inv_s4_factor
	vmovdqu %ymm0,   0(%rdi)
	vmovdqu %ymm1,  32(%rdi)
	vmovdqu %ymm2,  64(%rdi)
	vmovdqu %ymm3,  96(%rdi)
	vmovdqu %ymm4, 128(%rdi)
	vmovdqu %ymm5, 160(%rdi)
	vmovdqu %ymm6, 192(%rdi)
	vmovdqu %ymm7, 224(%rdi)
	vzeroupper
	ret
	.size control_inverse_cross3_asm,.-control_inverse_cross3_asm

	.macro TRANSPOSE s0,s1,s2,s3,t0,t1,t2,t3
	vpunpcklwd \s1, \s0, \t0
	vpunpckhwd \s1, \s0, \t1
	vpunpcklwd \s3, \s2, \t2
	vpunpckhwd \s3, \s2, \t3
	vpunpckldq \t2, \t0, \s0
	vpunpckhdq \t2, \t0, \s1
	vpunpckldq \t3, \t1, \s2
	vpunpckhdq \t3, \t1, \s3
	/* s0..s3 now hold adjacent quartic pairs in each 128-bit half. */
	vperm2i128 $0x20, \s1, \s0, \t0
	vperm2i128 $0x20, \s3, \s2, \t1
	vperm2i128 $0x31, \s1, \s0, \t2
	vperm2i128 $0x31, \s3, \s2, \t3
	.endm

	.p2align 5
	.globl hwa_to_tile4_asm
	.type hwa_to_tile4_asm,@function
hwa_to_tile4_asm:
	vmovdqu 0(%rsi), %ymm0
	vmovdqu 64(%rsi), %ymm1
	vmovdqu 128(%rsi), %ymm2
	vmovdqu 192(%rsi), %ymm3
	TRANSPOSE %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7
	vmovdqu %ymm4, 0(%rdi)
	vmovdqu %ymm5, 32(%rdi)
	vmovdqu %ymm6, 64(%rdi)
	vmovdqu %ymm7, 96(%rdi)
	vmovdqu 32(%rsi), %ymm0
	vmovdqu 96(%rsi), %ymm1
	vmovdqu 160(%rsi), %ymm2
	vmovdqu 224(%rsi), %ymm3
	TRANSPOSE %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7
	vmovdqu %ymm4, 128(%rdi)
	vmovdqu %ymm5, 160(%rdi)
	vmovdqu %ymm6, 192(%rdi)
	vmovdqu %ymm7, 224(%rdi)
	vzeroupper
	ret
	.size hwa_to_tile4_asm,.-hwa_to_tile4_asm

	.section .rodata
	.p2align 5
.Lctl_q:
	.rept 16
	.short 3457
	.endr
#include "../../avx2_gt32_tile4_official_001/generated/tile4_constants.inc"
	.section .note.GNU-stack,"",@progbits
