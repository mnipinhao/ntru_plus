/* Promoted scheduled pair+merge core; no spills and no lane ST3. */
#ifdef __APPLE__
#define pair_merge_full _pair_merge_full
#endif
.text
.global pair_merge_full
pair_merge_full:
pair_merge_full_slothy_start:
    ldr q14, [x1, #288]
    ldr q6, [x1, #336]
    ldr q4, [x1, #240]
    ldr q7, [x1, #192]
    ldr q9, [x1, #48]
    ldr q15, [x1, #384]
    ldr q3, [x2, #288]
    ldr q10, [x1, #144]
    ext v1.16B, v14.16B, v14.16B, #12
    ldr q14, [x1, #96]
    ext v6.16B, v6.16B, v6.16B, #14
    ext v4.16B, v4.16B, v4.16B, #10
    ext v7.16B, v7.16B, v7.16B, #8
    ext v16.16B, v9.16B, v9.16B, #2
    trn2 v19.8H, v15.8H, v6.8H
    trn1 v18.8H, v1.8H, v4.8H
    ext v10.16B, v10.16B, v10.16B, #6
    trn1 v11.8H, v15.8H, v6.8H
    ext v0.16B, v3.16B, v3.16B, #12
    ext v8.16B, v14.16B, v14.16B, #4
    trn1 v9.8H, v7.8H, v10.8H
    ldr q14, [x2, #48]
    trn2 v13.8H, v1.8H, v4.8H
    trn2 v3.4S, v11.4S, v18.4S
    trn1 v4.8H, v8.8H, v16.8H
    trn2 v16.8H, v8.8H, v16.8H
    trn2 v5.8H, v7.8H, v10.8H
    trn1 v8.4S, v19.4S, v13.4S
    trn2 v13.4S, v19.4S, v13.4S
    trn2 v19.4S, v9.4S, v4.4S
    trn1 v12.4S, v11.4S, v18.4S
    trn2 v18.4S, v5.4S, v16.4S
    trn1 v10.4S, v5.4S, v16.4S
    trn1 v16.2D, v3.2D, v19.2D
    trn2 v6.2D, v3.2D, v19.2D
    ldr q3, [x2, #336]
    trn1 v11.4S, v9.4S, v4.4S
    ldr q4, [x2, #192]
    ext v15.16B, v14.16B, v14.16B, #2
    ldr q14, [x2, #144]
    ldr q19, [x2, #240]
    trn1 v7.2D, v13.2D, v18.2D
    trn2 v18.2D, v13.2D, v18.2D
    ldr q13, [x2, #384]
    trn1 v5.2D, v12.2D, v11.2D
    mov w8, #9
    trn2 v12.2D, v12.2D, v11.2D
    ldr q2, [x1]
    trn1 v11.2D, v8.2D, v10.2D
    trn2 v8.2D, v8.2D, v10.2D
    ext v9.16B, v3.16B, v3.16B, #14
    ext v3.16B, v4.16B, v4.16B, #8
    mov w12, #3457
    ldr q4, [x2, #96]
    ext v10.16B, v19.16B, v19.16B, #10
    ext v19.16B, v14.16B, v14.16B, #6
    ldr q1, [x2]
    trn1 v14.8H, v13.8H, v9.8H
    trn2 v13.8H, v13.8H, v9.8H
    trn1 v17.8H, v0.8H, v10.8H
    trn2 v9.8H, v0.8H, v10.8H
    trn1 v10.8H, v3.8H, v19.8H
    trn2 v19.8H, v3.8H, v19.8H
    ext v4.16B, v4.16B, v4.16B, #4
    trn1 v0.4S, v14.4S, v17.4S
    trn2 v14.4S, v14.4S, v17.4S
    trn1 v3.8H, v4.8H, v15.8H
    trn2 v4.8H, v4.8H, v15.8H
    trn1 v15.4S, v13.4S, v9.4S
    trn2 v13.4S, v13.4S, v9.4S
    trn1 v17.4S, v10.4S, v3.4S
    trn2 v10.4S, v10.4S, v3.4S
    trn1 v9.4S, v19.4S, v4.4S
    trn2 v19.4S, v19.4S, v4.4S
    trn1 v4.2D, v0.2D, v17.2D
    trn2 v3.2D, v0.2D, v17.2D
    trn1 v17.2D, v15.2D, v9.2D
    trn1 v0.2D, v14.2D, v10.2D
    trn2 v15.2D, v15.2D, v9.2D
    trn2 v9.2D, v14.2D, v10.2D
    dup v14.8H, w8
    trn1 v10.2D, v13.2D, v19.2D
    trn2 v19.2D, v13.2D, v19.2D
    dup v13.8H, w12
    ldr q23, [x4, #0]
    orr v25.16B, v5.16B, v5.16B
    orr v20.16B, v4.16B, v4.16B
    add x5, x6, #0
    add x12, x5, #16
    ins v25.h[0], v2.h[0]
    ins v20.h[0], v1.h[0]
    ldr d24, [x12]
    tbl v30.16B, {v25.16B}, v23.16B
    tbl v25.16B, {v20.16B}, v23.16B
    ldr q23, [x5]
    ldr q20, [x9, #0]
    add x5, x7, #0
    ldr q21, [x5]
    add x5, x5, #16
    ldr d22, [x5]
    add x5, x0, #0
    tbl v29.16B, {v23.16B, v24.16B}, v20.16B
    sqrdmulh v20.8H, v30.8H, v14.8H
    mls v30.8H, v20.8H, v13.8H
    sqrdmulh v20.8H, v25.8H, v14.8H
    mls v25.8H, v20.8H, v13.8H
    sshr v20.8H, v30.8H, #15
    and v20.16B, v20.16B, v13.16B
    add v30.8H, v30.8H, v20.8H
    sshr v20.8H, v25.8H, #15
    xtn v26.8B, v30.8H
    and v20.16B, v20.16B, v13.16B
    add v25.8H, v25.8H, v20.8H
    ushr v20.8H, v30.8H, #8
    sli v20.8H, v25.8H, #4
    xtn v27.8B, v20.8H
    ushr v20.8H, v25.8H, #4
    xtn v28.8B, v20.8H
    ldr q20, [x9, #16]
    tbl v30.16B, {v21.16B, v22.16B}, v20.16B
    ldr q20, [x9, #32]
    tbl v25.16b, {v26.16b, v27.16b, v28.16b}, v20.16b
    orr v20.16B, v29.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #0]
    ldr q20, [x9, #48]
    tbl v29.16B, {v23.16B, v24.16B}, v20.16B
    ldr q20, [x9, #64]
    tbl v30.16B, {v21.16B, v22.16B}, v20.16B
    ldr q20, [x9, #80]
    tbl v25.16b, {v26.16b, v27.16b, v28.16b}, v20.16b
    orr v20.16B, v29.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #16]
    ldr q20, [x9, #96]
    tbl v29.16B, {v23.16B, v24.16B}, v20.16B
    ldr q20, [x9, #112]
    tbl v30.16B, {v21.16B, v22.16B}, v20.16B
    ldr q20, [x9, #128]
    tbl v25.16b, {v26.16b, v27.16b, v28.16b}, v20.16b
    orr v20.16B, v29.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #32]
    ldr q20, [x9, #144]
    tbl v29.16B, {v23.16B, v24.16B}, v20.16B
    ldr q20, [x9, #160]
    tbl v30.16B, {v21.16B, v22.16B}, v20.16B
    ldr q20, [x9, #176]
    tbl v25.16b, {v26.16b, v27.16b, v28.16b}, v20.16b
    ldr q20, [x9, #192]
    tbl v23.16B, {v23.16B, v24.16B}, v20.16B
    orr v20.16B, v29.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #48]
    ldr q20, [x9, #208]
    tbl v30.16B, {v21.16B, v22.16B}, v20.16B
    ldr q20, [x9, #224]
    tbl v25.16b, {v26.16b, v27.16b, v28.16b}, v20.16b
    orr v20.16B, v23.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str d20, [x5, #64]
    ldr q26, [x4, #16]
    ldr q27, [x3, #0]
    add x5, x6, #72
    add x12, x5, #16
    and v25.16B, v5.16B, v27.16B
    bic v20.16B, v11.16B, v27.16B
    ldr d5, [x12]
    orr v20.16B, v25.16B, v20.16B
    ins v20.h[1], v2.h[1]
    tbl v25.16B, {v20.16B}, v26.16B
    sqrdmulh v20.8H, v25.8H, v14.8H
    mls v25.8H, v20.8H, v13.8H
    sshr v20.8H, v25.8H, #15
    and v20.16B, v20.16B, v13.16B
    add v30.8H, v25.8H, v20.8H
    and v25.16B, v4.16B, v27.16B
    ldr q4, [x5]
    add x5, x7, #72
    bic v20.16B, v17.16B, v27.16B
    ldr q28, [x5]
    add x5, x5, #16
    xtn v21.8B, v30.8H
    ldr d29, [x5]
    add x5, x0, #216
    orr v20.16B, v25.16B, v20.16B
    ins v20.h[1], v1.h[1]
    tbl v25.16B, {v20.16B}, v26.16B
    sqrdmulh v20.8H, v25.8H, v14.8H
    mls v25.8H, v20.8H, v13.8H
    ldr q20, [x9, #0]
    tbl v27.16B, {v4.16B, v5.16B}, v20.16B
    sshr v20.8H, v25.8H, #15
    and v20.16B, v20.16B, v13.16B
    add v25.8H, v25.8H, v20.8H
    ushr v20.8H, v30.8H, #8
    sli v20.8H, v25.8H, #4
    xtn v22.8B, v20.8H
    ushr v20.8H, v25.8H, #4
    xtn v23.8B, v20.8H
    ldr q20, [x9, #16]
    tbl v30.16B, {v28.16B, v29.16B}, v20.16B
    ldr q20, [x9, #32]
    tbl v25.16b, {v21.16b, v22.16b, v23.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #0]
    ldr q20, [x9, #48]
    tbl v27.16B, {v4.16B, v5.16B}, v20.16B
    ldr q20, [x9, #64]
    tbl v30.16B, {v28.16B, v29.16B}, v20.16B
    ldr q20, [x9, #80]
    tbl v25.16b, {v21.16b, v22.16b, v23.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #16]
    ldr q20, [x9, #96]
    tbl v27.16B, {v4.16B, v5.16B}, v20.16B
    ldr q20, [x9, #112]
    tbl v30.16B, {v28.16B, v29.16B}, v20.16B
    ldr q20, [x9, #128]
    tbl v25.16b, {v21.16b, v22.16b, v23.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #32]
    ldr q20, [x9, #144]
    tbl v27.16B, {v4.16B, v5.16B}, v20.16B
    ldr q20, [x9, #160]
    tbl v30.16B, {v28.16B, v29.16B}, v20.16B
    ldr q20, [x9, #176]
    tbl v25.16b, {v21.16b, v22.16b, v23.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #48]
    ldr q20, [x9, #192]
    tbl v27.16B, {v4.16B, v5.16B}, v20.16B
    ldr q20, [x9, #208]
    tbl v30.16B, {v28.16B, v29.16B}, v20.16B
    ldr q20, [x9, #224]
    tbl v25.16b, {v21.16b, v22.16b, v23.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str d20, [x5, #64]
    ldr q5, [x4, #32]
    ldr q27, [x3, #16]
    add x5, x6, #144
    ldr q4, [x5]
    add x12, x5, #16
    add x5, x7, #144
    ldr q28, [x5]
    add x5, x5, #16
    ldr d29, [x5]
    add x5, x0, #432
    and v25.16B, v11.16B, v27.16B
    bic v20.16B, v16.16B, v27.16B
    orr v20.16B, v25.16B, v20.16B
    ins v20.h[2], v2.h[2]
    tbl v25.16B, {v20.16B}, v5.16B
    sqrdmulh v20.8H, v25.8H, v14.8H
    mls v25.8H, v20.8H, v13.8H
    sshr v20.8H, v25.8H, #15
    and v20.16B, v20.16B, v13.16B
    add v30.8H, v25.8H, v20.8H
    and v25.16B, v17.16B, v27.16B
    bic v20.16B, v0.16B, v27.16B
    xtn v21.8B, v30.8H
    orr v20.16B, v25.16B, v20.16B
    ins v20.h[2], v1.h[2]
    tbl v25.16B, {v20.16B}, v5.16B
    ldr d5, [x12]
    sqrdmulh v20.8H, v25.8H, v14.8H
    mls v25.8H, v20.8H, v13.8H
    ldr q20, [x9, #0]
    tbl v27.16B, {v4.16B, v5.16B}, v20.16B
    sshr v20.8H, v25.8H, #15
    and v20.16B, v20.16B, v13.16B
    add v25.8H, v25.8H, v20.8H
    ushr v20.8H, v30.8H, #8
    sli v20.8H, v25.8H, #4
    xtn v22.8B, v20.8H
    ushr v20.8H, v25.8H, #4
    xtn v23.8B, v20.8H
    ldr q20, [x9, #16]
    tbl v30.16B, {v28.16B, v29.16B}, v20.16B
    ldr q20, [x9, #32]
    tbl v25.16b, {v21.16b, v22.16b, v23.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #0]
    ldr q20, [x9, #48]
    tbl v27.16B, {v4.16B, v5.16B}, v20.16B
    ldr q20, [x9, #64]
    tbl v30.16B, {v28.16B, v29.16B}, v20.16B
    ldr q20, [x9, #80]
    tbl v25.16b, {v21.16b, v22.16b, v23.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #16]
    ldr q20, [x9, #96]
    tbl v27.16B, {v4.16B, v5.16B}, v20.16B
    ldr q20, [x9, #112]
    tbl v30.16B, {v28.16B, v29.16B}, v20.16B
    ldr q20, [x9, #128]
    tbl v25.16b, {v21.16b, v22.16b, v23.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #32]
    ldr q20, [x9, #144]
    tbl v27.16B, {v4.16B, v5.16B}, v20.16B
    ldr q20, [x9, #160]
    tbl v30.16B, {v28.16B, v29.16B}, v20.16B
    ldr q20, [x9, #176]
    tbl v25.16b, {v21.16b, v22.16b, v23.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #48]
    ldr q20, [x9, #192]
    tbl v27.16B, {v4.16B, v5.16B}, v20.16B
    ldr q20, [x9, #208]
    tbl v30.16B, {v28.16B, v29.16B}, v20.16B
    ldr q20, [x9, #224]
    tbl v25.16b, {v21.16b, v22.16b, v23.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str d20, [x5, #64]
    ldr q27, [x4, #48]
    ldr q26, [x3, #32]
    add x5, x6, #24
    ldr q28, [x5]
    add x5, x5, #16
    ldr d29, [x5]
    add x5, x7, #24
    and v25.16B, v16.16B, v26.16B
    bic v20.16B, v7.16B, v26.16B
    ldr q16, [x5]
    add x5, x5, #16
    ldr d17, [x5]
    add x5, x0, #72
    orr v20.16B, v25.16B, v20.16B
    ins v20.h[3], v2.h[3]
    tbl v25.16B, {v20.16B}, v27.16B
    sqrdmulh v20.8H, v25.8H, v14.8H
    mls v25.8H, v20.8H, v13.8H
    sshr v20.8H, v25.8H, #15
    and v20.16B, v20.16B, v13.16B
    add v30.8H, v25.8H, v20.8H
    and v25.16B, v0.16B, v26.16B
    bic v20.16B, v10.16B, v26.16B
    xtn v21.8B, v30.8H
    orr v20.16B, v25.16B, v20.16B
    ins v20.h[3], v1.h[3]
    tbl v25.16B, {v20.16B}, v27.16B
    sqrdmulh v20.8H, v25.8H, v14.8H
    mls v25.8H, v20.8H, v13.8H
    ldr q20, [x9, #0]
    tbl v27.16B, {v28.16B, v29.16B}, v20.16B
    sshr v20.8H, v25.8H, #15
    and v20.16B, v20.16B, v13.16B
    add v25.8H, v25.8H, v20.8H
    ushr v20.8H, v30.8H, #8
    sli v20.8H, v25.8H, #4
    xtn v22.8B, v20.8H
    ushr v20.8H, v25.8H, #4
    xtn v23.8B, v20.8H
    ldr q20, [x9, #16]
    tbl v30.16B, {v16.16B, v17.16B}, v20.16B
    ldr q20, [x9, #32]
    tbl v25.16b, {v21.16b, v22.16b, v23.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #0]
    ldr q20, [x9, #48]
    tbl v27.16B, {v28.16B, v29.16B}, v20.16B
    ldr q20, [x9, #64]
    tbl v30.16B, {v16.16B, v17.16B}, v20.16B
    ldr q20, [x9, #80]
    tbl v25.16b, {v21.16b, v22.16b, v23.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #16]
    ldr q20, [x9, #96]
    tbl v27.16B, {v28.16B, v29.16B}, v20.16B
    ldr q20, [x9, #112]
    tbl v30.16B, {v16.16B, v17.16B}, v20.16B
    ldr q20, [x9, #128]
    tbl v25.16b, {v21.16b, v22.16b, v23.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #32]
    ldr q20, [x9, #144]
    tbl v27.16B, {v28.16B, v29.16B}, v20.16B
    ldr q20, [x9, #160]
    tbl v30.16B, {v16.16B, v17.16B}, v20.16B
    ldr q20, [x9, #176]
    tbl v25.16b, {v21.16b, v22.16b, v23.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #48]
    ldr q20, [x9, #192]
    tbl v27.16B, {v28.16B, v29.16B}, v20.16B
    ldr q20, [x9, #208]
    tbl v30.16B, {v16.16B, v17.16B}, v20.16B
    ldr q20, [x9, #224]
    tbl v25.16b, {v21.16b, v22.16b, v23.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str d20, [x5, #64]
    add x5, x7, #96
    ldr q27, [x3, #48]
    ldr q23, [x4, #64]
    ldr q16, [x5]
    add x5, x5, #16
    ldr d17, [x5]
    add x5, x6, #96
    add x12, x5, #16
    ldr q28, [x5]
    add x5, x0, #288
    ldr d29, [x12]
    and v25.16B, v7.16B, v27.16B
    bic v20.16B, v12.16B, v27.16B
    orr v7.16B, v25.16B, v20.16B
    ins v7.h[4], v2.h[4]
    tbl v25.16B, {v7.16B}, v23.16B
    sqrdmulh v20.8H, v25.8H, v14.8H
    mls v25.8H, v20.8H, v13.8H
    sshr v20.8H, v25.8H, #15
    and v20.16B, v20.16B, v13.16B
    add v30.8H, v25.8H, v20.8H
    and v25.16B, v10.16B, v27.16B
    bic v20.16B, v3.16B, v27.16B
    orr v20.16B, v25.16B, v20.16B
    ins v20.h[4], v1.h[4]
    tbl v25.16B, {v20.16B}, v23.16B
    sqrdmulh v20.8H, v25.8H, v14.8H
    mls v25.8H, v20.8H, v13.8H
    ldr q20, [x9, #0]
    tbl v27.16B, {v28.16B, v29.16B}, v20.16B
    sshr v20.8H, v25.8H, #15
    and v20.16B, v20.16B, v13.16B
    xtn v21.8B, v30.8H
    add v25.8H, v25.8H, v20.8H
    ushr v20.8H, v30.8H, #8
    sli v20.8H, v25.8H, #4
    xtn v22.8B, v20.8H
    ldr q20, [x9, #16]
    tbl v30.16B, {v16.16B, v17.16B}, v20.16B
    ushr v20.8H, v25.8H, #4
    xtn v23.8B, v20.8H
    ldr q20, [x9, #32]
    tbl v25.16b, {v21.16b, v22.16b, v23.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #0]
    ldr q20, [x9, #48]
    tbl v27.16B, {v28.16B, v29.16B}, v20.16B
    ldr q20, [x9, #80]
    tbl v25.16b, {v21.16b, v22.16b, v23.16b}, v20.16b
    ldr q20, [x9, #64]
    tbl v30.16B, {v16.16B, v17.16B}, v20.16B
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #16]
    ldr q20, [x9, #96]
    tbl v27.16B, {v28.16B, v29.16B}, v20.16B
    ldr q20, [x9, #112]
    tbl v30.16B, {v16.16B, v17.16B}, v20.16B
    ldr q20, [x9, #128]
    tbl v25.16b, {v21.16b, v22.16b, v23.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #32]
    ldr q20, [x9, #144]
    tbl v27.16B, {v28.16B, v29.16B}, v20.16B
    ldr q20, [x9, #160]
    tbl v30.16B, {v16.16B, v17.16B}, v20.16B
    ldr q20, [x9, #176]
    tbl v25.16b, {v21.16b, v22.16b, v23.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #48]
    ldr q20, [x9, #192]
    tbl v27.16B, {v28.16B, v29.16B}, v20.16B
    ldr q20, [x9, #208]
    tbl v30.16B, {v16.16B, v17.16B}, v20.16B
    ldr q20, [x9, #224]
    tbl v25.16b, {v21.16b, v22.16b, v23.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str d20, [x5, #64]
    ldr q27, [x3, #64]
    add x5, x6, #168
    ldr q11, [x5]
    add x12, x5, #16
    add x5, x7, #168
    ldr q26, [x4, #80]
    ldr q23, [x5]
    add x5, x5, #16
    ldr d24, [x5]
    add x5, x0, #504
    bic v20.16B, v8.16B, v27.16B
    and v25.16B, v12.16B, v27.16B
    orr v12.16B, v25.16B, v20.16B
    ins v12.h[5], v2.h[5]
    tbl v25.16B, {v12.16B}, v26.16B
    ldr d12, [x12]
    sqrdmulh v20.8H, v25.8H, v14.8H
    mls v25.8H, v20.8H, v13.8H
    sshr v20.8H, v25.8H, #15
    and v20.16B, v20.16B, v13.16B
    add v30.8H, v25.8H, v20.8H
    and v25.16B, v3.16B, v27.16B
    bic v20.16B, v15.16B, v27.16B
    xtn v3.8B, v30.8H
    orr v20.16B, v25.16B, v20.16B
    ins v20.h[5], v1.h[5]
    tbl v25.16B, {v20.16B}, v26.16B
    sqrdmulh v20.8H, v25.8H, v14.8H
    mls v25.8H, v20.8H, v13.8H
    ldr q20, [x9, #0]
    tbl v27.16B, {v11.16B, v12.16B}, v20.16B
    sshr v20.8H, v25.8H, #15
    and v20.16B, v20.16B, v13.16B
    add v25.8H, v25.8H, v20.8H
    ushr v20.8H, v30.8H, #8
    sli v20.8H, v25.8H, #4
    xtn v4.8B, v20.8H
    ushr v20.8H, v25.8H, #4
    xtn v5.8B, v20.8H
    ldr q20, [x9, #16]
    tbl v30.16B, {v23.16B, v24.16B}, v20.16B
    ldr q20, [x9, #32]
    tbl v25.16b, {v3.16b, v4.16b, v5.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #0]
    ldr q20, [x9, #80]
    tbl v25.16b, {v3.16b, v4.16b, v5.16b}, v20.16b
    ldr q20, [x9, #64]
    tbl v30.16B, {v23.16B, v24.16B}, v20.16B
    ldr q20, [x9, #48]
    tbl v27.16B, {v11.16B, v12.16B}, v20.16B
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #16]
    ldr q20, [x9, #112]
    tbl v30.16B, {v23.16B, v24.16B}, v20.16B
    ldr q20, [x9, #96]
    tbl v27.16B, {v11.16B, v12.16B}, v20.16B
    ldr q20, [x9, #128]
    tbl v25.16b, {v3.16b, v4.16b, v5.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #32]
    ldr q20, [x9, #176]
    tbl v25.16b, {v3.16b, v4.16b, v5.16b}, v20.16b
    ldr q20, [x9, #144]
    tbl v27.16B, {v11.16B, v12.16B}, v20.16B
    ldr q20, [x9, #160]
    tbl v30.16B, {v23.16B, v24.16B}, v20.16B
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #48]
    ldr q20, [x9, #192]
    tbl v27.16B, {v11.16B, v12.16B}, v20.16B
    ldr q20, [x9, #208]
    tbl v30.16B, {v23.16B, v24.16B}, v20.16B
    ldr q20, [x9, #224]
    tbl v25.16b, {v3.16b, v4.16b, v5.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str d20, [x5, #64]
    ldr q26, [x4, #96]
    add x5, x6, #48
    ldr q27, [x3, #80]
    ldr q11, [x5]
    add x5, x5, #16
    ldr d12, [x5]
    add x5, x7, #48
    ldr q23, [x5]
    add x5, x5, #16
    ldr d24, [x5]
    bic v20.16B, v6.16B, v27.16B
    and v25.16B, v8.16B, v27.16B
    add x5, x0, #144
    orr v8.16B, v25.16B, v20.16B
    ins v8.h[6], v2.h[6]
    tbl v25.16B, {v8.16B}, v26.16B
    sqrdmulh v20.8H, v25.8H, v14.8H
    mls v25.8H, v20.8H, v13.8H
    sshr v20.8H, v25.8H, #15
    and v20.16B, v20.16B, v13.16B
    add v30.8H, v25.8H, v20.8H
    and v25.16B, v15.16B, v27.16B
    bic v20.16B, v9.16B, v27.16B
    orr v20.16B, v25.16B, v20.16B
    ins v20.h[6], v1.h[6]
    tbl v25.16B, {v20.16B}, v26.16B
    sqrdmulh v20.8H, v25.8H, v14.8H
    mls v25.8H, v20.8H, v13.8H
    ldr q20, [x9, #96]
    tbl v27.16B, {v11.16B, v12.16B}, v20.16B
    sshr v20.8H, v25.8H, #15
    and v20.16B, v20.16B, v13.16B
    add v25.8H, v25.8H, v20.8H
    ushr v20.8H, v30.8H, #8
    sli v20.8H, v25.8H, #4
    xtn v4.8B, v20.8H
    ldr q20, [x9, #112]
    xtn v3.8B, v30.8H
    tbl v30.16B, {v23.16B, v24.16B}, v20.16B
    ushr v20.8H, v25.8H, #4
    xtn v5.8B, v20.8H
    ldr q20, [x9, #128]
    tbl v25.16b, {v3.16b, v4.16b, v5.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #32]
    ldr q20, [x9, #144]
    tbl v27.16B, {v11.16B, v12.16B}, v20.16B
    ldr q20, [x9, #160]
    tbl v30.16B, {v23.16B, v24.16B}, v20.16B
    ldr q20, [x9, #176]
    tbl v25.16b, {v3.16b, v4.16b, v5.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #48]
    ldr q20, [x9, #48]
    tbl v27.16B, {v11.16B, v12.16B}, v20.16B
    ldr q20, [x9, #64]
    tbl v30.16B, {v23.16B, v24.16B}, v20.16B
    ldr q20, [x9, #80]
    tbl v25.16b, {v3.16b, v4.16b, v5.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #16]
    ldr q20, [x9, #0]
    tbl v27.16B, {v11.16B, v12.16B}, v20.16B
    ldr q20, [x9, #16]
    tbl v30.16B, {v23.16B, v24.16B}, v20.16B
    ldr q20, [x9, #32]
    tbl v25.16b, {v3.16b, v4.16b, v5.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #0]
    ldr q20, [x9, #192]
    tbl v27.16B, {v11.16B, v12.16B}, v20.16B
    ldr q20, [x9, #208]
    tbl v30.16B, {v23.16B, v24.16B}, v20.16B
    ldr q20, [x9, #224]
    tbl v25.16b, {v3.16b, v4.16b, v5.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str d20, [x5, #64]
    orr v6.16B, v6.16B, v6.16B
    ldr q27, [x4, #112]
    add x5, x6, #120
    ldr q23, [x5]
    add x12, x5, #16
    ins v6.h[7], v2.h[7]
    ldr d24, [x12]
    add x5, x7, #120
    ldr q5, [x5]
    add x5, x5, #16
    tbl v25.16B, {v6.16B}, v27.16B
    ldr d6, [x5]
    sqrdmulh v20.8H, v25.8H, v14.8H
    mls v25.8H, v20.8H, v13.8H
    sshr v20.8H, v25.8H, #15
    and v20.16B, v20.16B, v13.16B
    add v30.8H, v25.8H, v20.8H
    orr v20.16B, v9.16B, v9.16B
    ins v20.h[7], v1.h[7]
    add x5, x0, #360
    tbl v25.16B, {v20.16B}, v27.16B
    sqrdmulh v20.8H, v25.8H, v14.8H
    mls v25.8H, v20.8H, v13.8H
    ldr q20, [x9, #144]
    tbl v27.16B, {v23.16B, v24.16B}, v20.16B
    sshr v20.8H, v25.8H, #15
    and v20.16B, v20.16B, v13.16B
    add v25.8H, v25.8H, v20.8H
    ushr v20.8H, v30.8H, #8
    sli v20.8H, v25.8H, #4
    xtn v8.8B, v30.8H
    xtn v9.8B, v20.8H
    ldr q20, [x9, #160]
    tbl v30.16B, {v5.16B, v6.16B}, v20.16B
    ushr v20.8H, v25.8H, #4
    xtn v10.8B, v20.8H
    ldr q20, [x9, #176]
    tbl v25.16b, {v8.16b, v9.16b, v10.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #48]
    ldr q20, [x9, #16]
    tbl v30.16B, {v5.16B, v6.16B}, v20.16B
    ldr q20, [x9, #32]
    tbl v25.16b, {v8.16b, v9.16b, v10.16b}, v20.16b
    ldr q20, [x9, #0]
    tbl v27.16B, {v23.16B, v24.16B}, v20.16B
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #0]
    ldr q20, [x9, #64]
    tbl v30.16B, {v5.16B, v6.16B}, v20.16B
    ldr q20, [x9, #48]
    tbl v27.16B, {v23.16B, v24.16B}, v20.16B
    ldr q20, [x9, #80]
    tbl v25.16b, {v8.16b, v9.16b, v10.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #16]
    ldr q20, [x9, #224]
    tbl v25.16b, {v8.16b, v9.16b, v10.16b}, v20.16b
    ldr q20, [x9, #208]
    tbl v30.16B, {v5.16B, v6.16B}, v20.16B
    ldr q20, [x9, #192]
    tbl v27.16B, {v23.16B, v24.16B}, v20.16B
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str d20, [x5, #64]
    ldr q20, [x9, #128]
    tbl v25.16b, {v8.16b, v9.16b, v10.16b}, v20.16b
    ldr q20, [x9, #96]
    tbl v27.16B, {v23.16B, v24.16B}, v20.16B
    ldr q20, [x9, #112]
    tbl v30.16B, {v5.16B, v6.16B}, v20.16B
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #32]
    ldr q8, [x4, #128]
    orr v26.16B, v18.16B, v18.16B
    add x8, x7, #192
    ldr q24, [x9, #144]
    ldr q2, [x9, #96]
    add x16, x0, #576
    add x5, x6, #192
    add x12, x5, #16
    orr v7.16B, v19.16B, v19.16B
    ldr q15, [x5]
    ldr d16, [x12]
    ldr q11, [x8]
    ldr q17, [x9, #16]
    tbl v30.16B, {v26.16B}, v8.16B
    ldr q26, [x9, #80]
    ldr q5, [x9, #48]
    add x12, x8, #16
    tbl v0.16B, {v7.16B}, v8.16B
    ldr q7, [x9, #64]
    ldr d12, [x12]
    sqrdmulh v20.8H, v30.8H, v14.8H
    ldr q6, [x9, #160]
    sqrdmulh v22.8H, v0.8H, v14.8H
    tbl v1.16B, {v15.16B, v16.16B}, v24.16B
    ldr q14, [x9, #32]
    tbl v24.16B, {v11.16B, v12.16B}, v7.16B
    mls v30.8H, v20.8H, v13.8H
    ldr q7, [x9, #112]
    tbl v25.16B, {v15.16B, v16.16B}, v5.16B
    tbl v28.16B, {v11.16B, v12.16B}, v6.16B
    mls v0.8H, v22.8H, v13.8H
    sshr v3.8H, v30.8H, #15
    tbl v6.16B, {v11.16B, v12.16B}, v7.16B
    sshr v5.8H, v0.8H, #15
    and v7.16B, v3.16B, v13.16B
    ldr q22, [x9, #192]
    tbl v3.16B, {v15.16B, v16.16B}, v2.16B
    add v31.8H, v30.8H, v7.8H
    and v2.16B, v5.16B, v13.16B
    orr v13.16B, v25.16B, v24.16B
    orr v18.16B, v3.16B, v6.16B
    add v29.8H, v0.8H, v2.8H
    ldr q3, [x9, #208]
    ushr v10.8H, v31.8H, #8
    ushr v21.8H, v29.8H, #4
    sli v10.8H, v29.8H, #4
    xtn v19.8B, v31.8H
    xtn v21.8B, v21.8H
    ldr q29, [x9, #128]
    tbl v25.16B, {v11.16B, v12.16B}, v3.16B
    xtn v20.8B, v10.8H
    orr v30.16B, v1.16B, v28.16B
    tbl v1.16B, {v15.16B, v16.16B}, v22.16B
    tbl v22.16b, {v19.16b, v20.16b, v21.16b}, v14.16b
    ldr q14, [x9, #0]
    tbl v4.16b, {v19.16b, v20.16b, v21.16b}, v26.16b
    tbl v26.16B, {v11.16B, v12.16B}, v17.16B
    ldr q12, [x9, #224]
    orr v1.16B, v1.16B, v25.16B
    orr v25.16B, v13.16B, v4.16B
    tbl v27.16b, {v19.16b, v20.16b, v21.16b}, v29.16b
    ldr q13, [x9, #176]
    tbl v4.16B, {v15.16B, v16.16B}, v14.16B
    tbl v15.16b, {v19.16b, v20.16b, v21.16b}, v12.16b
    str q25, [x16, #16]
    orr v8.16B, v4.16B, v26.16B
    tbl v14.16b, {v19.16b, v20.16b, v21.16b}, v13.16b
    orr v18.16B, v18.16B, v27.16B
    orr v31.16B, v8.16B, v22.16B
    orr v24.16B, v1.16B, v15.16B
    str q18, [x16, #32]
    orr v9.16B, v30.16B, v14.16B
    str d24, [x16, #64]
    str q31, [x16, #0]
    str q9, [x16, #48]
pair_merge_full_slothy_end:
    ret
