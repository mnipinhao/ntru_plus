// Kernel: ntruplus768_gt_tmvp_candidate_a_tmvp_batch8
// Scheme: NTRU+768
// Platform: AArch64 Neon
// Scope: one public Candidate A TMVP product batch.
//
// Input representation:
//   x1/x2 point at rowpack stage4 lane0, k32 = 0 or 16, for one
//   (branch,row,kpair-block).  Four quartic lanes are separated by 64 bytes.
//
// Output representation:
//   x0 points at the corresponding rowpack output batch.  The stores are
//   interleaved [ce+co, ce-co] for eight even/odd pairs and four quartic lanes.
//
// This is symbolic source for Slothy handoff.  It is not allocated or optimized.

.text
.align 4
.global ntruplus768_gt_tmvp_candidate_a_tmvp_batch8
.global _ntruplus768_gt_tmvp_candidate_a_tmvp_batch8
#ifndef __APPLE__
.type ntruplus768_gt_tmvp_candidate_a_tmvp_batch8, %function
#endif

ntruplus768_gt_tmvp_candidate_a_tmvp_batch8:
_ntruplus768_gt_tmvp_candidate_a_tmvp_batch8:
    // ABI:
    // x0 = output rowpack batch base
    // x1 = a stage4 rowpack batch base
    // x2 = b stage4 rowpack batch base
    // x3 = constants: base, stage5 twiddle/pre, lambda_even, lambda_odd

    // live-in: x0 output pointer, x1 a pointer, x2 b pointer, x3 const pointer
    // live-out: rowpack stores at x0 lane offsets 0,64,128,192
    // range: stage4 inputs [-1728,1728], materialized stage5 observed within [-3435,3435]
    // reserved physical registers: x18-x30, sp; no fixed vector registers
slothy_start_ntruplus768_gt_tmvp_candidate_a_tmvp_batch8:
    ldr     Q<c_base>,      [x3, #0]
    ldr     Q<c_s5_tw>,     [x3, #16]
    ldr     Q<c_s5_pre>,    [x3, #32]
    ldr     Q<c_lam_even>,  [x3, #48]
    ldr     Q<c_lam_odd>,   [x3, #64]

    ldr     Q<a0_raw0>, [x1, #0]
    ldr     Q<a0_raw1>, [x1, #16]
    ldr     Q<a1_raw0>, [x1, #64]
    ldr     Q<a1_raw1>, [x1, #80]
    ldr     Q<a2_raw0>, [x1, #128]
    ldr     Q<a2_raw1>, [x1, #144]
    ldr     Q<a3_raw0>, [x1, #192]
    ldr     Q<a3_raw1>, [x1, #208]

    ldr     Q<b0_raw0>, [x2, #0]
    ldr     Q<b0_raw1>, [x2, #16]
    ldr     Q<b1_raw0>, [x2, #64]
    ldr     Q<b1_raw1>, [x2, #80]
    ldr     Q<b2_raw0>, [x2, #128]
    ldr     Q<b2_raw1>, [x2, #144]
    ldr     Q<b3_raw0>, [x2, #192]
    ldr     Q<b3_raw1>, [x2, #208]

    uzp1    V<a0e>.8h, V<a0_raw0>.8h, V<a0_raw1>.8h
    uzp2    V<a0o>.8h, V<a0_raw0>.8h, V<a0_raw1>.8h
    uzp1    V<a1e>.8h, V<a1_raw0>.8h, V<a1_raw1>.8h
    uzp2    V<a1o>.8h, V<a1_raw0>.8h, V<a1_raw1>.8h
    uzp1    V<a2e>.8h, V<a2_raw0>.8h, V<a2_raw1>.8h
    uzp2    V<a2o>.8h, V<a2_raw0>.8h, V<a2_raw1>.8h
    uzp1    V<a3e>.8h, V<a3_raw0>.8h, V<a3_raw1>.8h
    uzp2    V<a3o>.8h, V<a3_raw0>.8h, V<a3_raw1>.8h

    uzp1    V<b0e>.8h, V<b0_raw0>.8h, V<b0_raw1>.8h
    uzp2    V<b0o>.8h, V<b0_raw0>.8h, V<b0_raw1>.8h
    uzp1    V<b1e>.8h, V<b1_raw0>.8h, V<b1_raw1>.8h
    uzp2    V<b1o>.8h, V<b1_raw0>.8h, V<b1_raw1>.8h
    uzp1    V<b2e>.8h, V<b2_raw0>.8h, V<b2_raw1>.8h
    uzp2    V<b2o>.8h, V<b2_raw0>.8h, V<b2_raw1>.8h
    uzp1    V<b3e>.8h, V<b3_raw0>.8h, V<b3_raw1>.8h
    uzp2    V<b3o>.8h, V<b3_raw0>.8h, V<b3_raw1>.8h

    sqrdmulh V<a0w_q>.8h, V<a0o>.8h, V<c_s5_pre>.8h
    mul      V<a0w>.8h,   V<a0o>.8h, V<c_s5_tw>.8h
    mls      V<a0w>.8h,   V<a0w_q>.8h, V<c_base>.h[0]
    add      V<ae0>.8h,   V<a0e>.8h, V<a0w>.8h
    sub      V<ao0>.8h,   V<a0e>.8h, V<a0w>.8h

    sqrdmulh V<a1w_q>.8h, V<a1o>.8h, V<c_s5_pre>.8h
    mul      V<a1w>.8h,   V<a1o>.8h, V<c_s5_tw>.8h
    mls      V<a1w>.8h,   V<a1w_q>.8h, V<c_base>.h[0]
    add      V<ae1>.8h,   V<a1e>.8h, V<a1w>.8h
    sub      V<ao1>.8h,   V<a1e>.8h, V<a1w>.8h

    sqrdmulh V<a2w_q>.8h, V<a2o>.8h, V<c_s5_pre>.8h
    mul      V<a2w>.8h,   V<a2o>.8h, V<c_s5_tw>.8h
    mls      V<a2w>.8h,   V<a2w_q>.8h, V<c_base>.h[0]
    add      V<ae2>.8h,   V<a2e>.8h, V<a2w>.8h
    sub      V<ao2>.8h,   V<a2e>.8h, V<a2w>.8h

    sqrdmulh V<a3w_q>.8h, V<a3o>.8h, V<c_s5_pre>.8h
    mul      V<a3w>.8h,   V<a3o>.8h, V<c_s5_tw>.8h
    mls      V<a3w>.8h,   V<a3w_q>.8h, V<c_base>.h[0]
    add      V<ae3>.8h,   V<a3e>.8h, V<a3w>.8h
    sub      V<ao3>.8h,   V<a3e>.8h, V<a3w>.8h

    sqrdmulh V<b0w_q>.8h, V<b0o>.8h, V<c_s5_pre>.8h
    mul      V<b0w>.8h,   V<b0o>.8h, V<c_s5_tw>.8h
    mls      V<b0w>.8h,   V<b0w_q>.8h, V<c_base>.h[0]
    add      V<be0>.8h,   V<b0e>.8h, V<b0w>.8h
    sub      V<bo0>.8h,   V<b0e>.8h, V<b0w>.8h

    sqrdmulh V<b1w_q>.8h, V<b1o>.8h, V<c_s5_pre>.8h
    mul      V<b1w>.8h,   V<b1o>.8h, V<c_s5_tw>.8h
    mls      V<b1w>.8h,   V<b1w_q>.8h, V<c_base>.h[0]
    add      V<be1>.8h,   V<b1e>.8h, V<b1w>.8h
    sub      V<bo1>.8h,   V<b1e>.8h, V<b1w>.8h

    sqrdmulh V<b2w_q>.8h, V<b2o>.8h, V<c_s5_pre>.8h
    mul      V<b2w>.8h,   V<b2o>.8h, V<c_s5_tw>.8h
    mls      V<b2w>.8h,   V<b2w_q>.8h, V<c_base>.h[0]
    add      V<be2>.8h,   V<b2e>.8h, V<b2w>.8h
    sub      V<bo2>.8h,   V<b2e>.8h, V<b2w>.8h

    sqrdmulh V<b3w_q>.8h, V<b3o>.8h, V<c_s5_pre>.8h
    mul      V<b3w>.8h,   V<b3o>.8h, V<c_s5_tw>.8h
    mls      V<b3w>.8h,   V<b3w_q>.8h, V<c_base>.h[0]
    add      V<be3>.8h,   V<b3e>.8h, V<b3w>.8h
    sub      V<bo3>.8h,   V<b3e>.8h, V<b3w>.8h

    smull    V<e_acc0_l>.4s, V<ae1>.4h, V<be3>.4h
    smull2   V<e_acc0_h>.4s, V<ae1>.8h, V<be3>.8h
    smlal    V<e_acc0_l>.4s, V<ae2>.4h, V<be2>.4h
    smlal2   V<e_acc0_h>.4s, V<ae2>.8h, V<be2>.8h
    smlal    V<e_acc0_l>.4s, V<ae3>.4h, V<be1>.4h
    smlal2   V<e_acc0_h>.4s, V<ae3>.8h, V<be1>.8h

    smull    V<e_acc1_l>.4s, V<ae2>.4h, V<be3>.4h
    smull2   V<e_acc1_h>.4s, V<ae2>.8h, V<be3>.8h
    smlal    V<e_acc1_l>.4s, V<ae3>.4h, V<be2>.4h
    smlal2   V<e_acc1_h>.4s, V<ae3>.8h, V<be2>.8h

    smull    V<e_acc2_l>.4s, V<ae3>.4h, V<be3>.4h
    smull2   V<e_acc2_h>.4s, V<ae3>.8h, V<be3>.8h

    uzp1     V<e_q0>.8h, V<e_acc0_l>.8h, V<e_acc0_h>.8h
    uzp1     V<e_q1>.8h, V<e_acc1_l>.8h, V<e_acc1_h>.8h
    uzp1     V<e_q2>.8h, V<e_acc2_l>.8h, V<e_acc2_h>.8h
    mul      V<e_q0>.8h, V<e_q0>.8h, V<c_base>.h[2]
    mul      V<e_q1>.8h, V<e_q1>.8h, V<c_base>.h[2]
    mul      V<e_q2>.8h, V<e_q2>.8h, V<c_base>.h[2]
    smlal    V<e_acc0_l>.4s, V<e_q0>.4h, V<c_base>.h[0]
    smlal2   V<e_acc0_h>.4s, V<e_q0>.8h, V<c_base>.h[0]
    smlal    V<e_acc1_l>.4s, V<e_q1>.4h, V<c_base>.h[0]
    smlal2   V<e_acc1_h>.4s, V<e_q1>.8h, V<c_base>.h[0]
    smlal    V<e_acc2_l>.4s, V<e_q2>.4h, V<c_base>.h[0]
    smlal2   V<e_acc2_h>.4s, V<e_q2>.8h, V<c_base>.h[0]
    uzp2     V<e_red0>.8h, V<e_acc0_l>.8h, V<e_acc0_h>.8h
    uzp2     V<e_red1>.8h, V<e_acc1_l>.8h, V<e_acc1_h>.8h
    uzp2     V<e_red2>.8h, V<e_acc2_l>.8h, V<e_acc2_h>.8h

    smull    V<e_r3_l>.4s, V<ae3>.4h, V<be0>.4h
    smull2   V<e_r3_h>.4s, V<ae3>.8h, V<be0>.8h
    smlal    V<e_r3_l>.4s, V<ae0>.4h, V<be3>.4h
    smlal2   V<e_r3_h>.4s, V<ae0>.8h, V<be3>.8h
    smlal    V<e_r3_l>.4s, V<ae1>.4h, V<be2>.4h
    smlal2   V<e_r3_h>.4s, V<ae1>.8h, V<be2>.8h
    smlal    V<e_r3_l>.4s, V<ae2>.4h, V<be1>.4h
    smlal2   V<e_r3_h>.4s, V<ae2>.8h, V<be1>.8h

    smull    V<e_r2_l>.4s, V<e_red2>.4h, V<c_lam_even>.4h
    smull2   V<e_r2_h>.4s, V<e_red2>.8h, V<c_lam_even>.8h
    smlal    V<e_r2_l>.4s, V<ae0>.4h, V<be2>.4h
    smlal2   V<e_r2_h>.4s, V<ae0>.8h, V<be2>.8h
    smlal    V<e_r2_l>.4s, V<ae1>.4h, V<be1>.4h
    smlal2   V<e_r2_h>.4s, V<ae1>.8h, V<be1>.8h
    smlal    V<e_r2_l>.4s, V<ae2>.4h, V<be0>.4h
    smlal2   V<e_r2_h>.4s, V<ae2>.8h, V<be0>.8h

    smull    V<e_r1_l>.4s, V<e_red1>.4h, V<c_lam_even>.4h
    smull2   V<e_r1_h>.4s, V<e_red1>.8h, V<c_lam_even>.8h
    smlal    V<e_r1_l>.4s, V<ae0>.4h, V<be1>.4h
    smlal2   V<e_r1_h>.4s, V<ae0>.8h, V<be1>.8h
    smlal    V<e_r1_l>.4s, V<ae1>.4h, V<be0>.4h
    smlal2   V<e_r1_h>.4s, V<ae1>.8h, V<be0>.8h

    smull    V<e_r0_l>.4s, V<e_red0>.4h, V<c_lam_even>.4h
    smull2   V<e_r0_h>.4s, V<e_red0>.8h, V<c_lam_even>.8h
    smlal    V<e_r0_l>.4s, V<ae0>.4h, V<be0>.4h
    smlal2   V<e_r0_h>.4s, V<ae0>.8h, V<be0>.8h

    uzp1     V<e_qr0>.8h, V<e_r0_l>.8h, V<e_r0_h>.8h
    uzp1     V<e_qr1>.8h, V<e_r1_l>.8h, V<e_r1_h>.8h
    uzp1     V<e_qr2>.8h, V<e_r2_l>.8h, V<e_r2_h>.8h
    uzp1     V<e_qr3>.8h, V<e_r3_l>.8h, V<e_r3_h>.8h
    mul      V<e_qr0>.8h, V<e_qr0>.8h, V<c_base>.h[2]
    mul      V<e_qr1>.8h, V<e_qr1>.8h, V<c_base>.h[2]
    mul      V<e_qr2>.8h, V<e_qr2>.8h, V<c_base>.h[2]
    mul      V<e_qr3>.8h, V<e_qr3>.8h, V<c_base>.h[2]
    smlal    V<e_r0_l>.4s, V<e_qr0>.4h, V<c_base>.h[0]
    smlal2   V<e_r0_h>.4s, V<e_qr0>.8h, V<c_base>.h[0]
    smlal    V<e_r1_l>.4s, V<e_qr1>.4h, V<c_base>.h[0]
    smlal2   V<e_r1_h>.4s, V<e_qr1>.8h, V<c_base>.h[0]
    smlal    V<e_r2_l>.4s, V<e_qr2>.4h, V<c_base>.h[0]
    smlal2   V<e_r2_h>.4s, V<e_qr2>.8h, V<c_base>.h[0]
    smlal    V<e_r3_l>.4s, V<e_qr3>.4h, V<c_base>.h[0]
    smlal2   V<e_r3_h>.4s, V<e_qr3>.8h, V<c_base>.h[0]
    uzp2     V<er0>.8h, V<e_r0_l>.8h, V<e_r0_h>.8h
    uzp2     V<er1>.8h, V<e_r1_l>.8h, V<e_r1_h>.8h
    uzp2     V<er2>.8h, V<e_r2_l>.8h, V<e_r2_h>.8h
    uzp2     V<er3>.8h, V<e_r3_l>.8h, V<e_r3_h>.8h

    smull    V<er0_rsq_l>.4s, V<er0>.4h, V<c_base>.h[3]
    smull2   V<er0_rsq_h>.4s, V<er0>.8h, V<c_base>.h[3]
    smull    V<er1_rsq_l>.4s, V<er1>.4h, V<c_base>.h[3]
    smull2   V<er1_rsq_h>.4s, V<er1>.8h, V<c_base>.h[3]
    smull    V<er2_rsq_l>.4s, V<er2>.4h, V<c_base>.h[3]
    smull2   V<er2_rsq_h>.4s, V<er2>.8h, V<c_base>.h[3]
    smull    V<er3_rsq_l>.4s, V<er3>.4h, V<c_base>.h[3]
    smull2   V<er3_rsq_h>.4s, V<er3>.8h, V<c_base>.h[3]
    uzp1     V<er0_rsq_q>.8h, V<er0_rsq_l>.8h, V<er0_rsq_h>.8h
    uzp1     V<er1_rsq_q>.8h, V<er1_rsq_l>.8h, V<er1_rsq_h>.8h
    uzp1     V<er2_rsq_q>.8h, V<er2_rsq_l>.8h, V<er2_rsq_h>.8h
    uzp1     V<er3_rsq_q>.8h, V<er3_rsq_l>.8h, V<er3_rsq_h>.8h
    mul      V<er0_rsq_q>.8h, V<er0_rsq_q>.8h, V<c_base>.h[2]
    mul      V<er1_rsq_q>.8h, V<er1_rsq_q>.8h, V<c_base>.h[2]
    mul      V<er2_rsq_q>.8h, V<er2_rsq_q>.8h, V<c_base>.h[2]
    mul      V<er3_rsq_q>.8h, V<er3_rsq_q>.8h, V<c_base>.h[2]
    smlal    V<er0_rsq_l>.4s, V<er0_rsq_q>.4h, V<c_base>.h[0]
    smlal2   V<er0_rsq_h>.4s, V<er0_rsq_q>.8h, V<c_base>.h[0]
    smlal    V<er1_rsq_l>.4s, V<er1_rsq_q>.4h, V<c_base>.h[0]
    smlal2   V<er1_rsq_h>.4s, V<er1_rsq_q>.8h, V<c_base>.h[0]
    smlal    V<er2_rsq_l>.4s, V<er2_rsq_q>.4h, V<c_base>.h[0]
    smlal2   V<er2_rsq_h>.4s, V<er2_rsq_q>.8h, V<c_base>.h[0]
    smlal    V<er3_rsq_l>.4s, V<er3_rsq_q>.4h, V<c_base>.h[0]
    smlal2   V<er3_rsq_h>.4s, V<er3_rsq_q>.8h, V<c_base>.h[0]
    uzp2     V<er0n>.8h, V<er0_rsq_l>.8h, V<er0_rsq_h>.8h
    uzp2     V<er1n>.8h, V<er1_rsq_l>.8h, V<er1_rsq_h>.8h
    uzp2     V<er2n>.8h, V<er2_rsq_l>.8h, V<er2_rsq_h>.8h
    uzp2     V<er3n>.8h, V<er3_rsq_l>.8h, V<er3_rsq_h>.8h

    smull    V<o_acc0_l>.4s, V<ao1>.4h, V<bo3>.4h
    smull2   V<o_acc0_h>.4s, V<ao1>.8h, V<bo3>.8h
    smlal    V<o_acc0_l>.4s, V<ao2>.4h, V<bo2>.4h
    smlal2   V<o_acc0_h>.4s, V<ao2>.8h, V<bo2>.8h
    smlal    V<o_acc0_l>.4s, V<ao3>.4h, V<bo1>.4h
    smlal2   V<o_acc0_h>.4s, V<ao3>.8h, V<bo1>.8h

    smull    V<o_acc1_l>.4s, V<ao2>.4h, V<bo3>.4h
    smull2   V<o_acc1_h>.4s, V<ao2>.8h, V<bo3>.8h
    smlal    V<o_acc1_l>.4s, V<ao3>.4h, V<bo2>.4h
    smlal2   V<o_acc1_h>.4s, V<ao3>.8h, V<bo2>.8h

    smull    V<o_acc2_l>.4s, V<ao3>.4h, V<bo3>.4h
    smull2   V<o_acc2_h>.4s, V<ao3>.8h, V<bo3>.8h

    uzp1     V<o_q0>.8h, V<o_acc0_l>.8h, V<o_acc0_h>.8h
    uzp1     V<o_q1>.8h, V<o_acc1_l>.8h, V<o_acc1_h>.8h
    uzp1     V<o_q2>.8h, V<o_acc2_l>.8h, V<o_acc2_h>.8h
    mul      V<o_q0>.8h, V<o_q0>.8h, V<c_base>.h[2]
    mul      V<o_q1>.8h, V<o_q1>.8h, V<c_base>.h[2]
    mul      V<o_q2>.8h, V<o_q2>.8h, V<c_base>.h[2]
    smlal    V<o_acc0_l>.4s, V<o_q0>.4h, V<c_base>.h[0]
    smlal2   V<o_acc0_h>.4s, V<o_q0>.8h, V<c_base>.h[0]
    smlal    V<o_acc1_l>.4s, V<o_q1>.4h, V<c_base>.h[0]
    smlal2   V<o_acc1_h>.4s, V<o_q1>.8h, V<c_base>.h[0]
    smlal    V<o_acc2_l>.4s, V<o_q2>.4h, V<c_base>.h[0]
    smlal2   V<o_acc2_h>.4s, V<o_q2>.8h, V<c_base>.h[0]
    uzp2     V<o_red0>.8h, V<o_acc0_l>.8h, V<o_acc0_h>.8h
    uzp2     V<o_red1>.8h, V<o_acc1_l>.8h, V<o_acc1_h>.8h
    uzp2     V<o_red2>.8h, V<o_acc2_l>.8h, V<o_acc2_h>.8h

    smull    V<o_r3_l>.4s, V<ao3>.4h, V<bo0>.4h
    smull2   V<o_r3_h>.4s, V<ao3>.8h, V<bo0>.8h
    smlal    V<o_r3_l>.4s, V<ao0>.4h, V<bo3>.4h
    smlal2   V<o_r3_h>.4s, V<ao0>.8h, V<bo3>.8h
    smlal    V<o_r3_l>.4s, V<ao1>.4h, V<bo2>.4h
    smlal2   V<o_r3_h>.4s, V<ao1>.8h, V<bo2>.8h
    smlal    V<o_r3_l>.4s, V<ao2>.4h, V<bo1>.4h
    smlal2   V<o_r3_h>.4s, V<ao2>.8h, V<bo1>.8h

    smull    V<o_r2_l>.4s, V<o_red2>.4h, V<c_lam_odd>.4h
    smull2   V<o_r2_h>.4s, V<o_red2>.8h, V<c_lam_odd>.8h
    smlal    V<o_r2_l>.4s, V<ao0>.4h, V<bo2>.4h
    smlal2   V<o_r2_h>.4s, V<ao0>.8h, V<bo2>.8h
    smlal    V<o_r2_l>.4s, V<ao1>.4h, V<bo1>.4h
    smlal2   V<o_r2_h>.4s, V<ao1>.8h, V<bo1>.8h
    smlal    V<o_r2_l>.4s, V<ao2>.4h, V<bo0>.4h
    smlal2   V<o_r2_h>.4s, V<ao2>.8h, V<bo0>.8h

    smull    V<o_r1_l>.4s, V<o_red1>.4h, V<c_lam_odd>.4h
    smull2   V<o_r1_h>.4s, V<o_red1>.8h, V<c_lam_odd>.8h
    smlal    V<o_r1_l>.4s, V<ao0>.4h, V<bo1>.4h
    smlal2   V<o_r1_h>.4s, V<ao0>.8h, V<bo1>.8h
    smlal    V<o_r1_l>.4s, V<ao1>.4h, V<bo0>.4h
    smlal2   V<o_r1_h>.4s, V<ao1>.8h, V<bo0>.8h

    smull    V<o_r0_l>.4s, V<o_red0>.4h, V<c_lam_odd>.4h
    smull2   V<o_r0_h>.4s, V<o_red0>.8h, V<c_lam_odd>.8h
    smlal    V<o_r0_l>.4s, V<ao0>.4h, V<bo0>.4h
    smlal2   V<o_r0_h>.4s, V<ao0>.8h, V<bo0>.8h

    uzp1     V<o_qr0>.8h, V<o_r0_l>.8h, V<o_r0_h>.8h
    uzp1     V<o_qr1>.8h, V<o_r1_l>.8h, V<o_r1_h>.8h
    uzp1     V<o_qr2>.8h, V<o_r2_l>.8h, V<o_r2_h>.8h
    uzp1     V<o_qr3>.8h, V<o_r3_l>.8h, V<o_r3_h>.8h
    mul      V<o_qr0>.8h, V<o_qr0>.8h, V<c_base>.h[2]
    mul      V<o_qr1>.8h, V<o_qr1>.8h, V<c_base>.h[2]
    mul      V<o_qr2>.8h, V<o_qr2>.8h, V<c_base>.h[2]
    mul      V<o_qr3>.8h, V<o_qr3>.8h, V<c_base>.h[2]
    smlal    V<o_r0_l>.4s, V<o_qr0>.4h, V<c_base>.h[0]
    smlal2   V<o_r0_h>.4s, V<o_qr0>.8h, V<c_base>.h[0]
    smlal    V<o_r1_l>.4s, V<o_qr1>.4h, V<c_base>.h[0]
    smlal2   V<o_r1_h>.4s, V<o_qr1>.8h, V<c_base>.h[0]
    smlal    V<o_r2_l>.4s, V<o_qr2>.4h, V<c_base>.h[0]
    smlal2   V<o_r2_h>.4s, V<o_qr2>.8h, V<c_base>.h[0]
    smlal    V<o_r3_l>.4s, V<o_qr3>.4h, V<c_base>.h[0]
    smlal2   V<o_r3_h>.4s, V<o_qr3>.8h, V<c_base>.h[0]
    uzp2     V<or0>.8h, V<o_r0_l>.8h, V<o_r0_h>.8h
    uzp2     V<or1>.8h, V<o_r1_l>.8h, V<o_r1_h>.8h
    uzp2     V<or2>.8h, V<o_r2_l>.8h, V<o_r2_h>.8h
    uzp2     V<or3>.8h, V<o_r3_l>.8h, V<o_r3_h>.8h

    smull    V<or0_rsq_l>.4s, V<or0>.4h, V<c_base>.h[3]
    smull2   V<or0_rsq_h>.4s, V<or0>.8h, V<c_base>.h[3]
    smull    V<or1_rsq_l>.4s, V<or1>.4h, V<c_base>.h[3]
    smull2   V<or1_rsq_h>.4s, V<or1>.8h, V<c_base>.h[3]
    smull    V<or2_rsq_l>.4s, V<or2>.4h, V<c_base>.h[3]
    smull2   V<or2_rsq_h>.4s, V<or2>.8h, V<c_base>.h[3]
    smull    V<or3_rsq_l>.4s, V<or3>.4h, V<c_base>.h[3]
    smull2   V<or3_rsq_h>.4s, V<or3>.8h, V<c_base>.h[3]
    uzp1     V<or0_rsq_q>.8h, V<or0_rsq_l>.8h, V<or0_rsq_h>.8h
    uzp1     V<or1_rsq_q>.8h, V<or1_rsq_l>.8h, V<or1_rsq_h>.8h
    uzp1     V<or2_rsq_q>.8h, V<or2_rsq_l>.8h, V<or2_rsq_h>.8h
    uzp1     V<or3_rsq_q>.8h, V<or3_rsq_l>.8h, V<or3_rsq_h>.8h
    mul      V<or0_rsq_q>.8h, V<or0_rsq_q>.8h, V<c_base>.h[2]
    mul      V<or1_rsq_q>.8h, V<or1_rsq_q>.8h, V<c_base>.h[2]
    mul      V<or2_rsq_q>.8h, V<or2_rsq_q>.8h, V<c_base>.h[2]
    mul      V<or3_rsq_q>.8h, V<or3_rsq_q>.8h, V<c_base>.h[2]
    smlal    V<or0_rsq_l>.4s, V<or0_rsq_q>.4h, V<c_base>.h[0]
    smlal2   V<or0_rsq_h>.4s, V<or0_rsq_q>.8h, V<c_base>.h[0]
    smlal    V<or1_rsq_l>.4s, V<or1_rsq_q>.4h, V<c_base>.h[0]
    smlal2   V<or1_rsq_h>.4s, V<or1_rsq_q>.8h, V<c_base>.h[0]
    smlal    V<or2_rsq_l>.4s, V<or2_rsq_q>.4h, V<c_base>.h[0]
    smlal2   V<or2_rsq_h>.4s, V<or2_rsq_q>.8h, V<c_base>.h[0]
    smlal    V<or3_rsq_l>.4s, V<or3_rsq_q>.4h, V<c_base>.h[0]
    smlal2   V<or3_rsq_h>.4s, V<or3_rsq_q>.8h, V<c_base>.h[0]
    uzp2     V<or0n>.8h, V<or0_rsq_l>.8h, V<or0_rsq_h>.8h
    uzp2     V<or1n>.8h, V<or1_rsq_l>.8h, V<or1_rsq_h>.8h
    uzp2     V<or2n>.8h, V<or2_rsq_l>.8h, V<or2_rsq_h>.8h
    uzp2     V<or3n>.8h, V<or3_rsq_l>.8h, V<or3_rsq_h>.8h

    add      V<out0_even>.8h, V<er0n>.8h, V<or0n>.8h
    sub      V<out0_odd>.8h,  V<er0n>.8h, V<or0n>.8h
    add      V<out1_even>.8h, V<er1n>.8h, V<or1n>.8h
    sub      V<out1_odd>.8h,  V<er1n>.8h, V<or1n>.8h
    add      V<out2_even>.8h, V<er2n>.8h, V<or2n>.8h
    sub      V<out2_odd>.8h,  V<er2n>.8h, V<or2n>.8h
    add      V<out3_even>.8h, V<er3n>.8h, V<or3n>.8h
    sub      V<out3_odd>.8h,  V<er3n>.8h, V<or3n>.8h

    zip1     V<out0_lo>.8h, V<out0_even>.8h, V<out0_odd>.8h
    zip2     V<out0_hi>.8h, V<out0_even>.8h, V<out0_odd>.8h
    zip1     V<out1_lo>.8h, V<out1_even>.8h, V<out1_odd>.8h
    zip2     V<out1_hi>.8h, V<out1_even>.8h, V<out1_odd>.8h
    zip1     V<out2_lo>.8h, V<out2_even>.8h, V<out2_odd>.8h
    zip2     V<out2_hi>.8h, V<out2_even>.8h, V<out2_odd>.8h
    zip1     V<out3_lo>.8h, V<out3_even>.8h, V<out3_odd>.8h
    zip2     V<out3_hi>.8h, V<out3_even>.8h, V<out3_odd>.8h

    str      Q<out0_lo>, [x0, #0]
    str      Q<out0_hi>, [x0, #16]
    str      Q<out1_lo>, [x0, #64]
    str      Q<out1_hi>, [x0, #80]
    str      Q<out2_lo>, [x0, #128]
    str      Q<out2_hi>, [x0, #144]
    str      Q<out3_lo>, [x0, #192]
    str      Q<out3_hi>, [x0, #208]
slothy_end_ntruplus768_gt_tmvp_candidate_a_tmvp_batch8:
    ret

#ifndef __APPLE__
.size ntruplus768_gt_tmvp_candidate_a_tmvp_batch8, .-ntruplus768_gt_tmvp_candidate_a_tmvp_batch8
#endif
