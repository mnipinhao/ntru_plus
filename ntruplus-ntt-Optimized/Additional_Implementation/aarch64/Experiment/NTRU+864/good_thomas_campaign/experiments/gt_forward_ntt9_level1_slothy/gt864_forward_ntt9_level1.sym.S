/* M5H: three correlation-safe B3s over one complete NTT9 level-1 block. */
// live-in: f0..f8, roots, modq
// live-out: a0..a2, b0..b2, c0..c2
// preserved pressure: the other nine-vector column block is reserved by driver
// no memory, no physical registers, no 2a/3a intermediate

gt864_forward_ntt9_level1_slothy_start:
    // range: prove_level1.py; maximum signed16 magnitude 16816
    // A = B3(f0,f3,f6)
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

    // B = B3(f1,f4,f7)
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

    // C = B3(f8,f2,f5), preserving the paper-oriented input order
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
gt864_forward_ntt9_level1_slothy_end:
