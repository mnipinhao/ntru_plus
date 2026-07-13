/*
 * Benchmark-only delta-divstep Fq inverse core with V/R kept as centered
 * int16 modulo-q residues.
 *
 * ABI:
 *   v0.8h = input vector a
 *   v1.8h = unused constants vector, kept for ABI compatibility
 *   w0    = final_scale selector from the existing divstep helper
 *   returns v0.8h = divstep inverse output
 *
 * Range contract for the V/R state:
 *   V,R are corrected to [-1728,1728] after every divstep.
 *   Raw updates are either 2*V, 2*R, or R +/- V, so they are in
 *   [-3456,3456].  This fits signed int16 and one centered correction is
 *   enough to return to [-1728,1728].
 *
 * The final scale is folded into initial R:
 *   final_scale == 16  -> scaled_r, R0 = 2916 = -541 mod q
 *   otherwise          -> normal,   R0 = 2520 = -937 mod q
 */

.text
.align 2

#include "../support/common.inc"

.macro cneg_vec_s16 dst, src, mask
	eor \dst\().16b, \src\().16b, \mask\().16b
	sub \dst\().8h, \dst\().8h, \mask\().8h
.endm

.macro center_corr_s16 reg
	cmgt v26.8h, \reg\().8h, v9.8h
	sub v27.8h, \reg\().8h, v6.8h
	bit \reg\().16b, v27.16b, v26.16b
	cmgt v26.8h, v10.8h, \reg\().8h
	add v27.8h, \reg\().8h, v6.8h
	bit \reg\().16b, v27.16b, v26.16b
.endm

.macro divstep_modq16_round
	// s = [delta2 >= 0], t = -(g & 1), active = s & t.
	cmge v20.8h, v4.8h, v5.8h
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
	and v22.16b, v20.16b, v21.16b

	// f' = active ? old_g : old_f; g' = (g + selected_f) >> 1.
	cneg_vec_s16 v23, v2, v20
	and v23.16b, v23.16b, v21.16b
	bit v2.16b, v3.16b, v22.16b
	add v24.8h, v3.8h, v23.8h
	sshr v3.8h, v24.8h, #1

	// delta2' = (active ? -delta2 : delta2) + 2.
	cneg_vec_s16 v4, v4, v22
	add v4.8h, v4.8h, v7.8h

	// V' = active ? 2*R : 2*V; R' = R + t ? (s ? -V : V) : 0.
	cneg_vec_s16 v23, v16, v20
	and v23.16b, v23.16b, v21.16b
	shl v24.8h, v16.8h, #1
	shl v25.8h, v18.8h, #1
	add v18.8h, v18.8h, v23.8h
	bit v24.16b, v25.16b, v22.16b
	mov v16.16b, v24.16b

	center_corr_s16 v16
	center_corr_s16 v18
.endm

.global C_SYM(gt_fqinv_delta_divstep_modq16_asm)
C_SYM(gt_fqinv_delta_divstep_modq16_asm):
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
	movi v16.8h, #0
	mov w9, #2
	dup v7.8h, w9

	// Centered correction bounds.
	mov w9, #1728
	dup v9.8h, w9
	mov w9, #-1728
	dup v10.8h, w9

	// Fold final scale into R0. final_scale==16 is the scaled_r path.
	cmp w0, #16
	mov w9, #-541
	mov w10, #-937
	csel w9, w9, w10, eq
	dup v18.8h, w9

	.rept 28
	divstep_modq16_round
	.endr

	// if (f < 0) V = -V.
	cmgt v20.8h, v5.8h, v2.8h
	cneg_vec_s16 v16, v16, v20

	// Preserve existing zero behavior: input zero maps to zero.
	bic v0.16b, v16.16b, v31.16b
	ret
