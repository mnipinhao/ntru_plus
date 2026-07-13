/*
 * Benchmark-only scalar-GPR SWAR delta-divstep Fq inverse core.
 *
 * ABI:
 *   v0.8h = input vector a
 *   v1.8h = unused constants vector, kept for ABI compatibility
 *   w0    = final_scale selector
 *   returns v0.8h = divstep inverse output
 *
 * This packs two signed 31-bit lanes into one 64-bit GPR:
 *   bits  0..30: lane 0 data, bit 31 guard
 *   bits 32..62: lane 1 data, bit 63 guard
 *
 * The final representation scale is folded into initial Rcoef:
 *   final_scale == 16  -> scaled_r, R0 = -541
 *   otherwise          -> normal,   R0 = -937
 */

.text
.align 2

#include "../support/common.inc"

.macro swar_neg dst, src
	eor \dst, \src, x25
	add \dst, \dst, x26
	and \dst, \dst, x25
.endm

.macro swar_add dst, lhs, rhs
	add \dst, \lhs, \rhs
	and \dst, \dst, x25
.endm

.macro swar_select dst, iftrue, mask, tmp
	eor \tmp, \dst, \iftrue
	and \tmp, \tmp, \mask
	eor \dst, \dst, \tmp
.endm

.macro swar_round_pair F, G, D, V, R, S, T, A, TMP0, TMP1
	// S = [D >= 0], T = [G odd], A = S & T.
	lsr \S, \D, #30
	mvn \S, \S
	and \S, \S, x26
	mul \S, \S, x29
	and \T, \G, x26
	mul \T, \T, x29
	and \A, \S, \T

	// g' = (g + (t ? (s ? -f : f) : 0)) >> 1.
	swar_neg \TMP0, \F
	eor \TMP1, \F, \TMP0
	and \TMP1, \TMP1, \S
	eor \TMP0, \F, \TMP1
	and \TMP0, \TMP0, \T
	swar_add \TMP0, \G, \TMP0

	// f' = active ? old_g : old_f.
	swar_select \F, \G, \A, \TMP1

	// Per-lane arithmetic shift by one.
	and \TMP1, \TMP0, x27
	lsr \G, \TMP0, #1
	orr \G, \G, \TMP1
	and \G, \G, x25

	// delta2' = (active ? -delta2 : delta2) + 2.
	swar_neg \TMP0, \D
	swar_select \D, \TMP0, \A, \TMP1
	swar_add \D, \D, x28

	// R' = R + (T & V) - (A & (2*V)); V' = A ? 2*R : 2*V.
	mov \S, \R
	swar_add \TMP0, \V, \V
	swar_add \TMP1, \R, \R
	and \R, \V, \T
	and \V, \TMP0, \A
	swar_neg \V, \V
	swar_add \R, \S, \R
	swar_add \R, \R, \V
	mov \V, \TMP0
	swar_select \V, \TMP1, \A, \S
.endm

.macro swar_final_sign F, V, S, TMP
	lsr \S, \F, #30
	and \S, \S, x26
	mul \S, \S, x29
	swar_neg \TMP, \V
	swar_select \V, \TMP, \S, \TMP
.endm

.macro swar_store_pair packed, off, tmpx, tmpw
	lsl \tmpx, \packed, #33
	asr \tmpx, \tmpx, #33
	str \tmpw, [sp, #\off]
	lsl \tmpx, \packed, #1
	asr \tmpx, \tmpx, #33
	str \tmpw, [sp, #(\off + 4)]
.endm

.global C_SYM(gt_fqinv_delta_divstep_swar_asm)
C_SYM(gt_fqinv_delta_divstep_swar_asm):
	sub sp, sp, #128
	stp x19, x20, [sp, #0]
	stp x21, x22, [sp, #16]
	stp x23, x24, [sp, #32]
	stp x25, x26, [sp, #48]
	stp x27, x28, [sp, #64]
	str x29, [sp, #80]

	// Build SWAR constants.
	movz x29, #0xffff
	movk x29, #0x7fff, lsl #16
	orr x25, x29, x29, lsl #32
	mov x26, #1
	orr x26, x26, x26, lsl #32
	mov x27, #0x40000000
	orr x27, x27, x27, lsl #32
	mov x28, #2
	orr x28, x28, x28, lsl #32

	// v0 = normalize_modq_s16(a); v31 = zero-lane mask.
	movi v5.8h, #0
	mov w9, #3457
	dup v6.8h, w9
	cmgt v20.8h, v5.8h, v0.8h
	add v21.8h, v0.8h, v6.8h
	bit v0.16b, v21.16b, v20.16b
	cmge v20.8h, v0.8h, v6.8h
	sub v21.8h, v0.8h, v6.8h
	bit v0.16b, v21.16b, v20.16b
	cmeq v31.8h, v0.8h, v5.8h

	// Pack input lanes: G0=(a0,a1), G1=(a2,a3), G2=(a4,a5), G3=(a6,a7).
	umov w6, v0.h[0]
	umov w23, v0.h[1]
	orr x6, x6, x23, lsl #32
	umov w7, v0.h[2]
	umov w23, v0.h[3]
	orr x7, x7, x23, lsl #32
	umov w8, v0.h[4]
	umov w23, v0.h[5]
	orr x8, x8, x23, lsl #32
	umov w9, v0.h[6]
	umov w23, v0.h[7]
	orr x9, x9, x23, lsl #32

	// F = q, delta2 = 1, V = 0.
	mov w24, #3457
	orr x24, x24, x24, lsl #32
	mov x2, x24
	mov x3, x24
	mov x4, x24
	mov x5, x24
	mov x10, x26
	mov x11, x26
	mov x12, x26
	mov x13, x26
	mov x14, #0
	mov x15, #0
	mov x16, #0
	mov x17, #0

	// Fold final scale into R0. final_scale==16 is the scaled_r path.
	cmp w0, #16
	mov w23, #-541
	mov w24, #-937
	csel w23, w23, w24, eq
	sxtw x23, w23
	and x23, x23, x29
	orr x23, x23, x23, lsl #32
	mov x19, x23
	mov x20, x23
	mov x21, x23
	mov x22, x23

	.rept 28
	swar_round_pair x2, x6, x10, x14, x19, x0, x1, x18, x23, x24
	swar_round_pair x3, x7, x11, x15, x20, x0, x1, x18, x23, x24
	swar_round_pair x4, x8, x12, x16, x21, x0, x1, x18, x23, x24
	swar_round_pair x5, x9, x13, x17, x22, x0, x1, x18, x23, x24
	.endr

	swar_final_sign x2, x14, x0, x23
	swar_final_sign x3, x15, x0, x23
	swar_final_sign x4, x16, x0, x23
	swar_final_sign x5, x17, x0, x23

	swar_store_pair x14, 96, x23, w23
	swar_store_pair x15, 104, x23, w23
	swar_store_pair x16, 112, x23, w23
	swar_store_pair x17, 120, x23, w23
	ldr q16, [sp, #96]
	ldr q17, [sp, #112]

	// Reduce folded V modulo q.
	mov w9, #3457
	dup v6.4s, w9
	movz w9, #0x7a8f
	movk w9, #0x9, lsl #16
	dup v23.4s, w9
	sqrdmulh v24.4s, v16.4s, v23.4s
	mls v16.4s, v24.4s, v6.4s
	sqrdmulh v25.4s, v17.4s, v23.4s
	mls v17.4s, v25.4s, v6.4s

	// Center to [-1728, 1728] for exact representative compatibility.
	mov w9, #1728
	dup v24.4s, w9
	cmgt v25.4s, v16.4s, v24.4s
	sub v26.4s, v16.4s, v6.4s
	bit v16.16b, v26.16b, v25.16b
	cmgt v25.4s, v17.4s, v24.4s
	sub v26.4s, v17.4s, v6.4s
	bit v17.16b, v26.16b, v25.16b
	mov w9, #-1728
	dup v24.4s, w9
	cmgt v25.4s, v24.4s, v16.4s
	add v26.4s, v16.4s, v6.4s
	bit v16.16b, v26.16b, v25.16b
	cmgt v25.4s, v24.4s, v17.4s
	add v26.4s, v17.4s, v6.4s
	bit v17.16b, v26.16b, v25.16b

	xtn v16.4h, v16.4s
	xtn2 v16.8h, v17.4s
	bic v0.16b, v16.16b, v31.16b

	ldp x19, x20, [sp, #0]
	ldp x21, x22, [sp, #16]
	ldp x23, x24, [sp, #32]
	ldp x25, x26, [sp, #48]
	ldp x27, x28, [sp, #64]
	ldr x29, [sp, #80]
	add sp, sp, #128
	ret
