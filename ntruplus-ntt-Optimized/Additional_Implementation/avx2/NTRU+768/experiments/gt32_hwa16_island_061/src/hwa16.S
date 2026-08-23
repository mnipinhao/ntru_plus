/* HWA16 natural-Q coefficient-plane NTT32 island. */

	.text

	.macro HWA_LOAD
	vmovdqu 0(%rsi), %ymm0
	vmovdqu 32(%rsi), %ymm1
	vmovdqu 64(%rsi), %ymm2
	vmovdqu 96(%rsi), %ymm3
	vmovdqu 128(%rsi), %ymm4
	vmovdqu 160(%rsi), %ymm5
	vmovdqu 192(%rsi), %ymm6
	vmovdqu 224(%rsi), %ymm7
	.endm

	.macro HWA_STORE
	vmovdqu %ymm0, 0(%rdi)
	vmovdqu %ymm1, 32(%rdi)
	vmovdqu %ymm2, 64(%rdi)
	vmovdqu %ymm3, 96(%rdi)
	vmovdqu %ymm4, 128(%rdi)
	vmovdqu %ymm5, 160(%rdi)
	vmovdqu %ymm6, 192(%rdi)
	vmovdqu %ymm7, 224(%rdi)
	.endm

	.macro HWA_RAW_CROSS4 l0,h0,l1,h1,l2,h2,l3,h3
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

	.macro HWA_MONT_CROSS4 l0,h0,l1,h1,l2,h2,l3,h3,qinv,factor
	vpmullw \qinv+0(%rip), \h0, %ymm8
	vpmullw \qinv+32(%rip), \h1, %ymm9
	vpmullw \qinv+64(%rip), \h2, %ymm10
	vpmullw \qinv+96(%rip), \h3, %ymm11
	vpmulhw \factor+0(%rip), \h0, \h0
	vpmulhw \factor+32(%rip), \h1, \h1
	vpmulhw \factor+64(%rip), \h2, \h2
	vpmulhw \factor+96(%rip), \h3, \h3
	vpmulhw %ymm15, %ymm8, %ymm8
	vpmulhw %ymm15, %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpmulhw %ymm15, %ymm11, %ymm11
	vpsubw %ymm8, \h0, \h0
	vpsubw %ymm9, \h1, \h1
	vpsubw %ymm10, \h2, \h2
	vpsubw %ymm11, \h3, \h3
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

	/* V1: one HWA vector at a time. */
	.macro HWA_V1_D8 value,qinv,factor,offset
	vperm2i128 $0x00, \value, \value, %ymm8
	vperm2i128 $0x11, \value, \value, %ymm9
	vpmullw \qinv+\offset(%rip), %ymm9, %ymm10
	vpmulhw \factor+\offset(%rip), %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vperm2i128 $0x20, %ymm10, %ymm8, \value
	.endm

	.macro HWA_V1_LOCAL value,qinv,factor,offset,lowmask,highmask,blend
	vpshufb \lowmask(%rip), \value, %ymm8
	vpshufb \highmask(%rip), \value, %ymm9
	vpmullw \qinv+\offset(%rip), %ymm9, %ymm10
	vpmulhw \factor+\offset(%rip), %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vpblendw $\blend, %ymm10, %ymm8, \value
	.endm

	.macro HWA_V1_RAW_LOCAL value,lowmask,highmask,blend
	vpshufb \lowmask(%rip), \value, %ymm8
	vpshufb \highmask(%rip), \value, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vpblendw $\blend, %ymm10, %ymm8, \value
	.endm

	.macro HWA_APPLY8_V1_D8 qinv,factor
	HWA_V1_D8 %ymm0,\qinv,\factor,0
	HWA_V1_D8 %ymm1,\qinv,\factor,32
	HWA_V1_D8 %ymm2,\qinv,\factor,64
	HWA_V1_D8 %ymm3,\qinv,\factor,96
	HWA_V1_D8 %ymm4,\qinv,\factor,128
	HWA_V1_D8 %ymm5,\qinv,\factor,160
	HWA_V1_D8 %ymm6,\qinv,\factor,192
	HWA_V1_D8 %ymm7,\qinv,\factor,224
	.endm

	.macro HWA_APPLY8_V1_LOCAL qinv,factor,low,high,blend
	HWA_V1_LOCAL %ymm0,\qinv,\factor,0,\low,\high,\blend
	HWA_V1_LOCAL %ymm1,\qinv,\factor,32,\low,\high,\blend
	HWA_V1_LOCAL %ymm2,\qinv,\factor,64,\low,\high,\blend
	HWA_V1_LOCAL %ymm3,\qinv,\factor,96,\low,\high,\blend
	HWA_V1_LOCAL %ymm4,\qinv,\factor,128,\low,\high,\blend
	HWA_V1_LOCAL %ymm5,\qinv,\factor,160,\low,\high,\blend
	HWA_V1_LOCAL %ymm6,\qinv,\factor,192,\low,\high,\blend
	HWA_V1_LOCAL %ymm7,\qinv,\factor,224,\low,\high,\blend
	.endm

	.macro HWA_APPLY8_V1_RAW low,high,blend
	HWA_V1_RAW_LOCAL %ymm0,\low,\high,\blend
	HWA_V1_RAW_LOCAL %ymm1,\low,\high,\blend
	HWA_V1_RAW_LOCAL %ymm2,\low,\high,\blend
	HWA_V1_RAW_LOCAL %ymm3,\low,\high,\blend
	HWA_V1_RAW_LOCAL %ymm4,\low,\high,\blend
	HWA_V1_RAW_LOCAL %ymm5,\low,\high,\blend
	HWA_V1_RAW_LOCAL %ymm6,\low,\high,\blend
	HWA_V1_RAW_LOCAL %ymm7,\low,\high,\blend
	.endm

	.p2align 5
	.globl hwa16_forward_v1_asm
	.type hwa16_forward_v1_asm,@function
hwa16_forward_v1_asm:
	vmovdqa .Lhwa_q(%rip), %ymm15
	HWA_LOAD
	HWA_RAW_CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7
	HWA_APPLY8_V1_D8 .Lhwa_fwd_s2_qinv,.Lhwa_fwd_s2_factor
	HWA_APPLY8_V1_LOCAL .Lhwa_fwd_s3_qinv,.Lhwa_fwd_s3_factor,.Lhwa_d4_lowmask,.Lhwa_d4_highmask,0xf0
	HWA_APPLY8_V1_LOCAL .Lhwa_fwd_s4_qinv,.Lhwa_fwd_s4_factor,.Lhwa_d2_lowmask,.Lhwa_d2_highmask,0xcc
	HWA_APPLY8_V1_LOCAL .Lhwa_fwd_s5_qinv,.Lhwa_fwd_s5_factor,.Lhwa_d1_lowmask,.Lhwa_d1_highmask,0xaa
	HWA_STORE
	vzeroupper
	ret
	.size hwa16_forward_v1_asm,.-hwa16_forward_v1_asm

	.p2align 5
	.globl hwa16_inverse_v1_asm
	.type hwa16_inverse_v1_asm,@function
hwa16_inverse_v1_asm:
	vmovdqa .Lhwa_q(%rip), %ymm15
	HWA_LOAD
	HWA_APPLY8_V1_RAW .Lhwa_d1_lowmask,.Lhwa_d1_highmask,0xaa
	HWA_APPLY8_V1_LOCAL .Lhwa_inv_s1_qinv,.Lhwa_inv_s1_factor,.Lhwa_d2_lowmask,.Lhwa_d2_highmask,0xcc
	HWA_APPLY8_V1_LOCAL .Lhwa_inv_s2_qinv,.Lhwa_inv_s2_factor,.Lhwa_d4_lowmask,.Lhwa_d4_highmask,0xf0
	HWA_APPLY8_V1_D8 .Lhwa_inv_s3_qinv,.Lhwa_inv_s3_factor
	HWA_MONT_CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7,.Lhwa_inv_s4_cross_qinv,.Lhwa_inv_s4_cross_factor
	HWA_STORE
	vzeroupper
	ret
	.size hwa16_inverse_v1_asm,.-hwa16_inverse_v1_asm

	/* V2 mutation: pack two independent HWA vectors per routing operation. */
	.macro HWA_V2_D8 v0,v1,qinv,factor,offset
	vperm2i128 $0x20, \v1, \v0, %ymm8
	vperm2i128 $0x31, \v1, \v0, %ymm9
	vpmullw \qinv+\offset(%rip), %ymm9, %ymm10
	vpmulhw \factor+\offset(%rip), %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vperm2i128 $0x20, %ymm10, %ymm8, \v0
	vperm2i128 $0x31, %ymm10, %ymm8, \v1
	.endm

	.macro HWA_V2_D4 v0,v1,qinv,factor,offset
	vpunpcklqdq \v1, \v0, %ymm8
	vpunpckhqdq \v1, \v0, %ymm9
	vpmullw \qinv+\offset(%rip), %ymm9, %ymm10
	vpmulhw \factor+\offset(%rip), %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vpunpcklqdq %ymm10, %ymm8, \v0
	vpunpckhqdq %ymm10, %ymm8, \v1
	.endm

	.macro HWA_V2_D2 v0,v1,qinv,factor,offset
	vshufps $0x88, \v1, \v0, %ymm8
	vshufps $0xdd, \v1, \v0, %ymm9
	vpmullw \qinv+\offset(%rip), %ymm9, %ymm10
	vpmulhw \factor+\offset(%rip), %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vpunpckldq %ymm10, %ymm8, \v0
	vpunpckhdq %ymm10, %ymm8, \v1
	.endm

	.macro HWA_V2_RAW_D2 v0,v1
	vshufps $0x88, \v1, \v0, %ymm8
	vshufps $0xdd, \v1, \v0, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vpunpckldq %ymm10, %ymm8, \v0
	vpunpckhdq %ymm10, %ymm8, \v1
	.endm

	.macro HWA_V2_RAW_D4 v0,v1
	vpunpcklqdq \v1, \v0, %ymm8
	vpunpckhqdq \v1, \v0, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vpunpcklqdq %ymm10, %ymm8, \v0
	vpunpckhqdq %ymm10, %ymm8, \v1
	.endm

	.macro HWA_APPLY4_V2 macro,qinv,factor
	\macro %ymm0,%ymm1,\qinv,\factor,0
	\macro %ymm2,%ymm3,\qinv,\factor,32
	\macro %ymm4,%ymm5,\qinv,\factor,64
	\macro %ymm6,%ymm7,\qinv,\factor,96
	.endm

	.p2align 5
	.globl hwa16_forward_v2_asm
	.type hwa16_forward_v2_asm,@function
hwa16_forward_v2_asm:
	vmovdqa .Lhwa_q(%rip), %ymm15
	HWA_LOAD
	HWA_RAW_CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7
	HWA_APPLY4_V2 HWA_V2_D8,.Lhwa_fwd_s2_pair_qinv,.Lhwa_fwd_s2_pair_factor
	HWA_APPLY4_V2 HWA_V2_D4,.Lhwa_fwd_s3_pair_qinv,.Lhwa_fwd_s3_pair_factor
	HWA_APPLY4_V2 HWA_V2_D2,.Lhwa_fwd_s4_pair_qinv,.Lhwa_fwd_s4_pair_factor
	HWA_APPLY8_V1_LOCAL .Lhwa_fwd_s5_qinv,.Lhwa_fwd_s5_factor,.Lhwa_d1_lowmask,.Lhwa_d1_highmask,0xaa
	HWA_STORE
	vzeroupper
	ret
	.size hwa16_forward_v2_asm,.-hwa16_forward_v2_asm

	.p2align 5
	.globl hwa16_inverse_v2_asm
	.type hwa16_inverse_v2_asm,@function
hwa16_inverse_v2_asm:
	vmovdqa .Lhwa_q(%rip), %ymm15
	HWA_LOAD
	HWA_APPLY8_V1_RAW .Lhwa_d1_lowmask,.Lhwa_d1_highmask,0xaa
	HWA_APPLY4_V2 HWA_V2_D2,.Lhwa_inv_s1_pair_qinv,.Lhwa_inv_s1_pair_factor
	HWA_APPLY4_V2 HWA_V2_D4,.Lhwa_inv_s2_pair_qinv,.Lhwa_inv_s2_pair_factor
	HWA_APPLY4_V2 HWA_V2_D8,.Lhwa_inv_s3_pair_qinv,.Lhwa_inv_s3_pair_factor
	HWA_MONT_CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7,.Lhwa_inv_s4_cross_qinv,.Lhwa_inv_s4_cross_factor
	HWA_STORE
	vzeroupper
	ret
	.size hwa16_inverse_v2_asm,.-hwa16_inverse_v2_asm

	/* Native HWA16 coefficient-plane B3, e=0 x e=0 -> e=-1. */
	.macro HWA_BM_FIRST a,aq,b
	vpmullw \aq, \b, %ymm13
	vpmulhw \a, \b, %ymm15
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw %ymm13, %ymm15, %ymm15
	.endm
	.macro HWA_BM_ADD a,aq,b
	vpmullw \aq, \b, %ymm13
	vpmulhw \a, \b, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw %ymm13, %ymm14, %ymm14
	vpaddw %ymm14, %ymm15, %ymm15
	.endm
	.macro HWA_BM_LAMBDA
	vpmullw (%r9), %ymm15, %ymm13
	vpmulhw (%r8), %ymm15, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw %ymm13, %ymm14, %ymm15
	.endm

	.macro HWA_BM_GROUP g
	vmovdqu (\g*32)(%rdx), %ymm9
	vmovdqu ((2+\g)*32)(%rdx), %ymm10
	vmovdqu ((4+\g)*32)(%rdx), %ymm11
	vmovdqu ((6+\g)*32)(%rdx), %ymm12
	vmovdqu (\g*32)(%rsi), %ymm1
	vmovdqu ((2+\g)*32)(%rsi), %ymm2
	vmovdqu ((4+\g)*32)(%rsi), %ymm3
	vmovdqu ((6+\g)*32)(%rsi), %ymm4
	vpmullw .Lhwa_bm_qinv_scalar(%rip), %ymm1, %ymm5
	vpmullw .Lhwa_bm_qinv_scalar(%rip), %ymm2, %ymm6
	vpmullw .Lhwa_bm_qinv_scalar(%rip), %ymm3, %ymm7
	vpmullw .Lhwa_bm_qinv_scalar(%rip), %ymm4, %ymm8
	HWA_BM_FIRST %ymm2,%ymm6,%ymm12
	HWA_BM_ADD %ymm3,%ymm7,%ymm11
	HWA_BM_ADD %ymm4,%ymm8,%ymm10
	HWA_BM_LAMBDA
	HWA_BM_ADD %ymm1,%ymm5,%ymm9
	vmovdqu %ymm15, (\g*32)(%rdi)
	HWA_BM_FIRST %ymm3,%ymm7,%ymm12
	HWA_BM_ADD %ymm4,%ymm8,%ymm11
	HWA_BM_LAMBDA
	HWA_BM_ADD %ymm1,%ymm5,%ymm10
	HWA_BM_ADD %ymm2,%ymm6,%ymm9
	vmovdqu %ymm15, ((2+\g)*32)(%rdi)
	HWA_BM_FIRST %ymm4,%ymm8,%ymm12
	HWA_BM_LAMBDA
	HWA_BM_ADD %ymm1,%ymm5,%ymm11
	HWA_BM_ADD %ymm2,%ymm6,%ymm10
	HWA_BM_ADD %ymm3,%ymm7,%ymm9
	vmovdqu %ymm15, ((4+\g)*32)(%rdi)
	HWA_BM_FIRST %ymm1,%ymm5,%ymm12
	HWA_BM_ADD %ymm2,%ymm6,%ymm11
	HWA_BM_ADD %ymm3,%ymm7,%ymm10
	HWA_BM_ADD %ymm4,%ymm8,%ymm9
	vpmulhrsw .Lhwa_center10(%rip), %ymm15, %ymm14
	vpmullw %ymm0, %ymm14, %ymm14
	vpsubw %ymm14, %ymm15, %ymm15
	vmovdqu %ymm15, ((6+\g)*32)(%rdi)
	.endm

	.p2align 5
	.globl hwa16_basemul_asm
	.type hwa16_basemul_asm,@function
hwa16_basemul_asm:
	vmovdqa .Lhwa_q(%rip), %ymm0
	leaq .Lhwa_bm_lambda(%rip), %r8
	leaq .Lhwa_bm_lambda_qinv(%rip), %r9
	HWA_BM_GROUP 0
	addq $32, %r8
	addq $32, %r9
	HWA_BM_GROUP 1
	vzeroupper
	ret
	.size hwa16_basemul_asm,.-hwa16_basemul_asm

	.section .rodata
#include "../generated/hwa16_constants.inc"
	.p2align 5
.Lhwa_bm_qinv_scalar:
	.rept 16
	.short 12929
	.endr

	.section .note.GNU-stack,"",@progbits
