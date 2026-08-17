/* GT-N32-INVERSE-ASM-012: typed half-native IDFT3 + InvNTT32. */

	.text

/* Two independent physical groups; identical to the proved IDFT3_V2 order. */
	.macro N32_IDFT3_V2_DUAL
	vpaddw %ymm2, %ymm1, %ymm6
	vpsubw %ymm2, %ymm1, %ymm7
	vpaddw %ymm5, %ymm4, %ymm8
	vpsubw %ymm5, %ymm4, %ymm9
	vpmulhrsw %ymm14, %ymm6, %ymm10
	vpmulhrsw %ymm14, %ymm8, %ymm13
	vpsubw %ymm1, %ymm0, %ymm1
	vpsubw %ymm2, %ymm0, %ymm2
	vpsubw %ymm4, %ymm3, %ymm4
	vpsubw %ymm5, %ymm3, %ymm5
	vpmullw %ymm15, %ymm10, %ymm10
	vpmullw %ymm15, %ymm13, %ymm13
	vpsubw %ymm10, %ymm6, %ymm6
	vpsubw %ymm13, %ymm8, %ymm8
	vpmullw %ymm12, %ymm7, %ymm10
	vpmullw %ymm12, %ymm9, %ymm13
	vpmulhw %ymm11, %ymm7, %ymm7
	vpmulhw %ymm11, %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpmulhw %ymm15, %ymm13, %ymm13
	vpsubw %ymm10, %ymm7, %ymm7
	vpsubw %ymm13, %ymm9, %ymm9
	vpsubw %ymm7, %ymm1, %ymm1
	vpaddw %ymm7, %ymm2, %ymm2
	vpsubw %ymm9, %ymm4, %ymm4
	vpaddw %ymm9, %ymm5, %ymm5
	vpaddw %ymm6, %ymm0, %ymm0
	vpaddw %ymm8, %ymm3, %ymm3
	.endm

	.macro N32_RAW_LOCAL_QWORD_PAIR v0,v1
	vpunpcklqdq \v1, \v0, %ymm8
	vpunpckhqdq \v1, \v0, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vpunpcklqdq %ymm10, %ymm8, \v0
	vpunpckhqdq %ymm10, %ymm8, \v1
	.endm

/* Two ordinary length-4 streams packed into one complete Montgomery chain. */
	.macro N32_MONT_LOCAL_HALF_PAIR v0,v1
	vperm2i128 $0x20, \v1, \v0, %ymm8
	vperm2i128 $0x31, \v1, \v0, %ymm9
	vpmullw .Ln32_inv_l4_pair_qinv(%rip), %ymm9, %ymm10
	vpmulhw .Ln32_inv_l4_pair_factor(%rip), %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vperm2i128 $0x20, %ymm10, %ymm8, \v0
	vperm2i128 $0x31, %ymm10, %ymm8, \v1
	.endm

/*
 * Reflected length-4 pair:
 *   v1=[L(row1)|H(row2)], v2=[L(row2)|H(row1)].
 * Pack [L1|L2] and [H1|H2], execute the ordinary butterflies, then
 * reconstruct [S1|D2] and [S2|D1].  No row-repair representation exists.
 */
	.macro N32_MONT_LOCAL_HALF_REFLECTED v1,v2
	vperm2i128 $0x20, \v2, \v1, %ymm8
	vperm2i128 $0x13, \v2, \v1, %ymm9
	vpmullw .Ln32_inv_l4_pair_qinv(%rip), %ymm9, %ymm10
	vpmulhw .Ln32_inv_l4_pair_factor(%rip), %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vperm2i128 $0x30, %ymm10, %ymm8, \v1
	vperm2i128 $0x21, %ymm10, %ymm8, \v2
	.endm

	.macro N32_MONT_CROSS4 l0,h0,l1,h1,l2,h2,l3,h3,qinv,factor
	vpmullw \qinv+0(%rip),  \h0, %ymm8
	vpmullw \qinv+32(%rip), \h1, %ymm9
	vpmullw \qinv+64(%rip), \h2, %ymm10
	vpmullw \qinv+96(%rip), \h3, %ymm11
	vpmulhw \factor+0(%rip),  \h0, \h0
	vpmulhw \factor+32(%rip), \h1, \h1
	vpmulhw \factor+64(%rip), \h2, \h2
	vpmulhw \factor+96(%rip), \h3, \h3
	vpmulhw %ymm15, %ymm8,  %ymm8
	vpmulhw %ymm15, %ymm9,  %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpmulhw %ymm15, %ymm11, %ymm11
	vpsubw %ymm8,  \h0, \h0
	vpsubw %ymm9,  \h1, \h1
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
	vmovdqa %ymm8,  \h0
	vmovdqa %ymm9,  \h1
	vmovdqa %ymm10, \h2
	vmovdqa %ymm11, \h3
	.endm

	.macro N32_IDFT_L2_L4_PAIR
	vmovdqu   0(%rsi), %ymm0
	vmovdqu  32(%rsi), %ymm1
	vmovdqu  64(%rsi), %ymm2
	vmovdqu  96(%rsi), %ymm3
	vmovdqu 128(%rsi), %ymm4
	vmovdqu 160(%rsi), %ymm5
	N32_IDFT3_V2_DUAL
	N32_RAW_LOCAL_QWORD_PAIR %ymm0,%ymm3
	N32_RAW_LOCAL_QWORD_PAIR %ymm1,%ymm4
	N32_RAW_LOCAL_QWORD_PAIR %ymm2,%ymm5
	N32_MONT_LOCAL_HALF_PAIR %ymm0,%ymm3
	N32_MONT_LOCAL_HALF_REFLECTED %ymm1,%ymm2
	N32_MONT_LOCAL_HALF_REFLECTED %ymm4,%ymm5
	vmovdqu %ymm0,  0(%r8)
	vmovdqu %ymm3, 32(%r8)
	vmovdqu %ymm1,  0(%r9)
	vmovdqu %ymm4, 32(%r9)
	vmovdqu %ymm2,  0(%r10)
	vmovdqu %ymm5, 32(%r10)
	addq $192, %rsi
	addq $64, %r8
	addq $64, %r9
	addq $64, %r10
	.endm

	.macro N32_IDFT_L2_L4_ALL
	vmovdqa .Ln32_inv_q(%rip), %ymm15
	vmovdqa .Ln32_inv_center10(%rip), %ymm14
	vmovdqa .Ln32_inv_w_qinv(%rip), %ymm12
	vmovdqa .Ln32_inv_w_factor(%rip), %ymm11
	movq %rdi, %r8
	leaq 256(%rdi), %r9
	leaq 512(%rdi), %r10
	movl $4, %ecx
.Ln32_idft_branch0_loop\@:
	N32_IDFT_L2_L4_PAIR
	decl %ecx
	jne .Ln32_idft_branch0_loop\@
	leaq 768(%rdi), %r8
	leaq 1024(%rdi), %r9
	leaq 1280(%rdi), %r10
	movl $4, %ecx
.Ln32_idft_branch1_loop\@:
	N32_IDFT_L2_L4_PAIR
	decl %ecx
	jne .Ln32_idft_branch1_loop\@
	.endm

	.macro N32_LOAD_TILE
	vmovdqu   0(%rsi), %ymm0
	vmovdqu  32(%rsi), %ymm1
	vmovdqu  64(%rsi), %ymm2
	vmovdqu  96(%rsi), %ymm3
	vmovdqu 128(%rsi), %ymm4
	vmovdqu 160(%rsi), %ymm5
	vmovdqu 192(%rsi), %ymm6
	vmovdqu 224(%rsi), %ymm7
	.endm

	.macro N32_STORE_TILE
	vmovdqu %ymm0,   0(%rdi)
	vmovdqu %ymm1,  32(%rdi)
	vmovdqu %ymm2,  64(%rdi)
	vmovdqu %ymm3,  96(%rdi)
	vmovdqu %ymm4, 128(%rdi)
	vmovdqu %ymm5, 160(%rdi)
	vmovdqu %ymm6, 192(%rdi)
	vmovdqu %ymm7, 224(%rdi)
	.endm

	.macro N32_INV_L8_L32_ALL
	vmovdqa .Ln32_inv_q(%rip), %ymm15
	movl $6, %ecx
.Ln32_inv_suffix_loop\@:
	N32_LOAD_TILE
	N32_MONT_CROSS4 %ymm0,%ymm1,%ymm2,%ymm3,%ymm4,%ymm5,%ymm6,%ymm7, .Ln32_inv_l8_qinv, .Ln32_inv_l8_factor
	N32_MONT_CROSS4 %ymm0,%ymm2,%ymm1,%ymm3,%ymm4,%ymm6,%ymm5,%ymm7, .Ln32_inv_l16_qinv, .Ln32_inv_l16_factor
	N32_MONT_CROSS4 %ymm0,%ymm4,%ymm1,%ymm5,%ymm2,%ymm6,%ymm3,%ymm7, .Ln32_inv_l32_qinv, .Ln32_inv_l32_factor
	N32_STORE_TILE
	addq $256, %rsi
	addq $256, %rdi
	decl %ecx
	jne .Ln32_inv_suffix_loop\@
	.endm

	.section .text.gt32_n32_idft_l2_l4_half_asm,"ax",@progbits
	.p2align 5
	.globl gt32_n32_idft_l2_l4_half_asm
	.type gt32_n32_idft_l2_l4_half_asm,@function
gt32_n32_idft_l2_l4_half_asm:
	N32_IDFT_L2_L4_ALL
	vzeroupper
	ret
	.size gt32_n32_idft_l2_l4_half_asm,.-gt32_n32_idft_l2_l4_half_asm

	.section .text.gt32_n32_inv_l8_l32_half_asm,"ax",@progbits
	.p2align 5
	.globl gt32_n32_inv_l8_l32_half_asm
	.type gt32_n32_inv_l8_l32_half_asm,@function
gt32_n32_inv_l8_l32_half_asm:
	N32_INV_L8_L32_ALL
	vzeroupper
	ret
	.size gt32_n32_inv_l8_l32_half_asm,.-gt32_n32_inv_l8_l32_half_asm

	.section .text.gt32_n32_inverse_half_r1u_asm,"ax",@progbits
	.p2align 5
	.globl gt32_n32_inverse_half_r1u_asm
	.type gt32_n32_inverse_half_r1u_asm,@function
gt32_n32_inverse_half_r1u_asm:
	movq %rdi, %rax
	N32_IDFT_L2_L4_ALL
	movq %rax, %rsi
	movq %rax, %rdi
	N32_INV_L8_L32_ALL
	vzeroupper
	ret
	.size gt32_n32_inverse_half_r1u_asm,.-gt32_n32_inverse_half_r1u_asm

	.section .rodata
#include "../generated/tile4_n32_inverse_constants.inc"

	.section .note.GNU-stack,"",@progbits
