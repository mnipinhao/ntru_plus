/* D2a private coefficient-plane inverse NTT32 core, e=-1 -> e=-1. */

	.text

	.macro I2_RAW_LOCAL2 v0,v1,low_mask,high_mask,blend
	vmovdqa \low_mask(%rip), %ymm12
	vmovdqa \high_mask(%rip), %ymm13
	vpshufb %ymm12, %\v0, %ymm4
	vpshufb %ymm12, %\v1, %ymm5
	vpshufb %ymm13, %\v0, %ymm6
	vpshufb %ymm13, %\v1, %ymm7
	vpaddw %ymm6, %ymm4, %ymm8
	vpaddw %ymm7, %ymm5, %ymm10
	vpsubw %ymm6, %ymm4, %ymm9
	vpsubw %ymm7, %ymm5, %ymm11
	vpblendw $\blend, %ymm9, %ymm8, %\v0
	vpblendw $\blend, %ymm11, %ymm10, %\v1
	.endm

	.macro I2_MONT_LOCAL2 v0,v1,low_mask,high_mask,qinv,factor,blend
	vmovdqa \low_mask(%rip), %ymm12
	vmovdqa \high_mask(%rip), %ymm13
	vpshufb %ymm12, %\v0, %ymm4
	vpshufb %ymm12, %\v1, %ymm5
	vpshufb %ymm13, %\v0, %ymm6
	vpshufb %ymm13, %\v1, %ymm7
	vmovdqa \qinv(%rip), %ymm12
	vmovdqa \factor(%rip), %ymm13
	vpmullw %ymm12, %ymm6, %ymm8
	vpmullw %ymm12, %ymm7, %ymm9
	vpmulhw %ymm13, %ymm6, %ymm6
	vpmulhw %ymm13, %ymm7, %ymm7
	vpmulhw %ymm15, %ymm8, %ymm8
	vpmulhw %ymm15, %ymm9, %ymm9
	vpsubw %ymm8, %ymm6, %ymm6
	vpsubw %ymm9, %ymm7, %ymm7
	vpaddw %ymm6, %ymm4, %ymm8
	vpaddw %ymm7, %ymm5, %ymm10
	vpsubw %ymm6, %ymm4, %ymm9
	vpsubw %ymm7, %ymm5, %ymm11
	vpblendw $\blend, %ymm9, %ymm8, %\v0
	vpblendw $\blend, %ymm11, %ymm10, %\v1
	.endm

	/* q bit1 is physical p bit3: one packed Montgomery half butterfly. */
	.macro I2_MONT_HALF_PAIR v0,v1
	vperm2i128 $0x20, %\v1, %\v0, %ymm4
	vperm2i128 $0x31, %\v1, %\v0, %ymm5
	vpmullw .Li2_s2_qinv(%rip), %ymm5, %ymm6
	vpmulhw .Li2_s2_factor(%rip), %ymm5, %ymm5
	vpmulhw %ymm15, %ymm6, %ymm6
	vpsubw %ymm6, %ymm5, %ymm5
	vpsubw %ymm5, %ymm4, %ymm9
	vpaddw %ymm5, %ymm4, %ymm8
	vperm2i128 $0x20, %ymm9, %ymm8, %\v0
	vperm2i128 $0x31, %ymm9, %ymm8, %\v1
	.endm

	.macro I2_MONT_CROSS v0,v1
	vpmullw .Li2_s5_qinv(%rip), %\v1, %ymm4
	vpmulhw .Li2_s5_factor(%rip), %\v1, %ymm5
	vpmulhw %ymm15, %ymm4, %ymm4
	vpsubw %ymm4, %ymm5, %ymm5
	vpsubw %ymm5, %\v0, %ymm4
	vpaddw %ymm5, %\v0, %\v0
	vmovdqa %ymm4, %\v1
	.endm

	.macro I2_RAW_QWORD_PAIR v0,v1
	vpunpcklqdq %\v1, %\v0, %ymm8
	vpunpckhqdq %\v1, %\v0, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vpunpcklqdq %ymm10, %ymm8, %\v0
	vpunpckhqdq %ymm10, %ymm8, %\v1
	.endm

	.macro I2_MONT_HALF_PAIR_PAR v0,v1
	vperm2i128 $0x20, %\v1, %\v0, %ymm8
	vperm2i128 $0x31, %\v1, %\v0, %ymm9
	vpmullw .Li2_s2_qinv(%rip), %ymm9, %ymm10
	vpmulhw .Li2_s2_factor(%rip), %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpsubw %ymm10, %ymm9, %ymm9
	vpsubw %ymm9, %ymm8, %ymm10
	vpaddw %ymm9, %ymm8, %ymm8
	vperm2i128 $0x20, %ymm10, %ymm8, %\v0
	vperm2i128 $0x31, %ymm10, %ymm8, %\v1
	.endm

	/* Masks stay in ymm12/13; fixed factors use L1 memory operands. */
	.macro I2_MONT_SHUFFLE_PAIR v0,v1,qinv,factor,blend
	vpshufb %ymm12, %\v0, %ymm8
	vpshufb %ymm12, %\v1, %ymm9
	vpshufb %ymm13, %\v0, %ymm10
	vpshufb %ymm13, %\v1, %ymm11
	vpmullw \qinv(%rip), %ymm10, %\v0
	vpmullw \qinv(%rip), %ymm11, %\v1
	vpmulhw \factor(%rip), %ymm10, %ymm10
	vpmulhw \factor(%rip), %ymm11, %ymm11
	vpmulhw %ymm15, %\v0, %\v0
	vpmulhw %ymm15, %\v1, %\v1
	vpsubw %\v0, %ymm10, %ymm10
	vpsubw %\v1, %ymm11, %ymm11
	vpaddw %ymm10, %ymm8, %\v0
	vpaddw %ymm11, %ymm9, %\v1
	vpsubw %ymm10, %ymm8, %ymm8
	vpsubw %ymm11, %ymm9, %ymm9
	vpblendw $\blend, %ymm8, %\v0, %\v0
	vpblendw $\blend, %ymm9, %\v1, %\v1
	.endm

	.macro I2_MONT_CROSS4
	vpmullw .Li2_s5_qinv(%rip), %ymm4, %ymm8
	vpmullw .Li2_s5_qinv(%rip), %ymm5, %ymm9
	vpmullw .Li2_s5_qinv(%rip), %ymm6, %ymm10
	vpmullw .Li2_s5_qinv(%rip), %ymm7, %ymm11
	vpmulhw .Li2_s5_factor(%rip), %ymm4, %ymm4
	vpmulhw .Li2_s5_factor(%rip), %ymm5, %ymm5
	vpmulhw .Li2_s5_factor(%rip), %ymm6, %ymm6
	vpmulhw .Li2_s5_factor(%rip), %ymm7, %ymm7
	vpmulhw %ymm15, %ymm8, %ymm8
	vpmulhw %ymm15, %ymm9, %ymm9
	vpmulhw %ymm15, %ymm10, %ymm10
	vpmulhw %ymm15, %ymm11, %ymm11
	vpsubw %ymm8, %ymm4, %ymm4
	vpsubw %ymm9, %ymm5, %ymm5
	vpsubw %ymm10, %ymm6, %ymm6
	vpsubw %ymm11, %ymm7, %ymm7
	vpsubw %ymm4, %ymm0, %ymm8
	vpsubw %ymm5, %ymm1, %ymm9
	vpsubw %ymm6, %ymm2, %ymm10
	vpsubw %ymm7, %ymm3, %ymm11
	vpaddw %ymm4, %ymm0, %ymm0
	vpaddw %ymm5, %ymm1, %ymm1
	vpaddw %ymm6, %ymm2, %ymm2
	vpaddw %ymm7, %ymm3, %ymm3
	vmovdqa %ymm8, %ymm4
	vmovdqa %ymm9, %ymm5
	vmovdqa %ymm10, %ymm6
	vmovdqa %ymm11, %ymm7
	.endm

/*
 * rows and input use the private B2-S layout:
 *   group=2*tile+Q/16, word=64*group+16*c+position[Q%16].
 */
	.p2align 5
	.globl gt32_tile4_inverse_soa_private_asm
	.type gt32_tile4_inverse_soa_private_asm,@function
gt32_tile4_inverse_soa_private_asm:
	vmovdqa .Li2_q(%rip), %ymm15
	movl $6, %r8d
	.p2align 5
.Li2_tile_loop:
	movl $4, %ecx
	.p2align 5
.Li2_coefficient_loop:
	vmovdqu   0(%rsi), %ymm0
	vmovdqu 128(%rsi), %ymm1

	/* q bit0=p2, q bit1=p3, q bit2=p0, q bit3=p1, q bit4=vector. */
	I2_RAW_LOCAL2 ymm0,ymm1,.Li2_s1_low,.Li2_s1_high,0xf0
	I2_MONT_HALF_PAIR ymm0,ymm1
	I2_MONT_LOCAL2 ymm0,ymm1,.Li2_s3_low,.Li2_s3_high, \
		.Li2_s3_qinv,.Li2_s3_factor,0xaa
	I2_MONT_LOCAL2 ymm0,ymm1,.Li2_s4_low,.Li2_s4_high, \
		.Li2_s4_qinv,.Li2_s4_factor,0xcc
	I2_MONT_CROSS ymm0,ymm1

	vmovdqu %ymm0,   0(%rdi)
	vmovdqu %ymm1, 128(%rdi)
	addq $32, %rsi
	addq $32, %rdi
	decl %ecx
	jne .Li2_coefficient_loop
	addq $128, %rsi
	addq $128, %rdi
	decl %r8d
	jne .Li2_tile_loop
	vzeroupper
	ret
	.size gt32_tile4_inverse_soa_private_asm,.-gt32_tile4_inverse_soa_private_asm

	.p2align 5
	.globl gt32_tile4_inverse_soa_private_parallel_asm
	.type gt32_tile4_inverse_soa_private_parallel_asm,@function
gt32_tile4_inverse_soa_private_parallel_asm:
	vmovdqa .Li2_q(%rip), %ymm15
	movl $6, %ecx
	.p2align 5
.Li2_parallel_tile_loop:
	vmovdqu   0(%rsi), %ymm0
	vmovdqu  32(%rsi), %ymm1
	vmovdqu  64(%rsi), %ymm2
	vmovdqu  96(%rsi), %ymm3
	vmovdqu 128(%rsi), %ymm4
	vmovdqu 160(%rsi), %ymm5
	vmovdqu 192(%rsi), %ymm6
	vmovdqu 224(%rsi), %ymm7

	I2_RAW_QWORD_PAIR ymm0,ymm1
	I2_RAW_QWORD_PAIR ymm2,ymm3
	I2_RAW_QWORD_PAIR ymm4,ymm5
	I2_RAW_QWORD_PAIR ymm6,ymm7
	I2_MONT_HALF_PAIR_PAR ymm0,ymm1
	I2_MONT_HALF_PAIR_PAR ymm2,ymm3
	I2_MONT_HALF_PAIR_PAR ymm4,ymm5
	I2_MONT_HALF_PAIR_PAR ymm6,ymm7

	vmovdqa .Li2_s3_low(%rip), %ymm12
	vmovdqa .Li2_s3_high(%rip), %ymm13
	I2_MONT_SHUFFLE_PAIR ymm0,ymm1,.Li2_s3_qinv,.Li2_s3_factor,0xaa
	I2_MONT_SHUFFLE_PAIR ymm2,ymm3,.Li2_s3_qinv,.Li2_s3_factor,0xaa
	I2_MONT_SHUFFLE_PAIR ymm4,ymm5,.Li2_s3_qinv,.Li2_s3_factor,0xaa
	I2_MONT_SHUFFLE_PAIR ymm6,ymm7,.Li2_s3_qinv,.Li2_s3_factor,0xaa

	vmovdqa .Li2_s4_low(%rip), %ymm12
	vmovdqa .Li2_s4_high(%rip), %ymm13
	I2_MONT_SHUFFLE_PAIR ymm0,ymm1,.Li2_s4_qinv,.Li2_s4_factor,0xcc
	I2_MONT_SHUFFLE_PAIR ymm2,ymm3,.Li2_s4_qinv,.Li2_s4_factor,0xcc
	I2_MONT_SHUFFLE_PAIR ymm4,ymm5,.Li2_s4_qinv,.Li2_s4_factor,0xcc
	I2_MONT_SHUFFLE_PAIR ymm6,ymm7,.Li2_s4_qinv,.Li2_s4_factor,0xcc
	I2_MONT_CROSS4

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
	jne .Li2_parallel_tile_loop
	vzeroupper
	ret
	.size gt32_tile4_inverse_soa_private_parallel_asm,.-gt32_tile4_inverse_soa_private_parallel_asm

	/*
	 * Bounded P2 entry.  I-112 is not a zero-route native inverse on AVX2:
	 * four half permutes per tile restore the exact M register frontier, after
	 * which the qualified I2 arithmetic body is unchanged.  Output is M.
	 */
	.p2align 5
	.globl gt32_tile4_inverse_i112_entry_asm
	.type gt32_tile4_inverse_i112_entry_asm,@function
gt32_tile4_inverse_i112_entry_asm:
	vmovdqa .Li2_q(%rip), %ymm15
	movl $6, %ecx
	.p2align 5
.Li112_entry_tile_loop:
	vmovdqu   0(%rsi), %ymm0
	vmovdqu  32(%rsi), %ymm1
	vmovdqu  64(%rsi), %ymm2
	vmovdqu  96(%rsi), %ymm3
	vmovdqu 128(%rsi), %ymm4
	vmovdqu 160(%rsi), %ymm6
	vmovdqu 192(%rsi), %ymm5
	vmovdqu 224(%rsi), %ymm7
	vperm2i128 $0x20, %ymm1, %ymm0, %ymm8
	vperm2i128 $0x31, %ymm1, %ymm0, %ymm9
	vperm2i128 $0x20, %ymm3, %ymm2, %ymm10
	vperm2i128 $0x31, %ymm3, %ymm2, %ymm11
	vmovdqa %ymm8, %ymm0
	vmovdqa %ymm9, %ymm1
	vmovdqa %ymm4, %ymm2
	vmovdqa %ymm5, %ymm3
	vmovdqa %ymm10, %ymm4
	vmovdqa %ymm11, %ymm5

	I2_RAW_QWORD_PAIR ymm0,ymm1
	I2_RAW_QWORD_PAIR ymm2,ymm3
	I2_RAW_QWORD_PAIR ymm4,ymm5
	I2_RAW_QWORD_PAIR ymm6,ymm7
	I2_MONT_HALF_PAIR_PAR ymm0,ymm1
	I2_MONT_HALF_PAIR_PAR ymm2,ymm3
	I2_MONT_HALF_PAIR_PAR ymm4,ymm5
	I2_MONT_HALF_PAIR_PAR ymm6,ymm7

	vmovdqa .Li2_s3_low(%rip), %ymm12
	vmovdqa .Li2_s3_high(%rip), %ymm13
	I2_MONT_SHUFFLE_PAIR ymm0,ymm1,.Li2_s3_qinv,.Li2_s3_factor,0xaa
	I2_MONT_SHUFFLE_PAIR ymm2,ymm3,.Li2_s3_qinv,.Li2_s3_factor,0xaa
	I2_MONT_SHUFFLE_PAIR ymm4,ymm5,.Li2_s3_qinv,.Li2_s3_factor,0xaa
	I2_MONT_SHUFFLE_PAIR ymm6,ymm7,.Li2_s3_qinv,.Li2_s3_factor,0xaa

	vmovdqa .Li2_s4_low(%rip), %ymm12
	vmovdqa .Li2_s4_high(%rip), %ymm13
	I2_MONT_SHUFFLE_PAIR ymm0,ymm1,.Li2_s4_qinv,.Li2_s4_factor,0xcc
	I2_MONT_SHUFFLE_PAIR ymm2,ymm3,.Li2_s4_qinv,.Li2_s4_factor,0xcc
	I2_MONT_SHUFFLE_PAIR ymm4,ymm5,.Li2_s4_qinv,.Li2_s4_factor,0xcc
	I2_MONT_SHUFFLE_PAIR ymm6,ymm7,.Li2_s4_qinv,.Li2_s4_factor,0xcc
	I2_MONT_CROSS4

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
	jne .Li112_entry_tile_loop
	vzeroupper
	ret
	.size gt32_tile4_inverse_i112_entry_asm,.-gt32_tile4_inverse_i112_entry_asm

	.section .rodata
	.p2align 5
.Li2_q:
	.rept 16
	.short 3457
	.endr

	/* Physical p bit2: words 0..3 versus 4..7 in each 128-bit half. */
.Li2_s1_low:
	.byte 0,1,2,3,4,5,6,7,0,1,2,3,4,5,6,7
	.byte 0,1,2,3,4,5,6,7,0,1,2,3,4,5,6,7
.Li2_s1_high:
	.byte 8,9,10,11,12,13,14,15,8,9,10,11,12,13,14,15
	.byte 8,9,10,11,12,13,14,15,8,9,10,11,12,13,14,15

	/* Physical p bit0: adjacent int16 lanes. */
.Li2_s3_low:
	.byte 0,1,0,1,4,5,4,5,8,9,8,9,12,13,12,13
	.byte 0,1,0,1,4,5,4,5,8,9,8,9,12,13,12,13
.Li2_s3_high:
	.byte 2,3,2,3,6,7,6,7,10,11,10,11,14,15,14,15
	.byte 2,3,2,3,6,7,6,7,10,11,10,11,14,15,14,15

	/* Physical p bit1: pairs of int16 lanes. */
.Li2_s4_low:
	.byte 0,1,2,3,0,1,2,3,8,9,10,11,8,9,10,11
	.byte 0,1,2,3,0,1,2,3,8,9,10,11,8,9,10,11
.Li2_s4_high:
	.byte 4,5,6,7,4,5,6,7,12,13,14,15,12,13,14,15
	.byte 4,5,6,7,4,5,6,7,12,13,14,15,12,13,14,15

#include "../generated/tile4_private_inverse_constants.inc"

	.section .note.GNU-stack,"",@progbits
