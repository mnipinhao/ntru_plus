// Generated two-chunk P1 symbolic DAG; experiment only.
// live-in: x0=dst, x1=GT source, v0=q; live-out: x0 += 192.
// Range: input [-3457,3456], normalized output [0,3456].
// Reserved physical registers: x2-x30, sp, and fixed v0.
// Checker declarations: V<p4_a>, V<p5_a>, V<p6_a>, V<p7_a>, V<p8_a>, and V<p9_a> are defined by shl instructions below; they are not live-ins.
// Checker declarations: V<p4_b>, V<p5_b>, V<p6_b>, V<p7_b>, V<p8_b>, and V<p9_b> are defined by shl instructions below; they are not live-ins.
slothy_start_gt_canonical_pack_p1_pair:
    ldr D<g0_a>, [x1, #312]
    ldr D<g0_hi_a>, [x1, #288]
    mov V<g0_a>.d[1], V<g0_hi_a>.d[0]
    ldr D<g1_a>, [x1, #360]
    ldr D<g1_hi_a>, [x1, #336]
    mov V<g1_a>.d[1], V<g1_hi_a>.d[0]
    ldr D<g2_a>, [x1, #264]
    ldr D<g2_hi_a>, [x1, #240]
    mov V<g2_a>.d[1], V<g2_hi_a>.d[0]
    ldr D<g3_a>, [x1, #192]
    ldr D<g3_hi_a>, [x1, #216]
    mov V<g3_a>.d[1], V<g3_hi_a>.d[0]
    ldr D<g4_a>, [x1, #72]
    ldr D<g4_hi_a>, [x1, #48]
    mov V<g4_a>.d[1], V<g4_hi_a>.d[0]
    ldr D<g5_a>, [x1, #0]
    ldr D<g5_hi_a>, [x1, #24]
    mov V<g5_a>.d[1], V<g5_hi_a>.d[0]
    ldr D<g6_a>, [x1, #168]
    ldr D<g6_hi_a>, [x1, #144]
    mov V<g6_a>.d[1], V<g6_hi_a>.d[0]
    ldr D<g7_a>, [x1, #96]
    ldr D<g7_hi_a>, [x1, #120]
    mov V<g7_a>.d[1], V<g7_hi_a>.d[0]
    sshr V<sign0_a>.8h, V<g0_a>.8h, #15
    and V<corr0_a>.16b, V<sign0_a>.16b, v0.16b
    add V<ng0_a>.8h, V<g0_a>.8h, V<corr0_a>.8h
    sshr V<sign1_a>.8h, V<g1_a>.8h, #15
    and V<corr1_a>.16b, V<sign1_a>.16b, v0.16b
    add V<ng1_a>.8h, V<g1_a>.8h, V<corr1_a>.8h
    sshr V<sign2_a>.8h, V<g2_a>.8h, #15
    and V<corr2_a>.16b, V<sign2_a>.16b, v0.16b
    add V<ng2_a>.8h, V<g2_a>.8h, V<corr2_a>.8h
    sshr V<sign3_a>.8h, V<g3_a>.8h, #15
    and V<corr3_a>.16b, V<sign3_a>.16b, v0.16b
    add V<ng3_a>.8h, V<g3_a>.8h, V<corr3_a>.8h
    sshr V<sign4_a>.8h, V<g4_a>.8h, #15
    and V<corr4_a>.16b, V<sign4_a>.16b, v0.16b
    add V<ng4_a>.8h, V<g4_a>.8h, V<corr4_a>.8h
    sshr V<sign5_a>.8h, V<g5_a>.8h, #15
    and V<corr5_a>.16b, V<sign5_a>.16b, v0.16b
    add V<ng5_a>.8h, V<g5_a>.8h, V<corr5_a>.8h
    sshr V<sign6_a>.8h, V<g6_a>.8h, #15
    and V<corr6_a>.16b, V<sign6_a>.16b, v0.16b
    add V<ng6_a>.8h, V<g6_a>.8h, V<corr6_a>.8h
    sshr V<sign7_a>.8h, V<g7_a>.8h, #15
    and V<corr7_a>.16b, V<sign7_a>.16b, v0.16b
    add V<ng7_a>.8h, V<g7_a>.8h, V<corr7_a>.8h
    trn1 V<h0_a>.8h, V<ng0_a>.8h, V<ng1_a>.8h
    trn2 V<h1_a>.8h, V<ng0_a>.8h, V<ng1_a>.8h
    trn1 V<h2_a>.8h, V<ng2_a>.8h, V<ng3_a>.8h
    trn2 V<h3_a>.8h, V<ng2_a>.8h, V<ng3_a>.8h
    trn1 V<h4_a>.8h, V<ng4_a>.8h, V<ng5_a>.8h
    trn2 V<h5_a>.8h, V<ng4_a>.8h, V<ng5_a>.8h
    trn1 V<h6_a>.8h, V<ng6_a>.8h, V<ng7_a>.8h
    trn2 V<h7_a>.8h, V<ng6_a>.8h, V<ng7_a>.8h
    trn1 V<s0_a>.4s, V<h0_a>.4s, V<h2_a>.4s
    trn2 V<s2_a>.4s, V<h0_a>.4s, V<h2_a>.4s
    trn1 V<s1_a>.4s, V<h1_a>.4s, V<h3_a>.4s
    trn2 V<s3_a>.4s, V<h1_a>.4s, V<h3_a>.4s
    trn1 V<s4_a>.4s, V<h4_a>.4s, V<h6_a>.4s
    trn2 V<s6_a>.4s, V<h4_a>.4s, V<h6_a>.4s
    trn1 V<s5_a>.4s, V<h5_a>.4s, V<h7_a>.4s
    trn2 V<s7_a>.4s, V<h5_a>.4s, V<h7_a>.4s
    trn1 V<n0_a>.2d, V<s0_a>.2d, V<s4_a>.2d
    trn2 V<n4_a>.2d, V<s0_a>.2d, V<s4_a>.2d
    trn1 V<n1_a>.2d, V<s1_a>.2d, V<s5_a>.2d
    trn2 V<n5_a>.2d, V<s1_a>.2d, V<s5_a>.2d
    trn1 V<n2_a>.2d, V<s2_a>.2d, V<s6_a>.2d
    trn2 V<n6_a>.2d, V<s2_a>.2d, V<s6_a>.2d
    trn1 V<n3_a>.2d, V<s3_a>.2d, V<s7_a>.2d
    trn2 V<n7_a>.2d, V<s3_a>.2d, V<s7_a>.2d
    ushr V<p0_a>.8h, V<n1_a>.8h, #4
    ushr V<p1_a>.8h, V<n2_a>.8h, #8
    ushr V<p2_a>.8h, V<n5_a>.8h, #4
    ushr V<p3_a>.8h, V<n6_a>.8h, #8
    shl V<p4_a>.8h, V<n1_a>.8h, #12
    shl V<p5_a>.8h, V<n2_a>.8h, #8
    shl V<p6_a>.8h, V<n3_a>.8h, #4
    shl V<p7_a>.8h, V<n5_a>.8h, #12
    shl V<p8_a>.8h, V<n6_a>.8h, #8
    shl V<p9_a>.8h, V<n7_a>.8h, #4
    eor V<u0_a>.16b, V<n0_a>.16b, V<p4_a>.16b
    eor V<u1_a>.16b, V<p0_a>.16b, V<p5_a>.16b
    eor V<u2_a>.16b, V<p1_a>.16b, V<p6_a>.16b
    eor V<u3_a>.16b, V<n4_a>.16b, V<p7_a>.16b
    eor V<u4_a>.16b, V<p2_a>.16b, V<p8_a>.16b
    eor V<u5_a>.16b, V<p3_a>.16b, V<p9_a>.16b
    trn1 V<b0_a>.8h, V<u0_a>.8h, V<u1_a>.8h
    trn1 V<b1_a>.8h, V<u2_a>.8h, V<u3_a>.8h
    trn1 V<b2_a>.8h, V<u4_a>.8h, V<u5_a>.8h
    trn2 V<b3_a>.8h, V<u0_a>.8h, V<u1_a>.8h
    trn2 V<b4_a>.8h, V<u2_a>.8h, V<u3_a>.8h
    trn2 V<b5_a>.8h, V<u4_a>.8h, V<u5_a>.8h
    trn1 V<c0_a>.4s, V<b0_a>.4s, V<b1_a>.4s
    trn1 V<c1_a>.4s, V<b2_a>.4s, V<b3_a>.4s
    trn1 V<c2_a>.4s, V<b4_a>.4s, V<b5_a>.4s
    trn2 V<c3_a>.4s, V<b0_a>.4s, V<b1_a>.4s
    trn2 V<c4_a>.4s, V<b2_a>.4s, V<b3_a>.4s
    trn2 V<c5_a>.4s, V<b4_a>.4s, V<b5_a>.4s
    trn1 V<out0_a>.2d, V<c0_a>.2d, V<c1_a>.2d
    trn1 V<out1_a>.2d, V<c2_a>.2d, V<c3_a>.2d
    trn1 V<out2_a>.2d, V<c4_a>.2d, V<c5_a>.2d
    trn2 V<out3_a>.2d, V<c0_a>.2d, V<c1_a>.2d
    trn2 V<out4_a>.2d, V<c2_a>.2d, V<c3_a>.2d
    trn2 V<out5_a>.2d, V<c4_a>.2d, V<c5_a>.2d
    st1 {V<out0_a>.8h, V<out1_a>.8h, V<out2_a>.8h}, [x0], #48
    st1 {V<out3_a>.8h, V<out4_a>.8h, V<out5_a>.8h}, [x0], #48
    ldr D<g0_b>, [x1, #696]
    ldr D<g0_hi_b>, [x1, #672]
    mov V<g0_b>.d[1], V<g0_hi_b>.d[0]
    ldr D<g1_b>, [x1, #744]
    ldr D<g1_hi_b>, [x1, #720]
    mov V<g1_b>.d[1], V<g1_hi_b>.d[0]
    ldr D<g2_b>, [x1, #648]
    ldr D<g2_hi_b>, [x1, #624]
    mov V<g2_b>.d[1], V<g2_hi_b>.d[0]
    ldr D<g3_b>, [x1, #576]
    ldr D<g3_hi_b>, [x1, #600]
    mov V<g3_b>.d[1], V<g3_hi_b>.d[0]
    ldr D<g4_b>, [x1, #456]
    ldr D<g4_hi_b>, [x1, #432]
    mov V<g4_b>.d[1], V<g4_hi_b>.d[0]
    ldr D<g5_b>, [x1, #384]
    ldr D<g5_hi_b>, [x1, #408]
    mov V<g5_b>.d[1], V<g5_hi_b>.d[0]
    ldr D<g6_b>, [x1, #552]
    ldr D<g6_hi_b>, [x1, #528]
    mov V<g6_b>.d[1], V<g6_hi_b>.d[0]
    ldr D<g7_b>, [x1, #480]
    ldr D<g7_hi_b>, [x1, #504]
    mov V<g7_b>.d[1], V<g7_hi_b>.d[0]
    sshr V<sign0_b>.8h, V<g0_b>.8h, #15
    and V<corr0_b>.16b, V<sign0_b>.16b, v0.16b
    add V<ng0_b>.8h, V<g0_b>.8h, V<corr0_b>.8h
    sshr V<sign1_b>.8h, V<g1_b>.8h, #15
    and V<corr1_b>.16b, V<sign1_b>.16b, v0.16b
    add V<ng1_b>.8h, V<g1_b>.8h, V<corr1_b>.8h
    sshr V<sign2_b>.8h, V<g2_b>.8h, #15
    and V<corr2_b>.16b, V<sign2_b>.16b, v0.16b
    add V<ng2_b>.8h, V<g2_b>.8h, V<corr2_b>.8h
    sshr V<sign3_b>.8h, V<g3_b>.8h, #15
    and V<corr3_b>.16b, V<sign3_b>.16b, v0.16b
    add V<ng3_b>.8h, V<g3_b>.8h, V<corr3_b>.8h
    sshr V<sign4_b>.8h, V<g4_b>.8h, #15
    and V<corr4_b>.16b, V<sign4_b>.16b, v0.16b
    add V<ng4_b>.8h, V<g4_b>.8h, V<corr4_b>.8h
    sshr V<sign5_b>.8h, V<g5_b>.8h, #15
    and V<corr5_b>.16b, V<sign5_b>.16b, v0.16b
    add V<ng5_b>.8h, V<g5_b>.8h, V<corr5_b>.8h
    sshr V<sign6_b>.8h, V<g6_b>.8h, #15
    and V<corr6_b>.16b, V<sign6_b>.16b, v0.16b
    add V<ng6_b>.8h, V<g6_b>.8h, V<corr6_b>.8h
    sshr V<sign7_b>.8h, V<g7_b>.8h, #15
    and V<corr7_b>.16b, V<sign7_b>.16b, v0.16b
    add V<ng7_b>.8h, V<g7_b>.8h, V<corr7_b>.8h
    trn1 V<h0_b>.8h, V<ng0_b>.8h, V<ng1_b>.8h
    trn2 V<h1_b>.8h, V<ng0_b>.8h, V<ng1_b>.8h
    trn1 V<h2_b>.8h, V<ng2_b>.8h, V<ng3_b>.8h
    trn2 V<h3_b>.8h, V<ng2_b>.8h, V<ng3_b>.8h
    trn1 V<h4_b>.8h, V<ng4_b>.8h, V<ng5_b>.8h
    trn2 V<h5_b>.8h, V<ng4_b>.8h, V<ng5_b>.8h
    trn1 V<h6_b>.8h, V<ng6_b>.8h, V<ng7_b>.8h
    trn2 V<h7_b>.8h, V<ng6_b>.8h, V<ng7_b>.8h
    trn1 V<s0_b>.4s, V<h0_b>.4s, V<h2_b>.4s
    trn2 V<s2_b>.4s, V<h0_b>.4s, V<h2_b>.4s
    trn1 V<s1_b>.4s, V<h1_b>.4s, V<h3_b>.4s
    trn2 V<s3_b>.4s, V<h1_b>.4s, V<h3_b>.4s
    trn1 V<s4_b>.4s, V<h4_b>.4s, V<h6_b>.4s
    trn2 V<s6_b>.4s, V<h4_b>.4s, V<h6_b>.4s
    trn1 V<s5_b>.4s, V<h5_b>.4s, V<h7_b>.4s
    trn2 V<s7_b>.4s, V<h5_b>.4s, V<h7_b>.4s
    trn1 V<n0_b>.2d, V<s0_b>.2d, V<s4_b>.2d
    trn2 V<n4_b>.2d, V<s0_b>.2d, V<s4_b>.2d
    trn1 V<n1_b>.2d, V<s1_b>.2d, V<s5_b>.2d
    trn2 V<n5_b>.2d, V<s1_b>.2d, V<s5_b>.2d
    trn1 V<n2_b>.2d, V<s2_b>.2d, V<s6_b>.2d
    trn2 V<n6_b>.2d, V<s2_b>.2d, V<s6_b>.2d
    trn1 V<n3_b>.2d, V<s3_b>.2d, V<s7_b>.2d
    trn2 V<n7_b>.2d, V<s3_b>.2d, V<s7_b>.2d
    ushr V<p0_b>.8h, V<n1_b>.8h, #4
    ushr V<p1_b>.8h, V<n2_b>.8h, #8
    ushr V<p2_b>.8h, V<n5_b>.8h, #4
    ushr V<p3_b>.8h, V<n6_b>.8h, #8
    shl V<p4_b>.8h, V<n1_b>.8h, #12
    shl V<p5_b>.8h, V<n2_b>.8h, #8
    shl V<p6_b>.8h, V<n3_b>.8h, #4
    shl V<p7_b>.8h, V<n5_b>.8h, #12
    shl V<p8_b>.8h, V<n6_b>.8h, #8
    shl V<p9_b>.8h, V<n7_b>.8h, #4
    eor V<u0_b>.16b, V<n0_b>.16b, V<p4_b>.16b
    eor V<u1_b>.16b, V<p0_b>.16b, V<p5_b>.16b
    eor V<u2_b>.16b, V<p1_b>.16b, V<p6_b>.16b
    eor V<u3_b>.16b, V<n4_b>.16b, V<p7_b>.16b
    eor V<u4_b>.16b, V<p2_b>.16b, V<p8_b>.16b
    eor V<u5_b>.16b, V<p3_b>.16b, V<p9_b>.16b
    trn1 V<b0_b>.8h, V<u0_b>.8h, V<u1_b>.8h
    trn1 V<b1_b>.8h, V<u2_b>.8h, V<u3_b>.8h
    trn1 V<b2_b>.8h, V<u4_b>.8h, V<u5_b>.8h
    trn2 V<b3_b>.8h, V<u0_b>.8h, V<u1_b>.8h
    trn2 V<b4_b>.8h, V<u2_b>.8h, V<u3_b>.8h
    trn2 V<b5_b>.8h, V<u4_b>.8h, V<u5_b>.8h
    trn1 V<c0_b>.4s, V<b0_b>.4s, V<b1_b>.4s
    trn1 V<c1_b>.4s, V<b2_b>.4s, V<b3_b>.4s
    trn1 V<c2_b>.4s, V<b4_b>.4s, V<b5_b>.4s
    trn2 V<c3_b>.4s, V<b0_b>.4s, V<b1_b>.4s
    trn2 V<c4_b>.4s, V<b2_b>.4s, V<b3_b>.4s
    trn2 V<c5_b>.4s, V<b4_b>.4s, V<b5_b>.4s
    trn1 V<out0_b>.2d, V<c0_b>.2d, V<c1_b>.2d
    trn1 V<out1_b>.2d, V<c2_b>.2d, V<c3_b>.2d
    trn1 V<out2_b>.2d, V<c4_b>.2d, V<c5_b>.2d
    trn2 V<out3_b>.2d, V<c0_b>.2d, V<c1_b>.2d
    trn2 V<out4_b>.2d, V<c2_b>.2d, V<c3_b>.2d
    trn2 V<out5_b>.2d, V<c4_b>.2d, V<c5_b>.2d
    st1 {V<out0_b>.8h, V<out1_b>.8h, V<out2_b>.8h}, [x0], #48
    st1 {V<out3_b>.8h, V<out4_b>.8h, V<out5_b>.8h}, [x0], #48
slothy_end_gt_canonical_pack_p1_pair:
