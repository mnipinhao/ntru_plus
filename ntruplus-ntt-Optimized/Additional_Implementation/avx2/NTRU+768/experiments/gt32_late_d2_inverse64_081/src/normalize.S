	.text
	.macro NORM value,tmp
	vpmullw .Ld2_norm32_qinv(%rip), \value, \tmp
	vpmulhw .Ld2_norm32_factor(%rip), \value, \value
	vpmulhw .Ld2_q(%rip), \tmp, \tmp
	vpsubw \tmp, \value, \value
	.endm
	.p2align 5
	.globl inverse32_normalize_asm
	.type inverse32_normalize_asm,@function
inverse32_normalize_asm:
	vmovdqu   0(%rsi), %ymm0
	vmovdqu  32(%rsi), %ymm1
	vmovdqu  64(%rsi), %ymm2
	vmovdqu  96(%rsi), %ymm3
	vmovdqu 128(%rsi), %ymm4
	vmovdqu 160(%rsi), %ymm5
	vmovdqu 192(%rsi), %ymm6
	vmovdqu 224(%rsi), %ymm7
	NORM %ymm0,%ymm8
	NORM %ymm1,%ymm8
	NORM %ymm2,%ymm8
	NORM %ymm3,%ymm8
	NORM %ymm4,%ymm8
	NORM %ymm5,%ymm8
	NORM %ymm6,%ymm8
	NORM %ymm7,%ymm8
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
	.size inverse32_normalize_asm,.-inverse32_normalize_asm
	.section .rodata
#include "../generated/inverse64_constants.inc"
	.section .note.GNU-stack,"",@progbits
