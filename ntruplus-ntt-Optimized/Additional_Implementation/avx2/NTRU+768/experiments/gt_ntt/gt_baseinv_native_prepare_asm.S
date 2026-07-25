/*
 * Benchmark-only GTN16 baseinv prepare kernels.
 *
 * This is the production AVX2 quartic-adjugate schedule generalized from the
 * paired production zeta layout to one generated native lambda vector per
 * batch.  The lazy entry fuses four independent center10 chains immediately
 * after the first loads.  The no-center entry also accepts GTN-L3 directly:
 * its producer-specific proof bounds every initial unknown product below the
 * packed-Montgomery limit.  Both entries write four pre-sign adjugate vectors
 * and one determinant vector for each of the 12 native batches.
 *
 * SysV arguments:
 *   rdi = out[768], 32-byte aligned
 *   rsi = determinant[12], 32-byte aligned
 *   rdx = in[768], 32-byte aligned; may equal out
 */

.text

.macro GT_BASEINV_NATIVE_PREPARE name, center_input
.p2align 5
.globl \name
.type \name,@function
\name:
	vpbroadcastw .Lgt_baseinv_q(%rip), %ymm0
	vpbroadcastw .Lgt_baseinv_qinv(%rip), %ymm15
	leaq gt_native_lambda_qinv(%rip), %r9
	leaq gt_native_lambda(%rip), %rcx
	leaq 1536(%rdi), %r8

.p2align 5
.Lprepare_loop_\@:
.if \center_input
	/* ymm10 is reused by the quartic schedule, so refresh it per batch. */
	vpbroadcastw .Lgt_baseinv_center10(%rip), %ymm10
.endif
	vmovdqa   (%r9), %ymm14
	vmovdqa  (%rcx), %ymm1

	vmovdqu   (%rdx), %ymm2
	vmovdqu 32(%rdx), %ymm3
	vmovdqu 64(%rdx), %ymm4
	vmovdqu 96(%rdx), %ymm5

.if \center_input
	/* Four independent quotient chains expose the packed-multiply latency. */
	vpmulhrsw %ymm10, %ymm2, %ymm6
	vpmulhrsw %ymm10, %ymm3, %ymm7
	vpmulhrsw %ymm10, %ymm4, %ymm8
	vpmulhrsw %ymm10, %ymm5, %ymm9
	vpmullw %ymm0, %ymm6, %ymm6
	vpmullw %ymm0, %ymm7, %ymm7
	vpmullw %ymm0, %ymm8, %ymm8
	vpmullw %ymm0, %ymm9, %ymm9
	vpsubw %ymm6, %ymm2, %ymm2
	vpsubw %ymm7, %ymm3, %ymm3
	vpsubw %ymm8, %ymm4, %ymm4
	vpsubw %ymm9, %ymm5, %ymm5
.endif

	/* a0^2, a0*a2, a1^2. */
	vpmullw %ymm15, %ymm2, %ymm12
	vpmullw %ymm15, %ymm3, %ymm13
	vpmullw %ymm12, %ymm2, %ymm11
	vpmullw %ymm12, %ymm4, %ymm12
	vpmullw %ymm13, %ymm3, %ymm13
	vpmulhw %ymm2, %ymm2, %ymm6
	vpmulhw %ymm2, %ymm4, %ymm7
	vpmulhw %ymm3, %ymm3, %ymm8
	vpmulhw %ymm0, %ymm11, %ymm11
	vpmulhw %ymm0, %ymm12, %ymm12
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw %ymm11, %ymm6, %ymm6
	vpsubw %ymm12, %ymm7, %ymm7
	vpsubw %ymm13, %ymm8, %ymm8
	vpsllw $1, %ymm7, %ymm7
	vpsubw %ymm8, %ymm7, %ymm7

	/* a2^2, a3^2, a3*a1. */
	vpmullw %ymm15, %ymm4, %ymm12
	vpmullw %ymm15, %ymm5, %ymm13
	vpmullw %ymm12, %ymm4, %ymm11
	vpmullw %ymm13, %ymm5, %ymm12
	vpmullw %ymm13, %ymm3, %ymm13
	vpmulhw %ymm4, %ymm4, %ymm8
	vpmulhw %ymm5, %ymm5, %ymm9
	vpmulhw %ymm5, %ymm3, %ymm10
	vpmulhw %ymm0, %ymm11, %ymm11
	vpmulhw %ymm0, %ymm12, %ymm12
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw %ymm11, %ymm8, %ymm8
	vpsubw %ymm12, %ymm9, %ymm9
	vpsubw %ymm13, %ymm10, %ymm10
	vpsllw $1, %ymm10, %ymm10
	vpsubw %ymm10, %ymm8, %ymm8

	/* lambda*(a2^2-2*a1*a3), lambda*a3^2. */
	vpmullw %ymm14, %ymm8, %ymm12
	vpmullw %ymm14, %ymm9, %ymm13
	vpmulhw %ymm1, %ymm8, %ymm8
	vpmulhw %ymm1, %ymm9, %ymm9
	vpmulhw %ymm0, %ymm12, %ymm12
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw %ymm12, %ymm8, %ymm8
	vpsubw %ymm13, %ymm9, %ymm9
	vpaddw %ymm8, %ymm6, %ymm6 /* t0 */
	vpsubw %ymm9, %ymm7, %ymm7 /* t1 = 2*a0*a2-a1^2-lambda*a3^2 */

	/* determinant = t0^2 - lambda*t1^2. */
	vpmullw %ymm15, %ymm6, %ymm12
	vpmullw %ymm15, %ymm7, %ymm13
	vpmullw %ymm12, %ymm6, %ymm10
	vpmullw %ymm13, %ymm7, %ymm11
	vpmulhw %ymm6, %ymm6, %ymm8
	vpmulhw %ymm7, %ymm7, %ymm9
	vpmulhw %ymm0, %ymm10, %ymm10
	vpmulhw %ymm0, %ymm11, %ymm11
	vpsubw %ymm10, %ymm8, %ymm8
	vpsubw %ymm11, %ymm9, %ymm9
	vpmullw %ymm14, %ymm9, %ymm11
	vpmulhw %ymm1, %ymm9, %ymm9
	vpmulhw %ymm0, %ymm11, %ymm11
	vpsubw %ymm11, %ymm9, %ymm9
	vpsubw %ymm9, %ymm8, %ymm8

	/* lambda*a2 and lambda*a3. */
	vpmullw %ymm14, %ymm4, %ymm11
	vpmullw %ymm14, %ymm5, %ymm14
	vpmulhw %ymm1, %ymm4, %ymm9
	vpmulhw %ymm1, %ymm5, %ymm1
	vpmulhw %ymm0, %ymm11, %ymm11
	vpmulhw %ymm0, %ymm14, %ymm14
	vpsubw %ymm11, %ymm9, %ymm9
	vpsubw %ymm14, %ymm1, %ymm1

	/* lambda*a2*t1 and lambda*a3*t1. */
	vpmullw %ymm13, %ymm9, %ymm11
	vpmullw %ymm13, %ymm1, %ymm14
	vpmulhw %ymm7, %ymm9, %ymm9
	vpmulhw %ymm7, %ymm1, %ymm1
	vpmulhw %ymm0, %ymm11, %ymm11
	vpmulhw %ymm0, %ymm14, %ymm14
	vpsubw %ymm11, %ymm9, %ymm9
	vpsubw %ymm14, %ymm1, %ymm1

	/* a0*t1 and a1*t1. */
	vpmullw %ymm13, %ymm2, %ymm14
	vpmullw %ymm13, %ymm3, %ymm13
	vpmulhw %ymm7, %ymm2, %ymm11
	vpmulhw %ymm7, %ymm3, %ymm7
	vpmulhw %ymm0, %ymm14, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw %ymm14, %ymm11, %ymm11
	vpsubw %ymm13, %ymm7, %ymm7

	/* a0*t0, a1*t0, a2*t0, a3*t0. */
	vpmullw %ymm12, %ymm2, %ymm14
	vpmullw %ymm12, %ymm3, %ymm13
	vpmulhw %ymm6, %ymm2, %ymm2
	vpmulhw %ymm6, %ymm3, %ymm3
	vpmulhw %ymm0, %ymm14, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw %ymm14, %ymm2, %ymm2
	vpsubw %ymm13, %ymm3, %ymm3
	vpmullw %ymm12, %ymm4, %ymm13
	vpmullw %ymm12, %ymm5, %ymm14
	vpmulhw %ymm6, %ymm4, %ymm4
	vpmulhw %ymm6, %ymm5, %ymm5
	vpmulhw %ymm0, %ymm13, %ymm13
	vpmulhw %ymm0, %ymm14, %ymm14
	vpsubw %ymm13, %ymm4, %ymm4
	vpsubw %ymm14, %ymm5, %ymm5

	/* Production-compatible pre-sign adjugate. */
	vpsubw %ymm9, %ymm2, %ymm2
	vpsubw %ymm1, %ymm3, %ymm3
	vpsubw %ymm11, %ymm4, %ymm4
	vpsubw %ymm7, %ymm5, %ymm5

	vmovdqu %ymm2,   (%rdi)
	vmovdqu %ymm3, 32(%rdi)
	vmovdqu %ymm4, 64(%rdi)
	vmovdqu %ymm5, 96(%rdi)
	vmovdqa %ymm8, (%rsi)

	addq $32, %r9
	addq $32, %rcx
	addq $32, %rsi
	addq $128, %rdi
	addq $128, %rdx
	cmpq %r8, %rdi
	jb .Lprepare_loop_\@
	ret
.size \name,.-\name
.endm

GT_BASEINV_NATIVE_PREPARE gt_baseinv_native_prepare_centered_asm, 0
GT_BASEINV_NATIVE_PREPARE gt_baseinv_native_prepare_center_on_load_asm, 1

.section .rodata
.p2align 1
.Lgt_baseinv_q:
	.short 3457
.Lgt_baseinv_qinv:
	.short 12929
.Lgt_baseinv_center10:
	.short 10

.section .note.GNU-stack,"",@progbits
