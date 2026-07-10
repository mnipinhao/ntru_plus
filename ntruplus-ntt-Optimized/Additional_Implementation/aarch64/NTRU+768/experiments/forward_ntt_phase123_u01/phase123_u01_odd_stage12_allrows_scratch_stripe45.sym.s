// Generated source-order prototype for odd all-row shared-prefix U01 -> NTT32 stage12.
// Do not edit the generated body by hand; edit generate_stage12_allrows_u01_odd_scratch.py.
.text

slothy_start_phase123_u01_odd_stage12_allrows_scratch_stripe45:
    // U01 odd iter1: shared P0/P2/P4 prefix.
    add x7, x3, #384
    ldr q10, [x1, #800]
    ldr q12, [x1, #1056]
    ldr q14, [x1, #1312]
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
    ldr q4, [x1, #32]
    ldr q6, [x1, #288]
    ldr q8, [x1, #544]
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

    // Type B U01 odd slot0: a=Z2e, b=Z0e, c=Z4e -> Q4.
    sub v6.8h, v22.8h, v30.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul v8.8h, v6.8h, v0.h[2]
    mls v8.8h, v7.8h, v0.h[0]
    add v9.8h, v26.8h, v22.8h
    add v9.8h, v9.8h, v30.8h
    sub v10.8h, v26.8h, v30.8h
    add v10.8h, v10.8h, v8.8h
    sub v11.8h, v26.8h, v22.8h
    sub v11.8h, v11.8h, v8.8h
    str q9, [x13, #0]
    str q10, [x13, #128]
    str q11, [x13, #256]

    // Type B U01 odd slot1: a=Z4o, b=Z2o, c=Z0o -> Q5.
    sub v6.8h, v27.8h, v23.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul v8.8h, v6.8h, v0.h[2]
    mls v8.8h, v7.8h, v0.h[0]
    add v9.8h, v31.8h, v27.8h
    add v9.8h, v9.8h, v23.8h
    sub v10.8h, v31.8h, v23.8h
    add v10.8h, v10.8h, v8.8h
    sub v11.8h, v31.8h, v27.8h
    sub v11.8h, v11.8h, v8.8h
    str q9, [x13, #16]
    str q10, [x13, #144]
    str q11, [x13, #272]

    // U01 odd iter3: shared P0/P2/P4 prefix.
    add x7, x3, #1152
    ldr q10, [x1, #864]
    ldr q12, [x1, #1120]
    ldr q14, [x1, #1376]
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
    ldr q4, [x1, #96]
    ldr q6, [x1, #352]
    ldr q8, [x1, #608]
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

    // Type A U01 odd slot0: a=Z0e, b=Z4e, c=Z2e -> Q12.
    sub v6.8h, v30.8h, v26.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul v8.8h, v6.8h, v0.h[2]
    mls v8.8h, v7.8h, v0.h[0]
    add v9.8h, v22.8h, v30.8h
    add v9.8h, v9.8h, v26.8h
    sub v10.8h, v22.8h, v26.8h
    add v10.8h, v10.8h, v8.8h
    sub v11.8h, v22.8h, v30.8h
    sub v11.8h, v11.8h, v8.8h
    str q9, [x13, #32]
    str q10, [x13, #160]
    str q11, [x13, #288]

    // Type A U01 odd slot1: a=Z2o, b=Z0o, c=Z4o -> Q13.
    sub v6.8h, v23.8h, v31.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul v8.8h, v6.8h, v0.h[2]
    mls v8.8h, v7.8h, v0.h[0]
    add v9.8h, v27.8h, v23.8h
    add v9.8h, v9.8h, v31.8h
    sub v10.8h, v27.8h, v31.8h
    add v10.8h, v10.8h, v8.8h
    sub v11.8h, v27.8h, v23.8h
    sub v11.8h, v11.8h, v8.8h
    str q9, [x13, #48]
    str q10, [x13, #176]
    str q11, [x13, #304]

    // U01 odd iter5: shared P0/P2/P4 prefix.
    add x7, x3, #1920
    ldr q10, [x1, #928]
    ldr q12, [x1, #1184]
    ldr q14, [x1, #1440]
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
    ldr q4, [x1, #160]
    ldr q6, [x1, #416]
    ldr q8, [x1, #672]
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

    // Type C U01 odd slot0: a=Z4e, b=Z2e, c=Z0e -> Q20.
    sub v6.8h, v26.8h, v22.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul v8.8h, v6.8h, v0.h[2]
    mls v8.8h, v7.8h, v0.h[0]
    add v9.8h, v30.8h, v26.8h
    add v9.8h, v9.8h, v22.8h
    sub v10.8h, v30.8h, v22.8h
    add v10.8h, v10.8h, v8.8h
    sub v11.8h, v30.8h, v26.8h
    sub v11.8h, v11.8h, v8.8h
    str q9, [x13, #64]
    str q10, [x13, #192]
    str q11, [x13, #320]

    // Type C U01 odd slot1: a=Z0o, b=Z4o, c=Z2o -> Q21.
    sub v6.8h, v31.8h, v27.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul v8.8h, v6.8h, v0.h[2]
    mls v8.8h, v7.8h, v0.h[0]
    add v9.8h, v23.8h, v31.8h
    add v9.8h, v9.8h, v27.8h
    sub v10.8h, v23.8h, v27.8h
    add v10.8h, v10.8h, v8.8h
    sub v11.8h, v23.8h, v31.8h
    sub v11.8h, v11.8h, v8.8h
    str q9, [x13, #80]
    str q10, [x13, #208]
    str q11, [x13, #336]

    // U01 odd iter7: shared P0/P2/P4 prefix.
    add x7, x3, #2688
    ldr q10, [x1, #992]
    ldr q12, [x1, #1248]
    ldr q14, [x1, #1504]
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
    ldr q4, [x1, #224]
    ldr q6, [x1, #480]
    ldr q8, [x1, #736]
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

    // Type B U01 odd slot0: a=Z2e, b=Z0e, c=Z4e -> Q28.
    sub v6.8h, v22.8h, v30.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul v8.8h, v6.8h, v0.h[2]
    mls v8.8h, v7.8h, v0.h[0]
    add v9.8h, v26.8h, v22.8h
    add v9.8h, v9.8h, v30.8h
    sub v10.8h, v26.8h, v30.8h
    add v10.8h, v10.8h, v8.8h
    sub v11.8h, v26.8h, v22.8h
    sub v11.8h, v11.8h, v8.8h
    str q9, [x13, #96]
    str q10, [x13, #224]
    str q11, [x13, #352]

    // Type B U01 odd slot1: a=Z4o, b=Z2o, c=Z0o -> Q29.
    sub v6.8h, v27.8h, v23.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul v8.8h, v6.8h, v0.h[2]
    mls v8.8h, v7.8h, v0.h[0]
    add v9.8h, v31.8h, v27.8h
    add v9.8h, v9.8h, v23.8h
    sub v10.8h, v31.8h, v23.8h
    add v10.8h, v10.8h, v8.8h
    sub v11.8h, v31.8h, v27.8h
    sub v11.8h, v11.8h, v8.8h
    str q9, [x13, #112]
    str q10, [x13, #240]
    str q11, [x13, #368]

    ldr q2, [x12, #16]
    ldr q3, [x12, #32]
    ldr q4, [x12, #48]

    // Stage12 row0 stripe4.
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
    str q22, [x4, #64]
    str q23, [x4, #192]
    str q26, [x4, #320]
    str q27, [x4, #448]

    // Stage12 row0 stripe5.
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
    str q22, [x4, #80]
    str q23, [x4, #208]
    str q26, [x4, #336]
    str q27, [x4, #464]

    // Stage12 row1 stripe4.
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
    str q22, [x5, #64]
    str q23, [x5, #192]
    str q26, [x5, #320]
    str q27, [x5, #448]

    // Stage12 row1 stripe5.
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
    str q22, [x5, #80]
    str q23, [x5, #208]
    str q26, [x5, #336]
    str q27, [x5, #464]

    // Stage12 row2 stripe4.
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
    str q22, [x6, #64]
    str q23, [x6, #192]
    str q26, [x6, #320]
    str q27, [x6, #448]

    // Stage12 row2 stripe5.
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
    str q22, [x6, #80]
    str q23, [x6, #208]
    str q26, [x6, #336]
    str q27, [x6, #464]

slothy_end_phase123_u01_odd_stage12_allrows_scratch_stripe45:
