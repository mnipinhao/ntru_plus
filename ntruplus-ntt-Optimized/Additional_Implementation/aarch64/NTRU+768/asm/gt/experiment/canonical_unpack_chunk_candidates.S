// Generated canonical-unpack chunk candidates; experiment only.
.text

.p2align 4
.global poly_frombytes_gt_chunk0_u0
.global _poly_frombytes_gt_chunk0_u0
poly_frombytes_gt_chunk0_u0:
_poly_frombytes_gt_chunk0_u0:
    sub sp, sp, #64
    stp d8, d9, [sp, #0]
    stp d10, d11, [sp, #16]
    stp d12, d13, [sp, #32]
    stp d14, d15, [sp, #48]
    mov w2, #0x0fff
    dup v0.8h, w2
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
    ldp d8, d9, [sp, #0]
    ldp d10, d11, [sp, #16]
    ldp d12, d13, [sp, #32]
    ldp d14, d15, [sp, #48]
    add sp, sp, #64
    ret

.p2align 4
.global poly_frombytes_gt_chunk0_u1
.global _poly_frombytes_gt_chunk0_u1
poly_frombytes_gt_chunk0_u1:
_poly_frombytes_gt_chunk0_u1:
    sub sp, sp, #64
    stp d8, d9, [sp, #0]
    stp d10, d11, [sp, #16]
    stp d12, d13, [sp, #32]
    stp d14, d15, [sp, #48]
    mov w2, #0x0fff
    dup v0.8h, w2
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
    ldp d8, d9, [sp, #0]
    ldp d10, d11, [sp, #16]
    ldp d12, d13, [sp, #32]
    ldp d14, d15, [sp, #48]
    add sp, sp, #64
    ret
