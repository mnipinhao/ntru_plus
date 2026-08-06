/*
 * Native TILE4 quartic basemul, e=0 x e=0 -> e=-1.
 *
 * Four adjacent TILE4 vectors are transposed entirely in registers into four
 * 16-lane coefficient planes.  The arithmetic is the proven Frozen quartic
 * schedule, but the input and final output ABI remain TILE4.  Four result
 * planes temporarily occupy the destination block before the self-inverse
 * transpose overwrites them with final TILE4 data.  Consequently this first
 * candidate requires out != a && out != b.
 */

	.text

	/* Self-inverse transpose of 16 quartics x four int16 coefficients. */
	.macro TILE4_TRANSPOSE s0,s1,s2,s3,t0,t1,t2,t3
	vpunpcklwd %\s1, %\s0, %\t0
	vpunpckhwd %\s1, %\s0, %\t1
	vpunpcklwd %\s3, %\s2, %\t2
	vpunpckhwd %\s3, %\s2, %\t3

	vpunpckldq %\t2, %\t0, %\s0
	vpunpckhdq %\t2, %\t0, %\s1
	vpunpckldq %\t3, %\t1, %\s2
	vpunpckhdq %\t3, %\t1, %\s3

	vpunpcklqdq %\s2, %\s0, %\t0
	vpunpckhqdq %\s2, %\s0, %\t1
	vpunpcklqdq %\s3, %\s1, %\t2
	vpunpckhqdq %\s3, %\s1, %\t3
	.endm

	.macro TILE4_MONT_FIRST a,aq,b
	vpmullw %\aq, %\b, %ymm13
	vpmulhw %\a,  %\b, %ymm15
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw  %ymm13, %ymm15, %ymm15
	.endm

	.macro TILE4_MONT_ADD a,aq,b
	vpmullw %\aq, %\b, %ymm13
	vpmulhw %\a,  %\b, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw  %ymm13, %ymm14, %ymm14
	vpaddw  %ymm14, %ymm15, %ymm15
	.endm

	.macro TILE4_MONT_TO_HOIST dst,a,aq,b,tmp
	vpmullw %\aq, %\b, %\tmp
	vpmulhw %\a,  %\b, %\dst
	vpmulhw %ymm0, %\tmp, %\tmp
	vpsubw  %\tmp, %\dst, %\dst
	.endm

	.macro TILE4_MONT_ADD_HOIST acc,a,aq,b,lo,hi
	vpmullw %\aq, %\b, %\lo
	vpmulhw %\a,  %\b, %\hi
	vpmulhw %ymm0, %\lo, %\lo
	vpsubw  %\lo, %\hi, %\hi
	vpaddw  %\hi, %\acc, %\acc
	.endm

	.macro TILE4_MONT_TO_DEMAND dst,a,b,tmp
	vpmullw .Ltile4_bm_qinv(%rip), %\a, %\tmp
	vpmulhw %\a, %\b, %\dst
	vpmullw %\b, %\tmp, %\tmp
	vpmulhw %ymm0, %\tmp, %\tmp
	vpsubw %\tmp, %\dst, %\dst
	.endm

	.macro TILE4_MONT_ADD_DEMAND acc,a,b,lo,hi
	vpmullw .Ltile4_bm_qinv(%rip), %\a, %\lo
	vpmullw %\b, %\lo, %\lo
	vpmulhw %\a, %\b, %\hi
	vpmulhw %ymm0, %\lo, %\lo
	vpsubw %\lo, %\hi, %\hi
	vpaddw %\hi, %\acc, %\acc
	.endm

	/* Montgomery product without a persistent qinv-hoisted operand. */
	.macro TILE4_MONT_RAW_TO dst,a,b,lo
	vpmullw %\a, %\b, %\lo
	vpmullw .Ltile4_bm_qinv(%rip), %\lo, %\lo
	vpmulhw %\a, %\b, %\dst
	vpmulhw %ymm0, %\lo, %\lo
	vpsubw %\lo, %\dst, %\dst
	.endm

	.macro TILE4_MONT_LAMBDA
	vpmullw (%r9), %ymm15, %ymm13
	vpmulhw (%r8), %ymm15, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw  %ymm13, %ymm14, %ymm15
	.endm

	/*
	 * K2 hand schedule.  The destination block is public scratch: c0/c2 are
	 * completed first, then the same two free planes hold the three linear
	 * Karatsuba temporaries needed for c1/c3.  No stack spill is required.
	 */
	.macro TILE4_BASEMUL_K2_FUNCTION name
	.p2align 5
	.globl \name
	.type \name,@function
\name:
	leaq .Ltile4_bm_lambda(%rip), %r8
	leaq .Ltile4_bm_lambda_qinv(%rip), %r9
	vmovdqa .Ltile4_bm_q(%rip), %ymm0
	movl $12, %ecx
	.p2align 5
.Ltile4_bm_k2_loop\@:
	vmovdqu   0(%rdx), %ymm1
	vmovdqu  32(%rdx), %ymm2
	vmovdqu  64(%rdx), %ymm3
	vmovdqu  96(%rdx), %ymm4
	TILE4_TRANSPOSE ymm1,ymm2,ymm3,ymm4,ymm9,ymm10,ymm11,ymm12
	vmovdqu   0(%rsi), %ymm5
	vmovdqu  32(%rsi), %ymm6
	vmovdqu  64(%rsi), %ymm7
	vmovdqu  96(%rsi), %ymm8
	TILE4_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4

	/* p0, p2, q0, q2 occupy the four destination scratch planes. */
	TILE4_MONT_RAW_TO ymm5,ymm1,ymm9,ymm13
	vmovdqu %ymm5, 0(%rdi)
	TILE4_MONT_RAW_TO ymm5,ymm2,ymm10,ymm13
	vmovdqu %ymm5, 32(%rdi)
	TILE4_MONT_RAW_TO ymm5,ymm3,ymm11,ymm13
	vmovdqu %ymm5, 64(%rdi)
	TILE4_MONT_RAW_TO ymm5,ymm4,ymm12,ymm13
	vmovdqu %ymm5, 96(%rdi)

	/* r0 = s0-p0-q0; r2 = s2-p2-q2. */
	vpaddw %ymm3, %ymm1, %ymm5
	vpaddw %ymm11, %ymm9, %ymm6
	TILE4_MONT_RAW_TO ymm7,ymm5,ymm6,ymm8
	vpsubw 0(%rdi), %ymm7, %ymm7
	vpsubw 64(%rdi), %ymm7, %ymm7
	vpaddw %ymm4, %ymm2, %ymm5
	vpaddw %ymm12, %ymm10, %ymm6
	TILE4_MONT_RAW_TO ymm8,ymm5,ymm6,ymm13
	vpsubw 32(%rdi), %ymm8, %ymm8
	vpsubw 96(%rdi), %ymm8, %ymm8

	/* c0 = p0 + lambda*(q0+r2). */
	vmovdqu 64(%rdi), %ymm15
	vpaddw %ymm8, %ymm15, %ymm15
	TILE4_MONT_LAMBDA
	vpaddw 0(%rdi), %ymm15, %ymm15
	vmovdqu %ymm15, 0(%rdi)

	/* c2 = p2+r0+lambda*q2. */
	vmovdqu 96(%rdi), %ymm15
	TILE4_MONT_LAMBDA
	vpaddw 32(%rdi), %ymm15, %ymm15
	vpaddw %ymm7, %ymm15, %ymm15
	vmovdqu %ymm15, 64(%rdi)

	/* p1 via one linear Karatsuba product; planes 1/3 are scratch. */
	TILE4_MONT_RAW_TO ymm5,ymm1,ymm9,ymm13
	vmovdqu %ymm5, 32(%rdi)
	TILE4_MONT_RAW_TO ymm6,ymm2,ymm10,ymm13
	vmovdqu %ymm6, 96(%rdi)
	vpaddw %ymm2, %ymm1, %ymm7
	vpaddw %ymm10, %ymm9, %ymm8
	TILE4_MONT_RAW_TO ymm15,ymm7,ymm8,ymm13
	vpsubw 32(%rdi), %ymm15, %ymm15
	vpsubw 96(%rdi), %ymm15, %ymm15
	vmovdqa %ymm15, %ymm5

	/* q1. */
	TILE4_MONT_RAW_TO ymm6,ymm3,ymm11,ymm13
	vmovdqu %ymm6, 32(%rdi)
	TILE4_MONT_RAW_TO ymm7,ymm4,ymm12,ymm13
	vmovdqu %ymm7, 96(%rdi)
	vpaddw %ymm4, %ymm3, %ymm8
	vpaddw %ymm12, %ymm11, %ymm14
	TILE4_MONT_RAW_TO ymm15,ymm8,ymm14,ymm13
	vpsubw 32(%rdi), %ymm15, %ymm15
	vpsubw 96(%rdi), %ymm15, %ymm15
	vmovdqa %ymm15, %ymm6

	/* s1 for the summed linear polynomials. */
	vpaddw %ymm3, %ymm1, %ymm7
	vpaddw %ymm4, %ymm2, %ymm8
	vpaddw %ymm11, %ymm9, %ymm13
	vpaddw %ymm12, %ymm10, %ymm14
	TILE4_MONT_RAW_TO ymm15,ymm7,ymm13,ymm1
	vmovdqu %ymm15, 32(%rdi)
	TILE4_MONT_RAW_TO ymm15,ymm8,ymm14,ymm1
	vmovdqu %ymm15, 96(%rdi)
	vpaddw %ymm8, %ymm7, %ymm2
	vpaddw %ymm14, %ymm13, %ymm3
	TILE4_MONT_RAW_TO ymm15,ymm2,ymm3,ymm1
	vpsubw 32(%rdi), %ymm15, %ymm15
	vpsubw 96(%rdi), %ymm15, %ymm15

	/* c3=s1-p1-q1 is retained; c1=p1+lambda*q1 is stored. */
	vpsubw %ymm5, %ymm15, %ymm15
	vpsubw %ymm6, %ymm15, %ymm15
	vmovdqu %ymm15, 96(%rdi)
	vmovdqa %ymm6, %ymm15
	TILE4_MONT_LAMBDA
	vpaddw %ymm5, %ymm15, %ymm15
	vmovdqu %ymm15, 32(%rdi)
	vmovdqu 96(%rdi), %ymm15
	TILE4_OUTPUT_AOS_LATE_CENTER

	addq $128, %rsi
	addq $128, %rdx
	addq $128, %rdi
	addq $32, %r8
	addq $32, %r9
	decl %ecx
	jne .Ltile4_bm_k2_loop\@
	vzeroupper
	ret
	.size \name,.-\name
	.endm

	/*
	 * B4b: keep only a0*qinv and a1*qinv.  ymm7/8/13 carry the three
	 * wrapped sums so their lambda chains can issue together; a2/a3 low
	 * products are recomputed on demand to make those accumulators possible.
	 */
	.macro TILE4_BASEMUL_B4B_FUNCTION name
	.p2align 5
	.globl \name
	.type \name,@function
\name:
	leaq .Ltile4_bm_lambda(%rip), %r8
	leaq .Ltile4_bm_lambda_qinv(%rip), %r9
	vmovdqa .Ltile4_bm_q(%rip), %ymm0
	movl $12, %ecx
	.p2align 5
.Ltile4_bm_b4b_loop\@:
	vmovdqu   0(%rdx), %ymm1
	vmovdqu  32(%rdx), %ymm2
	vmovdqu  64(%rdx), %ymm3
	vmovdqu  96(%rdx), %ymm4
	TILE4_TRANSPOSE ymm1,ymm2,ymm3,ymm4,ymm9,ymm10,ymm11,ymm12
	vmovdqu   0(%rsi), %ymm5
	vmovdqu  32(%rsi), %ymm6
	vmovdqu  64(%rsi), %ymm7
	vmovdqu  96(%rsi), %ymm8
	TILE4_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4

	/* Partial qinv hoist. */
	vpmullw .Ltile4_bm_qinv(%rip), %ymm1, %ymm5
	vpmullw .Ltile4_bm_qinv(%rip), %ymm2, %ymm6

	/* w0, w1, w2 in three independent accumulators. */
	TILE4_MONT_TO_HOIST  ymm7,ymm2,ymm6,ymm12,ymm14
	TILE4_MONT_TO_DEMAND ymm8,ymm3,ymm12,ymm14
	TILE4_MONT_TO_DEMAND ymm13,ymm4,ymm12,ymm14
	TILE4_MONT_ADD_DEMAND ymm7,ymm3,ymm11,ymm14,ymm15
	TILE4_MONT_ADD_DEMAND ymm8,ymm4,ymm11,ymm14,ymm15
	TILE4_MONT_ADD_DEMAND ymm7,ymm4,ymm10,ymm14,ymm15

	/* Three lambda Montgomery chains, with the factors loaded once. */
	vpmullw (%r9), %ymm7, %ymm14
	vpmullw (%r9), %ymm8, %ymm15
	vpmullw (%r9), %ymm13, %ymm5
	vpmulhw (%r8), %ymm7, %ymm7
	vpmulhw (%r8), %ymm8, %ymm8
	vpmulhw (%r8), %ymm13, %ymm13
	vpmulhw %ymm0, %ymm14, %ymm14
	vpmulhw %ymm0, %ymm15, %ymm15
	vpmulhw %ymm0, %ymm5, %ymm5
	vpsubw %ymm14, %ymm7, %ymm7
	vpsubw %ymm15, %ymm8, %ymm8
	vpsubw %ymm5, %ymm13, %ymm13

	/* Direct terms are accumulated into c0/c1/c2. */
	vpmullw .Ltile4_bm_qinv(%rip), %ymm1, %ymm5
	TILE4_MONT_ADD_HOIST ymm7,ymm1,ymm5,ymm9,ymm14,ymm15
	TILE4_MONT_ADD_HOIST ymm8,ymm1,ymm5,ymm10,ymm14,ymm15
	TILE4_MONT_ADD_HOIST ymm8,ymm2,ymm6,ymm9,ymm14,ymm15
	TILE4_MONT_ADD_HOIST ymm13,ymm1,ymm5,ymm11,ymm14,ymm15
	TILE4_MONT_ADD_HOIST ymm13,ymm2,ymm6,ymm10,ymm14,ymm15
	TILE4_MONT_ADD_DEMAND ymm13,ymm3,ymm9,ymm14,ymm15

	/* c3 uses ymm5 after its final a0*qinv consumer has issued. */
	TILE4_MONT_TO_HOIST ymm5,ymm1,ymm5,ymm12,ymm14
	TILE4_MONT_ADD_HOIST ymm5,ymm2,ymm6,ymm11,ymm14,ymm15
	TILE4_MONT_ADD_DEMAND ymm5,ymm3,ymm10,ymm14,ymm15
	TILE4_MONT_ADD_DEMAND ymm5,ymm4,ymm9,ymm14,ymm15

	vmovdqu %ymm7,  0(%rdi)
	vmovdqu %ymm8, 32(%rdi)
	vmovdqu %ymm13, 64(%rdi)
	vmovdqa %ymm5, %ymm15
	TILE4_OUTPUT_AOS_LATE_CENTER

	addq $128, %rsi
	addq $128, %rdx
	addq $128, %rdi
	addq $32, %r8
	addq $32, %r9
	decl %ecx
	jne .Ltile4_bm_b4b_loop\@
	vzeroupper
	ret
	.size \name,.-\name
	.endm

	.macro TILE4_CENTER_RMINUS1
	vpmulhrsw .Ltile4_bm_center10(%rip), %ymm15, %ymm14
	vpmullw  %ymm0, %ymm14, %ymm14
	vpsubw   %ymm14, %ymm15, %ymm15
	.endm

	.macro TILE4_NO_FINALIZER
	.endm

	/* e=-1 times R^2 through Mont gives the general-ABI e=0 output. */
	.macro TILE4_MONT_RSQ
	vpmullw .Ltile4_bm_rsq_qinv(%rip), %ymm15, %ymm13
	vpmulhw .Ltile4_bm_rsq(%rip), %ymm15, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw  %ymm13, %ymm14, %ymm15
	.endm

	.macro TILE4_OUTPUT_AOS
	/* Four coefficient planes -> final native TILE4 output. */
	vmovdqu   0(%rdi), %ymm1
	vmovdqu  32(%rdi), %ymm2
	vmovdqu  64(%rdi), %ymm3
	vmovdqu  96(%rdi), %ymm4
	TILE4_TRANSPOSE ymm1,ymm2,ymm3,ymm4,ymm5,ymm6,ymm7,ymm8
	vmovdqu %ymm5,   0(%rdi)
	vmovdqu %ymm6,  32(%rdi)
	vmovdqu %ymm7,  64(%rdi)
	vmovdqu %ymm8,  96(%rdi)
	.endm

	/*
	 * B3 keeps c3 live, transposes the four raw e=-1 planes, then performs
	 * the four independent centered finalizers together.  This removes one
	 * scratch store/reload pair and exposes four reduction chains to OoO.
	 */
	.macro TILE4_OUTPUT_AOS_LATE_CENTER
	vmovdqu   0(%rdi), %ymm1
	vmovdqu  32(%rdi), %ymm2
	vmovdqu  64(%rdi), %ymm3
	TILE4_TRANSPOSE ymm1,ymm2,ymm3,ymm15,ymm5,ymm6,ymm7,ymm8

	vpmulhrsw .Ltile4_bm_center10(%rip), %ymm5, %ymm1
	vpmulhrsw .Ltile4_bm_center10(%rip), %ymm6, %ymm2
	vpmulhrsw .Ltile4_bm_center10(%rip), %ymm7, %ymm3
	vpmulhrsw .Ltile4_bm_center10(%rip), %ymm8, %ymm4
	vpmullw %ymm0, %ymm1, %ymm1
	vpmullw %ymm0, %ymm2, %ymm2
	vpmullw %ymm0, %ymm3, %ymm3
	vpmullw %ymm0, %ymm4, %ymm4
	vpsubw %ymm1, %ymm5, %ymm5
	vpsubw %ymm2, %ymm6, %ymm6
	vpsubw %ymm3, %ymm7, %ymm7
	vpsubw %ymm4, %ymm8, %ymm8
	vmovdqu %ymm5,   0(%rdi)
	vmovdqu %ymm6,  32(%rdi)
	vmovdqu %ymm7,  64(%rdi)
	vmovdqu %ymm8,  96(%rdi)
	.endm

	/* Keep raw c3 live; overlap its only required center with c0..c2 loads. */
	.macro TILE4_OUTPUT_AOS_LATE_C3CENTER
	vpmulhrsw .Ltile4_bm_center10(%rip), %ymm15, %ymm14
	vmovdqu   0(%rdi), %ymm1
	vmovdqu  32(%rdi), %ymm2
	vmovdqu  64(%rdi), %ymm3
	vpmullw %ymm0, %ymm14, %ymm14
	vpsubw %ymm14, %ymm15, %ymm15
	TILE4_TRANSPOSE ymm1,ymm2,ymm3,ymm15,ymm5,ymm6,ymm7,ymm8
	vmovdqu %ymm5,   0(%rdi)
	vmovdqu %ymm6,  32(%rdi)
	vmovdqu %ymm7,  64(%rdi)
	vmovdqu %ymm8,  96(%rdi)
	.endm

	/* Private consumer island keeps the four coefficient planes as stored. */
	.macro TILE4_OUTPUT_SOA_PRIVATE
	.endm

	/* B3 ablation: raw planes c0..c2 spill; c3 remains register-resident. */
	.macro TILE4_BASEMUL_B3_FUNCTION name,output
	.p2align 5
	.globl \name
	.type \name,@function
\name:
	leaq .Ltile4_bm_lambda(%rip), %r8
	leaq .Ltile4_bm_lambda_qinv(%rip), %r9
	vmovdqa .Ltile4_bm_q(%rip), %ymm0
	movl $12, %ecx

	.p2align 5
.Ltile4_bm_b3_loop\@:
	vmovdqu   0(%rdx), %ymm1
	vmovdqu  32(%rdx), %ymm2
	vmovdqu  64(%rdx), %ymm3
	vmovdqu  96(%rdx), %ymm4
	TILE4_TRANSPOSE ymm1,ymm2,ymm3,ymm4,ymm9,ymm10,ymm11,ymm12

	vmovdqu   0(%rsi), %ymm5
	vmovdqu  32(%rsi), %ymm6
	vmovdqu  64(%rsi), %ymm7
	vmovdqu  96(%rsi), %ymm8
	TILE4_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4

	vpmullw .Ltile4_bm_qinv(%rip), %ymm1, %ymm5
	vpmullw .Ltile4_bm_qinv(%rip), %ymm2, %ymm6
	vpmullw .Ltile4_bm_qinv(%rip), %ymm3, %ymm7
	vpmullw .Ltile4_bm_qinv(%rip), %ymm4, %ymm8

	TILE4_MONT_FIRST ymm2,ymm6,ymm12
	TILE4_MONT_ADD   ymm3,ymm7,ymm11
	TILE4_MONT_ADD   ymm4,ymm8,ymm10
	TILE4_MONT_LAMBDA
	TILE4_MONT_ADD   ymm1,ymm5,ymm9
	vmovdqu %ymm15, 0(%rdi)

	TILE4_MONT_FIRST ymm3,ymm7,ymm12
	TILE4_MONT_ADD   ymm4,ymm8,ymm11
	TILE4_MONT_LAMBDA
	TILE4_MONT_ADD   ymm1,ymm5,ymm10
	TILE4_MONT_ADD   ymm2,ymm6,ymm9
	vmovdqu %ymm15, 32(%rdi)

	TILE4_MONT_FIRST ymm4,ymm8,ymm12
	TILE4_MONT_LAMBDA
	TILE4_MONT_ADD   ymm1,ymm5,ymm11
	TILE4_MONT_ADD   ymm2,ymm6,ymm10
	TILE4_MONT_ADD   ymm3,ymm7,ymm9
	vmovdqu %ymm15, 64(%rdi)

	TILE4_MONT_FIRST ymm1,ymm5,ymm12
	TILE4_MONT_ADD   ymm2,ymm6,ymm11
	TILE4_MONT_ADD   ymm3,ymm7,ymm10
	TILE4_MONT_ADD   ymm4,ymm8,ymm9
	\output

	addq $128, %rsi
	addq $128, %rdx
	addq $128, %rdi
	addq $32, %r8
	addq $32, %r9
	decl %ecx
	jne .Ltile4_bm_b3_loop\@
	vzeroupper
	ret
	.size \name,.-\name
	.endm

	.macro TILE4_BASEMUL_FUNCTION name,finalizer0,finalizer1,finalizer2,finalizer3,output
	.p2align 5
	.globl \name
	.type \name,@function
\name:
	leaq .Ltile4_bm_lambda(%rip), %r8
	leaq .Ltile4_bm_lambda_qinv(%rip), %r9
	vmovdqa .Ltile4_bm_q(%rip), %ymm0
	movl $12, %ecx

	.p2align 5
.Ltile4_bm_loop\@:
	/* b AoS -> b0..b3 in ymm9..ymm12. */
	vmovdqu   0(%rdx), %ymm1
	vmovdqu  32(%rdx), %ymm2
	vmovdqu  64(%rdx), %ymm3
	vmovdqu  96(%rdx), %ymm4
	TILE4_TRANSPOSE ymm1,ymm2,ymm3,ymm4,ymm9,ymm10,ymm11,ymm12

	/* a AoS -> a0..a3 in ymm1..ymm4. */
	vmovdqu   0(%rsi), %ymm5
	vmovdqu  32(%rsi), %ymm6
	vmovdqu  64(%rsi), %ymm7
	vmovdqu  96(%rsi), %ymm8
	TILE4_TRANSPOSE ymm5,ymm6,ymm7,ymm8,ymm1,ymm2,ymm3,ymm4

	/* Hoist a_i*qinv for all sixteen Montgomery products. */
	vpmullw .Ltile4_bm_qinv(%rip), %ymm1, %ymm5
	vpmullw .Ltile4_bm_qinv(%rip), %ymm2, %ymm6
	vpmullw .Ltile4_bm_qinv(%rip), %ymm3, %ymm7
	vpmullw .Ltile4_bm_qinv(%rip), %ymm4, %ymm8

	/* c0 = a0*b0 + lambda*(a1*b3 + a2*b2 + a3*b1). */
	TILE4_MONT_FIRST ymm2,ymm6,ymm12
	TILE4_MONT_ADD   ymm3,ymm7,ymm11
	TILE4_MONT_ADD   ymm4,ymm8,ymm10
	TILE4_MONT_LAMBDA
	TILE4_MONT_ADD   ymm1,ymm5,ymm9
	\finalizer0
	vmovdqu %ymm15, 0(%rdi)

	/* c1 = a0*b1 + a1*b0 + lambda*(a2*b3 + a3*b2). */
	TILE4_MONT_FIRST ymm3,ymm7,ymm12
	TILE4_MONT_ADD   ymm4,ymm8,ymm11
	TILE4_MONT_LAMBDA
	TILE4_MONT_ADD   ymm1,ymm5,ymm10
	TILE4_MONT_ADD   ymm2,ymm6,ymm9
	\finalizer1
	vmovdqu %ymm15, 32(%rdi)

	/* c2 = a0*b2 + a1*b1 + a2*b0 + lambda*a3*b3. */
	TILE4_MONT_FIRST ymm4,ymm8,ymm12
	TILE4_MONT_LAMBDA
	TILE4_MONT_ADD   ymm1,ymm5,ymm11
	TILE4_MONT_ADD   ymm2,ymm6,ymm10
	TILE4_MONT_ADD   ymm3,ymm7,ymm9
	\finalizer2
	vmovdqu %ymm15, 64(%rdi)

	/* c3 = a0*b3 + a1*b2 + a2*b1 + a3*b0. */
	TILE4_MONT_FIRST ymm1,ymm5,ymm12
	TILE4_MONT_ADD   ymm2,ymm6,ymm11
	TILE4_MONT_ADD   ymm3,ymm7,ymm10
	TILE4_MONT_ADD   ymm4,ymm8,ymm9
	\finalizer3
	vmovdqu %ymm15, 96(%rdi)

	\output

	addq $128, %rsi
	addq $128, %rdx
	addq $128, %rdi
	addq $32, %r8
	addq $32, %r9
	decl %ecx
	jne .Ltile4_bm_loop\@
	vzeroupper
	ret
	.size \name,.-\name
	.endm

	TILE4_BASEMUL_FUNCTION gt32_tile4_basemul_b2_asm, \
		TILE4_CENTER_RMINUS1,TILE4_CENTER_RMINUS1, \
		TILE4_CENTER_RMINUS1,TILE4_CENTER_RMINUS1,TILE4_OUTPUT_AOS
	TILE4_BASEMUL_FUNCTION gt32_tile4_basemul_scale_soa_private_asm, \
		TILE4_CENTER_RMINUS1,TILE4_CENTER_RMINUS1, \
		TILE4_CENTER_RMINUS1,TILE4_CENTER_RMINUS1,TILE4_OUTPUT_SOA_PRIVATE
	TILE4_BASEMUL_FUNCTION gt32_tile4_basemul_raw_soa_private_asm, \
		TILE4_NO_FINALIZER,TILE4_NO_FINALIZER, \
		TILE4_NO_FINALIZER,TILE4_NO_FINALIZER,TILE4_OUTPUT_SOA_PRIVATE
	TILE4_BASEMUL_FUNCTION gt32_tile4_basemul_raw_aos_private_asm, \
		TILE4_NO_FINALIZER,TILE4_NO_FINALIZER, \
		TILE4_NO_FINALIZER,TILE4_NO_FINALIZER,TILE4_OUTPUT_AOS
	TILE4_BASEMUL_FUNCTION gt32_tile4_basemul_c3center_aos_private_asm, \
		TILE4_NO_FINALIZER,TILE4_NO_FINALIZER, \
		TILE4_NO_FINALIZER,TILE4_CENTER_RMINUS1,TILE4_OUTPUT_AOS
	TILE4_BASEMUL_FUNCTION gt32_tile4_basemul_general_b2_asm, \
		TILE4_MONT_RSQ,TILE4_MONT_RSQ, \
		TILE4_MONT_RSQ,TILE4_MONT_RSQ,TILE4_OUTPUT_AOS
	TILE4_BASEMUL_B3_FUNCTION gt32_tile4_basemul_b3_late_asm, \
		TILE4_OUTPUT_AOS_LATE_CENTER
	TILE4_BASEMUL_B3_FUNCTION gt32_tile4_basemul_c3center_late_aos_private_asm, \
		TILE4_OUTPUT_AOS_LATE_C3CENTER
	TILE4_BASEMUL_B4B_FUNCTION gt32_tile4_basemul_b4b_partial_asm
	TILE4_BASEMUL_K2_FUNCTION gt32_tile4_basemul_k2_asm

	.section .rodata
	.p2align 5
.Ltile4_bm_q:
	.rept 16
	.short 3457
	.endr
.Ltile4_bm_qinv:
	.rept 16
	.short 12929
	.endr
.Ltile4_bm_center10:
	.rept 16
	.short 10
	.endr
.Ltile4_bm_rsq:
	.rept 16
	.short 867
	.endr
.Ltile4_bm_rsq_qinv:
	.rept 16
	.short 2787
	.endr

#include "../generated/tile4_basemul_constants.inc"

	.section .note.GNU-stack,"",@progbits
