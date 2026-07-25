.text

/*
 * Convert four coefficient vectors into eight quartic block pairs.
 * ymm0..ymm3 contain [low-branch blocks | high-branch blocks].
 */
.macro POST_TRANSPOSE4X8
	vpunpcklwd %ymm1, %ymm0, %ymm4
	vpunpckhwd %ymm1, %ymm0, %ymm5
	vpunpcklwd %ymm3, %ymm2, %ymm6
	vpunpckhwd %ymm3, %ymm2, %ymm7
	vpunpckldq %ymm6, %ymm4, %ymm0
	vpunpckhdq %ymm6, %ymm4, %ymm1
	vpunpckldq %ymm7, %ymm5, %ymm2
	vpunpckhdq %ymm7, %ymm5, %ymm3
.endm

/* Store two public CRT blocks from both output branches. */
.macro POST_STORE_PAIR reg, index
	vextracti128 $1, %ymm\reg, %xmm4
	movzbl \index(%rdx), %eax
	vmovq %xmm\reg, (%rdi,%rax,8)
	vmovq %xmm4, 768(%rdi,%rax,8)
	movzbl \index+1(%rdx), %eax
	vpextrq $1, %xmm\reg, (%rdi,%rax,8)
	vpextrq $1, %xmm4, 768(%rdi,%rax,8)
.endm

/*
 * One (n3,Q-group) postprocess iteration.
 *
 * ymm0..ymm3  : four coefficients, then correction/high output
 * ymm4..ymm7  : Montgomery temporaries, then transpose temporaries
 * ymm8..ymm11 : branch sums, then normalized low output
 * ymm12..ymm13: current qinv/factor pair
 * ymm14       : free
 * ymm15       : q = 3457
 */
.macro POSTPROCESS_GROUP ninv_pair, two_ninv_pair
	vmovdqa  0(%rsi), %ymm0
	vmovdqa 32(%rsi), %ymm1
	vmovdqa 64(%rsi), %ymm2
	vmovdqa 96(%rsi), %ymm3
	vmovdqa (%r9), %ymm12
	vmovdqa (%r8), %ymm13

	/* Four independent fixed-factor untwist products. */
	vpmullw %ymm12, %ymm0, %ymm4
	vpmullw %ymm12, %ymm1, %ymm5
	vpmullw %ymm12, %ymm2, %ymm6
	vpmullw %ymm12, %ymm3, %ymm7
	vpmulhw %ymm13, %ymm0, %ymm0
	vpmulhw %ymm13, %ymm1, %ymm1
	vpmulhw %ymm13, %ymm2, %ymm2
	vpmulhw %ymm13, %ymm3, %ymm3
	vpmulhw %ymm15, %ymm4, %ymm4
	vpmulhw %ymm15, %ymm5, %ymm5
	vpmulhw %ymm15, %ymm6, %ymm6
	vpmulhw %ymm15, %ymm7, %ymm7
	vpsubw %ymm4, %ymm0, %ymm0
	vpsubw %ymm5, %ymm1, %ymm1
	vpsubw %ymm6, %ymm2, %ymm2
	vpsubw %ymm7, %ymm3, %ymm3

	/* Split branches only after all four untwist chains finish. */
	vextracti128 $1, %ymm0, %xmm4
	vextracti128 $1, %ymm1, %xmm5
	vextracti128 $1, %ymm2, %xmm6
	vextracti128 $1, %ymm3, %xmm7
	vpaddw %xmm4, %xmm0,  %xmm8
	vpaddw %xmm5, %xmm1,  %xmm9
	vpaddw %xmm6, %xmm2, %xmm10
	vpaddw %xmm7, %xmm3, %xmm11
	vpsubw %xmm4, %xmm0, %xmm0
	vpsubw %xmm5, %xmm1, %xmm1
	vpsubw %xmm6, %xmm2, %xmm2
	vpsubw %xmm7, %xmm3, %xmm3

	/* correction = Mont(branch0-branch1, z-z^5 inverse). */
	vmovdqa .Lpost_z_pair(%rip), %ymm12
	vextracti128 $1, %ymm12, %xmm13
	vpmullw %xmm12, %xmm0, %xmm4
	vpmullw %xmm12, %xmm1, %xmm5
	vpmullw %xmm12, %xmm2, %xmm6
	vpmullw %xmm12, %xmm3, %xmm7
	vpmulhw %xmm13, %xmm0, %xmm0
	vpmulhw %xmm13, %xmm1, %xmm1
	vpmulhw %xmm13, %xmm2, %xmm2
	vpmulhw %xmm13, %xmm3, %xmm3
	vpmulhw %xmm15, %xmm4, %xmm4
	vpmulhw %xmm15, %xmm5, %xmm5
	vpmulhw %xmm15, %xmm6, %xmm6
	vpmulhw %xmm15, %xmm7, %xmm7
	vpsubw %xmm4, %xmm0, %xmm0
	vpsubw %xmm5, %xmm1, %xmm1
	vpsubw %xmm6, %xmm2, %xmm2
	vpsubw %xmm7, %xmm3, %xmm3
	vpsubw %xmm0,  %xmm8,  %xmm8
	vpsubw %xmm1,  %xmm9,  %xmm9
	vpsubw %xmm2, %xmm10, %xmm10
	vpsubw %xmm3, %xmm11, %xmm11

	/* Low branch: Mont(sum-correction, 1/192). */
	vmovdqa \ninv_pair(%rip), %ymm12
	vextracti128 $1, %ymm12, %xmm13
	vpmullw %xmm12,  %xmm8, %xmm4
	vpmullw %xmm12,  %xmm9, %xmm5
	vpmullw %xmm12, %xmm10, %xmm6
	vpmullw %xmm12, %xmm11, %xmm7
	vpmulhw %xmm13,  %xmm8,  %xmm8
	vpmulhw %xmm13,  %xmm9,  %xmm9
	vpmulhw %xmm13, %xmm10, %xmm10
	vpmulhw %xmm13, %xmm11, %xmm11
	vpmulhw %xmm15, %xmm4, %xmm4
	vpmulhw %xmm15, %xmm5, %xmm5
	vpmulhw %xmm15, %xmm6, %xmm6
	vpmulhw %xmm15, %xmm7, %xmm7
	vpsubw %xmm4,  %xmm8,  %xmm8
	vpsubw %xmm5,  %xmm9,  %xmm9
	vpsubw %xmm6, %xmm10, %xmm10
	vpsubw %xmm7, %xmm11, %xmm11

	/* High branch: Mont(correction, 1/96). */
	vmovdqa \two_ninv_pair(%rip), %ymm12
	vextracti128 $1, %ymm12, %xmm13
	vpmullw %xmm12, %xmm0, %xmm4
	vpmullw %xmm12, %xmm1, %xmm5
	vpmullw %xmm12, %xmm2, %xmm6
	vpmullw %xmm12, %xmm3, %xmm7
	vpmulhw %xmm13, %xmm0, %xmm0
	vpmulhw %xmm13, %xmm1, %xmm1
	vpmulhw %xmm13, %xmm2, %xmm2
	vpmulhw %xmm13, %xmm3, %xmm3
	vpmulhw %xmm15, %xmm4, %xmm4
	vpmulhw %xmm15, %xmm5, %xmm5
	vpmulhw %xmm15, %xmm6, %xmm6
	vpmulhw %xmm15, %xmm7, %xmm7
	vpsubw %xmm4, %xmm0, %xmm0
	vpsubw %xmm5, %xmm1, %xmm1
	vpsubw %xmm6, %xmm2, %xmm2
	vpsubw %xmm7, %xmm3, %xmm3

	/* Re-form four branch-paired coefficient vectors. */
	vinserti128 $1, %xmm0,  %ymm8, %ymm0
	vinserti128 $1, %xmm1,  %ymm9, %ymm1
	vinserti128 $1, %xmm2, %ymm10, %ymm2
	vinserti128 $1, %xmm3, %ymm11, %ymm3

	POST_TRANSPOSE4X8
	POST_STORE_PAIR 0, 0
	POST_STORE_PAIR 1, 2
	POST_STORE_PAIR 2, 4
	POST_STORE_PAIR 3, 6
.endm

/*
 * void gt_invntt_soa_postprocess_asm(int16_t out[768],
 *                                    const int16_t rows[768])
 *
 * rows must be 32-byte aligned and separate from out.  Input rows are the
 * exact [0,q] inverse-DFT3 scratch.  Output matches the intrinsic canonical
 * coefficient layout exactly.
 */
.p2align 5
.globl gt_invntt_soa_postprocess_asm
.type gt_invntt_soa_postprocess_asm,@function
gt_invntt_soa_postprocess_asm:
	vmovdqa .Lpost_q(%rip), %ymm15
	leaq gt_inv_untwist(%rip), %r8
	leaq gt_inv_untwist_qinv(%rip), %r9
	leaq gt_inv_output_block(%rip), %rdx
	movl $12, %ecx
.p2align 5
.Lpost_group_loop:
	POSTPROCESS_GROUP .Lpost_ninv_pair, .Lpost_2ninv_pair
	addq $128, %rsi
	addq $32, %r8
	addq $32, %r9
	addq $8, %rdx
	decl %ecx
	jne .Lpost_group_loop

	vzeroupper
	ret
.size gt_invntt_soa_postprocess_asm,.-gt_invntt_soa_postprocess_asm

/*
 * Matching endpoint for an inverse input uniformly scaled by R^-1.  All
 * inverse twiddle and untwist factors remain in Montgomery form, so that
 * scale propagates unchanged until the two final normalization products.
 * Their factors carry one additional R and restore normal-domain output.
 */
.p2align 5
.globl gt_invntt_soa_postprocess_rminus1_asm
.type gt_invntt_soa_postprocess_rminus1_asm,@function
gt_invntt_soa_postprocess_rminus1_asm:
	vmovdqa .Lpost_q(%rip), %ymm15
	leaq gt_inv_untwist(%rip), %r8
	leaq gt_inv_untwist_qinv(%rip), %r9
	leaq gt_inv_output_block(%rip), %rdx
	movl $12, %ecx
.p2align 5
.Lpost_rminus1_group_loop:
	POSTPROCESS_GROUP .Lpost_ninv_rminus1_pair, .Lpost_2ninv_rminus1_pair
	addq $128, %rsi
	addq $32, %r8
	addq $32, %r9
	addq $8, %rdx
	decl %ecx
	jne .Lpost_rminus1_group_loop

	vzeroupper
	ret
.size gt_invntt_soa_postprocess_rminus1_asm,.-gt_invntt_soa_postprocess_rminus1_asm

.section .rodata
.p2align 5
.Lpost_q:
	.rept 16
	.short 3457
	.endr

/* Each pair is qinv[8] in its low half and factor[8] in its high half. */
.p2align 5
.Lpost_z_pair:
	.rept 8
	.short -30977
	.endr
	.rept 8
	.short -1665
	.endr
.Lpost_ninv_pair:
	.rept 8
	.short 341
	.endr
	.rept 8
	.short -811
	.endr
.Lpost_2ninv_pair:
	.rept 8
	.short 682
	.endr
	.rept 8
	.short -1622
	.endr
/* (1/192)*R^2 and (1/96)*R^2, stored as [factor*qinv | factor]. */
.Lpost_ninv_rminus1_pair:
	.rept 8
	.short 15375
	.endr
	.rept 8
	.short 1679
	.endr
.Lpost_2ninv_rminus1_pair:
	.rept 8
	.short 30749
	.endr
	.rept 8
	.short -99
	.endr

#ifndef GT_INVNTT_FUSED_INCLUDE
.section .note.GNU-stack,"",@progbits
#endif
