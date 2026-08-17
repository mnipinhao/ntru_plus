/*
 * P-J1 lane-wise batch inversion for twelve 16-lane determinant vectors.
 *
 * This is the same prefix-product / one-field-inverse algorithm as the C
 * oracle in gt_baseinv_native.c.  Prefix and operand_qinv have deliberately
 * separate stack slots.  An earlier 352-byte variant recomputed operand_qinv
 * in the backward scan; PMU showed that eleven extra vpmullw operations cost
 * more than their L1 stack traffic on the target core.
 *
 * int gt32_p_j1_batch_inverse_asm(int16_t determinant[12][16]);
 */

	.section .text.gt32_p_j1_batch_inverse_prefix,"ax",@progbits
	.p2align 5

	/* dst = a*b*R^-1 (mod q); tmp is destroyed. */
	.macro PJ1_MONT dst, a, b, tmp
	vpmullw \b, \a, \tmp
	vpmulhw \b, \a, \dst
	vpmullw %ymm14, \tmp, \tmp
	vpmulhw %ymm15, \tmp, \tmp
	vpsubw  \tmp, \dst, \dst
	.endm

	/* dst = a*factor*R^-1; factor_qinv = factor*qinv (low word). */
	.macro PJ1_MONT_FIXED dst, a, factor, factor_qinv, tmp
	vpmullw \factor_qinv, \a, \tmp
	vpmulhw \factor, \a, \dst
	vpmulhw %ymm15, \tmp, \tmp
	vpsubw  \tmp, \dst, \dst
	.endm

	.macro PJ1_MONT2 d0,a0,b0,d1,a1,b1,t0,t1
	vpmullw \b0, \a0, \t0
	vpmullw \b1, \a1, \t1
	vpmulhw \b0, \a0, \d0
	vpmulhw \b1, \a1, \d1
	vpmullw %ymm14, \t0, \t0
	vpmullw %ymm14, \t1, \t1
	vpmulhw %ymm15, \t0, \t0
	vpmulhw %ymm15, \t1, \t1
	vpsubw \t0, \d0, \d0
	vpsubw \t1, \d1, \d1
	.endm

	.macro PJ1_MONT4 d0,a0,b0,d1,a1,b1,d2,a2,b2,d3,a3,b3,t0,t1,t2,t3
	vpmullw \b0, \a0, \t0
	vpmullw \b1, \a1, \t1
	vpmullw \b2, \a2, \t2
	vpmullw \b3, \a3, \t3
	vpmulhw \b0, \a0, \d0
	vpmulhw \b1, \a1, \d1
	vpmulhw \b2, \a2, \d2
	vpmulhw \b3, \a3, \d3
	vpmullw %ymm14, \t0, \t0
	vpmullw %ymm14, \t1, \t1
	vpmullw %ymm14, \t2, \t2
	vpmullw %ymm14, \t3, \t3
	vpmulhw %ymm15, \t0, \t0
	vpmulhw %ymm15, \t1, \t1
	vpmulhw %ymm15, \t2, \t2
	vpmulhw %ymm15, \t3, \t3
	vpsubw \t0, \d0, \d0
	vpsubw \t1, \d1, \d1
	vpsubw \t2, \d2, \d2
	vpsubw \t3, \d3, \d3
	.endm

	/* ymm0 -> ymm0; constants ymm14/15 must already be live. */
	.macro PJ1_FIELD_INVERSE
	vpmullw %ymm14, %ymm0, %ymm1
	PJ1_MONT %ymm2, %ymm0, %ymm0, %ymm7
	vpmullw %ymm14, %ymm2, %ymm3
	PJ1_MONT %ymm4, %ymm2, %ymm2, %ymm7
	PJ1_MONT %ymm4, %ymm4, %ymm4, %ymm7
	PJ1_MONT %ymm6, %ymm4, %ymm4, %ymm7
	PJ1_MONT_FIXED %ymm2, %ymm4, %ymm2, %ymm3, %ymm7
	vpmullw %ymm14, %ymm2, %ymm3
	PJ1_MONT_FIXED %ymm4, %ymm6, %ymm2, %ymm3, %ymm7
	PJ1_MONT %ymm4, %ymm4, %ymm4, %ymm7
	PJ1_MONT_FIXED %ymm4, %ymm4, %ymm0, %ymm1, %ymm7
	PJ1_MONT_FIXED %ymm2, %ymm4, %ymm2, %ymm3, %ymm7
	.rept 6
	PJ1_MONT %ymm4, %ymm4, %ymm4, %ymm7
	.endr
	vpmullw %ymm14, %ymm4, %ymm5
	PJ1_MONT_FIXED %ymm4, %ymm2, %ymm4, %ymm5, %ymm7
	vpcmpeqd %ymm6, %ymm6, %ymm6
	vpsrlw $15, %ymm6, %ymm6
	PJ1_MONT_FIXED %ymm0, %ymm4, %ymm6, %ymm14, %ymm7
	.endm

	.globl gt32_p_j1_batch_inverse_asm
	.type gt32_p_j1_batch_inverse_asm,@function
gt32_p_j1_batch_inverse_asm:
	/* Eleven prefixes followed by eleven saved operand_qinv vectors. */
	subq $704, %rsp
	vpbroadcastd .Lpj1_q(%rip), %ymm15
	vpbroadcastd .Lpj1_qinv(%rip), %ymm14

	/* Forward prefix scan.  ymm0 remains the current prefix. */
	vmovdqu   0(%rdi), %ymm0
	vmovdqu %ymm0,   0(%rsp)
	.irp I,1,2,3,4,5,6,7,8,9,10
	vmovdqu (\I*32)(%rdi), %ymm1
	vpmullw %ymm14, %ymm1, %ymm2
	vmovdqu %ymm2, (320+\I*32)(%rsp)
	PJ1_MONT_FIXED %ymm0, %ymm0, %ymm1, %ymm2, %ymm3
	vmovdqu %ymm0, (\I*32)(%rsp)
	.endr
	vmovdqu 352(%rdi), %ymm1
	vpmullw %ymm14, %ymm1, %ymm2
	vmovdqu %ymm2, 672(%rsp)
	PJ1_MONT_FIXED %ymm0, %ymm0, %ymm1, %ymm2, %ymm3

	/* Reject if any of the sixteen total products is zero. */
	vpxor %ymm4, %ymm4, %ymm4
	vpcmpeqw %ymm4, %ymm0, %ymm4
	vptest %ymm4, %ymm4
	jnz .Lpj1_failure

	/*
	 * Field inverse x^(q-2), q=3457.  Register assignment:
	 *   r=ymm0, r_qinv=ymm1, t1=ymm2, t1_qinv=ymm3,
	 *   t2=ymm4, t2_qinv=ymm5, t3=ymm6, tmp=ymm7.
	 */
	vpmullw %ymm14, %ymm0, %ymm1
	PJ1_MONT %ymm2, %ymm0, %ymm0, %ymm7
	vpmullw %ymm14, %ymm2, %ymm3
	PJ1_MONT %ymm4, %ymm2, %ymm2, %ymm7
	PJ1_MONT %ymm4, %ymm4, %ymm4, %ymm7
	PJ1_MONT %ymm6, %ymm4, %ymm4, %ymm7
	PJ1_MONT_FIXED %ymm2, %ymm4, %ymm2, %ymm3, %ymm7
	vpmullw %ymm14, %ymm2, %ymm3
	PJ1_MONT_FIXED %ymm4, %ymm6, %ymm2, %ymm3, %ymm7
	PJ1_MONT %ymm4, %ymm4, %ymm4, %ymm7
	PJ1_MONT_FIXED %ymm4, %ymm4, %ymm0, %ymm1, %ymm7
	PJ1_MONT_FIXED %ymm2, %ymm4, %ymm2, %ymm3, %ymm7
	.rept 6
	PJ1_MONT %ymm4, %ymm4, %ymm4, %ymm7
	.endr
	vpmullw %ymm14, %ymm4, %ymm5
	PJ1_MONT_FIXED %ymm4, %ymm2, %ymm4, %ymm5, %ymm7

	/* Convert from the exponentiation scale with rinv=1. */
	vpcmpeqd %ymm6, %ymm6, %ymm6
	vpsrlw $15, %ymm6, %ymm6
	PJ1_MONT_FIXED %ymm0, %ymm4, %ymm6, %ymm14, %ymm7

	/*
	 * Backward scan.  ymm0 is the running inverse.
	 */
	.irp I,11,10,9,8,7,6,5,4,3,2,1
	vpmullw %ymm14, %ymm0, %ymm1
	vmovdqu ((\I-1)*32)(%rsp), %ymm2
	vmovdqu (\I*32)(%rdi), %ymm3
	vmovdqu (320+\I*32)(%rsp), %ymm4
	/* Interleave output and running-inverse Montgomery chains. */
	vpmullw %ymm1, %ymm2, %ymm6
	vpmullw %ymm4, %ymm0, %ymm7
	vpmulhw %ymm0, %ymm2, %ymm5
	vpmulhw %ymm3, %ymm0, %ymm0
	vpmulhw %ymm15, %ymm6, %ymm6
	vpmulhw %ymm15, %ymm7, %ymm7
	vpsubw %ymm6, %ymm5, %ymm5
	vpsubw %ymm7, %ymm0, %ymm0
	vmovdqu %ymm5, (\I*32)(%rdi)
	.endr
	vmovdqu %ymm0, 0(%rdi)

	xorl %eax, %eax
	addq $704, %rsp
	vzeroupper
	ret

.Lpj1_failure:
	movl $1, %eax
	addq $704, %rsp
	vzeroupper
	ret
	.size gt32_p_j1_batch_inverse_asm, .-gt32_p_j1_batch_inverse_asm

	/*
	 * Product-tree batch inversion.  It performs the same 33 inter-vector
	 * Montgomery products as the prefix algorithm, but exposes independent
	 * products at each tree level instead of a 22-node running dependency.
	 * Stack layout: p[6], q[3], r0 (ten vectors, 320 bytes).
	 */
	.section .text.gt32_p_j1_batch_inverse_tree,"ax",@progbits
	.p2align 5
	.globl gt32_p_j1_batch_inverse_tree_asm
	.type gt32_p_j1_batch_inverse_tree_asm,@function
gt32_p_j1_batch_inverse_tree_asm:
	subq $320, %rsp
	vpbroadcastd .Lpj1_q(%rip), %ymm15
	vpbroadcastd .Lpj1_qinv(%rip), %ymm14

	/* p0..p5 = pair products. */
	.irp O,0,128,256
	vmovdqu   0+\O(%rdi), %ymm0
	vmovdqu  32+\O(%rdi), %ymm1
	vmovdqu  64+\O(%rdi), %ymm2
	vmovdqu  96+\O(%rdi), %ymm3
	PJ1_MONT2 %ymm4,%ymm0,%ymm1,%ymm5,%ymm2,%ymm3,%ymm6,%ymm7
	vmovdqu %ymm4, (\O/2)(%rsp)
	vmovdqu %ymm5, (\O/2+32)(%rsp)
	.endr

	/* q0=p0*p1, q1=p2*p3, q2=p4*p5. */
	vmovdqu   0(%rsp), %ymm0
	vmovdqu  32(%rsp), %ymm1
	vmovdqu  64(%rsp), %ymm2
	vmovdqu  96(%rsp), %ymm3
	PJ1_MONT2 %ymm4,%ymm0,%ymm1,%ymm5,%ymm2,%ymm3,%ymm6,%ymm7
	vmovdqu %ymm4, 192(%rsp)
	vmovdqu %ymm5, 224(%rsp)
	vmovdqu 128(%rsp), %ymm0
	vmovdqu 160(%rsp), %ymm1
	PJ1_MONT %ymm2, %ymm0, %ymm1, %ymm3
	vmovdqu %ymm2, 256(%rsp)

	/* r0=q0*q1; root=r0*q2. */
	PJ1_MONT %ymm0, %ymm4, %ymm5, %ymm1
	vmovdqu %ymm0, 288(%rsp)
	PJ1_MONT %ymm0, %ymm0, %ymm2, %ymm1
	vpxor %ymm1, %ymm1, %ymm1
	vpcmpeqw %ymm1, %ymm0, %ymm1
	vptest %ymm1, %ymm1
	jnz .Lpj1_tree_failure

	PJ1_FIELD_INVERSE

	/* root -> inverse(r0), inverse(q2). */
	vmovdqu 288(%rsp), %ymm1
	vmovdqu 256(%rsp), %ymm2
	PJ1_MONT2 %ymm3,%ymm0,%ymm2,%ymm4,%ymm0,%ymm1,%ymm5,%ymm6
	vmovdqu %ymm3, 288(%rsp)
	vmovdqu %ymm4, 256(%rsp)

	/* inverse(r0) -> inverse(q0/q1), inverse(q2) -> inverse(p4/p5). */
	vmovdqu 192(%rsp), %ymm0
	vmovdqu 224(%rsp), %ymm1
	vmovdqu 288(%rsp), %ymm2
	PJ1_MONT2 %ymm3,%ymm2,%ymm1,%ymm4,%ymm2,%ymm0,%ymm5,%ymm6
	vmovdqu %ymm3, 192(%rsp)
	vmovdqu %ymm4, 224(%rsp)
	vmovdqu 128(%rsp), %ymm0
	vmovdqu 160(%rsp), %ymm1
	vmovdqu 256(%rsp), %ymm2
	PJ1_MONT2 %ymm3,%ymm2,%ymm1,%ymm4,%ymm2,%ymm0,%ymm5,%ymm6
	vmovdqu %ymm3, 128(%rsp)
	vmovdqu %ymm4, 160(%rsp)

	/* inverse(q0/q1) -> inverse(p0..p3). */
	vmovdqu   0(%rsp), %ymm0
	vmovdqu  32(%rsp), %ymm1
	vmovdqu  64(%rsp), %ymm2
	vmovdqu  96(%rsp), %ymm3
	vmovdqu 192(%rsp), %ymm4
	vmovdqu 224(%rsp), %ymm5
	PJ1_MONT4 %ymm6,%ymm4,%ymm1,%ymm7,%ymm4,%ymm0,%ymm8,%ymm5,%ymm3,%ymm9,%ymm5,%ymm2,%ymm10,%ymm11,%ymm12,%ymm13
	vmovdqu %ymm6,  0(%rsp)
	vmovdqu %ymm7, 32(%rsp)
	vmovdqu %ymm8, 64(%rsp)
	vmovdqu %ymm9, 96(%rsp)

	/* Each inverse(pi) expands to its two original leaf inverses. */
	.irp P,0,2,4
	vmovdqu (\P*32)(%rsp), %ymm0
	vmovdqu ((\P+1)*32)(%rsp), %ymm3
	vmovdqu (\P*64)(%rdi), %ymm1
	vmovdqu (\P*64+32)(%rdi), %ymm2
	vmovdqu (\P*64+64)(%rdi), %ymm4
	vmovdqu (\P*64+96)(%rdi), %ymm5
	PJ1_MONT4 %ymm6,%ymm0,%ymm2,%ymm7,%ymm0,%ymm1,%ymm8,%ymm3,%ymm5,%ymm9,%ymm3,%ymm4,%ymm10,%ymm11,%ymm12,%ymm13
	vmovdqu %ymm6, (\P*64)(%rdi)
	vmovdqu %ymm7, (\P*64+32)(%rdi)
	vmovdqu %ymm8, (\P*64+64)(%rdi)
	vmovdqu %ymm9, (\P*64+96)(%rdi)
	.endr

	xorl %eax, %eax
	addq $320, %rsp
	vzeroupper
	ret
.Lpj1_tree_failure:
	movl $1, %eax
	addq $320, %rsp
	vzeroupper
	ret
	.size gt32_p_j1_batch_inverse_tree_asm, .-gt32_p_j1_batch_inverse_tree_asm

	.section .rodata
	.p2align 2
.Lpj1_q:
	.long 0x0d810d81
.Lpj1_qinv:
	.long 0x32813281

	.section .note.GNU-stack,"",@progbits
