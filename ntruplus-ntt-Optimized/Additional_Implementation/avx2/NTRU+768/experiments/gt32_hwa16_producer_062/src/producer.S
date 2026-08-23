/*
 * Fixed (branch=0,k3=0) producer probe.
 *
 * Each candidate executes the same selected-tile top split, twist and DFT3.
 * P0 emits TILE4 and executes raw distance-16.  P1 explicitly materializes
 * natural-Q HWA16 before distance-16.  P2 retains the lower coefficient
 * planes and directly emits post-stage1 HWA16.
 */

	.text

	.macro P062_GT_BLEND3 x,y,z,r0,r1,r2
	vpblendd $0x0c, \y, \x, \r0
	vpblendd $0x30, \z, \r0, \r0
	vpblendd $0x0c, \x, \z, \r1
	vpblendd $0x30, \y, \r1, \r1
	vpblendd $0x0c, \z, \y, \r2
	vpblendd $0x30, \x, \r2, \r2
	.endm

	/* Leaves the selected k3=0 DFT3 output in ymm3. */
	.macro P062_TILE0_ITER disp,x,y,z
	vmovdqu 0+\disp(%rsi), %ymm0
	vmovdqu 256+\disp(%rsi), %ymm1
	vmovdqu 512+\disp(%rsi), %ymm2
	vmovdqu 768+\disp(%rsi), %ymm3
	vpmullw .Ltile4_frontend_zeta_top_raw(%rip), %ymm3, %ymm3
	vpaddw %ymm3, %ymm0, %ymm0
	vmovdqu 1024+\disp(%rsi), %ymm3
	vpmullw .Ltile4_frontend_zeta_top_raw(%rip), %ymm3, %ymm3
	vpaddw %ymm3, %ymm1, %ymm1
	vmovdqu 1280+\disp(%rsi), %ymm3
	vpmullw .Ltile4_frontend_zeta_top_raw(%rip), %ymm3, %ymm3
	vpaddw %ymm3, %ymm2, %ymm2
	P062_GT_BLEND3 \x,\y,\z,%ymm3,%ymm4,%ymm5
	/* Three independent twist Montgomery products, one temporary reused. */
	vpmullw 0(%rdx), %ymm3, %ymm6
	vpmulhw 0(%rcx), %ymm3, %ymm3
	vpmulhw %ymm15, %ymm6, %ymm6
	vpsubw %ymm6, %ymm3, %ymm3
	vpmullw 32(%rdx), %ymm4, %ymm6
	vpmulhw 32(%rcx), %ymm4, %ymm4
	vpmulhw %ymm15, %ymm6, %ymm6
	vpsubw %ymm6, %ymm4, %ymm4
	vpmullw 64(%rdx), %ymm5, %ymm6
	vpmulhw 64(%rcx), %ymm5, %ymm5
	vpmulhw %ymm15, %ymm6, %ymm6
	vpsubw %ymm6, %ymm5, %ymm5
	/* k3=0 is the sum output of DFT3. */
	vpaddw %ymm4, %ymm3, %ymm3
	vpaddw %ymm5, %ymm3, %ymm3
	addq $192, %rdx
	addq $192, %rcx
	.endm

	/* Four TILE4 packets -> four natural-Q coefficient planes. */
	.macro P062_TRANSPOSE s0,s1,s2,s3,t0,t1,t2,t3
	vpunpcklwd \s1, \s0, \t0
	vpunpckhwd \s1, \s0, \t1
	vpunpcklwd \s3, \s2, \t2
	vpunpckhwd \s3, \s2, \t3
	vpunpckldq \t2, \t0, \s0
	vpunpckhdq \t2, \t0, \s1
	vpunpckldq \t3, \t1, \s2
	vpunpckhdq \t3, \t1, \s3
	vpunpcklqdq \s2, \s0, \t0
	vpunpckhqdq \s2, \s0, \t1
	vpunpcklqdq \s3, \s1, \t2
	vpunpckhqdq \s3, \s1, \t3
	.endm

	/*
	 * P062_TRANSPOSE produces each coefficient plane in the qword-major
	 * order
	 *
	 *   0,4,8,12, 1,5,9,13, 2,6,10,14, 3,7,11,15.
	 *
	 * Natural-Q HWA16 requires 0..15.  Route two planes together so the
	 * cross-128-bit work is amortized across both outputs (8 instructions
	 * for two planes rather than a per-vector repair network).
	 */
	.macro P062_NATURALIZE_PAIR v0,v1,t0,t1,t2,t3,mask
	vperm2i128 $0x20, \v1, \v0, \t0
	vperm2i128 $0x31, \v1, \v0, \t1
	vpshufb \mask, \t0, \t0
	vpshufb \mask, \t1, \t1
	vpunpckldq \t1, \t0, \t2
	vpunpckhdq \t1, \t0, \t3
	vperm2i128 $0x20, \t3, \t2, \v0
	vperm2i128 $0x31, \t3, \t2, \v1
	.endm

	.macro P062_INIT
	leaq .Ltile4_frontend_wide_twist_qinv(%rip), %rdx
	leaq .Ltile4_frontend_wide_twist_factor(%rip), %rcx
	vmovdqa .Lproducer062_q(%rip), %ymm15
	.endm

	.macro P062_LOWER_TO target0,target1,target2,target3
	P062_TILE0_ITER 0,%ymm0,%ymm1,%ymm2
	vmovdqa %ymm3, %ymm12
	P062_TILE0_ITER 32,%ymm1,%ymm2,%ymm0
	vmovdqa %ymm3, %ymm13
	P062_TILE0_ITER 64,%ymm2,%ymm0,%ymm1
	vmovdqa %ymm3, %ymm14
	P062_TILE0_ITER 96,%ymm0,%ymm1,%ymm2
	P062_TRANSPOSE %ymm12,%ymm13,%ymm14,%ymm3,\target0,\target1,\target2,\target3
	.endm

	.macro P062_UPPER_TO target0,target1,target2,target3
	P062_TILE0_ITER 128,%ymm1,%ymm2,%ymm0
	vmovdqa %ymm3, %ymm12
	P062_TILE0_ITER 160,%ymm2,%ymm0,%ymm1
	vmovdqa %ymm3, %ymm13
	P062_TILE0_ITER 192,%ymm0,%ymm1,%ymm2
	vmovdqa %ymm3, %ymm14
	P062_TILE0_ITER 224,%ymm1,%ymm2,%ymm0
	P062_TRANSPOSE %ymm12,%ymm13,%ymm14,%ymm3,\target0,\target1,\target2,\target3
	.endm

	.p2align 6
	.globl producer062_p0_tile4_post_s1_asm
	.type producer062_p0_tile4_post_s1_asm,@function
producer062_p0_tile4_post_s1_asm:
	P062_INIT
	P062_TILE0_ITER 0,%ymm0,%ymm1,%ymm2
	vmovdqu %ymm3, 0(%rdi)
	P062_TILE0_ITER 32,%ymm1,%ymm2,%ymm0
	vmovdqu %ymm3, 32(%rdi)
	P062_TILE0_ITER 64,%ymm2,%ymm0,%ymm1
	vmovdqu %ymm3, 64(%rdi)
	P062_TILE0_ITER 96,%ymm0,%ymm1,%ymm2
	vmovdqu %ymm3, 96(%rdi)
	P062_TILE0_ITER 128,%ymm1,%ymm2,%ymm0
	vmovdqu %ymm3, 128(%rdi)
	P062_TILE0_ITER 160,%ymm2,%ymm0,%ymm1
	vmovdqu %ymm3, 160(%rdi)
	P062_TILE0_ITER 192,%ymm0,%ymm1,%ymm2
	vmovdqu %ymm3, 192(%rdi)
	P062_TILE0_ITER 224,%ymm1,%ymm2,%ymm0
	vmovdqu %ymm3, 224(%rdi)
	/* Existing TILE4 raw distance-16: vectors 0..3 pair with 4..7. */
	vmovdqu 0(%rdi), %ymm0
	vmovdqu 32(%rdi), %ymm1
	vmovdqu 64(%rdi), %ymm2
	vmovdqu 96(%rdi), %ymm3
	vmovdqu 128(%rdi), %ymm4
	vmovdqu 160(%rdi), %ymm5
	vmovdqu 192(%rdi), %ymm6
	vmovdqu 224(%rdi), %ymm7
	vpsubw %ymm4, %ymm0, %ymm8
	vpsubw %ymm5, %ymm1, %ymm9
	vpsubw %ymm6, %ymm2, %ymm10
	vpsubw %ymm7, %ymm3, %ymm11
	vpaddw %ymm4, %ymm0, %ymm0
	vpaddw %ymm5, %ymm1, %ymm1
	vpaddw %ymm6, %ymm2, %ymm2
	vpaddw %ymm7, %ymm3, %ymm3
	vmovdqu %ymm0, 0(%rdi)
	vmovdqu %ymm1, 32(%rdi)
	vmovdqu %ymm2, 64(%rdi)
	vmovdqu %ymm3, 96(%rdi)
	vmovdqu %ymm8, 128(%rdi)
	vmovdqu %ymm9, 160(%rdi)
	vmovdqu %ymm10, 192(%rdi)
	vmovdqu %ymm11, 224(%rdi)
	vzeroupper
	ret
	.size producer062_p0_tile4_post_s1_asm,.-producer062_p0_tile4_post_s1_asm

	.p2align 6
	.globl producer062_p1_hwa_explicit_post_s1_asm
	.type producer062_p1_hwa_explicit_post_s1_asm,@function
producer062_p1_hwa_explicit_post_s1_asm:
	P062_INIT
	P062_LOWER_TO %ymm8,%ymm9,%ymm10,%ymm11
	/* ymm7 is unused by the selected producer wave; retain the route mask. */
	vmovdqa .Lproducer062_naturalize(%rip), %ymm7
	P062_NATURALIZE_PAIR %ymm8,%ymm9,%ymm0,%ymm1,%ymm2,%ymm3,%ymm7
	P062_NATURALIZE_PAIR %ymm10,%ymm11,%ymm0,%ymm1,%ymm2,%ymm3,%ymm7
	vmovdqu %ymm8, 0(%rdi)
	vmovdqu %ymm9, 64(%rdi)
	vmovdqu %ymm10, 128(%rdi)
	vmovdqu %ymm11, 192(%rdi)
	P062_UPPER_TO %ymm8,%ymm9,%ymm10,%ymm11
	P062_NATURALIZE_PAIR %ymm8,%ymm9,%ymm0,%ymm1,%ymm2,%ymm3,%ymm7
	P062_NATURALIZE_PAIR %ymm10,%ymm11,%ymm0,%ymm1,%ymm2,%ymm3,%ymm7
	vmovdqu %ymm8, 32(%rdi)
	vmovdqu %ymm9, 96(%rdi)
	vmovdqu %ymm10, 160(%rdi)
	vmovdqu %ymm11, 224(%rdi)
	/* Explicit pre-S1 HWA materialization followed by raw YMM-pair S1. */
	vmovdqu 0(%rdi), %ymm0
	vmovdqu 32(%rdi), %ymm1
	vmovdqu 64(%rdi), %ymm2
	vmovdqu 96(%rdi), %ymm3
	vmovdqu 128(%rdi), %ymm4
	vmovdqu 160(%rdi), %ymm5
	vmovdqu 192(%rdi), %ymm6
	vmovdqu 224(%rdi), %ymm7
	vpsubw %ymm1, %ymm0, %ymm8
	vpsubw %ymm3, %ymm2, %ymm9
	vpsubw %ymm5, %ymm4, %ymm10
	vpsubw %ymm7, %ymm6, %ymm11
	vpaddw %ymm1, %ymm0, %ymm0
	vpaddw %ymm3, %ymm2, %ymm2
	vpaddw %ymm5, %ymm4, %ymm4
	vpaddw %ymm7, %ymm6, %ymm6
	vmovdqu %ymm0, 0(%rdi)
	vmovdqu %ymm8, 32(%rdi)
	vmovdqu %ymm2, 64(%rdi)
	vmovdqu %ymm9, 96(%rdi)
	vmovdqu %ymm4, 128(%rdi)
	vmovdqu %ymm10, 160(%rdi)
	vmovdqu %ymm6, 192(%rdi)
	vmovdqu %ymm11, 224(%rdi)
	vzeroupper
	ret
	.size producer062_p1_hwa_explicit_post_s1_asm,.-producer062_p1_hwa_explicit_post_s1_asm

	.p2align 6
	.globl producer062_p2_hwa_fused_post_s1_asm
	.type producer062_p2_hwa_fused_post_s1_asm,@function
producer062_p2_hwa_fused_post_s1_asm:
	P062_INIT
	/* Keep Q0..15 coefficient planes live across the upper producer wave. */
	P062_LOWER_TO %ymm8,%ymm9,%ymm10,%ymm11
	vmovdqa .Lproducer062_naturalize(%rip), %ymm7
	P062_NATURALIZE_PAIR %ymm8,%ymm9,%ymm0,%ymm1,%ymm2,%ymm3,%ymm7
	P062_NATURALIZE_PAIR %ymm10,%ymm11,%ymm0,%ymm1,%ymm2,%ymm3,%ymm7
	P062_UPPER_TO %ymm0,%ymm1,%ymm2,%ymm4
	/* ymm8..ymm11 remain live, so use the otherwise dead producer temps. */
	P062_NATURALIZE_PAIR %ymm0,%ymm1,%ymm5,%ymm6,%ymm12,%ymm13,%ymm7
	P062_NATURALIZE_PAIR %ymm2,%ymm4,%ymm5,%ymm6,%ymm12,%ymm13,%ymm7
	/* Directly form and store post-stage1 natural-Q HWA16. */
	vpsubw %ymm0, %ymm8, %ymm12
	vpaddw %ymm0, %ymm8, %ymm8
	vpsubw %ymm1, %ymm9, %ymm13
	vpaddw %ymm1, %ymm9, %ymm9
	vpsubw %ymm2, %ymm10, %ymm14
	vpaddw %ymm2, %ymm10, %ymm10
	vpsubw %ymm4, %ymm11, %ymm3
	vpaddw %ymm4, %ymm11, %ymm11
	vmovdqu %ymm8, 0(%rdi)
	vmovdqu %ymm12, 32(%rdi)
	vmovdqu %ymm9, 64(%rdi)
	vmovdqu %ymm13, 96(%rdi)
	vmovdqu %ymm10, 128(%rdi)
	vmovdqu %ymm14, 160(%rdi)
	vmovdqu %ymm11, 192(%rdi)
	vmovdqu %ymm3, 224(%rdi)
	vzeroupper
	ret
	.size producer062_p2_hwa_fused_post_s1_asm,.-producer062_p2_hwa_fused_post_s1_asm

	.section .rodata
	.p2align 5
.Lproducer062_q:
	.rept 16
	.short 3457
	.endr
	.p2align 5
.Lproducer062_naturalize:
	/* word indices 0,4,1,5,2,6,3,7 in each 128-bit lane */
	.byte 0,1, 8,9, 2,3, 10,11, 4,5, 12,13, 6,7, 14,15
	.byte 0,1, 8,9, 2,3, 10,11, 4,5, 12,13, 6,7, 14,15
#include "tile4_constants.inc"

	.section .note.GNU-stack,"",@progbits
