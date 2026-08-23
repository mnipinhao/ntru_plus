/* V3: persistent coefficient planes with permuted physical Q-bit ownership. */

	.text

	.macro V3_LOAD
	vmovdqu 0(%rsi), %ymm0
	vmovdqu 32(%rsi), %ymm1
	vmovdqu 64(%rsi), %ymm2
	vmovdqu 96(%rsi), %ymm3
	vmovdqu 128(%rsi), %ymm4
	vmovdqu 160(%rsi), %ymm5
	vmovdqu 192(%rsi), %ymm6
	vmovdqu 224(%rsi), %ymm7
	.endm
	.macro V3_STORE
	vmovdqu %ymm0, 0(%rdi)
	vmovdqu %ymm1, 32(%rdi)
	vmovdqu %ymm2, 64(%rdi)
	vmovdqu %ymm3, 96(%rdi)
	vmovdqu %ymm4, 128(%rdi)
	vmovdqu %ymm5, 160(%rdi)
	vmovdqu %ymm6, 192(%rdi)
	vmovdqu %ymm7, 224(%rdi)
	.endm

	.macro V3_RAW_Y
	vpsubw %ymm1, %ymm0, %ymm8
	vpsubw %ymm3, %ymm2, %ymm9
	vpsubw %ymm5, %ymm4, %ymm10
	vpsubw %ymm7, %ymm6, %ymm11
	vpaddw %ymm1, %ymm0, %ymm0
	vpaddw %ymm3, %ymm2, %ymm2
	vpaddw %ymm5, %ymm4, %ymm4
	vpaddw %ymm7, %ymm6, %ymm6
	vmovdqa %ymm8, %ymm1
	vmovdqa %ymm9, %ymm3
	vmovdqa %ymm10, %ymm5
	vmovdqa %ymm11, %ymm7
	.endm

	.macro V3_MONT_Y qinv,factor
	vpmullw \qinv+0(%rip), %ymm1, %ymm8
	vpmullw \qinv+32(%rip), %ymm3, %ymm9
	vpmullw \qinv+64(%rip), %ymm5, %ymm10
	vpmullw \qinv+96(%rip), %ymm7, %ymm11
	vpmulhw \factor+0(%rip), %ymm1, %ymm1
	vpmulhw \factor+32(%rip), %ymm3, %ymm3
	vpmulhw \factor+64(%rip), %ymm5, %ymm5
	vpmulhw \factor+96(%rip), %ymm7, %ymm7
	vpmulhw %ymm15, %ymm8, %ymm8
	vpmulhw %ymm15, %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpmulhw %ymm15, %ymm11, %ymm11
	vpsubw %ymm8, %ymm1, %ymm1
	vpsubw %ymm9, %ymm3, %ymm3
	vpsubw %ymm10, %ymm5, %ymm5
	vpsubw %ymm11, %ymm7, %ymm7
	vpsubw %ymm1, %ymm0, %ymm8
	vpsubw %ymm3, %ymm2, %ymm9
	vpsubw %ymm5, %ymm4, %ymm10
	vpsubw %ymm7, %ymm6, %ymm11
	vpaddw %ymm1, %ymm0, %ymm0
	vpaddw %ymm3, %ymm2, %ymm2
	vpaddw %ymm5, %ymm4, %ymm4
	vpaddw %ymm7, %ymm6, %ymm6
	vmovdqa %ymm8, %ymm1
	vmovdqa %ymm9, %ymm3
	vmovdqa %ymm10, %ymm5
	vmovdqa %ymm11, %ymm7
	.endm

	.macro V3_RAW_W_ONE value
	vpshufb .Lhwa_d1_lowmask(%rip), \value, %ymm8
	vpshufb .Lhwa_d1_highmask(%rip), \value, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vpblendw $0xaa, %ymm10, %ymm8, \value
	.endm
	.macro V3_RAW_W
	V3_RAW_W_ONE %ymm0
	V3_RAW_W_ONE %ymm1
	V3_RAW_W_ONE %ymm2
	V3_RAW_W_ONE %ymm3
	V3_RAW_W_ONE %ymm4
	V3_RAW_W_ONE %ymm5
	V3_RAW_W_ONE %ymm6
	V3_RAW_W_ONE %ymm7
	.endm

	.macro V3_MONT_W_ONE value,qinv,factor,offset
	vpshufb .Lhwa_d1_lowmask(%rip), \value, %ymm8
	vpshufb .Lhwa_d1_highmask(%rip), \value, %ymm9
	vpmullw \qinv+\offset(%rip), %ymm9, %ymm10
	vpmulhw \factor+\offset(%rip), %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vpblendw $0xaa, %ymm10, %ymm8, \value
	.endm
	.macro V3_MONT_W qinv,factor
	V3_MONT_W_ONE %ymm0,\qinv,\factor,0
	V3_MONT_W_ONE %ymm1,\qinv,\factor,32
	V3_MONT_W_ONE %ymm2,\qinv,\factor,64
	V3_MONT_W_ONE %ymm3,\qinv,\factor,96
	V3_MONT_W_ONE %ymm4,\qinv,\factor,128
	V3_MONT_W_ONE %ymm5,\qinv,\factor,160
	V3_MONT_W_ONE %ymm6,\qinv,\factor,192
	V3_MONT_W_ONE %ymm7,\qinv,\factor,224
	.endm

	.macro V3_D8 v0,v1,qinv,factor,offset
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
	.macro V3_D4 v0,v1,qinv,factor,offset
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
	.macro V3_D2 v0,v1,qinv,factor,offset
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
	.macro V3_APPLY4 macro,qinv,factor
	\macro %ymm0,%ymm1,\qinv,\factor,0
	\macro %ymm2,%ymm3,\qinv,\factor,32
	\macro %ymm4,%ymm5,\qinv,\factor,64
	\macro %ymm6,%ymm7,\qinv,\factor,96
	.endm

	.macro V3_FUNCTIONS name,fs2macro,fs3macro,fs4macro,is1macro,is2macro,is3macro
	.p2align 5
	.globl hwa16_v3_forward_\name\()_asm
	.type hwa16_v3_forward_\name\()_asm,@function
hwa16_v3_forward_\name\()_asm:
	vmovdqa .Lhwa_q(%rip), %ymm15
	V3_LOAD
	V3_RAW_W
	V3_APPLY4 \fs2macro,.Lv3_\name\()_fwd_s2_qinv,.Lv3_\name\()_fwd_s2_factor
	V3_APPLY4 \fs3macro,.Lv3_\name\()_fwd_s3_qinv,.Lv3_\name\()_fwd_s3_factor
	V3_APPLY4 \fs4macro,.Lv3_\name\()_fwd_s4_qinv,.Lv3_\name\()_fwd_s4_factor
	V3_MONT_Y .Lv3_\name\()_fwd_s5_qinv,.Lv3_\name\()_fwd_s5_factor
	V3_STORE
	vzeroupper
	ret
	.size hwa16_v3_forward_\name\()_asm,.-hwa16_v3_forward_\name\()_asm

	.p2align 5
	.globl hwa16_v3_inverse_\name\()_asm
	.type hwa16_v3_inverse_\name\()_asm,@function
hwa16_v3_inverse_\name\()_asm:
	vmovdqa .Lhwa_q(%rip), %ymm15
	V3_LOAD
	V3_RAW_Y
	V3_APPLY4 \is1macro,.Lv3_\name\()_inv_s1_qinv,.Lv3_\name\()_inv_s1_factor
	V3_APPLY4 \is2macro,.Lv3_\name\()_inv_s2_qinv,.Lv3_\name\()_inv_s2_factor
	V3_APPLY4 \is3macro,.Lv3_\name\()_inv_s3_qinv,.Lv3_\name\()_inv_s3_factor
	V3_MONT_W .Lv3_\name\()_inv_s4_qinv,.Lv3_\name\()_inv_s4_factor
	V3_STORE
	vzeroupper
	ret
	.size hwa16_v3_inverse_\name\()_asm,.-hwa16_v3_inverse_\name\()_asm
	.endm

	V3_FUNCTIONS m40a,V3_D8,V3_D4,V3_D2,V3_D2,V3_D4,V3_D8
	V3_FUNCTIONS m40b,V3_D2,V3_D4,V3_D8,V3_D8,V3_D4,V3_D2
	V3_FUNCTIONS m40c,V3_D4,V3_D8,V3_D2,V3_D2,V3_D8,V3_D4

	/* Three tiny typed entries share identical coefficient-plane arithmetic. */
	.macro V3_BM_ENTRY name
	.p2align 5
	.globl hwa16_v3_basemul_\name\()_asm
	.type hwa16_v3_basemul_\name\()_asm,@function
hwa16_v3_basemul_\name\()_asm:
	leaq .Lv3_\name\()_lambda(%rip), %r8
	leaq .Lv3_\name\()_lambda_qinv(%rip), %r9
	jmp hwa16_v3_basemul_common_asm
	.size hwa16_v3_basemul_\name\()_asm,.-hwa16_v3_basemul_\name\()_asm
	.endm
	V3_BM_ENTRY m40a
	V3_BM_ENTRY m40b
	V3_BM_ENTRY m40c

	.macro V3_BM_FIRST a,aq,b
	vpmullw \aq, \b, %ymm13
	vpmulhw \a, \b, %ymm15
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw %ymm13, %ymm15, %ymm15
	.endm
	.macro V3_BM_ADD a,aq,b
	vpmullw \aq, \b, %ymm13
	vpmulhw \a, \b, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw %ymm13, %ymm14, %ymm14
	vpaddw %ymm14, %ymm15, %ymm15
	.endm
	.macro V3_BM_LAMBDA
	vpmullw (%r9), %ymm15, %ymm13
	vpmulhw (%r8), %ymm15, %ymm14
	vpmulhw %ymm0, %ymm13, %ymm13
	vpsubw %ymm13, %ymm14, %ymm15
	.endm
	.macro V3_BM_GROUP g
	vmovdqu (\g*32)(%rdx), %ymm9
	vmovdqu ((2+\g)*32)(%rdx), %ymm10
	vmovdqu ((4+\g)*32)(%rdx), %ymm11
	vmovdqu ((6+\g)*32)(%rdx), %ymm12
	vmovdqu (\g*32)(%rsi), %ymm1
	vmovdqu ((2+\g)*32)(%rsi), %ymm2
	vmovdqu ((4+\g)*32)(%rsi), %ymm3
	vmovdqu ((6+\g)*32)(%rsi), %ymm4
	vpmullw .Lv3_bm_qinv_scalar(%rip), %ymm1, %ymm5
	vpmullw .Lv3_bm_qinv_scalar(%rip), %ymm2, %ymm6
	vpmullw .Lv3_bm_qinv_scalar(%rip), %ymm3, %ymm7
	vpmullw .Lv3_bm_qinv_scalar(%rip), %ymm4, %ymm8
	V3_BM_FIRST %ymm2,%ymm6,%ymm12
	V3_BM_ADD %ymm3,%ymm7,%ymm11
	V3_BM_ADD %ymm4,%ymm8,%ymm10
	V3_BM_LAMBDA
	V3_BM_ADD %ymm1,%ymm5,%ymm9
	vmovdqu %ymm15, (\g*32)(%rdi)
	V3_BM_FIRST %ymm3,%ymm7,%ymm12
	V3_BM_ADD %ymm4,%ymm8,%ymm11
	V3_BM_LAMBDA
	V3_BM_ADD %ymm1,%ymm5,%ymm10
	V3_BM_ADD %ymm2,%ymm6,%ymm9
	vmovdqu %ymm15, ((2+\g)*32)(%rdi)
	V3_BM_FIRST %ymm4,%ymm8,%ymm12
	V3_BM_LAMBDA
	V3_BM_ADD %ymm1,%ymm5,%ymm11
	V3_BM_ADD %ymm2,%ymm6,%ymm10
	V3_BM_ADD %ymm3,%ymm7,%ymm9
	vmovdqu %ymm15, ((4+\g)*32)(%rdi)
	V3_BM_FIRST %ymm1,%ymm5,%ymm12
	V3_BM_ADD %ymm2,%ymm6,%ymm11
	V3_BM_ADD %ymm3,%ymm7,%ymm10
	V3_BM_ADD %ymm4,%ymm8,%ymm9
	vpmulhrsw .Lhwa_center10(%rip), %ymm15, %ymm14
	vpmullw %ymm0, %ymm14, %ymm14
	vpsubw %ymm14, %ymm15, %ymm15
	vmovdqu %ymm15, ((6+\g)*32)(%rdi)
	.endm

	.p2align 5
	.type hwa16_v3_basemul_common_asm,@function
hwa16_v3_basemul_common_asm:
	vmovdqa .Lhwa_q(%rip), %ymm0
	V3_BM_GROUP 0
	addq $32, %r8
	addq $32, %r9
	V3_BM_GROUP 1
	vzeroupper
	ret
	.size hwa16_v3_basemul_common_asm,.-hwa16_v3_basemul_common_asm

	.section .rodata
#include "../generated/hwa16_constants.inc"
#include "../generated/v3_constants.inc"
	.p2align 5
.Lv3_bm_qinv_scalar:
	.rept 16
	.short 12929
	.endr

	.section .note.GNU-stack,"",@progbits
