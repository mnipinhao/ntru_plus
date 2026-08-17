/* Benchmark-only inverse radix-4 identity specialization.
 *
 * This keeps the public TILE4 inverse contract unchanged.  It combines two
 * adjacent inverse stage-1 radix-2 pairs so the identity qwords bypass
 * Montgomery multiplication while the non-identity qwords share one full
 * YMM Montgomery chain.
 */

.macro IR4_RAW_PAIR v0,v1
	vpunpckhqdq \v1, \v0, %ymm8
	vpunpcklqdq \v1, \v0, %ymm9
	vpsubw %ymm8, %ymm9, %ymm10
	vpaddw %ymm8, %ymm9, %ymm9
	vpunpcklqdq %ymm10, %ymm9, \v0
	vpunpckhqdq %ymm10, %ymm9, \v1
.endm

/* Two MONT_LOCAL_HALF_PAIR operations with the identity qwords separated.
 * Input pairs are (v0,v1) and (v2,v3).  The stage-1 table alternates
 * identity (-147 == R mod q) and non-identity (-366) qwords.
 */
.macro IR4_IDENTITY_TWO_PAIRS v0,v1,v2,v3
	vperm2i128 $0x20, \v1, \v0, %ymm8
	vperm2i128 $0x31, \v1, \v0, %ymm9
	vperm2i128 $0x20, \v3, \v2, %ymm10
	vperm2i128 $0x31, \v3, \v2, %ymm11

	vpunpcklqdq %ymm11, %ymm9, %ymm12
	vpunpckhqdq %ymm11, %ymm9, %ymm13
	vpmullw .Lir4_nonidentity_qinv(%rip), %ymm13, %ymm14
	vpmulhw .Lir4_nonidentity_factor(%rip), %ymm13, %ymm13
	vpmulhw %ymm15, %ymm14, %ymm14
	vpsubw %ymm14, %ymm13, %ymm13

	vpunpcklqdq %ymm13, %ymm12, %ymm9
	vpunpckhqdq %ymm13, %ymm12, %ymm11
	vpsubw %ymm9, %ymm8, %ymm12
	vpaddw %ymm9, %ymm8, %ymm8
	vpsubw %ymm11, %ymm10, %ymm13
	vpaddw %ymm11, %ymm10, %ymm10

	vperm2i128 $0x20, %ymm12, %ymm8, \v0
	vperm2i128 $0x31, %ymm12, %ymm8, \v1
	vperm2i128 $0x20, %ymm13, %ymm10, \v2
	vperm2i128 $0x31, %ymm13, %ymm10, \v3
.endm

.macro IR4_MONT_CROSS4 l0,h0,l1,h1,l2,h2,l3,h3,qinv,factor
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

	.section .text.gt32_tile4_inverse_radix4_identity_asm,"ax",@progbits
	.p2align 5
	.globl gt32_tile4_inverse_radix4_identity_asm
	.type gt32_tile4_inverse_radix4_identity_asm,@function
gt32_tile4_inverse_radix4_identity_asm:
	vmovdqa .Ltile4_q(%rip), %ymm15
	movl $6, %ecx
	.p2align 5
.Lir4_loop:
	vmovdqu   0(%rsi), %ymm0
	vmovdqu  32(%rsi), %ymm1
	vmovdqu  64(%rsi), %ymm2
	vmovdqu  96(%rsi), %ymm3
	vmovdqu 128(%rsi), %ymm4
	vmovdqu 160(%rsi), %ymm5
	vmovdqu 192(%rsi), %ymm6
	vmovdqu 224(%rsi), %ymm7

	IR4_RAW_PAIR %ymm0,%ymm1
	IR4_RAW_PAIR %ymm2,%ymm3
	IR4_RAW_PAIR %ymm4,%ymm5
	IR4_RAW_PAIR %ymm6,%ymm7
	IR4_IDENTITY_TWO_PAIRS %ymm0,%ymm1,%ymm2,%ymm3
	IR4_IDENTITY_TWO_PAIRS %ymm4,%ymm5,%ymm6,%ymm7
	IR4_MONT_CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, .Ltile4_inv_s2_qinv, .Ltile4_inv_s2_factor
	IR4_MONT_CROSS4 %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, .Ltile4_inv_s3_qinv, .Ltile4_inv_s3_factor
	IR4_MONT_CROSS4 %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7, .Ltile4_inv_s4_qinv, .Ltile4_inv_s4_factor

	vmovdqu %ymm0,   0(%rdi)
	vmovdqu %ymm1,  32(%rdi)
	vmovdqu %ymm2,  64(%rdi)
	vmovdqu %ymm3,  96(%rdi)
	vmovdqu %ymm4, 128(%rdi)
	vmovdqu %ymm5, 160(%rdi)
	vmovdqu %ymm6, 192(%rdi)
	vmovdqu %ymm7, 224(%rdi)
	addq $256, %rsi
	addq $256, %rdi
	decl %ecx
	jne .Lir4_loop
	vzeroupper
	ret
	.size gt32_tile4_inverse_radix4_identity_asm,.-gt32_tile4_inverse_radix4_identity_asm

	.section .rodata
	.p2align 5
.Lir4_nonidentity_qinv:
	.short -13422,-13422,-13422,-13422,-13422,-13422,-13422,-13422
	.short -13422,-13422,-13422,-13422,-13422,-13422,-13422,-13422
.Lir4_nonidentity_factor:
	.short -366,-366,-366,-366,-366,-366,-366,-366
	.short -366,-366,-366,-366,-366,-366,-366,-366

#include "../generated/tile4_constants.inc"

	.section .note.GNU-stack,"",@progbits
