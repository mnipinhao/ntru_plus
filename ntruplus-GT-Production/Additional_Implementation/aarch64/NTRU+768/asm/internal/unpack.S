// Generated checked U1 canonical unpack from clean GT Production; strategy=globalmax.
.text
.p2align 4
.global poly_frombytes
.global _poly_frombytes
poly_frombytes:
_poly_frombytes:
    sub sp, sp, #64
    stp d8, d9, [sp, #0]
    stp d10, d11, [sp, #16]
    stp d12, d13, [sp, #32]
    stp d14, d15, [sp, #48]
    adr x2, .Lcanonical_unpack_candidate_mask
    ldr q0, [x2]
    mov w10, #3457
    dup v8.8h, w10
    movi v7.16b, #0
    movi v22.16b, #0
    movi v24.16b, #0
    movi v25.16b, #0
    // canonical blocks 0..15
    ld1 {v14.8H, v15.8H, v16.8H}, [x1], #48
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    trn2 v9.2D, v16.2D, v20.2D
    trn1 v4.2D, v16.2D, v20.2D
    trn2 v30.2D, v14.2D, v18.2D
    trn1 v11.2D, v15.2D, v19.2D
    trn2 v12.2D, v15.2D, v19.2D
    trn1 v23.2D, v14.2D, v18.2D
    trn1 v31.4S, v30.4S, v4.4S
    trn2 v5.4S, v11.4S, v9.4S
    trn2 v15.4S, v30.4S, v4.4S
    trn1 v29.4S, v23.4S, v12.4S
    trn2 v14.4S, v23.4S, v12.4S
    trn2 v4.8H, v31.8H, v5.8H
    trn1 v27.4S, v11.4S, v9.4S
    trn2 v11.8H, v29.8H, v15.8H
    trn1 v31.8H, v31.8H, v5.8H
    ushr v10.8H, v4.8H, #4
    trn2 v26.8H, v14.8H, v27.8H
    ushr v28.8H, v11.8H, #8
    ushr v21.8H, v31.8H, #8
    trn1 v1.8H, v29.8H, v15.8H
    ushr v18.8H, v26.8H, #12
    and v6.16B, v26.16B, v0.16B
    trn1 v19.8H, v14.8H, v27.8H
    shl v30.8H, v31.8H, #4
    shl v12.8H, v4.8H, #8
    and v23.16B, v1.16B, v0.16B
    eor v31.16B, v18.16B, v30.16B
    shl v13.8H, v11.8H, #4
    eor v3.16B, v21.16B, v12.16B
    ushr v9.8H, v1.8H, #12
    shl v2.8H, v19.8H, #8
    and v20.16B, v31.16B, v0.16B
    eor v12.16B, v9.16B, v13.16B
    ushr v17.8H, v19.8H, #4
    and v31.16B, v10.16B, v0.16B
    eor v9.16B, v28.16B, v2.16B
    and v13.16B, v17.16B, v0.16B
    and v15.16B, v12.16B, v0.16B
    and v10.16B, v9.16B, v0.16B
    and v3.16B, v3.16B, v0.16B
    // Accumulate four independent unsigned maxima.
    umax v7.8h, v7.8h, v6.8h
    umax v7.8h, v7.8h, v23.8h
    umax v22.8h, v22.8h, v20.8h
    umax v22.8h, v22.8h, v31.8h
    umax v24.8h, v24.8h, v13.8h
    umax v24.8h, v24.8h, v15.8h
    umax v25.8h, v25.8h, v10.8h
    umax v25.8h, v25.8h, v3.8h
    trn1 v21.8H, v6.8H, v20.8H
    trn1 v2.8H, v23.8H, v15.8H
    trn1 v4.8H, v3.8H, v31.8H
    trn1 v14.8H, v10.8H, v13.8H
    trn2 v9.8H, v10.8H, v13.8H
    trn2 v26.8H, v3.8H, v31.8H
    trn2 v28.4S, v2.4S, v14.4S
    trn2 v17.4S, v21.4S, v4.4S
    trn1 v19.4S, v2.4S, v14.4S
    trn2 v30.8H, v6.8H, v20.8H
    trn2 v20.2D, v28.2D, v17.2D
    trn2 v5.8H, v23.8H, v15.8H
    trn1 v27.4S, v30.4S, v26.4S
    umov x9, v20.d[1]
    trn2 v10.4S, v30.4S, v26.4S
    trn1 v14.2D, v28.2D, v17.2D
    trn2 v28.4S, v5.4S, v9.4S
    trn1 v30.4S, v21.4S, v4.4S
    trn1 v18.4S, v5.4S, v9.4S
    str x9, [x0, #144]
    umov x9, v14.d[1]
    trn2 v31.2D, v28.2D, v10.2D
    trn1 v3.2D, v28.2D, v10.2D
    trn1 v23.2D, v19.2D, v30.2D
    trn2 v4.2D, v19.2D, v30.2D
    str d14, [x0, #264]
    str x9, [x0, #240]
    trn1 v17.2D, v18.2D, v27.2D
    umov x9, v23.d[1]
    str d23, [x0, #312]
    str d4, [x0, #72]
    trn2 v23.2D, v18.2D, v27.2D
    str d17, [x0, #360]
    str x9, [x0, #288]
    umov x9, v4.d[1]
    str d31, [x0, #96]
    str d23, [x0, #0]
    str x9, [x0, #48]
    umov x9, v23.d[1]
    str d3, [x0, #192]
    str x9, [x0, #24]
    umov x9, v17.d[1]
    str x9, [x0, #336]
    umov x9, v3.d[1]
    str d20, [x0, #168]
    str x9, [x0, #216]
    umov x9, v31.d[1]
    str x9, [x0, #120]
    // canonical blocks 16..31
    ld1 {v14.8H, v15.8H, v16.8H}, [x1], #48
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    trn2 v9.2D, v16.2D, v20.2D
    trn1 v4.2D, v16.2D, v20.2D
    trn2 v30.2D, v14.2D, v18.2D
    trn1 v11.2D, v15.2D, v19.2D
    trn2 v12.2D, v15.2D, v19.2D
    trn1 v23.2D, v14.2D, v18.2D
    trn1 v31.4S, v30.4S, v4.4S
    trn2 v5.4S, v11.4S, v9.4S
    trn2 v15.4S, v30.4S, v4.4S
    trn1 v29.4S, v23.4S, v12.4S
    trn2 v14.4S, v23.4S, v12.4S
    trn2 v4.8H, v31.8H, v5.8H
    trn1 v27.4S, v11.4S, v9.4S
    trn2 v11.8H, v29.8H, v15.8H
    trn1 v31.8H, v31.8H, v5.8H
    ushr v10.8H, v4.8H, #4
    trn2 v26.8H, v14.8H, v27.8H
    ushr v28.8H, v11.8H, #8
    ushr v21.8H, v31.8H, #8
    trn1 v1.8H, v29.8H, v15.8H
    ushr v18.8H, v26.8H, #12
    and v6.16B, v26.16B, v0.16B
    trn1 v19.8H, v14.8H, v27.8H
    shl v30.8H, v31.8H, #4
    shl v12.8H, v4.8H, #8
    and v23.16B, v1.16B, v0.16B
    eor v31.16B, v18.16B, v30.16B
    shl v13.8H, v11.8H, #4
    eor v3.16B, v21.16B, v12.16B
    ushr v9.8H, v1.8H, #12
    shl v2.8H, v19.8H, #8
    and v20.16B, v31.16B, v0.16B
    eor v12.16B, v9.16B, v13.16B
    ushr v17.8H, v19.8H, #4
    and v31.16B, v10.16B, v0.16B
    eor v9.16B, v28.16B, v2.16B
    and v13.16B, v17.16B, v0.16B
    and v15.16B, v12.16B, v0.16B
    and v10.16B, v9.16B, v0.16B
    and v3.16B, v3.16B, v0.16B
    // Accumulate four independent unsigned maxima.
    umax v7.8h, v7.8h, v6.8h
    umax v7.8h, v7.8h, v23.8h
    umax v22.8h, v22.8h, v20.8h
    umax v22.8h, v22.8h, v31.8h
    umax v24.8h, v24.8h, v13.8h
    umax v24.8h, v24.8h, v15.8h
    umax v25.8h, v25.8h, v10.8h
    umax v25.8h, v25.8h, v3.8h
    trn1 v21.8H, v6.8H, v20.8H
    trn1 v2.8H, v23.8H, v15.8H
    trn1 v4.8H, v3.8H, v31.8H
    trn1 v14.8H, v10.8H, v13.8H
    trn2 v9.8H, v10.8H, v13.8H
    trn2 v26.8H, v3.8H, v31.8H
    trn2 v28.4S, v2.4S, v14.4S
    trn2 v17.4S, v21.4S, v4.4S
    trn1 v19.4S, v2.4S, v14.4S
    trn2 v30.8H, v6.8H, v20.8H
    trn2 v20.2D, v28.2D, v17.2D
    trn2 v5.8H, v23.8H, v15.8H
    trn1 v27.4S, v30.4S, v26.4S
    umov x9, v20.d[1]
    trn2 v10.4S, v30.4S, v26.4S
    trn1 v14.2D, v28.2D, v17.2D
    trn2 v28.4S, v5.4S, v9.4S
    trn1 v30.4S, v21.4S, v4.4S
    trn1 v18.4S, v5.4S, v9.4S
    str x9, [x0, #528]
    umov x9, v14.d[1]
    trn2 v31.2D, v28.2D, v10.2D
    trn1 v3.2D, v28.2D, v10.2D
    trn1 v23.2D, v19.2D, v30.2D
    trn2 v4.2D, v19.2D, v30.2D
    str d14, [x0, #648]
    str x9, [x0, #624]
    trn1 v17.2D, v18.2D, v27.2D
    umov x9, v23.d[1]
    str d23, [x0, #696]
    str d4, [x0, #456]
    trn2 v23.2D, v18.2D, v27.2D
    str d17, [x0, #744]
    str x9, [x0, #672]
    umov x9, v4.d[1]
    str d31, [x0, #480]
    str d23, [x0, #384]
    str x9, [x0, #432]
    umov x9, v23.d[1]
    str d3, [x0, #576]
    str x9, [x0, #408]
    umov x9, v17.d[1]
    str x9, [x0, #720]
    umov x9, v3.d[1]
    str d20, [x0, #552]
    str x9, [x0, #600]
    umov x9, v31.d[1]
    str x9, [x0, #504]
    // canonical blocks 32..47
    ld1 {v14.8H, v15.8H, v16.8H}, [x1], #48
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    trn2 v9.2D, v16.2D, v20.2D
    trn1 v4.2D, v16.2D, v20.2D
    trn2 v30.2D, v14.2D, v18.2D
    trn1 v11.2D, v15.2D, v19.2D
    trn2 v12.2D, v15.2D, v19.2D
    trn1 v23.2D, v14.2D, v18.2D
    trn1 v31.4S, v30.4S, v4.4S
    trn2 v5.4S, v11.4S, v9.4S
    trn2 v15.4S, v30.4S, v4.4S
    trn1 v29.4S, v23.4S, v12.4S
    trn2 v14.4S, v23.4S, v12.4S
    trn2 v4.8H, v31.8H, v5.8H
    trn1 v27.4S, v11.4S, v9.4S
    trn2 v11.8H, v29.8H, v15.8H
    trn1 v31.8H, v31.8H, v5.8H
    ushr v10.8H, v4.8H, #4
    trn2 v26.8H, v14.8H, v27.8H
    ushr v28.8H, v11.8H, #8
    ushr v21.8H, v31.8H, #8
    trn1 v1.8H, v29.8H, v15.8H
    ushr v18.8H, v26.8H, #12
    and v6.16B, v26.16B, v0.16B
    trn1 v19.8H, v14.8H, v27.8H
    shl v30.8H, v31.8H, #4
    shl v12.8H, v4.8H, #8
    and v23.16B, v1.16B, v0.16B
    eor v31.16B, v18.16B, v30.16B
    shl v13.8H, v11.8H, #4
    eor v3.16B, v21.16B, v12.16B
    ushr v9.8H, v1.8H, #12
    shl v2.8H, v19.8H, #8
    and v20.16B, v31.16B, v0.16B
    eor v12.16B, v9.16B, v13.16B
    ushr v17.8H, v19.8H, #4
    and v31.16B, v10.16B, v0.16B
    eor v9.16B, v28.16B, v2.16B
    and v13.16B, v17.16B, v0.16B
    and v15.16B, v12.16B, v0.16B
    and v10.16B, v9.16B, v0.16B
    and v3.16B, v3.16B, v0.16B
    // Accumulate four independent unsigned maxima.
    umax v7.8h, v7.8h, v6.8h
    umax v7.8h, v7.8h, v23.8h
    umax v22.8h, v22.8h, v20.8h
    umax v22.8h, v22.8h, v31.8h
    umax v24.8h, v24.8h, v13.8h
    umax v24.8h, v24.8h, v15.8h
    umax v25.8h, v25.8h, v10.8h
    umax v25.8h, v25.8h, v3.8h
    trn1 v21.8H, v6.8H, v20.8H
    trn1 v2.8H, v23.8H, v15.8H
    trn1 v4.8H, v3.8H, v31.8H
    trn1 v14.8H, v10.8H, v13.8H
    trn2 v9.8H, v10.8H, v13.8H
    trn2 v26.8H, v3.8H, v31.8H
    trn2 v28.4S, v2.4S, v14.4S
    trn2 v17.4S, v21.4S, v4.4S
    trn1 v19.4S, v2.4S, v14.4S
    trn2 v30.8H, v6.8H, v20.8H
    trn2 v20.2D, v28.2D, v17.2D
    trn2 v5.8H, v23.8H, v15.8H
    trn1 v27.4S, v30.4S, v26.4S
    umov x9, v20.d[1]
    trn2 v10.4S, v30.4S, v26.4S
    trn1 v14.2D, v28.2D, v17.2D
    trn2 v28.4S, v5.4S, v9.4S
    trn1 v30.4S, v21.4S, v4.4S
    trn1 v18.4S, v5.4S, v9.4S
    str x9, [x0, #440]
    umov x9, v14.d[1]
    trn2 v31.2D, v28.2D, v10.2D
    trn1 v3.2D, v28.2D, v10.2D
    trn1 v23.2D, v19.2D, v30.2D
    trn2 v4.2D, v19.2D, v30.2D
    str d14, [x0, #224]
    str x9, [x0, #248]
    trn1 v17.2D, v18.2D, v27.2D
    umov x9, v23.d[1]
    str d23, [x0, #128]
    str d4, [x0, #320]
    trn2 v23.2D, v18.2D, v27.2D
    str d17, [x0, #176]
    str x9, [x0, #152]
    umov x9, v4.d[1]
    str d31, [x0, #464]
    str d23, [x0, #368]
    str x9, [x0, #344]
    umov x9, v23.d[1]
    str d3, [x0, #272]
    str x9, [x0, #392]
    umov x9, v17.d[1]
    str x9, [x0, #200]
    umov x9, v3.d[1]
    str d20, [x0, #416]
    str x9, [x0, #296]
    umov x9, v31.d[1]
    str x9, [x0, #488]
    // canonical blocks 48..63
    ld1 {v14.8H, v15.8H, v16.8H}, [x1], #48
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    trn2 v9.2D, v16.2D, v20.2D
    trn1 v4.2D, v16.2D, v20.2D
    trn2 v30.2D, v14.2D, v18.2D
    trn1 v11.2D, v15.2D, v19.2D
    trn2 v12.2D, v15.2D, v19.2D
    trn1 v23.2D, v14.2D, v18.2D
    trn1 v31.4S, v30.4S, v4.4S
    trn2 v5.4S, v11.4S, v9.4S
    trn2 v15.4S, v30.4S, v4.4S
    trn1 v29.4S, v23.4S, v12.4S
    trn2 v14.4S, v23.4S, v12.4S
    trn2 v4.8H, v31.8H, v5.8H
    trn1 v27.4S, v11.4S, v9.4S
    trn2 v11.8H, v29.8H, v15.8H
    trn1 v31.8H, v31.8H, v5.8H
    ushr v10.8H, v4.8H, #4
    trn2 v26.8H, v14.8H, v27.8H
    ushr v28.8H, v11.8H, #8
    ushr v21.8H, v31.8H, #8
    trn1 v1.8H, v29.8H, v15.8H
    ushr v18.8H, v26.8H, #12
    and v6.16B, v26.16B, v0.16B
    trn1 v19.8H, v14.8H, v27.8H
    shl v30.8H, v31.8H, #4
    shl v12.8H, v4.8H, #8
    and v23.16B, v1.16B, v0.16B
    eor v31.16B, v18.16B, v30.16B
    shl v13.8H, v11.8H, #4
    eor v3.16B, v21.16B, v12.16B
    ushr v9.8H, v1.8H, #12
    shl v2.8H, v19.8H, #8
    and v20.16B, v31.16B, v0.16B
    eor v12.16B, v9.16B, v13.16B
    ushr v17.8H, v19.8H, #4
    and v31.16B, v10.16B, v0.16B
    eor v9.16B, v28.16B, v2.16B
    and v13.16B, v17.16B, v0.16B
    and v15.16B, v12.16B, v0.16B
    and v10.16B, v9.16B, v0.16B
    and v3.16B, v3.16B, v0.16B
    // Accumulate four independent unsigned maxima.
    umax v7.8h, v7.8h, v6.8h
    umax v7.8h, v7.8h, v23.8h
    umax v22.8h, v22.8h, v20.8h
    umax v22.8h, v22.8h, v31.8h
    umax v24.8h, v24.8h, v13.8h
    umax v24.8h, v24.8h, v15.8h
    umax v25.8h, v25.8h, v10.8h
    umax v25.8h, v25.8h, v3.8h
    trn1 v21.8H, v6.8H, v20.8H
    trn1 v2.8H, v23.8H, v15.8H
    trn1 v4.8H, v3.8H, v31.8H
    trn1 v14.8H, v10.8H, v13.8H
    trn2 v9.8H, v10.8H, v13.8H
    trn2 v26.8H, v3.8H, v31.8H
    trn2 v28.4S, v2.4S, v14.4S
    trn2 v17.4S, v21.4S, v4.4S
    trn1 v19.4S, v2.4S, v14.4S
    trn2 v30.8H, v6.8H, v20.8H
    trn2 v20.2D, v28.2D, v17.2D
    trn2 v5.8H, v23.8H, v15.8H
    trn1 v27.4S, v30.4S, v26.4S
    umov x9, v20.d[1]
    trn2 v10.4S, v30.4S, v26.4S
    trn1 v14.2D, v28.2D, v17.2D
    trn2 v28.4S, v5.4S, v9.4S
    trn1 v30.4S, v21.4S, v4.4S
    trn1 v18.4S, v5.4S, v9.4S
    str x9, [x0, #584]
    umov x9, v14.d[1]
    trn2 v31.2D, v28.2D, v10.2D
    trn1 v3.2D, v28.2D, v10.2D
    trn1 v23.2D, v19.2D, v30.2D
    trn2 v4.2D, v19.2D, v30.2D
    str d14, [x0, #32]
    str x9, [x0, #56]
    trn1 v17.2D, v18.2D, v27.2D
    umov x9, v23.d[1]
    str d23, [x0, #704]
    str d4, [x0, #608]
    trn2 v23.2D, v18.2D, v27.2D
    str d17, [x0, #752]
    str x9, [x0, #728]
    umov x9, v4.d[1]
    str d31, [x0, #536]
    str d23, [x0, #656]
    str x9, [x0, #632]
    umov x9, v23.d[1]
    str d3, [x0, #80]
    str x9, [x0, #680]
    umov x9, v17.d[1]
    str x9, [x0, #8]
    umov x9, v3.d[1]
    str d20, [x0, #560]
    str x9, [x0, #104]
    umov x9, v31.d[1]
    str x9, [x0, #512]
    // canonical blocks 64..79
    ld1 {v14.8H, v15.8H, v16.8H}, [x1], #48
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    trn2 v9.2D, v16.2D, v20.2D
    trn1 v4.2D, v16.2D, v20.2D
    trn2 v30.2D, v14.2D, v18.2D
    trn1 v11.2D, v15.2D, v19.2D
    trn2 v12.2D, v15.2D, v19.2D
    trn1 v23.2D, v14.2D, v18.2D
    trn1 v31.4S, v30.4S, v4.4S
    trn2 v5.4S, v11.4S, v9.4S
    trn2 v15.4S, v30.4S, v4.4S
    trn1 v29.4S, v23.4S, v12.4S
    trn2 v14.4S, v23.4S, v12.4S
    trn2 v4.8H, v31.8H, v5.8H
    trn1 v27.4S, v11.4S, v9.4S
    trn2 v11.8H, v29.8H, v15.8H
    trn1 v31.8H, v31.8H, v5.8H
    ushr v10.8H, v4.8H, #4
    trn2 v26.8H, v14.8H, v27.8H
    ushr v28.8H, v11.8H, #8
    ushr v21.8H, v31.8H, #8
    trn1 v1.8H, v29.8H, v15.8H
    ushr v18.8H, v26.8H, #12
    and v6.16B, v26.16B, v0.16B
    trn1 v19.8H, v14.8H, v27.8H
    shl v30.8H, v31.8H, #4
    shl v12.8H, v4.8H, #8
    and v23.16B, v1.16B, v0.16B
    eor v31.16B, v18.16B, v30.16B
    shl v13.8H, v11.8H, #4
    eor v3.16B, v21.16B, v12.16B
    ushr v9.8H, v1.8H, #12
    shl v2.8H, v19.8H, #8
    and v20.16B, v31.16B, v0.16B
    eor v12.16B, v9.16B, v13.16B
    ushr v17.8H, v19.8H, #4
    and v31.16B, v10.16B, v0.16B
    eor v9.16B, v28.16B, v2.16B
    and v13.16B, v17.16B, v0.16B
    and v15.16B, v12.16B, v0.16B
    and v10.16B, v9.16B, v0.16B
    and v3.16B, v3.16B, v0.16B
    // Accumulate four independent unsigned maxima.
    umax v7.8h, v7.8h, v6.8h
    umax v7.8h, v7.8h, v23.8h
    umax v22.8h, v22.8h, v20.8h
    umax v22.8h, v22.8h, v31.8h
    umax v24.8h, v24.8h, v13.8h
    umax v24.8h, v24.8h, v15.8h
    umax v25.8h, v25.8h, v10.8h
    umax v25.8h, v25.8h, v3.8h
    trn1 v21.8H, v6.8H, v20.8H
    trn1 v2.8H, v23.8H, v15.8H
    trn1 v4.8H, v3.8H, v31.8H
    trn1 v14.8H, v10.8H, v13.8H
    trn2 v9.8H, v10.8H, v13.8H
    trn2 v26.8H, v3.8H, v31.8H
    trn2 v28.4S, v2.4S, v14.4S
    trn2 v17.4S, v21.4S, v4.4S
    trn1 v19.4S, v2.4S, v14.4S
    trn2 v30.8H, v6.8H, v20.8H
    trn2 v20.2D, v28.2D, v17.2D
    trn2 v5.8H, v23.8H, v15.8H
    trn1 v27.4S, v30.4S, v26.4S
    umov x9, v20.d[1]
    trn2 v10.4S, v30.4S, v26.4S
    trn1 v14.2D, v28.2D, v17.2D
    trn2 v28.4S, v5.4S, v9.4S
    trn1 v30.4S, v21.4S, v4.4S
    trn1 v18.4S, v5.4S, v9.4S
    str x9, [x0, #448]
    umov x9, v14.d[1]
    trn2 v31.2D, v28.2D, v10.2D
    trn1 v3.2D, v28.2D, v10.2D
    trn1 v23.2D, v19.2D, v30.2D
    trn2 v4.2D, v19.2D, v30.2D
    str d14, [x0, #280]
    str x9, [x0, #256]
    trn1 v17.2D, v18.2D, v27.2D
    umov x9, v23.d[1]
    str d23, [x0, #400]
    str d4, [x0, #592]
    trn2 v23.2D, v18.2D, v27.2D
    str d17, [x0, #376]
    str x9, [x0, #424]
    umov x9, v4.d[1]
    str d31, [x0, #520]
    str d23, [x0, #568]
    str x9, [x0, #616]
    umov x9, v23.d[1]
    str d3, [x0, #328]
    str x9, [x0, #544]
    umov x9, v17.d[1]
    str x9, [x0, #352]
    umov x9, v3.d[1]
    str d20, [x0, #472]
    str x9, [x0, #304]
    umov x9, v31.d[1]
    str x9, [x0, #496]
    // canonical blocks 80..95
    ld1 {v14.8H, v15.8H, v16.8H}, [x1], #48
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    trn2 v9.2D, v16.2D, v20.2D
    trn1 v4.2D, v16.2D, v20.2D
    trn2 v30.2D, v14.2D, v18.2D
    trn1 v11.2D, v15.2D, v19.2D
    trn2 v12.2D, v15.2D, v19.2D
    trn1 v23.2D, v14.2D, v18.2D
    trn1 v31.4S, v30.4S, v4.4S
    trn2 v5.4S, v11.4S, v9.4S
    trn2 v15.4S, v30.4S, v4.4S
    trn1 v29.4S, v23.4S, v12.4S
    trn2 v14.4S, v23.4S, v12.4S
    trn2 v4.8H, v31.8H, v5.8H
    trn1 v27.4S, v11.4S, v9.4S
    trn2 v11.8H, v29.8H, v15.8H
    trn1 v31.8H, v31.8H, v5.8H
    ushr v10.8H, v4.8H, #4
    trn2 v26.8H, v14.8H, v27.8H
    ushr v28.8H, v11.8H, #8
    ushr v21.8H, v31.8H, #8
    trn1 v1.8H, v29.8H, v15.8H
    ushr v18.8H, v26.8H, #12
    and v6.16B, v26.16B, v0.16B
    trn1 v19.8H, v14.8H, v27.8H
    shl v30.8H, v31.8H, #4
    shl v12.8H, v4.8H, #8
    and v23.16B, v1.16B, v0.16B
    eor v31.16B, v18.16B, v30.16B
    shl v13.8H, v11.8H, #4
    eor v3.16B, v21.16B, v12.16B
    ushr v9.8H, v1.8H, #12
    shl v2.8H, v19.8H, #8
    and v20.16B, v31.16B, v0.16B
    eor v12.16B, v9.16B, v13.16B
    ushr v17.8H, v19.8H, #4
    and v31.16B, v10.16B, v0.16B
    eor v9.16B, v28.16B, v2.16B
    and v13.16B, v17.16B, v0.16B
    and v15.16B, v12.16B, v0.16B
    and v10.16B, v9.16B, v0.16B
    and v3.16B, v3.16B, v0.16B
    // Accumulate four independent unsigned maxima.
    umax v7.8h, v7.8h, v6.8h
    umax v7.8h, v7.8h, v23.8h
    umax v22.8h, v22.8h, v20.8h
    umax v22.8h, v22.8h, v31.8h
    umax v24.8h, v24.8h, v13.8h
    umax v24.8h, v24.8h, v15.8h
    umax v25.8h, v25.8h, v10.8h
    umax v25.8h, v25.8h, v3.8h
    trn1 v21.8H, v6.8H, v20.8H
    trn1 v2.8H, v23.8H, v15.8H
    trn1 v4.8H, v3.8H, v31.8H
    trn1 v14.8H, v10.8H, v13.8H
    trn2 v9.8H, v10.8H, v13.8H
    trn2 v26.8H, v3.8H, v31.8H
    trn2 v28.4S, v2.4S, v14.4S
    trn2 v17.4S, v21.4S, v4.4S
    trn1 v19.4S, v2.4S, v14.4S
    trn2 v30.8H, v6.8H, v20.8H
    trn2 v20.2D, v28.2D, v17.2D
    trn2 v5.8H, v23.8H, v15.8H
    trn1 v27.4S, v30.4S, v26.4S
    umov x9, v20.d[1]
    trn2 v10.4S, v30.4S, v26.4S
    trn1 v14.2D, v28.2D, v17.2D
    trn2 v28.4S, v5.4S, v9.4S
    trn1 v30.4S, v21.4S, v4.4S
    trn1 v18.4S, v5.4S, v9.4S
    str x9, [x0, #64]
    umov x9, v14.d[1]
    trn2 v31.2D, v28.2D, v10.2D
    trn1 v3.2D, v28.2D, v10.2D
    trn1 v23.2D, v19.2D, v30.2D
    trn2 v4.2D, v19.2D, v30.2D
    str d14, [x0, #664]
    str x9, [x0, #640]
    trn1 v17.2D, v18.2D, v27.2D
    umov x9, v23.d[1]
    str d23, [x0, #16]
    str d4, [x0, #208]
    trn2 v23.2D, v18.2D, v27.2D
    str d17, [x0, #760]
    str x9, [x0, #40]
    umov x9, v4.d[1]
    str d31, [x0, #136]
    str d23, [x0, #184]
    str x9, [x0, #232]
    umov x9, v23.d[1]
    str d3, [x0, #712]
    str x9, [x0, #160]
    umov x9, v17.d[1]
    str x9, [x0, #736]
    umov x9, v3.d[1]
    str d20, [x0, #88]
    str x9, [x0, #688]
    umov x9, v31.d[1]
    str x9, [x0, #112]
    // canonical blocks 96..111
    ld1 {v14.8H, v15.8H, v16.8H}, [x1], #48
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    trn2 v9.2D, v16.2D, v20.2D
    trn1 v4.2D, v16.2D, v20.2D
    trn2 v30.2D, v14.2D, v18.2D
    trn1 v11.2D, v15.2D, v19.2D
    trn2 v12.2D, v15.2D, v19.2D
    trn1 v23.2D, v14.2D, v18.2D
    trn1 v31.4S, v30.4S, v4.4S
    trn2 v5.4S, v11.4S, v9.4S
    trn2 v15.4S, v30.4S, v4.4S
    trn1 v29.4S, v23.4S, v12.4S
    trn2 v14.4S, v23.4S, v12.4S
    trn2 v4.8H, v31.8H, v5.8H
    trn1 v27.4S, v11.4S, v9.4S
    trn2 v11.8H, v29.8H, v15.8H
    trn1 v31.8H, v31.8H, v5.8H
    ushr v10.8H, v4.8H, #4
    trn2 v26.8H, v14.8H, v27.8H
    ushr v28.8H, v11.8H, #8
    ushr v21.8H, v31.8H, #8
    trn1 v1.8H, v29.8H, v15.8H
    ushr v18.8H, v26.8H, #12
    and v6.16B, v26.16B, v0.16B
    trn1 v19.8H, v14.8H, v27.8H
    shl v30.8H, v31.8H, #4
    shl v12.8H, v4.8H, #8
    and v23.16B, v1.16B, v0.16B
    eor v31.16B, v18.16B, v30.16B
    shl v13.8H, v11.8H, #4
    eor v3.16B, v21.16B, v12.16B
    ushr v9.8H, v1.8H, #12
    shl v2.8H, v19.8H, #8
    and v20.16B, v31.16B, v0.16B
    eor v12.16B, v9.16B, v13.16B
    ushr v17.8H, v19.8H, #4
    and v31.16B, v10.16B, v0.16B
    eor v9.16B, v28.16B, v2.16B
    and v13.16B, v17.16B, v0.16B
    and v15.16B, v12.16B, v0.16B
    and v10.16B, v9.16B, v0.16B
    and v3.16B, v3.16B, v0.16B
    // Accumulate four independent unsigned maxima.
    umax v7.8h, v7.8h, v6.8h
    umax v7.8h, v7.8h, v23.8h
    umax v22.8h, v22.8h, v20.8h
    umax v22.8h, v22.8h, v31.8h
    umax v24.8h, v24.8h, v13.8h
    umax v24.8h, v24.8h, v15.8h
    umax v25.8h, v25.8h, v10.8h
    umax v25.8h, v25.8h, v3.8h
    trn1 v21.8H, v6.8H, v20.8H
    trn1 v2.8H, v23.8H, v15.8H
    trn1 v4.8H, v3.8H, v31.8H
    trn1 v14.8H, v10.8H, v13.8H
    trn2 v9.8H, v10.8H, v13.8H
    trn2 v26.8H, v3.8H, v31.8H
    trn2 v28.4S, v2.4S, v14.4S
    trn2 v17.4S, v21.4S, v4.4S
    trn1 v19.4S, v2.4S, v14.4S
    trn2 v30.8H, v6.8H, v20.8H
    trn2 v20.2D, v28.2D, v17.2D
    trn2 v5.8H, v23.8H, v15.8H
    trn1 v27.4S, v30.4S, v26.4S
    umov x9, v20.d[1]
    trn2 v10.4S, v30.4S, v26.4S
    trn1 v14.2D, v28.2D, v17.2D
    trn2 v28.4S, v5.4S, v9.4S
    trn1 v30.4S, v21.4S, v4.4S
    trn1 v18.4S, v5.4S, v9.4S
    str x9, [x0, #896]
    umov x9, v14.d[1]
    trn2 v31.2D, v28.2D, v10.2D
    trn1 v3.2D, v28.2D, v10.2D
    trn1 v23.2D, v19.2D, v30.2D
    trn2 v4.2D, v19.2D, v30.2D
    str d14, [x0, #1232]
    str x9, [x0, #1256]
    trn1 v17.2D, v18.2D, v27.2D
    umov x9, v23.d[1]
    str d23, [x0, #1136]
    str d4, [x0, #1040]
    trn2 v23.2D, v18.2D, v27.2D
    str d17, [x0, #1112]
    str x9, [x0, #1160]
    umov x9, v4.d[1]
    str d31, [x0, #968]
    str d23, [x0, #1016]
    str x9, [x0, #1064]
    umov x9, v23.d[1]
    str d3, [x0, #1208]
    str x9, [x0, #992]
    umov x9, v17.d[1]
    str x9, [x0, #1088]
    umov x9, v3.d[1]
    str d20, [x0, #920]
    str x9, [x0, #1184]
    umov x9, v31.d[1]
    str x9, [x0, #944]
    // canonical blocks 112..127
    ld1 {v14.8H, v15.8H, v16.8H}, [x1], #48
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    trn2 v9.2D, v16.2D, v20.2D
    trn1 v4.2D, v16.2D, v20.2D
    trn2 v30.2D, v14.2D, v18.2D
    trn1 v11.2D, v15.2D, v19.2D
    trn2 v12.2D, v15.2D, v19.2D
    trn1 v23.2D, v14.2D, v18.2D
    trn1 v31.4S, v30.4S, v4.4S
    trn2 v5.4S, v11.4S, v9.4S
    trn2 v15.4S, v30.4S, v4.4S
    trn1 v29.4S, v23.4S, v12.4S
    trn2 v14.4S, v23.4S, v12.4S
    trn2 v4.8H, v31.8H, v5.8H
    trn1 v27.4S, v11.4S, v9.4S
    trn2 v11.8H, v29.8H, v15.8H
    trn1 v31.8H, v31.8H, v5.8H
    ushr v10.8H, v4.8H, #4
    trn2 v26.8H, v14.8H, v27.8H
    ushr v28.8H, v11.8H, #8
    ushr v21.8H, v31.8H, #8
    trn1 v1.8H, v29.8H, v15.8H
    ushr v18.8H, v26.8H, #12
    and v6.16B, v26.16B, v0.16B
    trn1 v19.8H, v14.8H, v27.8H
    shl v30.8H, v31.8H, #4
    shl v12.8H, v4.8H, #8
    and v23.16B, v1.16B, v0.16B
    eor v31.16B, v18.16B, v30.16B
    shl v13.8H, v11.8H, #4
    eor v3.16B, v21.16B, v12.16B
    ushr v9.8H, v1.8H, #12
    shl v2.8H, v19.8H, #8
    and v20.16B, v31.16B, v0.16B
    eor v12.16B, v9.16B, v13.16B
    ushr v17.8H, v19.8H, #4
    and v31.16B, v10.16B, v0.16B
    eor v9.16B, v28.16B, v2.16B
    and v13.16B, v17.16B, v0.16B
    and v15.16B, v12.16B, v0.16B
    and v10.16B, v9.16B, v0.16B
    and v3.16B, v3.16B, v0.16B
    // Accumulate four independent unsigned maxima.
    umax v7.8h, v7.8h, v6.8h
    umax v7.8h, v7.8h, v23.8h
    umax v22.8h, v22.8h, v20.8h
    umax v22.8h, v22.8h, v31.8h
    umax v24.8h, v24.8h, v13.8h
    umax v24.8h, v24.8h, v15.8h
    umax v25.8h, v25.8h, v10.8h
    umax v25.8h, v25.8h, v3.8h
    trn1 v21.8H, v6.8H, v20.8H
    trn1 v2.8H, v23.8H, v15.8H
    trn1 v4.8H, v3.8H, v31.8H
    trn1 v14.8H, v10.8H, v13.8H
    trn2 v9.8H, v10.8H, v13.8H
    trn2 v26.8H, v3.8H, v31.8H
    trn2 v28.4S, v2.4S, v14.4S
    trn2 v17.4S, v21.4S, v4.4S
    trn1 v19.4S, v2.4S, v14.4S
    trn2 v30.8H, v6.8H, v20.8H
    trn2 v20.2D, v28.2D, v17.2D
    trn2 v5.8H, v23.8H, v15.8H
    trn1 v27.4S, v30.4S, v26.4S
    umov x9, v20.d[1]
    trn2 v10.4S, v30.4S, v26.4S
    trn1 v14.2D, v28.2D, v17.2D
    trn2 v28.4S, v5.4S, v9.4S
    trn1 v30.4S, v21.4S, v4.4S
    trn1 v18.4S, v5.4S, v9.4S
    str x9, [x0, #1472]
    umov x9, v14.d[1]
    trn2 v31.2D, v28.2D, v10.2D
    trn1 v3.2D, v28.2D, v10.2D
    trn1 v23.2D, v19.2D, v30.2D
    trn2 v4.2D, v19.2D, v30.2D
    str d14, [x0, #1304]
    str x9, [x0, #1280]
    trn1 v17.2D, v18.2D, v27.2D
    umov x9, v23.d[1]
    str d23, [x0, #1424]
    str d4, [x0, #848]
    trn2 v23.2D, v18.2D, v27.2D
    str d17, [x0, #1400]
    str x9, [x0, #1448]
    umov x9, v4.d[1]
    str d31, [x0, #776]
    str d23, [x0, #824]
    str x9, [x0, #872]
    umov x9, v23.d[1]
    str d3, [x0, #1352]
    str x9, [x0, #800]
    umov x9, v17.d[1]
    str x9, [x0, #1376]
    umov x9, v3.d[1]
    str d20, [x0, #1496]
    str x9, [x0, #1328]
    umov x9, v31.d[1]
    str x9, [x0, #1520]
    // canonical blocks 128..143
    ld1 {v14.8H, v15.8H, v16.8H}, [x1], #48
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    trn2 v9.2D, v16.2D, v20.2D
    trn1 v4.2D, v16.2D, v20.2D
    trn2 v30.2D, v14.2D, v18.2D
    trn1 v11.2D, v15.2D, v19.2D
    trn2 v12.2D, v15.2D, v19.2D
    trn1 v23.2D, v14.2D, v18.2D
    trn1 v31.4S, v30.4S, v4.4S
    trn2 v5.4S, v11.4S, v9.4S
    trn2 v15.4S, v30.4S, v4.4S
    trn1 v29.4S, v23.4S, v12.4S
    trn2 v14.4S, v23.4S, v12.4S
    trn2 v4.8H, v31.8H, v5.8H
    trn1 v27.4S, v11.4S, v9.4S
    trn2 v11.8H, v29.8H, v15.8H
    trn1 v31.8H, v31.8H, v5.8H
    ushr v10.8H, v4.8H, #4
    trn2 v26.8H, v14.8H, v27.8H
    ushr v28.8H, v11.8H, #8
    ushr v21.8H, v31.8H, #8
    trn1 v1.8H, v29.8H, v15.8H
    ushr v18.8H, v26.8H, #12
    and v6.16B, v26.16B, v0.16B
    trn1 v19.8H, v14.8H, v27.8H
    shl v30.8H, v31.8H, #4
    shl v12.8H, v4.8H, #8
    and v23.16B, v1.16B, v0.16B
    eor v31.16B, v18.16B, v30.16B
    shl v13.8H, v11.8H, #4
    eor v3.16B, v21.16B, v12.16B
    ushr v9.8H, v1.8H, #12
    shl v2.8H, v19.8H, #8
    and v20.16B, v31.16B, v0.16B
    eor v12.16B, v9.16B, v13.16B
    ushr v17.8H, v19.8H, #4
    and v31.16B, v10.16B, v0.16B
    eor v9.16B, v28.16B, v2.16B
    and v13.16B, v17.16B, v0.16B
    and v15.16B, v12.16B, v0.16B
    and v10.16B, v9.16B, v0.16B
    and v3.16B, v3.16B, v0.16B
    // Accumulate four independent unsigned maxima.
    umax v7.8h, v7.8h, v6.8h
    umax v7.8h, v7.8h, v23.8h
    umax v22.8h, v22.8h, v20.8h
    umax v22.8h, v22.8h, v31.8h
    umax v24.8h, v24.8h, v13.8h
    umax v24.8h, v24.8h, v15.8h
    umax v25.8h, v25.8h, v10.8h
    umax v25.8h, v25.8h, v3.8h
    trn1 v21.8H, v6.8H, v20.8H
    trn1 v2.8H, v23.8H, v15.8H
    trn1 v4.8H, v3.8H, v31.8H
    trn1 v14.8H, v10.8H, v13.8H
    trn2 v9.8H, v10.8H, v13.8H
    trn2 v26.8H, v3.8H, v31.8H
    trn2 v28.4S, v2.4S, v14.4S
    trn2 v17.4S, v21.4S, v4.4S
    trn1 v19.4S, v2.4S, v14.4S
    trn2 v30.8H, v6.8H, v20.8H
    trn2 v20.2D, v28.2D, v17.2D
    trn2 v5.8H, v23.8H, v15.8H
    trn1 v27.4S, v30.4S, v26.4S
    umov x9, v20.d[1]
    trn2 v10.4S, v30.4S, v26.4S
    trn1 v14.2D, v28.2D, v17.2D
    trn2 v28.4S, v5.4S, v9.4S
    trn1 v30.4S, v21.4S, v4.4S
    trn1 v18.4S, v5.4S, v9.4S
    str x9, [x0, #1168]
    umov x9, v14.d[1]
    trn2 v31.2D, v28.2D, v10.2D
    trn1 v3.2D, v28.2D, v10.2D
    trn1 v23.2D, v19.2D, v30.2D
    trn2 v4.2D, v19.2D, v30.2D
    str d14, [x0, #1288]
    str x9, [x0, #1264]
    trn1 v17.2D, v18.2D, v27.2D
    umov x9, v23.d[1]
    str d23, [x0, #1336]
    str d4, [x0, #1096]
    trn2 v23.2D, v18.2D, v27.2D
    str d17, [x0, #1384]
    str x9, [x0, #1312]
    umov x9, v4.d[1]
    str d31, [x0, #1120]
    str d23, [x0, #1024]
    str x9, [x0, #1072]
    umov x9, v23.d[1]
    str d3, [x0, #1216]
    str x9, [x0, #1048]
    umov x9, v17.d[1]
    str x9, [x0, #1360]
    umov x9, v3.d[1]
    str d20, [x0, #1192]
    str x9, [x0, #1240]
    umov x9, v31.d[1]
    str x9, [x0, #1144]
    // canonical blocks 144..159
    ld1 {v14.8H, v15.8H, v16.8H}, [x1], #48
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    trn2 v9.2D, v16.2D, v20.2D
    trn1 v4.2D, v16.2D, v20.2D
    trn2 v30.2D, v14.2D, v18.2D
    trn1 v11.2D, v15.2D, v19.2D
    trn2 v12.2D, v15.2D, v19.2D
    trn1 v23.2D, v14.2D, v18.2D
    trn1 v31.4S, v30.4S, v4.4S
    trn2 v5.4S, v11.4S, v9.4S
    trn2 v15.4S, v30.4S, v4.4S
    trn1 v29.4S, v23.4S, v12.4S
    trn2 v14.4S, v23.4S, v12.4S
    trn2 v4.8H, v31.8H, v5.8H
    trn1 v27.4S, v11.4S, v9.4S
    trn2 v11.8H, v29.8H, v15.8H
    trn1 v31.8H, v31.8H, v5.8H
    ushr v10.8H, v4.8H, #4
    trn2 v26.8H, v14.8H, v27.8H
    ushr v28.8H, v11.8H, #8
    ushr v21.8H, v31.8H, #8
    trn1 v1.8H, v29.8H, v15.8H
    ushr v18.8H, v26.8H, #12
    and v6.16B, v26.16B, v0.16B
    trn1 v19.8H, v14.8H, v27.8H
    shl v30.8H, v31.8H, #4
    shl v12.8H, v4.8H, #8
    and v23.16B, v1.16B, v0.16B
    eor v31.16B, v18.16B, v30.16B
    shl v13.8H, v11.8H, #4
    eor v3.16B, v21.16B, v12.16B
    ushr v9.8H, v1.8H, #12
    shl v2.8H, v19.8H, #8
    and v20.16B, v31.16B, v0.16B
    eor v12.16B, v9.16B, v13.16B
    ushr v17.8H, v19.8H, #4
    and v31.16B, v10.16B, v0.16B
    eor v9.16B, v28.16B, v2.16B
    and v13.16B, v17.16B, v0.16B
    and v15.16B, v12.16B, v0.16B
    and v10.16B, v9.16B, v0.16B
    and v3.16B, v3.16B, v0.16B
    // Accumulate four independent unsigned maxima.
    umax v7.8h, v7.8h, v6.8h
    umax v7.8h, v7.8h, v23.8h
    umax v22.8h, v22.8h, v20.8h
    umax v22.8h, v22.8h, v31.8h
    umax v24.8h, v24.8h, v13.8h
    umax v24.8h, v24.8h, v15.8h
    umax v25.8h, v25.8h, v10.8h
    umax v25.8h, v25.8h, v3.8h
    trn1 v21.8H, v6.8H, v20.8H
    trn1 v2.8H, v23.8H, v15.8H
    trn1 v4.8H, v3.8H, v31.8H
    trn1 v14.8H, v10.8H, v13.8H
    trn2 v9.8H, v10.8H, v13.8H
    trn2 v26.8H, v3.8H, v31.8H
    trn2 v28.4S, v2.4S, v14.4S
    trn2 v17.4S, v21.4S, v4.4S
    trn1 v19.4S, v2.4S, v14.4S
    trn2 v30.8H, v6.8H, v20.8H
    trn2 v20.2D, v28.2D, v17.2D
    trn2 v5.8H, v23.8H, v15.8H
    trn1 v27.4S, v30.4S, v26.4S
    umov x9, v20.d[1]
    trn2 v10.4S, v30.4S, v26.4S
    trn1 v14.2D, v28.2D, v17.2D
    trn2 v28.4S, v5.4S, v9.4S
    trn1 v30.4S, v21.4S, v4.4S
    trn1 v18.4S, v5.4S, v9.4S
    str x9, [x0, #784]
    umov x9, v14.d[1]
    trn2 v31.2D, v28.2D, v10.2D
    trn1 v3.2D, v28.2D, v10.2D
    trn1 v23.2D, v19.2D, v30.2D
    trn2 v4.2D, v19.2D, v30.2D
    str d14, [x0, #904]
    str x9, [x0, #880]
    trn1 v17.2D, v18.2D, v27.2D
    umov x9, v23.d[1]
    str d23, [x0, #952]
    str d4, [x0, #1480]
    trn2 v23.2D, v18.2D, v27.2D
    str d17, [x0, #1000]
    str x9, [x0, #928]
    umov x9, v4.d[1]
    str d31, [x0, #1504]
    str d23, [x0, #1408]
    str x9, [x0, #1456]
    umov x9, v23.d[1]
    str d3, [x0, #832]
    str x9, [x0, #1432]
    umov x9, v17.d[1]
    str x9, [x0, #976]
    umov x9, v3.d[1]
    str d20, [x0, #808]
    str x9, [x0, #856]
    umov x9, v31.d[1]
    str x9, [x0, #1528]
    // canonical blocks 160..175
    ld1 {v14.8H, v15.8H, v16.8H}, [x1], #48
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    trn2 v9.2D, v16.2D, v20.2D
    trn1 v4.2D, v16.2D, v20.2D
    trn2 v30.2D, v14.2D, v18.2D
    trn1 v11.2D, v15.2D, v19.2D
    trn2 v12.2D, v15.2D, v19.2D
    trn1 v23.2D, v14.2D, v18.2D
    trn1 v31.4S, v30.4S, v4.4S
    trn2 v5.4S, v11.4S, v9.4S
    trn2 v15.4S, v30.4S, v4.4S
    trn1 v29.4S, v23.4S, v12.4S
    trn2 v14.4S, v23.4S, v12.4S
    trn2 v4.8H, v31.8H, v5.8H
    trn1 v27.4S, v11.4S, v9.4S
    trn2 v11.8H, v29.8H, v15.8H
    trn1 v31.8H, v31.8H, v5.8H
    ushr v10.8H, v4.8H, #4
    trn2 v26.8H, v14.8H, v27.8H
    ushr v28.8H, v11.8H, #8
    ushr v21.8H, v31.8H, #8
    trn1 v1.8H, v29.8H, v15.8H
    ushr v18.8H, v26.8H, #12
    and v6.16B, v26.16B, v0.16B
    trn1 v19.8H, v14.8H, v27.8H
    shl v30.8H, v31.8H, #4
    shl v12.8H, v4.8H, #8
    and v23.16B, v1.16B, v0.16B
    eor v31.16B, v18.16B, v30.16B
    shl v13.8H, v11.8H, #4
    eor v3.16B, v21.16B, v12.16B
    ushr v9.8H, v1.8H, #12
    shl v2.8H, v19.8H, #8
    and v20.16B, v31.16B, v0.16B
    eor v12.16B, v9.16B, v13.16B
    ushr v17.8H, v19.8H, #4
    and v31.16B, v10.16B, v0.16B
    eor v9.16B, v28.16B, v2.16B
    and v13.16B, v17.16B, v0.16B
    and v15.16B, v12.16B, v0.16B
    and v10.16B, v9.16B, v0.16B
    and v3.16B, v3.16B, v0.16B
    // Accumulate four independent unsigned maxima.
    umax v7.8h, v7.8h, v6.8h
    umax v7.8h, v7.8h, v23.8h
    umax v22.8h, v22.8h, v20.8h
    umax v22.8h, v22.8h, v31.8h
    umax v24.8h, v24.8h, v13.8h
    umax v24.8h, v24.8h, v15.8h
    umax v25.8h, v25.8h, v10.8h
    umax v25.8h, v25.8h, v3.8h
    trn1 v21.8H, v6.8H, v20.8H
    trn1 v2.8H, v23.8H, v15.8H
    trn1 v4.8H, v3.8H, v31.8H
    trn1 v14.8H, v10.8H, v13.8H
    trn2 v9.8H, v10.8H, v13.8H
    trn2 v26.8H, v3.8H, v31.8H
    trn2 v28.4S, v2.4S, v14.4S
    trn2 v17.4S, v21.4S, v4.4S
    trn1 v19.4S, v2.4S, v14.4S
    trn2 v30.8H, v6.8H, v20.8H
    trn2 v20.2D, v28.2D, v17.2D
    trn2 v5.8H, v23.8H, v15.8H
    trn1 v27.4S, v30.4S, v26.4S
    umov x9, v20.d[1]
    trn2 v10.4S, v30.4S, v26.4S
    trn1 v14.2D, v28.2D, v17.2D
    trn2 v28.4S, v5.4S, v9.4S
    trn1 v30.4S, v21.4S, v4.4S
    trn1 v18.4S, v5.4S, v9.4S
    str x9, [x0, #1464]
    umov x9, v14.d[1]
    trn2 v31.2D, v28.2D, v10.2D
    trn1 v3.2D, v28.2D, v10.2D
    trn1 v23.2D, v19.2D, v30.2D
    trn2 v4.2D, v19.2D, v30.2D
    str d14, [x0, #1248]
    str x9, [x0, #1272]
    trn1 v17.2D, v18.2D, v27.2D
    umov x9, v23.d[1]
    str d23, [x0, #1152]
    str d4, [x0, #1344]
    trn2 v23.2D, v18.2D, v27.2D
    str d17, [x0, #1200]
    str x9, [x0, #1176]
    umov x9, v4.d[1]
    str d31, [x0, #1488]
    str d23, [x0, #1392]
    str x9, [x0, #1368]
    umov x9, v23.d[1]
    str d3, [x0, #1296]
    str x9, [x0, #1416]
    umov x9, v17.d[1]
    str x9, [x0, #1224]
    umov x9, v3.d[1]
    str d20, [x0, #1440]
    str x9, [x0, #1320]
    umov x9, v31.d[1]
    str x9, [x0, #1512]
    // canonical blocks 176..191
    ld1 {v14.8H, v15.8H, v16.8H}, [x1], #48
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    trn2 v9.2D, v16.2D, v20.2D
    trn1 v4.2D, v16.2D, v20.2D
    trn2 v30.2D, v14.2D, v18.2D
    trn1 v11.2D, v15.2D, v19.2D
    trn2 v12.2D, v15.2D, v19.2D
    trn1 v23.2D, v14.2D, v18.2D
    trn1 v31.4S, v30.4S, v4.4S
    trn2 v5.4S, v11.4S, v9.4S
    trn2 v15.4S, v30.4S, v4.4S
    trn1 v29.4S, v23.4S, v12.4S
    trn2 v14.4S, v23.4S, v12.4S
    trn2 v4.8H, v31.8H, v5.8H
    trn1 v27.4S, v11.4S, v9.4S
    trn2 v11.8H, v29.8H, v15.8H
    trn1 v31.8H, v31.8H, v5.8H
    ushr v10.8H, v4.8H, #4
    trn2 v26.8H, v14.8H, v27.8H
    ushr v28.8H, v11.8H, #8
    ushr v21.8H, v31.8H, #8
    trn1 v1.8H, v29.8H, v15.8H
    ushr v18.8H, v26.8H, #12
    and v6.16B, v26.16B, v0.16B
    trn1 v19.8H, v14.8H, v27.8H
    shl v30.8H, v31.8H, #4
    shl v12.8H, v4.8H, #8
    and v23.16B, v1.16B, v0.16B
    eor v31.16B, v18.16B, v30.16B
    shl v13.8H, v11.8H, #4
    eor v3.16B, v21.16B, v12.16B
    ushr v9.8H, v1.8H, #12
    shl v2.8H, v19.8H, #8
    and v20.16B, v31.16B, v0.16B
    eor v12.16B, v9.16B, v13.16B
    ushr v17.8H, v19.8H, #4
    and v31.16B, v10.16B, v0.16B
    eor v9.16B, v28.16B, v2.16B
    and v13.16B, v17.16B, v0.16B
    and v15.16B, v12.16B, v0.16B
    and v10.16B, v9.16B, v0.16B
    and v3.16B, v3.16B, v0.16B
    // Accumulate four independent unsigned maxima.
    umax v7.8h, v7.8h, v6.8h
    umax v7.8h, v7.8h, v23.8h
    umax v22.8h, v22.8h, v20.8h
    umax v22.8h, v22.8h, v31.8h
    umax v24.8h, v24.8h, v13.8h
    umax v24.8h, v24.8h, v15.8h
    umax v25.8h, v25.8h, v10.8h
    umax v25.8h, v25.8h, v3.8h
    trn1 v21.8H, v6.8H, v20.8H
    trn1 v2.8H, v23.8H, v15.8H
    trn1 v4.8H, v3.8H, v31.8H
    trn1 v14.8H, v10.8H, v13.8H
    trn2 v9.8H, v10.8H, v13.8H
    trn2 v26.8H, v3.8H, v31.8H
    trn2 v28.4S, v2.4S, v14.4S
    trn2 v17.4S, v21.4S, v4.4S
    trn1 v19.4S, v2.4S, v14.4S
    trn2 v30.8H, v6.8H, v20.8H
    trn2 v20.2D, v28.2D, v17.2D
    trn2 v5.8H, v23.8H, v15.8H
    trn1 v27.4S, v30.4S, v26.4S
    umov x9, v20.d[1]
    trn2 v10.4S, v30.4S, v26.4S
    trn1 v14.2D, v28.2D, v17.2D
    trn2 v28.4S, v5.4S, v9.4S
    trn1 v30.4S, v21.4S, v4.4S
    trn1 v18.4S, v5.4S, v9.4S
    str x9, [x0, #840]
    umov x9, v14.d[1]
    trn2 v31.2D, v28.2D, v10.2D
    trn1 v3.2D, v28.2D, v10.2D
    trn1 v23.2D, v19.2D, v30.2D
    trn2 v4.2D, v19.2D, v30.2D
    str d14, [x0, #1056]
    str x9, [x0, #1080]
    trn1 v17.2D, v18.2D, v27.2D
    umov x9, v23.d[1]
    str d23, [x0, #960]
    str d4, [x0, #864]
    trn2 v23.2D, v18.2D, v27.2D
    str d17, [x0, #1008]
    str x9, [x0, #984]
    umov x9, v4.d[1]
    str d31, [x0, #792]
    str d23, [x0, #912]
    str x9, [x0, #888]
    umov x9, v23.d[1]
    str d3, [x0, #1104]
    str x9, [x0, #936]
    umov x9, v17.d[1]
    str x9, [x0, #1032]
    umov x9, v3.d[1]
    str d20, [x0, #816]
    str x9, [x0, #1128]
    umov x9, v31.d[1]
    str x9, [x0, #768]
    umax v7.8h, v7.8h, v22.8h
    umax v24.8h, v24.8h, v25.8h
    umax v7.8h, v7.8h, v24.8h
    cmhs v7.8h, v7.8h, v8.8h
    umaxv h22, v7.8h
    umov w0, v22.h[0]
    cmp w0, #0
    cset w0, ne
    ldp d8, d9, [sp, #0]
    ldp d10, d11, [sp, #16]
    ldp d12, d13, [sp, #32]
    ldp d14, d15, [sp, #48]
    add sp, sp, #64
    ret

.p2align 4
.Lcanonical_unpack_candidate_mask:
    .hword 0x0fff, 0x0fff, 0x0fff, 0x0fff
    .hword 0x0fff, 0x0fff, 0x0fff, 0x0fff
