.text

/*
 * Four independent lane-local DIT butterflies.
 *
 * ymm0..ymm3  : four Q-group inputs and outputs
 * ymm4..ymm7  : duplicated low operands
 * ymm8..ymm11 : duplicated high operands, then Montgomery products/differences
 * ymm12..ymm13: shuffle masks, then qinv/factor tables
 * ymm14       : q
 * ymm15       : packed Barrett reciprocal
 */
.macro INTT_LOCAL_LEN2
	vmovdqa .Lintt_mask_len2_low(%rip), %ymm12
	vmovdqa .Lintt_mask_len2_high(%rip), %ymm13

	vpshufb %ymm12, %ymm0, %ymm4
	vpshufb %ymm12, %ymm1, %ymm5
	vpshufb %ymm12, %ymm2, %ymm6
	vpshufb %ymm12, %ymm3, %ymm7
	vpshufb %ymm13, %ymm0, %ymm8
	vpshufb %ymm13, %ymm1, %ymm9
	vpshufb %ymm13, %ymm2, %ymm10
	vpshufb %ymm13, %ymm3, %ymm11

	vpaddw %ymm8,  %ymm4, %ymm0
	vpaddw %ymm9,  %ymm5, %ymm1
	vpaddw %ymm10, %ymm6, %ymm2
	vpaddw %ymm11, %ymm7, %ymm3
	vpsubw %ymm8,  %ymm4, %ymm8
	vpsubw %ymm9,  %ymm5, %ymm9
	vpsubw %ymm10, %ymm6, %ymm10
	vpsubw %ymm11, %ymm7, %ymm11

	vpblendw $0xaa, %ymm8,  %ymm0, %ymm0
	vpblendw $0xaa, %ymm9,  %ymm1, %ymm1
	vpblendw $0xaa, %ymm10, %ymm2, %ymm2
	vpblendw $0xaa, %ymm11, %ymm3, %ymm3
.endm

.macro INTT_LOCAL_MONT low_mask, high_mask, table, blend
	vmovdqa \low_mask(%rip), %ymm12
	vmovdqa \high_mask(%rip), %ymm13

	vpshufb %ymm12, %ymm0, %ymm4
	vpshufb %ymm12, %ymm1, %ymm5
	vpshufb %ymm12, %ymm2, %ymm6
	vpshufb %ymm12, %ymm3, %ymm7
	vpshufb %ymm13, %ymm0, %ymm8
	vpshufb %ymm13, %ymm1, %ymm9
	vpshufb %ymm13, %ymm2, %ymm10
	vpshufb %ymm13, %ymm3, %ymm11

	/* Load one shared qinv/factor pair after the masks are dead. */
	vmovdqa \table+0(%rip), %ymm12
	vmovdqa \table+32(%rip), %ymm13
	vpmullw %ymm12, %ymm8,  %ymm0
	vpmullw %ymm12, %ymm9,  %ymm1
	vpmullw %ymm12, %ymm10, %ymm2
	vpmullw %ymm12, %ymm11, %ymm3
	vpmulhw %ymm13, %ymm8,  %ymm8
	vpmulhw %ymm13, %ymm9,  %ymm9
	vpmulhw %ymm13, %ymm10, %ymm10
	vpmulhw %ymm13, %ymm11, %ymm11
	vpmulhw %ymm14, %ymm0, %ymm0
	vpmulhw %ymm14, %ymm1, %ymm1
	vpmulhw %ymm14, %ymm2, %ymm2
	vpmulhw %ymm14, %ymm3, %ymm3
	vpsubw %ymm0, %ymm8,  %ymm8
	vpsubw %ymm1, %ymm9,  %ymm9
	vpsubw %ymm2, %ymm10, %ymm10
	vpsubw %ymm3, %ymm11, %ymm11

	vpaddw %ymm8,  %ymm4, %ymm0
	vpaddw %ymm9,  %ymm5, %ymm1
	vpaddw %ymm10, %ymm6, %ymm2
	vpaddw %ymm11, %ymm7, %ymm3
	vpsubw %ymm8,  %ymm4, %ymm8
	vpsubw %ymm9,  %ymm5, %ymm9
	vpsubw %ymm10, %ymm6, %ymm10
	vpsubw %ymm11, %ymm7, %ymm11

	vpblendw $\blend, %ymm8,  %ymm0, %ymm0
	vpblendw $\blend, %ymm9,  %ymm1, %ymm1
	vpblendw $\blend, %ymm10, %ymm2, %ymm2
	vpblendw $\blend, %ymm11, %ymm3, %ymm3
.endm

.macro INTT_LEN16
	vmovdqa .Lintt_twiddle_len16+0(%rip), %ymm12
	vmovdqa .Lintt_twiddle_len16+32(%rip), %ymm13
	vpmullw %ymm12, %ymm1, %ymm4
	vpmullw %ymm12, %ymm3, %ymm5
	vpmulhw %ymm13, %ymm1, %ymm1
	vpmulhw %ymm13, %ymm3, %ymm3
	vpmulhw %ymm14, %ymm4, %ymm4
	vpmulhw %ymm14, %ymm5, %ymm5
	vpsubw %ymm4, %ymm1, %ymm1
	vpsubw %ymm5, %ymm3, %ymm3

	vpsubw %ymm1, %ymm0, %ymm4
	vpsubw %ymm3, %ymm2, %ymm5
	vpaddw %ymm1, %ymm0, %ymm0
	vpaddw %ymm3, %ymm2, %ymm2
	vmovdqa %ymm4, %ymm1
	vmovdqa %ymm5, %ymm3
.endm

.macro INTT_LEN32
	vmovdqa .Lintt_twiddle_len32_low+0(%rip), %ymm12
	vmovdqa .Lintt_twiddle_len32_high+0(%rip), %ymm13
	vpmullw %ymm12, %ymm2, %ymm4
	vpmullw %ymm13, %ymm3, %ymm5
	vmovdqa .Lintt_twiddle_len32_low+32(%rip), %ymm12
	vmovdqa .Lintt_twiddle_len32_high+32(%rip), %ymm13
	vpmulhw %ymm12, %ymm2, %ymm2
	vpmulhw %ymm13, %ymm3, %ymm3
	vpmulhw %ymm14, %ymm4, %ymm4
	vpmulhw %ymm14, %ymm5, %ymm5
	vpsubw %ymm4, %ymm2, %ymm2
	vpsubw %ymm5, %ymm3, %ymm3

	vpsubw %ymm2, %ymm0, %ymm4
	vpsubw %ymm3, %ymm1, %ymm5
	vpaddw %ymm2, %ymm0, %ymm0
	vpaddw %ymm3, %ymm1, %ymm1
	vmovdqa %ymm4, %ymm2
	vmovdqa %ymm5, %ymm3
.endm

.macro INTT_BARRETT4
	vpmulhw %ymm15, %ymm0, %ymm4
	vpmulhw %ymm15, %ymm1, %ymm5
	vpmulhw %ymm15, %ymm2, %ymm6
	vpmulhw %ymm15, %ymm3, %ymm7
	vpsraw $10, %ymm4, %ymm4
	vpsraw $10, %ymm5, %ymm5
	vpsraw $10, %ymm6, %ymm6
	vpsraw $10, %ymm7, %ymm7
	vpmullw %ymm14, %ymm4, %ymm4
	vpmullw %ymm14, %ymm5, %ymm5
	vpmullw %ymm14, %ymm6, %ymm6
	vpmullw %ymm14, %ymm7, %ymm7
	vpsubw %ymm4, %ymm0, %ymm0
	vpsubw %ymm5, %ymm1, %ymm1
	vpsubw %ymm6, %ymm2, %ymm2
	vpsubw %ymm7, %ymm3, %ymm3
.endm

/*
 * void gt_invntt_soa_ntt32_asm(int16_t rows[768],
 *                               const int16_t soa[768])
 *
 * rows must be 32-byte aligned.  For fixed (k3,c), the four vectors are
 * Q=0..7, 8..15, 16..23, and 24..31 with one branch per 128-bit half.
 */
.p2align 5
.globl gt_invntt_soa_ntt32_asm
.type gt_invntt_soa_ntt32_asm,@function
gt_invntt_soa_ntt32_asm:
	vmovdqa .Lintt_q(%rip), %ymm14
	vmovdqa .Lintt_barrett_v(%rip), %ymm15
	movl $3, %r8d
.p2align 5
.Lintt_k3_loop:
	movl $4, %ecx
.p2align 5
.Lintt_coefficient_loop:
	vmovdqu   0(%rsi), %ymm0
	vmovdqu 128(%rsi), %ymm1
	vmovdqu 256(%rsi), %ymm2
	vmovdqu 384(%rsi), %ymm3

	INTT_LOCAL_LEN2
	INTT_LOCAL_MONT .Lintt_mask_len4_low, .Lintt_mask_len4_high, .Lintt_twiddle_len4, 0xcc
	INTT_LOCAL_MONT .Lintt_mask_len8_low, .Lintt_mask_len8_high, .Lintt_twiddle_len8, 0xf0
	INTT_LEN16
	INTT_LEN32
	INTT_BARRETT4

	vmovdqa %ymm0,   0(%rdi)
	vmovdqa %ymm1, 128(%rdi)
	vmovdqa %ymm2, 256(%rdi)
	vmovdqa %ymm3, 384(%rdi)

	addq $32, %rsi
	addq $32, %rdi
	decl %ecx
	jne .Lintt_coefficient_loop

	/* Four coefficients advanced 128 bytes; next k3 starts 512 bytes away. */
	addq $384, %rsi
	addq $384, %rdi
	decl %r8d
	jne .Lintt_k3_loop

	vzeroupper
	ret
.size gt_invntt_soa_ntt32_asm,.-gt_invntt_soa_ntt32_asm

.section .rodata
.p2align 5
.Lintt_q:
	.rept 16
	.short 3457
	.endr
.Lintt_barrett_v:
	.rept 16
	.short 19412
	.endr

/* One 128-bit byte-shuffle mask duplicated into both YMM halves. */
.macro MASK2X bytes:vararg
	.byte \bytes
	.byte \bytes
.endm

.p2align 5
.Lintt_mask_len2_low:
	MASK2X 0,1,0,1,4,5,4,5,8,9,8,9,12,13,12,13
.Lintt_mask_len2_high:
	MASK2X 2,3,2,3,6,7,6,7,10,11,10,11,14,15,14,15
.Lintt_mask_len4_low:
	MASK2X 0,1,2,3,0,1,2,3,8,9,10,11,8,9,10,11
.Lintt_mask_len4_high:
	MASK2X 4,5,6,7,4,5,6,7,12,13,14,15,12,13,14,15
.Lintt_mask_len8_low:
	MASK2X 0,1,2,3,4,5,6,7,0,1,2,3,4,5,6,7
.Lintt_mask_len8_high:
	MASK2X 8,9,10,11,12,13,14,15,8,9,10,11,12,13,14,15

/* Each table is qinv[16], followed by factor[16]. */
.p2align 5
.Lintt_twiddle_len4:
	.short -19,-13422,-19,-13422,-19,-13422,-19,-13422
	.short -19,-13422,-19,-13422,-19,-13422,-19,-13422
	.short -147,-366,-147,-366,-147,-366,-147,-366
	.short -147,-366,-147,-366,-147,-366,-147,-366

.Lintt_twiddle_len8:
	.short -19,-28834,-13422,32531,-19,-28834,-13422,32531
	.short -19,-28834,-13422,32531,-19,-28834,-13422,32531
	.short -147,1118,-366,-109,-147,1118,-366,-109
	.short -147,1118,-366,-109,-147,1118,-366,-109

.Lintt_twiddle_len16:
	.short -19,739,-28834,10427,-13422,-834,32531,-23526
	.short -19,739,-28834,10427,-13422,-834,32531,-23526
	.short -147,-1181,1118,1339,-366,446,-109,794
	.short -147,-1181,1118,1339,-366,446,-109,794

.Lintt_twiddle_len32_low:
	.short -19,8265,739,5327,-28834,-11147,10427,-24019
	.short -19,8265,739,5327,-28834,-11147,10427,-24019
	.short -147,-1591,-1181,-177,1118,-11,1339,429
	.short -147,-1591,-1181,-177,1118,-11,1339,429

.Lintt_twiddle_len32_high:
	.short -13422,19242,-834,-29536,32531,-27754,-23526,-31716
	.short -13422,19242,-834,-29536,32531,-27754,-23526,-31716
	.short -366,554,446,-864,-109,-874,794,-484
	.short -366,554,446,-864,-109,-874,794,-484

.section .note.GNU-stack,"",@progbits
