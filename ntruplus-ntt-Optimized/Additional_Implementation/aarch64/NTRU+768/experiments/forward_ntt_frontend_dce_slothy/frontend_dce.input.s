// Generated from the three production frontend iteration classes.
// Live-in: x1 input, x3 constants, x4/x5/x6 row outputs, v0 constants.
// Live-out: twelve q stores; x1/x3/x4/x5/x6 are dead at the integration boundary.
// Coefficient range: unchanged from the production Phase123 frontend.
// Reserved physical registers: all GPRs are fixed; v0 is fixed.
.text

// Iteration class 0: iterations 0, 3, 6
// Live-in: x1, x3, x4, x5, x6, v0.
// Live-out: twelve q stores; pointer values are dead.
// Coefficient range: identical to production.
// Reserved physical registers: x0-x30, sp, and v0.
slothy_start_gt_frontend_dce_class0:
    // high side
    ldp q10, q11, [x1, #768]
    ldr q12, [x1, #1024]
    ldr q13, [x1, #1040]
    ldr q14, [x1, #1280]
    ldr q15, [x1, #1296]
    mul v16.8h, v10.8h, v0.h[4]
    mul v17.8h, v11.8h, v0.h[4]
    mul v18.8h, v12.8h, v0.h[4]
    mul v19.8h, v13.8h, v0.h[4]
    mul v20.8h, v14.8h, v0.h[4]
    mul v21.8h, v15.8h, v0.h[4]
    sqrdmulh v4.8h, v10.8h, v0.h[5]
    sqrdmulh v5.8h, v11.8h, v0.h[5]
    sqrdmulh v6.8h, v12.8h, v0.h[5]
    sqrdmulh v7.8h, v13.8h, v0.h[5]
    sqrdmulh v8.8h, v14.8h, v0.h[5]
    sqrdmulh v9.8h, v15.8h, v0.h[5]
    mls v16.8h, v4.8h, v0.h[0]
    mls v17.8h, v5.8h, v0.h[0]
    mls v18.8h, v6.8h, v0.h[0]
    mls v19.8h, v7.8h, v0.h[0]
    mls v20.8h, v8.8h, v0.h[0]
    mls v21.8h, v9.8h, v0.h[0]
    sub v10.8h, v10.8h, v16.8h
    sub v11.8h, v11.8h, v17.8h
    sub v12.8h, v12.8h, v18.8h
    sub v13.8h, v13.8h, v19.8h
    sub v14.8h, v14.8h, v20.8h
    sub v15.8h, v15.8h, v21.8h
    ldp q4, q5, [x1, #0]
    ldp q6, q7, [x1, #256]
    ldp q8, q9, [x1, #512]
    add v10.8h, v10.8h, v4.8h
    add v11.8h, v11.8h, v5.8h
    add v12.8h, v12.8h, v6.8h
    add v13.8h, v13.8h, v7.8h
    add v14.8h, v14.8h, v8.8h
    add v15.8h, v15.8h, v9.8h
    add v4.8h, v4.8h, v16.8h
    add v5.8h, v5.8h, v17.8h
    add v6.8h, v6.8h, v18.8h
    add v7.8h, v7.8h, v19.8h
    add v8.8h, v8.8h, v20.8h
    add v9.8h, v9.8h, v21.8h
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v10.8h, v2.8h
    mul      v10.8h, v10.8h, v1.8h
    mls      v10.8h, v3.8h, v0.h[0]
    // v11 = [B1[8]..B1[15]], blocks k=2,3
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v11.8h, v2.8h
    mul      v11.8h, v11.8h, v1.8h
    mls      v11.8h, v3.8h, v0.h[0]
    // v12 = [B1[128]..B1[135]], blocks k=32,33
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v12.8h, v2.8h
    mul      v12.8h, v12.8h, v1.8h
    mls      v12.8h, v3.8h, v0.h[0]
    // v13 = [B1[136]..B1[143]], blocks k=34,35
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v13.8h, v2.8h
    mul      v13.8h, v13.8h, v1.8h
    mls      v13.8h, v3.8h, v0.h[0]
    // v14 = [B1[256]..B1[263]], blocks k=64,65
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v14.8h, v2.8h
    mul      v14.8h, v14.8h, v1.8h
    mls      v14.8h, v3.8h, v0.h[0]
    // v15 = [B1[264]..B1[271]], blocks k=66,67
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v15.8h, v2.8h
    mul      v15.8h, v15.8h, v1.8h
    mls      v15.8h, v3.8h, v0.h[0]
    // v4 = [B0[0]..B0[7]], blocks k=0,1
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v4.8h, v2.8h
    mul      v4.8h, v4.8h, v1.8h
    mls      v4.8h, v3.8h, v0.h[0]
    // v5 = [B0[8]..B0[15]], blocks k=2,3
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v5.8h, v2.8h
    mul      v5.8h, v5.8h, v1.8h
    mls      v5.8h, v3.8h, v0.h[0]
    // v6 = [B0[128]..B0[135]], blocks k=32,33
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v6.8h, v2.8h
    mul      v6.8h, v6.8h, v1.8h
    mls      v6.8h, v3.8h, v0.h[0]
    // v7 = [B0[136]..B0[143]], blocks k=34,35
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v7.8h, v2.8h
    mul      v7.8h, v7.8h, v1.8h
    mls      v7.8h, v3.8h, v0.h[0]
    // v8 = [B0[256]..B0[263]], blocks k=64,65
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v8.8h, v2.8h
    mul      v8.8h, v8.8h, v1.8h
    mls      v8.8h, v3.8h, v0.h[0]
    // v9 = [B0[264]..B0[271]], blocks k=66,67
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v9.8h, v2.8h
    mul      v9.8h, v9.8h, v1.8h
    mls      v9.8h, v3.8h, v0.h[0]
    zip1 v22.2d, v4.2d, v10.2d
    zip2 v23.2d, v4.2d, v10.2d
    zip1 v24.2d, v5.2d, v11.2d
    zip2 v25.2d, v5.2d, v11.2d
    zip1 v26.2d, v6.2d, v12.2d
    zip2 v27.2d, v6.2d, v12.2d
    zip1 v28.2d, v7.2d, v13.2d
    zip2 v29.2d, v7.2d, v13.2d
    zip1 v30.2d, v8.2d, v14.2d
    zip2 v31.2d, v8.2d, v14.2d
    zip1 v4.2d, v9.2d, v15.2d
    zip2 v5.2d, v9.2d, v15.2d
    sub      v6.8h, v30.8h, v26.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul      v8.8h, v6.8h, v0.h[2]
    mls      v8.8h, v7.8h, v0.h[0]
    add      v9.8h,  v22.8h, v30.8h
    add      v9.8h,  v9.8h,  v26.8h
    sub      v10.8h, v22.8h, v26.8h
    add      v10.8h, v10.8h, v8.8h
    sub      v11.8h, v22.8h, v30.8h
    sub      v11.8h, v11.8h, v8.8h
    str q9,  [x4, #0]
    str q10, [x5, #0]
    str q11, [x6, #0]
    sub      v6.8h, v23.8h, v31.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul      v8.8h, v6.8h, v0.h[2]
    mls      v8.8h, v7.8h, v0.h[0]
    add      v9.8h,  v27.8h, v23.8h
    add      v9.8h,  v9.8h,  v31.8h
    sub      v10.8h, v27.8h, v31.8h
    add      v10.8h, v10.8h, v8.8h
    sub      v11.8h, v27.8h, v23.8h
    sub      v11.8h, v11.8h, v8.8h
    str q9,  [x4, #16]
    str q10, [x5, #16]
    str q11, [x6, #16]
    sub      v6.8h, v28.8h, v24.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul      v8.8h, v6.8h, v0.h[2]
    mls      v8.8h, v7.8h, v0.h[0]
    add      v9.8h,  v4.8h, v28.8h
    add      v9.8h,  v9.8h,  v24.8h
    sub      v10.8h, v4.8h, v24.8h
    add      v10.8h, v10.8h, v8.8h
    sub      v11.8h, v4.8h, v28.8h
    sub      v11.8h, v11.8h, v8.8h
    str q9,  [x4, #32]
    str q10, [x5, #32]
    str q11, [x6, #32]
    sub      v6.8h, v5.8h, v29.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul      v8.8h, v6.8h, v0.h[2]
    mls      v8.8h, v7.8h, v0.h[0]
    add      v9.8h,  v25.8h, v5.8h
    add      v9.8h,  v9.8h,  v29.8h
    sub      v10.8h, v25.8h, v29.8h
    add      v10.8h, v10.8h, v8.8h
    sub      v11.8h, v25.8h, v5.8h
    sub      v11.8h, v11.8h, v8.8h
    str q9,  [x4, #48]
    str q10, [x5, #48]
    str q11, [x6, #48]
slothy_end_gt_frontend_dce_class0:

// Iteration class 1: iterations 1, 4, 7
// Live-in: x1, x3, x4, x5, x6, v0.
// Live-out: twelve q stores; pointer values are dead.
// Coefficient range: identical to production.
// Reserved physical registers: x0-x30, sp, and v0.
slothy_start_gt_frontend_dce_class1:
    // high side
    ldp q10, q11, [x1, #768]
    ldr q12, [x1, #1024]
    ldr q13, [x1, #1040]
    ldr q14, [x1, #1280]
    ldr q15, [x1, #1296]
    mul v16.8h, v10.8h, v0.h[4]
    mul v17.8h, v11.8h, v0.h[4]
    mul v18.8h, v12.8h, v0.h[4]
    mul v19.8h, v13.8h, v0.h[4]
    mul v20.8h, v14.8h, v0.h[4]
    mul v21.8h, v15.8h, v0.h[4]
    sqrdmulh v4.8h, v10.8h, v0.h[5]
    sqrdmulh v5.8h, v11.8h, v0.h[5]
    sqrdmulh v6.8h, v12.8h, v0.h[5]
    sqrdmulh v7.8h, v13.8h, v0.h[5]
    sqrdmulh v8.8h, v14.8h, v0.h[5]
    sqrdmulh v9.8h, v15.8h, v0.h[5]
    mls v16.8h, v4.8h, v0.h[0]
    mls v17.8h, v5.8h, v0.h[0]
    mls v18.8h, v6.8h, v0.h[0]
    mls v19.8h, v7.8h, v0.h[0]
    mls v20.8h, v8.8h, v0.h[0]
    mls v21.8h, v9.8h, v0.h[0]
    sub v10.8h, v10.8h, v16.8h
    sub v11.8h, v11.8h, v17.8h
    sub v12.8h, v12.8h, v18.8h
    sub v13.8h, v13.8h, v19.8h
    sub v14.8h, v14.8h, v20.8h
    sub v15.8h, v15.8h, v21.8h
    ldp q4, q5, [x1, #0]
    ldp q6, q7, [x1, #256]
    ldp q8, q9, [x1, #512]
    add v10.8h, v10.8h, v4.8h
    add v11.8h, v11.8h, v5.8h
    add v12.8h, v12.8h, v6.8h
    add v13.8h, v13.8h, v7.8h
    add v14.8h, v14.8h, v8.8h
    add v15.8h, v15.8h, v9.8h
    add v4.8h, v4.8h, v16.8h
    add v5.8h, v5.8h, v17.8h
    add v6.8h, v6.8h, v18.8h
    add v7.8h, v7.8h, v19.8h
    add v8.8h, v8.8h, v20.8h
    add v9.8h, v9.8h, v21.8h
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v10.8h, v2.8h
    mul      v10.8h, v10.8h, v1.8h
    mls      v10.8h, v3.8h, v0.h[0]
    // v11 = [B1[8]..B1[15]], blocks k=2,3
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v11.8h, v2.8h
    mul      v11.8h, v11.8h, v1.8h
    mls      v11.8h, v3.8h, v0.h[0]
    // v12 = [B1[128]..B1[135]], blocks k=32,33
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v12.8h, v2.8h
    mul      v12.8h, v12.8h, v1.8h
    mls      v12.8h, v3.8h, v0.h[0]
    // v13 = [B1[136]..B1[143]], blocks k=34,35
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v13.8h, v2.8h
    mul      v13.8h, v13.8h, v1.8h
    mls      v13.8h, v3.8h, v0.h[0]
    // v14 = [B1[256]..B1[263]], blocks k=64,65
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v14.8h, v2.8h
    mul      v14.8h, v14.8h, v1.8h
    mls      v14.8h, v3.8h, v0.h[0]
    // v15 = [B1[264]..B1[271]], blocks k=66,67
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v15.8h, v2.8h
    mul      v15.8h, v15.8h, v1.8h
    mls      v15.8h, v3.8h, v0.h[0]
    // v4 = [B0[0]..B0[7]], blocks k=0,1
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v4.8h, v2.8h
    mul      v4.8h, v4.8h, v1.8h
    mls      v4.8h, v3.8h, v0.h[0]
    // v5 = [B0[8]..B0[15]], blocks k=2,3
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v5.8h, v2.8h
    mul      v5.8h, v5.8h, v1.8h
    mls      v5.8h, v3.8h, v0.h[0]
    // v6 = [B0[128]..B0[135]], blocks k=32,33
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v6.8h, v2.8h
    mul      v6.8h, v6.8h, v1.8h
    mls      v6.8h, v3.8h, v0.h[0]
    // v7 = [B0[136]..B0[143]], blocks k=34,35
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v7.8h, v2.8h
    mul      v7.8h, v7.8h, v1.8h
    mls      v7.8h, v3.8h, v0.h[0]
    // v8 = [B0[256]..B0[263]], blocks k=64,65
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v8.8h, v2.8h
    mul      v8.8h, v8.8h, v1.8h
    mls      v8.8h, v3.8h, v0.h[0]
    // v9 = [B0[264]..B0[271]], blocks k=66,67
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v9.8h, v2.8h
    mul      v9.8h, v9.8h, v1.8h
    mls      v9.8h, v3.8h, v0.h[0]
    zip1 v22.2d, v4.2d, v10.2d
    zip2 v23.2d, v4.2d, v10.2d
    zip1 v24.2d, v5.2d, v11.2d
    zip2 v25.2d, v5.2d, v11.2d
    zip1 v26.2d, v6.2d, v12.2d
    zip2 v27.2d, v6.2d, v12.2d
    zip1 v28.2d, v7.2d, v13.2d
    zip2 v29.2d, v7.2d, v13.2d
    zip1 v30.2d, v8.2d, v14.2d
    zip2 v31.2d, v8.2d, v14.2d
    zip1 v4.2d, v9.2d, v15.2d
    zip2 v5.2d, v9.2d, v15.2d
    sub      v6.8h, v22.8h, v30.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul      v8.8h, v6.8h, v0.h[2]
    mls      v8.8h, v7.8h, v0.h[0]
    add      v9.8h,  v26.8h, v22.8h
    add      v9.8h,  v9.8h,  v30.8h
    sub      v10.8h, v26.8h, v30.8h
    add      v10.8h, v10.8h, v8.8h
    sub      v11.8h, v26.8h, v22.8h
    sub      v11.8h, v11.8h, v8.8h
    str q9,  [x4, #0]
    str q10, [x5, #0]
    str q11, [x6, #0]
    sub      v6.8h, v27.8h, v23.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul      v8.8h, v6.8h, v0.h[2]
    mls      v8.8h, v7.8h, v0.h[0]
    add      v9.8h,  v31.8h, v27.8h
    add      v9.8h,  v9.8h,  v23.8h
    sub      v10.8h, v31.8h, v23.8h
    add      v10.8h, v10.8h, v8.8h
    sub      v11.8h, v31.8h, v27.8h
    sub      v11.8h, v11.8h, v8.8h
    str q9,  [x4, #16]
    str q10, [x5, #16]
    str q11, [x6, #16]
    sub      v6.8h, v4.8h, v28.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul      v8.8h, v6.8h, v0.h[2]
    mls      v8.8h, v7.8h, v0.h[0]
    add      v9.8h,  v24.8h, v4.8h
    add      v9.8h,  v9.8h,  v28.8h
    sub      v10.8h, v24.8h, v28.8h
    add      v10.8h, v10.8h, v8.8h
    sub      v11.8h, v24.8h, v4.8h
    sub      v11.8h, v11.8h, v8.8h
    str q9,  [x4, #32]
    str q10, [x5, #32]
    str q11, [x6, #32]
    sub      v6.8h, v25.8h, v5.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul      v8.8h, v6.8h, v0.h[2]
    mls      v8.8h, v7.8h, v0.h[0]
    add      v9.8h,  v29.8h, v25.8h
    add      v9.8h,  v9.8h,  v5.8h
    sub      v10.8h, v29.8h, v5.8h
    add      v10.8h, v10.8h, v8.8h
    sub      v11.8h, v29.8h, v25.8h
    sub      v11.8h, v11.8h, v8.8h
    str q9,  [x4, #48]
    str q10, [x5, #48]
    str q11, [x6, #48]
slothy_end_gt_frontend_dce_class1:

// Iteration class 2: iterations 2, 5
// Live-in: x1, x3, x4, x5, x6, v0.
// Live-out: twelve q stores; pointer values are dead.
// Coefficient range: identical to production.
// Reserved physical registers: x0-x30, sp, and v0.
slothy_start_gt_frontend_dce_class2:
    // high side
    ldp q10, q11, [x1, #768]
    ldr q12, [x1, #1024]
    ldr q13, [x1, #1040]
    ldr q14, [x1, #1280]
    ldr q15, [x1, #1296]
    mul v16.8h, v10.8h, v0.h[4]
    mul v17.8h, v11.8h, v0.h[4]
    mul v18.8h, v12.8h, v0.h[4]
    mul v19.8h, v13.8h, v0.h[4]
    mul v20.8h, v14.8h, v0.h[4]
    mul v21.8h, v15.8h, v0.h[4]
    sqrdmulh v4.8h, v10.8h, v0.h[5]
    sqrdmulh v5.8h, v11.8h, v0.h[5]
    sqrdmulh v6.8h, v12.8h, v0.h[5]
    sqrdmulh v7.8h, v13.8h, v0.h[5]
    sqrdmulh v8.8h, v14.8h, v0.h[5]
    sqrdmulh v9.8h, v15.8h, v0.h[5]
    mls v16.8h, v4.8h, v0.h[0]
    mls v17.8h, v5.8h, v0.h[0]
    mls v18.8h, v6.8h, v0.h[0]
    mls v19.8h, v7.8h, v0.h[0]
    mls v20.8h, v8.8h, v0.h[0]
    mls v21.8h, v9.8h, v0.h[0]
    sub v10.8h, v10.8h, v16.8h
    sub v11.8h, v11.8h, v17.8h
    sub v12.8h, v12.8h, v18.8h
    sub v13.8h, v13.8h, v19.8h
    sub v14.8h, v14.8h, v20.8h
    sub v15.8h, v15.8h, v21.8h
    ldp q4, q5, [x1, #0]
    ldp q6, q7, [x1, #256]
    ldp q8, q9, [x1, #512]
    add v10.8h, v10.8h, v4.8h
    add v11.8h, v11.8h, v5.8h
    add v12.8h, v12.8h, v6.8h
    add v13.8h, v13.8h, v7.8h
    add v14.8h, v14.8h, v8.8h
    add v15.8h, v15.8h, v9.8h
    add v4.8h, v4.8h, v16.8h
    add v5.8h, v5.8h, v17.8h
    add v6.8h, v6.8h, v18.8h
    add v7.8h, v7.8h, v19.8h
    add v8.8h, v8.8h, v20.8h
    add v9.8h, v9.8h, v21.8h
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v10.8h, v2.8h
    mul      v10.8h, v10.8h, v1.8h
    mls      v10.8h, v3.8h, v0.h[0]
    // v11 = [B1[8]..B1[15]], blocks k=2,3
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v11.8h, v2.8h
    mul      v11.8h, v11.8h, v1.8h
    mls      v11.8h, v3.8h, v0.h[0]
    // v12 = [B1[128]..B1[135]], blocks k=32,33
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v12.8h, v2.8h
    mul      v12.8h, v12.8h, v1.8h
    mls      v12.8h, v3.8h, v0.h[0]
    // v13 = [B1[136]..B1[143]], blocks k=34,35
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v13.8h, v2.8h
    mul      v13.8h, v13.8h, v1.8h
    mls      v13.8h, v3.8h, v0.h[0]
    // v14 = [B1[256]..B1[263]], blocks k=64,65
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v14.8h, v2.8h
    mul      v14.8h, v14.8h, v1.8h
    mls      v14.8h, v3.8h, v0.h[0]
    // v15 = [B1[264]..B1[271]], blocks k=66,67
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v15.8h, v2.8h
    mul      v15.8h, v15.8h, v1.8h
    mls      v15.8h, v3.8h, v0.h[0]
    // v4 = [B0[0]..B0[7]], blocks k=0,1
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v4.8h, v2.8h
    mul      v4.8h, v4.8h, v1.8h
    mls      v4.8h, v3.8h, v0.h[0]
    // v5 = [B0[8]..B0[15]], blocks k=2,3
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v5.8h, v2.8h
    mul      v5.8h, v5.8h, v1.8h
    mls      v5.8h, v3.8h, v0.h[0]
    // v6 = [B0[128]..B0[135]], blocks k=32,33
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v6.8h, v2.8h
    mul      v6.8h, v6.8h, v1.8h
    mls      v6.8h, v3.8h, v0.h[0]
    // v7 = [B0[136]..B0[143]], blocks k=34,35
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v7.8h, v2.8h
    mul      v7.8h, v7.8h, v1.8h
    mls      v7.8h, v3.8h, v0.h[0]
    // v8 = [B0[256]..B0[263]], blocks k=64,65
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v8.8h, v2.8h
    mul      v8.8h, v8.8h, v1.8h
    mls      v8.8h, v3.8h, v0.h[0]
    // v9 = [B0[264]..B0[271]], blocks k=66,67
    ldp q1, q2, [x3], #32
    sqrdmulh v3.8h, v9.8h, v2.8h
    mul      v9.8h, v9.8h, v1.8h
    mls      v9.8h, v3.8h, v0.h[0]
    zip1 v22.2d, v4.2d, v10.2d
    zip2 v23.2d, v4.2d, v10.2d
    zip1 v24.2d, v5.2d, v11.2d
    zip2 v25.2d, v5.2d, v11.2d
    zip1 v26.2d, v6.2d, v12.2d
    zip2 v27.2d, v6.2d, v12.2d
    zip1 v28.2d, v7.2d, v13.2d
    zip2 v29.2d, v7.2d, v13.2d
    zip1 v30.2d, v8.2d, v14.2d
    zip2 v31.2d, v8.2d, v14.2d
    zip1 v4.2d, v9.2d, v15.2d
    zip2 v5.2d, v9.2d, v15.2d
    sub      v6.8h, v26.8h, v22.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul      v8.8h, v6.8h, v0.h[2]
    mls      v8.8h, v7.8h, v0.h[0]
    add      v9.8h,  v30.8h, v26.8h
    add      v9.8h,  v9.8h,  v22.8h
    sub      v10.8h, v30.8h, v22.8h
    add      v10.8h, v10.8h, v8.8h
    sub      v11.8h, v30.8h, v26.8h
    sub      v11.8h, v11.8h, v8.8h
    str q9,  [x4, #0]
    str q10, [x5, #0]
    str q11, [x6, #0]
    sub      v6.8h, v31.8h, v27.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul      v8.8h, v6.8h, v0.h[2]
    mls      v8.8h, v7.8h, v0.h[0]
    add      v9.8h,  v23.8h, v31.8h
    add      v9.8h,  v9.8h,  v27.8h
    sub      v10.8h, v23.8h, v27.8h
    add      v10.8h, v10.8h, v8.8h
    sub      v11.8h, v23.8h, v31.8h
    sub      v11.8h, v11.8h, v8.8h
    str q9,  [x4, #16]
    str q10, [x5, #16]
    str q11, [x6, #16]
    sub      v6.8h, v24.8h, v4.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul      v8.8h, v6.8h, v0.h[2]
    mls      v8.8h, v7.8h, v0.h[0]
    add      v9.8h,  v28.8h, v24.8h
    add      v9.8h,  v9.8h,  v4.8h
    sub      v10.8h, v28.8h, v4.8h
    add      v10.8h, v10.8h, v8.8h
    sub      v11.8h, v28.8h, v24.8h
    sub      v11.8h, v11.8h, v8.8h
    str q9,  [x4, #32]
    str q10, [x5, #32]
    str q11, [x6, #32]
    sub      v6.8h, v29.8h, v25.8h
    sqrdmulh v7.8h, v6.8h, v0.h[3]
    mul      v8.8h, v6.8h, v0.h[2]
    mls      v8.8h, v7.8h, v0.h[0]
    add      v9.8h,  v5.8h, v29.8h
    add      v9.8h,  v9.8h,  v25.8h
    sub      v10.8h, v5.8h, v25.8h
    add      v10.8h, v10.8h, v8.8h
    sub      v11.8h, v5.8h, v29.8h
    sub      v11.8h, v11.8h, v8.8h
    str q9,  [x4, #48]
    str q10, [x5, #48]
    str q11, [x6, #48]
slothy_end_gt_frontend_dce_class2:
