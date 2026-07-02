/*
 * Slothy symbolic prototype for the complete GT basemul_add32 pipeline.
 *
 * This models one source-order loop body from asm/gt/base_gt.S when
 * GT_BASEMUL_ADD32_RMINUS1_FINALIZE is enabled:
 *
 *   ld4(a), ld4(b), ld4(c)
 *   quartic product modulo X^4-lambda
 *   required inner Montgomery reductions for the lambda wraparound terms
 *   add32 finalizer out = Mont(c * R + raw_rminus1 * R^2)
 *   st4(out)
 *
 * It is intentionally not production-wired.  The region uses fixed public
 * pointer GPRs x0..x5 but all NEON temporaries are symbolic.
 */

	.text
	.align 2

	.global base_gt_add32_full_pipeline_slothy_prototype
	.global _base_gt_add32_full_pipeline_slothy_prototype
base_gt_add32_full_pipeline_slothy_prototype:
_base_gt_add32_full_pipeline_slothy_prototype:
	/*
	 * Live-in: x0=dst, x1=src1, x2=src2, x3=src3 addend,
	 * x4=lambda vector pointer, x5=Lgt_base_consts pointer.
	 * Live-out: memory at old x0 gets st4(out0,out1,out2,out3);
	 * x0,x1,x2,x3 advance by 64 bytes and x4 advances by 16 bytes.
	 * Range: KEM GT production input bounds; internal high terms are
	 * Montgomery-reduced before lambda multiplication; final add32 uses
	 * int32 lanes for c * R + raw_rminus1 * R^2.
	 * Reserved physical registers: x6-x30 and sp.  Concrete x0-x5 are
	 * public memory pointers.  The symbolic names below are also listed so
	 * the local checker sees all ld4-defined vectors:
	 * Q<const>, Q<lam>, Q<a0>, Q<a1>, Q<a2>, Q<a3>, Q<b0>, Q<b1>, Q<b2>,
	 * Q<b3>, Q<c0>, Q<c1>, Q<c2>, Q<c3>.
	 *
	 * Live-in summary for the checker: x0, x1, x2, x3, x4, x5.
	 * Live-out summary for the checker: dst memory plus post-incremented
	 * x0, x1, x2, x3, x4.  Range summary: reduced signed int16 residues
	 * with int32 Montgomery-fold accumulators.  Reserved physical register
	 * summary: x6-x30 and sp.
	 */
slothy_start_base_gt_add32_full_pipeline:
	ldr Q<const>, [x5]
	ldr Q<lam>, [x4], #16
	ld4 {V<a0>.8h, V<a1>.8h, V<a2>.8h, V<a3>.8h}, [x1], #64
	ld4 {V<b0>.8h, V<b1>.8h, V<b2>.8h, V<b3>.8h}, [x2], #64
	ld4 {V<c0>.8h, V<c1>.8h, V<c2>.8h, V<c3>.8h}, [x3], #64

	// High wraparound dot products before multiplying by lambda.
	smull  V<w0_lo>.4s, V<a1>.4h, V<b3>.4h
	smull2 V<w0_hi>.4s, V<a1>.8h, V<b3>.8h
	smull  V<w1_lo>.4s, V<a2>.4h, V<b3>.4h
	smull2 V<w1_hi>.4s, V<a2>.8h, V<b3>.8h
	smull  V<w2_lo>.4s, V<a3>.4h, V<b3>.4h
	smull2 V<w2_hi>.4s, V<a3>.8h, V<b3>.8h

	smlal  V<w0_lo>.4s, V<a2>.4h, V<b2>.4h
	smlal2 V<w0_hi>.4s, V<a2>.8h, V<b2>.8h
	smlal  V<w1_lo>.4s, V<a3>.4h, V<b2>.4h
	smlal2 V<w1_hi>.4s, V<a3>.8h, V<b2>.8h

	smlal  V<w0_lo>.4s, V<a3>.4h, V<b1>.4h
	smlal2 V<w0_hi>.4s, V<a3>.8h, V<b1>.8h

	uzp1 V<w2_mlow>.8h, V<w2_lo>.8h, V<w2_hi>.8h
	uzp1 V<w1_mlow>.8h, V<w1_lo>.8h, V<w1_hi>.8h
	uzp1 V<w0_mlow>.8h, V<w0_lo>.8h, V<w0_hi>.8h

	mul V<w2_m>.8h, V<w2_mlow>.8h, V<const>.h[2]
	mul V<w1_m>.8h, V<w1_mlow>.8h, V<const>.h[2]
	mul V<w0_m>.8h, V<w0_mlow>.8h, V<const>.h[2]

	smlal  V<w2_lo>.4s, V<w2_m>.4h, V<const>.h[0]
	smlal2 V<w2_hi>.4s, V<w2_m>.8h, V<const>.h[0]
	smlal  V<w1_lo>.4s, V<w1_m>.4h, V<const>.h[0]
	smlal2 V<w1_hi>.4s, V<w1_m>.8h, V<const>.h[0]
	smlal  V<w0_lo>.4s, V<w0_m>.4h, V<const>.h[0]
	smlal2 V<w0_hi>.4s, V<w0_m>.8h, V<const>.h[0]

	uzp2 V<w2_red>.8h, V<w2_lo>.8h, V<w2_hi>.8h
	uzp2 V<w1_red>.8h, V<w1_lo>.8h, V<w1_hi>.8h
	uzp2 V<w0_red>.8h, V<w0_lo>.8h, V<w0_hi>.8h

	// Four raw quartic output coefficients, before the second product fold.
	smull  V<r3_lo>.4s, V<a3>.4h, V<b0>.4h
	smull2 V<r3_hi>.4s, V<a3>.8h, V<b0>.8h
	smull  V<r2_lo>.4s, V<w2_red>.4h, V<lam>.4h
	smull2 V<r2_hi>.4s, V<w2_red>.8h, V<lam>.8h
	smull  V<r1_lo>.4s, V<w1_red>.4h, V<lam>.4h
	smull2 V<r1_hi>.4s, V<w1_red>.8h, V<lam>.8h
	smull  V<r0_lo>.4s, V<w0_red>.4h, V<lam>.4h
	smull2 V<r0_hi>.4s, V<w0_red>.8h, V<lam>.8h

	smlal  V<r3_lo>.4s, V<a0>.4h, V<b3>.4h
	smlal2 V<r3_hi>.4s, V<a0>.8h, V<b3>.8h
	smlal  V<r2_lo>.4s, V<a0>.4h, V<b2>.4h
	smlal2 V<r2_hi>.4s, V<a0>.8h, V<b2>.8h
	smlal  V<r1_lo>.4s, V<a0>.4h, V<b1>.4h
	smlal2 V<r1_hi>.4s, V<a0>.8h, V<b1>.8h
	smlal  V<r0_lo>.4s, V<a0>.4h, V<b0>.4h
	smlal2 V<r0_hi>.4s, V<a0>.8h, V<b0>.8h

	smlal  V<r3_lo>.4s, V<a1>.4h, V<b2>.4h
	smlal2 V<r3_hi>.4s, V<a1>.8h, V<b2>.8h
	smlal  V<r2_lo>.4s, V<a1>.4h, V<b1>.4h
	smlal2 V<r2_hi>.4s, V<a1>.8h, V<b1>.8h
	smlal  V<r1_lo>.4s, V<a1>.4h, V<b0>.4h
	smlal2 V<r1_hi>.4s, V<a1>.8h, V<b0>.8h

	smlal  V<r3_lo>.4s, V<a2>.4h, V<b1>.4h
	smlal2 V<r3_hi>.4s, V<a2>.8h, V<b1>.8h
	smlal  V<r2_lo>.4s, V<a2>.4h, V<b0>.4h
	smlal2 V<r2_hi>.4s, V<a2>.8h, V<b0>.8h

	// Product Montgomery fold: raw0..raw3 are R^-1 residues.
	uzp1 V<r0_mlow>.8h, V<r0_lo>.8h, V<r0_hi>.8h
	uzp1 V<r1_mlow>.8h, V<r1_lo>.8h, V<r1_hi>.8h
	uzp1 V<r2_mlow>.8h, V<r2_lo>.8h, V<r2_hi>.8h
	uzp1 V<r3_mlow>.8h, V<r3_lo>.8h, V<r3_hi>.8h

	mul V<r0_m>.8h, V<r0_mlow>.8h, V<const>.h[2]
	mul V<r1_m>.8h, V<r1_mlow>.8h, V<const>.h[2]
	mul V<r2_m>.8h, V<r2_mlow>.8h, V<const>.h[2]
	mul V<r3_m>.8h, V<r3_mlow>.8h, V<const>.h[2]

	smlal  V<r0_lo>.4s, V<r0_m>.4h, V<const>.h[0]
	smlal2 V<r0_hi>.4s, V<r0_m>.8h, V<const>.h[0]
	smlal  V<r1_lo>.4s, V<r1_m>.4h, V<const>.h[0]
	smlal2 V<r1_hi>.4s, V<r1_m>.8h, V<const>.h[0]
	smlal  V<r2_lo>.4s, V<r2_m>.4h, V<const>.h[0]
	smlal2 V<r2_hi>.4s, V<r2_m>.8h, V<const>.h[0]
	smlal  V<r3_lo>.4s, V<r3_m>.4h, V<const>.h[0]
	smlal2 V<r3_hi>.4s, V<r3_m>.8h, V<const>.h[0]

	uzp2 V<raw0>.8h, V<r0_lo>.8h, V<r0_hi>.8h
	uzp2 V<raw1>.8h, V<r1_lo>.8h, V<r1_hi>.8h
	uzp2 V<raw2>.8h, V<r2_lo>.8h, V<r2_hi>.8h
	uzp2 V<raw3>.8h, V<r3_lo>.8h, V<r3_hi>.8h

	// add32 finalizer: out = Mont(c * R + raw_rminus1 * R^2).
	smull  V<o0_lo>.4s, V<raw0>.4h, V<const>.h[7]
	smull2 V<o0_hi>.4s, V<raw0>.8h, V<const>.h[7]
	smull  V<o1_lo>.4s, V<raw1>.4h, V<const>.h[7]
	smull2 V<o1_hi>.4s, V<raw1>.8h, V<const>.h[7]
	smull  V<o2_lo>.4s, V<raw2>.4h, V<const>.h[7]
	smull2 V<o2_hi>.4s, V<raw2>.8h, V<const>.h[7]
	smull  V<o3_lo>.4s, V<raw3>.4h, V<const>.h[7]
	smull2 V<o3_hi>.4s, V<raw3>.8h, V<const>.h[7]

	smlal  V<o0_lo>.4s, V<c0>.4h, V<const>.h[3]
	smlal2 V<o0_hi>.4s, V<c0>.8h, V<const>.h[3]
	smlal  V<o1_lo>.4s, V<c1>.4h, V<const>.h[3]
	smlal2 V<o1_hi>.4s, V<c1>.8h, V<const>.h[3]
	smlal  V<o2_lo>.4s, V<c2>.4h, V<const>.h[3]
	smlal2 V<o2_hi>.4s, V<c2>.8h, V<const>.h[3]
	smlal  V<o3_lo>.4s, V<c3>.4h, V<const>.h[3]
	smlal2 V<o3_hi>.4s, V<c3>.8h, V<const>.h[3]

	uzp1 V<o0_mlow>.8h, V<o0_lo>.8h, V<o0_hi>.8h
	uzp1 V<o1_mlow>.8h, V<o1_lo>.8h, V<o1_hi>.8h
	uzp1 V<o2_mlow>.8h, V<o2_lo>.8h, V<o2_hi>.8h
	uzp1 V<o3_mlow>.8h, V<o3_lo>.8h, V<o3_hi>.8h

	mul V<o0_m>.8h, V<o0_mlow>.8h, V<const>.h[2]
	mul V<o1_m>.8h, V<o1_mlow>.8h, V<const>.h[2]
	mul V<o2_m>.8h, V<o2_mlow>.8h, V<const>.h[2]
	mul V<o3_m>.8h, V<o3_mlow>.8h, V<const>.h[2]

	smlal  V<o0_lo>.4s, V<o0_m>.4h, V<const>.h[0]
	smlal2 V<o0_hi>.4s, V<o0_m>.8h, V<const>.h[0]
	smlal  V<o1_lo>.4s, V<o1_m>.4h, V<const>.h[0]
	smlal2 V<o1_hi>.4s, V<o1_m>.8h, V<const>.h[0]
	smlal  V<o2_lo>.4s, V<o2_m>.4h, V<const>.h[0]
	smlal2 V<o2_hi>.4s, V<o2_m>.8h, V<const>.h[0]
	smlal  V<o3_lo>.4s, V<o3_m>.4h, V<const>.h[0]
	smlal2 V<o3_hi>.4s, V<o3_m>.8h, V<const>.h[0]

	uzp2 V<out0>.8h, V<o0_lo>.8h, V<o0_hi>.8h
	uzp2 V<out1>.8h, V<o1_lo>.8h, V<o1_hi>.8h
	uzp2 V<out2>.8h, V<o2_lo>.8h, V<o2_hi>.8h
	uzp2 V<out3>.8h, V<o3_lo>.8h, V<o3_hi>.8h

	st4 {V<out0>.8h, V<out1>.8h, V<out2>.8h, V<out3>.8h}, [x0], #64
slothy_end_base_gt_add32_full_pipeline:
	ret
