/* Hand-written AVX2 D2 formation/QBM and natural sign-Q inverse64. */
	.text

	.macro MONT_FIXED value,tmp,factor,qinv,off
	vpmullw \qinv+\off(%rip), \value, \tmp
	vpmulhw \factor+\off(%rip), \value, \value
	vpmulhw .Ld2_q(%rip), \tmp, \tmp
	vpsubw \tmp, \value, \value
	.endm

	.macro REDC32 value,tmp
	vpmullw .Ld2_qinv_scalar(%rip), \value, \tmp
	vpand .Ld2_low16(%rip), \tmp, \tmp
	vpmaddwd .Ld2_qpair(%rip), \tmp, \tmp
	vpsubd \tmp, \value, \value
	vpsrad $16, \value, \value
	.endm

	.macro DOT2 a0,a1,b0,b1,out
	vpunpcklwd \a1, \a0, %ymm8
	vpunpckhwd \a1, \a0, %ymm9
	vpunpcklwd \b1, \b0, %ymm10
	vpunpckhwd \b1, \b0, %ymm11
	vpmaddwd %ymm10, %ymm8, %ymm8
	vpmaddwd %ymm11, %ymm9, %ymm9
	REDC32 %ymm8,%ymm12
	REDC32 %ymm9,%ymm12
	vpackssdw %ymm9, %ymm8, \out
	.endm

	/* Build and multiply one sign for sixteen Q values. */
	.macro SIGN_QBM inoff,koff,outoff,formfactor,formq,weightfactor,weightq,sign
	vmovdqu \inoff+64(%rsi), %ymm1
	MONT_FIXED %ymm1,%ymm2,\formfactor,\formq,\koff
	vmovdqu \inoff+0(%rsi), %ymm3
	\sign %ymm1, %ymm3, %ymm3
	vmovdqu \inoff+96(%rsi), %ymm1
	MONT_FIXED %ymm1,%ymm2,\formfactor,\formq,\koff
	vmovdqu \inoff+32(%rsi), %ymm4
	\sign %ymm1, %ymm4, %ymm4
	vmovdqu \inoff+64(%rdx), %ymm1
	MONT_FIXED %ymm1,%ymm2,\formfactor,\formq,\koff
	vmovdqu \inoff+0(%rdx), %ymm5
	\sign %ymm1, %ymm5, %ymm5
	vmovdqu \inoff+96(%rdx), %ymm1
	MONT_FIXED %ymm1,%ymm2,\formfactor,\formq,\koff
	vmovdqu \inoff+32(%rdx), %ymm6
	\sign %ymm1, %ymm6, %ymm6
	vmovdqa %ymm6, %ymm7
	MONT_FIXED %ymm7,%ymm2,\weightfactor,\weightq,\koff
	DOT2 %ymm3,%ymm4,%ymm5,%ymm7,%ymm13
	vmovdqu %ymm13, \outoff(%rdi)
	DOT2 %ymm3,%ymm4,%ymm6,%ymm5,%ymm13
	vmovdqu %ymm13, 128+\outoff(%rdi)
	.endm

	.macro PLUS src,dst,out
	vpaddw \src, \dst, \out
	.endm
	.macro MINUS src,dst,out
	vpsubw \src, \dst, \out
	.endm

	.p2align 5
	.globl d2_inverse64_qbm_asm
	.type d2_inverse64_qbm_asm,@function
d2_inverse64_qbm_asm:
	/* plane0: +Q0..31,-Q0..31; plane1 starts at +128 bytes. */
	SIGN_QBM 0,0,0,.Ld2_mu,.Ld2_mu_qinv,.Ld2_mu,.Ld2_mu_qinv,PLUS
	SIGN_QBM 0,0,64,.Ld2_mu,.Ld2_mu_qinv,.Ld2_neg_mu,.Ld2_neg_mu_qinv,MINUS
	SIGN_QBM 128,32,32,.Ld2_mu,.Ld2_mu_qinv,.Ld2_mu,.Ld2_mu_qinv,PLUS
	SIGN_QBM 128,32,96,.Ld2_mu,.Ld2_mu_qinv,.Ld2_neg_mu,.Ld2_neg_mu_qinv,MINUS
	vzeroupper
	ret
	.size d2_inverse64_qbm_asm,.-d2_inverse64_qbm_asm

	.macro PERM32 inoff,outoff
	vmovdqu \inoff+0(%rsi), %ymm0
	vmovdqu \inoff+32(%rsi), %ymm1
	vperm2i128 $0x00, %ymm0, %ymm0, %ymm4
	vperm2i128 $0x11, %ymm0, %ymm0, %ymm5
	vperm2i128 $0x00, %ymm1, %ymm1, %ymm6
	vperm2i128 $0x11, %ymm1, %ymm1, %ymm7
	vpshufb .Ld2_perm_o0_s0(%rip), %ymm4, %ymm8
	vpshufb .Ld2_perm_o0_s1(%rip), %ymm5, %ymm9
	vpshufb .Ld2_perm_o0_s2(%rip), %ymm6, %ymm10
	vpshufb .Ld2_perm_o0_s3(%rip), %ymm7, %ymm11
	vpor %ymm9, %ymm8, %ymm8
	vpor %ymm11, %ymm10, %ymm10
	vpor %ymm10, %ymm8, %ymm8
	vmovdqu %ymm8, \outoff+0(%rdi)
	vpshufb .Ld2_perm_o1_s0(%rip), %ymm4, %ymm8
	vpshufb .Ld2_perm_o1_s1(%rip), %ymm5, %ymm9
	vpshufb .Ld2_perm_o1_s2(%rip), %ymm6, %ymm10
	vpshufb .Ld2_perm_o1_s3(%rip), %ymm7, %ymm11
	vpor %ymm9, %ymm8, %ymm8
	vpor %ymm11, %ymm10, %ymm10
	vpor %ymm10, %ymm8, %ymm8
	vmovdqu %ymm8, \outoff+32(%rdi)
	.endm
	.macro INTERLEAVE64 off
	vmovdqu \off+0(%rdi), %ymm0
	vmovdqu \off+32(%rdi), %ymm1
	vmovdqu \off+64(%rdi), %ymm2
	vmovdqu \off+96(%rdi), %ymm3
	vpunpcklwd %ymm2, %ymm0, %ymm4
	vpunpckhwd %ymm2, %ymm0, %ymm5
	vpunpcklwd %ymm3, %ymm1, %ymm6
	vpunpckhwd %ymm3, %ymm1, %ymm7
	/* unpack is 128-bit-lane local; restore contiguous r=0..7/8..15. */
	vperm2i128 $0x20, %ymm5, %ymm4, %ymm8
	vperm2i128 $0x31, %ymm5, %ymm4, %ymm9
	vperm2i128 $0x20, %ymm7, %ymm6, %ymm10
	vperm2i128 $0x31, %ymm7, %ymm6, %ymm11
	vmovdqu %ymm8, \off+0(%rdi)
	vmovdqu %ymm9, \off+32(%rdi)
	vmovdqu %ymm10, \off+64(%rdi)
	vmovdqu %ymm11, \off+96(%rdi)
	.endm

	/*
	 * The selected production inverse maps a physical nibble b3b2b1b0 to
	 * r=b1b0b3b2.  This is a 4x4 word transpose inside each sixteen-Q YMM,
	 * not a generic four-source permutation.
	 */
	.macro PERM16 inoff,outoff
	vmovdqu \inoff(%rsi), %ymm0
	vpshufb .Ld2_perm16_stage0(%rip), %ymm0, %ymm0
	vperm2i128 $0x00, %ymm0, %ymm0, %ymm1
	vperm2i128 $0x11, %ymm0, %ymm0, %ymm2
	vpunpckldq %ymm2, %ymm1, %ymm3
	vpunpckhdq %ymm2, %ymm1, %ymm4
	vperm2i128 $0x20, %ymm4, %ymm3, %ymm5
	vmovdqu %ymm5, \outoff(%rdi)
	.endm

	.p2align 5
	.globl d2_inverse64_naturalize_asm
	.type d2_inverse64_naturalize_asm,@function
d2_inverse64_naturalize_asm:
	PERM16 0,0
	PERM16 32,32
	PERM16 64,64
	PERM16 96,96
	INTERLEAVE64 0
	PERM16 128,128
	PERM16 160,160
	PERM16 192,192
	PERM16 224,224
	INTERLEAVE64 128
	vzeroupper
	ret
	.size d2_inverse64_naturalize_asm,.-d2_inverse64_naturalize_asm

	.macro RAW_D1 value
	vpshufb .Ld2_d1_lowmask(%rip), \value, %ymm8
	vpshufb .Ld2_d1_highmask(%rip), \value, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vpblendw $0xaa, %ymm10, %ymm8, \value
	.endm

	.macro PAIR_D2 v0,v1,factor,qinv,off
	vshufps $0x88, \v1, \v0, %ymm8
	vshufps $0xdd, \v1, \v0, %ymm9
	MONT_FIXED %ymm9,%ymm10,\factor,\qinv,\off
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vpunpckldq %ymm10, %ymm8, \v0
	vpunpckhdq %ymm10, %ymm8, \v1
	.endm

	.macro PAIR_D4 v0,v1,factor,qinv,off
	vpunpcklqdq \v1, \v0, %ymm8
	vpunpckhqdq \v1, \v0, %ymm9
	MONT_FIXED %ymm9,%ymm10,\factor,\qinv,\off
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vpunpcklqdq %ymm10, %ymm8, \v0
	vpunpckhqdq %ymm10, %ymm8, \v1
	.endm

	.macro PAIR_D8 v0,v1,factor,qinv,off
	vperm2i128 $0x20, \v1, \v0, %ymm8
	vperm2i128 $0x31, \v1, \v0, %ymm9
	MONT_FIXED %ymm9,%ymm10,\factor,\qinv,\off
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vperm2i128 $0x20, %ymm10, %ymm8, \v0
	vperm2i128 $0x31, %ymm10, %ymm8, \v1
	.endm

	.macro CROSS4 l0,h0,l1,h1,l2,h2,l3,h3,factor,qinv
	MONT_FIXED \h0,%ymm8,\factor,\qinv,0
	MONT_FIXED \h1,%ymm9,\factor,\qinv,32
	MONT_FIXED \h2,%ymm10,\factor,\qinv,0
	MONT_FIXED \h3,%ymm11,\factor,\qinv,32
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

	.macro NORM64 value
	MONT_FIXED \value,%ymm8,.Ld2_norm64_factor,.Ld2_norm64_qinv,0
	.endm

	/* Compress alternating even/odd words from two vectors. */
	.macro EXTRACT_PAIR v0,v1,mask,out
	vpshufb \mask(%rip), \v0, %ymm8
	vpshufb \mask(%rip), \v1, %ymm9
	vpermq $0xd8, %ymm8, %ymm8
	vpermq $0xd8, %ymm9, %ymm9
	vperm2i128 $0x20, %ymm9, %ymm8, \out
	.endm

	.p2align 5
	.globl d2_inverse64_inv_asm
	.type d2_inverse64_inv_asm,@function
d2_inverse64_inv_asm:
	vmovdqu   0(%rsi), %ymm0
	vmovdqu  32(%rsi), %ymm1
	vmovdqu  64(%rsi), %ymm2
	vmovdqu  96(%rsi), %ymm3
	vmovdqu 128(%rsi), %ymm4
	vmovdqu 160(%rsi), %ymm5
	vmovdqu 192(%rsi), %ymm6
	vmovdqu 224(%rsi), %ymm7
	RAW_D1 %ymm0
	RAW_D1 %ymm1
	RAW_D1 %ymm2
	RAW_D1 %ymm3
	RAW_D1 %ymm4
	RAW_D1 %ymm5
	RAW_D1 %ymm6
	RAW_D1 %ymm7
	PAIR_D2 %ymm0,%ymm1,.Ld2_inv_l4_factor,.Ld2_inv_l4_qinv,0
	PAIR_D2 %ymm2,%ymm3,.Ld2_inv_l4_factor,.Ld2_inv_l4_qinv,32
	PAIR_D2 %ymm4,%ymm5,.Ld2_inv_l4_factor,.Ld2_inv_l4_qinv,0
	PAIR_D2 %ymm6,%ymm7,.Ld2_inv_l4_factor,.Ld2_inv_l4_qinv,32
	PAIR_D4 %ymm0,%ymm1,.Ld2_inv_l8_factor,.Ld2_inv_l8_qinv,0
	PAIR_D4 %ymm2,%ymm3,.Ld2_inv_l8_factor,.Ld2_inv_l8_qinv,32
	PAIR_D4 %ymm4,%ymm5,.Ld2_inv_l8_factor,.Ld2_inv_l8_qinv,0
	PAIR_D4 %ymm6,%ymm7,.Ld2_inv_l8_factor,.Ld2_inv_l8_qinv,32
	PAIR_D8 %ymm0,%ymm1,.Ld2_inv_l16_factor,.Ld2_inv_l16_qinv,0
	PAIR_D8 %ymm2,%ymm3,.Ld2_inv_l16_factor,.Ld2_inv_l16_qinv,32
	PAIR_D8 %ymm4,%ymm5,.Ld2_inv_l16_factor,.Ld2_inv_l16_qinv,0
	PAIR_D8 %ymm6,%ymm7,.Ld2_inv_l16_factor,.Ld2_inv_l16_qinv,32
	CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7,.Ld2_inv_l32_factor,.Ld2_inv_l32_qinv
	CROSS4 %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7,.Ld2_inv_l64_factor,.Ld2_inv_l64_qinv
	NORM64 %ymm0
	NORM64 %ymm1
	NORM64 %ymm2
	NORM64 %ymm3
	NORM64 %ymm4
	NORM64 %ymm5
	NORM64 %ymm6
	NORM64 %ymm7
	EXTRACT_PAIR %ymm0,%ymm1,.Ld2_even_mask,%ymm10
	vmovdqu %ymm10, 0(%rdi)
	EXTRACT_PAIR %ymm2,%ymm3,.Ld2_even_mask,%ymm10
	vmovdqu %ymm10, 32(%rdi)
	EXTRACT_PAIR %ymm4,%ymm5,.Ld2_even_mask,%ymm10
	vmovdqu %ymm10, 64(%rdi)
	EXTRACT_PAIR %ymm6,%ymm7,.Ld2_even_mask,%ymm10
	vmovdqu %ymm10, 96(%rdi)
	EXTRACT_PAIR %ymm0,%ymm1,.Ld2_odd_mask,%ymm10
	vmovdqu %ymm10, 128(%rdi)
	EXTRACT_PAIR %ymm2,%ymm3,.Ld2_odd_mask,%ymm10
	vmovdqu %ymm10, 160(%rdi)
	EXTRACT_PAIR %ymm4,%ymm5,.Ld2_odd_mask,%ymm10
	vmovdqu %ymm10, 192(%rdi)
	EXTRACT_PAIR %ymm6,%ymm7,.Ld2_odd_mask,%ymm10
	vmovdqu %ymm10, 224(%rdi)
	vzeroupper
	ret
	.size d2_inverse64_inv_asm,.-d2_inverse64_inv_asm

	.section .rodata
#include "../generated/inverse64_constants.inc"
	/* d1 selects low/high word of each pair inside a 128-bit lane. */
	.p2align 5
.Ld2_d1_lowmask:
	.byte 0,1,0,1,4,5,4,5,8,9,8,9,12,13,12,13
	.byte 0,1,0,1,4,5,4,5,8,9,8,9,12,13,12,13
	.p2align 5
.Ld2_d1_highmask:
	.byte 2,3,2,3,6,7,6,7,10,11,10,11,14,15,14,15
	.byte 2,3,2,3,6,7,6,7,10,11,10,11,14,15,14,15
	.p2align 5
.Ld2_perm16_stage0:
	.byte 0,1,8,9,2,3,10,11,4,5,12,13,6,7,14,15
	.byte 0,1,8,9,2,3,10,11,4,5,12,13,6,7,14,15
	.section .note.GNU-stack,"",@progbits
