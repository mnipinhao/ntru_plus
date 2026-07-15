.text

/*
 * Four independent radix-2 CT butterflies.
 *
 * Each twiddle table entry is 64 bytes:
 *   +0  : 16 packed (twiddle*qinv) int16 values
 *   +32 : 16 packed twiddle int16 values
 *
 * The high operands are destroyed after both product halves are issued.
 * ymm8..ymm11 are the four correction/output temporaries.
 */
.macro MONT_STAGE l0, h0, l1, h1, l2, h2, l3, h3, table_offset
	vpmullw \table_offset+0(%rdx),   \h0, %ymm8
	vpmullw \table_offset+64(%rdx),  \h1, %ymm9
	vpmullw \table_offset+128(%rdx), \h2, %ymm10
	vpmullw \table_offset+192(%rdx), \h3, %ymm11

	vpmulhw \table_offset+32(%rdx),  \h0, \h0
	vpmulhw \table_offset+96(%rdx),  \h1, \h1
	vpmulhw \table_offset+160(%rdx), \h2, \h2
	vpmulhw \table_offset+224(%rdx), \h3, \h3

	vpmulhw .Lgt_q(%rip), %ymm8,  %ymm8
	vpmulhw .Lgt_q(%rip), %ymm9,  %ymm9
	vpmulhw .Lgt_q(%rip), %ymm10, %ymm10
	vpmulhw .Lgt_q(%rip), %ymm11, %ymm11

	vpsubw %ymm8,  \h0, \h0
	vpsubw %ymm9,  \h1, \h1
	vpsubw %ymm10, \h2, \h2
	vpsubw %ymm11, \h3, \h3

	/* tmp = u-t; low = u+t; high = tmp. */
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

/* Packed int16 Barrett checkpoint.  For |a| <= 8(q-1), output is in [0,q]. */
.macro BARRETT_ONE value
	vpmulhw .Lgt_v(%rip), \value, %ymm8
	vpsraw $10, %ymm8, %ymm8
	vpmullw .Lgt_q(%rip), %ymm8, %ymm8
	vpsubw %ymm8, \value, \value
.endm

.macro BARRETT_EIGHT
	BARRETT_ONE %ymm0
	BARRETT_ONE %ymm1
	BARRETT_ONE %ymm2
	BARRETT_ONE %ymm3
	BARRETT_ONE %ymm4
	BARRETT_ONE %ymm5
	BARRETT_ONE %ymm6
	BARRETT_ONE %ymm7
.endm

/*
 * Lane-local 8x8 int16 transpose.
 *
 * Input:  ymm0..ymm7 are Q rows.
 * Output: ymm8..ymm15 are stream columns.  The two 128-bit halves are
 * transposed independently, which handles row01 and packed-row2 together.
 */
.macro TRANSPOSE8X8
	vpunpcklwd %ymm1, %ymm0, %ymm8
	vpunpckhwd %ymm1, %ymm0, %ymm9
	vpunpcklwd %ymm3, %ymm2, %ymm10
	vpunpckhwd %ymm3, %ymm2, %ymm11
	vpunpcklwd %ymm5, %ymm4, %ymm12
	vpunpckhwd %ymm5, %ymm4, %ymm13
	vpunpcklwd %ymm7, %ymm6, %ymm14
	vpunpckhwd %ymm7, %ymm6, %ymm15

	vpunpckldq %ymm10, %ymm8,  %ymm0
	vpunpckhdq %ymm10, %ymm8,  %ymm1
	vpunpckldq %ymm11, %ymm9,  %ymm2
	vpunpckhdq %ymm11, %ymm9,  %ymm3
	vpunpckldq %ymm14, %ymm12, %ymm4
	vpunpckhdq %ymm14, %ymm12, %ymm5
	vpunpckldq %ymm15, %ymm13, %ymm6
	vpunpckhdq %ymm15, %ymm13, %ymm7

	vpunpcklqdq %ymm4, %ymm0, %ymm8
	vpunpckhqdq %ymm4, %ymm0, %ymm9
	vpunpcklqdq %ymm5, %ymm1, %ymm10
	vpunpckhqdq %ymm5, %ymm1, %ymm11
	vpunpcklqdq %ymm6, %ymm2, %ymm12
	vpunpckhqdq %ymm6, %ymm2, %ymm13
	vpunpcklqdq %ymm7, %ymm3, %ymm14
	vpunpckhqdq %ymm7, %ymm3, %ymm15
.endm

/*
 * Convert stream columns into one 16-block SoA batch per 128-bit half.
 * dest_low and dest_high point at the two output batches represented by the
 * low and high transpose halves.
 */
.macro STORE_SOA dest_low, dest_high
	vperm2i128 $0x20, %ymm12, %ymm8,  %ymm0
	vperm2i128 $0x31, %ymm12, %ymm8,  %ymm1
	vmovdqu %ymm0, 0(\dest_low)
	vmovdqu %ymm1, 0(\dest_high)

	vperm2i128 $0x20, %ymm13, %ymm9,  %ymm0
	vperm2i128 $0x31, %ymm13, %ymm9,  %ymm1
	vmovdqu %ymm0, 32(\dest_low)
	vmovdqu %ymm1, 32(\dest_high)

	vperm2i128 $0x20, %ymm14, %ymm10, %ymm0
	vperm2i128 $0x31, %ymm14, %ymm10, %ymm1
	vmovdqu %ymm0, 64(\dest_low)
	vmovdqu %ymm1, 64(\dest_high)

	vperm2i128 $0x20, %ymm15, %ymm11, %ymm0
	vperm2i128 $0x31, %ymm15, %ymm11, %ymm1
	vmovdqu %ymm0, 96(\dest_low)
	vmovdqu %ymm1, 96(\dest_high)
.endm

/*
 * void gt_ntt_avx2_stage345_soa_asm(int16_t out[768],
 *                                   const gt_stage2_scratch *scratch)
 *
 * out batch mapping:
 *   batch = 4*k3 + Q/8
 *   lane  = 8*branch + Q%8
 *   word  = 64*batch + 16*c + lane
 */
.p2align 5
.globl gt_ntt_avx2_stage345_soa_asm
.type gt_ntt_avx2_stage345_soa_asm,@function
gt_ntt_avx2_stage345_soa_asm:
	/* row01: four Q blocks.  Low half is row0, high half is row1. */
	leaq .Lrow01_twiddles(%rip), %rdx
	movq %rdi, %rcx
	leaq 512(%rdi), %r8
	movl $4, %r9d
.p2align 5
.Lrow01_loop:
	vmovdqa   0(%rsi), %ymm0
	vmovdqa  32(%rsi), %ymm1
	vmovdqa  64(%rsi), %ymm2
	vmovdqa  96(%rsi), %ymm3
	vmovdqa 128(%rsi), %ymm4
	vmovdqa 160(%rsi), %ymm5
	vmovdqa 192(%rsi), %ymm6
	vmovdqa 224(%rsi), %ymm7

	MONT_STAGE %ymm0, %ymm4, %ymm1, %ymm5, %ymm2, %ymm6, %ymm3, %ymm7, 0
	MONT_STAGE %ymm0, %ymm2, %ymm1, %ymm3, %ymm4, %ymm6, %ymm5, %ymm7, 256
	MONT_STAGE %ymm0, %ymm1, %ymm2, %ymm3, %ymm4, %ymm5, %ymm6, %ymm7, 512
	BARRETT_EIGHT
	TRANSPOSE8X8
	STORE_SOA %rcx, %r8

	addq $256, %rsi
	addq $768, %rdx
	addq $128, %rcx
	addq $128, %r8
	decl %r9d
	jne .Lrow01_loop

	/* row2: two packed blocks.  High half is the corresponding Q+16 group. */
	leaq .Lrow2_twiddles(%rip), %rdx
	leaq 1024(%rdi), %rcx
	leaq 1280(%rdi), %r8
	movl $2, %r9d
.p2align 5
.Lrow2_loop:
	vmovdqa   0(%rsi), %ymm0
	vmovdqa  32(%rsi), %ymm1
	vmovdqa  64(%rsi), %ymm2
	vmovdqa  96(%rsi), %ymm3
	vmovdqa 128(%rsi), %ymm4
	vmovdqa 160(%rsi), %ymm5
	vmovdqa 192(%rsi), %ymm6
	vmovdqa 224(%rsi), %ymm7

	MONT_STAGE %ymm0, %ymm4, %ymm1, %ymm5, %ymm2, %ymm6, %ymm3, %ymm7, 0
	MONT_STAGE %ymm0, %ymm2, %ymm1, %ymm3, %ymm4, %ymm6, %ymm5, %ymm7, 256
	MONT_STAGE %ymm0, %ymm1, %ymm2, %ymm3, %ymm4, %ymm5, %ymm6, %ymm7, 512
	BARRETT_EIGHT
	TRANSPOSE8X8
	STORE_SOA %rcx, %r8

	addq $256, %rsi
	addq $768, %rdx
	addq $128, %rcx
	addq $128, %r8
	decl %r9d
	jne .Lrow2_loop

	vzeroupper
	ret
.size gt_ntt_avx2_stage345_soa_asm,.-gt_ntt_avx2_stage345_soa_asm

/* Test-only entry point for exhaustively checking the packed reducer macro. */
.p2align 5
.globl gt_ntt_avx2_barrett_packed_asm
.type gt_ntt_avx2_barrett_packed_asm,@function
gt_ntt_avx2_barrett_packed_asm:
	vmovdqu (%rsi), %ymm0
	BARRETT_ONE %ymm0
	vmovdqu %ymm0, (%rdi)
	vzeroupper
	ret
.size gt_ntt_avx2_barrett_packed_asm,.-gt_ntt_avx2_barrett_packed_asm

.section .rodata
.p2align 5
.Lgt_q:
	.rept 16
	.short 3457
	.endr
.Lgt_v:
	.rept 16
	.short 19412
	.endr

/* qinv vector followed by twiddle vector. */
.macro TW16 factor, factor_qinv
	.rept 16
	.short \factor_qinv
	.endr
	.rept 16
	.short \factor
	.endr
.endm

.macro TW8X2 factor_low, factor_high, qinv_low, qinv_high
	.rept 8
	.short \qinv_low
	.endr
	.rept 8
	.short \qinv_high
	.endr
	.rept 8
	.short \factor_low
	.endr
	.rept 8
	.short \factor_high
	.endr
.endm

.p2align 5
.Lrow01_twiddles:
	/* base 0: stages 3, 4, 5. */
	TW16 -147, -19
	TW16 -147, -19
	TW16 -147, -19
	TW16 -147, -19
	TW16 -147, -19
	TW16 -147, -19
	TW16 366, 13422
	TW16 366, 13422
	TW16 -147, -19
	TW16 366, 13422
	TW16 109, -32531
	TW16 -1118, 28834

	/* base 8. */
	TW16 366, 13422
	TW16 366, 13422
	TW16 366, 13422
	TW16 366, 13422
	TW16 109, -32531
	TW16 109, -32531
	TW16 -1118, 28834
	TW16 -1118, 28834
	TW16 -794, 23526
	TW16 -1339, -10427
	TW16 -446, 834
	TW16 1181, -739

	/* base 16. */
	TW16 109, -32531
	TW16 109, -32531
	TW16 109, -32531
	TW16 109, -32531
	TW16 -794, 23526
	TW16 -794, 23526
	TW16 -1339, -10427
	TW16 -1339, -10427
	TW16 484, 31716
	TW16 -429, 24019
	TW16 864, 29536
	TW16 177, -5327

	/* base 24. */
	TW16 -1118, 28834
	TW16 -1118, 28834
	TW16 -1118, 28834
	TW16 -1118, 28834
	TW16 -446, 834
	TW16 -446, 834
	TW16 1181, -739
	TW16 1181, -739
	TW16 874, 27754
	TW16 11, 11147
	TW16 -554, -19242
	TW16 1591, -8265

.p2align 5
.Lrow2_twiddles:
	/* packed base 0: low Q=0..7, high Q=16..23. */
	TW8X2 -147, 109, -19, -32531
	TW8X2 -147, 109, -19, -32531
	TW8X2 -147, 109, -19, -32531
	TW8X2 -147, 109, -19, -32531
	TW8X2 -147, -794, -19, 23526
	TW8X2 -147, -794, -19, 23526
	TW8X2 366, -1339, 13422, -10427
	TW8X2 366, -1339, 13422, -10427
	TW8X2 -147, 484, -19, 31716
	TW8X2 366, -429, 13422, 24019
	TW8X2 109, 864, -32531, 29536
	TW8X2 -1118, 177, 28834, -5327

	/* packed base 8: low Q=8..15, high Q=24..31. */
	TW8X2 366, -1118, 13422, 28834
	TW8X2 366, -1118, 13422, 28834
	TW8X2 366, -1118, 13422, 28834
	TW8X2 366, -1118, 13422, 28834
	TW8X2 109, -446, -32531, 834
	TW8X2 109, -446, -32531, 834
	TW8X2 -1118, 1181, 28834, -739
	TW8X2 -1118, 1181, 28834, -739
	TW8X2 -794, 874, 23526, 27754
	TW8X2 -1339, 11, -10427, 11147
	TW8X2 -446, -554, 834, -19242
	TW8X2 1181, 1591, -739, -8265

.section .note.GNU-stack,"",@progbits
