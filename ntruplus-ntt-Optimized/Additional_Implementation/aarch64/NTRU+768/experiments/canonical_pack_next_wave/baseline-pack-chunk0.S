// Exact extraction from asm/gt/support/poly_canonical_pack.S.
// Live-in: x0=dst, x1=GT source base, v0=q.
// Live-out: x0 advanced by 96 and canonical blocks 0..15 stored.
// Range: each source lane is in [-3457,3456].
// Reserved physical registers: x2-x30 and sp.
slothy_start_gt_canonical_pack_chunk0_baseline:
    ldr d9, [x1, #312]
    ldr d8, [x1, #288]
    ins v9.d[1], v8.d[0]
    ldr d10, [x1, #360]
    ldr d8, [x1, #336]
    ins v10.d[1], v8.d[0]
    ldr d11, [x1, #264]
    ldr d8, [x1, #240]
    ins v11.d[1], v8.d[0]
    ldr d12, [x1, #192]
    ldr d8, [x1, #216]
    ins v12.d[1], v8.d[0]
    ldr d26, [x1, #72]
    ldr d8, [x1, #48]
    ins v26.d[1], v8.d[0]
    ldr d27, [x1, #0]
    ldr d8, [x1, #24]
    ins v27.d[1], v8.d[0]
    ldr d28, [x1, #168]
    ldr d8, [x1, #144]
    ins v28.d[1], v8.d[0]
    ldr d29, [x1, #96]
    ldr d8, [x1, #120]
    ins v29.d[1], v8.d[0]
    trn1 v1.8h, v9.8h, v10.8h
    trn2 v2.8h, v9.8h, v10.8h
    trn1 v3.8h, v11.8h, v12.8h
    trn2 v4.8h, v11.8h, v12.8h
    trn1 v5.8h, v26.8h, v27.8h
    trn2 v6.8h, v26.8h, v27.8h
    trn1 v7.8h, v28.8h, v29.8h
    trn2 v8.8h, v28.8h, v29.8h
    trn1 v9.4s, v1.4s, v3.4s
    trn2 v11.4s, v1.4s, v3.4s
    trn1 v10.4s, v2.4s, v4.4s
    trn2 v12.4s, v2.4s, v4.4s
    trn1 v26.4s, v5.4s, v7.4s
    trn2 v28.4s, v5.4s, v7.4s
    trn1 v27.4s, v6.4s, v8.4s
    trn2 v29.4s, v6.4s, v8.4s
    trn2 v1.2d, v9.2d, v26.2d
    trn1 v9.2d, v9.2d, v26.2d
    mov v26.16b, v1.16b
    trn2 v2.2d, v10.2d, v27.2d
    trn1 v10.2d, v10.2d, v27.2d
    mov v27.16b, v2.16b
    trn2 v3.2d, v11.2d, v28.2d
    trn1 v11.2d, v11.2d, v28.2d
    mov v28.16b, v3.16b
    trn2 v4.2d, v12.2d, v29.2d
    trn1 v12.2d, v12.2d, v29.2d
    mov v29.16b, v4.16b
    sshr v8.8H, v9.8H, #15
    sshr v30.8H, v10.8H, #15
    and v25.16B, v8.16B, v0.16B
    sshr v24.8H, v12.8H, #15
    sshr v18.8H, v11.8H, #15
    and v30.16B, v30.16B, v0.16B
    add v7.8H, v9.8H, v25.8H
    and v4.16B, v24.16B, v0.16B
    sshr v3.8H, v26.8H, #15
    and v9.16B, v18.16B, v0.16B
    add v24.8H, v12.8H, v4.8H
    sshr v19.8H, v29.8H, #15
    add v21.8H, v11.8H, v9.8H
    sshr v9.8H, v27.8H, #15
    and v19.16B, v19.16B, v0.16B
    shl v11.8H, v24.8H, #4
    and v25.16B, v9.16B, v0.16B
    sshr v1.8H, v28.8H, #15
    add v10.8H, v10.8H, v30.8H
    add v9.8H, v29.8H, v19.8H
    add v25.8H, v27.8H, v25.8H
    ushr v8.8H, v21.8H, #8
    and v22.16B, v3.16B, v0.16B
    ushr v20.8H, v10.8H, #4
    shl v24.8H, v9.8H, #4
    and v3.16B, v1.16B, v0.16B
    eor v11.16B, v8.16B, v11.16B
    ushr v15.8H, v25.8H, #4
    add v2.8H, v28.8H, v3.8H
    shl v19.8H, v10.8H, #12
    shl v18.8H, v21.8H, #8
    add v5.8H, v26.8H, v22.8H
    shl v25.8H, v25.8H, #12
    eor v31.16B, v7.16B, v19.16B
    shl v9.8H, v2.8H, #8
    eor v6.16B, v20.16B, v18.16B
    ushr v3.8H, v2.8H, #8
    eor v8.16B, v5.16B, v25.16B
    trn1 v1.8H, v31.8H, v6.8H
    eor v27.16B, v15.16B, v9.16B
    eor v3.16B, v3.16B, v24.16B
    trn1 v9.8H, v11.8H, v8.8H
    trn2 v30.8H, v31.8H, v6.8H
    trn2 v5.8H, v11.8H, v8.8H
    trn2 v14.4S, v1.4S, v9.4S
    trn2 v8.8H, v27.8H, v3.8H
    trn1 v18.8H, v27.8H, v3.8H
    trn1 v25.4S, v1.4S, v9.4S
    trn1 v22.4S, v5.4S, v8.4S
    trn2 v24.4S, v5.4S, v8.4S
    trn1 v10.4S, v18.4S, v30.4S
    trn2 v18.4S, v18.4S, v30.4S
    trn1 v2.2D, v22.2D, v14.2D
    trn2 v5.2D, v22.2D, v14.2D
    trn1 v1.2D, v25.2D, v10.2D
    trn1 v3.2D, v18.2D, v24.2D
    trn2 v4.2D, v25.2D, v10.2D
    trn2 v6.2D, v18.2D, v24.2D
    st1 {v1.8h, v2.8h, v3.8h}, [x0], #48
    st1 {v4.8h, v5.8h, v6.8h}, [x0], #48
slothy_end_gt_canonical_pack_chunk0_baseline:
