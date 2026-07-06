/*
 * Benchmark-only delta-divstep scalar Fq inverse core.
 *
 * ABI:
 *   v0.8h = input vector a
 *   v1.8h = constants vector for fqmul
 *   w0    = final_scale
 *   returns v0.8h = divstep inverse output
 *
 * This mirrors fqinv_divstep_neon_intrinsics() in poly_gt_baseinv_batch.c:
 *   f = q, g = normalize(a), delta2 = 1, V = 0, R = 1
 *   28 fixed delta-divsteps
 *   final sign fix, int32 mod-q reduction, fqmul by final_scale
 */

.text
.align 2

#include "common.inc"

.macro fqmul dst, lhs, rhs
	smull v24.4s, \lhs\().4h, \rhs\().4h
	smull2 v25.4s, \lhs\().8h, \rhs\().8h
	uzp1 v26.8h, v24.8h, v25.8h
	mul v26.8h, v26.8h, v1.h[2]
	smlal v24.4s, v26.4h, v1.h[0]
	smlal2 v25.4s, v26.8h, v1.h[0]
	uzp2 \dst\().8h, v24.8h, v25.8h
.endm

.macro cneg_vec_s16 dst, src, mask
	eor \dst\().16b, \src\().16b, \mask\().16b
	sub \dst\().8h, \dst\().8h, \mask\().8h
.endm

.macro cneg_vec_s32 dst, src, mask
	eor \dst\().16b, \src\().16b, \mask\().16b
	sub \dst\().4s, \dst\().4s, \mask\().4s
.endm

.macro divstep_round
	// Branchless per-lane equivalent of divstep_example.S csel/cneg.
	// s = [delta2 >= 0], matching the current C helper and GE example.
	cmge v20.8h, v4.8h, v5.8h

	// t = -(g & 1), as an all-zero/all-one 16-bit mask.
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15

	// active = s & t
	and v22.16b, v20.16b, v21.16b

	// g' = (g + (t ? (s ? -f : f) : 0)) >> 1
	cneg_vec_s16 v23, v2, v20
	and v23.16b, v23.16b, v21.16b

	// f' = active ? old_g : old_f.  Do this before overwriting g.
	bit v2.16b, v3.16b, v22.16b

	add v24.8h, v3.8h, v23.8h
	sshr v3.8h, v24.8h, #1

	// delta2' = (active ? -delta2 : delta2) + 2
	cneg_vec_s16 v4, v4, v22
	add v4.8h, v4.8h, v7.8h

	// Extend only the masks needed by 32-bit V/R:
	// R' = R + (t & V) - (active & (2*V))
	// V' = active ? 2*R : 2*V
	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h

	// Low lanes: update R in place, then V in place.
	and v28.16b, v16.16b, v24.16b
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b

	// High lanes: same update with high-half masks.
	and v28.16b, v17.16b, v25.16b
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
.endm

.global C_SYM(gt_fqinv_delta_divstep_asm)
C_SYM(gt_fqinv_delta_divstep_asm):
	// v0 = normalize_modq_s16(a)
	movi v5.8h, #0
	mov w9, #3457
	dup v6.8h, w9

	cmgt v20.8h, v5.8h, v0.8h
	add v21.8h, v0.8h, v6.8h
	bit v0.16b, v21.16b, v20.16b

	cmge v20.8h, v0.8h, v6.8h
	sub v21.8h, v0.8h, v6.8h
	bit v0.16b, v21.16b, v20.16b

	// f = q, g = amod, delta2 = 1, V = 0, R = 1
	mov v2.16b, v6.16b
	mov v3.16b, v0.16b
	mov w9, #1
	dup v4.8h, w9
	movi v16.4s, #0
	movi v17.4s, #0
	dup v18.4s, w9
	dup v19.4s, w9
	mov w9, #2
	dup v7.8h, w9

	.rept 28
	divstep_round
	.endr

	// if (f < 0) V = -V
	cmgt v20.8h, v5.8h, v2.8h
	sxtl v21.4s, v20.4h
	sxtl2 v22.4s, v20.8h

	cneg_vec_s32 v16, v16, v21
	cneg_vec_s32 v17, v17, v22

	// reduce_s32_modq_to_s16(Vlo, Vhi)
	mov w9, #3457
	dup v6.4s, w9
	movz w9, #0x7a8f
	movk w9, #0x9, lsl #16
	dup v23.4s, w9

	sqrdmulh v24.4s, v16.4s, v23.4s
	mls v16.4s, v24.4s, v6.4s
	sqrdmulh v25.4s, v17.4s, v23.4s
	mls v17.4s, v25.4s, v6.4s

	xtn v16.4h, v16.4s
	xtn2 v16.8h, v17.4s

	// final representation scale.
	dup v7.8h, w0
	fqmul v16, v16, v7

	// Preserve existing zero behavior: input zero maps to zero.
	cmeq v20.8h, v0.8h, v5.8h
	bic v0.16b, v16.16b, v20.16b
	ret
