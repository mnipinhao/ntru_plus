// Generated selected P1 full canonical pack; GT production keygen path.
.text

.p2align 4
.global poly_tobytes_gt_canonical_p1
.global _poly_tobytes_gt_canonical_p1
poly_tobytes_gt_canonical_p1:
_poly_tobytes_gt_canonical_p1:
    sub sp, sp, #64
    stp d8, d9, [sp, #0]
    stp d10, d11, [sp, #16]
    stp d12, d13, [sp, #32]
    stp d14, d15, [sp, #48]
    adr x2, .Lcanonical_pack_candidate_q
    ldr q0, [x2]
    // canonical blocks 0..15
    ldr d12, [x1, #0]
    ldr d6, [x1, #24]
    ldr d1, [x1, #72]
    ldr d22, [x1, #48]
    ldr d20, [x1, #144]
    ldr d29, [x1, #168]
    ldr d5, [x1, #96]
    ldr d4, [x1, #120]
    mov v12.d[1], v6.d[0]
    ldr d15, [x1, #264]
    mov v1.d[1], v22.d[0]
    ldr d13, [x1, #240]
    mov v29.d[1], v20.d[0]
    sshr v11.8H, v12.8H, #15
    mov v5.d[1], v4.d[0]
    sshr v20.8H, v1.8H, #15
    ldr d3, [x1, #336]
    ldr d22, [x1, #360]
    and v4.16B, v20.16B, v0.16B
    and v28.16B, v11.16B, v0.16B
    sshr v11.8H, v5.8H, #15
    ldr d10, [x1, #216]
    add v20.8H, v1.8H, v4.8H
    add v19.8H, v12.8H, v28.8H
    ldr d24, [x1, #288]
    ldr d17, [x1, #312]
    and v30.16B, v11.16B, v0.16B
    trn1 v25.8H, v20.8H, v19.8H
    mov v15.d[1], v13.d[0]
    mov v22.d[1], v3.d[0]
    ldr d9, [x1, #192]
    sshr v4.8H, v29.8H, #15
    add v18.8H, v5.8H, v30.8H
    sshr v11.8H, v15.8H, #15
    sshr v26.8H, v22.8H, #15
    mov v17.d[1], v24.d[0]
    trn2 v16.8H, v20.8H, v19.8H
    and v3.16B, v4.16B, v0.16B
    mov v9.d[1], v10.d[0]
    and v14.16B, v11.16B, v0.16B
    add v5.8H, v29.8H, v3.8H
    sshr v2.8H, v17.8H, #15
    add v29.8H, v15.8H, v14.8H
    sshr v10.8H, v9.8H, #15
    and v6.16B, v26.16B, v0.16B
    and v21.16B, v2.16B, v0.16B
    trn2 v3.8H, v5.8H, v18.8H
    and v11.16B, v10.16B, v0.16B
    add v22.8H, v22.8H, v6.8H
    add v30.8H, v17.8H, v21.8H
    add v20.8H, v9.8H, v11.8H
    trn1 v31.4S, v16.4S, v3.4S
    trn2 v10.4S, v16.4S, v3.4S
    trn2 v4.8H, v30.8H, v22.8H
    trn1 v9.8H, v29.8H, v20.8H
    trn2 v24.8H, v29.8H, v20.8H
    trn1 v11.8H, v30.8H, v22.8H
    trn1 v23.8H, v5.8H, v18.8H
    trn1 v28.4S, v4.4S, v24.4S
    trn2 v22.4S, v4.4S, v24.4S
    trn2 v7.4S, v25.4S, v23.4S
    trn1 v16.4S, v25.4S, v23.4S
    trn2 v17.4S, v11.4S, v9.4S
    trn2 v3.2D, v22.2D, v10.2D
    trn2 v6.2D, v28.2D, v31.2D
    trn1 v2.4S, v11.4S, v9.4S
    shl v11.8H, v3.8H, #4
    trn2 v3.2D, v17.2D, v7.2D
    ushr v30.8H, v6.8H, #4
    trn1 v20.2D, v28.2D, v31.2D
    shl v4.8H, v3.8H, #8
    trn1 v29.2D, v17.2D, v7.2D
    ushr v1.8H, v3.8H, #8
    trn1 v5.2D, v22.2D, v10.2D
    eor v8.16B, v30.16B, v4.16B
    ushr v21.8H, v20.8H, #4
    eor v3.16B, v1.16B, v11.16B
    shl v22.8H, v5.8H, #4
    shl v19.8H, v20.8H, #12
    trn1 v24.2D, v2.2D, v16.2D
    shl v15.8H, v6.8H, #12
    trn2 v7.2D, v2.2D, v16.2D
    trn1 v20.8H, v8.8H, v3.8H
    ushr v10.8H, v29.8H, #8
    shl v4.8H, v29.8H, #8
    eor v18.16B, v24.16B, v19.16B
    eor v6.16B, v10.16B, v22.16B
    eor v10.16B, v7.16B, v15.16B
    trn2 v11.8H, v8.8H, v3.8H
    eor v24.16B, v21.16B, v4.16B
    trn1 v19.8H, v6.8H, v10.8H
    trn2 v27.8H, v6.8H, v10.8H
    trn1 v26.8H, v18.8H, v24.8H
    trn2 v31.8H, v18.8H, v24.8H
    trn1 v7.4S, v27.4S, v11.4S
    trn2 v4.4S, v27.4S, v11.4S
    trn1 v8.4S, v26.4S, v19.4S
    trn1 v22.4S, v20.4S, v31.4S
    trn2 v3.4S, v20.4S, v31.4S
    trn2 v30.4S, v26.4S, v19.4S
    trn1 v11.2D, v8.2D, v22.2D
    trn2 v20.2D, v8.2D, v22.2D
    trn1 v12.2D, v7.2D, v30.2D
    trn1 v13.2D, v3.2D, v4.2D
    trn2 v21.2D, v7.2D, v30.2D
    st1 {v11.8H, v12.8H, v13.8H}, [x0], #48
    trn2 v22.2D, v3.2D, v4.2D
    st1 {v20.8H, v21.8H, v22.8H}, [x0], #48
    // canonical blocks 16..31
    ldr d12, [x1, #384]
    ldr d6, [x1, #408]
    ldr d1, [x1, #456]
    ldr d22, [x1, #432]
    ldr d20, [x1, #528]
    ldr d29, [x1, #552]
    ldr d5, [x1, #480]
    ldr d4, [x1, #504]
    mov v12.d[1], v6.d[0]
    ldr d15, [x1, #648]
    mov v1.d[1], v22.d[0]
    ldr d13, [x1, #624]
    mov v29.d[1], v20.d[0]
    sshr v11.8H, v12.8H, #15
    mov v5.d[1], v4.d[0]
    sshr v20.8H, v1.8H, #15
    ldr d3, [x1, #720]
    ldr d22, [x1, #744]
    and v4.16B, v20.16B, v0.16B
    and v28.16B, v11.16B, v0.16B
    sshr v11.8H, v5.8H, #15
    ldr d10, [x1, #600]
    add v20.8H, v1.8H, v4.8H
    add v19.8H, v12.8H, v28.8H
    ldr d24, [x1, #672]
    ldr d17, [x1, #696]
    and v30.16B, v11.16B, v0.16B
    trn1 v25.8H, v20.8H, v19.8H
    mov v15.d[1], v13.d[0]
    mov v22.d[1], v3.d[0]
    ldr d9, [x1, #576]
    sshr v4.8H, v29.8H, #15
    add v18.8H, v5.8H, v30.8H
    sshr v11.8H, v15.8H, #15
    sshr v26.8H, v22.8H, #15
    mov v17.d[1], v24.d[0]
    trn2 v16.8H, v20.8H, v19.8H
    and v3.16B, v4.16B, v0.16B
    mov v9.d[1], v10.d[0]
    and v14.16B, v11.16B, v0.16B
    add v5.8H, v29.8H, v3.8H
    sshr v2.8H, v17.8H, #15
    add v29.8H, v15.8H, v14.8H
    sshr v10.8H, v9.8H, #15
    and v6.16B, v26.16B, v0.16B
    and v21.16B, v2.16B, v0.16B
    trn2 v3.8H, v5.8H, v18.8H
    and v11.16B, v10.16B, v0.16B
    add v22.8H, v22.8H, v6.8H
    add v30.8H, v17.8H, v21.8H
    add v20.8H, v9.8H, v11.8H
    trn1 v31.4S, v16.4S, v3.4S
    trn2 v10.4S, v16.4S, v3.4S
    trn2 v4.8H, v30.8H, v22.8H
    trn1 v9.8H, v29.8H, v20.8H
    trn2 v24.8H, v29.8H, v20.8H
    trn1 v11.8H, v30.8H, v22.8H
    trn1 v23.8H, v5.8H, v18.8H
    trn1 v28.4S, v4.4S, v24.4S
    trn2 v22.4S, v4.4S, v24.4S
    trn2 v7.4S, v25.4S, v23.4S
    trn1 v16.4S, v25.4S, v23.4S
    trn2 v17.4S, v11.4S, v9.4S
    trn2 v3.2D, v22.2D, v10.2D
    trn2 v6.2D, v28.2D, v31.2D
    trn1 v2.4S, v11.4S, v9.4S
    shl v11.8H, v3.8H, #4
    trn2 v3.2D, v17.2D, v7.2D
    ushr v30.8H, v6.8H, #4
    trn1 v20.2D, v28.2D, v31.2D
    shl v4.8H, v3.8H, #8
    trn1 v29.2D, v17.2D, v7.2D
    ushr v1.8H, v3.8H, #8
    trn1 v5.2D, v22.2D, v10.2D
    eor v8.16B, v30.16B, v4.16B
    ushr v21.8H, v20.8H, #4
    eor v3.16B, v1.16B, v11.16B
    shl v22.8H, v5.8H, #4
    shl v19.8H, v20.8H, #12
    trn1 v24.2D, v2.2D, v16.2D
    shl v15.8H, v6.8H, #12
    trn2 v7.2D, v2.2D, v16.2D
    trn1 v20.8H, v8.8H, v3.8H
    ushr v10.8H, v29.8H, #8
    shl v4.8H, v29.8H, #8
    eor v18.16B, v24.16B, v19.16B
    eor v6.16B, v10.16B, v22.16B
    eor v10.16B, v7.16B, v15.16B
    trn2 v11.8H, v8.8H, v3.8H
    eor v24.16B, v21.16B, v4.16B
    trn1 v19.8H, v6.8H, v10.8H
    trn2 v27.8H, v6.8H, v10.8H
    trn1 v26.8H, v18.8H, v24.8H
    trn2 v31.8H, v18.8H, v24.8H
    trn1 v7.4S, v27.4S, v11.4S
    trn2 v4.4S, v27.4S, v11.4S
    trn1 v8.4S, v26.4S, v19.4S
    trn1 v22.4S, v20.4S, v31.4S
    trn2 v3.4S, v20.4S, v31.4S
    trn2 v30.4S, v26.4S, v19.4S
    trn1 v11.2D, v8.2D, v22.2D
    trn2 v20.2D, v8.2D, v22.2D
    trn1 v12.2D, v7.2D, v30.2D
    trn1 v13.2D, v3.2D, v4.2D
    trn2 v21.2D, v7.2D, v30.2D
    st1 {v11.8H, v12.8H, v13.8H}, [x0], #48
    trn2 v22.2D, v3.2D, v4.2D
    st1 {v20.8H, v21.8H, v22.8H}, [x0], #48
    // canonical blocks 32..47
    ldr d12, [x1, #368]
    ldr d6, [x1, #392]
    ldr d1, [x1, #320]
    ldr d22, [x1, #344]
    ldr d20, [x1, #440]
    ldr d29, [x1, #416]
    ldr d5, [x1, #464]
    ldr d4, [x1, #488]
    mov v12.d[1], v6.d[0]
    ldr d15, [x1, #224]
    mov v1.d[1], v22.d[0]
    ldr d13, [x1, #248]
    mov v29.d[1], v20.d[0]
    sshr v11.8H, v12.8H, #15
    mov v5.d[1], v4.d[0]
    sshr v20.8H, v1.8H, #15
    ldr d3, [x1, #200]
    ldr d22, [x1, #176]
    and v4.16B, v20.16B, v0.16B
    and v28.16B, v11.16B, v0.16B
    sshr v11.8H, v5.8H, #15
    ldr d10, [x1, #296]
    add v20.8H, v1.8H, v4.8H
    add v19.8H, v12.8H, v28.8H
    ldr d24, [x1, #152]
    ldr d17, [x1, #128]
    and v30.16B, v11.16B, v0.16B
    trn1 v25.8H, v20.8H, v19.8H
    mov v15.d[1], v13.d[0]
    mov v22.d[1], v3.d[0]
    ldr d9, [x1, #272]
    sshr v4.8H, v29.8H, #15
    add v18.8H, v5.8H, v30.8H
    sshr v11.8H, v15.8H, #15
    sshr v26.8H, v22.8H, #15
    mov v17.d[1], v24.d[0]
    trn2 v16.8H, v20.8H, v19.8H
    and v3.16B, v4.16B, v0.16B
    mov v9.d[1], v10.d[0]
    and v14.16B, v11.16B, v0.16B
    add v5.8H, v29.8H, v3.8H
    sshr v2.8H, v17.8H, #15
    add v29.8H, v15.8H, v14.8H
    sshr v10.8H, v9.8H, #15
    and v6.16B, v26.16B, v0.16B
    and v21.16B, v2.16B, v0.16B
    trn2 v3.8H, v5.8H, v18.8H
    and v11.16B, v10.16B, v0.16B
    add v22.8H, v22.8H, v6.8H
    add v30.8H, v17.8H, v21.8H
    add v20.8H, v9.8H, v11.8H
    trn1 v31.4S, v16.4S, v3.4S
    trn2 v10.4S, v16.4S, v3.4S
    trn2 v4.8H, v30.8H, v22.8H
    trn1 v9.8H, v29.8H, v20.8H
    trn2 v24.8H, v29.8H, v20.8H
    trn1 v11.8H, v30.8H, v22.8H
    trn1 v23.8H, v5.8H, v18.8H
    trn1 v28.4S, v4.4S, v24.4S
    trn2 v22.4S, v4.4S, v24.4S
    trn2 v7.4S, v25.4S, v23.4S
    trn1 v16.4S, v25.4S, v23.4S
    trn2 v17.4S, v11.4S, v9.4S
    trn2 v3.2D, v22.2D, v10.2D
    trn2 v6.2D, v28.2D, v31.2D
    trn1 v2.4S, v11.4S, v9.4S
    shl v11.8H, v3.8H, #4
    trn2 v3.2D, v17.2D, v7.2D
    ushr v30.8H, v6.8H, #4
    trn1 v20.2D, v28.2D, v31.2D
    shl v4.8H, v3.8H, #8
    trn1 v29.2D, v17.2D, v7.2D
    ushr v1.8H, v3.8H, #8
    trn1 v5.2D, v22.2D, v10.2D
    eor v8.16B, v30.16B, v4.16B
    ushr v21.8H, v20.8H, #4
    eor v3.16B, v1.16B, v11.16B
    shl v22.8H, v5.8H, #4
    shl v19.8H, v20.8H, #12
    trn1 v24.2D, v2.2D, v16.2D
    shl v15.8H, v6.8H, #12
    trn2 v7.2D, v2.2D, v16.2D
    trn1 v20.8H, v8.8H, v3.8H
    ushr v10.8H, v29.8H, #8
    shl v4.8H, v29.8H, #8
    eor v18.16B, v24.16B, v19.16B
    eor v6.16B, v10.16B, v22.16B
    eor v10.16B, v7.16B, v15.16B
    trn2 v11.8H, v8.8H, v3.8H
    eor v24.16B, v21.16B, v4.16B
    trn1 v19.8H, v6.8H, v10.8H
    trn2 v27.8H, v6.8H, v10.8H
    trn1 v26.8H, v18.8H, v24.8H
    trn2 v31.8H, v18.8H, v24.8H
    trn1 v7.4S, v27.4S, v11.4S
    trn2 v4.4S, v27.4S, v11.4S
    trn1 v8.4S, v26.4S, v19.4S
    trn1 v22.4S, v20.4S, v31.4S
    trn2 v3.4S, v20.4S, v31.4S
    trn2 v30.4S, v26.4S, v19.4S
    trn1 v11.2D, v8.2D, v22.2D
    trn2 v20.2D, v8.2D, v22.2D
    trn1 v12.2D, v7.2D, v30.2D
    trn1 v13.2D, v3.2D, v4.2D
    trn2 v21.2D, v7.2D, v30.2D
    st1 {v11.8H, v12.8H, v13.8H}, [x0], #48
    trn2 v22.2D, v3.2D, v4.2D
    st1 {v20.8H, v21.8H, v22.8H}, [x0], #48
    // canonical blocks 48..63
    ldr d12, [x1, #656]
    ldr d6, [x1, #680]
    ldr d1, [x1, #608]
    ldr d22, [x1, #632]
    ldr d20, [x1, #584]
    ldr d29, [x1, #560]
    ldr d5, [x1, #536]
    ldr d4, [x1, #512]
    mov v12.d[1], v6.d[0]
    ldr d15, [x1, #32]
    mov v1.d[1], v22.d[0]
    ldr d13, [x1, #56]
    mov v29.d[1], v20.d[0]
    sshr v11.8H, v12.8H, #15
    mov v5.d[1], v4.d[0]
    sshr v20.8H, v1.8H, #15
    ldr d3, [x1, #8]
    ldr d22, [x1, #752]
    and v4.16B, v20.16B, v0.16B
    and v28.16B, v11.16B, v0.16B
    sshr v11.8H, v5.8H, #15
    ldr d10, [x1, #104]
    add v20.8H, v1.8H, v4.8H
    add v19.8H, v12.8H, v28.8H
    ldr d24, [x1, #728]
    ldr d17, [x1, #704]
    and v30.16B, v11.16B, v0.16B
    trn1 v25.8H, v20.8H, v19.8H
    mov v15.d[1], v13.d[0]
    mov v22.d[1], v3.d[0]
    ldr d9, [x1, #80]
    sshr v4.8H, v29.8H, #15
    add v18.8H, v5.8H, v30.8H
    sshr v11.8H, v15.8H, #15
    sshr v26.8H, v22.8H, #15
    mov v17.d[1], v24.d[0]
    trn2 v16.8H, v20.8H, v19.8H
    and v3.16B, v4.16B, v0.16B
    mov v9.d[1], v10.d[0]
    and v14.16B, v11.16B, v0.16B
    add v5.8H, v29.8H, v3.8H
    sshr v2.8H, v17.8H, #15
    add v29.8H, v15.8H, v14.8H
    sshr v10.8H, v9.8H, #15
    and v6.16B, v26.16B, v0.16B
    and v21.16B, v2.16B, v0.16B
    trn2 v3.8H, v5.8H, v18.8H
    and v11.16B, v10.16B, v0.16B
    add v22.8H, v22.8H, v6.8H
    add v30.8H, v17.8H, v21.8H
    add v20.8H, v9.8H, v11.8H
    trn1 v31.4S, v16.4S, v3.4S
    trn2 v10.4S, v16.4S, v3.4S
    trn2 v4.8H, v30.8H, v22.8H
    trn1 v9.8H, v29.8H, v20.8H
    trn2 v24.8H, v29.8H, v20.8H
    trn1 v11.8H, v30.8H, v22.8H
    trn1 v23.8H, v5.8H, v18.8H
    trn1 v28.4S, v4.4S, v24.4S
    trn2 v22.4S, v4.4S, v24.4S
    trn2 v7.4S, v25.4S, v23.4S
    trn1 v16.4S, v25.4S, v23.4S
    trn2 v17.4S, v11.4S, v9.4S
    trn2 v3.2D, v22.2D, v10.2D
    trn2 v6.2D, v28.2D, v31.2D
    trn1 v2.4S, v11.4S, v9.4S
    shl v11.8H, v3.8H, #4
    trn2 v3.2D, v17.2D, v7.2D
    ushr v30.8H, v6.8H, #4
    trn1 v20.2D, v28.2D, v31.2D
    shl v4.8H, v3.8H, #8
    trn1 v29.2D, v17.2D, v7.2D
    ushr v1.8H, v3.8H, #8
    trn1 v5.2D, v22.2D, v10.2D
    eor v8.16B, v30.16B, v4.16B
    ushr v21.8H, v20.8H, #4
    eor v3.16B, v1.16B, v11.16B
    shl v22.8H, v5.8H, #4
    shl v19.8H, v20.8H, #12
    trn1 v24.2D, v2.2D, v16.2D
    shl v15.8H, v6.8H, #12
    trn2 v7.2D, v2.2D, v16.2D
    trn1 v20.8H, v8.8H, v3.8H
    ushr v10.8H, v29.8H, #8
    shl v4.8H, v29.8H, #8
    eor v18.16B, v24.16B, v19.16B
    eor v6.16B, v10.16B, v22.16B
    eor v10.16B, v7.16B, v15.16B
    trn2 v11.8H, v8.8H, v3.8H
    eor v24.16B, v21.16B, v4.16B
    trn1 v19.8H, v6.8H, v10.8H
    trn2 v27.8H, v6.8H, v10.8H
    trn1 v26.8H, v18.8H, v24.8H
    trn2 v31.8H, v18.8H, v24.8H
    trn1 v7.4S, v27.4S, v11.4S
    trn2 v4.4S, v27.4S, v11.4S
    trn1 v8.4S, v26.4S, v19.4S
    trn1 v22.4S, v20.4S, v31.4S
    trn2 v3.4S, v20.4S, v31.4S
    trn2 v30.4S, v26.4S, v19.4S
    trn1 v11.2D, v8.2D, v22.2D
    trn2 v20.2D, v8.2D, v22.2D
    trn1 v12.2D, v7.2D, v30.2D
    trn1 v13.2D, v3.2D, v4.2D
    trn2 v21.2D, v7.2D, v30.2D
    st1 {v11.8H, v12.8H, v13.8H}, [x0], #48
    trn2 v22.2D, v3.2D, v4.2D
    st1 {v20.8H, v21.8H, v22.8H}, [x0], #48
    // canonical blocks 64..79
    ldr d12, [x1, #568]
    ldr d6, [x1, #544]
    ldr d1, [x1, #592]
    ldr d22, [x1, #616]
    ldr d20, [x1, #448]
    ldr d29, [x1, #472]
    ldr d5, [x1, #520]
    ldr d4, [x1, #496]
    mov v12.d[1], v6.d[0]
    ldr d15, [x1, #280]
    mov v1.d[1], v22.d[0]
    ldr d13, [x1, #256]
    mov v29.d[1], v20.d[0]
    sshr v11.8H, v12.8H, #15
    mov v5.d[1], v4.d[0]
    sshr v20.8H, v1.8H, #15
    ldr d3, [x1, #352]
    ldr d22, [x1, #376]
    and v4.16B, v20.16B, v0.16B
    and v28.16B, v11.16B, v0.16B
    sshr v11.8H, v5.8H, #15
    ldr d10, [x1, #304]
    add v20.8H, v1.8H, v4.8H
    add v19.8H, v12.8H, v28.8H
    ldr d24, [x1, #424]
    ldr d17, [x1, #400]
    and v30.16B, v11.16B, v0.16B
    trn1 v25.8H, v20.8H, v19.8H
    mov v15.d[1], v13.d[0]
    mov v22.d[1], v3.d[0]
    ldr d9, [x1, #328]
    sshr v4.8H, v29.8H, #15
    add v18.8H, v5.8H, v30.8H
    sshr v11.8H, v15.8H, #15
    sshr v26.8H, v22.8H, #15
    mov v17.d[1], v24.d[0]
    trn2 v16.8H, v20.8H, v19.8H
    and v3.16B, v4.16B, v0.16B
    mov v9.d[1], v10.d[0]
    and v14.16B, v11.16B, v0.16B
    add v5.8H, v29.8H, v3.8H
    sshr v2.8H, v17.8H, #15
    add v29.8H, v15.8H, v14.8H
    sshr v10.8H, v9.8H, #15
    and v6.16B, v26.16B, v0.16B
    and v21.16B, v2.16B, v0.16B
    trn2 v3.8H, v5.8H, v18.8H
    and v11.16B, v10.16B, v0.16B
    add v22.8H, v22.8H, v6.8H
    add v30.8H, v17.8H, v21.8H
    add v20.8H, v9.8H, v11.8H
    trn1 v31.4S, v16.4S, v3.4S
    trn2 v10.4S, v16.4S, v3.4S
    trn2 v4.8H, v30.8H, v22.8H
    trn1 v9.8H, v29.8H, v20.8H
    trn2 v24.8H, v29.8H, v20.8H
    trn1 v11.8H, v30.8H, v22.8H
    trn1 v23.8H, v5.8H, v18.8H
    trn1 v28.4S, v4.4S, v24.4S
    trn2 v22.4S, v4.4S, v24.4S
    trn2 v7.4S, v25.4S, v23.4S
    trn1 v16.4S, v25.4S, v23.4S
    trn2 v17.4S, v11.4S, v9.4S
    trn2 v3.2D, v22.2D, v10.2D
    trn2 v6.2D, v28.2D, v31.2D
    trn1 v2.4S, v11.4S, v9.4S
    shl v11.8H, v3.8H, #4
    trn2 v3.2D, v17.2D, v7.2D
    ushr v30.8H, v6.8H, #4
    trn1 v20.2D, v28.2D, v31.2D
    shl v4.8H, v3.8H, #8
    trn1 v29.2D, v17.2D, v7.2D
    ushr v1.8H, v3.8H, #8
    trn1 v5.2D, v22.2D, v10.2D
    eor v8.16B, v30.16B, v4.16B
    ushr v21.8H, v20.8H, #4
    eor v3.16B, v1.16B, v11.16B
    shl v22.8H, v5.8H, #4
    shl v19.8H, v20.8H, #12
    trn1 v24.2D, v2.2D, v16.2D
    shl v15.8H, v6.8H, #12
    trn2 v7.2D, v2.2D, v16.2D
    trn1 v20.8H, v8.8H, v3.8H
    ushr v10.8H, v29.8H, #8
    shl v4.8H, v29.8H, #8
    eor v18.16B, v24.16B, v19.16B
    eor v6.16B, v10.16B, v22.16B
    eor v10.16B, v7.16B, v15.16B
    trn2 v11.8H, v8.8H, v3.8H
    eor v24.16B, v21.16B, v4.16B
    trn1 v19.8H, v6.8H, v10.8H
    trn2 v27.8H, v6.8H, v10.8H
    trn1 v26.8H, v18.8H, v24.8H
    trn2 v31.8H, v18.8H, v24.8H
    trn1 v7.4S, v27.4S, v11.4S
    trn2 v4.4S, v27.4S, v11.4S
    trn1 v8.4S, v26.4S, v19.4S
    trn1 v22.4S, v20.4S, v31.4S
    trn2 v3.4S, v20.4S, v31.4S
    trn2 v30.4S, v26.4S, v19.4S
    trn1 v11.2D, v8.2D, v22.2D
    trn2 v20.2D, v8.2D, v22.2D
    trn1 v12.2D, v7.2D, v30.2D
    trn1 v13.2D, v3.2D, v4.2D
    trn2 v21.2D, v7.2D, v30.2D
    st1 {v11.8H, v12.8H, v13.8H}, [x0], #48
    trn2 v22.2D, v3.2D, v4.2D
    st1 {v20.8H, v21.8H, v22.8H}, [x0], #48
    // canonical blocks 80..95
    ldr d12, [x1, #184]
    ldr d6, [x1, #160]
    ldr d1, [x1, #208]
    ldr d22, [x1, #232]
    ldr d20, [x1, #64]
    ldr d29, [x1, #88]
    ldr d5, [x1, #136]
    ldr d4, [x1, #112]
    mov v12.d[1], v6.d[0]
    ldr d15, [x1, #664]
    mov v1.d[1], v22.d[0]
    ldr d13, [x1, #640]
    mov v29.d[1], v20.d[0]
    sshr v11.8H, v12.8H, #15
    mov v5.d[1], v4.d[0]
    sshr v20.8H, v1.8H, #15
    ldr d3, [x1, #736]
    ldr d22, [x1, #760]
    and v4.16B, v20.16B, v0.16B
    and v28.16B, v11.16B, v0.16B
    sshr v11.8H, v5.8H, #15
    ldr d10, [x1, #688]
    add v20.8H, v1.8H, v4.8H
    add v19.8H, v12.8H, v28.8H
    ldr d24, [x1, #40]
    ldr d17, [x1, #16]
    and v30.16B, v11.16B, v0.16B
    trn1 v25.8H, v20.8H, v19.8H
    mov v15.d[1], v13.d[0]
    mov v22.d[1], v3.d[0]
    ldr d9, [x1, #712]
    sshr v4.8H, v29.8H, #15
    add v18.8H, v5.8H, v30.8H
    sshr v11.8H, v15.8H, #15
    sshr v26.8H, v22.8H, #15
    mov v17.d[1], v24.d[0]
    trn2 v16.8H, v20.8H, v19.8H
    and v3.16B, v4.16B, v0.16B
    mov v9.d[1], v10.d[0]
    and v14.16B, v11.16B, v0.16B
    add v5.8H, v29.8H, v3.8H
    sshr v2.8H, v17.8H, #15
    add v29.8H, v15.8H, v14.8H
    sshr v10.8H, v9.8H, #15
    and v6.16B, v26.16B, v0.16B
    and v21.16B, v2.16B, v0.16B
    trn2 v3.8H, v5.8H, v18.8H
    and v11.16B, v10.16B, v0.16B
    add v22.8H, v22.8H, v6.8H
    add v30.8H, v17.8H, v21.8H
    add v20.8H, v9.8H, v11.8H
    trn1 v31.4S, v16.4S, v3.4S
    trn2 v10.4S, v16.4S, v3.4S
    trn2 v4.8H, v30.8H, v22.8H
    trn1 v9.8H, v29.8H, v20.8H
    trn2 v24.8H, v29.8H, v20.8H
    trn1 v11.8H, v30.8H, v22.8H
    trn1 v23.8H, v5.8H, v18.8H
    trn1 v28.4S, v4.4S, v24.4S
    trn2 v22.4S, v4.4S, v24.4S
    trn2 v7.4S, v25.4S, v23.4S
    trn1 v16.4S, v25.4S, v23.4S
    trn2 v17.4S, v11.4S, v9.4S
    trn2 v3.2D, v22.2D, v10.2D
    trn2 v6.2D, v28.2D, v31.2D
    trn1 v2.4S, v11.4S, v9.4S
    shl v11.8H, v3.8H, #4
    trn2 v3.2D, v17.2D, v7.2D
    ushr v30.8H, v6.8H, #4
    trn1 v20.2D, v28.2D, v31.2D
    shl v4.8H, v3.8H, #8
    trn1 v29.2D, v17.2D, v7.2D
    ushr v1.8H, v3.8H, #8
    trn1 v5.2D, v22.2D, v10.2D
    eor v8.16B, v30.16B, v4.16B
    ushr v21.8H, v20.8H, #4
    eor v3.16B, v1.16B, v11.16B
    shl v22.8H, v5.8H, #4
    shl v19.8H, v20.8H, #12
    trn1 v24.2D, v2.2D, v16.2D
    shl v15.8H, v6.8H, #12
    trn2 v7.2D, v2.2D, v16.2D
    trn1 v20.8H, v8.8H, v3.8H
    ushr v10.8H, v29.8H, #8
    shl v4.8H, v29.8H, #8
    eor v18.16B, v24.16B, v19.16B
    eor v6.16B, v10.16B, v22.16B
    eor v10.16B, v7.16B, v15.16B
    trn2 v11.8H, v8.8H, v3.8H
    eor v24.16B, v21.16B, v4.16B
    trn1 v19.8H, v6.8H, v10.8H
    trn2 v27.8H, v6.8H, v10.8H
    trn1 v26.8H, v18.8H, v24.8H
    trn2 v31.8H, v18.8H, v24.8H
    trn1 v7.4S, v27.4S, v11.4S
    trn2 v4.4S, v27.4S, v11.4S
    trn1 v8.4S, v26.4S, v19.4S
    trn1 v22.4S, v20.4S, v31.4S
    trn2 v3.4S, v20.4S, v31.4S
    trn2 v30.4S, v26.4S, v19.4S
    trn1 v11.2D, v8.2D, v22.2D
    trn2 v20.2D, v8.2D, v22.2D
    trn1 v12.2D, v7.2D, v30.2D
    trn1 v13.2D, v3.2D, v4.2D
    trn2 v21.2D, v7.2D, v30.2D
    st1 {v11.8H, v12.8H, v13.8H}, [x0], #48
    trn2 v22.2D, v3.2D, v4.2D
    st1 {v20.8H, v21.8H, v22.8H}, [x0], #48
    // canonical blocks 96..111
    ldr d12, [x1, #1016]
    ldr d6, [x1, #992]
    ldr d1, [x1, #1040]
    ldr d22, [x1, #1064]
    ldr d20, [x1, #896]
    ldr d29, [x1, #920]
    ldr d5, [x1, #968]
    ldr d4, [x1, #944]
    mov v12.d[1], v6.d[0]
    ldr d15, [x1, #1232]
    mov v1.d[1], v22.d[0]
    ldr d13, [x1, #1256]
    mov v29.d[1], v20.d[0]
    sshr v11.8H, v12.8H, #15
    mov v5.d[1], v4.d[0]
    sshr v20.8H, v1.8H, #15
    ldr d3, [x1, #1088]
    ldr d22, [x1, #1112]
    and v4.16B, v20.16B, v0.16B
    and v28.16B, v11.16B, v0.16B
    sshr v11.8H, v5.8H, #15
    ldr d10, [x1, #1184]
    add v20.8H, v1.8H, v4.8H
    add v19.8H, v12.8H, v28.8H
    ldr d24, [x1, #1160]
    ldr d17, [x1, #1136]
    and v30.16B, v11.16B, v0.16B
    trn1 v25.8H, v20.8H, v19.8H
    mov v15.d[1], v13.d[0]
    mov v22.d[1], v3.d[0]
    ldr d9, [x1, #1208]
    sshr v4.8H, v29.8H, #15
    add v18.8H, v5.8H, v30.8H
    sshr v11.8H, v15.8H, #15
    sshr v26.8H, v22.8H, #15
    mov v17.d[1], v24.d[0]
    trn2 v16.8H, v20.8H, v19.8H
    and v3.16B, v4.16B, v0.16B
    mov v9.d[1], v10.d[0]
    and v14.16B, v11.16B, v0.16B
    add v5.8H, v29.8H, v3.8H
    sshr v2.8H, v17.8H, #15
    add v29.8H, v15.8H, v14.8H
    sshr v10.8H, v9.8H, #15
    and v6.16B, v26.16B, v0.16B
    and v21.16B, v2.16B, v0.16B
    trn2 v3.8H, v5.8H, v18.8H
    and v11.16B, v10.16B, v0.16B
    add v22.8H, v22.8H, v6.8H
    add v30.8H, v17.8H, v21.8H
    add v20.8H, v9.8H, v11.8H
    trn1 v31.4S, v16.4S, v3.4S
    trn2 v10.4S, v16.4S, v3.4S
    trn2 v4.8H, v30.8H, v22.8H
    trn1 v9.8H, v29.8H, v20.8H
    trn2 v24.8H, v29.8H, v20.8H
    trn1 v11.8H, v30.8H, v22.8H
    trn1 v23.8H, v5.8H, v18.8H
    trn1 v28.4S, v4.4S, v24.4S
    trn2 v22.4S, v4.4S, v24.4S
    trn2 v7.4S, v25.4S, v23.4S
    trn1 v16.4S, v25.4S, v23.4S
    trn2 v17.4S, v11.4S, v9.4S
    trn2 v3.2D, v22.2D, v10.2D
    trn2 v6.2D, v28.2D, v31.2D
    trn1 v2.4S, v11.4S, v9.4S
    shl v11.8H, v3.8H, #4
    trn2 v3.2D, v17.2D, v7.2D
    ushr v30.8H, v6.8H, #4
    trn1 v20.2D, v28.2D, v31.2D
    shl v4.8H, v3.8H, #8
    trn1 v29.2D, v17.2D, v7.2D
    ushr v1.8H, v3.8H, #8
    trn1 v5.2D, v22.2D, v10.2D
    eor v8.16B, v30.16B, v4.16B
    ushr v21.8H, v20.8H, #4
    eor v3.16B, v1.16B, v11.16B
    shl v22.8H, v5.8H, #4
    shl v19.8H, v20.8H, #12
    trn1 v24.2D, v2.2D, v16.2D
    shl v15.8H, v6.8H, #12
    trn2 v7.2D, v2.2D, v16.2D
    trn1 v20.8H, v8.8H, v3.8H
    ushr v10.8H, v29.8H, #8
    shl v4.8H, v29.8H, #8
    eor v18.16B, v24.16B, v19.16B
    eor v6.16B, v10.16B, v22.16B
    eor v10.16B, v7.16B, v15.16B
    trn2 v11.8H, v8.8H, v3.8H
    eor v24.16B, v21.16B, v4.16B
    trn1 v19.8H, v6.8H, v10.8H
    trn2 v27.8H, v6.8H, v10.8H
    trn1 v26.8H, v18.8H, v24.8H
    trn2 v31.8H, v18.8H, v24.8H
    trn1 v7.4S, v27.4S, v11.4S
    trn2 v4.4S, v27.4S, v11.4S
    trn1 v8.4S, v26.4S, v19.4S
    trn1 v22.4S, v20.4S, v31.4S
    trn2 v3.4S, v20.4S, v31.4S
    trn2 v30.4S, v26.4S, v19.4S
    trn1 v11.2D, v8.2D, v22.2D
    trn2 v20.2D, v8.2D, v22.2D
    trn1 v12.2D, v7.2D, v30.2D
    trn1 v13.2D, v3.2D, v4.2D
    trn2 v21.2D, v7.2D, v30.2D
    st1 {v11.8H, v12.8H, v13.8H}, [x0], #48
    trn2 v22.2D, v3.2D, v4.2D
    st1 {v20.8H, v21.8H, v22.8H}, [x0], #48
    // canonical blocks 112..127
    ldr d12, [x1, #824]
    ldr d6, [x1, #800]
    ldr d1, [x1, #848]
    ldr d22, [x1, #872]
    ldr d20, [x1, #1472]
    ldr d29, [x1, #1496]
    ldr d5, [x1, #776]
    ldr d4, [x1, #1520]
    mov v12.d[1], v6.d[0]
    ldr d15, [x1, #1304]
    mov v1.d[1], v22.d[0]
    ldr d13, [x1, #1280]
    mov v29.d[1], v20.d[0]
    sshr v11.8H, v12.8H, #15
    mov v5.d[1], v4.d[0]
    sshr v20.8H, v1.8H, #15
    ldr d3, [x1, #1376]
    ldr d22, [x1, #1400]
    and v4.16B, v20.16B, v0.16B
    and v28.16B, v11.16B, v0.16B
    sshr v11.8H, v5.8H, #15
    ldr d10, [x1, #1328]
    add v20.8H, v1.8H, v4.8H
    add v19.8H, v12.8H, v28.8H
    ldr d24, [x1, #1448]
    ldr d17, [x1, #1424]
    and v30.16B, v11.16B, v0.16B
    trn1 v25.8H, v20.8H, v19.8H
    mov v15.d[1], v13.d[0]
    mov v22.d[1], v3.d[0]
    ldr d9, [x1, #1352]
    sshr v4.8H, v29.8H, #15
    add v18.8H, v5.8H, v30.8H
    sshr v11.8H, v15.8H, #15
    sshr v26.8H, v22.8H, #15
    mov v17.d[1], v24.d[0]
    trn2 v16.8H, v20.8H, v19.8H
    and v3.16B, v4.16B, v0.16B
    mov v9.d[1], v10.d[0]
    and v14.16B, v11.16B, v0.16B
    add v5.8H, v29.8H, v3.8H
    sshr v2.8H, v17.8H, #15
    add v29.8H, v15.8H, v14.8H
    sshr v10.8H, v9.8H, #15
    and v6.16B, v26.16B, v0.16B
    and v21.16B, v2.16B, v0.16B
    trn2 v3.8H, v5.8H, v18.8H
    and v11.16B, v10.16B, v0.16B
    add v22.8H, v22.8H, v6.8H
    add v30.8H, v17.8H, v21.8H
    add v20.8H, v9.8H, v11.8H
    trn1 v31.4S, v16.4S, v3.4S
    trn2 v10.4S, v16.4S, v3.4S
    trn2 v4.8H, v30.8H, v22.8H
    trn1 v9.8H, v29.8H, v20.8H
    trn2 v24.8H, v29.8H, v20.8H
    trn1 v11.8H, v30.8H, v22.8H
    trn1 v23.8H, v5.8H, v18.8H
    trn1 v28.4S, v4.4S, v24.4S
    trn2 v22.4S, v4.4S, v24.4S
    trn2 v7.4S, v25.4S, v23.4S
    trn1 v16.4S, v25.4S, v23.4S
    trn2 v17.4S, v11.4S, v9.4S
    trn2 v3.2D, v22.2D, v10.2D
    trn2 v6.2D, v28.2D, v31.2D
    trn1 v2.4S, v11.4S, v9.4S
    shl v11.8H, v3.8H, #4
    trn2 v3.2D, v17.2D, v7.2D
    ushr v30.8H, v6.8H, #4
    trn1 v20.2D, v28.2D, v31.2D
    shl v4.8H, v3.8H, #8
    trn1 v29.2D, v17.2D, v7.2D
    ushr v1.8H, v3.8H, #8
    trn1 v5.2D, v22.2D, v10.2D
    eor v8.16B, v30.16B, v4.16B
    ushr v21.8H, v20.8H, #4
    eor v3.16B, v1.16B, v11.16B
    shl v22.8H, v5.8H, #4
    shl v19.8H, v20.8H, #12
    trn1 v24.2D, v2.2D, v16.2D
    shl v15.8H, v6.8H, #12
    trn2 v7.2D, v2.2D, v16.2D
    trn1 v20.8H, v8.8H, v3.8H
    ushr v10.8H, v29.8H, #8
    shl v4.8H, v29.8H, #8
    eor v18.16B, v24.16B, v19.16B
    eor v6.16B, v10.16B, v22.16B
    eor v10.16B, v7.16B, v15.16B
    trn2 v11.8H, v8.8H, v3.8H
    eor v24.16B, v21.16B, v4.16B
    trn1 v19.8H, v6.8H, v10.8H
    trn2 v27.8H, v6.8H, v10.8H
    trn1 v26.8H, v18.8H, v24.8H
    trn2 v31.8H, v18.8H, v24.8H
    trn1 v7.4S, v27.4S, v11.4S
    trn2 v4.4S, v27.4S, v11.4S
    trn1 v8.4S, v26.4S, v19.4S
    trn1 v22.4S, v20.4S, v31.4S
    trn2 v3.4S, v20.4S, v31.4S
    trn2 v30.4S, v26.4S, v19.4S
    trn1 v11.2D, v8.2D, v22.2D
    trn2 v20.2D, v8.2D, v22.2D
    trn1 v12.2D, v7.2D, v30.2D
    trn1 v13.2D, v3.2D, v4.2D
    trn2 v21.2D, v7.2D, v30.2D
    st1 {v11.8H, v12.8H, v13.8H}, [x0], #48
    trn2 v22.2D, v3.2D, v4.2D
    st1 {v20.8H, v21.8H, v22.8H}, [x0], #48
    // canonical blocks 128..143
    ldr d12, [x1, #1024]
    ldr d6, [x1, #1048]
    ldr d1, [x1, #1096]
    ldr d22, [x1, #1072]
    ldr d20, [x1, #1168]
    ldr d29, [x1, #1192]
    ldr d5, [x1, #1120]
    ldr d4, [x1, #1144]
    mov v12.d[1], v6.d[0]
    ldr d15, [x1, #1288]
    mov v1.d[1], v22.d[0]
    ldr d13, [x1, #1264]
    mov v29.d[1], v20.d[0]
    sshr v11.8H, v12.8H, #15
    mov v5.d[1], v4.d[0]
    sshr v20.8H, v1.8H, #15
    ldr d3, [x1, #1360]
    ldr d22, [x1, #1384]
    and v4.16B, v20.16B, v0.16B
    and v28.16B, v11.16B, v0.16B
    sshr v11.8H, v5.8H, #15
    ldr d10, [x1, #1240]
    add v20.8H, v1.8H, v4.8H
    add v19.8H, v12.8H, v28.8H
    ldr d24, [x1, #1312]
    ldr d17, [x1, #1336]
    and v30.16B, v11.16B, v0.16B
    trn1 v25.8H, v20.8H, v19.8H
    mov v15.d[1], v13.d[0]
    mov v22.d[1], v3.d[0]
    ldr d9, [x1, #1216]
    sshr v4.8H, v29.8H, #15
    add v18.8H, v5.8H, v30.8H
    sshr v11.8H, v15.8H, #15
    sshr v26.8H, v22.8H, #15
    mov v17.d[1], v24.d[0]
    trn2 v16.8H, v20.8H, v19.8H
    and v3.16B, v4.16B, v0.16B
    mov v9.d[1], v10.d[0]
    and v14.16B, v11.16B, v0.16B
    add v5.8H, v29.8H, v3.8H
    sshr v2.8H, v17.8H, #15
    add v29.8H, v15.8H, v14.8H
    sshr v10.8H, v9.8H, #15
    and v6.16B, v26.16B, v0.16B
    and v21.16B, v2.16B, v0.16B
    trn2 v3.8H, v5.8H, v18.8H
    and v11.16B, v10.16B, v0.16B
    add v22.8H, v22.8H, v6.8H
    add v30.8H, v17.8H, v21.8H
    add v20.8H, v9.8H, v11.8H
    trn1 v31.4S, v16.4S, v3.4S
    trn2 v10.4S, v16.4S, v3.4S
    trn2 v4.8H, v30.8H, v22.8H
    trn1 v9.8H, v29.8H, v20.8H
    trn2 v24.8H, v29.8H, v20.8H
    trn1 v11.8H, v30.8H, v22.8H
    trn1 v23.8H, v5.8H, v18.8H
    trn1 v28.4S, v4.4S, v24.4S
    trn2 v22.4S, v4.4S, v24.4S
    trn2 v7.4S, v25.4S, v23.4S
    trn1 v16.4S, v25.4S, v23.4S
    trn2 v17.4S, v11.4S, v9.4S
    trn2 v3.2D, v22.2D, v10.2D
    trn2 v6.2D, v28.2D, v31.2D
    trn1 v2.4S, v11.4S, v9.4S
    shl v11.8H, v3.8H, #4
    trn2 v3.2D, v17.2D, v7.2D
    ushr v30.8H, v6.8H, #4
    trn1 v20.2D, v28.2D, v31.2D
    shl v4.8H, v3.8H, #8
    trn1 v29.2D, v17.2D, v7.2D
    ushr v1.8H, v3.8H, #8
    trn1 v5.2D, v22.2D, v10.2D
    eor v8.16B, v30.16B, v4.16B
    ushr v21.8H, v20.8H, #4
    eor v3.16B, v1.16B, v11.16B
    shl v22.8H, v5.8H, #4
    shl v19.8H, v20.8H, #12
    trn1 v24.2D, v2.2D, v16.2D
    shl v15.8H, v6.8H, #12
    trn2 v7.2D, v2.2D, v16.2D
    trn1 v20.8H, v8.8H, v3.8H
    ushr v10.8H, v29.8H, #8
    shl v4.8H, v29.8H, #8
    eor v18.16B, v24.16B, v19.16B
    eor v6.16B, v10.16B, v22.16B
    eor v10.16B, v7.16B, v15.16B
    trn2 v11.8H, v8.8H, v3.8H
    eor v24.16B, v21.16B, v4.16B
    trn1 v19.8H, v6.8H, v10.8H
    trn2 v27.8H, v6.8H, v10.8H
    trn1 v26.8H, v18.8H, v24.8H
    trn2 v31.8H, v18.8H, v24.8H
    trn1 v7.4S, v27.4S, v11.4S
    trn2 v4.4S, v27.4S, v11.4S
    trn1 v8.4S, v26.4S, v19.4S
    trn1 v22.4S, v20.4S, v31.4S
    trn2 v3.4S, v20.4S, v31.4S
    trn2 v30.4S, v26.4S, v19.4S
    trn1 v11.2D, v8.2D, v22.2D
    trn2 v20.2D, v8.2D, v22.2D
    trn1 v12.2D, v7.2D, v30.2D
    trn1 v13.2D, v3.2D, v4.2D
    trn2 v21.2D, v7.2D, v30.2D
    st1 {v11.8H, v12.8H, v13.8H}, [x0], #48
    trn2 v22.2D, v3.2D, v4.2D
    st1 {v20.8H, v21.8H, v22.8H}, [x0], #48
    // canonical blocks 144..159
    ldr d12, [x1, #1408]
    ldr d6, [x1, #1432]
    ldr d1, [x1, #1480]
    ldr d22, [x1, #1456]
    ldr d20, [x1, #784]
    ldr d29, [x1, #808]
    ldr d5, [x1, #1504]
    ldr d4, [x1, #1528]
    mov v12.d[1], v6.d[0]
    ldr d15, [x1, #904]
    mov v1.d[1], v22.d[0]
    ldr d13, [x1, #880]
    mov v29.d[1], v20.d[0]
    sshr v11.8H, v12.8H, #15
    mov v5.d[1], v4.d[0]
    sshr v20.8H, v1.8H, #15
    ldr d3, [x1, #976]
    ldr d22, [x1, #1000]
    and v4.16B, v20.16B, v0.16B
    and v28.16B, v11.16B, v0.16B
    sshr v11.8H, v5.8H, #15
    ldr d10, [x1, #856]
    add v20.8H, v1.8H, v4.8H
    add v19.8H, v12.8H, v28.8H
    ldr d24, [x1, #928]
    ldr d17, [x1, #952]
    and v30.16B, v11.16B, v0.16B
    trn1 v25.8H, v20.8H, v19.8H
    mov v15.d[1], v13.d[0]
    mov v22.d[1], v3.d[0]
    ldr d9, [x1, #832]
    sshr v4.8H, v29.8H, #15
    add v18.8H, v5.8H, v30.8H
    sshr v11.8H, v15.8H, #15
    sshr v26.8H, v22.8H, #15
    mov v17.d[1], v24.d[0]
    trn2 v16.8H, v20.8H, v19.8H
    and v3.16B, v4.16B, v0.16B
    mov v9.d[1], v10.d[0]
    and v14.16B, v11.16B, v0.16B
    add v5.8H, v29.8H, v3.8H
    sshr v2.8H, v17.8H, #15
    add v29.8H, v15.8H, v14.8H
    sshr v10.8H, v9.8H, #15
    and v6.16B, v26.16B, v0.16B
    and v21.16B, v2.16B, v0.16B
    trn2 v3.8H, v5.8H, v18.8H
    and v11.16B, v10.16B, v0.16B
    add v22.8H, v22.8H, v6.8H
    add v30.8H, v17.8H, v21.8H
    add v20.8H, v9.8H, v11.8H
    trn1 v31.4S, v16.4S, v3.4S
    trn2 v10.4S, v16.4S, v3.4S
    trn2 v4.8H, v30.8H, v22.8H
    trn1 v9.8H, v29.8H, v20.8H
    trn2 v24.8H, v29.8H, v20.8H
    trn1 v11.8H, v30.8H, v22.8H
    trn1 v23.8H, v5.8H, v18.8H
    trn1 v28.4S, v4.4S, v24.4S
    trn2 v22.4S, v4.4S, v24.4S
    trn2 v7.4S, v25.4S, v23.4S
    trn1 v16.4S, v25.4S, v23.4S
    trn2 v17.4S, v11.4S, v9.4S
    trn2 v3.2D, v22.2D, v10.2D
    trn2 v6.2D, v28.2D, v31.2D
    trn1 v2.4S, v11.4S, v9.4S
    shl v11.8H, v3.8H, #4
    trn2 v3.2D, v17.2D, v7.2D
    ushr v30.8H, v6.8H, #4
    trn1 v20.2D, v28.2D, v31.2D
    shl v4.8H, v3.8H, #8
    trn1 v29.2D, v17.2D, v7.2D
    ushr v1.8H, v3.8H, #8
    trn1 v5.2D, v22.2D, v10.2D
    eor v8.16B, v30.16B, v4.16B
    ushr v21.8H, v20.8H, #4
    eor v3.16B, v1.16B, v11.16B
    shl v22.8H, v5.8H, #4
    shl v19.8H, v20.8H, #12
    trn1 v24.2D, v2.2D, v16.2D
    shl v15.8H, v6.8H, #12
    trn2 v7.2D, v2.2D, v16.2D
    trn1 v20.8H, v8.8H, v3.8H
    ushr v10.8H, v29.8H, #8
    shl v4.8H, v29.8H, #8
    eor v18.16B, v24.16B, v19.16B
    eor v6.16B, v10.16B, v22.16B
    eor v10.16B, v7.16B, v15.16B
    trn2 v11.8H, v8.8H, v3.8H
    eor v24.16B, v21.16B, v4.16B
    trn1 v19.8H, v6.8H, v10.8H
    trn2 v27.8H, v6.8H, v10.8H
    trn1 v26.8H, v18.8H, v24.8H
    trn2 v31.8H, v18.8H, v24.8H
    trn1 v7.4S, v27.4S, v11.4S
    trn2 v4.4S, v27.4S, v11.4S
    trn1 v8.4S, v26.4S, v19.4S
    trn1 v22.4S, v20.4S, v31.4S
    trn2 v3.4S, v20.4S, v31.4S
    trn2 v30.4S, v26.4S, v19.4S
    trn1 v11.2D, v8.2D, v22.2D
    trn2 v20.2D, v8.2D, v22.2D
    trn1 v12.2D, v7.2D, v30.2D
    trn1 v13.2D, v3.2D, v4.2D
    trn2 v21.2D, v7.2D, v30.2D
    st1 {v11.8H, v12.8H, v13.8H}, [x0], #48
    trn2 v22.2D, v3.2D, v4.2D
    st1 {v20.8H, v21.8H, v22.8H}, [x0], #48
    // canonical blocks 160..175
    ldr d12, [x1, #1392]
    ldr d6, [x1, #1416]
    ldr d1, [x1, #1344]
    ldr d22, [x1, #1368]
    ldr d20, [x1, #1464]
    ldr d29, [x1, #1440]
    ldr d5, [x1, #1488]
    ldr d4, [x1, #1512]
    mov v12.d[1], v6.d[0]
    ldr d15, [x1, #1248]
    mov v1.d[1], v22.d[0]
    ldr d13, [x1, #1272]
    mov v29.d[1], v20.d[0]
    sshr v11.8H, v12.8H, #15
    mov v5.d[1], v4.d[0]
    sshr v20.8H, v1.8H, #15
    ldr d3, [x1, #1224]
    ldr d22, [x1, #1200]
    and v4.16B, v20.16B, v0.16B
    and v28.16B, v11.16B, v0.16B
    sshr v11.8H, v5.8H, #15
    ldr d10, [x1, #1320]
    add v20.8H, v1.8H, v4.8H
    add v19.8H, v12.8H, v28.8H
    ldr d24, [x1, #1176]
    ldr d17, [x1, #1152]
    and v30.16B, v11.16B, v0.16B
    trn1 v25.8H, v20.8H, v19.8H
    mov v15.d[1], v13.d[0]
    mov v22.d[1], v3.d[0]
    ldr d9, [x1, #1296]
    sshr v4.8H, v29.8H, #15
    add v18.8H, v5.8H, v30.8H
    sshr v11.8H, v15.8H, #15
    sshr v26.8H, v22.8H, #15
    mov v17.d[1], v24.d[0]
    trn2 v16.8H, v20.8H, v19.8H
    and v3.16B, v4.16B, v0.16B
    mov v9.d[1], v10.d[0]
    and v14.16B, v11.16B, v0.16B
    add v5.8H, v29.8H, v3.8H
    sshr v2.8H, v17.8H, #15
    add v29.8H, v15.8H, v14.8H
    sshr v10.8H, v9.8H, #15
    and v6.16B, v26.16B, v0.16B
    and v21.16B, v2.16B, v0.16B
    trn2 v3.8H, v5.8H, v18.8H
    and v11.16B, v10.16B, v0.16B
    add v22.8H, v22.8H, v6.8H
    add v30.8H, v17.8H, v21.8H
    add v20.8H, v9.8H, v11.8H
    trn1 v31.4S, v16.4S, v3.4S
    trn2 v10.4S, v16.4S, v3.4S
    trn2 v4.8H, v30.8H, v22.8H
    trn1 v9.8H, v29.8H, v20.8H
    trn2 v24.8H, v29.8H, v20.8H
    trn1 v11.8H, v30.8H, v22.8H
    trn1 v23.8H, v5.8H, v18.8H
    trn1 v28.4S, v4.4S, v24.4S
    trn2 v22.4S, v4.4S, v24.4S
    trn2 v7.4S, v25.4S, v23.4S
    trn1 v16.4S, v25.4S, v23.4S
    trn2 v17.4S, v11.4S, v9.4S
    trn2 v3.2D, v22.2D, v10.2D
    trn2 v6.2D, v28.2D, v31.2D
    trn1 v2.4S, v11.4S, v9.4S
    shl v11.8H, v3.8H, #4
    trn2 v3.2D, v17.2D, v7.2D
    ushr v30.8H, v6.8H, #4
    trn1 v20.2D, v28.2D, v31.2D
    shl v4.8H, v3.8H, #8
    trn1 v29.2D, v17.2D, v7.2D
    ushr v1.8H, v3.8H, #8
    trn1 v5.2D, v22.2D, v10.2D
    eor v8.16B, v30.16B, v4.16B
    ushr v21.8H, v20.8H, #4
    eor v3.16B, v1.16B, v11.16B
    shl v22.8H, v5.8H, #4
    shl v19.8H, v20.8H, #12
    trn1 v24.2D, v2.2D, v16.2D
    shl v15.8H, v6.8H, #12
    trn2 v7.2D, v2.2D, v16.2D
    trn1 v20.8H, v8.8H, v3.8H
    ushr v10.8H, v29.8H, #8
    shl v4.8H, v29.8H, #8
    eor v18.16B, v24.16B, v19.16B
    eor v6.16B, v10.16B, v22.16B
    eor v10.16B, v7.16B, v15.16B
    trn2 v11.8H, v8.8H, v3.8H
    eor v24.16B, v21.16B, v4.16B
    trn1 v19.8H, v6.8H, v10.8H
    trn2 v27.8H, v6.8H, v10.8H
    trn1 v26.8H, v18.8H, v24.8H
    trn2 v31.8H, v18.8H, v24.8H
    trn1 v7.4S, v27.4S, v11.4S
    trn2 v4.4S, v27.4S, v11.4S
    trn1 v8.4S, v26.4S, v19.4S
    trn1 v22.4S, v20.4S, v31.4S
    trn2 v3.4S, v20.4S, v31.4S
    trn2 v30.4S, v26.4S, v19.4S
    trn1 v11.2D, v8.2D, v22.2D
    trn2 v20.2D, v8.2D, v22.2D
    trn1 v12.2D, v7.2D, v30.2D
    trn1 v13.2D, v3.2D, v4.2D
    trn2 v21.2D, v7.2D, v30.2D
    st1 {v11.8H, v12.8H, v13.8H}, [x0], #48
    trn2 v22.2D, v3.2D, v4.2D
    st1 {v20.8H, v21.8H, v22.8H}, [x0], #48
    // canonical blocks 176..191
    ldr d12, [x1, #912]
    ldr d6, [x1, #936]
    ldr d1, [x1, #864]
    ldr d22, [x1, #888]
    ldr d20, [x1, #840]
    ldr d29, [x1, #816]
    ldr d5, [x1, #792]
    ldr d4, [x1, #768]
    mov v12.d[1], v6.d[0]
    ldr d15, [x1, #1056]
    mov v1.d[1], v22.d[0]
    ldr d13, [x1, #1080]
    mov v29.d[1], v20.d[0]
    sshr v11.8H, v12.8H, #15
    mov v5.d[1], v4.d[0]
    sshr v20.8H, v1.8H, #15
    ldr d3, [x1, #1032]
    ldr d22, [x1, #1008]
    and v4.16B, v20.16B, v0.16B
    and v28.16B, v11.16B, v0.16B
    sshr v11.8H, v5.8H, #15
    ldr d10, [x1, #1128]
    add v20.8H, v1.8H, v4.8H
    add v19.8H, v12.8H, v28.8H
    ldr d24, [x1, #984]
    ldr d17, [x1, #960]
    and v30.16B, v11.16B, v0.16B
    trn1 v25.8H, v20.8H, v19.8H
    mov v15.d[1], v13.d[0]
    mov v22.d[1], v3.d[0]
    ldr d9, [x1, #1104]
    sshr v4.8H, v29.8H, #15
    add v18.8H, v5.8H, v30.8H
    sshr v11.8H, v15.8H, #15
    sshr v26.8H, v22.8H, #15
    mov v17.d[1], v24.d[0]
    trn2 v16.8H, v20.8H, v19.8H
    and v3.16B, v4.16B, v0.16B
    mov v9.d[1], v10.d[0]
    and v14.16B, v11.16B, v0.16B
    add v5.8H, v29.8H, v3.8H
    sshr v2.8H, v17.8H, #15
    add v29.8H, v15.8H, v14.8H
    sshr v10.8H, v9.8H, #15
    and v6.16B, v26.16B, v0.16B
    and v21.16B, v2.16B, v0.16B
    trn2 v3.8H, v5.8H, v18.8H
    and v11.16B, v10.16B, v0.16B
    add v22.8H, v22.8H, v6.8H
    add v30.8H, v17.8H, v21.8H
    add v20.8H, v9.8H, v11.8H
    trn1 v31.4S, v16.4S, v3.4S
    trn2 v10.4S, v16.4S, v3.4S
    trn2 v4.8H, v30.8H, v22.8H
    trn1 v9.8H, v29.8H, v20.8H
    trn2 v24.8H, v29.8H, v20.8H
    trn1 v11.8H, v30.8H, v22.8H
    trn1 v23.8H, v5.8H, v18.8H
    trn1 v28.4S, v4.4S, v24.4S
    trn2 v22.4S, v4.4S, v24.4S
    trn2 v7.4S, v25.4S, v23.4S
    trn1 v16.4S, v25.4S, v23.4S
    trn2 v17.4S, v11.4S, v9.4S
    trn2 v3.2D, v22.2D, v10.2D
    trn2 v6.2D, v28.2D, v31.2D
    trn1 v2.4S, v11.4S, v9.4S
    shl v11.8H, v3.8H, #4
    trn2 v3.2D, v17.2D, v7.2D
    ushr v30.8H, v6.8H, #4
    trn1 v20.2D, v28.2D, v31.2D
    shl v4.8H, v3.8H, #8
    trn1 v29.2D, v17.2D, v7.2D
    ushr v1.8H, v3.8H, #8
    trn1 v5.2D, v22.2D, v10.2D
    eor v8.16B, v30.16B, v4.16B
    ushr v21.8H, v20.8H, #4
    eor v3.16B, v1.16B, v11.16B
    shl v22.8H, v5.8H, #4
    shl v19.8H, v20.8H, #12
    trn1 v24.2D, v2.2D, v16.2D
    shl v15.8H, v6.8H, #12
    trn2 v7.2D, v2.2D, v16.2D
    trn1 v20.8H, v8.8H, v3.8H
    ushr v10.8H, v29.8H, #8
    shl v4.8H, v29.8H, #8
    eor v18.16B, v24.16B, v19.16B
    eor v6.16B, v10.16B, v22.16B
    eor v10.16B, v7.16B, v15.16B
    trn2 v11.8H, v8.8H, v3.8H
    eor v24.16B, v21.16B, v4.16B
    trn1 v19.8H, v6.8H, v10.8H
    trn2 v27.8H, v6.8H, v10.8H
    trn1 v26.8H, v18.8H, v24.8H
    trn2 v31.8H, v18.8H, v24.8H
    trn1 v7.4S, v27.4S, v11.4S
    trn2 v4.4S, v27.4S, v11.4S
    trn1 v8.4S, v26.4S, v19.4S
    trn1 v22.4S, v20.4S, v31.4S
    trn2 v3.4S, v20.4S, v31.4S
    trn2 v30.4S, v26.4S, v19.4S
    trn1 v11.2D, v8.2D, v22.2D
    trn2 v20.2D, v8.2D, v22.2D
    trn1 v12.2D, v7.2D, v30.2D
    trn1 v13.2D, v3.2D, v4.2D
    trn2 v21.2D, v7.2D, v30.2D
    st1 {v11.8H, v12.8H, v13.8H}, [x0], #48
    trn2 v22.2D, v3.2D, v4.2D
    st1 {v20.8H, v21.8H, v22.8H}, [x0], #48
    ldp d8, d9, [sp, #0]
    ldp d10, d11, [sp, #16]
    ldp d12, d13, [sp, #32]
    ldp d14, d15, [sp, #48]
    add sp, sp, #64
    ret

.p2align 4
.Lcanonical_pack_candidate_q:
    .hword 3457, 3457, 3457, 3457
    .hword 3457, 3457, 3457, 3457
