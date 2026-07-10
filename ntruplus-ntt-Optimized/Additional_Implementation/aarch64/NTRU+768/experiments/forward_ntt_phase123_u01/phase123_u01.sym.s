// Phase123 U01 symbolic prototype.
//
// This file is not production assembly.  It isolates the Phase123 slots0+1
// producer for the direct-stage12 route.
//
// Live-in:
//   x1 = input pointer at selected Phase123 iteration
//   x3 = twist/precompute base for selected Phase123 iteration
//   x4 = row0 output pointer for selected Phase123 iteration
//   x5 = row1 output pointer for selected Phase123 iteration
//   x6 = row2 output pointer for selected Phase123 iteration
//   v0 = q/reduction/DFT3 constants
//
// Live-out:
//   [x4/#0,#16], [x5/#0,#16], [x6/#0,#16] store slots0+1.
//   x1/x3/x4/x5/x6 are unchanged.

.text

// Common U01 producer prefix:
//   Produce P0/P2/P4 B0/B1 values, apply their twiddle/precompute pairs,
//   and create Z0e/Z0o, Z2e/Z2o, Z4e/Z4o.
//
// Register result:
//   v22/v23 = Z0e/Z0o
//   v26/v27 = Z2e/Z2o
//   v30/v31 = Z4e/Z4o

slothy_start_ntt_phase123_u01_type_a:
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

    ldp q1, q2, [x3, #0]
    sqrdmulh v3.8h, v10.8h, v2.8h
    mul v10.8h, v10.8h, v1.8h
    mls v10.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x3, #64]
    sqrdmulh v3.8h, v12.8h, v2.8h
    mul v12.8h, v12.8h, v1.8h
    mls v12.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x3, #128]
    sqrdmulh v3.8h, v14.8h, v2.8h
    mul v14.8h, v14.8h, v1.8h
    mls v14.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x3, #192]
    sqrdmulh v3.8h, v4.8h, v2.8h
    mul v4.8h, v4.8h, v1.8h
    mls v4.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x3, #256]
    sqrdmulh v3.8h, v6.8h, v2.8h
    mul v6.8h, v6.8h, v1.8h
    mls v6.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x3, #320]
    sqrdmulh v3.8h, v8.8h, v2.8h
    mul v8.8h, v8.8h, v1.8h
    mls v8.8h, v3.8h, v0.h[0]

    zip1 v22.2d, v4.2d, v10.2d
    zip2 v23.2d, v4.2d, v10.2d
    zip1 v26.2d, v6.2d, v12.2d
    zip2 v27.2d, v6.2d, v12.2d
    zip1 v30.2d, v8.2d, v14.2d
    zip2 v31.2d, v8.2d, v14.2d

    // Type A slot0: a=Z0e, b=Z4e, c=Z2e.
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
    str q9, [x4, #0]
    str q10, [x5, #0]
    str q11, [x6, #0]

    // Type A slot1: a=Z2o, b=Z0o, c=Z4o.
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
    str q9, [x4, #16]
    str q10, [x5, #16]
    str q11, [x6, #16]
slothy_end_ntt_phase123_u01_type_a:

slothy_start_ntt_phase123_u01_type_b:
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

    ldp q1, q2, [x3, #0]
    sqrdmulh v3.8h, v10.8h, v2.8h
    mul v10.8h, v10.8h, v1.8h
    mls v10.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x3, #64]
    sqrdmulh v3.8h, v12.8h, v2.8h
    mul v12.8h, v12.8h, v1.8h
    mls v12.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x3, #128]
    sqrdmulh v3.8h, v14.8h, v2.8h
    mul v14.8h, v14.8h, v1.8h
    mls v14.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x3, #192]
    sqrdmulh v3.8h, v4.8h, v2.8h
    mul v4.8h, v4.8h, v1.8h
    mls v4.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x3, #256]
    sqrdmulh v3.8h, v6.8h, v2.8h
    mul v6.8h, v6.8h, v1.8h
    mls v6.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x3, #320]
    sqrdmulh v3.8h, v8.8h, v2.8h
    mul v8.8h, v8.8h, v1.8h
    mls v8.8h, v3.8h, v0.h[0]

    zip1 v22.2d, v4.2d, v10.2d
    zip2 v23.2d, v4.2d, v10.2d
    zip1 v26.2d, v6.2d, v12.2d
    zip2 v27.2d, v6.2d, v12.2d
    zip1 v30.2d, v8.2d, v14.2d
    zip2 v31.2d, v8.2d, v14.2d

    // Type B slot0: a=Z2e, b=Z0e, c=Z4e.
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
    str q9, [x4, #0]
    str q10, [x5, #0]
    str q11, [x6, #0]

    // Type B slot1: a=Z4o, b=Z2o, c=Z0o.
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
    str q9, [x4, #16]
    str q10, [x5, #16]
    str q11, [x6, #16]
slothy_end_ntt_phase123_u01_type_b:

slothy_start_ntt_phase123_u01_type_c:
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

    ldp q1, q2, [x3, #0]
    sqrdmulh v3.8h, v10.8h, v2.8h
    mul v10.8h, v10.8h, v1.8h
    mls v10.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x3, #64]
    sqrdmulh v3.8h, v12.8h, v2.8h
    mul v12.8h, v12.8h, v1.8h
    mls v12.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x3, #128]
    sqrdmulh v3.8h, v14.8h, v2.8h
    mul v14.8h, v14.8h, v1.8h
    mls v14.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x3, #192]
    sqrdmulh v3.8h, v4.8h, v2.8h
    mul v4.8h, v4.8h, v1.8h
    mls v4.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x3, #256]
    sqrdmulh v3.8h, v6.8h, v2.8h
    mul v6.8h, v6.8h, v1.8h
    mls v6.8h, v3.8h, v0.h[0]
    ldp q1, q2, [x3, #320]
    sqrdmulh v3.8h, v8.8h, v2.8h
    mul v8.8h, v8.8h, v1.8h
    mls v8.8h, v3.8h, v0.h[0]

    zip1 v22.2d, v4.2d, v10.2d
    zip2 v23.2d, v4.2d, v10.2d
    zip1 v26.2d, v6.2d, v12.2d
    zip2 v27.2d, v6.2d, v12.2d
    zip1 v30.2d, v8.2d, v14.2d
    zip2 v31.2d, v8.2d, v14.2d

    // Type C slot0: a=Z4e, b=Z2e, c=Z0e.
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
    str q9, [x4, #0]
    str q10, [x5, #0]
    str q11, [x6, #0]

    // Type C slot1: a=Z0o, b=Z4o, c=Z2o.
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
    str q9, [x4, #16]
    str q10, [x5, #16]
    str q11, [x6, #16]
slothy_end_ntt_phase123_u01_type_c:
