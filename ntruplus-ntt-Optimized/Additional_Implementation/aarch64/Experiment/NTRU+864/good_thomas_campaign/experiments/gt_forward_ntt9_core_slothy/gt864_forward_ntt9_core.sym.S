/* M5I: complete paper-oriented NTT9 core over one already-twisted block. */
// live-in: f0, f1, f2, f3, f4, f5, f6, f7, f8, roots, modq
// live-out: out0, out1, out2, out3, out4, out5, out6, out7, out8
// preserved pressure: the other nine-vector column block is reserved by driver
// roots.h[0..7]: rho,rho',rho2,rho2',eta,eta',eta^-1,(eta^-1)'
// range: exact correlation-aware proof in prove_core.py, maximum magnitude 28568
// no memory, no physical registers, no 2a/3a intermediate

gt864_forward_ntt9_core_slothy_start:
    // Level 1 A = B3(f0,f3,f6)
    orr       V<a_saved>.16b, V<f0>.16b, V<f0>.16b
    add       V<a_sum01>.8h, V<f0>.8h, V<f3>.8h
    add       V<a0>.8h, V<a_sum01>.8h, V<f6>.8h
    sqrdmulh  V<a_qb>.8h, V<f3>.8h, V<roots>.h[1]
    mul       V<a_rb>.8h, V<f3>.8h, V<roots>.h[0]
    mls       V<a_rb>.8h, V<a_qb>.8h, V<modq>.8h
    sqrdmulh  V<a_qc>.8h, V<f6>.8h, V<roots>.h[3]
    mul       V<a_r2c>.8h, V<f6>.8h, V<roots>.h[2]
    mls       V<a_r2c>.8h, V<a_qc>.8h, V<modq>.8h
    add       V<a_weighted>.8h, V<a_rb>.8h, V<a_r2c>.8h
    add       V<a1>.8h, V<a_weighted>.8h, V<a_saved>.8h
    sub       V<a_p0>.8h, V<a_saved>.8h, V<a0>.8h
    sub       V<a_p1>.8h, V<a_saved>.8h, V<a1>.8h
    add       V<a_p2>.8h, V<a_p0>.8h, V<a_p1>.8h
    add       V<a2>.8h, V<a_p2>.8h, V<a_saved>.8h

    // Level 1 B = B3(f1,f4,f7)
    orr       V<b_saved>.16b, V<f1>.16b, V<f1>.16b
    add       V<b_sum01>.8h, V<f1>.8h, V<f4>.8h
    add       V<b0>.8h, V<b_sum01>.8h, V<f7>.8h
    sqrdmulh  V<b_qb>.8h, V<f4>.8h, V<roots>.h[1]
    mul       V<b_rb>.8h, V<f4>.8h, V<roots>.h[0]
    mls       V<b_rb>.8h, V<b_qb>.8h, V<modq>.8h
    sqrdmulh  V<b_qc>.8h, V<f7>.8h, V<roots>.h[3]
    mul       V<b_r2c>.8h, V<f7>.8h, V<roots>.h[2]
    mls       V<b_r2c>.8h, V<b_qc>.8h, V<modq>.8h
    add       V<b_weighted>.8h, V<b_rb>.8h, V<b_r2c>.8h
    add       V<b1>.8h, V<b_weighted>.8h, V<b_saved>.8h
    sub       V<b_p0>.8h, V<b_saved>.8h, V<b0>.8h
    sub       V<b_p1>.8h, V<b_saved>.8h, V<b1>.8h
    add       V<b_p2>.8h, V<b_p0>.8h, V<b_p1>.8h
    add       V<b2>.8h, V<b_p2>.8h, V<b_saved>.8h

    // Level 1 C = B3(f8,f2,f5), paper-oriented input order
    orr       V<c_saved>.16b, V<f8>.16b, V<f8>.16b
    add       V<c_sum01>.8h, V<f8>.8h, V<f2>.8h
    add       V<c0>.8h, V<c_sum01>.8h, V<f5>.8h
    sqrdmulh  V<c_qb>.8h, V<f2>.8h, V<roots>.h[1]
    mul       V<c_rb>.8h, V<f2>.8h, V<roots>.h[0]
    mls       V<c_rb>.8h, V<c_qb>.8h, V<modq>.8h
    sqrdmulh  V<c_qc>.8h, V<f5>.8h, V<roots>.h[3]
    mul       V<c_r2c>.8h, V<f5>.8h, V<roots>.h[2]
    mls       V<c_r2c>.8h, V<c_qc>.8h, V<modq>.8h
    add       V<c_weighted>.8h, V<c_rb>.8h, V<c_r2c>.8h
    add       V<c1>.8h, V<c_weighted>.8h, V<c_saved>.8h
    sub       V<c_p0>.8h, V<c_saved>.8h, V<c0>.8h
    sub       V<c_p1>.8h, V<c_saved>.8h, V<c1>.8h
    add       V<c_p2>.8h, V<c_p0>.8h, V<c_p1>.8h
    add       V<c2>.8h, V<c_p2>.8h, V<c_saved>.8h

    // Consume row 0 immediately: G0 = B3(a0,b0,c0)
    orr       V<g0_saved>.16b, V<a0>.16b, V<a0>.16b
    add       V<g0_sum01>.8h, V<a0>.8h, V<b0>.8h
    add       V<out0>.8h, V<g0_sum01>.8h, V<c0>.8h
    sqrdmulh  V<g0_qb>.8h, V<b0>.8h, V<roots>.h[1]
    mul       V<g0_rb>.8h, V<b0>.8h, V<roots>.h[0]
    mls       V<g0_rb>.8h, V<g0_qb>.8h, V<modq>.8h
    sqrdmulh  V<g0_qc>.8h, V<c0>.8h, V<roots>.h[3]
    mul       V<g0_r2c>.8h, V<c0>.8h, V<roots>.h[2]
    mls       V<g0_r2c>.8h, V<g0_qc>.8h, V<modq>.8h
    add       V<g0_weighted>.8h, V<g0_rb>.8h, V<g0_r2c>.8h
    add       V<out3>.8h, V<g0_weighted>.8h, V<g0_saved>.8h
    sub       V<g0_p0>.8h, V<g0_saved>.8h, V<out0>.8h
    sub       V<g0_p1>.8h, V<g0_saved>.8h, V<out3>.8h
    add       V<g0_p2>.8h, V<g0_p0>.8h, V<g0_p1>.8h
    add       V<out6>.8h, V<g0_p2>.8h, V<g0_saved>.8h

    // Eta corrections are created only when their level-2 consumer is ready.
    sqrdmulh  V<eta_b1_q>.8h, V<b1>.8h, V<roots>.h[5]
    mul       V<eta_b1>.8h, V<b1>.8h, V<roots>.h[4]
    mls       V<eta_b1>.8h, V<eta_b1_q>.8h, V<modq>.8h
    sqrdmulh  V<eta_inv_c1_q>.8h, V<c1>.8h, V<roots>.h[7]
    mul       V<eta_inv_c1>.8h, V<c1>.8h, V<roots>.h[6]
    mls       V<eta_inv_c1>.8h, V<eta_inv_c1_q>.8h, V<modq>.8h

    // G1 = B3(a1,eta*b1,eta^-1*c1)
    orr       V<g1_saved>.16b, V<a1>.16b, V<a1>.16b
    add       V<g1_sum01>.8h, V<a1>.8h, V<eta_b1>.8h
    add       V<out1>.8h, V<g1_sum01>.8h, V<eta_inv_c1>.8h
    sqrdmulh  V<g1_qb>.8h, V<eta_b1>.8h, V<roots>.h[1]
    mul       V<g1_rb>.8h, V<eta_b1>.8h, V<roots>.h[0]
    mls       V<g1_rb>.8h, V<g1_qb>.8h, V<modq>.8h
    sqrdmulh  V<g1_qc>.8h, V<eta_inv_c1>.8h, V<roots>.h[3]
    mul       V<g1_r2c>.8h, V<eta_inv_c1>.8h, V<roots>.h[2]
    mls       V<g1_r2c>.8h, V<g1_qc>.8h, V<modq>.8h
    add       V<g1_weighted>.8h, V<g1_rb>.8h, V<g1_r2c>.8h
    add       V<out4>.8h, V<g1_weighted>.8h, V<g1_saved>.8h
    sub       V<g1_p0>.8h, V<g1_saved>.8h, V<out1>.8h
    sub       V<g1_p1>.8h, V<g1_saved>.8h, V<out4>.8h
    add       V<g1_p2>.8h, V<g1_p0>.8h, V<g1_p1>.8h
    add       V<out7>.8h, V<g1_p2>.8h, V<g1_saved>.8h

    sqrdmulh  V<eta_inv_b2_q>.8h, V<b2>.8h, V<roots>.h[7]
    mul       V<eta_inv_b2>.8h, V<b2>.8h, V<roots>.h[6]
    mls       V<eta_inv_b2>.8h, V<eta_inv_b2_q>.8h, V<modq>.8h
    sqrdmulh  V<eta_c2_q>.8h, V<c2>.8h, V<roots>.h[5]
    mul       V<eta_c2>.8h, V<c2>.8h, V<roots>.h[4]
    mls       V<eta_c2>.8h, V<eta_c2_q>.8h, V<modq>.8h

    // G2 = B3(a2,eta^-1*b2,eta*c2); map to paper output order.
    orr       V<g2_saved>.16b, V<a2>.16b, V<a2>.16b
    add       V<g2_sum01>.8h, V<a2>.8h, V<eta_inv_b2>.8h
    add       V<out8>.8h, V<g2_sum01>.8h, V<eta_c2>.8h
    sqrdmulh  V<g2_qb>.8h, V<eta_inv_b2>.8h, V<roots>.h[1]
    mul       V<g2_rb>.8h, V<eta_inv_b2>.8h, V<roots>.h[0]
    mls       V<g2_rb>.8h, V<g2_qb>.8h, V<modq>.8h
    sqrdmulh  V<g2_qc>.8h, V<eta_c2>.8h, V<roots>.h[3]
    mul       V<g2_r2c>.8h, V<eta_c2>.8h, V<roots>.h[2]
    mls       V<g2_r2c>.8h, V<g2_qc>.8h, V<modq>.8h
    add       V<g2_weighted>.8h, V<g2_rb>.8h, V<g2_r2c>.8h
    add       V<out2>.8h, V<g2_weighted>.8h, V<g2_saved>.8h
    sub       V<g2_p0>.8h, V<g2_saved>.8h, V<out8>.8h
    sub       V<g2_p1>.8h, V<g2_saved>.8h, V<out2>.8h
    add       V<g2_p2>.8h, V<g2_p0>.8h, V<g2_p1>.8h
    add       V<out5>.8h, V<g2_p2>.8h, V<g2_saved>.8h
gt864_forward_ntt9_core_slothy_end:
