// Source-order prototype for the Phase123 U01 -> NTT32 stage12 handoff.
//
// Scope:
//   row0 only, Phase123 iterations 0/2/4/6, NTT32 stage12 stripes0+1.
//   This is not production assembly and is not Slothy-scheduled yet.

.text

// Live-in: x1=input base, x3=Phase123 twist base, x4=row0 output base,
//          x12=ntt32_twiddle_vecs base, v0=q/reduction constants.
// Live-out: post-stage12 row0 Q0/Q1/Q8/Q9/Q16/Q17/Q24/Q25 stores at x4
//           offsets 0/16/128/144/256/272/384/400.
// Range: same raw row0 U01 range as production Phase123, then same lazy
//        NTT32 stage12 range as production my_32ntt.
// Reserved physical regs: source-order prototype fixes x1/x3/x4/x7/x12/v0-v31.
slothy_start_phase123_u01_stage12_row0_stripe01:
    // U01 iter0, row0 slots0+1 -> hold Q0/Q1 in v24/v25.
    add x7, x3, #0
    ldr q10, [x1, #768]
    ldr q12, [x1, #1024]
    ldr q14, [x1, #1280]
    mul v16.8h, v10.8h, v0.h[4]
    mul v18.8h, v12.8h, v0.h[4]
    mul v20.8h, v14.8h, v0.h[4]
    sqrdmulh v1.8h, v10.8h, v0.h[5]
    sqrdmulh v3.8h, v12.8h, v0.h[5]
    sqrdmulh v7.8h, v14.8h, v0.h[5]
    mls v16.8h, v1.8h, v0.h[0]
    mls v18.8h, v3.8h, v0.h[0]
    mls v20.8h, v7.8h, v0.h[0]
    sub v10.8h, v10.8h, v16.8h
    sub v12.8h, v12.8h, v18.8h
    sub v14.8h, v14.8h, v20.8h
    ldr q4, [x1, #0]
    ldr q6, [x1, #256]
    ldr q8, [x1, #512]
    add v10.8h, v10.8h, v4.8h
    add v12.8h, v12.8h, v6.8h
    add v14.8h, v14.8h, v8.8h
    add v4.8h, v4.8h, v16.8h
    add v6.8h, v6.8h, v18.8h
    add v8.8h, v8.8h, v20.8h
    ldp q1, q2, [x7, #0]
    sqrdmulh v3.8h, v10.8h, v2.8h
    mul v10.8h, v10.8h, v1.8h
    mls v10.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #64]
    sqrdmulh v3.8h, v12.8h, v2.8h
    mul v12.8h, v12.8h, v1.8h
    mls v12.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #128]
    sqrdmulh v3.8h, v14.8h, v2.8h
    mul v14.8h, v14.8h, v1.8h
    mls v14.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #192]
    sqrdmulh v3.8h, v4.8h, v2.8h
    mul v4.8h, v4.8h, v1.8h
    mls v4.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #256]
    sqrdmulh v3.8h, v6.8h, v2.8h
    mul v6.8h, v6.8h, v1.8h
    mls v6.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #320]
    sqrdmulh v3.8h, v8.8h, v2.8h
    mul v8.8h, v8.8h, v1.8h
    mls v8.8h, v3.8h, v0.h[0]
    zip1 v22.2d, v4.2d, v10.2d
    zip2 v23.2d, v4.2d, v10.2d
    zip1 v26.2d, v6.2d, v12.2d
    zip2 v27.2d, v6.2d, v12.2d
    zip1 v30.2d, v8.2d, v14.2d
    zip2 v31.2d, v8.2d, v14.2d
    add v24.8h, v22.8h, v26.8h
    add v24.8h, v24.8h, v30.8h
    add v25.8h, v23.8h, v27.8h
    add v25.8h, v25.8h, v31.8h

    // U01 iter2, row0 slots0+1 -> hold Q8/Q9 in v28/v29.
    add x7, x3, #768
    ldr q10, [x1, #832]
    ldr q12, [x1, #1088]
    ldr q14, [x1, #1344]
    mul v16.8h, v10.8h, v0.h[4]
    mul v18.8h, v12.8h, v0.h[4]
    mul v20.8h, v14.8h, v0.h[4]
    sqrdmulh v1.8h, v10.8h, v0.h[5]
    sqrdmulh v3.8h, v12.8h, v0.h[5]
    sqrdmulh v7.8h, v14.8h, v0.h[5]
    mls v16.8h, v1.8h, v0.h[0]
    mls v18.8h, v3.8h, v0.h[0]
    mls v20.8h, v7.8h, v0.h[0]
    sub v10.8h, v10.8h, v16.8h
    sub v12.8h, v12.8h, v18.8h
    sub v14.8h, v14.8h, v20.8h
    ldr q4, [x1, #64]
    ldr q6, [x1, #320]
    ldr q8, [x1, #576]
    add v10.8h, v10.8h, v4.8h
    add v12.8h, v12.8h, v6.8h
    add v14.8h, v14.8h, v8.8h
    add v4.8h, v4.8h, v16.8h
    add v6.8h, v6.8h, v18.8h
    add v8.8h, v8.8h, v20.8h
    ldp q1, q2, [x7, #0]
    sqrdmulh v3.8h, v10.8h, v2.8h
    mul v10.8h, v10.8h, v1.8h
    mls v10.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #64]
    sqrdmulh v3.8h, v12.8h, v2.8h
    mul v12.8h, v12.8h, v1.8h
    mls v12.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #128]
    sqrdmulh v3.8h, v14.8h, v2.8h
    mul v14.8h, v14.8h, v1.8h
    mls v14.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #192]
    sqrdmulh v3.8h, v4.8h, v2.8h
    mul v4.8h, v4.8h, v1.8h
    mls v4.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #256]
    sqrdmulh v3.8h, v6.8h, v2.8h
    mul v6.8h, v6.8h, v1.8h
    mls v6.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #320]
    sqrdmulh v3.8h, v8.8h, v2.8h
    mul v8.8h, v8.8h, v1.8h
    mls v8.8h, v3.8h, v0.h[0]
    zip1 v22.2d, v4.2d, v10.2d
    zip2 v23.2d, v4.2d, v10.2d
    zip1 v26.2d, v6.2d, v12.2d
    zip2 v27.2d, v6.2d, v12.2d
    zip1 v30.2d, v8.2d, v14.2d
    zip2 v31.2d, v8.2d, v14.2d
    add v28.8h, v22.8h, v26.8h
    add v28.8h, v28.8h, v30.8h
    add v29.8h, v23.8h, v27.8h
    add v29.8h, v29.8h, v31.8h

    // U01 iter4, row0 slots0+1 -> hold Q16/Q17 in v5/v11.
    add x7, x3, #1536
    ldr q10, [x1, #896]
    ldr q12, [x1, #1152]
    ldr q14, [x1, #1408]
    mul v16.8h, v10.8h, v0.h[4]
    mul v18.8h, v12.8h, v0.h[4]
    mul v20.8h, v14.8h, v0.h[4]
    sqrdmulh v1.8h, v10.8h, v0.h[5]
    sqrdmulh v3.8h, v12.8h, v0.h[5]
    sqrdmulh v7.8h, v14.8h, v0.h[5]
    mls v16.8h, v1.8h, v0.h[0]
    mls v18.8h, v3.8h, v0.h[0]
    mls v20.8h, v7.8h, v0.h[0]
    sub v10.8h, v10.8h, v16.8h
    sub v12.8h, v12.8h, v18.8h
    sub v14.8h, v14.8h, v20.8h
    ldr q4, [x1, #128]
    ldr q6, [x1, #384]
    ldr q8, [x1, #640]
    add v10.8h, v10.8h, v4.8h
    add v12.8h, v12.8h, v6.8h
    add v14.8h, v14.8h, v8.8h
    add v4.8h, v4.8h, v16.8h
    add v6.8h, v6.8h, v18.8h
    add v8.8h, v8.8h, v20.8h
    ldp q1, q2, [x7, #0]
    sqrdmulh v3.8h, v10.8h, v2.8h
    mul v10.8h, v10.8h, v1.8h
    mls v10.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #64]
    sqrdmulh v3.8h, v12.8h, v2.8h
    mul v12.8h, v12.8h, v1.8h
    mls v12.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #128]
    sqrdmulh v3.8h, v14.8h, v2.8h
    mul v14.8h, v14.8h, v1.8h
    mls v14.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #192]
    sqrdmulh v3.8h, v4.8h, v2.8h
    mul v4.8h, v4.8h, v1.8h
    mls v4.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #256]
    sqrdmulh v3.8h, v6.8h, v2.8h
    mul v6.8h, v6.8h, v1.8h
    mls v6.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #320]
    sqrdmulh v3.8h, v8.8h, v2.8h
    mul v8.8h, v8.8h, v1.8h
    mls v8.8h, v3.8h, v0.h[0]
    zip1 v22.2d, v4.2d, v10.2d
    zip2 v23.2d, v4.2d, v10.2d
    zip1 v26.2d, v6.2d, v12.2d
    zip2 v27.2d, v6.2d, v12.2d
    zip1 v30.2d, v8.2d, v14.2d
    zip2 v31.2d, v8.2d, v14.2d
    add v5.8h, v22.8h, v26.8h
    add v5.8h, v5.8h, v30.8h
    add v11.8h, v23.8h, v27.8h
    add v11.8h, v11.8h, v31.8h

    // U01 iter6, row0 slots0+1 -> hold Q24/Q25 in v13/v15.
    add x7, x3, #2304
    ldr q10, [x1, #960]
    ldr q12, [x1, #1216]
    ldr q14, [x1, #1472]
    mul v16.8h, v10.8h, v0.h[4]
    mul v18.8h, v12.8h, v0.h[4]
    mul v20.8h, v14.8h, v0.h[4]
    sqrdmulh v1.8h, v10.8h, v0.h[5]
    sqrdmulh v3.8h, v12.8h, v0.h[5]
    sqrdmulh v7.8h, v14.8h, v0.h[5]
    mls v16.8h, v1.8h, v0.h[0]
    mls v18.8h, v3.8h, v0.h[0]
    mls v20.8h, v7.8h, v0.h[0]
    sub v10.8h, v10.8h, v16.8h
    sub v12.8h, v12.8h, v18.8h
    sub v14.8h, v14.8h, v20.8h
    ldr q4, [x1, #192]
    ldr q6, [x1, #448]
    ldr q8, [x1, #704]
    add v10.8h, v10.8h, v4.8h
    add v12.8h, v12.8h, v6.8h
    add v14.8h, v14.8h, v8.8h
    add v4.8h, v4.8h, v16.8h
    add v6.8h, v6.8h, v18.8h
    add v8.8h, v8.8h, v20.8h
    ldp q1, q2, [x7, #0]
    sqrdmulh v3.8h, v10.8h, v2.8h
    mul v10.8h, v10.8h, v1.8h
    mls v10.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #64]
    sqrdmulh v3.8h, v12.8h, v2.8h
    mul v12.8h, v12.8h, v1.8h
    mls v12.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #128]
    sqrdmulh v3.8h, v14.8h, v2.8h
    mul v14.8h, v14.8h, v1.8h
    mls v14.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #192]
    sqrdmulh v3.8h, v4.8h, v2.8h
    mul v4.8h, v4.8h, v1.8h
    mls v4.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #256]
    sqrdmulh v3.8h, v6.8h, v2.8h
    mul v6.8h, v6.8h, v1.8h
    mls v6.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #320]
    sqrdmulh v3.8h, v8.8h, v2.8h
    mul v8.8h, v8.8h, v1.8h
    mls v8.8h, v3.8h, v0.h[0]
    zip1 v22.2d, v4.2d, v10.2d
    zip2 v23.2d, v4.2d, v10.2d
    zip1 v26.2d, v6.2d, v12.2d
    zip2 v27.2d, v6.2d, v12.2d
    zip1 v30.2d, v8.2d, v14.2d
    zip2 v31.2d, v8.2d, v14.2d
    add v13.8h, v22.8h, v26.8h
    add v13.8h, v13.8h, v30.8h
    add v15.8h, v23.8h, v27.8h
    add v15.8h, v15.8h, v31.8h

    // NTT32 stage12 twiddles. Production stage12 uses lane 0 after resetting
    // ntt32_twiddle_vecs before each stripe.
    ldr q2, [x12, #16]
    ldr q3, [x12, #32]
    ldr q4, [x12, #48]

    // Stage12 stripe0: Q0/Q8/Q16/Q24.
    add v16.8h, v28.8h, v13.8h
    sqrdmulh v17.8h, v16.8h, v2.h[0]
    mls v16.8h, v17.8h, v0.h[0]
    sub v18.8h, v28.8h, v13.8h
    sqrdmulh v19.8h, v18.8h, v4.h[0]
    mul v18.8h, v18.8h, v3.h[0]
    mls v18.8h, v19.8h, v0.h[0]
    add v20.8h, v24.8h, v5.8h
    sub v21.8h, v24.8h, v5.8h
    add v22.8h, v20.8h, v16.8h
    sub v23.8h, v20.8h, v16.8h
    add v26.8h, v21.8h, v18.8h
    sub v27.8h, v21.8h, v18.8h
    str q22, [x4, #0]
    str q23, [x4, #128]
    str q26, [x4, #256]
    str q27, [x4, #384]

    // Stage12 stripe1: Q1/Q9/Q17/Q25.
    add v16.8h, v29.8h, v15.8h
    sqrdmulh v17.8h, v16.8h, v2.h[0]
    mls v16.8h, v17.8h, v0.h[0]
    sub v18.8h, v29.8h, v15.8h
    sqrdmulh v19.8h, v18.8h, v4.h[0]
    mul v18.8h, v18.8h, v3.h[0]
    mls v18.8h, v19.8h, v0.h[0]
    add v20.8h, v25.8h, v11.8h
    sub v21.8h, v25.8h, v11.8h
    add v22.8h, v20.8h, v16.8h
    sub v23.8h, v20.8h, v16.8h
    add v26.8h, v21.8h, v18.8h
    sub v27.8h, v21.8h, v18.8h
    str q22, [x4, #16]
    str q23, [x4, #144]
    str q26, [x4, #272]
    str q27, [x4, #400]
slothy_end_phase123_u01_stage12_row0_stripe01:
