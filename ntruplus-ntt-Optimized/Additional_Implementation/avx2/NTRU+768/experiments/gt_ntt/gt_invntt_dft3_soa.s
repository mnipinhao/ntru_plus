.text

/*
 * One lane-local inverse DFT3 followed by three packed Barrett checkpoints.
 *
 * ymm0..ymm2  : y0, y1, y2
 * ymm3        : y2-y1, then Montgomery product
 * ymm4        : Montgomery correction
 * ymm5..ymm7  : raw x0, x1, x2, then reduced outputs
 * ymm8..ymm10 : three Barrett quotients
 * ymm11       : q = 3457
 * ymm12       : packed Barrett reciprocal = 19412
 * ymm13       : omega3*qinv mod 2^16 = 13706
 * ymm14       : omega3 = -886
 * ymm15       : free
 */
.macro INTT_DFT3_BARRETT
	vmovdqa    0(%rdi), %ymm0
	vmovdqa  512(%rdi), %ymm1
	vmovdqa 1024(%rdi), %ymm2

	/* Start the only Montgomery chain. */
	vpsubw  %ymm1,  %ymm2, %ymm3
	vpmullw %ymm13, %ymm3, %ymm4
	vpmulhw %ymm14, %ymm3, %ymm3

	/* Independent DFT3 partials fill the multiply latency. */
	vpaddw %ymm1, %ymm0, %ymm5
	vpsubw %ymm1, %ymm0, %ymm6
	vpsubw %ymm2, %ymm0, %ymm7
	vpaddw %ymm2, %ymm5, %ymm5

	vpmulhw %ymm11, %ymm4, %ymm4
	vpsubw  %ymm4,  %ymm3, %ymm3
	vpaddw  %ymm3,  %ymm6, %ymm6
	vpsubw  %ymm3,  %ymm7, %ymm7

	/* Interleave three independent packed Barrett chains. */
	vpmulhw %ymm12, %ymm5,  %ymm8
	vpmulhw %ymm12, %ymm6,  %ymm9
	vpmulhw %ymm12, %ymm7, %ymm10
	vpsraw  $10, %ymm8,  %ymm8
	vpsraw  $10, %ymm9,  %ymm9
	vpsraw  $10, %ymm10, %ymm10
	vpmullw %ymm11, %ymm8,  %ymm8
	vpmullw %ymm11, %ymm9,  %ymm9
	vpmullw %ymm11, %ymm10, %ymm10
	vpsubw  %ymm8,  %ymm5, %ymm5
	vpsubw  %ymm9,  %ymm6, %ymm6
	vpsubw  %ymm10, %ymm7, %ymm7

	vmovdqa %ymm5,    0(%rdi)
	vmovdqa %ymm6,  512(%rdi)
	vmovdqa %ymm7, 1024(%rdi)
.endm

/*
 * void gt_invntt_soa_dft3_asm(int16_t rows[768])
 *
 * rows is a 32-byte-aligned, in-place scratch buffer.  For each of the
 * 16 (group, coefficient) vectors, y0/y1/y2 are 512 bytes apart.  Inputs and
 * exact outputs are in [0,q], matching gt_invntt_soa_dft3_intrinsic.
 */
.p2align 5
.globl gt_invntt_soa_dft3_asm
.type gt_invntt_soa_dft3_asm,@function
gt_invntt_soa_dft3_asm:
	vmovdqa .Ldft3_q(%rip), %ymm11
	vmovdqa .Ldft3_barrett_v(%rip), %ymm12
	vmovdqa .Ldft3_omega3_qinv(%rip), %ymm13
	vmovdqa .Ldft3_omega3(%rip), %ymm14
	movl $16, %ecx
.p2align 5
.Ldft3_loop:
	INTT_DFT3_BARRETT
	addq $32, %rdi
	decl %ecx
	jne .Ldft3_loop

	vzeroupper
	ret
.size gt_invntt_soa_dft3_asm,.-gt_invntt_soa_dft3_asm

.section .rodata
.p2align 5
.Ldft3_q:
	.rept 16
	.short 3457
	.endr
.Ldft3_barrett_v:
	.rept 16
	.short 19412
	.endr
.Ldft3_omega3_qinv:
	.rept 16
	.short 13706
	.endr
.Ldft3_omega3:
	.rept 16
	.short -886
	.endr

#ifndef GT_INVNTT_FUSED_INCLUDE
.section .note.GNU-stack,"",@progbits
#endif
