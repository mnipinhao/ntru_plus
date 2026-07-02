.text
.align 2

/*
 * Symbolic Slothy input for the GT basemul_add32 finalization block only.
 *
 * This mirrors the GT_BASEMUL_ADD32_RMINUS1_FINALIZE path in ../base_gt.S:
 *
 *   out = Mont(c * R + raw_rminus1 * R^2)
 *
 * It is not production-wired.  The loads before the Slothy region are
 * prototype scaffolding for an isolated one-stripe wrapper: x1 and x2 point to
 * four pre-deinterleaved Q vectors each, and x3 points at the base constants.
 * In the production loop these logical live-ins are already in registers after
 * the quartic product and c-input load.
 */

.global base_gt_add32_rminus1_finalize_symbolic
base_gt_add32_rminus1_finalize_symbolic:
	/* Prototype scaffolding, outside the optimized region. */
	ldr Q<v_raw0>, [x1, #0]
	ldr Q<v_raw1>, [x1, #16]
	ldr Q<v_raw2>, [x1, #32]
	ldr Q<v_raw3>, [x1, #48]
	ldr Q<v_c0>, [x2, #0]
	ldr Q<v_c1>, [x2, #16]
	ldr Q<v_c2>, [x2, #32]
	ldr Q<v_c3>, [x2, #48]
	ldr Q<v_const>, [x3]

slothy_start_base_gt_add32_rminus1_finalize:
	// live-in: Q<v_raw0>..Q<v_raw3> are R^-1 raw basemul residues.
	// live-in: Q<v_c0>..Q<v_c3> are normal R^0 addend coefficients.
	// live-in: Q<v_const>.h[0]=q, h[2]=-qinv, h[3]=R, h[7]=R^2.
	// reserved physical registers: x0 is the concrete output pointer; the driver reserves platform/ABI registers.
	// range: raw lanes in [-3456,3456], c lanes normal bounded residues; 32-bit prefinal lanes hold c*R + raw*R^2.

	// coeff 0: prefinal = raw0 * R^2 + c0 * R
	smull  V<v_acc0_lo>.4s, V<v_raw0>.4h, V<v_const>.h[7]
	smull2 V<v_acc0_hi>.4s, V<v_raw0>.8h, V<v_const>.h[7]
	smlal  V<v_acc0_lo>.4s, V<v_c0>.4h, V<v_const>.h[3]
	smlal2 V<v_acc0_hi>.4s, V<v_c0>.8h, V<v_const>.h[3]
	uzp1   V<v_m0>.8h, V<v_acc0_lo>.8h, V<v_acc0_hi>.8h
	mul    V<v_m0q>.8h, V<v_m0>.8h, V<v_const>.h[2]
	smlal  V<v_acc0_lo>.4s, V<v_m0q>.4h, V<v_const>.h[0]
	smlal2 V<v_acc0_hi>.4s, V<v_m0q>.8h, V<v_const>.h[0]
	uzp2   V<v_out0>.8h, V<v_acc0_lo>.8h, V<v_acc0_hi>.8h

	// coeff 1: prefinal = raw1 * R^2 + c1 * R
	smull  V<v_acc1_lo>.4s, V<v_raw1>.4h, V<v_const>.h[7]
	smull2 V<v_acc1_hi>.4s, V<v_raw1>.8h, V<v_const>.h[7]
	smlal  V<v_acc1_lo>.4s, V<v_c1>.4h, V<v_const>.h[3]
	smlal2 V<v_acc1_hi>.4s, V<v_c1>.8h, V<v_const>.h[3]
	uzp1   V<v_m1>.8h, V<v_acc1_lo>.8h, V<v_acc1_hi>.8h
	mul    V<v_m1q>.8h, V<v_m1>.8h, V<v_const>.h[2]
	smlal  V<v_acc1_lo>.4s, V<v_m1q>.4h, V<v_const>.h[0]
	smlal2 V<v_acc1_hi>.4s, V<v_m1q>.8h, V<v_const>.h[0]
	uzp2   V<v_out1>.8h, V<v_acc1_lo>.8h, V<v_acc1_hi>.8h

	// coeff 2: prefinal = raw2 * R^2 + c2 * R
	smull  V<v_acc2_lo>.4s, V<v_raw2>.4h, V<v_const>.h[7]
	smull2 V<v_acc2_hi>.4s, V<v_raw2>.8h, V<v_const>.h[7]
	smlal  V<v_acc2_lo>.4s, V<v_c2>.4h, V<v_const>.h[3]
	smlal2 V<v_acc2_hi>.4s, V<v_c2>.8h, V<v_const>.h[3]
	uzp1   V<v_m2>.8h, V<v_acc2_lo>.8h, V<v_acc2_hi>.8h
	mul    V<v_m2q>.8h, V<v_m2>.8h, V<v_const>.h[2]
	smlal  V<v_acc2_lo>.4s, V<v_m2q>.4h, V<v_const>.h[0]
	smlal2 V<v_acc2_hi>.4s, V<v_m2q>.8h, V<v_const>.h[0]
	uzp2   V<v_out2>.8h, V<v_acc2_lo>.8h, V<v_acc2_hi>.8h

	// coeff 3: prefinal = raw3 * R^2 + c3 * R
	smull  V<v_acc3_lo>.4s, V<v_raw3>.4h, V<v_const>.h[7]
	smull2 V<v_acc3_hi>.4s, V<v_raw3>.8h, V<v_const>.h[7]
	smlal  V<v_acc3_lo>.4s, V<v_c3>.4h, V<v_const>.h[3]
	smlal2 V<v_acc3_hi>.4s, V<v_c3>.8h, V<v_const>.h[3]
	uzp1   V<v_m3>.8h, V<v_acc3_lo>.8h, V<v_acc3_hi>.8h
	mul    V<v_m3q>.8h, V<v_m3>.8h, V<v_const>.h[2]
	smlal  V<v_acc3_lo>.4s, V<v_m3q>.4h, V<v_const>.h[0]
	smlal2 V<v_acc3_hi>.4s, V<v_m3q>.8h, V<v_const>.h[0]
	uzp2   V<v_out3>.8h, V<v_acc3_lo>.8h, V<v_acc3_hi>.8h

	st4 {V<v_out0>.8h, V<v_out1>.8h, V<v_out2>.8h, V<v_out3>.8h}, [x0], #64
	// live-out: memory at old x0 receives normal R^0 block-major coefficients; x0 is advanced by 64 bytes.
slothy_end_base_gt_add32_rminus1_finalize:

	ret
