/*
 * Symbolic form of the exact 100-instruction V3 shared helper.
 *
 * Live-in bindings:
 *   lhs0..lhs3 = v4..v7
 *   v0          = fixed reduction constants
 *   x0/x2/x3    = dst/rhs/zeta pointers
 *
 * v24-v31 are deliberately absent and reserved by the driver. They carry the
 * next gather group across each helper call and must remain unchanged.
 */

.text
.align 2
// Live-in: x0 x2 x3, fixed v0, and Q<lhs0> Q<lhs1> Q<lhs2> Q<lhs3>.
// The loads define Q<lambda> Q<b0> Q<b1> Q<b2> Q<b3>.
// Live-out: x0+64, x2+64, x3+16, output memory, and v24-v31 unchanged.
// Range: production signed int16 inputs, int32 quartic accumulators, reduced int16 outputs.
// Reserved physical registers: v0, v24-v31, x1, x4-x30, and sp.
slothy_start_decap_verify_helper_v3:
	ld1 {V<lambda>.8h}, [x3], #16
	ld1 {V<b0>.8h, V<b1>.8h, V<b2>.8h, V<b3>.8h}, [x2], #64

	// Quartic wraparound dot products.
	smull V<w0_lo>.4s, V<lhs1>.4h, V<b3>.4h
	smull2 V<w0_hi>.4s, V<lhs1>.8h, V<b3>.8h
	smull V<w1_lo>.4s, V<lhs2>.4h, V<b3>.4h
	smull2 V<w1_hi>.4s, V<lhs2>.8h, V<b3>.8h
	smull V<w2_lo>.4s, V<lhs3>.4h, V<b3>.4h
	smull2 V<w2_hi>.4s, V<lhs3>.8h, V<b3>.8h

	smlal V<w0_lo>.4s, V<lhs2>.4h, V<b2>.4h
	smlal2 V<w0_hi>.4s, V<lhs2>.8h, V<b2>.8h
	smlal V<w1_lo>.4s, V<lhs3>.4h, V<b2>.4h
	smlal2 V<w1_hi>.4s, V<lhs3>.8h, V<b2>.8h
	smlal V<w0_lo>.4s, V<lhs3>.4h, V<b1>.4h
	smlal2 V<w0_hi>.4s, V<lhs3>.8h, V<b1>.8h

	// Montgomery-fold the three wraparound values.
	uzp1 V<w2_mraw>.8h, V<w2_lo>.8h, V<w2_hi>.8h
	uzp1 V<w1_mraw>.8h, V<w1_lo>.8h, V<w1_hi>.8h
	uzp1 V<w0_mraw>.8h, V<w0_lo>.8h, V<w0_hi>.8h
	mul V<w2_m>.8h, V<w2_mraw>.8h, v0.h[2]
	mul V<w1_m>.8h, V<w1_mraw>.8h, v0.h[2]
	mul V<w0_m>.8h, V<w0_mraw>.8h, v0.h[2]
	smlal V<w2_lo>.4s, V<w2_m>.4h, v0.h[0]
	smlal2 V<w2_hi>.4s, V<w2_m>.8h, v0.h[0]
	smlal V<w1_lo>.4s, V<w1_m>.4h, v0.h[0]
	smlal2 V<w1_hi>.4s, V<w1_m>.8h, v0.h[0]
	smlal V<w0_lo>.4s, V<w0_m>.4h, v0.h[0]
	smlal2 V<w0_hi>.4s, V<w0_m>.8h, v0.h[0]

	uzp2 V<w2_red>.8h, V<w2_lo>.8h, V<w2_hi>.8h
	uzp2 V<w1_red>.8h, V<w1_lo>.8h, V<w1_hi>.8h
	smull V<r3_lo>.4s, V<lhs3>.4h, V<b0>.4h
	smull2 V<r3_hi>.4s, V<lhs3>.8h, V<b0>.8h
	smull V<r2_lo>.4s, V<w2_red>.4h, V<lambda>.4h
	smull2 V<r2_hi>.4s, V<w2_red>.8h, V<lambda>.8h
	uzp2 V<w0_red>.8h, V<w0_lo>.8h, V<w0_hi>.8h
	smull V<r1_lo>.4s, V<w1_red>.4h, V<lambda>.4h
	smull2 V<r1_hi>.4s, V<w1_red>.8h, V<lambda>.8h
	smull V<r0_lo>.4s, V<w0_red>.4h, V<lambda>.4h
	smull2 V<r0_hi>.4s, V<w0_red>.8h, V<lambda>.8h

	// Remaining four quartic dot products.
	smlal V<r3_lo>.4s, V<lhs0>.4h, V<b3>.4h
	smlal2 V<r3_hi>.4s, V<lhs0>.8h, V<b3>.8h
	smlal V<r2_lo>.4s, V<lhs0>.4h, V<b2>.4h
	smlal2 V<r2_hi>.4s, V<lhs0>.8h, V<b2>.8h
	smlal V<r1_lo>.4s, V<lhs0>.4h, V<b1>.4h
	smlal2 V<r1_hi>.4s, V<lhs0>.8h, V<b1>.8h
	smlal V<r0_lo>.4s, V<lhs0>.4h, V<b0>.4h
	smlal2 V<r0_hi>.4s, V<lhs0>.8h, V<b0>.8h
	smlal V<r3_lo>.4s, V<lhs1>.4h, V<b2>.4h
	smlal2 V<r3_hi>.4s, V<lhs1>.8h, V<b2>.8h
	smlal V<r2_lo>.4s, V<lhs1>.4h, V<b1>.4h
	smlal2 V<r2_hi>.4s, V<lhs1>.8h, V<b1>.8h
	smlal V<r1_lo>.4s, V<lhs1>.4h, V<b0>.4h
	smlal2 V<r1_hi>.4s, V<lhs1>.8h, V<b0>.8h
	smlal V<r3_lo>.4s, V<lhs2>.4h, V<b1>.4h
	smlal2 V<r3_hi>.4s, V<lhs2>.8h, V<b1>.8h
	smlal V<r2_lo>.4s, V<lhs2>.4h, V<b0>.4h
	smlal2 V<r2_hi>.4s, V<lhs2>.8h, V<b0>.8h

	// Montgomery-fold the four output accumulators.
	uzp1 V<r3_mraw>.8h, V<r3_lo>.8h, V<r3_hi>.8h
	uzp1 V<r2_mraw>.8h, V<r2_lo>.8h, V<r2_hi>.8h
	uzp1 V<r1_mraw>.8h, V<r1_lo>.8h, V<r1_hi>.8h
	uzp1 V<r0_mraw>.8h, V<r0_lo>.8h, V<r0_hi>.8h
	mul V<r3_m>.8h, V<r3_mraw>.8h, v0.h[2]
	mul V<r2_m>.8h, V<r2_mraw>.8h, v0.h[2]
	mul V<r1_m>.8h, V<r1_mraw>.8h, v0.h[2]
	mul V<r0_m>.8h, V<r0_mraw>.8h, v0.h[2]
	smlal V<r3_lo>.4s, V<r3_m>.4h, v0.h[0]
	smlal V<r2_lo>.4s, V<r2_m>.4h, v0.h[0]
	smlal V<r1_lo>.4s, V<r1_m>.4h, v0.h[0]
	smlal V<r0_lo>.4s, V<r0_m>.4h, v0.h[0]
	smlal2 V<r3_hi>.4s, V<r3_m>.8h, v0.h[0]
	smlal2 V<r2_hi>.4s, V<r2_m>.8h, v0.h[0]
	smlal2 V<r1_hi>.4s, V<r1_m>.8h, v0.h[0]
	smlal2 V<r0_hi>.4s, V<r0_m>.8h, v0.h[0]

	uzp2 V<raw3>.8h, V<r3_lo>.8h, V<r3_hi>.8h
	uzp2 V<raw2>.8h, V<r2_lo>.8h, V<r2_hi>.8h
	uzp2 V<raw1>.8h, V<r1_lo>.8h, V<r1_hi>.8h
	uzp2 V<raw0>.8h, V<r0_lo>.8h, V<r0_hi>.8h

	// Final Montgomery scale followed by Barrett representative reduction.
	mul V<out3>.8h, V<raw3>.8h, v0.h[3]
	mul V<out2>.8h, V<raw2>.8h, v0.h[3]
	mul V<out1>.8h, V<raw1>.8h, v0.h[3]
	mul V<out0>.8h, V<raw0>.8h, v0.h[3]
	sqrdmulh V<corr3>.8h, V<raw3>.8h, v0.h[4]
	sqrdmulh V<corr2>.8h, V<raw2>.8h, v0.h[4]
	sqrdmulh V<corr1>.8h, V<raw1>.8h, v0.h[4]
	sqrdmulh V<corr0>.8h, V<raw0>.8h, v0.h[4]
	mls V<out3>.8h, V<corr3>.8h, v0.h[0]
	mls V<out2>.8h, V<corr2>.8h, v0.h[0]
	mls V<out1>.8h, V<corr1>.8h, v0.h[0]
	mls V<out0>.8h, V<corr0>.8h, v0.h[0]

	sqdmulh V<quo3>.8h, V<out3>.8h, v0.h[1]
	sqdmulh V<quo2>.8h, V<out2>.8h, v0.h[1]
	sqdmulh V<quo1>.8h, V<out1>.8h, v0.h[1]
	sqdmulh V<quo0>.8h, V<out0>.8h, v0.h[1]
	srshr V<quo3>.8h, V<quo3>.8h, #11
	srshr V<quo2>.8h, V<quo2>.8h, #11
	srshr V<quo1>.8h, V<quo1>.8h, #11
	srshr V<quo0>.8h, V<quo0>.8h, #11
	mls V<out3>.8h, V<quo3>.8h, v0.h[0]
	mls V<out2>.8h, V<quo2>.8h, v0.h[0]
	mls V<out1>.8h, V<quo1>.8h, v0.h[0]
	mls V<out0>.8h, V<quo0>.8h, v0.h[0]

	st1 {V<out0>.8h, V<out1>.8h, V<out2>.8h, V<out3>.8h}, [x0], #64
slothy_end_decap_verify_helper_v3:
