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

/*
 * The same four butterflies without copying each difference back to its old
 * high register.  The caller treats t0..t3 as the logical high outputs and the
 * destroyed h0..h3 registers as the next stage's temporary set.
 */
.macro MONT_STAGE_NOCOPY l0, h0, l1, h1, l2, h2, l3, h3, t0, t1, t2, t3, table_offset
	vpmullw \table_offset+0(%rdx),   \h0, \t0
	vpmullw \table_offset+64(%rdx),  \h1, \t1
	vpmullw \table_offset+128(%rdx), \h2, \t2
	vpmullw \table_offset+192(%rdx), \h3, \t3

	vpmulhw \table_offset+32(%rdx),  \h0, \h0
	vpmulhw \table_offset+96(%rdx),  \h1, \h1
	vpmulhw \table_offset+160(%rdx), \h2, \h2
	vpmulhw \table_offset+224(%rdx), \h3, \h3

	vpmulhw .Lgt_q(%rip), \t0, \t0
	vpmulhw .Lgt_q(%rip), \t1, \t1
	vpmulhw .Lgt_q(%rip), \t2, \t2
	vpmulhw .Lgt_q(%rip), \t3, \t3

	vpsubw \t0, \h0, \h0
	vpsubw \t1, \h1, \h1
	vpsubw \t2, \h2, \h2
	vpsubw \t3, \h3, \h3

	/* t = u-twiddled; low = u+twiddled; t remains the high output. */
	vpsubw \h0, \l0, \t0
	vpsubw \h1, \l1, \t1
	vpsubw \h2, \l2, \t2
	vpsubw \h3, \l3, \t3
	vpaddw \h0, \l0, \l0
	vpaddw \h1, \l1, \l1
	vpaddw \h2, \l2, \l2
	vpaddw \h3, \l3, \l3
.endm

/* MONT_STAGE_NOCOPY with q held in a register for the complete block. */
.macro MONT_STAGE_NOCOPY_QREG l0, h0, l1, h1, l2, h2, l3, h3, t0, t1, t2, t3, table_offset, qreg
	vpmullw \table_offset+0(%rdx),   \h0, \t0
	vpmullw \table_offset+64(%rdx),  \h1, \t1
	vpmullw \table_offset+128(%rdx), \h2, \t2
	vpmullw \table_offset+192(%rdx), \h3, \t3

	vpmulhw \table_offset+32(%rdx),  \h0, \h0
	vpmulhw \table_offset+96(%rdx),  \h1, \h1
	vpmulhw \table_offset+160(%rdx), \h2, \h2
	vpmulhw \table_offset+224(%rdx), \h3, \h3

	vpmulhw \qreg, \t0, \t0
	vpmulhw \qreg, \t1, \t1
	vpmulhw \qreg, \t2, \t2
	vpmulhw \qreg, \t3, \t3

	vpsubw \t0, \h0, \h0
	vpsubw \t1, \h1, \h1
	vpsubw \t2, \h2, \h2
	vpsubw \t3, \h3, \h3

	vpsubw \h0, \l0, \t0
	vpsubw \h1, \l1, \t1
	vpsubw \h2, \l2, \t2
	vpsubw \h3, \l3, \t3
	vpaddw \h0, \l0, \l0
	vpaddw \h1, \l1, \l1
	vpaddw \h2, \l2, \l2
	vpaddw \h3, \l3, \l3
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

.macro BARRETT_ONE_TEMP value, temp
	vpmulhw .Lgt_v(%rip), \value, \temp
	vpsraw $10, \temp, \temp
	vpmullw .Lgt_q(%rip), \temp, \temp
	vpsubw \temp, \value, \value
.endm

/*
 * Three-instruction signed representative checkpoint.
 *
 * vpmulhrsw computes round(a*10/2^15), so the subtraction remains congruent
 * to a modulo q.  Exhaustive scalar enumeration over the Stage345 contract
 * |a| <= 8(q-1) gives [-3080,3079].  This is intentionally a benchmark-only
 * signed representation candidate; unlike BARRETT_ONE it does not return the
 * canonical [0,q] representative.
 */
.macro CENTER_ONE_TEMP value, temp
	vpmulhrsw .Lgt_center_10(%rip), \value, \temp
	vpmullw .Lgt_q(%rip), \temp, \temp
	vpsubw \temp, \value, \value
.endm

/* Last two layers shared by the standalone and Barrett-fused transposes. */
.macro TRANSPOSE8X8_LAYERS23
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

	TRANSPOSE8X8_LAYERS23
.endm

/*
 * Expose eight independent Barrett chains, then overwrite each consumed
 * quotient-product pair with the corresponding first transpose layer.  The
 * arithmetic and final register layout are identical to BARRETT_EIGHT followed
 * by TRANSPOSE8X8.
 */
.macro BARRETT_TRANSPOSE8X8_INTERLEAVED
	vpmulhw .Lgt_v(%rip), %ymm0, %ymm8
	vpmulhw .Lgt_v(%rip), %ymm1, %ymm9
	vpmulhw .Lgt_v(%rip), %ymm2, %ymm10
	vpmulhw .Lgt_v(%rip), %ymm3, %ymm11
	vpmulhw .Lgt_v(%rip), %ymm4, %ymm12
	vpmulhw .Lgt_v(%rip), %ymm5, %ymm13
	vpmulhw .Lgt_v(%rip), %ymm6, %ymm14
	vpmulhw .Lgt_v(%rip), %ymm7, %ymm15

	vpsraw $10, %ymm8,  %ymm8
	vpsraw $10, %ymm9,  %ymm9
	vpsraw $10, %ymm10, %ymm10
	vpsraw $10, %ymm11, %ymm11
	vpsraw $10, %ymm12, %ymm12
	vpsraw $10, %ymm13, %ymm13
	vpsraw $10, %ymm14, %ymm14
	vpsraw $10, %ymm15, %ymm15

	vpmullw .Lgt_q(%rip), %ymm8,  %ymm8
	vpmullw .Lgt_q(%rip), %ymm9,  %ymm9
	vpmullw .Lgt_q(%rip), %ymm10, %ymm10
	vpmullw .Lgt_q(%rip), %ymm11, %ymm11
	vpmullw .Lgt_q(%rip), %ymm12, %ymm12
	vpmullw .Lgt_q(%rip), %ymm13, %ymm13
	vpmullw .Lgt_q(%rip), %ymm14, %ymm14
	vpmullw .Lgt_q(%rip), %ymm15, %ymm15

	vpsubw %ymm8, %ymm0, %ymm0
	vpsubw %ymm9, %ymm1, %ymm1
	vpunpcklwd %ymm1, %ymm0, %ymm8
	vpunpckhwd %ymm1, %ymm0, %ymm9

	vpsubw %ymm10, %ymm2, %ymm2
	vpsubw %ymm11, %ymm3, %ymm3
	vpunpcklwd %ymm3, %ymm2, %ymm10
	vpunpckhwd %ymm3, %ymm2, %ymm11

	vpsubw %ymm12, %ymm4, %ymm4
	vpsubw %ymm13, %ymm5, %ymm5
	vpunpcklwd %ymm5, %ymm4, %ymm12
	vpunpckhwd %ymm5, %ymm4, %ymm13

	vpsubw %ymm14, %ymm6, %ymm6
	vpsubw %ymm15, %ymm7, %ymm7
	vpunpcklwd %ymm7, %ymm6, %ymm14
	vpunpckhwd %ymm7, %ymm6, %ymm15

	TRANSPOSE8X8_LAYERS23
.endm

/*
 * Logical Q-row order after the three no-copy stages:
 *   [ymm0, ymm2, ymm4, ymm3, ymm8, ymm10, ymm6, ymm11].
 * ymm1 is free and preserves the serial one-temporary Barrett schedule.
 */
.macro BARRETT8_REMAPPED_SERIAL
	BARRETT_ONE_TEMP %ymm0,  %ymm1
	BARRETT_ONE_TEMP %ymm2,  %ymm1
	BARRETT_ONE_TEMP %ymm4,  %ymm1
	BARRETT_ONE_TEMP %ymm3,  %ymm1
	BARRETT_ONE_TEMP %ymm8,  %ymm1
	BARRETT_ONE_TEMP %ymm10, %ymm1
	BARRETT_ONE_TEMP %ymm6,  %ymm1
	BARRETT_ONE_TEMP %ymm11, %ymm1
.endm

/*
 * Same logical row order as BARRETT8_REMAPPED_SERIAL.  All registers not
 * holding logical rows become independent quotient temporaries, exposing the
 * vpmulhrsw -> vpmullw latency across all eight chains.
 */
.macro CENTER8_REMAPPED_PARALLEL
	vpmulhrsw .Lgt_center_10(%rip), %ymm0,  %ymm1
	vpmulhrsw .Lgt_center_10(%rip), %ymm2,  %ymm5
	vpmulhrsw .Lgt_center_10(%rip), %ymm4,  %ymm7
	vpmulhrsw .Lgt_center_10(%rip), %ymm3,  %ymm9
	vpmulhrsw .Lgt_center_10(%rip), %ymm8,  %ymm12
	vpmulhrsw .Lgt_center_10(%rip), %ymm10, %ymm13
	vpmulhrsw .Lgt_center_10(%rip), %ymm6,  %ymm14
	vpmulhrsw .Lgt_center_10(%rip), %ymm11, %ymm15

	vpmullw .Lgt_q(%rip), %ymm1,  %ymm1
	vpmullw .Lgt_q(%rip), %ymm5,  %ymm5
	vpmullw .Lgt_q(%rip), %ymm7,  %ymm7
	vpmullw .Lgt_q(%rip), %ymm9,  %ymm9
	vpmullw .Lgt_q(%rip), %ymm12, %ymm12
	vpmullw .Lgt_q(%rip), %ymm13, %ymm13
	vpmullw .Lgt_q(%rip), %ymm14, %ymm14
	vpmullw .Lgt_q(%rip), %ymm15, %ymm15

	vpsubw %ymm1,  %ymm0,  %ymm0
	vpsubw %ymm5,  %ymm2,  %ymm2
	vpsubw %ymm7,  %ymm4,  %ymm4
	vpsubw %ymm9,  %ymm3,  %ymm3
	vpsubw %ymm12, %ymm8,  %ymm8
	vpsubw %ymm13, %ymm10, %ymm10
	vpsubw %ymm14, %ymm6,  %ymm6
	vpsubw %ymm15, %ymm11, %ymm11
.endm

.macro BARRETT_ONE_QVREG value, temp, qreg, vreg
	vpmulhw \vreg, \value, \temp
	vpsraw $10, \temp, \temp
	vpmullw \qreg, \temp, \temp
	vpsubw \temp, \value, \value
.endm

/* ymm12 is free after stage 5; ymm14=q and ymm15=v remain live. */
.macro BARRETT8_REMAPPED_RESIDENT
	BARRETT_ONE_QVREG %ymm0,  %ymm12, %ymm14, %ymm15
	BARRETT_ONE_QVREG %ymm2,  %ymm12, %ymm14, %ymm15
	BARRETT_ONE_QVREG %ymm4,  %ymm12, %ymm14, %ymm15
	BARRETT_ONE_QVREG %ymm3,  %ymm12, %ymm14, %ymm15
	BARRETT_ONE_QVREG %ymm8,  %ymm12, %ymm14, %ymm15
	BARRETT_ONE_QVREG %ymm10, %ymm12, %ymm14, %ymm15
	BARRETT_ONE_QVREG %ymm6,  %ymm12, %ymm14, %ymm15
	BARRETT_ONE_QVREG %ymm11, %ymm12, %ymm14, %ymm15
.endm

/*
 * Transpose the remapped rows without first moving them to ymm0..ymm7.
 * Consume the rows currently occupying ymm8/ymm10/ymm11 before those
 * registers become the first two transpose pairs' destinations.
 */
.macro TRANSPOSE8X8_REMAPPED
	vpunpcklwd %ymm10, %ymm8, %ymm12
	vpunpckhwd %ymm10, %ymm8, %ymm13
	vpunpcklwd %ymm11, %ymm6, %ymm14
	vpunpckhwd %ymm11, %ymm6, %ymm15

	vpunpcklwd %ymm2, %ymm0, %ymm8
	vpunpckhwd %ymm2, %ymm0, %ymm9
	vpunpcklwd %ymm3, %ymm4, %ymm10
	vpunpckhwd %ymm3, %ymm4, %ymm11

	TRANSPOSE8X8_LAYERS23
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
 * Queue all cross-half permutations before issuing any store.  ymm0..ymm7 are
 * dead after the transpose and hold the eight independent store values.
 */
.macro STORE_SOA_QUEUED dest_low, dest_high
	vperm2i128 $0x20, %ymm12, %ymm8,  %ymm0
	vperm2i128 $0x31, %ymm12, %ymm8,  %ymm1
	vperm2i128 $0x20, %ymm13, %ymm9,  %ymm2
	vperm2i128 $0x31, %ymm13, %ymm9,  %ymm3
	vperm2i128 $0x20, %ymm14, %ymm10, %ymm4
	vperm2i128 $0x31, %ymm14, %ymm10, %ymm5
	vperm2i128 $0x20, %ymm15, %ymm11, %ymm6
	vperm2i128 $0x31, %ymm15, %ymm11, %ymm7

	vmovdqu %ymm0,  0(\dest_low)
	vmovdqu %ymm1,  0(\dest_high)
	vmovdqu %ymm2, 32(\dest_low)
	vmovdqu %ymm3, 32(\dest_high)
	vmovdqu %ymm4, 64(\dest_low)
	vmovdqu %ymm5, 64(\dest_high)
	vmovdqu %ymm6, 96(\dest_low)
	vmovdqu %ymm7, 96(\dest_high)
.endm

/*
 * Preserve the lane-local transpose result as the output layout.
 *
 * TRANSPOSE8X8_REMAPPED is still required: before it, each logical register
 * is one Q row whose lanes are streams; after it:
 *   ymm8..ymm11  = branch 0, c0..c3
 *   ymm12..ymm15 = branch 1, c0..c3
 *
 * Each YMM already contains the two desired eight-lane groups in its low and
 * high 128-bit halves, so this layout needs no cross-half vperm2i128.  dest
 * points at the first of two adjacent 128-byte batches.
 */
.macro STORE_NATIVE_BATCH_PAIR dest
	vmovdqu %ymm8,    0(\dest)
	vmovdqu %ymm9,   32(\dest)
	vmovdqu %ymm10,  64(\dest)
	vmovdqu %ymm11,  96(\dest)
	vmovdqu %ymm12, 128(\dest)
	vmovdqu %ymm13, 160(\dest)
	vmovdqu %ymm14, 192(\dest)
	vmovdqu %ymm15, 224(\dest)
.endm

/*
 * Generate the serial baseline and all scheduling candidates from the same
 * NTT32 and SoA-store body.  Mode 0 is the canonical serial path, mode 1 is
 * the eight-chain Barrett path, mode 2 carries remapped butterfly outputs
 * directly into a serial Barrett and transpose, and mode 3 additionally keeps
 * q and the Barrett reciprocal resident for the full block.  Mode 4 uses the
 * mode-2 arithmetic with all eight SoA permutations queued before the stores.
 * Modes 5 and 6 replace only the final canonical Barrett checkpoint with the
 * three-instruction signed checkpoint; mode 5 keeps the serial store schedule
 * and mode 6 queues the permutations.  The selector is resolved by the
 * assembler.
 *
 * void name(int16_t out[768], const gt_stage2_scratch *scratch)
 *
 * out batch mapping:
 *   batch = 4*k3 + Q/8
 *   lane  = 8*branch + Q%8
 *   word  = 64*batch + 16*c + lane
 */
.macro STAGE345_FUNCTION name, mode
.p2align 5
.globl \name
.type \name,@function
\name:
	/* row01: four Q blocks.  Low half is row0, high half is row1. */
	leaq .Lrow01_twiddles(%rip), %rdx
	movq %rdi, %rcx
	leaq 512(%rdi), %r8
	movl $4, %r9d
.p2align 5
.Lrow01_loop_\@:
	vmovdqa   0(%rsi), %ymm0
	vmovdqa  32(%rsi), %ymm1
	vmovdqa  64(%rsi), %ymm2
	vmovdqa  96(%rsi), %ymm3
	vmovdqa 128(%rsi), %ymm4
	vmovdqa 160(%rsi), %ymm5
	vmovdqa 192(%rsi), %ymm6
	vmovdqa 224(%rsi), %ymm7

	.if \mode >= 4
	MONT_STAGE_NOCOPY %ymm0, %ymm4, %ymm1, %ymm5, %ymm2, %ymm6, %ymm3, %ymm7, %ymm8, %ymm9, %ymm10, %ymm11, 0
	MONT_STAGE_NOCOPY %ymm0, %ymm2, %ymm1, %ymm3, %ymm8, %ymm10, %ymm9, %ymm11, %ymm4, %ymm5, %ymm6, %ymm7, 256
	MONT_STAGE_NOCOPY %ymm0, %ymm1, %ymm4, %ymm5, %ymm8, %ymm9, %ymm6, %ymm7, %ymm2, %ymm3, %ymm10, %ymm11, 512
	.if \mode >= 5
	CENTER8_REMAPPED_PARALLEL
	.else
	BARRETT8_REMAPPED_SERIAL
	.endif
	TRANSPOSE8X8_REMAPPED
	.else
	.if \mode == 2
	MONT_STAGE_NOCOPY %ymm0, %ymm4, %ymm1, %ymm5, %ymm2, %ymm6, %ymm3, %ymm7, %ymm8, %ymm9, %ymm10, %ymm11, 0
	MONT_STAGE_NOCOPY %ymm0, %ymm2, %ymm1, %ymm3, %ymm8, %ymm10, %ymm9, %ymm11, %ymm4, %ymm5, %ymm6, %ymm7, 256
	MONT_STAGE_NOCOPY %ymm0, %ymm1, %ymm4, %ymm5, %ymm8, %ymm9, %ymm6, %ymm7, %ymm2, %ymm3, %ymm10, %ymm11, 512
	BARRETT8_REMAPPED_SERIAL
	TRANSPOSE8X8_REMAPPED
	.else
	.if \mode == 3
	vmovdqa .Lgt_q(%rip), %ymm14
	vmovdqa .Lgt_v(%rip), %ymm15
	MONT_STAGE_NOCOPY_QREG %ymm0, %ymm4, %ymm1, %ymm5, %ymm2, %ymm6, %ymm3, %ymm7, %ymm8, %ymm9, %ymm10, %ymm11, 0, %ymm14
	MONT_STAGE_NOCOPY_QREG %ymm0, %ymm2, %ymm1, %ymm3, %ymm8, %ymm10, %ymm9, %ymm11, %ymm4, %ymm5, %ymm6, %ymm7, 256, %ymm14
	MONT_STAGE_NOCOPY_QREG %ymm0, %ymm1, %ymm4, %ymm5, %ymm8, %ymm9, %ymm6, %ymm7, %ymm2, %ymm3, %ymm10, %ymm11, 512, %ymm14
	BARRETT8_REMAPPED_RESIDENT
	TRANSPOSE8X8_REMAPPED
	.else
	MONT_STAGE %ymm0, %ymm4, %ymm1, %ymm5, %ymm2, %ymm6, %ymm3, %ymm7, 0
	MONT_STAGE %ymm0, %ymm2, %ymm1, %ymm3, %ymm4, %ymm6, %ymm5, %ymm7, 256
	MONT_STAGE %ymm0, %ymm1, %ymm2, %ymm3, %ymm4, %ymm5, %ymm6, %ymm7, 512
	.if \mode
	BARRETT_TRANSPOSE8X8_INTERLEAVED
	.else
	BARRETT_EIGHT
	TRANSPOSE8X8
	.endif
	.endif
	.endif
	.endif
	.if \mode == 4
	STORE_SOA_QUEUED %rcx, %r8
	.else
	.if \mode == 6
	STORE_SOA_QUEUED %rcx, %r8
	.else
	STORE_SOA %rcx, %r8
	.endif
	.endif

	addq $256, %rsi
	addq $768, %rdx
	addq $128, %rcx
	addq $128, %r8
	decl %r9d
	jne .Lrow01_loop_\@

	/* row2: two packed blocks.  High half is the corresponding Q+16 group. */
	leaq .Lrow2_twiddles(%rip), %rdx
	leaq 1024(%rdi), %rcx
	leaq 1280(%rdi), %r8
	movl $2, %r9d
.p2align 5
.Lrow2_loop_\@:
	vmovdqa   0(%rsi), %ymm0
	vmovdqa  32(%rsi), %ymm1
	vmovdqa  64(%rsi), %ymm2
	vmovdqa  96(%rsi), %ymm3
	vmovdqa 128(%rsi), %ymm4
	vmovdqa 160(%rsi), %ymm5
	vmovdqa 192(%rsi), %ymm6
	vmovdqa 224(%rsi), %ymm7

	.if \mode >= 4
	MONT_STAGE_NOCOPY %ymm0, %ymm4, %ymm1, %ymm5, %ymm2, %ymm6, %ymm3, %ymm7, %ymm8, %ymm9, %ymm10, %ymm11, 0
	MONT_STAGE_NOCOPY %ymm0, %ymm2, %ymm1, %ymm3, %ymm8, %ymm10, %ymm9, %ymm11, %ymm4, %ymm5, %ymm6, %ymm7, 256
	MONT_STAGE_NOCOPY %ymm0, %ymm1, %ymm4, %ymm5, %ymm8, %ymm9, %ymm6, %ymm7, %ymm2, %ymm3, %ymm10, %ymm11, 512
	.if \mode >= 5
	CENTER8_REMAPPED_PARALLEL
	.else
	BARRETT8_REMAPPED_SERIAL
	.endif
	TRANSPOSE8X8_REMAPPED
	.else
	.if \mode == 2
	MONT_STAGE_NOCOPY %ymm0, %ymm4, %ymm1, %ymm5, %ymm2, %ymm6, %ymm3, %ymm7, %ymm8, %ymm9, %ymm10, %ymm11, 0
	MONT_STAGE_NOCOPY %ymm0, %ymm2, %ymm1, %ymm3, %ymm8, %ymm10, %ymm9, %ymm11, %ymm4, %ymm5, %ymm6, %ymm7, 256
	MONT_STAGE_NOCOPY %ymm0, %ymm1, %ymm4, %ymm5, %ymm8, %ymm9, %ymm6, %ymm7, %ymm2, %ymm3, %ymm10, %ymm11, 512
	BARRETT8_REMAPPED_SERIAL
	TRANSPOSE8X8_REMAPPED
	.else
	.if \mode == 3
	vmovdqa .Lgt_q(%rip), %ymm14
	vmovdqa .Lgt_v(%rip), %ymm15
	MONT_STAGE_NOCOPY_QREG %ymm0, %ymm4, %ymm1, %ymm5, %ymm2, %ymm6, %ymm3, %ymm7, %ymm8, %ymm9, %ymm10, %ymm11, 0, %ymm14
	MONT_STAGE_NOCOPY_QREG %ymm0, %ymm2, %ymm1, %ymm3, %ymm8, %ymm10, %ymm9, %ymm11, %ymm4, %ymm5, %ymm6, %ymm7, 256, %ymm14
	MONT_STAGE_NOCOPY_QREG %ymm0, %ymm1, %ymm4, %ymm5, %ymm8, %ymm9, %ymm6, %ymm7, %ymm2, %ymm3, %ymm10, %ymm11, 512, %ymm14
	BARRETT8_REMAPPED_RESIDENT
	TRANSPOSE8X8_REMAPPED
	.else
	MONT_STAGE %ymm0, %ymm4, %ymm1, %ymm5, %ymm2, %ymm6, %ymm3, %ymm7, 0
	MONT_STAGE %ymm0, %ymm2, %ymm1, %ymm3, %ymm4, %ymm6, %ymm5, %ymm7, 256
	MONT_STAGE %ymm0, %ymm1, %ymm2, %ymm3, %ymm4, %ymm5, %ymm6, %ymm7, 512
	.if \mode
	BARRETT_TRANSPOSE8X8_INTERLEAVED
	.else
	BARRETT_EIGHT
	TRANSPOSE8X8
	.endif
	.endif
	.endif
	.endif
	.if \mode == 4
	STORE_SOA_QUEUED %rcx, %r8
	.else
	.if \mode == 6
	STORE_SOA_QUEUED %rcx, %r8
	.else
	STORE_SOA %rcx, %r8
	.endif
	.endif

	addq $256, %rsi
	addq $768, %rdx
	addq $128, %rcx
	addq $128, %r8
	decl %r9d
	jne .Lrow2_loop_\@

	vzeroupper
	ret
.size \name,.-\name
.endm

/*
 * Benchmark-only centered Stage345 with transpose-native output.
 *
 * This deliberately keeps the lane-local TRANSPOSE8X8_REMAPPED and removes
 * only the subsequent cross-128-bit STORE_SOA permutations.  The 12 batches
 * are four contiguous YMM vectors (c0,c1,c2,c3), with this mapping:
 *
 * row01, Q-group g=0..3, branch b=0..1:
 *   batch = 2*g + b
 *   lane  = Q%8 for row0, 8 + Q%8 for row1
 *
 * row2, Q-group g=0..1, branch b=0..1:
 *   batch = 8 + 2*g + b
 *   lane  = Q%8 for Q=8*g..8*g+7,
 *           8 + Q%8 for Q=8*g+16..8*g+23
 *
 * STORE_NATIVE_BATCH_PAIR writes two adjacent batches (256 bytes) per block.
 * Four row01 blocks plus two row2 blocks therefore cover all 1536 output
 * bytes exactly once.  rdi is used as a linear output cursor.
 *
 * void gt_ntt_avx2_stage345_native_centered_asm(
 *     int16_t out[768], const gt_stage2_scratch *scratch)
 */
.p2align 5
.globl gt_ntt_avx2_stage345_native_centered_asm
.type gt_ntt_avx2_stage345_native_centered_asm,@function
gt_ntt_avx2_stage345_native_centered_asm:
	/* row01: four Q groups, each producing branch batches 2*g and 2*g+1. */
	leaq .Lrow01_twiddles(%rip), %rdx
	movl $4, %r9d
.p2align 5
.Lnative_row01_loop:
	vmovdqa   0(%rsi), %ymm0
	vmovdqa  32(%rsi), %ymm1
	vmovdqa  64(%rsi), %ymm2
	vmovdqa  96(%rsi), %ymm3
	vmovdqa 128(%rsi), %ymm4
	vmovdqa 160(%rsi), %ymm5
	vmovdqa 192(%rsi), %ymm6
	vmovdqa 224(%rsi), %ymm7

	MONT_STAGE_NOCOPY %ymm0, %ymm4, %ymm1, %ymm5, %ymm2, %ymm6, %ymm3, %ymm7, %ymm8, %ymm9, %ymm10, %ymm11, 0
	MONT_STAGE_NOCOPY %ymm0, %ymm2, %ymm1, %ymm3, %ymm8, %ymm10, %ymm9, %ymm11, %ymm4, %ymm5, %ymm6, %ymm7, 256
	MONT_STAGE_NOCOPY %ymm0, %ymm1, %ymm4, %ymm5, %ymm8, %ymm9, %ymm6, %ymm7, %ymm2, %ymm3, %ymm10, %ymm11, 512
	CENTER8_REMAPPED_PARALLEL
	TRANSPOSE8X8_REMAPPED
	STORE_NATIVE_BATCH_PAIR %rdi

	addq $256, %rsi
	addq $768, %rdx
	addq $256, %rdi
	decl %r9d
	jne .Lnative_row01_loop

	/*
	 * row2 begins exactly where row01 left the output cursor: batch 8.
	 * Each low/high half is the Q/Q+16 pair for the same branch.
	 */
	leaq .Lrow2_twiddles(%rip), %rdx
	movl $2, %r9d
.p2align 5
.Lnative_row2_loop:
	vmovdqa   0(%rsi), %ymm0
	vmovdqa  32(%rsi), %ymm1
	vmovdqa  64(%rsi), %ymm2
	vmovdqa  96(%rsi), %ymm3
	vmovdqa 128(%rsi), %ymm4
	vmovdqa 160(%rsi), %ymm5
	vmovdqa 192(%rsi), %ymm6
	vmovdqa 224(%rsi), %ymm7

	MONT_STAGE_NOCOPY %ymm0, %ymm4, %ymm1, %ymm5, %ymm2, %ymm6, %ymm3, %ymm7, %ymm8, %ymm9, %ymm10, %ymm11, 0
	MONT_STAGE_NOCOPY %ymm0, %ymm2, %ymm1, %ymm3, %ymm8, %ymm10, %ymm9, %ymm11, %ymm4, %ymm5, %ymm6, %ymm7, 256
	MONT_STAGE_NOCOPY %ymm0, %ymm1, %ymm4, %ymm5, %ymm8, %ymm9, %ymm6, %ymm7, %ymm2, %ymm3, %ymm10, %ymm11, 512
	CENTER8_REMAPPED_PARALLEL
	TRANSPOSE8X8_REMAPPED
	STORE_NATIVE_BATCH_PAIR %rdi

	addq $256, %rsi
	addq $768, %rdx
	addq $256, %rdi
	decl %r9d
	jne .Lnative_row2_loop

	vzeroupper
	ret
.size gt_ntt_avx2_stage345_native_centered_asm,.-gt_ntt_avx2_stage345_native_centered_asm

STAGE345_FUNCTION gt_ntt_avx2_stage345_soa_asm, 0
STAGE345_FUNCTION gt_ntt_avx2_stage345_soa_interleaved_asm, 1
STAGE345_FUNCTION gt_ntt_avx2_stage345_soa_remapped_asm, 2
STAGE345_FUNCTION gt_ntt_avx2_stage345_soa_resident_asm, 3
STAGE345_FUNCTION gt_ntt_avx2_stage345_soa_queued_store_asm, 4
STAGE345_FUNCTION gt_ntt_avx2_stage345_soa_centered_asm, 5
STAGE345_FUNCTION gt_ntt_avx2_stage345_soa_centered_queued_store_asm, 6

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

/* Test-only entry point for the signed three-instruction reducer. */
.p2align 5
.globl gt_ntt_avx2_centered_packed_asm
.type gt_ntt_avx2_centered_packed_asm,@function
gt_ntt_avx2_centered_packed_asm:
	vmovdqu (%rsi), %ymm0
	CENTER_ONE_TEMP %ymm0, %ymm1
	vmovdqu %ymm0, (%rdi)
	vzeroupper
	ret
.size gt_ntt_avx2_centered_packed_asm,.-gt_ntt_avx2_centered_packed_asm

.section .rodata
.p2align 5
.globl gt_ntt_avx2_stage345_q_const
.hidden gt_ntt_avx2_stage345_q_const
gt_ntt_avx2_stage345_q_const:
.Lgt_q:
	.rept 16
	.short 3457
	.endr
.Lgt_v:
	.rept 16
	.short 19412
	.endr
.globl gt_ntt_avx2_stage345_center10_const
.hidden gt_ntt_avx2_stage345_center10_const
gt_ntt_avx2_stage345_center10_const:
.Lgt_center_10:
	.rept 16
	.short 10
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
.globl gt_ntt_avx2_stage345_row01_twiddles
.hidden gt_ntt_avx2_stage345_row01_twiddles
gt_ntt_avx2_stage345_row01_twiddles:
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

	.set .Lrow01_twiddle_bytes, . - .Lrow01_twiddles
	.if .Lrow01_twiddle_bytes != 3072
	.error "row01 Stage345 twiddle table must contain four 768-byte blocks"
	.endif
.p2align 5
.globl gt_ntt_avx2_stage345_row2_twiddles
.hidden gt_ntt_avx2_stage345_row2_twiddles
gt_ntt_avx2_stage345_row2_twiddles:
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
