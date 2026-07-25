/*
 * Zero-spill AVX2 quartic basemul for the GT SoA/native layouts.
 *
 * Per 16-lane batch:
 *   ymm1..ymm4   = a0..a3
 *   ymm5..ymm8   = a0*qinv..a3*qinv (mod 2^16)
 *   ymm9..ymm12  = b0..b3
 *   ymm13        = Montgomery low/correction temporary
 *   ymm14        = Montgomery product temporary
 *   ymm15        = output accumulator
 *   ymm0         = q
 *
 * Hoisting a_i*qinv changes only the low-half computation:
 *   ((a_i*b_j) mod 2^16)*qinv == (a_i*qinv mod 2^16)*b_j mod 2^16.
 * The signed high product and all range contracts are unchanged.
 */

	.text

	.macro GT_MONT_FIRST a, aq, b
	vpmullw %\aq, %\b, %ymm13
	vpmulhw %\a,  %\b, %ymm15
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw  %ymm13, %ymm15, %ymm15
	.endm

	.macro GT_MONT_ADD a, aq, b
	vpmullw %\aq, %\b, %ymm13
	vpmulhw %\a,  %\b, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw  %ymm13, %ymm14, %ymm14
	vpaddw  %ymm14, %ymm15, %ymm15
	.endm

	.macro GT_MONT_LAMBDA
	vpmullw (%r9), %ymm15, %ymm13
	vpmulhw (%r8), %ymm15, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw  %ymm13, %ymm14, %ymm15
	.endm

	.macro GT_MONT_RSQ
	vpmullw .Lgt_rsq_qinv(%rip), %ymm15, %ymm13
	vpmulhw .Lgt_rsq(%rip),      %ymm15, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw  %ymm13, %ymm14, %ymm15
	.endm

/*
 * Preserve the quartic accumulator in R^-1 domain while restoring the
 * inverse input bound.  Before this checkpoint |accumulator| <= 4*(q-1).
 * Exhaustive evaluation on [-13824,13824] gives [-2359,2359].
 */
	.macro GT_CENTER_RMINUS1
	vpmulhrsw .Lgt_center10(%rip), %ymm15, %ymm14
	vpmullw  %ymm0, %ymm14, %ymm14
	vpsubw   %ymm14, %ymm15, %ymm15
	.endm

	/* Deliberate no-op finalizer for the coefficient-specific c0-lazy path. */
	.macro GT_KEEP_RMINUS1
	.endm

	.macro GT_BASEMUL_BODY batch_label, c0_finalizer, c123_finalizer
	vmovdqa .Lgt_q(%rip), %ymm0
	movl $12, %ecx

	.p2align 5
\batch_label:
	/* All eight input vectors stay resident for the complete quartic. */
	vmovdqu   0(%rsi), %ymm1
	vmovdqu  32(%rsi), %ymm2
	vmovdqu  64(%rsi), %ymm3
	vmovdqu  96(%rsi), %ymm4
	vmovdqu   0(%rdx), %ymm9
	vmovdqu  32(%rdx), %ymm10
	vmovdqu  64(%rdx), %ymm11
	vmovdqu  96(%rdx), %ymm12

	/* One qinv premultiply per a coefficient, reused by four products. */
	vpmullw .Lgt_qinv(%rip), %ymm1, %ymm5
	vpmullw .Lgt_qinv(%rip), %ymm2, %ymm6
	vpmullw .Lgt_qinv(%rip), %ymm3, %ymm7
	vpmullw .Lgt_qinv(%rip), %ymm4, %ymm8

	/* c0 = a0*b0 + lambda*(a1*b3 + a2*b2 + a3*b1). */
	GT_MONT_FIRST ymm2, ymm6, ymm12
	GT_MONT_ADD   ymm3, ymm7, ymm11
	GT_MONT_ADD   ymm4, ymm8, ymm10
	GT_MONT_LAMBDA
	GT_MONT_ADD   ymm1, ymm5, ymm9
	\c0_finalizer
	vmovdqu %ymm15, 0(%rdi)

	/* c1 = a0*b1 + a1*b0 + lambda*(a2*b3 + a3*b2). */
	GT_MONT_FIRST ymm3, ymm7, ymm12
	GT_MONT_ADD   ymm4, ymm8, ymm11
	GT_MONT_LAMBDA
	GT_MONT_ADD   ymm1, ymm5, ymm10
	GT_MONT_ADD   ymm2, ymm6, ymm9
	\c123_finalizer
	vmovdqu %ymm15, 32(%rdi)

	/* c2 = a0*b2 + a1*b1 + a2*b0 + lambda*a3*b3. */
	GT_MONT_FIRST ymm4, ymm8, ymm12
	GT_MONT_LAMBDA
	GT_MONT_ADD   ymm1, ymm5, ymm11
	GT_MONT_ADD   ymm2, ymm6, ymm10
	GT_MONT_ADD   ymm3, ymm7, ymm9
	\c123_finalizer
	vmovdqu %ymm15, 64(%rdi)

	/* c3 = a0*b3 + a1*b2 + a2*b1 + a3*b0. */
	GT_MONT_FIRST ymm1, ymm5, ymm12
	GT_MONT_ADD   ymm2, ymm6, ymm11
	GT_MONT_ADD   ymm3, ymm7, ymm10
	GT_MONT_ADD   ymm4, ymm8, ymm9
	\c123_finalizer
	vmovdqu %ymm15, 96(%rdi)

	addq $128, %rsi
	addq $128, %rdx
	addq $128, %rdi
	addq $32, %r8
	addq $32, %r9
	decl %ecx
	jne \batch_label

	vzeroupper
	ret
	.endm

	.p2align 5
	.globl gt_basemul_soa_asm_avx2
	.type gt_basemul_soa_asm_avx2,@function
gt_basemul_soa_asm_avx2:
	leaq gt_soa_lambda(%rip), %r8
	leaq gt_soa_lambda_qinv(%rip), %r9
	jmp .Lgt_basemul_layout_asm
	.size gt_basemul_soa_asm_avx2,.-gt_basemul_soa_asm_avx2

	.p2align 5
	.globl gt_basemul_native_asm_avx2
	.type gt_basemul_native_asm_avx2,@function
gt_basemul_native_asm_avx2:
	leaq gt_native_lambda(%rip), %r8
	leaq gt_native_lambda_qinv(%rip), %r9
.Lgt_basemul_layout_asm:
	GT_BASEMUL_BODY .Lgt_basemul_batch, GT_MONT_RSQ, GT_MONT_RSQ
	.size gt_basemul_native_asm_avx2,.-gt_basemul_native_asm_avx2

	.p2align 5
	.globl gt_basemul_soa_rminus1_asm_avx2
	.type gt_basemul_soa_rminus1_asm_avx2,@function
gt_basemul_soa_rminus1_asm_avx2:
	leaq gt_soa_lambda(%rip), %r8
	leaq gt_soa_lambda_qinv(%rip), %r9
	jmp .Lgt_basemul_rminus1_layout_asm
	.size gt_basemul_soa_rminus1_asm_avx2,.-gt_basemul_soa_rminus1_asm_avx2

	.p2align 5
	.globl gt_basemul_native_rminus1_asm_avx2
	.type gt_basemul_native_rminus1_asm_avx2,@function
gt_basemul_native_rminus1_asm_avx2:
	leaq gt_native_lambda(%rip), %r8
	leaq gt_native_lambda_qinv(%rip), %r9

.Lgt_basemul_rminus1_layout_asm:
	GT_BASEMUL_BODY .Lgt_basemul_rminus1_batch, GT_CENTER_RMINUS1, GT_CENTER_RMINUS1
	.size gt_basemul_native_rminus1_asm_avx2,.-gt_basemul_native_rminus1_asm_avx2

	.p2align 5
	.globl gt_basemul_soa_rminus1_c0lazy_asm_avx2
	.type gt_basemul_soa_rminus1_c0lazy_asm_avx2,@function
gt_basemul_soa_rminus1_c0lazy_asm_avx2:
	leaq gt_soa_lambda(%rip), %r8
	leaq gt_soa_lambda_qinv(%rip), %r9
	jmp .Lgt_basemul_rminus1_c0lazy_layout_asm
	.size gt_basemul_soa_rminus1_c0lazy_asm_avx2,.-gt_basemul_soa_rminus1_c0lazy_asm_avx2

	.p2align 5
	.globl gt_basemul_native_rminus1_c0lazy_asm_avx2
	.type gt_basemul_native_rminus1_c0lazy_asm_avx2,@function
gt_basemul_native_rminus1_c0lazy_asm_avx2:
	leaq gt_native_lambda(%rip), %r8
	leaq gt_native_lambda_qinv(%rip), %r9

.Lgt_basemul_rminus1_c0lazy_layout_asm:
	GT_BASEMUL_BODY .Lgt_basemul_rminus1_c0lazy_batch, GT_KEEP_RMINUS1, GT_CENTER_RMINUS1
	.size gt_basemul_native_rminus1_c0lazy_asm_avx2,.-gt_basemul_native_rminus1_c0lazy_asm_avx2

	.section .rodata
	.p2align 5
.Lgt_q:
	.rept 16
	.short 3457
	.endr
.Lgt_qinv:
	.rept 16
	.short 12929
	.endr
.Lgt_rsq:
	.rept 16
	.short 867
	.endr
.Lgt_rsq_qinv:
	.rept 16
	.short 2787
	.endr
.Lgt_center10:
	.rept 16
	.short 10
	.endr

	.section .note.GNU-stack,"",@progbits
