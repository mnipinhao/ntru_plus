/*
 * Generated symbolic Slothy source for one benchmark-only HIERK8
 * prepare2 group. See kernel-contract.yml and instruction-dag.yml.
 *
 * Live-in/out: x0-x5 pointer streams and fixed v0 constants.
 * No spills and no secret-dependent control or memory addressing.
 */

.text
.align 2
// Live-in: x0-x5 pointer streams and fixed v0 constants.
// Live-out: exact stores, x0-x5 pointer advances, and v0 preserved.
// Range: current GT baseinv signed-int16 inputs, int32 widened products, exact int16 outputs.
// Reserved physical registers: x6-x30, sp, and fixed vector v0.
// The loads define Q<b0_zeta> Q<b1_zeta> Q<b2_zeta> Q<b0_a0> Q<b0_a1> Q<b0_a2> Q<b0_a3>.
// They also define Q<b1_a0> Q<b1_a1> Q<b1_a2> Q<b1_a3> Q<b2_a0> Q<b2_a1> Q<b2_a2> Q<b2_a3>.
slothy_start_gt_baseinv_prepare2_group:
// Live-in: x0 x1 x4 x5 and fixed v0; loaded values are defined below.
// Live-out: x0 x1 x4 x5 advances and Q<c01> for phase 2.
// Range: current GT baseinv int16 inputs, int32 products, exact int16 outputs.
// Reserved physical registers: x6-x30, sp, and fixed vector v0.
slothy_start_gt_baseinv_prepare2_phase01:
	ld1 {V<b0_zeta>.8h, V<b1_zeta>.8h}, [x5], #32
	ld4 {V<b0_a0>.8h, V<b0_a1>.8h, V<b0_a2>.8h, V<b0_a3>.8h}, [x4], #64
	movi V<zero>.8h, #0

	// Block 0: closed-form quartic prepare
	sub V<b0_neg_a2>.8h, V<zero>.8h, V<b0_a2>.8h
	sub V<b0_neg_a3>.8h, V<zero>.8h, V<b0_a3>.8h
	add V<b0_neg2a2>.8h, V<b0_neg_a2>.8h, V<b0_neg_a2>.8h
	add V<b0_neg2a3>.8h, V<b0_neg_a3>.8h, V<b0_neg_a3>.8h
	smull V<b0_r_t0a_lo>.4s, V<b0_a2>.4h, V<b0_a2>.4h
	smull2 V<b0_r_t0a_hi>.4s, V<b0_a2>.8h, V<b0_a2>.8h
	smlal V<b0_r_t0a_lo>.4s, V<b0_a1>.4h, V<b0_neg2a3>.4h
	smlal2 V<b0_r_t0a_hi>.4s, V<b0_a1>.8h, V<b0_neg2a3>.8h
	uzp1 V<b0_r_t0a_mraw>.8h, V<b0_r_t0a_lo>.8h, V<b0_r_t0a_hi>.8h
	mul V<b0_r_t0a_mred>.8h, V<b0_r_t0a_mraw>.8h, v0.h[2]
	smlal V<b0_r_t0a_lo>.4s, V<b0_r_t0a_mred>.4h, v0.h[0]
	smlal2 V<b0_r_t0a_hi>.4s, V<b0_r_t0a_mred>.8h, v0.h[0]
	uzp2 V<b0_t0a>.8h, V<b0_r_t0a_lo>.8h, V<b0_r_t0a_hi>.8h
	smull V<b0_r_t1a_lo>.4s, V<b0_a3>.4h, V<b0_a3>.4h
	smull2 V<b0_r_t1a_hi>.4s, V<b0_a3>.8h, V<b0_a3>.8h
	uzp1 V<b0_r_t1a_mraw>.8h, V<b0_r_t1a_lo>.8h, V<b0_r_t1a_hi>.8h
	mul V<b0_r_t1a_mred>.8h, V<b0_r_t1a_mraw>.8h, v0.h[2]
	smlal V<b0_r_t1a_lo>.4s, V<b0_r_t1a_mred>.4h, v0.h[0]
	smlal2 V<b0_r_t1a_hi>.4s, V<b0_r_t1a_mred>.8h, v0.h[0]
	uzp2 V<b0_t1a>.8h, V<b0_r_t1a_lo>.8h, V<b0_r_t1a_hi>.8h
	smull V<b0_r_t0_lo>.4s, V<b0_t0a>.4h, V<b0_zeta>.4h
	smull2 V<b0_r_t0_hi>.4s, V<b0_t0a>.8h, V<b0_zeta>.8h
	smlal V<b0_r_t0_lo>.4s, V<b0_a0>.4h, V<b0_a0>.4h
	smlal2 V<b0_r_t0_hi>.4s, V<b0_a0>.8h, V<b0_a0>.8h
	uzp1 V<b0_r_t0_mraw>.8h, V<b0_r_t0_lo>.8h, V<b0_r_t0_hi>.8h
	mul V<b0_r_t0_mred>.8h, V<b0_r_t0_mraw>.8h, v0.h[2]
	smlal V<b0_r_t0_lo>.4s, V<b0_r_t0_mred>.4h, v0.h[0]
	smlal2 V<b0_r_t0_hi>.4s, V<b0_r_t0_mred>.8h, v0.h[0]
	uzp2 V<b0_t0>.8h, V<b0_r_t0_lo>.8h, V<b0_r_t0_hi>.8h
	smull V<b0_r_t1_lo>.4s, V<b0_t1a>.4h, V<b0_zeta>.4h
	smull2 V<b0_r_t1_hi>.4s, V<b0_t1a>.8h, V<b0_zeta>.8h
	smlal V<b0_r_t1_lo>.4s, V<b0_a1>.4h, V<b0_a1>.4h
	smlal2 V<b0_r_t1_hi>.4s, V<b0_a1>.8h, V<b0_a1>.8h
	smlal V<b0_r_t1_lo>.4s, V<b0_a0>.4h, V<b0_neg2a2>.4h
	smlal2 V<b0_r_t1_hi>.4s, V<b0_a0>.8h, V<b0_neg2a2>.8h
	uzp1 V<b0_r_t1_mraw>.8h, V<b0_r_t1_lo>.8h, V<b0_r_t1_hi>.8h
	mul V<b0_r_t1_mred>.8h, V<b0_r_t1_mraw>.8h, v0.h[2]
	smlal V<b0_r_t1_lo>.4s, V<b0_r_t1_mred>.4h, v0.h[0]
	smlal2 V<b0_r_t1_hi>.4s, V<b0_r_t1_mred>.8h, v0.h[0]
	uzp2 V<b0_t1>.8h, V<b0_r_t1_lo>.8h, V<b0_r_t1_hi>.8h
	smull V<b0_r_t2_lo>.4s, V<b0_t1>.4h, V<b0_zeta>.4h
	smull2 V<b0_r_t2_hi>.4s, V<b0_t1>.8h, V<b0_zeta>.8h
	uzp1 V<b0_r_t2_mraw>.8h, V<b0_r_t2_lo>.8h, V<b0_r_t2_hi>.8h
	mul V<b0_r_t2_mred>.8h, V<b0_r_t2_mraw>.8h, v0.h[2]
	smlal V<b0_r_t2_lo>.4s, V<b0_r_t2_mred>.4h, v0.h[0]
	smlal2 V<b0_r_t2_hi>.4s, V<b0_r_t2_mred>.8h, v0.h[0]
	uzp2 V<b0_t2>.8h, V<b0_r_t2_lo>.8h, V<b0_r_t2_hi>.8h
	sub V<b0_negt1>.8h, V<zero>.8h, V<b0_t1>.8h
	smull V<b0_r_den_lo>.4s, V<b0_t0>.4h, V<b0_t0>.4h
	smull2 V<b0_r_den_hi>.4s, V<b0_t0>.8h, V<b0_t0>.8h
	smlal V<b0_r_den_lo>.4s, V<b0_negt1>.4h, V<b0_t2>.4h
	smlal2 V<b0_r_den_hi>.4s, V<b0_negt1>.8h, V<b0_t2>.8h
	uzp1 V<b0_r_den_mraw>.8h, V<b0_r_den_lo>.8h, V<b0_r_den_hi>.8h
	mul V<b0_r_den_mred>.8h, V<b0_r_den_mraw>.8h, v0.h[2]
	smlal V<b0_r_den_lo>.4s, V<b0_r_den_mred>.4h, v0.h[0]
	smlal2 V<b0_r_den_hi>.4s, V<b0_r_den_mred>.8h, v0.h[0]
	uzp2 V<b0_den>.8h, V<b0_r_den_lo>.8h, V<b0_r_den_hi>.8h
	smull V<b0_r_n0_lo>.4s, V<b0_a0>.4h, V<b0_t0>.4h
	smull2 V<b0_r_n0_hi>.4s, V<b0_a0>.8h, V<b0_t0>.8h
	smlal V<b0_r_n0_lo>.4s, V<b0_a2>.4h, V<b0_t2>.4h
	smlal2 V<b0_r_n0_hi>.4s, V<b0_a2>.8h, V<b0_t2>.8h
	uzp1 V<b0_r_n0_mraw>.8h, V<b0_r_n0_lo>.8h, V<b0_r_n0_hi>.8h
	mul V<b0_r_n0_mred>.8h, V<b0_r_n0_mraw>.8h, v0.h[2]
	smlal V<b0_r_n0_lo>.4s, V<b0_r_n0_mred>.4h, v0.h[0]
	smlal2 V<b0_r_n0_hi>.4s, V<b0_r_n0_mred>.8h, v0.h[0]
	uzp2 V<b0_n0>.8h, V<b0_r_n0_lo>.8h, V<b0_r_n0_hi>.8h
	smull V<b0_r_n1_lo>.4s, V<b0_a3>.4h, V<b0_t2>.4h
	smull2 V<b0_r_n1_hi>.4s, V<b0_a3>.8h, V<b0_t2>.8h
	smlal V<b0_r_n1_lo>.4s, V<b0_a1>.4h, V<b0_t0>.4h
	smlal2 V<b0_r_n1_hi>.4s, V<b0_a1>.8h, V<b0_t0>.8h
	uzp1 V<b0_r_n1_mraw>.8h, V<b0_r_n1_lo>.8h, V<b0_r_n1_hi>.8h
	mul V<b0_r_n1_mred>.8h, V<b0_r_n1_mraw>.8h, v0.h[2]
	smlal V<b0_r_n1_lo>.4s, V<b0_r_n1_mred>.4h, v0.h[0]
	smlal2 V<b0_r_n1_hi>.4s, V<b0_r_n1_mred>.8h, v0.h[0]
	uzp2 V<b0_n1>.8h, V<b0_r_n1_lo>.8h, V<b0_r_n1_hi>.8h
	smull V<b0_r_n2_lo>.4s, V<b0_a2>.4h, V<b0_t0>.4h
	smull2 V<b0_r_n2_hi>.4s, V<b0_a2>.8h, V<b0_t0>.8h
	smlal V<b0_r_n2_lo>.4s, V<b0_a0>.4h, V<b0_t1>.4h
	smlal2 V<b0_r_n2_hi>.4s, V<b0_a0>.8h, V<b0_t1>.8h
	uzp1 V<b0_r_n2_mraw>.8h, V<b0_r_n2_lo>.8h, V<b0_r_n2_hi>.8h
	mul V<b0_r_n2_mred>.8h, V<b0_r_n2_mraw>.8h, v0.h[2]
	smlal V<b0_r_n2_lo>.4s, V<b0_r_n2_mred>.4h, v0.h[0]
	smlal2 V<b0_r_n2_hi>.4s, V<b0_r_n2_mred>.8h, v0.h[0]
	uzp2 V<b0_n2>.8h, V<b0_r_n2_lo>.8h, V<b0_r_n2_hi>.8h
	smull V<b0_r_n3_lo>.4s, V<b0_a1>.4h, V<b0_t1>.4h
	smull2 V<b0_r_n3_hi>.4s, V<b0_a1>.8h, V<b0_t1>.8h
	smlal V<b0_r_n3_lo>.4s, V<b0_a3>.4h, V<b0_t0>.4h
	smlal2 V<b0_r_n3_hi>.4s, V<b0_a3>.8h, V<b0_t0>.8h
	uzp1 V<b0_r_n3_mraw>.8h, V<b0_r_n3_lo>.8h, V<b0_r_n3_hi>.8h
	mul V<b0_r_n3_mred>.8h, V<b0_r_n3_mraw>.8h, v0.h[2]
	smlal V<b0_r_n3_lo>.4s, V<b0_r_n3_mred>.4h, v0.h[0]
	smlal2 V<b0_r_n3_hi>.4s, V<b0_r_n3_mred>.8h, v0.h[0]
	uzp2 V<b0_n3>.8h, V<b0_r_n3_lo>.8h, V<b0_r_n3_hi>.8h
	st4 {V<b0_n0>.8h, V<b0_n1>.8h, V<b0_n2>.8h, V<b0_n3>.8h}, [x0], #64

	ld4 {V<b1_a0>.8h, V<b1_a1>.8h, V<b1_a2>.8h, V<b1_a3>.8h}, [x4], #64
	// Block 1: closed-form quartic prepare
	sub V<b1_neg_a2>.8h, V<zero>.8h, V<b1_a2>.8h
	sub V<b1_neg_a3>.8h, V<zero>.8h, V<b1_a3>.8h
	add V<b1_neg2a2>.8h, V<b1_neg_a2>.8h, V<b1_neg_a2>.8h
	add V<b1_neg2a3>.8h, V<b1_neg_a3>.8h, V<b1_neg_a3>.8h
	smull V<b1_r_t0a_lo>.4s, V<b1_a2>.4h, V<b1_a2>.4h
	smull2 V<b1_r_t0a_hi>.4s, V<b1_a2>.8h, V<b1_a2>.8h
	smlal V<b1_r_t0a_lo>.4s, V<b1_a1>.4h, V<b1_neg2a3>.4h
	smlal2 V<b1_r_t0a_hi>.4s, V<b1_a1>.8h, V<b1_neg2a3>.8h
	uzp1 V<b1_r_t0a_mraw>.8h, V<b1_r_t0a_lo>.8h, V<b1_r_t0a_hi>.8h
	mul V<b1_r_t0a_mred>.8h, V<b1_r_t0a_mraw>.8h, v0.h[2]
	smlal V<b1_r_t0a_lo>.4s, V<b1_r_t0a_mred>.4h, v0.h[0]
	smlal2 V<b1_r_t0a_hi>.4s, V<b1_r_t0a_mred>.8h, v0.h[0]
	uzp2 V<b1_t0a>.8h, V<b1_r_t0a_lo>.8h, V<b1_r_t0a_hi>.8h
	smull V<b1_r_t1a_lo>.4s, V<b1_a3>.4h, V<b1_a3>.4h
	smull2 V<b1_r_t1a_hi>.4s, V<b1_a3>.8h, V<b1_a3>.8h
	uzp1 V<b1_r_t1a_mraw>.8h, V<b1_r_t1a_lo>.8h, V<b1_r_t1a_hi>.8h
	mul V<b1_r_t1a_mred>.8h, V<b1_r_t1a_mraw>.8h, v0.h[2]
	smlal V<b1_r_t1a_lo>.4s, V<b1_r_t1a_mred>.4h, v0.h[0]
	smlal2 V<b1_r_t1a_hi>.4s, V<b1_r_t1a_mred>.8h, v0.h[0]
	uzp2 V<b1_t1a>.8h, V<b1_r_t1a_lo>.8h, V<b1_r_t1a_hi>.8h
	smull V<b1_r_t0_lo>.4s, V<b1_t0a>.4h, V<b1_zeta>.4h
	smull2 V<b1_r_t0_hi>.4s, V<b1_t0a>.8h, V<b1_zeta>.8h
	smlal V<b1_r_t0_lo>.4s, V<b1_a0>.4h, V<b1_a0>.4h
	smlal2 V<b1_r_t0_hi>.4s, V<b1_a0>.8h, V<b1_a0>.8h
	uzp1 V<b1_r_t0_mraw>.8h, V<b1_r_t0_lo>.8h, V<b1_r_t0_hi>.8h
	mul V<b1_r_t0_mred>.8h, V<b1_r_t0_mraw>.8h, v0.h[2]
	smlal V<b1_r_t0_lo>.4s, V<b1_r_t0_mred>.4h, v0.h[0]
	smlal2 V<b1_r_t0_hi>.4s, V<b1_r_t0_mred>.8h, v0.h[0]
	uzp2 V<b1_t0>.8h, V<b1_r_t0_lo>.8h, V<b1_r_t0_hi>.8h
	smull V<b1_r_t1_lo>.4s, V<b1_t1a>.4h, V<b1_zeta>.4h
	smull2 V<b1_r_t1_hi>.4s, V<b1_t1a>.8h, V<b1_zeta>.8h
	smlal V<b1_r_t1_lo>.4s, V<b1_a1>.4h, V<b1_a1>.4h
	smlal2 V<b1_r_t1_hi>.4s, V<b1_a1>.8h, V<b1_a1>.8h
	smlal V<b1_r_t1_lo>.4s, V<b1_a0>.4h, V<b1_neg2a2>.4h
	smlal2 V<b1_r_t1_hi>.4s, V<b1_a0>.8h, V<b1_neg2a2>.8h
	uzp1 V<b1_r_t1_mraw>.8h, V<b1_r_t1_lo>.8h, V<b1_r_t1_hi>.8h
	mul V<b1_r_t1_mred>.8h, V<b1_r_t1_mraw>.8h, v0.h[2]
	smlal V<b1_r_t1_lo>.4s, V<b1_r_t1_mred>.4h, v0.h[0]
	smlal2 V<b1_r_t1_hi>.4s, V<b1_r_t1_mred>.8h, v0.h[0]
	uzp2 V<b1_t1>.8h, V<b1_r_t1_lo>.8h, V<b1_r_t1_hi>.8h
	smull V<b1_r_t2_lo>.4s, V<b1_t1>.4h, V<b1_zeta>.4h
	smull2 V<b1_r_t2_hi>.4s, V<b1_t1>.8h, V<b1_zeta>.8h
	uzp1 V<b1_r_t2_mraw>.8h, V<b1_r_t2_lo>.8h, V<b1_r_t2_hi>.8h
	mul V<b1_r_t2_mred>.8h, V<b1_r_t2_mraw>.8h, v0.h[2]
	smlal V<b1_r_t2_lo>.4s, V<b1_r_t2_mred>.4h, v0.h[0]
	smlal2 V<b1_r_t2_hi>.4s, V<b1_r_t2_mred>.8h, v0.h[0]
	uzp2 V<b1_t2>.8h, V<b1_r_t2_lo>.8h, V<b1_r_t2_hi>.8h
	sub V<b1_negt1>.8h, V<zero>.8h, V<b1_t1>.8h
	smull V<b1_r_den_lo>.4s, V<b1_t0>.4h, V<b1_t0>.4h
	smull2 V<b1_r_den_hi>.4s, V<b1_t0>.8h, V<b1_t0>.8h
	smlal V<b1_r_den_lo>.4s, V<b1_negt1>.4h, V<b1_t2>.4h
	smlal2 V<b1_r_den_hi>.4s, V<b1_negt1>.8h, V<b1_t2>.8h
	uzp1 V<b1_r_den_mraw>.8h, V<b1_r_den_lo>.8h, V<b1_r_den_hi>.8h
	mul V<b1_r_den_mred>.8h, V<b1_r_den_mraw>.8h, v0.h[2]
	smlal V<b1_r_den_lo>.4s, V<b1_r_den_mred>.4h, v0.h[0]
	smlal2 V<b1_r_den_hi>.4s, V<b1_r_den_mred>.8h, v0.h[0]
	uzp2 V<b1_den>.8h, V<b1_r_den_lo>.8h, V<b1_r_den_hi>.8h
	smull V<b1_r_n0_lo>.4s, V<b1_a0>.4h, V<b1_t0>.4h
	smull2 V<b1_r_n0_hi>.4s, V<b1_a0>.8h, V<b1_t0>.8h
	smlal V<b1_r_n0_lo>.4s, V<b1_a2>.4h, V<b1_t2>.4h
	smlal2 V<b1_r_n0_hi>.4s, V<b1_a2>.8h, V<b1_t2>.8h
	uzp1 V<b1_r_n0_mraw>.8h, V<b1_r_n0_lo>.8h, V<b1_r_n0_hi>.8h
	mul V<b1_r_n0_mred>.8h, V<b1_r_n0_mraw>.8h, v0.h[2]
	smlal V<b1_r_n0_lo>.4s, V<b1_r_n0_mred>.4h, v0.h[0]
	smlal2 V<b1_r_n0_hi>.4s, V<b1_r_n0_mred>.8h, v0.h[0]
	uzp2 V<b1_n0>.8h, V<b1_r_n0_lo>.8h, V<b1_r_n0_hi>.8h
	smull V<b1_r_n1_lo>.4s, V<b1_a3>.4h, V<b1_t2>.4h
	smull2 V<b1_r_n1_hi>.4s, V<b1_a3>.8h, V<b1_t2>.8h
	smlal V<b1_r_n1_lo>.4s, V<b1_a1>.4h, V<b1_t0>.4h
	smlal2 V<b1_r_n1_hi>.4s, V<b1_a1>.8h, V<b1_t0>.8h
	uzp1 V<b1_r_n1_mraw>.8h, V<b1_r_n1_lo>.8h, V<b1_r_n1_hi>.8h
	mul V<b1_r_n1_mred>.8h, V<b1_r_n1_mraw>.8h, v0.h[2]
	smlal V<b1_r_n1_lo>.4s, V<b1_r_n1_mred>.4h, v0.h[0]
	smlal2 V<b1_r_n1_hi>.4s, V<b1_r_n1_mred>.8h, v0.h[0]
	uzp2 V<b1_n1>.8h, V<b1_r_n1_lo>.8h, V<b1_r_n1_hi>.8h
	smull V<b1_r_n2_lo>.4s, V<b1_a2>.4h, V<b1_t0>.4h
	smull2 V<b1_r_n2_hi>.4s, V<b1_a2>.8h, V<b1_t0>.8h
	smlal V<b1_r_n2_lo>.4s, V<b1_a0>.4h, V<b1_t1>.4h
	smlal2 V<b1_r_n2_hi>.4s, V<b1_a0>.8h, V<b1_t1>.8h
	uzp1 V<b1_r_n2_mraw>.8h, V<b1_r_n2_lo>.8h, V<b1_r_n2_hi>.8h
	mul V<b1_r_n2_mred>.8h, V<b1_r_n2_mraw>.8h, v0.h[2]
	smlal V<b1_r_n2_lo>.4s, V<b1_r_n2_mred>.4h, v0.h[0]
	smlal2 V<b1_r_n2_hi>.4s, V<b1_r_n2_mred>.8h, v0.h[0]
	uzp2 V<b1_n2>.8h, V<b1_r_n2_lo>.8h, V<b1_r_n2_hi>.8h
	smull V<b1_r_n3_lo>.4s, V<b1_a1>.4h, V<b1_t1>.4h
	smull2 V<b1_r_n3_hi>.4s, V<b1_a1>.8h, V<b1_t1>.8h
	smlal V<b1_r_n3_lo>.4s, V<b1_a3>.4h, V<b1_t0>.4h
	smlal2 V<b1_r_n3_hi>.4s, V<b1_a3>.8h, V<b1_t0>.8h
	uzp1 V<b1_r_n3_mraw>.8h, V<b1_r_n3_lo>.8h, V<b1_r_n3_hi>.8h
	mul V<b1_r_n3_mred>.8h, V<b1_r_n3_mraw>.8h, v0.h[2]
	smlal V<b1_r_n3_lo>.4s, V<b1_r_n3_mred>.4h, v0.h[0]
	smlal2 V<b1_r_n3_hi>.4s, V<b1_r_n3_mred>.8h, v0.h[0]
	uzp2 V<b1_n3>.8h, V<b1_r_n3_lo>.8h, V<b1_r_n3_hi>.8h
	st4 {V<b1_n0>.8h, V<b1_n1>.8h, V<b1_n2>.8h, V<b1_n3>.8h}, [x0], #64

	smull V<c01_r_lo>.4s, V<b0_den>.4h, V<b1_den>.4h
	smull2 V<c01_r_hi>.4s, V<b0_den>.8h, V<b1_den>.8h
	uzp1 V<c01_r_mraw>.8h, V<c01_r_lo>.8h, V<c01_r_hi>.8h
	mul V<c01_r_mred>.8h, V<c01_r_mraw>.8h, v0.h[2]
	smlal V<c01_r_lo>.4s, V<c01_r_mred>.4h, v0.h[0]
	smlal2 V<c01_r_hi>.4s, V<c01_r_mred>.8h, v0.h[0]
	uzp2 V<c01>.8h, V<c01_r_lo>.8h, V<c01_r_hi>.8h
	stp Q<b0_den>, Q<b1_den>, [x1], #32
slothy_end_gt_baseinv_prepare2_phase01:

// Live-in: x0-x5, fixed v0, and Q<c01> from phase 01.
// Live-out: exact final stores and x0-x5 group pointer advances.
// Range: current GT baseinv int16 inputs, int32 products, exact int16 outputs.
// Reserved physical registers: x6-x30, sp, and fixed vector v0.
// The loads define Q<b2_zeta> Q<b2_a0> Q<b2_a1> Q<b2_a2> Q<b2_a3>.
slothy_start_gt_baseinv_prepare2_phase2:
	ldr Q<b2_zeta>, [x5], #16
	ld4 {V<b2_a0>.8h, V<b2_a1>.8h, V<b2_a2>.8h, V<b2_a3>.8h}, [x4], #64
	movi V<zero2>.8h, #0
	// Block 2: closed-form quartic prepare
	sub V<b2_neg_a2>.8h, V<zero2>.8h, V<b2_a2>.8h
	sub V<b2_neg_a3>.8h, V<zero2>.8h, V<b2_a3>.8h
	add V<b2_neg2a2>.8h, V<b2_neg_a2>.8h, V<b2_neg_a2>.8h
	add V<b2_neg2a3>.8h, V<b2_neg_a3>.8h, V<b2_neg_a3>.8h
	smull V<b2_r_t0a_lo>.4s, V<b2_a2>.4h, V<b2_a2>.4h
	smull2 V<b2_r_t0a_hi>.4s, V<b2_a2>.8h, V<b2_a2>.8h
	smlal V<b2_r_t0a_lo>.4s, V<b2_a1>.4h, V<b2_neg2a3>.4h
	smlal2 V<b2_r_t0a_hi>.4s, V<b2_a1>.8h, V<b2_neg2a3>.8h
	uzp1 V<b2_r_t0a_mraw>.8h, V<b2_r_t0a_lo>.8h, V<b2_r_t0a_hi>.8h
	mul V<b2_r_t0a_mred>.8h, V<b2_r_t0a_mraw>.8h, v0.h[2]
	smlal V<b2_r_t0a_lo>.4s, V<b2_r_t0a_mred>.4h, v0.h[0]
	smlal2 V<b2_r_t0a_hi>.4s, V<b2_r_t0a_mred>.8h, v0.h[0]
	uzp2 V<b2_t0a>.8h, V<b2_r_t0a_lo>.8h, V<b2_r_t0a_hi>.8h
	smull V<b2_r_t1a_lo>.4s, V<b2_a3>.4h, V<b2_a3>.4h
	smull2 V<b2_r_t1a_hi>.4s, V<b2_a3>.8h, V<b2_a3>.8h
	uzp1 V<b2_r_t1a_mraw>.8h, V<b2_r_t1a_lo>.8h, V<b2_r_t1a_hi>.8h
	mul V<b2_r_t1a_mred>.8h, V<b2_r_t1a_mraw>.8h, v0.h[2]
	smlal V<b2_r_t1a_lo>.4s, V<b2_r_t1a_mred>.4h, v0.h[0]
	smlal2 V<b2_r_t1a_hi>.4s, V<b2_r_t1a_mred>.8h, v0.h[0]
	uzp2 V<b2_t1a>.8h, V<b2_r_t1a_lo>.8h, V<b2_r_t1a_hi>.8h
	smull V<b2_r_t0_lo>.4s, V<b2_t0a>.4h, V<b2_zeta>.4h
	smull2 V<b2_r_t0_hi>.4s, V<b2_t0a>.8h, V<b2_zeta>.8h
	smlal V<b2_r_t0_lo>.4s, V<b2_a0>.4h, V<b2_a0>.4h
	smlal2 V<b2_r_t0_hi>.4s, V<b2_a0>.8h, V<b2_a0>.8h
	uzp1 V<b2_r_t0_mraw>.8h, V<b2_r_t0_lo>.8h, V<b2_r_t0_hi>.8h
	mul V<b2_r_t0_mred>.8h, V<b2_r_t0_mraw>.8h, v0.h[2]
	smlal V<b2_r_t0_lo>.4s, V<b2_r_t0_mred>.4h, v0.h[0]
	smlal2 V<b2_r_t0_hi>.4s, V<b2_r_t0_mred>.8h, v0.h[0]
	uzp2 V<b2_t0>.8h, V<b2_r_t0_lo>.8h, V<b2_r_t0_hi>.8h
	smull V<b2_r_t1_lo>.4s, V<b2_t1a>.4h, V<b2_zeta>.4h
	smull2 V<b2_r_t1_hi>.4s, V<b2_t1a>.8h, V<b2_zeta>.8h
	smlal V<b2_r_t1_lo>.4s, V<b2_a1>.4h, V<b2_a1>.4h
	smlal2 V<b2_r_t1_hi>.4s, V<b2_a1>.8h, V<b2_a1>.8h
	smlal V<b2_r_t1_lo>.4s, V<b2_a0>.4h, V<b2_neg2a2>.4h
	smlal2 V<b2_r_t1_hi>.4s, V<b2_a0>.8h, V<b2_neg2a2>.8h
	uzp1 V<b2_r_t1_mraw>.8h, V<b2_r_t1_lo>.8h, V<b2_r_t1_hi>.8h
	mul V<b2_r_t1_mred>.8h, V<b2_r_t1_mraw>.8h, v0.h[2]
	smlal V<b2_r_t1_lo>.4s, V<b2_r_t1_mred>.4h, v0.h[0]
	smlal2 V<b2_r_t1_hi>.4s, V<b2_r_t1_mred>.8h, v0.h[0]
	uzp2 V<b2_t1>.8h, V<b2_r_t1_lo>.8h, V<b2_r_t1_hi>.8h
	smull V<b2_r_t2_lo>.4s, V<b2_t1>.4h, V<b2_zeta>.4h
	smull2 V<b2_r_t2_hi>.4s, V<b2_t1>.8h, V<b2_zeta>.8h
	uzp1 V<b2_r_t2_mraw>.8h, V<b2_r_t2_lo>.8h, V<b2_r_t2_hi>.8h
	mul V<b2_r_t2_mred>.8h, V<b2_r_t2_mraw>.8h, v0.h[2]
	smlal V<b2_r_t2_lo>.4s, V<b2_r_t2_mred>.4h, v0.h[0]
	smlal2 V<b2_r_t2_hi>.4s, V<b2_r_t2_mred>.8h, v0.h[0]
	uzp2 V<b2_t2>.8h, V<b2_r_t2_lo>.8h, V<b2_r_t2_hi>.8h
	sub V<b2_negt1>.8h, V<zero2>.8h, V<b2_t1>.8h
	smull V<b2_r_den_lo>.4s, V<b2_t0>.4h, V<b2_t0>.4h
	smull2 V<b2_r_den_hi>.4s, V<b2_t0>.8h, V<b2_t0>.8h
	smlal V<b2_r_den_lo>.4s, V<b2_negt1>.4h, V<b2_t2>.4h
	smlal2 V<b2_r_den_hi>.4s, V<b2_negt1>.8h, V<b2_t2>.8h
	uzp1 V<b2_r_den_mraw>.8h, V<b2_r_den_lo>.8h, V<b2_r_den_hi>.8h
	mul V<b2_r_den_mred>.8h, V<b2_r_den_mraw>.8h, v0.h[2]
	smlal V<b2_r_den_lo>.4s, V<b2_r_den_mred>.4h, v0.h[0]
	smlal2 V<b2_r_den_hi>.4s, V<b2_r_den_mred>.8h, v0.h[0]
	uzp2 V<b2_den>.8h, V<b2_r_den_lo>.8h, V<b2_r_den_hi>.8h
	smull V<b2_r_n0_lo>.4s, V<b2_a0>.4h, V<b2_t0>.4h
	smull2 V<b2_r_n0_hi>.4s, V<b2_a0>.8h, V<b2_t0>.8h
	smlal V<b2_r_n0_lo>.4s, V<b2_a2>.4h, V<b2_t2>.4h
	smlal2 V<b2_r_n0_hi>.4s, V<b2_a2>.8h, V<b2_t2>.8h
	uzp1 V<b2_r_n0_mraw>.8h, V<b2_r_n0_lo>.8h, V<b2_r_n0_hi>.8h
	mul V<b2_r_n0_mred>.8h, V<b2_r_n0_mraw>.8h, v0.h[2]
	smlal V<b2_r_n0_lo>.4s, V<b2_r_n0_mred>.4h, v0.h[0]
	smlal2 V<b2_r_n0_hi>.4s, V<b2_r_n0_mred>.8h, v0.h[0]
	uzp2 V<b2_n0>.8h, V<b2_r_n0_lo>.8h, V<b2_r_n0_hi>.8h
	smull V<b2_r_n1_lo>.4s, V<b2_a3>.4h, V<b2_t2>.4h
	smull2 V<b2_r_n1_hi>.4s, V<b2_a3>.8h, V<b2_t2>.8h
	smlal V<b2_r_n1_lo>.4s, V<b2_a1>.4h, V<b2_t0>.4h
	smlal2 V<b2_r_n1_hi>.4s, V<b2_a1>.8h, V<b2_t0>.8h
	uzp1 V<b2_r_n1_mraw>.8h, V<b2_r_n1_lo>.8h, V<b2_r_n1_hi>.8h
	mul V<b2_r_n1_mred>.8h, V<b2_r_n1_mraw>.8h, v0.h[2]
	smlal V<b2_r_n1_lo>.4s, V<b2_r_n1_mred>.4h, v0.h[0]
	smlal2 V<b2_r_n1_hi>.4s, V<b2_r_n1_mred>.8h, v0.h[0]
	uzp2 V<b2_n1>.8h, V<b2_r_n1_lo>.8h, V<b2_r_n1_hi>.8h
	smull V<b2_r_n2_lo>.4s, V<b2_a2>.4h, V<b2_t0>.4h
	smull2 V<b2_r_n2_hi>.4s, V<b2_a2>.8h, V<b2_t0>.8h
	smlal V<b2_r_n2_lo>.4s, V<b2_a0>.4h, V<b2_t1>.4h
	smlal2 V<b2_r_n2_hi>.4s, V<b2_a0>.8h, V<b2_t1>.8h
	uzp1 V<b2_r_n2_mraw>.8h, V<b2_r_n2_lo>.8h, V<b2_r_n2_hi>.8h
	mul V<b2_r_n2_mred>.8h, V<b2_r_n2_mraw>.8h, v0.h[2]
	smlal V<b2_r_n2_lo>.4s, V<b2_r_n2_mred>.4h, v0.h[0]
	smlal2 V<b2_r_n2_hi>.4s, V<b2_r_n2_mred>.8h, v0.h[0]
	uzp2 V<b2_n2>.8h, V<b2_r_n2_lo>.8h, V<b2_r_n2_hi>.8h
	smull V<b2_r_n3_lo>.4s, V<b2_a1>.4h, V<b2_t1>.4h
	smull2 V<b2_r_n3_hi>.4s, V<b2_a1>.8h, V<b2_t1>.8h
	smlal V<b2_r_n3_lo>.4s, V<b2_a3>.4h, V<b2_t0>.4h
	smlal2 V<b2_r_n3_hi>.4s, V<b2_a3>.8h, V<b2_t0>.8h
	uzp1 V<b2_r_n3_mraw>.8h, V<b2_r_n3_lo>.8h, V<b2_r_n3_hi>.8h
	mul V<b2_r_n3_mred>.8h, V<b2_r_n3_mraw>.8h, v0.h[2]
	smlal V<b2_r_n3_lo>.4s, V<b2_r_n3_mred>.4h, v0.h[0]
	smlal2 V<b2_r_n3_hi>.4s, V<b2_r_n3_mred>.8h, v0.h[0]
	uzp2 V<b2_n3>.8h, V<b2_r_n3_lo>.8h, V<b2_r_n3_hi>.8h
	st4 {V<b2_n0>.8h, V<b2_n1>.8h, V<b2_n2>.8h, V<b2_n3>.8h}, [x0], #64

	smull V<group_r_lo>.4s, V<c01>.4h, V<b2_den>.4h
	smull2 V<group_r_hi>.4s, V<c01>.8h, V<b2_den>.8h
	uzp1 V<group_r_mraw>.8h, V<group_r_lo>.8h, V<group_r_hi>.8h
	mul V<group_r_mred>.8h, V<group_r_mraw>.8h, v0.h[2]
	smlal V<group_r_lo>.4s, V<group_r_mred>.4h, v0.h[0]
	smlal2 V<group_r_hi>.4s, V<group_r_mred>.8h, v0.h[0]
	uzp2 V<group_product>.8h, V<group_r_lo>.8h, V<group_r_hi>.8h
	str Q<b2_den>, [x1], #16
	str Q<c01>, [x2], #16
	str Q<group_product>, [x3], #16
slothy_end_gt_baseinv_prepare2_phase2:
slothy_end_gt_baseinv_prepare2_group:
