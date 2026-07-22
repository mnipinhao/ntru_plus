// Generated cross-chunk scheduling candidate; experiment only.
.text

.p2align 4
.global poly_tobytes_gt_canonical_cross_chunk
.global _poly_tobytes_gt_canonical_cross_chunk
poly_tobytes_gt_canonical_cross_chunk:
_poly_tobytes_gt_canonical_cross_chunk:
    sub sp, sp, #64
    stp d8, d9, [sp, #0]
    stp d10, d11, [sp, #16]
    stp d12, d13, [sp, #32]
    stp d14, d15, [sp, #48]
    adr x2, .Lcanonical_pack_cross_chunk_q
    ldr q0, [x2]
    // canonical blocks 0..31
    ldr d9, [x1, #312]
    ldr d1, [x1, #576]
    ldr d27, [x1, #336]
    ldr d24, [x1, #600]
    ldr d8, [x1, #24]
    ldr d13, [x1, #0]
    ldr d7, [x1, #360]
    ldr d11, [x1, #264]
    ldr d10, [x1, #288]
    ldr d29, [x1, #240]
    mov v1.d[1], v24.d[0]
    ldr d31, [x1, #192]
    mov v13.d[1], v8.d[0]
    ldr d20, [x1, #48]
    mov v7.d[1], v27.d[0]
    ldr d8, [x1, #216]
    ldr d16, [x1, #72]
    mov v9.d[1], v10.d[0]
    mov v11.d[1], v29.d[0]
    sshr v24.8H, v7.8H, #15
    ldr d3, [x1, #168]
    ldr d19, [x1, #96]
    sshr v29.8H, v13.8H, #15
    ldr d10, [x1, #120]
    ldr d6, [x1, #144]
    mov v31.d[1], v8.d[0]
    mov v16.d[1], v20.d[0]
    sshr v21.8H, v9.8H, #15
    sshr v22.8H, v11.8H, #15
    and v24.16B, v24.16B, v0.16B
    and v14.16B, v21.16B, v0.16B
    sshr v8.8H, v31.8H, #15
    and v27.16B, v22.16B, v0.16B
    mov v3.d[1], v6.d[0]
    mov v19.d[1], v10.d[0]
    and v8.16B, v8.16B, v0.16B
    add v20.8H, v11.8H, v27.8H
    add v10.8H, v7.8H, v24.8H
    sshr v22.8H, v16.8H, #15
    add v11.8H, v9.8H, v14.8H
    add v28.8H, v31.8H, v8.8H
    sshr v24.8H, v19.8H, #15
    and v22.16B, v22.16B, v0.16B
    sshr v8.8H, v3.8H, #15
    and v24.16B, v24.16B, v0.16B
    and v29.16B, v29.16B, v0.16B
    add v27.8H, v16.8H, v22.8H
    and v8.16B, v8.16B, v0.16B
    add v22.8H, v13.8H, v29.8H
    add v24.8H, v19.8H, v24.8H
    trn2 v19.8H, v11.8H, v10.8H
    add v8.8H, v3.8H, v8.8H
    trn1 v10.8H, v11.8H, v10.8H
    trn1 v9.8H, v20.8H, v28.8H
    trn2 v3.8H, v20.8H, v28.8H
    trn1 v16.8H, v27.8H, v22.8H
    trn2 v30.8H, v8.8H, v24.8H
    trn2 v27.8H, v27.8H, v22.8H
    trn1 v23.4S, v10.4S, v9.4S
    trn1 v7.8H, v8.8H, v24.8H
    trn1 v22.4S, v19.4S, v3.4S
    trn1 v24.4S, v27.4S, v30.4S
    trn2 v10.4S, v10.4S, v9.4S
    trn2 v21.4S, v16.4S, v7.4S
    trn2 v11.4S, v19.4S, v3.4S
    trn1 v6.2D, v22.2D, v24.2D
    trn2 v14.4S, v27.4S, v30.4S
    trn1 v27.2D, v10.2D, v21.2D
    trn2 v13.2D, v22.2D, v24.2D
    ushr v20.8H, v6.8H, #4
    ushr v3.8H, v27.8H, #8
    trn2 v8.2D, v10.2D, v21.2D
    ushr v22.8H, v13.8H, #4
    trn1 v31.4S, v16.4S, v7.4S
    ushr v19.8H, v8.8H, #8
    trn1 v24.2D, v11.2D, v14.2D
    shl v29.8H, v6.8H, #12
    ldr d12, [x1, #528]
    shl v7.8H, v24.8H, #4
    trn1 v16.2D, v23.2D, v31.2D
    shl v18.8H, v27.8H, #8
    trn2 v14.2D, v11.2D, v14.2D
    shl v24.8H, v8.8H, #8
    eor v29.16B, v16.16B, v29.16B
    shl v27.8H, v13.8H, #12
    trn2 v13.2D, v23.2D, v31.2D
    eor v22.16B, v22.16B, v24.16B
    shl v8.8H, v14.8H, #4
    eor v14.16B, v13.16B, v27.16B
    eor v24.16B, v20.16B, v18.16B
    ldr d20, [x1, #696]
    eor v27.16B, v19.16B, v8.16B
    ldr d8, [x1, #672]
    eor v26.16B, v3.16B, v7.16B
    trn2 v10.8H, v29.8H, v24.8H
    trn1 v16.8H, v29.8H, v24.8H
    trn1 v7.8H, v22.8H, v27.8H
    trn2 v29.8H, v22.8H, v27.8H
    ldr d24, [x1, #720]
    ldr d19, [x1, #744]
    mov v20.d[1], v8.d[0]
    trn1 v13.8H, v26.8H, v14.8H
    trn2 v8.8H, v26.8H, v14.8H
    ldr d14, [x1, #648]
    trn1 v3.4S, v7.4S, v10.4S
    trn1 v11.4S, v16.4S, v13.4S
    mov v19.d[1], v24.d[0]
    ldr d24, [x1, #624]
    trn2 v27.4S, v8.4S, v29.4S
    ldr d31, [x1, #456]
    trn1 v22.4S, v8.4S, v29.4S
    trn2 v8.4S, v16.4S, v13.4S
    trn2 v6.4S, v7.4S, v10.4S
    ldr d16, [x1, #384]
    ldr d13, [x1, #552]
    mov v14.d[1], v24.d[0]
    ldr d29, [x1, #408]
    trn1 v10.2D, v6.2D, v27.2D
    trn1 v9.2D, v22.2D, v8.2D
    sshr v17.8H, v1.8H, #15
    trn2 v4.2D, v11.2D, v3.2D
    trn2 v5.2D, v22.2D, v8.2D
    ldr d22, [x1, #432]
    trn1 v8.2D, v11.2D, v3.2D
    sshr v24.8H, v20.8H, #15
    mov v16.d[1], v29.d[0]
    trn2 v6.2D, v6.2D, v27.2D
    st1 {v8.8H, v9.8H, v10.8H}, [x0], #48
    ldr d3, [x1, #480]
    mov v13.d[1], v12.d[0]
    sshr v10.8H, v19.8H, #15
    ldr d8, [x1, #504]
    mov v31.d[1], v22.d[0]
    sshr v22.8H, v13.8H, #15
    and v27.16B, v24.16B, v0.16B
    sshr v24.8H, v16.8H, #15
    and v22.16B, v22.16B, v0.16B
    sshr v12.8H, v31.8H, #15
    sshr v18.8H, v14.8H, #15
    mov v3.d[1], v8.d[0]
    add v7.8H, v20.8H, v27.8H
    add v27.8H, v13.8H, v22.8H
    and v22.16B, v18.16B, v0.16B
    and v10.16B, v10.16B, v0.16B
    sshr v8.8H, v3.8H, #15
    and v29.16B, v17.16B, v0.16B
    add v19.8H, v19.8H, v10.8H
    add v20.8H, v14.8H, v22.8H
    add v1.8H, v1.8H, v29.8H
    and v17.16B, v24.16B, v0.16B
    trn1 v22.8H, v7.8H, v19.8H
    and v10.16B, v12.16B, v0.16B
    trn1 v24.8H, v20.8H, v1.8H
    add v12.8H, v16.8H, v17.8H
    and v8.16B, v8.16B, v0.16B
    add v14.8H, v31.8H, v10.8H
    trn2 v19.8H, v7.8H, v19.8H
    trn2 v10.4S, v22.4S, v24.4S
    add v8.8H, v3.8H, v8.8H
    trn2 v31.8H, v14.8H, v12.8H
    st1 {v4.8H, v5.8H, v6.8H}, [x0], #48
    trn1 v29.8H, v14.8H, v12.8H
    trn2 v17.8H, v27.8H, v8.8H
    trn2 v1.8H, v20.8H, v1.8H
    trn1 v3.4S, v22.4S, v24.4S
    trn1 v12.8H, v27.8H, v8.8H
    trn1 v15.4S, v31.4S, v17.4S
    trn1 v22.4S, v19.4S, v1.4S
    trn2 v20.4S, v31.4S, v17.4S
    trn2 v8.4S, v29.4S, v12.4S
    trn1 v27.4S, v29.4S, v12.4S
    trn1 v29.2D, v22.2D, v15.2D
    trn1 v12.2D, v10.2D, v8.2D
    trn2 v16.4S, v19.4S, v1.4S
    trn2 v24.2D, v22.2D, v15.2D
    shl v22.8H, v29.8H, #12
    ushr v14.8H, v29.8H, #4
    trn2 v7.2D, v10.2D, v8.2D
    shl v15.8H, v12.8H, #8
    trn1 v13.2D, v3.2D, v27.2D
    ushr v19.8H, v24.8H, #4
    trn2 v3.2D, v3.2D, v27.2D
    eor v17.16B, v14.16B, v15.16B
    ushr v10.8H, v12.8H, #8
    eor v9.16B, v13.16B, v22.16B
    shl v27.8H, v7.8H, #8
    shl v8.8H, v24.8H, #12
    trn1 v29.2D, v16.2D, v20.2D
    ushr v12.8H, v7.8H, #8
    trn2 v20.2D, v16.2D, v20.2D
    trn2 v18.8H, v9.8H, v17.8H
    shl v29.8H, v29.8H, #4
    eor v8.16B, v3.16B, v8.16B
    shl v11.8H, v20.8H, #4
    trn1 v15.8H, v9.8H, v17.8H
    eor v29.16B, v10.16B, v29.16B
    eor v14.16B, v12.16B, v11.16B
    eor v13.16B, v19.16B, v27.16B
    trn1 v24.8H, v29.8H, v8.8H
    trn2 v27.8H, v29.8H, v8.8H
    trn2 v2.8H, v13.8H, v14.8H
    trn1 v29.8H, v13.8H, v14.8H
    trn2 v5.4S, v15.4S, v24.4S
    trn1 v14.4S, v15.4S, v24.4S
    trn2 v15.4S, v27.4S, v2.4S
    trn1 v17.4S, v27.4S, v2.4S
    trn2 v22.4S, v29.4S, v18.4S
    trn1 v1.4S, v29.4S, v18.4S
    trn1 v9.2D, v17.2D, v5.2D
    trn1 v10.2D, v22.2D, v15.2D
    trn1 v8.2D, v14.2D, v1.2D
    trn2 v25.2D, v17.2D, v5.2D
    trn2 v24.2D, v14.2D, v1.2D
    st1 {v8.8H, v9.8H, v10.8H}, [x0], #48
    trn2 v26.2D, v22.2D, v15.2D
    st1 {v24.8H, v25.8H, v26.8H}, [x0], #48
    // canonical blocks 32..63
    ldr d9, [x1, #128]
    ldr d1, [x1, #80]
    ldr d27, [x1, #200]
    ldr d24, [x1, #104]
    ldr d8, [x1, #392]
    ldr d13, [x1, #368]
    ldr d7, [x1, #176]
    ldr d11, [x1, #224]
    ldr d10, [x1, #152]
    ldr d29, [x1, #248]
    mov v1.d[1], v24.d[0]
    ldr d31, [x1, #272]
    mov v13.d[1], v8.d[0]
    ldr d20, [x1, #344]
    mov v7.d[1], v27.d[0]
    ldr d8, [x1, #296]
    ldr d16, [x1, #320]
    mov v9.d[1], v10.d[0]
    mov v11.d[1], v29.d[0]
    sshr v24.8H, v7.8H, #15
    ldr d3, [x1, #416]
    ldr d19, [x1, #464]
    sshr v29.8H, v13.8H, #15
    ldr d10, [x1, #488]
    ldr d6, [x1, #440]
    mov v31.d[1], v8.d[0]
    mov v16.d[1], v20.d[0]
    sshr v21.8H, v9.8H, #15
    sshr v22.8H, v11.8H, #15
    and v24.16B, v24.16B, v0.16B
    and v14.16B, v21.16B, v0.16B
    sshr v8.8H, v31.8H, #15
    and v27.16B, v22.16B, v0.16B
    mov v3.d[1], v6.d[0]
    mov v19.d[1], v10.d[0]
    and v8.16B, v8.16B, v0.16B
    add v20.8H, v11.8H, v27.8H
    add v10.8H, v7.8H, v24.8H
    sshr v22.8H, v16.8H, #15
    add v11.8H, v9.8H, v14.8H
    add v28.8H, v31.8H, v8.8H
    sshr v24.8H, v19.8H, #15
    and v22.16B, v22.16B, v0.16B
    sshr v8.8H, v3.8H, #15
    and v24.16B, v24.16B, v0.16B
    and v29.16B, v29.16B, v0.16B
    add v27.8H, v16.8H, v22.8H
    and v8.16B, v8.16B, v0.16B
    add v22.8H, v13.8H, v29.8H
    add v24.8H, v19.8H, v24.8H
    trn2 v19.8H, v11.8H, v10.8H
    add v8.8H, v3.8H, v8.8H
    trn1 v10.8H, v11.8H, v10.8H
    trn1 v9.8H, v20.8H, v28.8H
    trn2 v3.8H, v20.8H, v28.8H
    trn1 v16.8H, v27.8H, v22.8H
    trn2 v30.8H, v8.8H, v24.8H
    trn2 v27.8H, v27.8H, v22.8H
    trn1 v23.4S, v10.4S, v9.4S
    trn1 v7.8H, v8.8H, v24.8H
    trn1 v22.4S, v19.4S, v3.4S
    trn1 v24.4S, v27.4S, v30.4S
    trn2 v10.4S, v10.4S, v9.4S
    trn2 v21.4S, v16.4S, v7.4S
    trn2 v11.4S, v19.4S, v3.4S
    trn1 v6.2D, v22.2D, v24.2D
    trn2 v14.4S, v27.4S, v30.4S
    trn1 v27.2D, v10.2D, v21.2D
    trn2 v13.2D, v22.2D, v24.2D
    ushr v20.8H, v6.8H, #4
    ushr v3.8H, v27.8H, #8
    trn2 v8.2D, v10.2D, v21.2D
    ushr v22.8H, v13.8H, #4
    trn1 v31.4S, v16.4S, v7.4S
    ushr v19.8H, v8.8H, #8
    trn1 v24.2D, v11.2D, v14.2D
    shl v29.8H, v6.8H, #12
    ldr d12, [x1, #584]
    shl v7.8H, v24.8H, #4
    trn1 v16.2D, v23.2D, v31.2D
    shl v18.8H, v27.8H, #8
    trn2 v14.2D, v11.2D, v14.2D
    shl v24.8H, v8.8H, #8
    eor v29.16B, v16.16B, v29.16B
    shl v27.8H, v13.8H, #12
    trn2 v13.2D, v23.2D, v31.2D
    eor v22.16B, v22.16B, v24.16B
    shl v8.8H, v14.8H, #4
    eor v14.16B, v13.16B, v27.16B
    eor v24.16B, v20.16B, v18.16B
    ldr d20, [x1, #704]
    eor v27.16B, v19.16B, v8.16B
    ldr d8, [x1, #728]
    eor v26.16B, v3.16B, v7.16B
    trn2 v10.8H, v29.8H, v24.8H
    trn1 v16.8H, v29.8H, v24.8H
    trn1 v7.8H, v22.8H, v27.8H
    trn2 v29.8H, v22.8H, v27.8H
    ldr d24, [x1, #8]
    ldr d19, [x1, #752]
    mov v20.d[1], v8.d[0]
    trn1 v13.8H, v26.8H, v14.8H
    trn2 v8.8H, v26.8H, v14.8H
    ldr d14, [x1, #32]
    trn1 v3.4S, v7.4S, v10.4S
    trn1 v11.4S, v16.4S, v13.4S
    mov v19.d[1], v24.d[0]
    ldr d24, [x1, #56]
    trn2 v27.4S, v8.4S, v29.4S
    ldr d31, [x1, #608]
    trn1 v22.4S, v8.4S, v29.4S
    trn2 v8.4S, v16.4S, v13.4S
    trn2 v6.4S, v7.4S, v10.4S
    ldr d16, [x1, #656]
    ldr d13, [x1, #560]
    mov v14.d[1], v24.d[0]
    ldr d29, [x1, #680]
    trn1 v10.2D, v6.2D, v27.2D
    trn1 v9.2D, v22.2D, v8.2D
    sshr v17.8H, v1.8H, #15
    trn2 v4.2D, v11.2D, v3.2D
    trn2 v5.2D, v22.2D, v8.2D
    ldr d22, [x1, #632]
    trn1 v8.2D, v11.2D, v3.2D
    sshr v24.8H, v20.8H, #15
    mov v16.d[1], v29.d[0]
    trn2 v6.2D, v6.2D, v27.2D
    st1 {v8.8H, v9.8H, v10.8H}, [x0], #48
    ldr d3, [x1, #536]
    mov v13.d[1], v12.d[0]
    sshr v10.8H, v19.8H, #15
    ldr d8, [x1, #512]
    mov v31.d[1], v22.d[0]
    sshr v22.8H, v13.8H, #15
    and v27.16B, v24.16B, v0.16B
    sshr v24.8H, v16.8H, #15
    and v22.16B, v22.16B, v0.16B
    sshr v12.8H, v31.8H, #15
    sshr v18.8H, v14.8H, #15
    mov v3.d[1], v8.d[0]
    add v7.8H, v20.8H, v27.8H
    add v27.8H, v13.8H, v22.8H
    and v22.16B, v18.16B, v0.16B
    and v10.16B, v10.16B, v0.16B
    sshr v8.8H, v3.8H, #15
    and v29.16B, v17.16B, v0.16B
    add v19.8H, v19.8H, v10.8H
    add v20.8H, v14.8H, v22.8H
    add v1.8H, v1.8H, v29.8H
    and v17.16B, v24.16B, v0.16B
    trn1 v22.8H, v7.8H, v19.8H
    and v10.16B, v12.16B, v0.16B
    trn1 v24.8H, v20.8H, v1.8H
    add v12.8H, v16.8H, v17.8H
    and v8.16B, v8.16B, v0.16B
    add v14.8H, v31.8H, v10.8H
    trn2 v19.8H, v7.8H, v19.8H
    trn2 v10.4S, v22.4S, v24.4S
    add v8.8H, v3.8H, v8.8H
    trn2 v31.8H, v14.8H, v12.8H
    st1 {v4.8H, v5.8H, v6.8H}, [x0], #48
    trn1 v29.8H, v14.8H, v12.8H
    trn2 v17.8H, v27.8H, v8.8H
    trn2 v1.8H, v20.8H, v1.8H
    trn1 v3.4S, v22.4S, v24.4S
    trn1 v12.8H, v27.8H, v8.8H
    trn1 v15.4S, v31.4S, v17.4S
    trn1 v22.4S, v19.4S, v1.4S
    trn2 v20.4S, v31.4S, v17.4S
    trn2 v8.4S, v29.4S, v12.4S
    trn1 v27.4S, v29.4S, v12.4S
    trn1 v29.2D, v22.2D, v15.2D
    trn1 v12.2D, v10.2D, v8.2D
    trn2 v16.4S, v19.4S, v1.4S
    trn2 v24.2D, v22.2D, v15.2D
    shl v22.8H, v29.8H, #12
    ushr v14.8H, v29.8H, #4
    trn2 v7.2D, v10.2D, v8.2D
    shl v15.8H, v12.8H, #8
    trn1 v13.2D, v3.2D, v27.2D
    ushr v19.8H, v24.8H, #4
    trn2 v3.2D, v3.2D, v27.2D
    eor v17.16B, v14.16B, v15.16B
    ushr v10.8H, v12.8H, #8
    eor v9.16B, v13.16B, v22.16B
    shl v27.8H, v7.8H, #8
    shl v8.8H, v24.8H, #12
    trn1 v29.2D, v16.2D, v20.2D
    ushr v12.8H, v7.8H, #8
    trn2 v20.2D, v16.2D, v20.2D
    trn2 v18.8H, v9.8H, v17.8H
    shl v29.8H, v29.8H, #4
    eor v8.16B, v3.16B, v8.16B
    shl v11.8H, v20.8H, #4
    trn1 v15.8H, v9.8H, v17.8H
    eor v29.16B, v10.16B, v29.16B
    eor v14.16B, v12.16B, v11.16B
    eor v13.16B, v19.16B, v27.16B
    trn1 v24.8H, v29.8H, v8.8H
    trn2 v27.8H, v29.8H, v8.8H
    trn2 v2.8H, v13.8H, v14.8H
    trn1 v29.8H, v13.8H, v14.8H
    trn2 v5.4S, v15.4S, v24.4S
    trn1 v14.4S, v15.4S, v24.4S
    trn2 v15.4S, v27.4S, v2.4S
    trn1 v17.4S, v27.4S, v2.4S
    trn2 v22.4S, v29.4S, v18.4S
    trn1 v1.4S, v29.4S, v18.4S
    trn1 v9.2D, v17.2D, v5.2D
    trn1 v10.2D, v22.2D, v15.2D
    trn1 v8.2D, v14.2D, v1.2D
    trn2 v25.2D, v17.2D, v5.2D
    trn2 v24.2D, v14.2D, v1.2D
    st1 {v8.8H, v9.8H, v10.8H}, [x0], #48
    trn2 v26.2D, v22.2D, v15.2D
    st1 {v24.8H, v25.8H, v26.8H}, [x0], #48
    // canonical blocks 64..95
    ldr d9, [x1, #400]
    ldr d1, [x1, #712]
    ldr d27, [x1, #352]
    ldr d24, [x1, #688]
    ldr d8, [x1, #544]
    ldr d13, [x1, #568]
    ldr d7, [x1, #376]
    ldr d11, [x1, #280]
    ldr d10, [x1, #424]
    ldr d29, [x1, #256]
    mov v1.d[1], v24.d[0]
    ldr d31, [x1, #328]
    mov v13.d[1], v8.d[0]
    ldr d20, [x1, #616]
    mov v7.d[1], v27.d[0]
    ldr d8, [x1, #304]
    ldr d16, [x1, #592]
    mov v9.d[1], v10.d[0]
    mov v11.d[1], v29.d[0]
    sshr v24.8H, v7.8H, #15
    ldr d3, [x1, #472]
    ldr d19, [x1, #520]
    sshr v29.8H, v13.8H, #15
    ldr d10, [x1, #496]
    ldr d6, [x1, #448]
    mov v31.d[1], v8.d[0]
    mov v16.d[1], v20.d[0]
    sshr v21.8H, v9.8H, #15
    sshr v22.8H, v11.8H, #15
    and v24.16B, v24.16B, v0.16B
    and v14.16B, v21.16B, v0.16B
    sshr v8.8H, v31.8H, #15
    and v27.16B, v22.16B, v0.16B
    mov v3.d[1], v6.d[0]
    mov v19.d[1], v10.d[0]
    and v8.16B, v8.16B, v0.16B
    add v20.8H, v11.8H, v27.8H
    add v10.8H, v7.8H, v24.8H
    sshr v22.8H, v16.8H, #15
    add v11.8H, v9.8H, v14.8H
    add v28.8H, v31.8H, v8.8H
    sshr v24.8H, v19.8H, #15
    and v22.16B, v22.16B, v0.16B
    sshr v8.8H, v3.8H, #15
    and v24.16B, v24.16B, v0.16B
    and v29.16B, v29.16B, v0.16B
    add v27.8H, v16.8H, v22.8H
    and v8.16B, v8.16B, v0.16B
    add v22.8H, v13.8H, v29.8H
    add v24.8H, v19.8H, v24.8H
    trn2 v19.8H, v11.8H, v10.8H
    add v8.8H, v3.8H, v8.8H
    trn1 v10.8H, v11.8H, v10.8H
    trn1 v9.8H, v20.8H, v28.8H
    trn2 v3.8H, v20.8H, v28.8H
    trn1 v16.8H, v27.8H, v22.8H
    trn2 v30.8H, v8.8H, v24.8H
    trn2 v27.8H, v27.8H, v22.8H
    trn1 v23.4S, v10.4S, v9.4S
    trn1 v7.8H, v8.8H, v24.8H
    trn1 v22.4S, v19.4S, v3.4S
    trn1 v24.4S, v27.4S, v30.4S
    trn2 v10.4S, v10.4S, v9.4S
    trn2 v21.4S, v16.4S, v7.4S
    trn2 v11.4S, v19.4S, v3.4S
    trn1 v6.2D, v22.2D, v24.2D
    trn2 v14.4S, v27.4S, v30.4S
    trn1 v27.2D, v10.2D, v21.2D
    trn2 v13.2D, v22.2D, v24.2D
    ushr v20.8H, v6.8H, #4
    ushr v3.8H, v27.8H, #8
    trn2 v8.2D, v10.2D, v21.2D
    ushr v22.8H, v13.8H, #4
    trn1 v31.4S, v16.4S, v7.4S
    ushr v19.8H, v8.8H, #8
    trn1 v24.2D, v11.2D, v14.2D
    shl v29.8H, v6.8H, #12
    ldr d12, [x1, #64]
    shl v7.8H, v24.8H, #4
    trn1 v16.2D, v23.2D, v31.2D
    shl v18.8H, v27.8H, #8
    trn2 v14.2D, v11.2D, v14.2D
    shl v24.8H, v8.8H, #8
    eor v29.16B, v16.16B, v29.16B
    shl v27.8H, v13.8H, #12
    trn2 v13.2D, v23.2D, v31.2D
    eor v22.16B, v22.16B, v24.16B
    shl v8.8H, v14.8H, #4
    eor v14.16B, v13.16B, v27.16B
    eor v24.16B, v20.16B, v18.16B
    ldr d20, [x1, #16]
    eor v27.16B, v19.16B, v8.16B
    ldr d8, [x1, #40]
    eor v26.16B, v3.16B, v7.16B
    trn2 v10.8H, v29.8H, v24.8H
    trn1 v16.8H, v29.8H, v24.8H
    trn1 v7.8H, v22.8H, v27.8H
    trn2 v29.8H, v22.8H, v27.8H
    ldr d24, [x1, #736]
    ldr d19, [x1, #760]
    mov v20.d[1], v8.d[0]
    trn1 v13.8H, v26.8H, v14.8H
    trn2 v8.8H, v26.8H, v14.8H
    ldr d14, [x1, #664]
    trn1 v3.4S, v7.4S, v10.4S
    trn1 v11.4S, v16.4S, v13.4S
    mov v19.d[1], v24.d[0]
    ldr d24, [x1, #640]
    trn2 v27.4S, v8.4S, v29.4S
    ldr d31, [x1, #208]
    trn1 v22.4S, v8.4S, v29.4S
    trn2 v8.4S, v16.4S, v13.4S
    trn2 v6.4S, v7.4S, v10.4S
    ldr d16, [x1, #184]
    ldr d13, [x1, #88]
    mov v14.d[1], v24.d[0]
    ldr d29, [x1, #160]
    trn1 v10.2D, v6.2D, v27.2D
    trn1 v9.2D, v22.2D, v8.2D
    sshr v17.8H, v1.8H, #15
    trn2 v4.2D, v11.2D, v3.2D
    trn2 v5.2D, v22.2D, v8.2D
    ldr d22, [x1, #232]
    trn1 v8.2D, v11.2D, v3.2D
    sshr v24.8H, v20.8H, #15
    mov v16.d[1], v29.d[0]
    trn2 v6.2D, v6.2D, v27.2D
    st1 {v8.8H, v9.8H, v10.8H}, [x0], #48
    ldr d3, [x1, #136]
    mov v13.d[1], v12.d[0]
    sshr v10.8H, v19.8H, #15
    ldr d8, [x1, #112]
    mov v31.d[1], v22.d[0]
    sshr v22.8H, v13.8H, #15
    and v27.16B, v24.16B, v0.16B
    sshr v24.8H, v16.8H, #15
    and v22.16B, v22.16B, v0.16B
    sshr v12.8H, v31.8H, #15
    sshr v18.8H, v14.8H, #15
    mov v3.d[1], v8.d[0]
    add v7.8H, v20.8H, v27.8H
    add v27.8H, v13.8H, v22.8H
    and v22.16B, v18.16B, v0.16B
    and v10.16B, v10.16B, v0.16B
    sshr v8.8H, v3.8H, #15
    and v29.16B, v17.16B, v0.16B
    add v19.8H, v19.8H, v10.8H
    add v20.8H, v14.8H, v22.8H
    add v1.8H, v1.8H, v29.8H
    and v17.16B, v24.16B, v0.16B
    trn1 v22.8H, v7.8H, v19.8H
    and v10.16B, v12.16B, v0.16B
    trn1 v24.8H, v20.8H, v1.8H
    add v12.8H, v16.8H, v17.8H
    and v8.16B, v8.16B, v0.16B
    add v14.8H, v31.8H, v10.8H
    trn2 v19.8H, v7.8H, v19.8H
    trn2 v10.4S, v22.4S, v24.4S
    add v8.8H, v3.8H, v8.8H
    trn2 v31.8H, v14.8H, v12.8H
    st1 {v4.8H, v5.8H, v6.8H}, [x0], #48
    trn1 v29.8H, v14.8H, v12.8H
    trn2 v17.8H, v27.8H, v8.8H
    trn2 v1.8H, v20.8H, v1.8H
    trn1 v3.4S, v22.4S, v24.4S
    trn1 v12.8H, v27.8H, v8.8H
    trn1 v15.4S, v31.4S, v17.4S
    trn1 v22.4S, v19.4S, v1.4S
    trn2 v20.4S, v31.4S, v17.4S
    trn2 v8.4S, v29.4S, v12.4S
    trn1 v27.4S, v29.4S, v12.4S
    trn1 v29.2D, v22.2D, v15.2D
    trn1 v12.2D, v10.2D, v8.2D
    trn2 v16.4S, v19.4S, v1.4S
    trn2 v24.2D, v22.2D, v15.2D
    shl v22.8H, v29.8H, #12
    ushr v14.8H, v29.8H, #4
    trn2 v7.2D, v10.2D, v8.2D
    shl v15.8H, v12.8H, #8
    trn1 v13.2D, v3.2D, v27.2D
    ushr v19.8H, v24.8H, #4
    trn2 v3.2D, v3.2D, v27.2D
    eor v17.16B, v14.16B, v15.16B
    ushr v10.8H, v12.8H, #8
    eor v9.16B, v13.16B, v22.16B
    shl v27.8H, v7.8H, #8
    shl v8.8H, v24.8H, #12
    trn1 v29.2D, v16.2D, v20.2D
    ushr v12.8H, v7.8H, #8
    trn2 v20.2D, v16.2D, v20.2D
    trn2 v18.8H, v9.8H, v17.8H
    shl v29.8H, v29.8H, #4
    eor v8.16B, v3.16B, v8.16B
    shl v11.8H, v20.8H, #4
    trn1 v15.8H, v9.8H, v17.8H
    eor v29.16B, v10.16B, v29.16B
    eor v14.16B, v12.16B, v11.16B
    eor v13.16B, v19.16B, v27.16B
    trn1 v24.8H, v29.8H, v8.8H
    trn2 v27.8H, v29.8H, v8.8H
    trn2 v2.8H, v13.8H, v14.8H
    trn1 v29.8H, v13.8H, v14.8H
    trn2 v5.4S, v15.4S, v24.4S
    trn1 v14.4S, v15.4S, v24.4S
    trn2 v15.4S, v27.4S, v2.4S
    trn1 v17.4S, v27.4S, v2.4S
    trn2 v22.4S, v29.4S, v18.4S
    trn1 v1.4S, v29.4S, v18.4S
    trn1 v9.2D, v17.2D, v5.2D
    trn1 v10.2D, v22.2D, v15.2D
    trn1 v8.2D, v14.2D, v1.2D
    trn2 v25.2D, v17.2D, v5.2D
    trn2 v24.2D, v14.2D, v1.2D
    st1 {v8.8H, v9.8H, v10.8H}, [x0], #48
    trn2 v26.2D, v22.2D, v15.2D
    st1 {v24.8H, v25.8H, v26.8H}, [x0], #48
    // canonical blocks 96..127
    ldr d9, [x1, #1136]
    ldr d1, [x1, #1352]
    ldr d27, [x1, #1088]
    ldr d24, [x1, #1328]
    ldr d8, [x1, #992]
    ldr d13, [x1, #1016]
    ldr d7, [x1, #1112]
    ldr d11, [x1, #1232]
    ldr d10, [x1, #1160]
    ldr d29, [x1, #1256]
    mov v1.d[1], v24.d[0]
    ldr d31, [x1, #1208]
    mov v13.d[1], v8.d[0]
    ldr d20, [x1, #1064]
    mov v7.d[1], v27.d[0]
    ldr d8, [x1, #1184]
    ldr d16, [x1, #1040]
    mov v9.d[1], v10.d[0]
    mov v11.d[1], v29.d[0]
    sshr v24.8H, v7.8H, #15
    ldr d3, [x1, #920]
    ldr d19, [x1, #968]
    sshr v29.8H, v13.8H, #15
    ldr d10, [x1, #944]
    ldr d6, [x1, #896]
    mov v31.d[1], v8.d[0]
    mov v16.d[1], v20.d[0]
    sshr v21.8H, v9.8H, #15
    sshr v22.8H, v11.8H, #15
    and v24.16B, v24.16B, v0.16B
    and v14.16B, v21.16B, v0.16B
    sshr v8.8H, v31.8H, #15
    and v27.16B, v22.16B, v0.16B
    mov v3.d[1], v6.d[0]
    mov v19.d[1], v10.d[0]
    and v8.16B, v8.16B, v0.16B
    add v20.8H, v11.8H, v27.8H
    add v10.8H, v7.8H, v24.8H
    sshr v22.8H, v16.8H, #15
    add v11.8H, v9.8H, v14.8H
    add v28.8H, v31.8H, v8.8H
    sshr v24.8H, v19.8H, #15
    and v22.16B, v22.16B, v0.16B
    sshr v8.8H, v3.8H, #15
    and v24.16B, v24.16B, v0.16B
    and v29.16B, v29.16B, v0.16B
    add v27.8H, v16.8H, v22.8H
    and v8.16B, v8.16B, v0.16B
    add v22.8H, v13.8H, v29.8H
    add v24.8H, v19.8H, v24.8H
    trn2 v19.8H, v11.8H, v10.8H
    add v8.8H, v3.8H, v8.8H
    trn1 v10.8H, v11.8H, v10.8H
    trn1 v9.8H, v20.8H, v28.8H
    trn2 v3.8H, v20.8H, v28.8H
    trn1 v16.8H, v27.8H, v22.8H
    trn2 v30.8H, v8.8H, v24.8H
    trn2 v27.8H, v27.8H, v22.8H
    trn1 v23.4S, v10.4S, v9.4S
    trn1 v7.8H, v8.8H, v24.8H
    trn1 v22.4S, v19.4S, v3.4S
    trn1 v24.4S, v27.4S, v30.4S
    trn2 v10.4S, v10.4S, v9.4S
    trn2 v21.4S, v16.4S, v7.4S
    trn2 v11.4S, v19.4S, v3.4S
    trn1 v6.2D, v22.2D, v24.2D
    trn2 v14.4S, v27.4S, v30.4S
    trn1 v27.2D, v10.2D, v21.2D
    trn2 v13.2D, v22.2D, v24.2D
    ushr v20.8H, v6.8H, #4
    ushr v3.8H, v27.8H, #8
    trn2 v8.2D, v10.2D, v21.2D
    ushr v22.8H, v13.8H, #4
    trn1 v31.4S, v16.4S, v7.4S
    ushr v19.8H, v8.8H, #8
    trn1 v24.2D, v11.2D, v14.2D
    shl v29.8H, v6.8H, #12
    ldr d12, [x1, #1472]
    shl v7.8H, v24.8H, #4
    trn1 v16.2D, v23.2D, v31.2D
    shl v18.8H, v27.8H, #8
    trn2 v14.2D, v11.2D, v14.2D
    shl v24.8H, v8.8H, #8
    eor v29.16B, v16.16B, v29.16B
    shl v27.8H, v13.8H, #12
    trn2 v13.2D, v23.2D, v31.2D
    eor v22.16B, v22.16B, v24.16B
    shl v8.8H, v14.8H, #4
    eor v14.16B, v13.16B, v27.16B
    eor v24.16B, v20.16B, v18.16B
    ldr d20, [x1, #1424]
    eor v27.16B, v19.16B, v8.16B
    ldr d8, [x1, #1448]
    eor v26.16B, v3.16B, v7.16B
    trn2 v10.8H, v29.8H, v24.8H
    trn1 v16.8H, v29.8H, v24.8H
    trn1 v7.8H, v22.8H, v27.8H
    trn2 v29.8H, v22.8H, v27.8H
    ldr d24, [x1, #1376]
    ldr d19, [x1, #1400]
    mov v20.d[1], v8.d[0]
    trn1 v13.8H, v26.8H, v14.8H
    trn2 v8.8H, v26.8H, v14.8H
    ldr d14, [x1, #1304]
    trn1 v3.4S, v7.4S, v10.4S
    trn1 v11.4S, v16.4S, v13.4S
    mov v19.d[1], v24.d[0]
    ldr d24, [x1, #1280]
    trn2 v27.4S, v8.4S, v29.4S
    ldr d31, [x1, #848]
    trn1 v22.4S, v8.4S, v29.4S
    trn2 v8.4S, v16.4S, v13.4S
    trn2 v6.4S, v7.4S, v10.4S
    ldr d16, [x1, #824]
    ldr d13, [x1, #1496]
    mov v14.d[1], v24.d[0]
    ldr d29, [x1, #800]
    trn1 v10.2D, v6.2D, v27.2D
    trn1 v9.2D, v22.2D, v8.2D
    sshr v17.8H, v1.8H, #15
    trn2 v4.2D, v11.2D, v3.2D
    trn2 v5.2D, v22.2D, v8.2D
    ldr d22, [x1, #872]
    trn1 v8.2D, v11.2D, v3.2D
    sshr v24.8H, v20.8H, #15
    mov v16.d[1], v29.d[0]
    trn2 v6.2D, v6.2D, v27.2D
    st1 {v8.8H, v9.8H, v10.8H}, [x0], #48
    ldr d3, [x1, #776]
    mov v13.d[1], v12.d[0]
    sshr v10.8H, v19.8H, #15
    ldr d8, [x1, #1520]
    mov v31.d[1], v22.d[0]
    sshr v22.8H, v13.8H, #15
    and v27.16B, v24.16B, v0.16B
    sshr v24.8H, v16.8H, #15
    and v22.16B, v22.16B, v0.16B
    sshr v12.8H, v31.8H, #15
    sshr v18.8H, v14.8H, #15
    mov v3.d[1], v8.d[0]
    add v7.8H, v20.8H, v27.8H
    add v27.8H, v13.8H, v22.8H
    and v22.16B, v18.16B, v0.16B
    and v10.16B, v10.16B, v0.16B
    sshr v8.8H, v3.8H, #15
    and v29.16B, v17.16B, v0.16B
    add v19.8H, v19.8H, v10.8H
    add v20.8H, v14.8H, v22.8H
    add v1.8H, v1.8H, v29.8H
    and v17.16B, v24.16B, v0.16B
    trn1 v22.8H, v7.8H, v19.8H
    and v10.16B, v12.16B, v0.16B
    trn1 v24.8H, v20.8H, v1.8H
    add v12.8H, v16.8H, v17.8H
    and v8.16B, v8.16B, v0.16B
    add v14.8H, v31.8H, v10.8H
    trn2 v19.8H, v7.8H, v19.8H
    trn2 v10.4S, v22.4S, v24.4S
    add v8.8H, v3.8H, v8.8H
    trn2 v31.8H, v14.8H, v12.8H
    st1 {v4.8H, v5.8H, v6.8H}, [x0], #48
    trn1 v29.8H, v14.8H, v12.8H
    trn2 v17.8H, v27.8H, v8.8H
    trn2 v1.8H, v20.8H, v1.8H
    trn1 v3.4S, v22.4S, v24.4S
    trn1 v12.8H, v27.8H, v8.8H
    trn1 v15.4S, v31.4S, v17.4S
    trn1 v22.4S, v19.4S, v1.4S
    trn2 v20.4S, v31.4S, v17.4S
    trn2 v8.4S, v29.4S, v12.4S
    trn1 v27.4S, v29.4S, v12.4S
    trn1 v29.2D, v22.2D, v15.2D
    trn1 v12.2D, v10.2D, v8.2D
    trn2 v16.4S, v19.4S, v1.4S
    trn2 v24.2D, v22.2D, v15.2D
    shl v22.8H, v29.8H, #12
    ushr v14.8H, v29.8H, #4
    trn2 v7.2D, v10.2D, v8.2D
    shl v15.8H, v12.8H, #8
    trn1 v13.2D, v3.2D, v27.2D
    ushr v19.8H, v24.8H, #4
    trn2 v3.2D, v3.2D, v27.2D
    eor v17.16B, v14.16B, v15.16B
    ushr v10.8H, v12.8H, #8
    eor v9.16B, v13.16B, v22.16B
    shl v27.8H, v7.8H, #8
    shl v8.8H, v24.8H, #12
    trn1 v29.2D, v16.2D, v20.2D
    ushr v12.8H, v7.8H, #8
    trn2 v20.2D, v16.2D, v20.2D
    trn2 v18.8H, v9.8H, v17.8H
    shl v29.8H, v29.8H, #4
    eor v8.16B, v3.16B, v8.16B
    shl v11.8H, v20.8H, #4
    trn1 v15.8H, v9.8H, v17.8H
    eor v29.16B, v10.16B, v29.16B
    eor v14.16B, v12.16B, v11.16B
    eor v13.16B, v19.16B, v27.16B
    trn1 v24.8H, v29.8H, v8.8H
    trn2 v27.8H, v29.8H, v8.8H
    trn2 v2.8H, v13.8H, v14.8H
    trn1 v29.8H, v13.8H, v14.8H
    trn2 v5.4S, v15.4S, v24.4S
    trn1 v14.4S, v15.4S, v24.4S
    trn2 v15.4S, v27.4S, v2.4S
    trn1 v17.4S, v27.4S, v2.4S
    trn2 v22.4S, v29.4S, v18.4S
    trn1 v1.4S, v29.4S, v18.4S
    trn1 v9.2D, v17.2D, v5.2D
    trn1 v10.2D, v22.2D, v15.2D
    trn1 v8.2D, v14.2D, v1.2D
    trn2 v25.2D, v17.2D, v5.2D
    trn2 v24.2D, v14.2D, v1.2D
    st1 {v8.8H, v9.8H, v10.8H}, [x0], #48
    trn2 v26.2D, v22.2D, v15.2D
    st1 {v24.8H, v25.8H, v26.8H}, [x0], #48
    // canonical blocks 128..159
    ldr d9, [x1, #1336]
    ldr d1, [x1, #832]
    ldr d27, [x1, #1360]
    ldr d24, [x1, #856]
    ldr d8, [x1, #1048]
    ldr d13, [x1, #1024]
    ldr d7, [x1, #1384]
    ldr d11, [x1, #1288]
    ldr d10, [x1, #1312]
    ldr d29, [x1, #1264]
    mov v1.d[1], v24.d[0]
    ldr d31, [x1, #1216]
    mov v13.d[1], v8.d[0]
    ldr d20, [x1, #1072]
    mov v7.d[1], v27.d[0]
    ldr d8, [x1, #1240]
    ldr d16, [x1, #1096]
    mov v9.d[1], v10.d[0]
    mov v11.d[1], v29.d[0]
    sshr v24.8H, v7.8H, #15
    ldr d3, [x1, #1192]
    ldr d19, [x1, #1120]
    sshr v29.8H, v13.8H, #15
    ldr d10, [x1, #1144]
    ldr d6, [x1, #1168]
    mov v31.d[1], v8.d[0]
    mov v16.d[1], v20.d[0]
    sshr v21.8H, v9.8H, #15
    sshr v22.8H, v11.8H, #15
    and v24.16B, v24.16B, v0.16B
    and v14.16B, v21.16B, v0.16B
    sshr v8.8H, v31.8H, #15
    and v27.16B, v22.16B, v0.16B
    mov v3.d[1], v6.d[0]
    mov v19.d[1], v10.d[0]
    and v8.16B, v8.16B, v0.16B
    add v20.8H, v11.8H, v27.8H
    add v10.8H, v7.8H, v24.8H
    sshr v22.8H, v16.8H, #15
    add v11.8H, v9.8H, v14.8H
    add v28.8H, v31.8H, v8.8H
    sshr v24.8H, v19.8H, #15
    and v22.16B, v22.16B, v0.16B
    sshr v8.8H, v3.8H, #15
    and v24.16B, v24.16B, v0.16B
    and v29.16B, v29.16B, v0.16B
    add v27.8H, v16.8H, v22.8H
    and v8.16B, v8.16B, v0.16B
    add v22.8H, v13.8H, v29.8H
    add v24.8H, v19.8H, v24.8H
    trn2 v19.8H, v11.8H, v10.8H
    add v8.8H, v3.8H, v8.8H
    trn1 v10.8H, v11.8H, v10.8H
    trn1 v9.8H, v20.8H, v28.8H
    trn2 v3.8H, v20.8H, v28.8H
    trn1 v16.8H, v27.8H, v22.8H
    trn2 v30.8H, v8.8H, v24.8H
    trn2 v27.8H, v27.8H, v22.8H
    trn1 v23.4S, v10.4S, v9.4S
    trn1 v7.8H, v8.8H, v24.8H
    trn1 v22.4S, v19.4S, v3.4S
    trn1 v24.4S, v27.4S, v30.4S
    trn2 v10.4S, v10.4S, v9.4S
    trn2 v21.4S, v16.4S, v7.4S
    trn2 v11.4S, v19.4S, v3.4S
    trn1 v6.2D, v22.2D, v24.2D
    trn2 v14.4S, v27.4S, v30.4S
    trn1 v27.2D, v10.2D, v21.2D
    trn2 v13.2D, v22.2D, v24.2D
    ushr v20.8H, v6.8H, #4
    ushr v3.8H, v27.8H, #8
    trn2 v8.2D, v10.2D, v21.2D
    ushr v22.8H, v13.8H, #4
    trn1 v31.4S, v16.4S, v7.4S
    ushr v19.8H, v8.8H, #8
    trn1 v24.2D, v11.2D, v14.2D
    shl v29.8H, v6.8H, #12
    ldr d12, [x1, #784]
    shl v7.8H, v24.8H, #4
    trn1 v16.2D, v23.2D, v31.2D
    shl v18.8H, v27.8H, #8
    trn2 v14.2D, v11.2D, v14.2D
    shl v24.8H, v8.8H, #8
    eor v29.16B, v16.16B, v29.16B
    shl v27.8H, v13.8H, #12
    trn2 v13.2D, v23.2D, v31.2D
    eor v22.16B, v22.16B, v24.16B
    shl v8.8H, v14.8H, #4
    eor v14.16B, v13.16B, v27.16B
    eor v24.16B, v20.16B, v18.16B
    ldr d20, [x1, #952]
    eor v27.16B, v19.16B, v8.16B
    ldr d8, [x1, #928]
    eor v26.16B, v3.16B, v7.16B
    trn2 v10.8H, v29.8H, v24.8H
    trn1 v16.8H, v29.8H, v24.8H
    trn1 v7.8H, v22.8H, v27.8H
    trn2 v29.8H, v22.8H, v27.8H
    ldr d24, [x1, #976]
    ldr d19, [x1, #1000]
    mov v20.d[1], v8.d[0]
    trn1 v13.8H, v26.8H, v14.8H
    trn2 v8.8H, v26.8H, v14.8H
    ldr d14, [x1, #904]
    trn1 v3.4S, v7.4S, v10.4S
    trn1 v11.4S, v16.4S, v13.4S
    mov v19.d[1], v24.d[0]
    ldr d24, [x1, #880]
    trn2 v27.4S, v8.4S, v29.4S
    ldr d31, [x1, #1480]
    trn1 v22.4S, v8.4S, v29.4S
    trn2 v8.4S, v16.4S, v13.4S
    trn2 v6.4S, v7.4S, v10.4S
    ldr d16, [x1, #1408]
    ldr d13, [x1, #808]
    mov v14.d[1], v24.d[0]
    ldr d29, [x1, #1432]
    trn1 v10.2D, v6.2D, v27.2D
    trn1 v9.2D, v22.2D, v8.2D
    sshr v17.8H, v1.8H, #15
    trn2 v4.2D, v11.2D, v3.2D
    trn2 v5.2D, v22.2D, v8.2D
    ldr d22, [x1, #1456]
    trn1 v8.2D, v11.2D, v3.2D
    sshr v24.8H, v20.8H, #15
    mov v16.d[1], v29.d[0]
    trn2 v6.2D, v6.2D, v27.2D
    st1 {v8.8H, v9.8H, v10.8H}, [x0], #48
    ldr d3, [x1, #1504]
    mov v13.d[1], v12.d[0]
    sshr v10.8H, v19.8H, #15
    ldr d8, [x1, #1528]
    mov v31.d[1], v22.d[0]
    sshr v22.8H, v13.8H, #15
    and v27.16B, v24.16B, v0.16B
    sshr v24.8H, v16.8H, #15
    and v22.16B, v22.16B, v0.16B
    sshr v12.8H, v31.8H, #15
    sshr v18.8H, v14.8H, #15
    mov v3.d[1], v8.d[0]
    add v7.8H, v20.8H, v27.8H
    add v27.8H, v13.8H, v22.8H
    and v22.16B, v18.16B, v0.16B
    and v10.16B, v10.16B, v0.16B
    sshr v8.8H, v3.8H, #15
    and v29.16B, v17.16B, v0.16B
    add v19.8H, v19.8H, v10.8H
    add v20.8H, v14.8H, v22.8H
    add v1.8H, v1.8H, v29.8H
    and v17.16B, v24.16B, v0.16B
    trn1 v22.8H, v7.8H, v19.8H
    and v10.16B, v12.16B, v0.16B
    trn1 v24.8H, v20.8H, v1.8H
    add v12.8H, v16.8H, v17.8H
    and v8.16B, v8.16B, v0.16B
    add v14.8H, v31.8H, v10.8H
    trn2 v19.8H, v7.8H, v19.8H
    trn2 v10.4S, v22.4S, v24.4S
    add v8.8H, v3.8H, v8.8H
    trn2 v31.8H, v14.8H, v12.8H
    st1 {v4.8H, v5.8H, v6.8H}, [x0], #48
    trn1 v29.8H, v14.8H, v12.8H
    trn2 v17.8H, v27.8H, v8.8H
    trn2 v1.8H, v20.8H, v1.8H
    trn1 v3.4S, v22.4S, v24.4S
    trn1 v12.8H, v27.8H, v8.8H
    trn1 v15.4S, v31.4S, v17.4S
    trn1 v22.4S, v19.4S, v1.4S
    trn2 v20.4S, v31.4S, v17.4S
    trn2 v8.4S, v29.4S, v12.4S
    trn1 v27.4S, v29.4S, v12.4S
    trn1 v29.2D, v22.2D, v15.2D
    trn1 v12.2D, v10.2D, v8.2D
    trn2 v16.4S, v19.4S, v1.4S
    trn2 v24.2D, v22.2D, v15.2D
    shl v22.8H, v29.8H, #12
    ushr v14.8H, v29.8H, #4
    trn2 v7.2D, v10.2D, v8.2D
    shl v15.8H, v12.8H, #8
    trn1 v13.2D, v3.2D, v27.2D
    ushr v19.8H, v24.8H, #4
    trn2 v3.2D, v3.2D, v27.2D
    eor v17.16B, v14.16B, v15.16B
    ushr v10.8H, v12.8H, #8
    eor v9.16B, v13.16B, v22.16B
    shl v27.8H, v7.8H, #8
    shl v8.8H, v24.8H, #12
    trn1 v29.2D, v16.2D, v20.2D
    ushr v12.8H, v7.8H, #8
    trn2 v20.2D, v16.2D, v20.2D
    trn2 v18.8H, v9.8H, v17.8H
    shl v29.8H, v29.8H, #4
    eor v8.16B, v3.16B, v8.16B
    shl v11.8H, v20.8H, #4
    trn1 v15.8H, v9.8H, v17.8H
    eor v29.16B, v10.16B, v29.16B
    eor v14.16B, v12.16B, v11.16B
    eor v13.16B, v19.16B, v27.16B
    trn1 v24.8H, v29.8H, v8.8H
    trn2 v27.8H, v29.8H, v8.8H
    trn2 v2.8H, v13.8H, v14.8H
    trn1 v29.8H, v13.8H, v14.8H
    trn2 v5.4S, v15.4S, v24.4S
    trn1 v14.4S, v15.4S, v24.4S
    trn2 v15.4S, v27.4S, v2.4S
    trn1 v17.4S, v27.4S, v2.4S
    trn2 v22.4S, v29.4S, v18.4S
    trn1 v1.4S, v29.4S, v18.4S
    trn1 v9.2D, v17.2D, v5.2D
    trn1 v10.2D, v22.2D, v15.2D
    trn1 v8.2D, v14.2D, v1.2D
    trn2 v25.2D, v17.2D, v5.2D
    trn2 v24.2D, v14.2D, v1.2D
    st1 {v8.8H, v9.8H, v10.8H}, [x0], #48
    trn2 v26.2D, v22.2D, v15.2D
    st1 {v24.8H, v25.8H, v26.8H}, [x0], #48
    // canonical blocks 160..191
    ldr d9, [x1, #1152]
    ldr d1, [x1, #1104]
    ldr d27, [x1, #1224]
    ldr d24, [x1, #1128]
    ldr d8, [x1, #1416]
    ldr d13, [x1, #1392]
    ldr d7, [x1, #1200]
    ldr d11, [x1, #1248]
    ldr d10, [x1, #1176]
    ldr d29, [x1, #1272]
    mov v1.d[1], v24.d[0]
    ldr d31, [x1, #1296]
    mov v13.d[1], v8.d[0]
    ldr d20, [x1, #1368]
    mov v7.d[1], v27.d[0]
    ldr d8, [x1, #1320]
    ldr d16, [x1, #1344]
    mov v9.d[1], v10.d[0]
    mov v11.d[1], v29.d[0]
    sshr v24.8H, v7.8H, #15
    ldr d3, [x1, #1440]
    ldr d19, [x1, #1488]
    sshr v29.8H, v13.8H, #15
    ldr d10, [x1, #1512]
    ldr d6, [x1, #1464]
    mov v31.d[1], v8.d[0]
    mov v16.d[1], v20.d[0]
    sshr v21.8H, v9.8H, #15
    sshr v22.8H, v11.8H, #15
    and v24.16B, v24.16B, v0.16B
    and v14.16B, v21.16B, v0.16B
    sshr v8.8H, v31.8H, #15
    and v27.16B, v22.16B, v0.16B
    mov v3.d[1], v6.d[0]
    mov v19.d[1], v10.d[0]
    and v8.16B, v8.16B, v0.16B
    add v20.8H, v11.8H, v27.8H
    add v10.8H, v7.8H, v24.8H
    sshr v22.8H, v16.8H, #15
    add v11.8H, v9.8H, v14.8H
    add v28.8H, v31.8H, v8.8H
    sshr v24.8H, v19.8H, #15
    and v22.16B, v22.16B, v0.16B
    sshr v8.8H, v3.8H, #15
    and v24.16B, v24.16B, v0.16B
    and v29.16B, v29.16B, v0.16B
    add v27.8H, v16.8H, v22.8H
    and v8.16B, v8.16B, v0.16B
    add v22.8H, v13.8H, v29.8H
    add v24.8H, v19.8H, v24.8H
    trn2 v19.8H, v11.8H, v10.8H
    add v8.8H, v3.8H, v8.8H
    trn1 v10.8H, v11.8H, v10.8H
    trn1 v9.8H, v20.8H, v28.8H
    trn2 v3.8H, v20.8H, v28.8H
    trn1 v16.8H, v27.8H, v22.8H
    trn2 v30.8H, v8.8H, v24.8H
    trn2 v27.8H, v27.8H, v22.8H
    trn1 v23.4S, v10.4S, v9.4S
    trn1 v7.8H, v8.8H, v24.8H
    trn1 v22.4S, v19.4S, v3.4S
    trn1 v24.4S, v27.4S, v30.4S
    trn2 v10.4S, v10.4S, v9.4S
    trn2 v21.4S, v16.4S, v7.4S
    trn2 v11.4S, v19.4S, v3.4S
    trn1 v6.2D, v22.2D, v24.2D
    trn2 v14.4S, v27.4S, v30.4S
    trn1 v27.2D, v10.2D, v21.2D
    trn2 v13.2D, v22.2D, v24.2D
    ushr v20.8H, v6.8H, #4
    ushr v3.8H, v27.8H, #8
    trn2 v8.2D, v10.2D, v21.2D
    ushr v22.8H, v13.8H, #4
    trn1 v31.4S, v16.4S, v7.4S
    ushr v19.8H, v8.8H, #8
    trn1 v24.2D, v11.2D, v14.2D
    shl v29.8H, v6.8H, #12
    ldr d12, [x1, #840]
    shl v7.8H, v24.8H, #4
    trn1 v16.2D, v23.2D, v31.2D
    shl v18.8H, v27.8H, #8
    trn2 v14.2D, v11.2D, v14.2D
    shl v24.8H, v8.8H, #8
    eor v29.16B, v16.16B, v29.16B
    shl v27.8H, v13.8H, #12
    trn2 v13.2D, v23.2D, v31.2D
    eor v22.16B, v22.16B, v24.16B
    shl v8.8H, v14.8H, #4
    eor v14.16B, v13.16B, v27.16B
    eor v24.16B, v20.16B, v18.16B
    ldr d20, [x1, #960]
    eor v27.16B, v19.16B, v8.16B
    ldr d8, [x1, #984]
    eor v26.16B, v3.16B, v7.16B
    trn2 v10.8H, v29.8H, v24.8H
    trn1 v16.8H, v29.8H, v24.8H
    trn1 v7.8H, v22.8H, v27.8H
    trn2 v29.8H, v22.8H, v27.8H
    ldr d24, [x1, #1032]
    ldr d19, [x1, #1008]
    mov v20.d[1], v8.d[0]
    trn1 v13.8H, v26.8H, v14.8H
    trn2 v8.8H, v26.8H, v14.8H
    ldr d14, [x1, #1056]
    trn1 v3.4S, v7.4S, v10.4S
    trn1 v11.4S, v16.4S, v13.4S
    mov v19.d[1], v24.d[0]
    ldr d24, [x1, #1080]
    trn2 v27.4S, v8.4S, v29.4S
    ldr d31, [x1, #864]
    trn1 v22.4S, v8.4S, v29.4S
    trn2 v8.4S, v16.4S, v13.4S
    trn2 v6.4S, v7.4S, v10.4S
    ldr d16, [x1, #912]
    ldr d13, [x1, #816]
    mov v14.d[1], v24.d[0]
    ldr d29, [x1, #936]
    trn1 v10.2D, v6.2D, v27.2D
    trn1 v9.2D, v22.2D, v8.2D
    sshr v17.8H, v1.8H, #15
    trn2 v4.2D, v11.2D, v3.2D
    trn2 v5.2D, v22.2D, v8.2D
    ldr d22, [x1, #888]
    trn1 v8.2D, v11.2D, v3.2D
    sshr v24.8H, v20.8H, #15
    mov v16.d[1], v29.d[0]
    trn2 v6.2D, v6.2D, v27.2D
    st1 {v8.8H, v9.8H, v10.8H}, [x0], #48
    ldr d3, [x1, #792]
    mov v13.d[1], v12.d[0]
    sshr v10.8H, v19.8H, #15
    ldr d8, [x1, #768]
    mov v31.d[1], v22.d[0]
    sshr v22.8H, v13.8H, #15
    and v27.16B, v24.16B, v0.16B
    sshr v24.8H, v16.8H, #15
    and v22.16B, v22.16B, v0.16B
    sshr v12.8H, v31.8H, #15
    sshr v18.8H, v14.8H, #15
    mov v3.d[1], v8.d[0]
    add v7.8H, v20.8H, v27.8H
    add v27.8H, v13.8H, v22.8H
    and v22.16B, v18.16B, v0.16B
    and v10.16B, v10.16B, v0.16B
    sshr v8.8H, v3.8H, #15
    and v29.16B, v17.16B, v0.16B
    add v19.8H, v19.8H, v10.8H
    add v20.8H, v14.8H, v22.8H
    add v1.8H, v1.8H, v29.8H
    and v17.16B, v24.16B, v0.16B
    trn1 v22.8H, v7.8H, v19.8H
    and v10.16B, v12.16B, v0.16B
    trn1 v24.8H, v20.8H, v1.8H
    add v12.8H, v16.8H, v17.8H
    and v8.16B, v8.16B, v0.16B
    add v14.8H, v31.8H, v10.8H
    trn2 v19.8H, v7.8H, v19.8H
    trn2 v10.4S, v22.4S, v24.4S
    add v8.8H, v3.8H, v8.8H
    trn2 v31.8H, v14.8H, v12.8H
    st1 {v4.8H, v5.8H, v6.8H}, [x0], #48
    trn1 v29.8H, v14.8H, v12.8H
    trn2 v17.8H, v27.8H, v8.8H
    trn2 v1.8H, v20.8H, v1.8H
    trn1 v3.4S, v22.4S, v24.4S
    trn1 v12.8H, v27.8H, v8.8H
    trn1 v15.4S, v31.4S, v17.4S
    trn1 v22.4S, v19.4S, v1.4S
    trn2 v20.4S, v31.4S, v17.4S
    trn2 v8.4S, v29.4S, v12.4S
    trn1 v27.4S, v29.4S, v12.4S
    trn1 v29.2D, v22.2D, v15.2D
    trn1 v12.2D, v10.2D, v8.2D
    trn2 v16.4S, v19.4S, v1.4S
    trn2 v24.2D, v22.2D, v15.2D
    shl v22.8H, v29.8H, #12
    ushr v14.8H, v29.8H, #4
    trn2 v7.2D, v10.2D, v8.2D
    shl v15.8H, v12.8H, #8
    trn1 v13.2D, v3.2D, v27.2D
    ushr v19.8H, v24.8H, #4
    trn2 v3.2D, v3.2D, v27.2D
    eor v17.16B, v14.16B, v15.16B
    ushr v10.8H, v12.8H, #8
    eor v9.16B, v13.16B, v22.16B
    shl v27.8H, v7.8H, #8
    shl v8.8H, v24.8H, #12
    trn1 v29.2D, v16.2D, v20.2D
    ushr v12.8H, v7.8H, #8
    trn2 v20.2D, v16.2D, v20.2D
    trn2 v18.8H, v9.8H, v17.8H
    shl v29.8H, v29.8H, #4
    eor v8.16B, v3.16B, v8.16B
    shl v11.8H, v20.8H, #4
    trn1 v15.8H, v9.8H, v17.8H
    eor v29.16B, v10.16B, v29.16B
    eor v14.16B, v12.16B, v11.16B
    eor v13.16B, v19.16B, v27.16B
    trn1 v24.8H, v29.8H, v8.8H
    trn2 v27.8H, v29.8H, v8.8H
    trn2 v2.8H, v13.8H, v14.8H
    trn1 v29.8H, v13.8H, v14.8H
    trn2 v5.4S, v15.4S, v24.4S
    trn1 v14.4S, v15.4S, v24.4S
    trn2 v15.4S, v27.4S, v2.4S
    trn1 v17.4S, v27.4S, v2.4S
    trn2 v22.4S, v29.4S, v18.4S
    trn1 v1.4S, v29.4S, v18.4S
    trn1 v9.2D, v17.2D, v5.2D
    trn1 v10.2D, v22.2D, v15.2D
    trn1 v8.2D, v14.2D, v1.2D
    trn2 v25.2D, v17.2D, v5.2D
    trn2 v24.2D, v14.2D, v1.2D
    st1 {v8.8H, v9.8H, v10.8H}, [x0], #48
    trn2 v26.2D, v22.2D, v15.2D
    st1 {v24.8H, v25.8H, v26.8H}, [x0], #48
    ldp d8, d9, [sp, #0]
    ldp d10, d11, [sp, #16]
    ldp d12, d13, [sp, #32]
    ldp d14, d15, [sp, #48]
    add sp, sp, #64
    ret

.p2align 4
.Lcanonical_pack_cross_chunk_q:
    .hword 3457, 3457, 3457, 3457
    .hword 3457, 3457, 3457, 3457
