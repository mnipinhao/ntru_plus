// Generated from the verified P1 semantic DAG; experiment only.
// Live-in: x0=dst, v0=q, and fixed v1-v8 are one gathered chunk.
// Live-out: x0 advanced by 96 and one canonical chunk stored.
// Range: input [-3457,3456], normalized output [0,3456].
// Reserved physical registers: x1-x30, sp, and fixed v0-v8.
// Checker declarations: V<p4>, V<p5>, V<p6>, V<p7>, V<p8>, and V<p9> are defined by shl instructions below; they are not live-ins.
slothy_start_gt_canonical_pack_compact_core:
    sshr V<sign0>.8h, v1.8h, #15
    and V<corr0>.16b, V<sign0>.16b, v0.16b
    add V<ng0>.8h, v1.8h, V<corr0>.8h
    sshr V<sign1>.8h, v2.8h, #15
    and V<corr1>.16b, V<sign1>.16b, v0.16b
    add V<ng1>.8h, v2.8h, V<corr1>.8h
    sshr V<sign2>.8h, v3.8h, #15
    and V<corr2>.16b, V<sign2>.16b, v0.16b
    add V<ng2>.8h, v3.8h, V<corr2>.8h
    sshr V<sign3>.8h, v4.8h, #15
    and V<corr3>.16b, V<sign3>.16b, v0.16b
    add V<ng3>.8h, v4.8h, V<corr3>.8h
    sshr V<sign4>.8h, v5.8h, #15
    and V<corr4>.16b, V<sign4>.16b, v0.16b
    add V<ng4>.8h, v5.8h, V<corr4>.8h
    sshr V<sign5>.8h, v6.8h, #15
    and V<corr5>.16b, V<sign5>.16b, v0.16b
    add V<ng5>.8h, v6.8h, V<corr5>.8h
    sshr V<sign6>.8h, v7.8h, #15
    and V<corr6>.16b, V<sign6>.16b, v0.16b
    add V<ng6>.8h, v7.8h, V<corr6>.8h
    sshr V<sign7>.8h, v8.8h, #15
    and V<corr7>.16b, V<sign7>.16b, v0.16b
    add V<ng7>.8h, v8.8h, V<corr7>.8h
    trn1 V<h0>.8h, V<ng0>.8h, V<ng1>.8h
    trn2 V<h1>.8h, V<ng0>.8h, V<ng1>.8h
    trn1 V<h2>.8h, V<ng2>.8h, V<ng3>.8h
    trn2 V<h3>.8h, V<ng2>.8h, V<ng3>.8h
    trn1 V<h4>.8h, V<ng4>.8h, V<ng5>.8h
    trn2 V<h5>.8h, V<ng4>.8h, V<ng5>.8h
    trn1 V<h6>.8h, V<ng6>.8h, V<ng7>.8h
    trn2 V<h7>.8h, V<ng6>.8h, V<ng7>.8h
    trn1 V<s0>.4s, V<h0>.4s, V<h2>.4s
    trn2 V<s2>.4s, V<h0>.4s, V<h2>.4s
    trn1 V<s1>.4s, V<h1>.4s, V<h3>.4s
    trn2 V<s3>.4s, V<h1>.4s, V<h3>.4s
    trn1 V<s4>.4s, V<h4>.4s, V<h6>.4s
    trn2 V<s6>.4s, V<h4>.4s, V<h6>.4s
    trn1 V<s5>.4s, V<h5>.4s, V<h7>.4s
    trn2 V<s7>.4s, V<h5>.4s, V<h7>.4s
    trn1 V<n0>.2d, V<s0>.2d, V<s4>.2d
    trn2 V<n4>.2d, V<s0>.2d, V<s4>.2d
    trn1 V<n1>.2d, V<s1>.2d, V<s5>.2d
    trn2 V<n5>.2d, V<s1>.2d, V<s5>.2d
    trn1 V<n2>.2d, V<s2>.2d, V<s6>.2d
    trn2 V<n6>.2d, V<s2>.2d, V<s6>.2d
    trn1 V<n3>.2d, V<s3>.2d, V<s7>.2d
    trn2 V<n7>.2d, V<s3>.2d, V<s7>.2d
    ushr V<p0>.8h, V<n1>.8h, #4
    ushr V<p1>.8h, V<n2>.8h, #8
    ushr V<p2>.8h, V<n5>.8h, #4
    ushr V<p3>.8h, V<n6>.8h, #8
    shl V<p4>.8h, V<n1>.8h, #12
    shl V<p5>.8h, V<n2>.8h, #8
    shl V<p6>.8h, V<n3>.8h, #4
    shl V<p7>.8h, V<n5>.8h, #12
    shl V<p8>.8h, V<n6>.8h, #8
    shl V<p9>.8h, V<n7>.8h, #4
    eor V<u0>.16b, V<n0>.16b, V<p4>.16b
    eor V<u1>.16b, V<p0>.16b, V<p5>.16b
    eor V<u2>.16b, V<p1>.16b, V<p6>.16b
    eor V<u3>.16b, V<n4>.16b, V<p7>.16b
    eor V<u4>.16b, V<p2>.16b, V<p8>.16b
    eor V<u5>.16b, V<p3>.16b, V<p9>.16b
    trn1 V<b0>.8h, V<u0>.8h, V<u1>.8h
    trn1 V<b1>.8h, V<u2>.8h, V<u3>.8h
    trn1 V<b2>.8h, V<u4>.8h, V<u5>.8h
    trn2 V<b3>.8h, V<u0>.8h, V<u1>.8h
    trn2 V<b4>.8h, V<u2>.8h, V<u3>.8h
    trn2 V<b5>.8h, V<u4>.8h, V<u5>.8h
    trn1 V<c0>.4s, V<b0>.4s, V<b1>.4s
    trn1 V<c1>.4s, V<b2>.4s, V<b3>.4s
    trn1 V<c2>.4s, V<b4>.4s, V<b5>.4s
    trn2 V<c3>.4s, V<b0>.4s, V<b1>.4s
    trn2 V<c4>.4s, V<b2>.4s, V<b3>.4s
    trn2 V<c5>.4s, V<b4>.4s, V<b5>.4s
    trn1 V<out0>.2d, V<c0>.2d, V<c1>.2d
    trn1 V<out1>.2d, V<c2>.2d, V<c3>.2d
    trn1 V<out2>.2d, V<c4>.2d, V<c5>.2d
    trn2 V<out3>.2d, V<c0>.2d, V<c1>.2d
    trn2 V<out4>.2d, V<c2>.2d, V<c3>.2d
    trn2 V<out5>.2d, V<c4>.2d, V<c5>.2d
    st1 {V<out0>.8h, V<out1>.8h, V<out2>.8h}, [x0], #48
    st1 {V<out3>.8h, V<out4>.8h, V<out5>.8h}, [x0], #48
slothy_end_gt_canonical_pack_compact_core:
