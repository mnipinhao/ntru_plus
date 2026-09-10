.text
.global pair_merge_full
pair_merge_full:
pair_merge_full_slothy_start:
    ldr q15, [x1, #384]
    ldr q6, [x1, #336]
    ext v6.16B, v6.16B, v6.16B, #14
    ldr q14, [x1, #288]
    ext v1.16B, v14.16B, v14.16B, #12
    ldr q4, [x1, #240]
    ext v4.16B, v4.16B, v4.16B, #10
    ldr q7, [x1, #192]
    ext v7.16B, v7.16B, v7.16B, #8
    ldr q10, [x1, #144]
    ext v10.16B, v10.16B, v10.16B, #6
    ldr q14, [x1, #96]
    ext v8.16B, v14.16B, v14.16B, #4
    ldr q9, [x1, #48]
    ext v16.16B, v9.16B, v9.16B, #2
    ldr q2, [x1]
    trn1 v11.8H, v15.8H, v6.8H
    trn2 v19.8H, v15.8H, v6.8H
    trn1 v18.8H, v1.8H, v4.8H
    trn2 v13.8H, v1.8H, v4.8H
    trn1 v9.8H, v7.8H, v10.8H
    trn2 v5.8H, v7.8H, v10.8H
    trn1 v4.8H, v8.8H, v16.8H
    trn2 v16.8H, v8.8H, v16.8H
    trn1 v12.4S, v11.4S, v18.4S
    trn1 v8.4S, v19.4S, v13.4S
    trn2 v3.4S, v11.4S, v18.4S
    trn2 v13.4S, v19.4S, v13.4S
    trn1 v11.4S, v9.4S, v4.4S
    trn1 v10.4S, v5.4S, v16.4S
    trn2 v19.4S, v9.4S, v4.4S
    trn2 v18.4S, v5.4S, v16.4S
    trn1 v5.2D, v12.2D, v11.2D
    trn2 v12.2D, v12.2D, v11.2D
    trn1 v11.2D, v8.2D, v10.2D
    trn2 v8.2D, v8.2D, v10.2D
    trn1 v16.2D, v3.2D, v19.2D
    trn2 v6.2D, v3.2D, v19.2D
    trn1 v7.2D, v13.2D, v18.2D
    trn2 v18.2D, v13.2D, v18.2D
    ldr q13, [x2, #384]
    ldr q3, [x2, #336]
    ext v9.16B, v3.16B, v3.16B, #14
    ldr q3, [x2, #288]
    ext v0.16B, v3.16B, v3.16B, #12
    ldr q19, [x2, #240]
    ext v10.16B, v19.16B, v19.16B, #10
    ldr q4, [x2, #192]
    ext v3.16B, v4.16B, v4.16B, #8
    ldr q14, [x2, #144]
    ext v19.16B, v14.16B, v14.16B, #6
    ldr q4, [x2, #96]
    ext v4.16B, v4.16B, v4.16B, #4
    ldr q14, [x2, #48]
    ext v15.16B, v14.16B, v14.16B, #2
    ldr q1, [x2]
    trn1 v14.8H, v13.8H, v9.8H
    trn2 v13.8H, v13.8H, v9.8H
    trn1 v17.8H, v0.8H, v10.8H
    trn2 v9.8H, v0.8H, v10.8H
    trn1 v10.8H, v3.8H, v19.8H
    trn2 v19.8H, v3.8H, v19.8H
    trn1 v3.8H, v4.8H, v15.8H
    trn2 v4.8H, v4.8H, v15.8H
    trn1 v0.4S, v14.4S, v17.4S
    trn1 v15.4S, v13.4S, v9.4S
    trn2 v14.4S, v14.4S, v17.4S
    trn2 v13.4S, v13.4S, v9.4S
    trn1 v17.4S, v10.4S, v3.4S
    trn1 v9.4S, v19.4S, v4.4S
    trn2 v10.4S, v10.4S, v3.4S
    trn2 v19.4S, v19.4S, v4.4S
    trn1 v4.2D, v0.2D, v17.2D
    trn2 v3.2D, v0.2D, v17.2D
    trn1 v17.2D, v15.2D, v9.2D
    trn2 v15.2D, v15.2D, v9.2D
    trn1 v0.2D, v14.2D, v10.2D
    trn2 v9.2D, v14.2D, v10.2D
    trn1 v10.2D, v13.2D, v19.2D
    trn2 v19.2D, v13.2D, v19.2D
    mov w12, #3457
    dup v13.8H, w12
    mov w8, #9
    dup v14.8H, w8
    ldr q23, [x4, #0]
    orr v25.16B, v5.16B, v5.16B
    ins v25.h[0], v2.h[0]
    tbl v30.16B, {v25.16B}, v23.16B
    sqrdmulh v20.8H, v30.8H, v14.8H
    mls v30.8H, v20.8H, v13.8H
    sshr v20.8H, v30.8H, #15
    and v20.16B, v20.16B, v13.16B
    add v30.8H, v30.8H, v20.8H
    orr v20.16B, v4.16B, v4.16B
    ins v20.h[0], v1.h[0]
    tbl v25.16B, {v20.16B}, v23.16B
    sqrdmulh v20.8H, v25.8H, v14.8H
    mls v25.8H, v20.8H, v13.8H
    sshr v20.8H, v25.8H, #15
    and v20.16B, v20.16B, v13.16B
    add v25.8H, v25.8H, v20.8H
    xtn v26.8B, v30.8H
    ushr v20.8H, v30.8H, #8
    sli v20.8H, v25.8H, #4
    xtn v27.8B, v20.8H
    ushr v20.8H, v25.8H, #4
    xtn v28.8B, v20.8H
    add x5, x6, #0
    ldr q23, [x5]
    add x12, x5, #16
    ldr d24, [x12]
    add x5, x7, #0
    ldr q21, [x5]
    add x5, x5, #16
    ldr d22, [x5]
    add x5, x0, #0
    ldr q20, [x9, #0]
    tbl v29.16B, {v23.16B, v24.16B}, v20.16B
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
    orr v20.16B, v29.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #48]
    ldr q20, [x9, #192]
    tbl v23.16B, {v23.16B, v24.16B}, v20.16B
    ldr q20, [x9, #208]
    tbl v30.16B, {v21.16B, v22.16B}, v20.16B
    ldr q20, [x9, #224]
    tbl v25.16b, {v26.16b, v27.16b, v28.16b}, v20.16b
    orr v20.16B, v23.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str d20, [x5, #64]
    ldr q26, [x4, #16]
    ldr q27, [x3, #0]
    and v25.16B, v5.16B, v27.16B
    bic v20.16B, v11.16B, v27.16B
    orr v20.16B, v25.16B, v20.16B
    ins v20.h[1], v2.h[1]
    tbl v25.16B, {v20.16B}, v26.16B
    sqrdmulh v20.8H, v25.8H, v14.8H
    mls v25.8H, v20.8H, v13.8H
    sshr v20.8H, v25.8H, #15
    and v20.16B, v20.16B, v13.16B
    add v30.8H, v25.8H, v20.8H
    and v25.16B, v4.16B, v27.16B
    bic v20.16B, v17.16B, v27.16B
    orr v20.16B, v25.16B, v20.16B
    ins v20.h[1], v1.h[1]
    tbl v25.16B, {v20.16B}, v26.16B
    sqrdmulh v20.8H, v25.8H, v14.8H
    mls v25.8H, v20.8H, v13.8H
    sshr v20.8H, v25.8H, #15
    and v20.16B, v20.16B, v13.16B
    add v25.8H, v25.8H, v20.8H
    xtn v21.8B, v30.8H
    ushr v20.8H, v30.8H, #8
    sli v20.8H, v25.8H, #4
    xtn v22.8B, v20.8H
    ushr v20.8H, v25.8H, #4
    xtn v23.8B, v20.8H
    add x5, x6, #72
    ldr q4, [x5]
    add x12, x5, #16
    ldr d5, [x12]
    add x5, x7, #72
    ldr q28, [x5]
    add x5, x5, #16
    ldr d29, [x5]
    add x5, x0, #216
    ldr q20, [x9, #0]
    tbl v27.16B, {v4.16B, v5.16B}, v20.16B
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
    orr v20.16B, v25.16B, v20.16B
    ins v20.h[2], v1.h[2]
    tbl v25.16B, {v20.16B}, v5.16B
    sqrdmulh v20.8H, v25.8H, v14.8H
    mls v25.8H, v20.8H, v13.8H
    sshr v20.8H, v25.8H, #15
    and v20.16B, v20.16B, v13.16B
    add v25.8H, v25.8H, v20.8H
    xtn v21.8B, v30.8H
    ushr v20.8H, v30.8H, #8
    sli v20.8H, v25.8H, #4
    xtn v22.8B, v20.8H
    ushr v20.8H, v25.8H, #4
    xtn v23.8B, v20.8H
    add x5, x6, #144
    ldr q4, [x5]
    add x12, x5, #16
    ldr d5, [x12]
    add x5, x7, #144
    ldr q28, [x5]
    add x5, x5, #16
    ldr d29, [x5]
    add x5, x0, #432
    ldr q20, [x9, #0]
    tbl v27.16B, {v4.16B, v5.16B}, v20.16B
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
    and v25.16B, v16.16B, v26.16B
    bic v20.16B, v7.16B, v26.16B
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
    orr v20.16B, v25.16B, v20.16B
    ins v20.h[3], v1.h[3]
    tbl v25.16B, {v20.16B}, v27.16B
    sqrdmulh v20.8H, v25.8H, v14.8H
    mls v25.8H, v20.8H, v13.8H
    sshr v20.8H, v25.8H, #15
    and v20.16B, v20.16B, v13.16B
    add v25.8H, v25.8H, v20.8H
    xtn v21.8B, v30.8H
    ushr v20.8H, v30.8H, #8
    sli v20.8H, v25.8H, #4
    xtn v22.8B, v20.8H
    ushr v20.8H, v25.8H, #4
    xtn v23.8B, v20.8H
    add x5, x6, #24
    ldr q28, [x5]
    add x5, x5, #16
    ldr d29, [x5]
    add x5, x7, #24
    ldr q16, [x5]
    add x5, x5, #16
    ldr d17, [x5]
    add x5, x0, #72
    ldr q20, [x9, #0]
    tbl v27.16B, {v28.16B, v29.16B}, v20.16B
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
    ldr q23, [x4, #64]
    ldr q27, [x3, #48]
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
    sshr v20.8H, v25.8H, #15
    and v20.16B, v20.16B, v13.16B
    add v25.8H, v25.8H, v20.8H
    xtn v21.8B, v30.8H
    ushr v20.8H, v30.8H, #8
    sli v20.8H, v25.8H, #4
    xtn v22.8B, v20.8H
    ushr v20.8H, v25.8H, #4
    xtn v23.8B, v20.8H
    add x5, x6, #96
    ldr q28, [x5]
    add x12, x5, #16
    ldr d29, [x12]
    add x5, x7, #96
    ldr q16, [x5]
    add x5, x5, #16
    ldr d17, [x5]
    add x5, x0, #288
    ldr q20, [x9, #0]
    tbl v27.16B, {v28.16B, v29.16B}, v20.16B
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
    ldr q26, [x4, #80]
    ldr q27, [x3, #64]
    and v25.16B, v12.16B, v27.16B
    bic v20.16B, v8.16B, v27.16B
    orr v12.16B, v25.16B, v20.16B
    ins v12.h[5], v2.h[5]
    tbl v25.16B, {v12.16B}, v26.16B
    sqrdmulh v20.8H, v25.8H, v14.8H
    mls v25.8H, v20.8H, v13.8H
    sshr v20.8H, v25.8H, #15
    and v20.16B, v20.16B, v13.16B
    add v30.8H, v25.8H, v20.8H
    and v25.16B, v3.16B, v27.16B
    bic v20.16B, v15.16B, v27.16B
    orr v20.16B, v25.16B, v20.16B
    ins v20.h[5], v1.h[5]
    tbl v25.16B, {v20.16B}, v26.16B
    sqrdmulh v20.8H, v25.8H, v14.8H
    mls v25.8H, v20.8H, v13.8H
    sshr v20.8H, v25.8H, #15
    and v20.16B, v20.16B, v13.16B
    add v25.8H, v25.8H, v20.8H
    xtn v3.8B, v30.8H
    ushr v20.8H, v30.8H, #8
    sli v20.8H, v25.8H, #4
    xtn v4.8B, v20.8H
    ushr v20.8H, v25.8H, #4
    xtn v5.8B, v20.8H
    add x5, x6, #168
    ldr q11, [x5]
    add x12, x5, #16
    ldr d12, [x12]
    add x5, x7, #168
    ldr q23, [x5]
    add x5, x5, #16
    ldr d24, [x5]
    add x5, x0, #504
    ldr q20, [x9, #0]
    tbl v27.16B, {v11.16B, v12.16B}, v20.16B
    ldr q20, [x9, #16]
    tbl v30.16B, {v23.16B, v24.16B}, v20.16B
    ldr q20, [x9, #32]
    tbl v25.16b, {v3.16b, v4.16b, v5.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #0]
    ldr q20, [x9, #48]
    tbl v27.16B, {v11.16B, v12.16B}, v20.16B
    ldr q20, [x9, #64]
    tbl v30.16B, {v23.16B, v24.16B}, v20.16B
    ldr q20, [x9, #80]
    tbl v25.16b, {v3.16b, v4.16b, v5.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #16]
    ldr q20, [x9, #96]
    tbl v27.16B, {v11.16B, v12.16B}, v20.16B
    ldr q20, [x9, #112]
    tbl v30.16B, {v23.16B, v24.16B}, v20.16B
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
    ldr q27, [x3, #80]
    and v25.16B, v8.16B, v27.16B
    bic v20.16B, v6.16B, v27.16B
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
    sshr v20.8H, v25.8H, #15
    and v20.16B, v20.16B, v13.16B
    add v25.8H, v25.8H, v20.8H
    xtn v3.8B, v30.8H
    ushr v20.8H, v30.8H, #8
    sli v20.8H, v25.8H, #4
    xtn v4.8B, v20.8H
    ushr v20.8H, v25.8H, #4
    xtn v5.8B, v20.8H
    add x5, x6, #48
    ldr q11, [x5]
    add x5, x5, #16
    ldr d12, [x5]
    add x5, x7, #48
    ldr q23, [x5]
    add x5, x5, #16
    ldr d24, [x5]
    add x5, x0, #144
    ldr q20, [x9, #0]
    tbl v27.16B, {v11.16B, v12.16B}, v20.16B
    ldr q20, [x9, #16]
    tbl v30.16B, {v23.16B, v24.16B}, v20.16B
    ldr q20, [x9, #32]
    tbl v25.16b, {v3.16b, v4.16b, v5.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #0]
    ldr q20, [x9, #48]
    tbl v27.16B, {v11.16B, v12.16B}, v20.16B
    ldr q20, [x9, #64]
    tbl v30.16B, {v23.16B, v24.16B}, v20.16B
    ldr q20, [x9, #80]
    tbl v25.16b, {v3.16b, v4.16b, v5.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #16]
    ldr q20, [x9, #96]
    tbl v27.16B, {v11.16B, v12.16B}, v20.16B
    ldr q20, [x9, #112]
    tbl v30.16B, {v23.16B, v24.16B}, v20.16B
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
    ldr q20, [x9, #192]
    tbl v27.16B, {v11.16B, v12.16B}, v20.16B
    ldr q20, [x9, #208]
    tbl v30.16B, {v23.16B, v24.16B}, v20.16B
    ldr q20, [x9, #224]
    tbl v25.16b, {v3.16b, v4.16b, v5.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str d20, [x5, #64]
    ldr q27, [x4, #112]
    orr v6.16B, v6.16B, v6.16B
    ins v6.h[7], v2.h[7]
    tbl v25.16B, {v6.16B}, v27.16B
    sqrdmulh v20.8H, v25.8H, v14.8H
    mls v25.8H, v20.8H, v13.8H
    sshr v20.8H, v25.8H, #15
    and v20.16B, v20.16B, v13.16B
    add v30.8H, v25.8H, v20.8H
    orr v20.16B, v9.16B, v9.16B
    ins v20.h[7], v1.h[7]
    tbl v25.16B, {v20.16B}, v27.16B
    sqrdmulh v20.8H, v25.8H, v14.8H
    mls v25.8H, v20.8H, v13.8H
    sshr v20.8H, v25.8H, #15
    and v20.16B, v20.16B, v13.16B
    add v25.8H, v25.8H, v20.8H
    xtn v8.8B, v30.8H
    ushr v20.8H, v30.8H, #8
    sli v20.8H, v25.8H, #4
    xtn v9.8B, v20.8H
    ushr v20.8H, v25.8H, #4
    xtn v10.8B, v20.8H
    add x5, x6, #120
    ldr q23, [x5]
    add x12, x5, #16
    ldr d24, [x12]
    add x5, x7, #120
    ldr q5, [x5]
    add x5, x5, #16
    ldr d6, [x5]
    add x5, x0, #360
    ldr q20, [x9, #0]
    tbl v27.16B, {v23.16B, v24.16B}, v20.16B
    ldr q20, [x9, #16]
    tbl v30.16B, {v5.16B, v6.16B}, v20.16B
    ldr q20, [x9, #32]
    tbl v25.16b, {v8.16b, v9.16b, v10.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #0]
    ldr q20, [x9, #48]
    tbl v27.16B, {v23.16B, v24.16B}, v20.16B
    ldr q20, [x9, #64]
    tbl v30.16B, {v5.16B, v6.16B}, v20.16B
    ldr q20, [x9, #80]
    tbl v25.16b, {v8.16b, v9.16b, v10.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #16]
    ldr q20, [x9, #96]
    tbl v27.16B, {v23.16B, v24.16B}, v20.16B
    ldr q20, [x9, #112]
    tbl v30.16B, {v5.16B, v6.16B}, v20.16B
    ldr q20, [x9, #128]
    tbl v25.16b, {v8.16b, v9.16b, v10.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #32]
    ldr q20, [x9, #144]
    tbl v27.16B, {v23.16B, v24.16B}, v20.16B
    ldr q20, [x9, #160]
    tbl v30.16B, {v5.16B, v6.16B}, v20.16B
    ldr q20, [x9, #176]
    tbl v25.16b, {v8.16b, v9.16b, v10.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str q20, [x5, #48]
    ldr q20, [x9, #192]
    tbl v27.16B, {v23.16B, v24.16B}, v20.16B
    ldr q20, [x9, #208]
    tbl v30.16B, {v5.16B, v6.16B}, v20.16B
    ldr q20, [x9, #224]
    tbl v25.16b, {v8.16b, v9.16b, v10.16b}, v20.16b
    orr v20.16B, v27.16B, v30.16B
    orr v20.16B, v20.16B, v25.16B
    str d20, [x5, #64]
    ldr q8, [x4, #128]
    orr v26.16B, v18.16B, v18.16B
    tbl v30.16B, {v26.16B}, v8.16B
    sqrdmulh v20.8H, v30.8H, v14.8H
    mls v30.8H, v20.8H, v13.8H
    sshr v3.8H, v30.8H, #15
    and v7.16B, v3.16B, v13.16B
    add v31.8H, v30.8H, v7.8H
    orr v7.16B, v19.16B, v19.16B
    tbl v0.16B, {v7.16B}, v8.16B
    sqrdmulh v22.8H, v0.8H, v14.8H
    mls v0.8H, v22.8H, v13.8H
    sshr v5.8H, v0.8H, #15
    and v2.16B, v5.16B, v13.16B
    add v29.8H, v0.8H, v2.8H
    xtn v19.8B, v31.8H
    ushr v10.8H, v31.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v20.8B, v10.8H
    ushr v21.8H, v29.8H, #4
    xtn v21.8B, v21.8H
    add x5, x6, #192
    ldr q15, [x5]
    add x12, x5, #16
    ldr d16, [x12]
    add x8, x7, #192
    ldr q11, [x8]
    add x12, x8, #16
    ldr d12, [x12]
    add x16, x0, #576
    ldr q14, [x9, #0]
    tbl v4.16B, {v15.16B, v16.16B}, v14.16B
    ldr q17, [x9, #16]
    tbl v26.16B, {v11.16B, v12.16B}, v17.16B
    ldr q14, [x9, #32]
    tbl v22.16b, {v19.16b, v20.16b, v21.16b}, v14.16b
    orr v8.16B, v4.16B, v26.16B
    orr v31.16B, v8.16B, v22.16B
    str q31, [x16, #0]
    ldr q5, [x9, #48]
    tbl v25.16B, {v15.16B, v16.16B}, v5.16B
    ldr q7, [x9, #64]
    tbl v24.16B, {v11.16B, v12.16B}, v7.16B
    ldr q26, [x9, #80]
    tbl v4.16b, {v19.16b, v20.16b, v21.16b}, v26.16b
    orr v13.16B, v25.16B, v24.16B
    orr v25.16B, v13.16B, v4.16B
    str q25, [x16, #16]
    ldr q2, [x9, #96]
    tbl v3.16B, {v15.16B, v16.16B}, v2.16B
    ldr q7, [x9, #112]
    tbl v6.16B, {v11.16B, v12.16B}, v7.16B
    ldr q29, [x9, #128]
    tbl v27.16b, {v19.16b, v20.16b, v21.16b}, v29.16b
    orr v18.16B, v3.16B, v6.16B
    orr v18.16B, v18.16B, v27.16B
    str q18, [x16, #32]
    ldr q24, [x9, #144]
    tbl v1.16B, {v15.16B, v16.16B}, v24.16B
    ldr q6, [x9, #160]
    tbl v28.16B, {v11.16B, v12.16B}, v6.16B
    ldr q13, [x9, #176]
    tbl v14.16b, {v19.16b, v20.16b, v21.16b}, v13.16b
    orr v30.16B, v1.16B, v28.16B
    orr v9.16B, v30.16B, v14.16B
    str q9, [x16, #48]
    ldr q22, [x9, #192]
    tbl v1.16B, {v15.16B, v16.16B}, v22.16B
    ldr q3, [x9, #208]
    tbl v25.16B, {v11.16B, v12.16B}, v3.16B
    ldr q12, [x9, #224]
    tbl v15.16b, {v19.16b, v20.16b, v21.16b}, v12.16b
    orr v1.16B, v1.16B, v25.16B
    orr v24.16B, v1.16B, v15.16B
    str d24, [x16, #64]
pair_merge_full_slothy_end:
    ret
