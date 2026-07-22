// Mechanical U0 extraction from production poly_frombytes_gt_canonical.
slothy_start_gt_canonical_unpack_chunk_u0:
    ld1 {v18.8H, v19.8H, v20.8H}, [x1], #48
    ld1 {v26.8H, v27.8H, v28.8H}, [x1], #48
    trn1 v31.2D, v18.2D, v26.2D
    trn2 v14.2D, v18.2D, v26.2D
    trn2 v2.2D, v19.2D, v27.2D
    trn1 v17.2D, v20.2D, v28.2D
    trn1 v27.2D, v19.2D, v27.2D
    trn2 v30.2D, v20.2D, v28.2D
    trn2 v15.4S, v14.4S, v17.4S
    trn1 v29.4S, v31.4S, v2.4S
    trn2 v23.4S, v31.4S, v2.4S
    trn1 v21.4S, v27.4S, v30.4S
    trn2 v13.8H, v29.8H, v15.8H
    trn1 v16.8H, v29.8H, v15.8H
    trn1 v18.4S, v14.4S, v17.4S
    trn1 v25.8H, v23.8H, v21.8H
    trn2 v2.4S, v27.4S, v30.4S
    ushr v5.8H, v13.8H, #8
    shl v20.8H, v25.8H, #8
    and v24.16B, v16.16B, v0.16B
    shl v19.8H, v13.8H, #4
    trn1 v4.8H, v18.8H, v2.8H
    ushr v10.8H, v16.8H, #12
    eor v29.16B, v5.16B, v20.16B
    trn2 v15.8H, v18.8H, v2.8H
    ushr v5.8H, v25.8H, #4
    eor v19.16B, v10.16B, v19.16B
    and v26.16B, v29.16B, v0.16B
    and v27.16B, v5.16B, v0.16B
    shl v22.8H, v4.8H, #4
    and v25.16B, v19.16B, v0.16B
    shl v5.8H, v15.8H, #8
    trn2 v29.8H, v23.8H, v21.8H
    ushr v13.8H, v15.8H, #4
    ushr v6.8H, v4.8H, #8
    ushr v28.8H, v29.8H, #12
    eor v6.16B, v6.16B, v5.16B
    eor v30.16B, v28.16B, v22.16B
    and v14.16B, v29.16B, v0.16B
    and v16.16B, v6.16B, v0.16B
    and v17.16B, v13.16B, v0.16B
    and v15.16B, v30.16B, v0.16B
    trn1 v1.8h, v24.8h, v25.8h
    trn2 v2.8h, v24.8h, v25.8h
    trn1 v3.8h, v26.8h, v27.8h
    trn2 v4.8h, v26.8h, v27.8h
    trn1 v5.8h, v14.8h, v15.8h
    trn2 v6.8h, v14.8h, v15.8h
    trn1 v7.8h, v16.8h, v17.8h
    trn2 v8.8h, v16.8h, v17.8h
    trn1 v24.4s, v1.4s, v3.4s
    trn2 v26.4s, v1.4s, v3.4s
    trn1 v25.4s, v2.4s, v4.4s
    trn2 v27.4s, v2.4s, v4.4s
    trn1 v14.4s, v5.4s, v7.4s
    trn2 v16.4s, v5.4s, v7.4s
    trn1 v15.4s, v6.4s, v8.4s
    trn2 v17.4s, v6.4s, v8.4s
    trn2 v1.2d, v24.2d, v14.2d
    trn1 v24.2d, v24.2d, v14.2d
    mov v14.16b, v1.16b
    trn2 v2.2d, v25.2d, v15.2d
    trn1 v25.2d, v25.2d, v15.2d
    mov v15.16b, v2.16b
    trn2 v3.2d, v26.2d, v16.2d
    trn1 v26.2d, v26.2d, v16.2d
    mov v16.16b, v3.16b
    trn2 v4.2d, v27.2d, v17.2d
    trn1 v27.2d, v27.2d, v17.2d
    mov v17.16b, v4.16b
    str d24, [x0, #312]
    umov x9, v24.d[1]
    str x9, [x0, #288]
    str d25, [x0, #360]
    umov x9, v25.d[1]
    str x9, [x0, #336]
    str d26, [x0, #264]
    umov x9, v26.d[1]
    str x9, [x0, #240]
    str d27, [x0, #192]
    umov x9, v27.d[1]
    str x9, [x0, #216]
    str d14, [x0, #72]
    umov x9, v14.d[1]
    str x9, [x0, #48]
    str d15, [x0, #0]
    umov x9, v15.d[1]
    str x9, [x0, #24]
    str d16, [x0, #168]
    umov x9, v16.d[1]
    str x9, [x0, #144]
    str d17, [x0, #96]
    umov x9, v17.d[1]
    str x9, [x0, #120]
slothy_end_gt_canonical_unpack_chunk_u0:
