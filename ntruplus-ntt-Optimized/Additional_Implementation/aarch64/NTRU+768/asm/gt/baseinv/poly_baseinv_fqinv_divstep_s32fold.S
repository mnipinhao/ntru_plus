/*
 * Benchmark-only 27-round delta-divstep Fq inverse core.
 *
 * ABI:
 *   v0.8h = input vector a
 *   v1.8h = unused constants vector, kept for ABI compatibility
 *   w0    = final_scale selector from the existing divstep helper
 *   returns v0.8h = divstep inverse output
 *
 * True delta2 round:
 *   s      = delta2 >= 0
 *   t      = g & 1
 *   active = s & t
 *   f'      = active ? g : f
 *   g'      = (g + (t ? (s ? -f : f) : 0)) >> 1
 *   delta2' = (active ? -delta2 : delta2) + 2
 *   V'      = active ? 2*R : 2*V
 *   R'      = R + (t ? (s ? -V : V) : 0)
 *
 * Exhaustive q=3457 check: 27 rounds are sufficient for all a=1..3456;
 * 26 rounds fail for a={2927,3186,3255,3439}.
 *
 * Final scale is folded into the initial R coefficient:
 *   final_scale == 32 -> scaled_r, R0 = 2375 = -1082 mod q
 *   otherwise         -> normal,   R0 = 1583 mod q
 *
 * Exhaustive int32 bound, a=1..3456, all 27 rounds:
 *   R0 = 1583:  max |V/R| = 284940000
 *   R0 = -1082: max |V/R| = 194760000
 * Both fit signed int32.  The final int32 modular reduction is unchanged
 * from the exact V/R divstep ASM, and the final fqmul is removed.
 *
 * Benchmark-only compile-time variants:
 *   GT_BASEINV_S32FOLD_FINAL_SPECIAL       skip dead g/delta/R in round 26
 *   GT_BASEINV_S32FOLD_EARLY_SPECIAL       use round 0/1 s=true contracts
 *   GT_BASEINV_S32FOLD_SIGN_AFTER_REDUCE   reduce before final f-sign negate
 *   GT_BASEINV_S32FOLD_TNEXT               precompute next t mask from numerator
 *   GT_BASEINV_S32FOLD_TMASK_SHLSHR        use old shl/sshr t-mask generation
 *   GT_BASEINV_S32FOLD_RUPDATE_XORNEG      use xor/sub R-adjust update
 */

.text
.align 2

#include "../support/common.inc"

.global C_SYM(gt_fqinv_delta_divstep_s32fold_asm)
C_SYM(gt_fqinv_delta_divstep_s32fold_asm):
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

	// f = q, g = amod, delta2 = 1, V = 0.
	mov v2.16b, v6.16b
	mov v3.16b, v0.16b
	mov w9, #1
	dup v4.8h, w9
	movi v16.4s, #0
	movi v17.4s, #0
	mov w9, #2
	dup v7.8h, w9
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	movi v8.8h, #1
#endif

	// Fold final scale into R0. final_scale==32 is the scaled_r path.
	cmp w0, #32
	mov w9, #-1082
	mov w10, #1583
	csel w9, w9, w10, eq
	dup v18.4s, w9
	dup v19.4s, w9

#if defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif

#if defined(GT_BASEINV_S32FOLD_EARLY_SPECIAL)
	// round 0 special: s=true, active=t, V=0, R=R0
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	neg v23.8h, v2.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v21.16b
	sshr v3.8h, v31.8h, #1
	add v4.8h, v4.8h, v7.8h
	and v23.16b, v21.16b, v7.16b
	sub v4.8h, v4.8h, v23.8h
	sxtl v26.4s, v21.4h
	sxtl2 v27.4s, v21.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif
	shl v16.4s, v18.4s, #1
	and v16.16b, v16.16b, v26.16b
	shl v17.4s, v19.4s, #1
	and v17.16b, v17.16b, v27.16b

#else
	// round 0: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

#endif

#if defined(GT_BASEINV_S32FOLD_EARLY_SPECIAL)
	// round 1 special: s=true, active=t
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	neg v23.8h, v2.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v21.16b
	sshr v3.8h, v31.8h, #1
	eor v23.16b, v4.16b, v21.16b
	sub v23.8h, v23.8h, v21.8h
	add v4.8h, v23.8h, v7.8h
	sxtl v26.4s, v21.4h
	sxtl2 v27.4s, v21.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif
	and v28.16b, v16.16b, v26.16b
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	sub v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
	and v28.16b, v17.16b, v27.16b
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	sub v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b

#else
	// round 1: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

#endif

	// round 2: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

	// round 3: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

	// round 4: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

	// round 5: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

	// round 6: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

	// round 7: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

	// round 8: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

	// round 9: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

	// round 10: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

	// round 11: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

	// round 12: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

	// round 13: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

	// round 14: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

	// round 15: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

	// round 16: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

	// round 17: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

	// round 18: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

	// round 19: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

	// round 20: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

	// round 21: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

	// round 22: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

	// round 23: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

	// round 24: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

	// round 25: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
#if defined(GT_BASEINV_S32FOLD_TNEXT)
	shl v21.8h, v31.8h, #14
	sshr v21.8h, v21.8h, #15
#endif

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

#if defined(GT_BASEINV_S32FOLD_FINAL_SPECIAL)
	// round 26 special: only final f sign and V are used
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b
	bit v2.16b, v3.16b, v22.16b
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	bit v16.16b, v29.16b, v26.16b
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	bit v17.16b, v29.16b, v27.16b

#else
	// round 26: true delta2 divstep
	cmge v20.8h, v4.8h, v5.8h
#if !defined(GT_BASEINV_S32FOLD_TNEXT)
#if !defined(GT_BASEINV_S32FOLD_TMASK_SHLSHR)
	and v21.16b, v3.16b, v8.16b
	neg v21.8h, v21.8h
#else
	shl v21.8h, v3.8h, #15
	sshr v21.8h, v21.8h, #15
#endif
#endif
	and v22.16b, v20.16b, v21.16b

	eor v23.16b, v2.16b, v20.16b
	sub v23.8h, v23.8h, v20.8h
	and v23.16b, v23.16b, v21.16b
	add v31.8h, v3.8h, v23.8h
	bit v2.16b, v3.16b, v22.16b
	sshr v3.8h, v31.8h, #1

	eor v23.16b, v4.16b, v22.16b
	sub v23.8h, v23.8h, v22.8h
	add v4.8h, v23.8h, v7.8h

	sxtl v24.4s, v21.4h
	sxtl2 v25.4s, v21.8h
	sxtl v26.4s, v22.4h
	sxtl2 v27.4s, v22.8h

	and v28.16b, v16.16b, v24.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v26.16b
	sub v28.4s, v28.4s, v26.4s
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	add v18.4s, v18.4s, v28.4s
	bit v16.16b, v29.16b, v26.16b
#else
	shl v16.4s, v16.4s, #1
	shl v29.4s, v18.4s, #1
	and v30.16b, v16.16b, v26.16b
	add v18.4s, v18.4s, v28.4s
	sub v18.4s, v18.4s, v30.4s
	bit v16.16b, v29.16b, v26.16b
#endif

	and v28.16b, v17.16b, v25.16b
#if defined(GT_BASEINV_S32FOLD_RUPDATE_XORNEG)
	eor v28.16b, v28.16b, v27.16b
	sub v28.4s, v28.4s, v27.4s
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	add v19.4s, v19.4s, v28.4s
	bit v17.16b, v29.16b, v27.16b
#else
	shl v17.4s, v17.4s, #1
	shl v29.4s, v19.4s, #1
	and v30.16b, v17.16b, v27.16b
	add v19.4s, v19.4s, v28.4s
	sub v19.4s, v19.4s, v30.4s
	bit v17.16b, v29.16b, v27.16b
#endif

#endif

#if !defined(GT_BASEINV_S32FOLD_SIGN_AFTER_REDUCE)
	// if (f < 0) V = -V before reduction
	cmgt v20.8h, v5.8h, v2.8h
	sxtl v21.4s, v20.4h
	sxtl2 v22.4s, v20.8h
	eor v16.16b, v16.16b, v21.16b
	sub v16.4s, v16.4s, v21.4s
	eor v17.16b, v17.16b, v22.16b
	sub v17.4s, v17.4s, v22.4s
#endif

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

#if defined(GT_BASEINV_S32FOLD_SIGN_AFTER_REDUCE)
	// if (f < 0) Vmod = -Vmod after reduction
	cmgt v20.8h, v5.8h, v2.8h
	eor v16.16b, v16.16b, v20.16b
	sub v16.8h, v16.8h, v20.8h
#endif

	// Preserve existing zero behavior: input zero maps to zero.
	cmeq v20.8h, v0.8h, v5.8h
	bic v0.16b, v16.16b, v20.16b
	ret
