// U1 whole-DAG canonical unpack; experiment only.
// Live-in: x0=GT destination base, x1=canonical source, v0=0x0fff.
// Live-out: x1 advanced by 96; 16 fixed GT blocks stored.
// x9 is a caller-saved lane-transfer temporary.
slothy_start_gt_canonical_unpack_chunk_u1:
    ld1 {V<p0>.8h, V<p1>.8h, V<p2>.8h}, [x1], #48
    ld1 {V<p3>.8h, V<p4>.8h, V<p5>.8h}, [x1], #48
    trn1 V<d0>.2d, V<p0>.2d, V<p3>.2d
    trn2 V<d1>.2d, V<p0>.2d, V<p3>.2d
    trn1 V<d2>.2d, V<p1>.2d, V<p4>.2d
    trn2 V<d3>.2d, V<p1>.2d, V<p4>.2d
    trn1 V<d4>.2d, V<p2>.2d, V<p5>.2d
    trn2 V<d5>.2d, V<p2>.2d, V<p5>.2d
    trn1 V<s0>.4s, V<d0>.4s, V<d3>.4s
    trn2 V<s1>.4s, V<d0>.4s, V<d3>.4s
    trn1 V<s2>.4s, V<d1>.4s, V<d4>.4s
    trn2 V<s3>.4s, V<d1>.4s, V<d4>.4s
    trn1 V<s4>.4s, V<d2>.4s, V<d5>.4s
    trn2 V<s5>.4s, V<d2>.4s, V<d5>.4s
    trn1 V<z0>.8h, V<s0>.8h, V<s3>.8h
    trn2 V<z1>.8h, V<s0>.8h, V<s3>.8h
    trn1 V<z2>.8h, V<s1>.8h, V<s4>.8h
    trn2 V<z3>.8h, V<s1>.8h, V<s4>.8h
    trn1 V<z4>.8h, V<s2>.8h, V<s5>.8h
    trn2 V<z5>.8h, V<s2>.8h, V<s5>.8h
    ushr V<sh0>.8h, V<z0>.8h, #12
    shl V<sh1>.8h, V<z1>.8h, #4
    ushr V<sh2>.8h, V<z1>.8h, #8
    shl V<sh3>.8h, V<z2>.8h, #8
    ushr V<sh4>.8h, V<z2>.8h, #4
    ushr V<sh5>.8h, V<z3>.8h, #12
    shl V<sh6>.8h, V<z4>.8h, #4
    ushr V<sh7>.8h, V<z4>.8h, #8
    shl V<sh8>.8h, V<z5>.8h, #8
    ushr V<sh9>.8h, V<z5>.8h, #4
    eor V<m1>.16b, V<sh0>.16b, V<sh1>.16b
    eor V<m2>.16b, V<sh2>.16b, V<sh3>.16b
    eor V<m5>.16b, V<sh5>.16b, V<sh6>.16b
    eor V<m6>.16b, V<sh7>.16b, V<sh8>.16b
    and V<u0>.16b, V<z0>.16b, v0.16b
    and V<u1>.16b, V<m1>.16b, v0.16b
    and V<u2>.16b, V<m2>.16b, v0.16b
    and V<u3>.16b, V<sh4>.16b, v0.16b
    and V<u4>.16b, V<z3>.16b, v0.16b
    and V<u5>.16b, V<m5>.16b, v0.16b
    and V<u6>.16b, V<m6>.16b, v0.16b
    and V<u7>.16b, V<sh9>.16b, v0.16b
    trn1 V<h0>.8h, V<u0>.8h, V<u1>.8h
    trn2 V<h1>.8h, V<u0>.8h, V<u1>.8h
    trn1 V<h2>.8h, V<u2>.8h, V<u3>.8h
    trn2 V<h3>.8h, V<u2>.8h, V<u3>.8h
    trn1 V<h4>.8h, V<u4>.8h, V<u5>.8h
    trn2 V<h5>.8h, V<u4>.8h, V<u5>.8h
    trn1 V<h6>.8h, V<u6>.8h, V<u7>.8h
    trn2 V<h7>.8h, V<u6>.8h, V<u7>.8h
    trn1 V<q0s>.4s, V<h0>.4s, V<h2>.4s
    trn2 V<q2s>.4s, V<h0>.4s, V<h2>.4s
    trn1 V<q1s>.4s, V<h1>.4s, V<h3>.4s
    trn2 V<q3s>.4s, V<h1>.4s, V<h3>.4s
    trn1 V<q4s>.4s, V<h4>.4s, V<h6>.4s
    trn2 V<q6s>.4s, V<h4>.4s, V<h6>.4s
    trn1 V<q5s>.4s, V<h5>.4s, V<h7>.4s
    trn2 V<q7s>.4s, V<h5>.4s, V<h7>.4s
    trn1 V<q0>.2d, V<q0s>.2d, V<q4s>.2d
    trn2 V<q4>.2d, V<q0s>.2d, V<q4s>.2d
    trn1 V<q1>.2d, V<q1s>.2d, V<q5s>.2d
    trn2 V<q5>.2d, V<q1s>.2d, V<q5s>.2d
    trn1 V<q2>.2d, V<q2s>.2d, V<q6s>.2d
    trn2 V<q6>.2d, V<q2s>.2d, V<q6s>.2d
    trn1 V<q3>.2d, V<q3s>.2d, V<q7s>.2d
    trn2 V<q7>.2d, V<q3s>.2d, V<q7s>.2d
    str D<q0>, [x0, #312]
    umov x9, V<q0>.d[1]
    str x9, [x0, #288]
    str D<q1>, [x0, #360]
    umov x9, V<q1>.d[1]
    str x9, [x0, #336]
    str D<q2>, [x0, #264]
    umov x9, V<q2>.d[1]
    str x9, [x0, #240]
    str D<q3>, [x0, #192]
    umov x9, V<q3>.d[1]
    str x9, [x0, #216]
    str D<q4>, [x0, #72]
    umov x9, V<q4>.d[1]
    str x9, [x0, #48]
    str D<q5>, [x0, #0]
    umov x9, V<q5>.d[1]
    str x9, [x0, #24]
    str D<q6>, [x0, #168]
    umov x9, V<q6>.d[1]
    str x9, [x0, #144]
    str D<q7>, [x0, #96]
    umov x9, V<q7>.d[1]
    str x9, [x0, #120]
slothy_end_gt_canonical_unpack_chunk_u1:
