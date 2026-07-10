// Generated source-order prototype for all-row shared-prefix U23 -> NTT32 stage12.
//
// Do not edit the generated body by hand; edit generate_stage12_allrows_u23_scratch.py.
//
// Scope:
//   Phase123 iterations 0/2/4/6, rows0/1/2, slots2+3,
//   then NTT32 stage12 stripes2+3 for rows0/1/2.
//
// Scratch layout at x13, in stage12 consumption order:
//   row0: x13 +   0: Q2,Q3,Q10,Q11,Q18,Q19,Q26,Q27
//   row1: x13 + 128: Q2,Q3,Q10,Q11,Q18,Q19,Q26,Q27
//   row2: x13 + 256: Q2,Q3,Q10,Q11,Q18,Q19,Q26,Q27

.text

// Live-in: x1=input base, x3=Phase123 twist base,
//          x4/x5/x6=row output bases, x12=ntt32_twiddle_vecs,
//          x13=temporary stage12-order scratch, v0=q/constants.
// Live-out: post-stage12 rows0/1/2 Q2/Q3/Q10/Q11/Q18/Q19/Q26/Q27 stores.
slothy_start_phase123_u23_stage12_allrows_scratch_stripe23:
    // U23 iter0: shared P1/P3/P5 prefix.
    add x7, x3, #0
    ldr q10, [x1, #784]
    ldr q12, [x1, #1040]
    ldr q14, [x1, #1296]
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
    ldr q4, [x1, #16]
    ldr q6, [x1, #272]
    ldr q8, [x1, #528]
    add v10.8h, v10.8h, v4.8h
    add v12.8h, v12.8h, v6.8h
    add v14.8h, v14.8h, v8.8h
    add v4.8h, v4.8h, v16.8h
    add v6.8h, v6.8h, v18.8h
    add v8.8h, v8.8h, v20.8h
    ldp q1, q2, [x7, #32]
    sqrdmulh v3.8h, v10.8h, v2.8h
    mul v10.8h, v10.8h, v1.8h
    mls v10.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #96]
    sqrdmulh v3.8h, v12.8h, v2.8h
    mul v12.8h, v12.8h, v1.8h
    mls v12.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #160]
    sqrdmulh v3.8h, v14.8h, v2.8h
    mul v14.8h, v14.8h, v1.8h
    mls v14.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #224]
    sqrdmulh v3.8h, v4.8h, v2.8h
    mul v4.8h, v4.8h, v1.8h
    mls v4.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #288]
    sqrdmulh v3.8h, v6.8h, v2.8h
    mul v6.8h, v6.8h, v1.8h
    mls v6.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #352]
    sqrdmulh v3.8h, v8.8h, v2.8h
    mul v8.8h, v8.8h, v1.8h
    mls v8.8h, v3.8h, v0.h[0]
    zip1 v24.2d, v4.2d, v10.2d
    zip2 v25.2d, v4.2d, v10.2d
    zip1 v28.2d, v6.2d, v12.2d
    zip2 v29.2d, v6.2d, v12.2d
    zip1 v30.2d, v8.2d, v14.2d
    zip2 v31.2d, v8.2d, v14.2d

    // Type A U23 slot2: a=Z5e, b=Z3e, c=Z1e -> Q2.
    sub v6.8h, v28.8h, v24.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul v8.8h, v6.8h, v0.h[2]
    mls v8.8h, v7.8h, v0.h[0]
    add v9.8h, v30.8h, v28.8h
    add v9.8h, v9.8h, v24.8h
    sub v10.8h, v30.8h, v24.8h
    add v10.8h, v10.8h, v8.8h
    sub v11.8h, v30.8h, v28.8h
    sub v11.8h, v11.8h, v8.8h
    str q9, [x13, #0]
    str q10, [x13, #128]
    str q11, [x13, #256]

    // Type A U23 slot3: a=Z1o, b=Z5o, c=Z3o -> Q3.
    sub v6.8h, v31.8h, v29.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul v8.8h, v6.8h, v0.h[2]
    mls v8.8h, v7.8h, v0.h[0]
    add v9.8h, v25.8h, v31.8h
    add v9.8h, v9.8h, v29.8h
    sub v10.8h, v25.8h, v29.8h
    add v10.8h, v10.8h, v8.8h
    sub v11.8h, v25.8h, v31.8h
    sub v11.8h, v11.8h, v8.8h
    str q9, [x13, #16]
    str q10, [x13, #144]
    str q11, [x13, #272]

    // U23 iter2: shared P1/P3/P5 prefix.
    add x7, x3, #768
    ldr q10, [x1, #848]
    ldr q12, [x1, #1104]
    ldr q14, [x1, #1360]
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
    ldr q4, [x1, #80]
    ldr q6, [x1, #336]
    ldr q8, [x1, #592]
    add v10.8h, v10.8h, v4.8h
    add v12.8h, v12.8h, v6.8h
    add v14.8h, v14.8h, v8.8h
    add v4.8h, v4.8h, v16.8h
    add v6.8h, v6.8h, v18.8h
    add v8.8h, v8.8h, v20.8h
    ldp q1, q2, [x7, #32]
    sqrdmulh v3.8h, v10.8h, v2.8h
    mul v10.8h, v10.8h, v1.8h
    mls v10.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #96]
    sqrdmulh v3.8h, v12.8h, v2.8h
    mul v12.8h, v12.8h, v1.8h
    mls v12.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #160]
    sqrdmulh v3.8h, v14.8h, v2.8h
    mul v14.8h, v14.8h, v1.8h
    mls v14.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #224]
    sqrdmulh v3.8h, v4.8h, v2.8h
    mul v4.8h, v4.8h, v1.8h
    mls v4.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #288]
    sqrdmulh v3.8h, v6.8h, v2.8h
    mul v6.8h, v6.8h, v1.8h
    mls v6.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #352]
    sqrdmulh v3.8h, v8.8h, v2.8h
    mul v8.8h, v8.8h, v1.8h
    mls v8.8h, v3.8h, v0.h[0]
    zip1 v24.2d, v4.2d, v10.2d
    zip2 v25.2d, v4.2d, v10.2d
    zip1 v28.2d, v6.2d, v12.2d
    zip2 v29.2d, v6.2d, v12.2d
    zip1 v30.2d, v8.2d, v14.2d
    zip2 v31.2d, v8.2d, v14.2d

    // Type C U23 slot2: a=Z3e, b=Z1e, c=Z5e -> Q10.
    sub v6.8h, v24.8h, v30.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul v8.8h, v6.8h, v0.h[2]
    mls v8.8h, v7.8h, v0.h[0]
    add v9.8h, v28.8h, v24.8h
    add v9.8h, v9.8h, v30.8h
    sub v10.8h, v28.8h, v30.8h
    add v10.8h, v10.8h, v8.8h
    sub v11.8h, v28.8h, v24.8h
    sub v11.8h, v11.8h, v8.8h
    str q9, [x13, #32]
    str q10, [x13, #160]
    str q11, [x13, #288]

    // Type C U23 slot3: a=Z5o, b=Z3o, c=Z1o -> Q11.
    sub v6.8h, v29.8h, v25.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul v8.8h, v6.8h, v0.h[2]
    mls v8.8h, v7.8h, v0.h[0]
    add v9.8h, v31.8h, v29.8h
    add v9.8h, v9.8h, v25.8h
    sub v10.8h, v31.8h, v25.8h
    add v10.8h, v10.8h, v8.8h
    sub v11.8h, v31.8h, v29.8h
    sub v11.8h, v11.8h, v8.8h
    str q9, [x13, #48]
    str q10, [x13, #176]
    str q11, [x13, #304]

    // U23 iter4: shared P1/P3/P5 prefix.
    add x7, x3, #1536
    ldr q10, [x1, #912]
    ldr q12, [x1, #1168]
    ldr q14, [x1, #1424]
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
    ldr q4, [x1, #144]
    ldr q6, [x1, #400]
    ldr q8, [x1, #656]
    add v10.8h, v10.8h, v4.8h
    add v12.8h, v12.8h, v6.8h
    add v14.8h, v14.8h, v8.8h
    add v4.8h, v4.8h, v16.8h
    add v6.8h, v6.8h, v18.8h
    add v8.8h, v8.8h, v20.8h
    ldp q1, q2, [x7, #32]
    sqrdmulh v3.8h, v10.8h, v2.8h
    mul v10.8h, v10.8h, v1.8h
    mls v10.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #96]
    sqrdmulh v3.8h, v12.8h, v2.8h
    mul v12.8h, v12.8h, v1.8h
    mls v12.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #160]
    sqrdmulh v3.8h, v14.8h, v2.8h
    mul v14.8h, v14.8h, v1.8h
    mls v14.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #224]
    sqrdmulh v3.8h, v4.8h, v2.8h
    mul v4.8h, v4.8h, v1.8h
    mls v4.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #288]
    sqrdmulh v3.8h, v6.8h, v2.8h
    mul v6.8h, v6.8h, v1.8h
    mls v6.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #352]
    sqrdmulh v3.8h, v8.8h, v2.8h
    mul v8.8h, v8.8h, v1.8h
    mls v8.8h, v3.8h, v0.h[0]
    zip1 v24.2d, v4.2d, v10.2d
    zip2 v25.2d, v4.2d, v10.2d
    zip1 v28.2d, v6.2d, v12.2d
    zip2 v29.2d, v6.2d, v12.2d
    zip1 v30.2d, v8.2d, v14.2d
    zip2 v31.2d, v8.2d, v14.2d

    // Type B U23 slot2: a=Z1e, b=Z5e, c=Z3e -> Q18.
    sub v6.8h, v30.8h, v28.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul v8.8h, v6.8h, v0.h[2]
    mls v8.8h, v7.8h, v0.h[0]
    add v9.8h, v24.8h, v30.8h
    add v9.8h, v9.8h, v28.8h
    sub v10.8h, v24.8h, v28.8h
    add v10.8h, v10.8h, v8.8h
    sub v11.8h, v24.8h, v30.8h
    sub v11.8h, v11.8h, v8.8h
    str q9, [x13, #64]
    str q10, [x13, #192]
    str q11, [x13, #320]

    // Type B U23 slot3: a=Z3o, b=Z1o, c=Z5o -> Q19.
    sub v6.8h, v25.8h, v31.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul v8.8h, v6.8h, v0.h[2]
    mls v8.8h, v7.8h, v0.h[0]
    add v9.8h, v29.8h, v25.8h
    add v9.8h, v9.8h, v31.8h
    sub v10.8h, v29.8h, v31.8h
    add v10.8h, v10.8h, v8.8h
    sub v11.8h, v29.8h, v25.8h
    sub v11.8h, v11.8h, v8.8h
    str q9, [x13, #80]
    str q10, [x13, #208]
    str q11, [x13, #336]

    // U23 iter6: shared P1/P3/P5 prefix.
    add x7, x3, #2304
    ldr q10, [x1, #976]
    ldr q12, [x1, #1232]
    ldr q14, [x1, #1488]
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
    ldr q4, [x1, #208]
    ldr q6, [x1, #464]
    ldr q8, [x1, #720]
    add v10.8h, v10.8h, v4.8h
    add v12.8h, v12.8h, v6.8h
    add v14.8h, v14.8h, v8.8h
    add v4.8h, v4.8h, v16.8h
    add v6.8h, v6.8h, v18.8h
    add v8.8h, v8.8h, v20.8h
    ldp q1, q2, [x7, #32]
    sqrdmulh v3.8h, v10.8h, v2.8h
    mul v10.8h, v10.8h, v1.8h
    mls v10.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #96]
    sqrdmulh v3.8h, v12.8h, v2.8h
    mul v12.8h, v12.8h, v1.8h
    mls v12.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #160]
    sqrdmulh v3.8h, v14.8h, v2.8h
    mul v14.8h, v14.8h, v1.8h
    mls v14.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #224]
    sqrdmulh v3.8h, v4.8h, v2.8h
    mul v4.8h, v4.8h, v1.8h
    mls v4.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #288]
    sqrdmulh v3.8h, v6.8h, v2.8h
    mul v6.8h, v6.8h, v1.8h
    mls v6.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x7, #352]
    sqrdmulh v3.8h, v8.8h, v2.8h
    mul v8.8h, v8.8h, v1.8h
    mls v8.8h, v3.8h, v0.h[0]
    zip1 v24.2d, v4.2d, v10.2d
    zip2 v25.2d, v4.2d, v10.2d
    zip1 v28.2d, v6.2d, v12.2d
    zip2 v29.2d, v6.2d, v12.2d
    zip1 v30.2d, v8.2d, v14.2d
    zip2 v31.2d, v8.2d, v14.2d

    // Type A U23 slot2: a=Z5e, b=Z3e, c=Z1e -> Q26.
    sub v6.8h, v28.8h, v24.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul v8.8h, v6.8h, v0.h[2]
    mls v8.8h, v7.8h, v0.h[0]
    add v9.8h, v30.8h, v28.8h
    add v9.8h, v9.8h, v24.8h
    sub v10.8h, v30.8h, v24.8h
    add v10.8h, v10.8h, v8.8h
    sub v11.8h, v30.8h, v28.8h
    sub v11.8h, v11.8h, v8.8h
    str q9, [x13, #96]
    str q10, [x13, #224]
    str q11, [x13, #352]

    // Type A U23 slot3: a=Z1o, b=Z5o, c=Z3o -> Q27.
    sub v6.8h, v31.8h, v29.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul v8.8h, v6.8h, v0.h[2]
    mls v8.8h, v7.8h, v0.h[0]
    add v9.8h, v25.8h, v31.8h
    add v9.8h, v9.8h, v29.8h
    sub v10.8h, v25.8h, v29.8h
    add v10.8h, v10.8h, v8.8h
    sub v11.8h, v25.8h, v31.8h
    sub v11.8h, v11.8h, v8.8h
    str q9, [x13, #112]
    str q10, [x13, #240]
    str q11, [x13, #368]

    // NTT32 stage12 twiddles. Production resets ntt32_twiddle_vecs
    // before each stripe, so stripe2/3 both use lane 0.
    ldr q2, [x12, #16]
    ldr q3, [x12, #32]
    ldr q4, [x12, #48]

    // Stage12 row0 stripe2.
    ldr q24, [x13, #0]
    ldr q28, [x13, #32]
    ldr q5, [x13, #64]
    ldr q13, [x13, #96]
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
    str q22, [x4, #32]
    str q23, [x4, #160]
    str q26, [x4, #288]
    str q27, [x4, #416]

    // Stage12 row0 stripe3.
    ldr q24, [x13, #16]
    ldr q28, [x13, #48]
    ldr q5, [x13, #80]
    ldr q13, [x13, #112]
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
    str q22, [x4, #48]
    str q23, [x4, #176]
    str q26, [x4, #304]
    str q27, [x4, #432]

    // Stage12 row1 stripe2.
    ldr q24, [x13, #128]
    ldr q28, [x13, #160]
    ldr q5, [x13, #192]
    ldr q13, [x13, #224]
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
    str q22, [x5, #32]
    str q23, [x5, #160]
    str q26, [x5, #288]
    str q27, [x5, #416]

    // Stage12 row1 stripe3.
    ldr q24, [x13, #144]
    ldr q28, [x13, #176]
    ldr q5, [x13, #208]
    ldr q13, [x13, #240]
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
    str q22, [x5, #48]
    str q23, [x5, #176]
    str q26, [x5, #304]
    str q27, [x5, #432]

    // Stage12 row2 stripe2.
    ldr q24, [x13, #256]
    ldr q28, [x13, #288]
    ldr q5, [x13, #320]
    ldr q13, [x13, #352]
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
    str q22, [x6, #32]
    str q23, [x6, #160]
    str q26, [x6, #288]
    str q27, [x6, #416]

    // Stage12 row2 stripe3.
    ldr q24, [x13, #272]
    ldr q28, [x13, #304]
    ldr q5, [x13, #336]
    ldr q13, [x13, #368]
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
    str q22, [x6, #48]
    str q23, [x6, #176]
    str q26, [x6, #304]
    str q27, [x6, #432]

slothy_end_phase123_u23_stage12_allrows_scratch_stripe23:
