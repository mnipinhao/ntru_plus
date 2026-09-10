.text
.global _pair_merge_small
_pair_merge_small:
pair_merge_small_slothy_start:
    ldr q15, [x1, #384]
    mov w12, #3457
    ldr q6, [x1, #336]
    ldr q16, [x1, #48]
    ldr q14, [x1, #288]
    ldr q7, [x1, #192]
    ldr q0, [x1, #96]
    ext v17.16B, v6.16B, v6.16B, #14
    ldr q6, [x1, #240]
    ext v1.16B, v14.16B, v14.16B, #12
    ldr q4, [x1]
    ext v10.16B, v7.16B, v7.16B, #8
    ext v19.16B, v0.16B, v0.16B, #4
    ext v11.16B, v16.16B, v16.16B, #2
    ldr q2, [x2]
    ext v14.16B, v6.16B, v6.16B, #10
    ldr q6, [x1, #144]
    trn2 v13.8H, v19.8H, v11.8H
    trn1 v9.8H, v15.8H, v17.8H
    trn1 v5.8H, v1.8H, v14.8H
    trn2 v18.8H, v1.8H, v14.8H
    trn2 v12.8H, v15.8H, v17.8H
    trn2 v0.4S, v9.4S, v5.4S
    trn1 v16.8H, v19.8H, v11.8H
    ext v3.16B, v6.16B, v6.16B, #6
    trn1 v19.4S, v9.4S, v5.4S
    trn1 v11.4S, v12.4S, v18.4S
    trn1 v8.8H, v10.8H, v3.8H
    trn2 v12.4S, v12.4S, v18.4S
    trn2 v1.8H, v10.8H, v3.8H
    trn1 v5.4S, v8.4S, v16.4S
    trn2 v7.4S, v8.4S, v16.4S
    ldr q8, [x2, #384]
    trn1 v18.4S, v1.4S, v13.4S
    trn2 v13.4S, v1.4S, v13.4S
    trn1 v1.2D, v0.2D, v7.2D
    trn2 v0.2D, v0.2D, v7.2D
    trn1 v7.2D, v12.2D, v13.2D
    trn2 v10.2D, v12.2D, v13.2D
    ldr q13, [x2, #192]
    trn1 v14.2D, v19.2D, v5.2D
    ext v16.16B, v13.16B, v13.16B, #8
    ldr q13, [x2, #336]
    trn1 v3.2D, v11.2D, v18.2D
    trn2 v6.2D, v19.2D, v5.2D
    trn2 v17.2D, v11.2D, v18.2D
    ext v12.16B, v13.16B, v13.16B, #14
    ldr q13, [x2, #288]
    trn1 v15.8H, v8.8H, v12.8H
    trn2 v9.8H, v8.8H, v12.8H
    ext v19.16B, v13.16B, v13.16B, #12
    ldr q13, [x2, #240]
    ext v5.16B, v13.16B, v13.16B, #10
    ldr q13, [x2, #144]
    trn1 v12.8H, v19.8H, v5.8H
    ext v18.16B, v13.16B, v13.16B, #6
    ldr q13, [x2, #96]
    trn2 v5.8H, v19.8H, v5.8H
    trn1 v8.8H, v16.8H, v18.8H
    ext v11.16B, v13.16B, v13.16B, #4
    ldr q13, [x2, #48]
    trn2 v19.8H, v16.8H, v18.8H
    trn1 v16.4S, v15.4S, v12.4S
    trn2 v15.4S, v15.4S, v12.4S
    ext v13.16B, v13.16B, v13.16B, #2
    trn1 v18.8H, v11.8H, v13.8H
    trn2 v13.8H, v11.8H, v13.8H
    trn1 v11.4S, v9.4S, v5.4S
    trn2 v9.4S, v9.4S, v5.4S
    trn1 v12.4S, v8.4S, v18.4S
    trn1 v5.4S, v19.4S, v13.4S
    trn2 v18.4S, v8.4S, v18.4S
    trn2 v13.4S, v19.4S, v13.4S
    trn1 v8.2D, v16.2D, v12.2D
    trn2 v19.2D, v16.2D, v12.2D
    trn1 v16.2D, v11.2D, v5.2D
    trn2 v11.2D, v11.2D, v5.2D
    trn1 v12.2D, v15.2D, v18.2D
    trn2 v5.2D, v15.2D, v18.2D
    dup v15.8H, w12
    trn1 v18.2D, v9.2D, v13.2D
    trn2 v13.2D, v9.2D, v13.2D
    ldr q29, [x4, #0]
    orr v25.16B, v14.16B, v14.16B
    add x5, x6, #0
    ldr q23, [x5]
    add x5, x5, #16
    ins v25.h[0], v4.h[0]
    ldr d24, [x5]
    add x5, x7, #0
    ldr q21, [x5]
    add x5, x5, #16
    ldr d22, [x5]
    add x5, x0, #0
    tbl v20.16B, {v25.16B}, v29.16B
    sshr v25.8H, v20.8H, #15
    and v25.16B, v25.16B, v15.16B
    add v30.8H, v20.8H, v25.8H
    orr v25.16B, v8.16B, v8.16B
    ins v25.h[0], v2.h[0]
    xtn v26.8B, v30.8H
    tbl v20.16B, {v25.16B}, v29.16B
    ldr q25, [x9, #0]
    tbl v29.16B, {v23.16B, v24.16B}, v25.16B
    sshr v25.8H, v20.8H, #15
    and v25.16B, v25.16B, v15.16B
    add v20.8H, v20.8H, v25.8H
    ushr v25.8H, v30.8H, #8
    sli v25.8H, v20.8H, #4
    xtn v27.8B, v25.8H
    ushr v25.8H, v20.8H, #4
    xtn v28.8B, v25.8H
    ldr q25, [x9, #16]
    tbl v30.16B, {v21.16B, v22.16B}, v25.16B
    ldr q25, [x9, #32]
    tbl v20.16b, {v26.16b, v27.16b, v28.16b}, v25.16b
    orr v25.16B, v29.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #0]
    ldr q25, [x9, #48]
    tbl v29.16B, {v23.16B, v24.16B}, v25.16B
    ldr q25, [x9, #64]
    tbl v30.16B, {v21.16B, v22.16B}, v25.16B
    ldr q25, [x9, #80]
    tbl v20.16b, {v26.16b, v27.16b, v28.16b}, v25.16b
    orr v25.16B, v29.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #16]
    ldr q25, [x9, #96]
    tbl v29.16B, {v23.16B, v24.16B}, v25.16B
    ldr q25, [x9, #112]
    tbl v30.16B, {v21.16B, v22.16B}, v25.16B
    ldr q25, [x9, #128]
    tbl v20.16b, {v26.16b, v27.16b, v28.16b}, v25.16b
    orr v25.16B, v29.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #32]
    ldr q25, [x9, #144]
    tbl v29.16B, {v23.16B, v24.16B}, v25.16B
    ldr q25, [x9, #160]
    tbl v30.16B, {v21.16B, v22.16B}, v25.16B
    ldr q25, [x9, #176]
    tbl v20.16b, {v26.16b, v27.16b, v28.16b}, v25.16b
    ldr q25, [x9, #192]
    tbl v23.16B, {v23.16B, v24.16B}, v25.16B
    orr v25.16B, v29.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #48]
    ldr q25, [x9, #208]
    tbl v30.16B, {v21.16B, v22.16B}, v25.16B
    ldr q25, [x9, #224]
    tbl v20.16b, {v26.16b, v27.16b, v28.16b}, v25.16b
    orr v25.16B, v23.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str d25, [x5, #64]
    ldr q23, [x4, #16]
    ldr q26, [x3, #0]
    add x5, x6, #72
    and v20.16B, v14.16B, v26.16B
    bic v25.16B, v3.16B, v26.16B
    orr v25.16B, v20.16B, v25.16B
    ins v25.h[1], v4.h[1]
    tbl v20.16B, {v25.16B}, v23.16B
    sshr v25.8H, v20.8H, #15
    and v25.16B, v25.16B, v15.16B
    add v30.8H, v20.8H, v25.8H
    and v20.16B, v8.16B, v26.16B
    ldr q8, [x5]
    add x5, x5, #16
    bic v25.16B, v16.16B, v26.16B
    ldr d9, [x5]
    add x5, x7, #72
    xtn v21.8B, v30.8H
    ldr q28, [x5]
    add x5, x5, #16
    orr v25.16B, v20.16B, v25.16B
    ldr d29, [x5]
    add x5, x0, #216
    ins v25.h[1], v2.h[1]
    tbl v20.16B, {v25.16B}, v23.16B
    ldr q25, [x9, #0]
    tbl v27.16B, {v8.16B, v9.16B}, v25.16B
    sshr v25.8H, v20.8H, #15
    and v25.16B, v25.16B, v15.16B
    add v20.8H, v20.8H, v25.8H
    ushr v25.8H, v30.8H, #8
    sli v25.8H, v20.8H, #4
    xtn v22.8B, v25.8H
    ushr v25.8H, v20.8H, #4
    xtn v23.8B, v25.8H
    ldr q25, [x9, #16]
    tbl v30.16B, {v28.16B, v29.16B}, v25.16B
    ldr q25, [x9, #32]
    tbl v20.16b, {v21.16b, v22.16b, v23.16b}, v25.16b
    orr v25.16B, v27.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #0]
    ldr q25, [x9, #48]
    tbl v27.16B, {v8.16B, v9.16B}, v25.16B
    ldr q25, [x9, #64]
    tbl v30.16B, {v28.16B, v29.16B}, v25.16B
    ldr q25, [x9, #80]
    tbl v20.16b, {v21.16b, v22.16b, v23.16b}, v25.16b
    orr v25.16B, v27.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #16]
    ldr q25, [x9, #96]
    tbl v27.16B, {v8.16B, v9.16B}, v25.16B
    ldr q25, [x9, #112]
    tbl v30.16B, {v28.16B, v29.16B}, v25.16B
    ldr q25, [x9, #128]
    tbl v20.16b, {v21.16b, v22.16b, v23.16b}, v25.16b
    orr v25.16B, v27.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #32]
    ldr q25, [x9, #144]
    tbl v27.16B, {v8.16B, v9.16B}, v25.16B
    ldr q25, [x9, #160]
    tbl v30.16B, {v28.16B, v29.16B}, v25.16B
    ldr q25, [x9, #176]
    tbl v20.16b, {v21.16b, v22.16b, v23.16b}, v25.16b
    orr v25.16B, v27.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #48]
    ldr q25, [x9, #192]
    tbl v27.16B, {v8.16B, v9.16B}, v25.16B
    ldr q25, [x9, #208]
    tbl v30.16B, {v28.16B, v29.16B}, v25.16B
    ldr q25, [x9, #224]
    tbl v20.16b, {v21.16b, v22.16b, v23.16b}, v25.16b
    orr v25.16B, v27.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str d25, [x5, #64]
    ldr q23, [x4, #32]
    ldr q27, [x3, #16]
    add x5, x6, #144
    ldr q8, [x5]
    add x12, x5, #16
    add x5, x7, #144
    ldr d9, [x12]
    ldr q28, [x5]
    add x5, x5, #16
    ldr d29, [x5]
    add x5, x0, #432
    and v20.16B, v3.16B, v27.16B
    bic v25.16B, v1.16B, v27.16B
    orr v25.16B, v20.16B, v25.16B
    ins v25.h[2], v4.h[2]
    tbl v20.16B, {v25.16B}, v23.16B
    sshr v25.8H, v20.8H, #15
    and v25.16B, v25.16B, v15.16B
    add v30.8H, v20.8H, v25.8H
    and v20.16B, v16.16B, v27.16B
    bic v25.16B, v12.16B, v27.16B
    xtn v21.8B, v30.8H
    orr v25.16B, v20.16B, v25.16B
    ins v25.h[2], v2.h[2]
    tbl v20.16B, {v25.16B}, v23.16B
    ldr q25, [x9, #0]
    tbl v27.16B, {v8.16B, v9.16B}, v25.16B
    sshr v25.8H, v20.8H, #15
    and v25.16B, v25.16B, v15.16B
    add v20.8H, v20.8H, v25.8H
    ushr v25.8H, v30.8H, #8
    sli v25.8H, v20.8H, #4
    xtn v22.8B, v25.8H
    ushr v25.8H, v20.8H, #4
    xtn v23.8B, v25.8H
    ldr q25, [x9, #16]
    tbl v30.16B, {v28.16B, v29.16B}, v25.16B
    ldr q25, [x9, #32]
    tbl v20.16b, {v21.16b, v22.16b, v23.16b}, v25.16b
    orr v25.16B, v27.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #0]
    ldr q25, [x9, #48]
    tbl v27.16B, {v8.16B, v9.16B}, v25.16B
    ldr q25, [x9, #64]
    tbl v30.16B, {v28.16B, v29.16B}, v25.16B
    ldr q25, [x9, #80]
    tbl v20.16b, {v21.16b, v22.16b, v23.16b}, v25.16b
    orr v25.16B, v27.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #16]
    ldr q25, [x9, #96]
    tbl v27.16B, {v8.16B, v9.16B}, v25.16B
    ldr q25, [x9, #112]
    tbl v30.16B, {v28.16B, v29.16B}, v25.16B
    ldr q25, [x9, #128]
    tbl v20.16b, {v21.16b, v22.16b, v23.16b}, v25.16b
    orr v25.16B, v27.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #32]
    ldr q25, [x9, #144]
    tbl v27.16B, {v8.16B, v9.16B}, v25.16B
    ldr q25, [x9, #160]
    tbl v30.16B, {v28.16B, v29.16B}, v25.16B
    ldr q25, [x9, #176]
    tbl v20.16b, {v21.16b, v22.16b, v23.16b}, v25.16b
    orr v25.16B, v27.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #48]
    ldr q25, [x9, #192]
    tbl v27.16B, {v8.16B, v9.16B}, v25.16B
    ldr q25, [x9, #208]
    tbl v30.16B, {v28.16B, v29.16B}, v25.16B
    ldr q25, [x9, #224]
    tbl v20.16b, {v21.16b, v22.16b, v23.16b}, v25.16b
    orr v25.16B, v27.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str d25, [x5, #64]
    ldr q23, [x4, #48]
    ldr q27, [x3, #32]
    add x5, x6, #24
    ldr q8, [x5]
    add x5, x5, #16
    ldr d9, [x5]
    add x5, x7, #24
    ldr q28, [x5]
    add x5, x5, #16
    ldr d29, [x5]
    add x5, x0, #72
    and v20.16B, v1.16B, v27.16B
    bic v25.16B, v7.16B, v27.16B
    orr v25.16B, v20.16B, v25.16B
    ins v25.h[3], v4.h[3]
    tbl v20.16B, {v25.16B}, v23.16B
    sshr v25.8H, v20.8H, #15
    and v25.16B, v25.16B, v15.16B
    add v30.8H, v20.8H, v25.8H
    and v25.16B, v12.16B, v27.16B
    bic v20.16B, v18.16B, v27.16B
    xtn v21.8B, v30.8H
    orr v25.16B, v25.16B, v20.16B
    ins v25.h[3], v2.h[3]
    tbl v20.16B, {v25.16B}, v23.16B
    ldr q25, [x9, #0]
    tbl v27.16B, {v8.16B, v9.16B}, v25.16B
    sshr v25.8H, v20.8H, #15
    and v25.16B, v25.16B, v15.16B
    add v20.8H, v20.8H, v25.8H
    ushr v25.8H, v30.8H, #8
    sli v25.8H, v20.8H, #4
    xtn v22.8B, v25.8H
    ushr v25.8H, v20.8H, #4
    xtn v23.8B, v25.8H
    ldr q25, [x9, #16]
    tbl v30.16B, {v28.16B, v29.16B}, v25.16B
    ldr q25, [x9, #32]
    tbl v20.16b, {v21.16b, v22.16b, v23.16b}, v25.16b
    orr v25.16B, v27.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #0]
    ldr q25, [x9, #48]
    tbl v27.16B, {v8.16B, v9.16B}, v25.16B
    ldr q25, [x9, #64]
    tbl v30.16B, {v28.16B, v29.16B}, v25.16B
    ldr q25, [x9, #80]
    tbl v20.16b, {v21.16b, v22.16b, v23.16b}, v25.16b
    orr v25.16B, v27.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #16]
    ldr q25, [x9, #96]
    tbl v27.16B, {v8.16B, v9.16B}, v25.16B
    ldr q25, [x9, #112]
    tbl v30.16B, {v28.16B, v29.16B}, v25.16B
    ldr q25, [x9, #128]
    tbl v20.16b, {v21.16b, v22.16b, v23.16b}, v25.16b
    orr v25.16B, v27.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #32]
    ldr q25, [x9, #144]
    tbl v27.16B, {v8.16B, v9.16B}, v25.16B
    ldr q25, [x9, #160]
    tbl v30.16B, {v28.16B, v29.16B}, v25.16B
    ldr q25, [x9, #176]
    tbl v20.16b, {v21.16b, v22.16b, v23.16b}, v25.16b
    orr v25.16B, v27.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #48]
    ldr q25, [x9, #192]
    tbl v27.16B, {v8.16B, v9.16B}, v25.16B
    ldr q25, [x9, #208]
    tbl v30.16B, {v28.16B, v29.16B}, v25.16B
    ldr q25, [x9, #224]
    tbl v20.16b, {v21.16b, v22.16b, v23.16b}, v25.16b
    orr v25.16B, v27.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str d25, [x5, #64]
    ldr q26, [x4, #64]
    ldr q27, [x3, #48]
    add x5, x6, #96
    ldr q23, [x5]
    add x5, x5, #16
    ldr d24, [x5]
    add x5, x7, #96
    and v20.16B, v7.16B, v27.16B
    bic v25.16B, v6.16B, v27.16B
    orr v25.16B, v20.16B, v25.16B
    ins v25.h[4], v4.h[4]
    tbl v20.16B, {v25.16B}, v26.16B
    sshr v25.8H, v20.8H, #15
    and v25.16B, v25.16B, v15.16B
    add v30.8H, v20.8H, v25.8H
    and v20.16B, v18.16B, v27.16B
    bic v25.16B, v19.16B, v27.16B
    xtn v7.8B, v30.8H
    orr v25.16B, v20.16B, v25.16B
    ldr q27, [x5]
    add x5, x5, #16
    ldr d28, [x5]
    add x5, x0, #288
    ins v25.h[4], v2.h[4]
    tbl v20.16B, {v25.16B}, v26.16B
    ldr q25, [x9, #0]
    tbl v18.16B, {v23.16B, v24.16B}, v25.16B
    sshr v25.8H, v20.8H, #15
    and v25.16B, v25.16B, v15.16B
    add v20.8H, v20.8H, v25.8H
    ushr v25.8H, v30.8H, #8
    sli v25.8H, v20.8H, #4
    xtn v8.8B, v25.8H
    ushr v25.8H, v20.8H, #4
    xtn v9.8B, v25.8H
    ldr q25, [x9, #16]
    tbl v30.16B, {v27.16B, v28.16B}, v25.16B
    ldr q25, [x9, #32]
    tbl v20.16b, {v7.16b, v8.16b, v9.16b}, v25.16b
    orr v25.16B, v18.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #0]
    ldr q25, [x9, #48]
    tbl v18.16B, {v23.16B, v24.16B}, v25.16B
    ldr q25, [x9, #64]
    tbl v30.16B, {v27.16B, v28.16B}, v25.16B
    ldr q25, [x9, #80]
    tbl v20.16b, {v7.16b, v8.16b, v9.16b}, v25.16b
    orr v25.16B, v18.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #16]
    ldr q25, [x9, #96]
    tbl v18.16B, {v23.16B, v24.16B}, v25.16B
    ldr q25, [x9, #112]
    tbl v30.16B, {v27.16B, v28.16B}, v25.16B
    ldr q25, [x9, #128]
    tbl v20.16b, {v7.16b, v8.16b, v9.16b}, v25.16b
    orr v25.16B, v18.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #32]
    ldr q25, [x9, #144]
    tbl v18.16B, {v23.16B, v24.16B}, v25.16B
    ldr q25, [x9, #160]
    tbl v30.16B, {v27.16B, v28.16B}, v25.16B
    ldr q25, [x9, #176]
    tbl v20.16b, {v7.16b, v8.16b, v9.16b}, v25.16b
    orr v25.16B, v18.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #48]
    ldr q25, [x9, #192]
    tbl v18.16B, {v23.16B, v24.16B}, v25.16B
    ldr q25, [x9, #208]
    tbl v30.16B, {v27.16B, v28.16B}, v25.16B
    ldr q25, [x9, #224]
    tbl v20.16b, {v7.16b, v8.16b, v9.16b}, v25.16b
    orr v25.16B, v18.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str d25, [x5, #64]
    ldr q27, [x4, #80]
    ldr q18, [x3, #64]
    add x5, x6, #168
    ldr q23, [x5]
    add x5, x5, #16
    ldr d24, [x5]
    add x5, x7, #168
    and v20.16B, v6.16B, v18.16B
    bic v25.16B, v17.16B, v18.16B
    orr v25.16B, v20.16B, v25.16B
    ins v25.h[5], v4.h[5]
    tbl v20.16B, {v25.16B}, v27.16B
    sshr v25.8H, v20.8H, #15
    and v25.16B, v25.16B, v15.16B
    add v30.8H, v20.8H, v25.8H
    and v20.16B, v19.16B, v18.16B
    bic v25.16B, v11.16B, v18.16B
    xtn v7.8B, v30.8H
    orr v25.16B, v20.16B, v25.16B
    ins v25.h[5], v2.h[5]
    tbl v20.16B, {v25.16B}, v27.16B
    ldr q27, [x5]
    add x5, x5, #16
    ldr q25, [x9, #0]
    ldr d28, [x5]
    add x5, x0, #504
    tbl v18.16B, {v23.16B, v24.16B}, v25.16B
    sshr v25.8H, v20.8H, #15
    and v25.16B, v25.16B, v15.16B
    add v20.8H, v20.8H, v25.8H
    ushr v25.8H, v30.8H, #8
    sli v25.8H, v20.8H, #4
    xtn v8.8B, v25.8H
    ushr v25.8H, v20.8H, #4
    xtn v9.8B, v25.8H
    ldr q25, [x9, #16]
    tbl v30.16B, {v27.16B, v28.16B}, v25.16B
    ldr q25, [x9, #32]
    tbl v20.16b, {v7.16b, v8.16b, v9.16b}, v25.16b
    orr v25.16B, v18.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #0]
    ldr q25, [x9, #48]
    tbl v18.16B, {v23.16B, v24.16B}, v25.16B
    ldr q25, [x9, #64]
    tbl v30.16B, {v27.16B, v28.16B}, v25.16B
    ldr q25, [x9, #80]
    tbl v20.16b, {v7.16b, v8.16b, v9.16b}, v25.16b
    orr v25.16B, v18.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #16]
    ldr q25, [x9, #96]
    tbl v18.16B, {v23.16B, v24.16B}, v25.16B
    ldr q25, [x9, #112]
    tbl v30.16B, {v27.16B, v28.16B}, v25.16B
    ldr q25, [x9, #128]
    tbl v20.16b, {v7.16b, v8.16b, v9.16b}, v25.16b
    orr v25.16B, v18.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #32]
    ldr q25, [x9, #144]
    tbl v18.16B, {v23.16B, v24.16B}, v25.16B
    ldr q25, [x9, #160]
    tbl v30.16B, {v27.16B, v28.16B}, v25.16B
    ldr q25, [x9, #176]
    tbl v20.16b, {v7.16b, v8.16b, v9.16b}, v25.16b
    orr v25.16B, v18.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #48]
    ldr q25, [x9, #192]
    tbl v18.16B, {v23.16B, v24.16B}, v25.16B
    ldr q25, [x9, #208]
    tbl v30.16B, {v27.16B, v28.16B}, v25.16B
    ldr q25, [x9, #224]
    tbl v20.16b, {v7.16b, v8.16b, v9.16b}, v25.16b
    orr v25.16B, v18.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str d25, [x5, #64]
    ldr q27, [x4, #96]
    ldr q18, [x3, #80]
    add x5, x6, #48
    ldr q23, [x5]
    add x5, x5, #16
    ldr d24, [x5]
    add x5, x7, #48
    and v20.16B, v17.16B, v18.16B
    bic v25.16B, v0.16B, v18.16B
    orr v25.16B, v20.16B, v25.16B
    ins v25.h[6], v4.h[6]
    tbl v20.16B, {v25.16B}, v27.16B
    sshr v25.8H, v20.8H, #15
    and v25.16B, v25.16B, v15.16B
    add v30.8H, v20.8H, v25.8H
    and v20.16B, v11.16B, v18.16B
    bic v25.16B, v5.16B, v18.16B
    xtn v7.8B, v30.8H
    orr v25.16B, v20.16B, v25.16B
    ins v25.h[6], v2.h[6]
    tbl v20.16B, {v25.16B}, v27.16B
    ldr q27, [x5]
    add x5, x5, #16
    ldr q25, [x9, #0]
    ldr d28, [x5]
    add x5, x0, #144
    tbl v18.16B, {v23.16B, v24.16B}, v25.16B
    sshr v25.8H, v20.8H, #15
    and v25.16B, v25.16B, v15.16B
    add v20.8H, v20.8H, v25.8H
    ushr v25.8H, v30.8H, #8
    sli v25.8H, v20.8H, #4
    xtn v8.8B, v25.8H
    ushr v25.8H, v20.8H, #4
    xtn v9.8B, v25.8H
    ldr q25, [x9, #16]
    tbl v30.16B, {v27.16B, v28.16B}, v25.16B
    ldr q25, [x9, #32]
    tbl v20.16b, {v7.16b, v8.16b, v9.16b}, v25.16b
    orr v25.16B, v18.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #0]
    ldr q25, [x9, #48]
    tbl v18.16B, {v23.16B, v24.16B}, v25.16B
    ldr q25, [x9, #64]
    tbl v30.16B, {v27.16B, v28.16B}, v25.16B
    ldr q25, [x9, #80]
    tbl v20.16b, {v7.16b, v8.16b, v9.16b}, v25.16b
    orr v25.16B, v18.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #16]
    ldr q25, [x9, #96]
    tbl v18.16B, {v23.16B, v24.16B}, v25.16B
    ldr q25, [x9, #112]
    tbl v30.16B, {v27.16B, v28.16B}, v25.16B
    ldr q25, [x9, #128]
    tbl v20.16b, {v7.16b, v8.16b, v9.16b}, v25.16b
    orr v25.16B, v18.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #32]
    ldr q25, [x9, #144]
    tbl v18.16B, {v23.16B, v24.16B}, v25.16B
    ldr q25, [x9, #160]
    tbl v30.16B, {v27.16B, v28.16B}, v25.16B
    ldr q25, [x9, #176]
    tbl v20.16b, {v7.16b, v8.16b, v9.16b}, v25.16b
    orr v25.16B, v18.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #48]
    ldr q25, [x9, #192]
    tbl v18.16B, {v23.16B, v24.16B}, v25.16B
    ldr q25, [x9, #208]
    tbl v30.16B, {v27.16B, v28.16B}, v25.16B
    ldr q25, [x9, #224]
    tbl v20.16b, {v7.16b, v8.16b, v9.16b}, v25.16b
    orr v25.16B, v18.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str d25, [x5, #64]
    ldr q18, [x4, #112]
    orr v25.16B, v0.16B, v0.16B
    add x5, x6, #120
    add x12, x5, #16
    ins v25.h[7], v4.h[7]
    ldr d6, [x12]
    tbl v20.16B, {v25.16B}, v18.16B
    sshr v25.8H, v20.8H, #15
    and v25.16B, v25.16B, v15.16B
    add v30.8H, v20.8H, v25.8H
    orr v25.16B, v5.16B, v5.16B
    ldr q5, [x5]
    add x5, x7, #120
    ldr q27, [x5]
    add x5, x5, #16
    ins v25.h[7], v2.h[7]
    xtn v21.8B, v30.8H
    ldr d28, [x5]
    add x5, x0, #360
    tbl v20.16B, {v25.16B}, v18.16B
    ldr q25, [x9, #0]
    tbl v18.16B, {v5.16B, v6.16B}, v25.16B
    sshr v25.8H, v20.8H, #15
    and v25.16B, v25.16B, v15.16B
    add v20.8H, v20.8H, v25.8H
    ushr v25.8H, v30.8H, #8
    sli v25.8H, v20.8H, #4
    xtn v22.8B, v25.8H
    ushr v25.8H, v20.8H, #4
    xtn v23.8B, v25.8H
    ldr q25, [x9, #16]
    tbl v30.16B, {v27.16B, v28.16B}, v25.16B
    ldr q25, [x9, #32]
    tbl v20.16b, {v21.16b, v22.16b, v23.16b}, v25.16b
    orr v25.16B, v18.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #0]
    ldr q25, [x9, #48]
    tbl v18.16B, {v5.16B, v6.16B}, v25.16B
    ldr q25, [x9, #64]
    tbl v30.16B, {v27.16B, v28.16B}, v25.16B
    ldr q25, [x9, #80]
    tbl v20.16b, {v21.16b, v22.16b, v23.16b}, v25.16b
    orr v25.16B, v18.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #16]
    ldr q25, [x9, #96]
    tbl v18.16B, {v5.16B, v6.16B}, v25.16B
    ldr q25, [x9, #112]
    tbl v30.16B, {v27.16B, v28.16B}, v25.16B
    ldr q25, [x9, #128]
    tbl v20.16b, {v21.16b, v22.16b, v23.16b}, v25.16b
    orr v25.16B, v18.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #32]
    ldr q25, [x9, #144]
    tbl v18.16B, {v5.16B, v6.16B}, v25.16B
    ldr q25, [x9, #160]
    tbl v30.16B, {v27.16B, v28.16B}, v25.16B
    ldr q25, [x9, #176]
    tbl v20.16b, {v21.16b, v22.16b, v23.16b}, v25.16b
    orr v25.16B, v18.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str q25, [x5, #48]
    ldr q25, [x9, #192]
    tbl v18.16B, {v5.16B, v6.16B}, v25.16B
    ldr q25, [x9, #208]
    tbl v30.16B, {v27.16B, v28.16B}, v25.16B
    ldr q25, [x9, #224]
    tbl v20.16b, {v21.16b, v22.16b, v23.16b}, v25.16b
    orr v25.16B, v18.16B, v30.16B
    orr v25.16B, v25.16B, v20.16B
    str d25, [x5, #64]
    ldr q21, [x9, #64]
    orr v12.16B, v13.16B, v13.16B
    ldr q11, [x4, #128]
    add x12, x7, #192
    ldr q22, [x9, #80]
    add x16, x0, #576
    orr v18.16B, v10.16B, v10.16B
    add x8, x12, #16
    ldr d2, [x8]
    add x5, x6, #192
    ldr q25, [x9, #128]
    ldr q29, [x9, #208]
    tbl v1.16B, {v18.16B}, v11.16B
    tbl v12.16B, {v12.16B}, v11.16B
    ldr q3, [x9, #96]
    ldr q4, [x5]
    sshr v16.8H, v1.8H, #15
    and v27.16B, v16.16B, v15.16B
    sshr v16.8H, v12.8H, #15
    add v5.8H, v1.8H, v27.8H
    ldr q27, [x9, #112]
    and v13.16B, v16.16B, v15.16B
    ldr q1, [x12]
    add x12, x5, #16
    ldr q15, [x9, #224]
    add v14.8H, v12.8H, v13.8H
    ldr q12, [x9, #192]
    xtn v17.8B, v5.8H
    ushr v6.8H, v5.8H, #8
    ldr d5, [x12]
    ushr v13.8H, v14.8H, #4
    ldr q8, [x9, #0]
    tbl v9.16B, {v1.16B, v2.16B}, v27.16B
    sli v6.8H, v14.8H, #4
    ldr q30, [x9, #176]
    xtn v19.8B, v13.8H
    ldr q13, [x9, #16]
    tbl v28.16B, {v1.16B, v2.16B}, v21.16B
    xtn v18.8B, v6.8H
    tbl v29.16B, {v1.16B, v2.16B}, v29.16B
    tbl v0.16B, {v4.16B, v5.16B}, v3.16B
    tbl v16.16B, {v4.16B, v5.16B}, v12.16B
    ldr q12, [x9, #48]
    ldr q6, [x9, #160]
    tbl v21.16B, {v4.16B, v5.16B}, v8.16B
    tbl v8.16b, {v17.16b, v18.16b, v19.16b}, v25.16b
    orr v25.16B, v16.16B, v29.16B
    tbl v29.16b, {v17.16b, v18.16b, v19.16b}, v30.16b
    ldr q30, [x9, #32]
    orr v9.16B, v0.16B, v9.16B
    tbl v23.16B, {v1.16B, v2.16B}, v13.16B
    tbl v7.16B, {v4.16B, v5.16B}, v12.16B
    orr v31.16B, v9.16B, v8.16B
    ldr q9, [x9, #144]
    orr v11.16B, v7.16B, v28.16B
    orr v28.16B, v21.16B, v23.16B
    tbl v21.16b, {v17.16b, v18.16b, v19.16b}, v22.16b
    tbl v27.16B, {v1.16B, v2.16B}, v6.16B
    tbl v22.16b, {v17.16b, v18.16b, v19.16b}, v30.16b
    tbl v19.16b, {v17.16b, v18.16b, v19.16b}, v15.16b
    tbl v8.16B, {v4.16B, v5.16B}, v9.16B
    str q31, [x16, #32]
    orr v3.16B, v11.16B, v21.16B
    orr v0.16B, v8.16B, v27.16B
    orr v22.16B, v28.16B, v22.16B
    orr v20.16B, v25.16B, v19.16B
    str q3, [x16, #16]
    orr v21.16B, v0.16B, v29.16B
    str d20, [x16, #64]
    str q22, [x16, #0]
    str q21, [x16, #48]
pair_merge_small_slothy_end:
    ret
