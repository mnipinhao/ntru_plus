/* Reuse the measured 063/064 Late-SoA implementation verbatim. */
#include "../../gt32_late_soa_064/src/full_bridge.S"

	.text
	.p2align 5
	.globl late066_inverse_prefix_m_to_post_i1_asm
	.type late066_inverse_prefix_m_to_post_i1_asm,@function
late066_inverse_prefix_m_to_post_i1_asm:
	vmovdqa .Llate_q(%rip), %ymm15
	movl $6, %ecx
	.p2align 5
.Llate066_prefix_loop:
	vmovdqu   0(%rsi), %ymm0
	vmovdqu  32(%rsi), %ymm1
	vmovdqu  64(%rsi), %ymm2
	vmovdqu  96(%rsi), %ymm3
	vmovdqu 128(%rsi), %ymm4
	vmovdqu 160(%rsi), %ymm5
	vmovdqu 192(%rsi), %ymm6
	vmovdqu 224(%rsi), %ymm7

	/* Production M-entry transpose with inverse stage 0 absorbed. */
	vpunpckhwd %ymm1, %ymm0, %ymm8
	vpunpcklwd %ymm1, %ymm0, %ymm0
	vpunpckhwd %ymm3, %ymm2, %ymm1
	vpunpcklwd %ymm3, %ymm2, %ymm2
	vpunpckhwd %ymm5, %ymm4, %ymm3
	vpunpcklwd %ymm5, %ymm4, %ymm4
	vpunpckhwd %ymm7, %ymm6, %ymm5
	vpunpcklwd %ymm7, %ymm6, %ymm6
	vpsubw %ymm8, %ymm0, %ymm7
	vpsubw %ymm1, %ymm2, %ymm9
	vpsubw %ymm3, %ymm4, %ymm10
	vpsubw %ymm5, %ymm6, %ymm11
	vpaddw %ymm8, %ymm0, %ymm0
	vpaddw %ymm1, %ymm2, %ymm2
	vpaddw %ymm3, %ymm4, %ymm4
	vpaddw %ymm5, %ymm6, %ymm6
	vpunpckhdq %ymm2, %ymm0, %ymm1
	vpunpckldq %ymm2, %ymm0, %ymm0
	vpunpckhdq %ymm9, %ymm7, %ymm2
	vpunpckldq %ymm9, %ymm7, %ymm7
	vpunpckhdq %ymm6, %ymm4, %ymm3
	vpunpckldq %ymm6, %ymm4, %ymm4
	vpunpckhdq %ymm11, %ymm10, %ymm5
	vpunpckldq %ymm11, %ymm10, %ymm10
	vpunpckhqdq %ymm7, %ymm0, %ymm6
	vpunpcklqdq %ymm7, %ymm0, %ymm0
	vpunpckhqdq %ymm2, %ymm1, %ymm7
	vpunpcklqdq %ymm2, %ymm1, %ymm1
	vpunpckhqdq %ymm10, %ymm4, %ymm2
	vpunpcklqdq %ymm10, %ymm4, %ymm4
	vpunpckhqdq %ymm5, %ymm3, %ymm8
	vpunpcklqdq %ymm5, %ymm3, %ymm3

	/* Production inverse stage 1. */
	vperm2i128 $0x20, %ymm6, %ymm0, %ymm5
	vperm2i128 $0x31, %ymm6, %ymm0, %ymm9
	vpmullw .Ltile4_inv_s1_pair_qinv+0(%rip), %ymm9, %ymm10
	vpmulhw .Ltile4_inv_s1_pair_factor+0(%rip), %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm9, %ymm5, %ymm10
	vpaddw %ymm9, %ymm5, %ymm5
	vperm2i128 $0x20, %ymm10, %ymm5, %ymm0
	vperm2i128 $0x31, %ymm10, %ymm5, %ymm6

	vperm2i128 $0x20, %ymm7, %ymm1, %ymm5
	vperm2i128 $0x31, %ymm7, %ymm1, %ymm9
	vpmullw .Ltile4_inv_s1_pair_qinv+32(%rip), %ymm9, %ymm10
	vpmulhw .Ltile4_inv_s1_pair_factor+32(%rip), %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm9, %ymm5, %ymm10
	vpaddw %ymm9, %ymm5, %ymm5
	vperm2i128 $0x20, %ymm10, %ymm5, %ymm1
	vperm2i128 $0x31, %ymm10, %ymm5, %ymm7

	vperm2i128 $0x20, %ymm2, %ymm4, %ymm5
	vperm2i128 $0x31, %ymm2, %ymm4, %ymm9
	vpmullw .Ltile4_inv_s1_pair_qinv+64(%rip), %ymm9, %ymm10
	vpmulhw .Ltile4_inv_s1_pair_factor+64(%rip), %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm9, %ymm5, %ymm10
	vpaddw %ymm9, %ymm5, %ymm5
	vperm2i128 $0x20, %ymm10, %ymm5, %ymm4
	vperm2i128 $0x31, %ymm10, %ymm5, %ymm2

	vperm2i128 $0x20, %ymm8, %ymm3, %ymm5
	vperm2i128 $0x31, %ymm8, %ymm3, %ymm9
	vpmullw .Ltile4_inv_s1_pair_qinv+96(%rip), %ymm9, %ymm10
	vpmulhw .Ltile4_inv_s1_pair_factor+96(%rip), %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm9, %ymm5, %ymm10
	vpaddw %ymm9, %ymm5, %ymm5
	vperm2i128 $0x20, %ymm10, %ymm5, %ymm3
	vperm2i128 $0x31, %ymm10, %ymm5, %ymm8

	/* Post-I1 order consumed by the shared inverse remainder. */
	vmovdqu %ymm0,   0(%rdi)
	vmovdqu %ymm6,  32(%rdi)
	vmovdqu %ymm1,  64(%rdi)
	vmovdqu %ymm7,  96(%rdi)
	vmovdqu %ymm4, 128(%rdi)
	vmovdqu %ymm2, 160(%rdi)
	vmovdqu %ymm3, 192(%rdi)
	vmovdqu %ymm8, 224(%rdi)
	addq $256, %rsi
	addq $256, %rdi
	decl %ecx
	jne .Llate066_prefix_loop
	vzeroupper
	ret
	.size late066_inverse_prefix_m_to_post_i1_asm,.-late066_inverse_prefix_m_to_post_i1_asm
