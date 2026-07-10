/*
 * Benchmark-only delta-divstep Fq inverse core with lazy int16 V/R tracking.
 *
 * ABI:
 *   v0.8h = input vector a
 *   v1.8h = unused constants vector, kept for ABI compatibility
 *   w0    = final_scale selector from the existing divstep helper
 *   returns v0.8h = divstep inverse output
 *
 * This is a probe for the "4-step block + lazy V/R" route.  It keeps f/g/delta2
 * in int16 like the s32fold path, but keeps V/R as int16 residues and performs
 * a real centered reduction only after each 4-round block.  It is not a
 * transition-matrix block divstep; it is the lower-risk range/correction probe
 * for that route.
 *
 * Exhaustive scalar range model for q=3457 and folded R0:
 *   correction period 4: max raw |V/R| = 27616
 *   centered reduction may require up to 8*q, so one +/-q correction is not
 *   enough.  The block reducer uses an int16 reciprocal quotient followed by
 *   one centered correction.
 *
 * Final scale is folded into initial R:
 *   final_scale == 32 -> scaled_r, R0 = 2375 = -1082 mod q
 *   otherwise         -> normal,   R0 = 1583 mod q
 */

.text
.align 2

#include "common.inc"

.macro cneg_vec_s16 dst, src, mask
	eor \dst\().16b, \src\().16b, \mask\().16b
	sub \dst\().8h, \dst\().8h, \mask\().8h
.endm

.macro center_reduce_s16 reg
	// qhat = round(x * 9 / 2^15), exact enough for |x| <= 27616.
	sqrdmulh v26.8h, \reg\().8h, v11.8h
	mls \reg\().8h, v26.8h, v6.8h

	cmgt v26.8h, \reg\().8h, v9.8h
	sub v27.8h, \reg\().8h, v6.8h
	bit \reg\().16b, v27.16b, v26.16b
	cmgt v26.8h, v10.8h, \reg\().8h
	add v27.8h, \reg\().8h, v6.8h
	bit \reg\().16b, v27.16b, v26.16b
.endm

.macro divstep_lazy16_round
	// s = [delta2 >= 0], t = -(g & 1), active = s & t.
	cmge v20.8h, v4.8h, v5.8h
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
	and v22.16b, v20.16b, v21.16b

	// f' = active ? old_g : old_f; g' = (g + selected_f) >> 1.
	cneg_vec_s16 v23, v2, v20
	and v23.16b, v23.16b, v21.16b
	add v24.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v24.8h, #1

	// delta2' = (active ? -delta2 : delta2) + 2.
	cneg_vec_s16 v4, v4, v22
	add v4.8h, v4.8h, v7.8h

	// V' = active ? 2*R : 2*V; R' = R + (t ? (s ? -V : V) : 0).
	cneg_vec_s16 v23, v16, v20
	and v23.16b, v23.16b, v21.16b
	shl v24.8h, v16.8h, #1
	shl v25.8h, v18.8h, #1
	add v18.8h, v18.8h, v23.8h
	bit v24.16b, v25.16b, v22.16b
	mov v16.16b, v24.16b
.endm

.macro divstep_lazy16_final_round
	// Final round only needs final f sign and final V.
	cmge v20.8h, v4.8h, v5.8h
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
	and v22.16b, v20.16b, v21.16b
	bit v2.16b, v3.16b, v22.16b
	shl v24.8h, v16.8h, #1
	shl v25.8h, v18.8h, #1
	bit v24.16b, v25.16b, v22.16b
	mov v16.16b, v24.16b
.endm

.macro divstep_lazy16_block4
	divstep_lazy16_round
	divstep_lazy16_round
	divstep_lazy16_round
	divstep_lazy16_round
	center_reduce_s16 v16
	center_reduce_s16 v18
.endm

.global C_SYM(gt_fqinv_delta_divstep_lazy16_asm)
C_SYM(gt_fqinv_delta_divstep_lazy16_asm):
	// v0 = normalize_modq_s16(a); keep zero mask for failure behavior.
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

	// f = q, g = amod, delta2 = 1, V = 0.
	mov v2.16b, v6.16b
	mov v3.16b, v0.16b
	mov w9, #1
	dup v4.8h, w9
	dup v8.8h, w9
	movi v16.8h, #0
	mov w9, #2
	dup v7.8h, w9

	// Centered reducer constants.
	mov w9, #1728
	dup v9.8h, w9
	mov w9, #-1728
	dup v10.8h, w9
	mov w9, #9
	dup v11.8h, w9

	// Fold final scale into R0. final_scale==32 is the scaled_r path.
	cmp w0, #32
	mov w9, #-1082
	mov w10, #1583
	csel w9, w9, w10, eq
	dup v18.8h, w9

	// 24 rounds as six 4-round lazy blocks.
	divstep_lazy16_block4
	divstep_lazy16_block4
	divstep_lazy16_block4
	divstep_lazy16_block4
	divstep_lazy16_block4
	divstep_lazy16_block4

	// Rounds 24 and 25, then the final round 26.
	divstep_lazy16_round
	divstep_lazy16_round
	divstep_lazy16_final_round

	// if (f < 0) V = -V.
	cmgt v20.8h, v5.8h, v2.8h
	cneg_vec_s16 v16, v16, v20
	center_reduce_s16 v16

	// Preserve existing zero behavior: input zero maps to zero.
	bic v0.16b, v16.16b, v31.16b
	ret
