.text
.global lazy_i16
lazy_i16:
// P3-B inherited P3-A physical allocation with dead-register reuse; final stores are centered in producer registers.
// live-in: x0 output, x1 packed scratch, x3 stage table, x4 scale table, and documented vector inputs.
// live-out: x0 and the centered natural-order coefficient output in memory.
// coefficient range: I9 <= 3456; I16 <= 30939; terminal <= 6912; stored centered <= 1728.
// reserved physical registers: x18-x30, sp, and xzr; no stack spill is permitted.
lazy_i16_slothy_start:
    mov w17, #3457
    dup v18.8H, w17
    ldr q9, [x1, #0]
    ldr q2, [x1, #16]
    ldr q4, [x1, #32]
    ldr q24, [x1, #48]
    ldr q5, [x1, #64]
    ldr q17, [x1, #80]
    ldr q15, [x1, #96]
    ldr q21, [x1, #112]
    ldr q23, [x1, #128]
    ldr q11, [x1, #144]
    ldr q13, [x1, #160]
    ldr q12, [x1, #176]
    ldr q14, [x1, #192]
    ldr q10, [x1, #208]
    ldr q16, [x1, #224]
    ldr q7, [x1, #240]
    orr v30.16B, v9.16B, v9.16B
    add v31.8H, v9.8H, v23.8H
    sub v20.8H, v30.8H, v23.8H
    orr v30.16B, v5.16B, v5.16B
    add v29.8H, v5.8H, v14.8H
    sub v25.8H, v30.8H, v14.8H
    orr v30.16B, v4.16B, v4.16B
    add v4.8H, v4.8H, v13.8H
    sub v9.8H, v30.8H, v13.8H
    orr v30.16B, v15.16B, v15.16B
    add v5.8H, v15.8H, v16.8H
    sub v23.8H, v30.8H, v16.8H
    orr v30.16B, v2.16B, v2.16B
    add v15.8H, v2.8H, v11.8H
    sub v2.8H, v30.8H, v11.8H
    orr v30.16B, v17.16B, v17.16B
    add v17.8H, v17.8H, v10.8H
    sub v11.8H, v30.8H, v10.8H
    orr v30.16B, v24.16B, v24.16B
    add v13.8H, v24.8H, v12.8H
    sub v12.8H, v30.8H, v12.8H
    orr v30.16B, v21.16B, v21.16B
    add v14.8H, v21.8H, v7.8H
    sub v16.8H, v30.8H, v7.8H
    ldr q10, [x3, #32]
    sqrdmulh v7.8H, v25.8H, v10.H[3]
    sqrdmulh v30.8H, v23.8H, v10.H[7]
    mul v28.8H, v25.8H, v10.H[2]
    mul v1.8H, v23.8H, v10.H[6]
    mls v28.8H, v7.8H, v18.8H
    mls v1.8H, v30.8H, v18.8H
    orr v30.16B, v31.16B, v31.16B
    add v31.8H, v31.8H, v29.8H
    sub v19.8H, v30.8H, v29.8H
    orr v30.16B, v20.16B, v20.16B
    add v29.8H, v20.8H, v28.8H
    sub v22.8H, v30.8H, v28.8H
    orr v30.16B, v4.16B, v4.16B
    add v25.8H, v4.8H, v5.8H
    sub v4.8H, v30.8H, v5.8H
    orr v30.16B, v9.16B, v9.16B
    add v5.8H, v9.8H, v1.8H
    sub v23.8H, v30.8H, v1.8H
    ldr q10, [x3, #48]
    sqrdmulh v7.8H, v11.8H, v10.H[3]
    sqrdmulh v30.8H, v16.8H, v10.H[7]
    mul v3.8H, v11.8H, v10.H[2]
    mul v8.8H, v16.8H, v10.H[6]
    mls v3.8H, v7.8H, v18.8H
    mls v8.8H, v30.8H, v18.8H
    orr v30.16B, v15.16B, v15.16B
    add v15.8H, v15.8H, v17.8H
    sub v24.8H, v30.8H, v17.8H
    orr v30.16B, v2.16B, v2.16B
    add v17.8H, v2.8H, v3.8H
    sub v21.8H, v30.8H, v3.8H
    orr v30.16B, v13.16B, v13.16B
    add v11.8H, v13.8H, v14.8H
    sub v13.8H, v30.8H, v14.8H
    orr v30.16B, v12.16B, v12.16B
    add v12.8H, v12.8H, v8.8H
    sub v14.8H, v30.8H, v8.8H
    ldr q10, [x3, #64]
    sqrdmulh v16.8H, v5.8H, v10.H[3]
    sqrdmulh v7.8H, v4.8H, v10.H[5]
    sqrdmulh v30.8H, v23.8H, v10.H[7]
    mul v6.8H, v5.8H, v10.H[2]
    mul v9.8H, v4.8H, v10.H[4]
    mul v2.8H, v23.8H, v10.H[6]
    mls v6.8H, v16.8H, v18.8H
    mls v9.8H, v7.8H, v18.8H
    mls v2.8H, v30.8H, v18.8H
    orr v30.16B, v31.16B, v31.16B
    add v20.8H, v31.8H, v25.8H
    sub v31.8H, v30.8H, v25.8H
    orr v30.16B, v29.16B, v29.16B
    add v29.8H, v29.8H, v6.8H
    sub v3.8H, v30.8H, v6.8H
    orr v30.16B, v19.16B, v19.16B
    add v25.8H, v19.8H, v9.8H
    sub v26.8H, v30.8H, v9.8H
    orr v30.16B, v22.16B, v22.16B
    add v23.8H, v22.8H, v2.8H
    sub v19.8H, v30.8H, v2.8H
    ldr q10, [x3, #80]
    sqrdmulh v16.8H, v12.8H, v10.H[3]
    sqrdmulh v7.8H, v13.8H, v10.H[5]
    sqrdmulh v30.8H, v14.8H, v10.H[7]
    mul v4.8H, v12.8H, v10.H[2]
    mul v9.8H, v13.8H, v10.H[4]
    mul v5.8H, v14.8H, v10.H[6]
    mls v4.8H, v16.8H, v18.8H
    mls v9.8H, v7.8H, v18.8H
    mls v5.8H, v30.8H, v18.8H
    orr v30.16B, v15.16B, v15.16B
    add v15.8H, v15.8H, v11.8H
    sub v2.8H, v30.8H, v11.8H
    orr v30.16B, v17.16B, v17.16B
    add v13.8H, v17.8H, v4.8H
    sub v4.8H, v30.8H, v4.8H
    orr v30.16B, v24.16B, v24.16B
    add v12.8H, v24.8H, v9.8H
    sub v17.8H, v30.8H, v9.8H
    orr v30.16B, v21.16B, v21.16B
    add v11.8H, v21.8H, v5.8H
    sub v5.8H, v30.8H, v5.8H
    ldr q14, [x3, #96]
    sqrdmulh v10.8H, v15.8H, v14.H[1]
    sqrdmulh v16.8H, v13.8H, v14.H[3]
    sqrdmulh v7.8H, v12.8H, v14.H[5]
    sqrdmulh v30.8H, v11.8H, v14.H[7]
    mul v13.8H, v13.8H, v14.H[2]
    mul v12.8H, v12.8H, v14.H[4]
    mul v14.8H, v11.8H, v14.H[6]
    mls v15.8H, v10.8H, v18.8H
    mls v13.8H, v16.8H, v18.8H
    mls v12.8H, v7.8H, v18.8H
    mls v14.8H, v30.8H, v18.8H
    orr v30.16B, v20.16B, v20.16B
    add v22.8H, v20.8H, v15.8H
    sub v8.8H, v30.8H, v15.8H
    orr v30.16B, v29.16B, v29.16B
    add v6.8H, v29.8H, v13.8H
    sub v24.8H, v30.8H, v13.8H
    orr v30.16B, v25.16B, v25.16B
    add v15.8H, v25.8H, v12.8H
    sub v21.8H, v30.8H, v12.8H
    orr v30.16B, v23.16B, v23.16B
    add v23.8H, v23.8H, v14.8H
    sub v20.8H, v30.8H, v14.8H
    ldr q7, [x3, #112]
    sqrdmulh v11.8H, v2.8H, v7.H[1]
    sqrdmulh v13.8H, v4.8H, v7.H[3]
    sqrdmulh v12.8H, v17.8H, v7.H[5]
    sqrdmulh v30.8H, v5.8H, v7.H[7]
    mul v14.8H, v2.8H, v7.H[0]
    mul v10.8H, v4.8H, v7.H[2]
    mul v16.8H, v17.8H, v7.H[4]
    mul v7.8H, v5.8H, v7.H[6]
    mls v14.8H, v11.8H, v18.8H
    mls v10.8H, v13.8H, v18.8H
    mls v16.8H, v12.8H, v18.8H
    mls v7.8H, v30.8H, v18.8H
    orr v30.16B, v31.16B, v31.16B
    add v31.8H, v31.8H, v14.8H
    sub v29.8H, v30.8H, v14.8H
    orr v30.16B, v3.16B, v3.16B
    add v25.8H, v3.8H, v10.8H
    sub v9.8H, v30.8H, v10.8H
    orr v30.16B, v26.16B, v26.16B
    add v2.8H, v26.8H, v16.8H
    sub v4.8H, v30.8H, v16.8H
    orr v30.16B, v19.16B, v19.16B
    add v17.8H, v19.8H, v7.8H
    sub v5.8H, v30.8H, v7.8H
    ldr q30, [x4, #16]
    sqrdmulh v13.8H, v22.8H, v30.8H
    ldr q30, [x4, #48]
    sqrdmulh v12.8H, v6.8H, v30.8H
    ldr q30, [x4, #80]
    sqrdmulh v14.8H, v15.8H, v30.8H
    ldr q30, [x4, #112]
    sqrdmulh v10.8H, v23.8H, v30.8H
    ldr q30, [x4, #0]
    mul v7.8H, v22.8H, v30.8H
    ldr q30, [x4, #32]
    mul v16.8H, v6.8H, v30.8H
    ldr q30, [x4, #64]
    mul v15.8H, v15.8H, v30.8H
    ldr q30, [x4, #96]
    mul v23.8H, v23.8H, v30.8H
    mls v7.8H, v13.8H, v18.8H
    mls v16.8H, v12.8H, v18.8H
    mls v15.8H, v14.8H, v18.8H
    mls v23.8H, v10.8H, v18.8H
    orr v11.16B, v7.16B, v7.16B
    orr v13.16B, v16.16B, v16.16B
    ext v7.16B, v7.16B, v7.16B, #8
    ext v30.16B, v16.16B, v16.16B, #8
    sub v7.8H, v7.8H, v11.8H
    sub v14.8H, v30.8H, v13.8H
    mov w9, #63902
    dup v10.8H, w9
    mov w8, #50048
    dup v30.8H, w8
    sqrdmulh v16.8H, v7.8H, v30.8H
    sqrdmulh v30.8H, v14.8H, v30.8H
    mul v7.8H, v7.8H, v10.8H
    mul v12.8H, v14.8H, v10.8H
    mls v7.8H, v16.8H, v18.8H
    mls v12.8H, v30.8H, v18.8H
    zip1 v0.2d, v7.2d, v12.2d
    movi v3.8h, #9
    sqrdmulh v1.8h, v0.8h, v3.8h
    mls v0.8h, v1.8h, v18.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v18.16b
    add v0.8h, v0.8h, v1.8h
    ushr v3.8h, v18.8h, #1
    cmgt v1.8h, v0.8h, v3.8h
    and v1.16b, v1.16b, v18.16b
    sub v0.8h, v0.8h, v1.8h
    umov w7, v0.h[0]
    strh w7, [x0, #864]
    umov w2, v0.h[1]
    strh w2, [x0, #870]
    umov w12, v0.h[2]
    strh w12, [x0, #876]
    umov w10, v0.h[3]
    strh w10, [x0, #882]
    umov w5, v0.h[4]
    strh w5, [x0, #918]
    umov w15, v0.h[5]
    strh w15, [x0, #924]
    umov w14, v0.h[6]
    strh w14, [x0, #930]
    umov w11, v0.h[7]
    strh w11, [x0, #936]
    mov w16, #64814
    dup v14.8H, w16
    mov w13, #58692
    dup v30.8H, w13
    sqrdmulh v10.8H, v7.8H, v30.8H
    sqrdmulh v16.8H, v12.8H, v30.8H
    mul v7.8H, v7.8H, v14.8H
    mul v30.8H, v12.8H, v14.8H
    mls v7.8H, v10.8H, v18.8H
    mls v30.8H, v16.8H, v18.8H
    sub v7.8H, v11.8H, v7.8H
    sub v30.8H, v13.8H, v30.8H
    zip1 v0.2d, v7.2d, v30.2d
    movi v3.8h, #9
    sqrdmulh v1.8h, v0.8h, v3.8h
    mls v0.8h, v1.8h, v18.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v18.16b
    add v0.8h, v0.8h, v1.8h
    ushr v3.8h, v18.8h, #1
    cmgt v1.8h, v0.8h, v3.8h
    and v1.16b, v1.16b, v18.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #0]
    umov w13, v0.h[1]
    strh w13, [x0, #6]
    umov w13, v0.h[2]
    strh w13, [x0, #12]
    umov w13, v0.h[3]
    strh w13, [x0, #18]
    umov w13, v0.h[4]
    strh w13, [x0, #54]
    umov w13, v0.h[5]
    strh w13, [x0, #60]
    umov w13, v0.h[6]
    strh w13, [x0, #66]
    umov w13, v0.h[7]
    strh w13, [x0, #72]
    orr v11.16B, v15.16B, v15.16B
    orr v13.16B, v23.16B, v23.16B
    ext v7.16B, v15.16B, v15.16B, #8
    ext v30.16B, v23.16B, v23.16B, #8
    sub v7.8H, v7.8H, v11.8H
    sub v14.8H, v30.8H, v13.8H
    mov w13, #63902
    dup v10.8H, w13
    mov w13, #50048
    dup v30.8H, w13
    sqrdmulh v16.8H, v7.8H, v30.8H
    sqrdmulh v30.8H, v14.8H, v30.8H
    mul v7.8H, v7.8H, v10.8H
    mul v12.8H, v14.8H, v10.8H
    mls v7.8H, v16.8H, v18.8H
    mls v12.8H, v30.8H, v18.8H
    zip1 v0.2d, v7.2d, v12.2d
    movi v3.8h, #9
    sqrdmulh v1.8h, v0.8h, v3.8h
    mls v0.8h, v1.8h, v18.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v18.16b
    add v0.8h, v0.8h, v1.8h
    ushr v3.8h, v18.8h, #1
    cmgt v1.8h, v0.8h, v3.8h
    and v1.16b, v1.16b, v18.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #972]
    umov w13, v0.h[1]
    strh w13, [x0, #978]
    umov w13, v0.h[2]
    strh w13, [x0, #984]
    umov w13, v0.h[3]
    strh w13, [x0, #990]
    umov w13, v0.h[4]
    strh w13, [x0, #1026]
    umov w13, v0.h[5]
    strh w13, [x0, #1032]
    umov w13, v0.h[6]
    strh w13, [x0, #1038]
    umov w13, v0.h[7]
    strh w13, [x0, #1044]
    mov w13, #64814
    dup v14.8H, w13
    mov w13, #58692
    dup v30.8H, w13
    sqrdmulh v10.8H, v7.8H, v30.8H
    sqrdmulh v16.8H, v12.8H, v30.8H
    mul v7.8H, v7.8H, v14.8H
    mul v30.8H, v12.8H, v14.8H
    mls v7.8H, v10.8H, v18.8H
    mls v30.8H, v16.8H, v18.8H
    sub v7.8H, v11.8H, v7.8H
    sub v30.8H, v13.8H, v30.8H
    zip1 v0.2d, v7.2d, v30.2d
    movi v3.8h, #9
    sqrdmulh v1.8h, v0.8h, v3.8h
    mls v0.8h, v1.8h, v18.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v18.16b
    add v0.8h, v0.8h, v1.8h
    ushr v3.8h, v18.8h, #1
    cmgt v1.8h, v0.8h, v3.8h
    and v1.16b, v1.16b, v18.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #108]
    umov w13, v0.h[1]
    strh w13, [x0, #114]
    umov w13, v0.h[2]
    strh w13, [x0, #120]
    umov w13, v0.h[3]
    strh w13, [x0, #126]
    umov w13, v0.h[4]
    strh w13, [x0, #162]
    umov w13, v0.h[5]
    strh w13, [x0, #168]
    umov w13, v0.h[6]
    strh w13, [x0, #174]
    umov w13, v0.h[7]
    strh w13, [x0, #180]
    ldr q30, [x4, #144]
    sqrdmulh v13.8H, v31.8H, v30.8H
    ldr q30, [x4, #176]
    sqrdmulh v12.8H, v25.8H, v30.8H
    ldr q30, [x4, #208]
    sqrdmulh v14.8H, v2.8H, v30.8H
    ldr q30, [x4, #240]
    sqrdmulh v10.8H, v17.8H, v30.8H
    ldr q30, [x4, #128]
    mul v7.8H, v31.8H, v30.8H
    ldr q30, [x4, #160]
    mul v16.8H, v25.8H, v30.8H
    ldr q30, [x4, #192]
    mul v15.8H, v2.8H, v30.8H
    ldr q30, [x4, #224]
    mul v23.8H, v17.8H, v30.8H
    mls v7.8H, v13.8H, v18.8H
    mls v16.8H, v12.8H, v18.8H
    mls v15.8H, v14.8H, v18.8H
    mls v23.8H, v10.8H, v18.8H
    orr v11.16B, v7.16B, v7.16B
    orr v13.16B, v16.16B, v16.16B
    ext v7.16B, v7.16B, v7.16B, #8
    ext v30.16B, v16.16B, v16.16B, #8
    sub v7.8H, v7.8H, v11.8H
    sub v14.8H, v30.8H, v13.8H
    mov w13, #63902
    dup v10.8H, w13
    mov w13, #50048
    dup v30.8H, w13
    sqrdmulh v16.8H, v7.8H, v30.8H
    sqrdmulh v30.8H, v14.8H, v30.8H
    mul v7.8H, v7.8H, v10.8H
    mul v12.8H, v14.8H, v10.8H
    mls v7.8H, v16.8H, v18.8H
    mls v12.8H, v30.8H, v18.8H
    zip1 v0.2d, v7.2d, v12.2d
    movi v2.8h, #9
    sqrdmulh v1.8h, v0.8h, v2.8h
    mls v0.8h, v1.8h, v18.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v18.16b
    add v0.8h, v0.8h, v1.8h
    ushr v2.8h, v18.8h, #1
    cmgt v1.8h, v0.8h, v2.8h
    and v1.16b, v1.16b, v18.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #1080]
    umov w13, v0.h[1]
    strh w13, [x0, #1086]
    umov w13, v0.h[2]
    strh w13, [x0, #1092]
    umov w13, v0.h[3]
    strh w13, [x0, #1098]
    umov w13, v0.h[4]
    strh w13, [x0, #1134]
    umov w13, v0.h[5]
    strh w13, [x0, #1140]
    umov w13, v0.h[6]
    strh w13, [x0, #1146]
    umov w13, v0.h[7]
    strh w13, [x0, #1152]
    mov w13, #64814
    dup v14.8H, w13
    mov w13, #58692
    dup v30.8H, w13
    sqrdmulh v10.8H, v7.8H, v30.8H
    sqrdmulh v16.8H, v12.8H, v30.8H
    mul v7.8H, v7.8H, v14.8H
    mul v30.8H, v12.8H, v14.8H
    mls v7.8H, v10.8H, v18.8H
    mls v30.8H, v16.8H, v18.8H
    sub v7.8H, v11.8H, v7.8H
    sub v30.8H, v13.8H, v30.8H
    zip1 v0.2d, v7.2d, v30.2d
    movi v2.8h, #9
    sqrdmulh v1.8h, v0.8h, v2.8h
    mls v0.8h, v1.8h, v18.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v18.16b
    add v0.8h, v0.8h, v1.8h
    ushr v2.8h, v18.8h, #1
    cmgt v1.8h, v0.8h, v2.8h
    and v1.16b, v1.16b, v18.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #216]
    umov w13, v0.h[1]
    strh w13, [x0, #222]
    umov w13, v0.h[2]
    strh w13, [x0, #228]
    umov w13, v0.h[3]
    strh w13, [x0, #234]
    umov w13, v0.h[4]
    strh w13, [x0, #270]
    umov w13, v0.h[5]
    strh w13, [x0, #276]
    umov w13, v0.h[6]
    strh w13, [x0, #282]
    umov w13, v0.h[7]
    strh w13, [x0, #288]
    orr v11.16B, v15.16B, v15.16B
    orr v13.16B, v23.16B, v23.16B
    ext v7.16B, v15.16B, v15.16B, #8
    ext v30.16B, v23.16B, v23.16B, #8
    sub v7.8H, v7.8H, v11.8H
    sub v14.8H, v30.8H, v13.8H
    mov w13, #63902
    dup v10.8H, w13
    mov w13, #50048
    dup v30.8H, w13
    sqrdmulh v16.8H, v7.8H, v30.8H
    sqrdmulh v30.8H, v14.8H, v30.8H
    mul v7.8H, v7.8H, v10.8H
    mul v12.8H, v14.8H, v10.8H
    mls v7.8H, v16.8H, v18.8H
    mls v12.8H, v30.8H, v18.8H
    zip1 v0.2d, v7.2d, v12.2d
    movi v2.8h, #9
    sqrdmulh v1.8h, v0.8h, v2.8h
    mls v0.8h, v1.8h, v18.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v18.16b
    add v0.8h, v0.8h, v1.8h
    ushr v2.8h, v18.8h, #1
    cmgt v1.8h, v0.8h, v2.8h
    and v1.16b, v1.16b, v18.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #1188]
    umov w13, v0.h[1]
    strh w13, [x0, #1194]
    umov w13, v0.h[2]
    strh w13, [x0, #1200]
    umov w13, v0.h[3]
    strh w13, [x0, #1206]
    umov w13, v0.h[4]
    strh w13, [x0, #1242]
    umov w13, v0.h[5]
    strh w13, [x0, #1248]
    umov w13, v0.h[6]
    strh w13, [x0, #1254]
    umov w13, v0.h[7]
    strh w13, [x0, #1260]
    mov w13, #64814
    dup v14.8H, w13
    mov w13, #58692
    dup v30.8H, w13
    sqrdmulh v10.8H, v7.8H, v30.8H
    sqrdmulh v16.8H, v12.8H, v30.8H
    mul v7.8H, v7.8H, v14.8H
    mul v30.8H, v12.8H, v14.8H
    mls v7.8H, v10.8H, v18.8H
    mls v30.8H, v16.8H, v18.8H
    sub v7.8H, v11.8H, v7.8H
    sub v30.8H, v13.8H, v30.8H
    zip1 v0.2d, v7.2d, v30.2d
    movi v2.8h, #9
    sqrdmulh v1.8h, v0.8h, v2.8h
    mls v0.8h, v1.8h, v18.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v18.16b
    add v0.8h, v0.8h, v1.8h
    ushr v2.8h, v18.8h, #1
    cmgt v1.8h, v0.8h, v2.8h
    and v1.16b, v1.16b, v18.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #324]
    umov w13, v0.h[1]
    strh w13, [x0, #330]
    umov w13, v0.h[2]
    strh w13, [x0, #336]
    umov w13, v0.h[3]
    strh w13, [x0, #342]
    umov w13, v0.h[4]
    strh w13, [x0, #378]
    umov w13, v0.h[5]
    strh w13, [x0, #384]
    umov w13, v0.h[6]
    strh w13, [x0, #390]
    umov w13, v0.h[7]
    strh w13, [x0, #396]
    ldr q30, [x4, #272]
    sqrdmulh v13.8H, v8.8H, v30.8H
    ldr q30, [x4, #304]
    sqrdmulh v12.8H, v24.8H, v30.8H
    ldr q30, [x4, #336]
    sqrdmulh v14.8H, v21.8H, v30.8H
    ldr q30, [x4, #368]
    sqrdmulh v10.8H, v20.8H, v30.8H
    ldr q30, [x4, #256]
    mul v7.8H, v8.8H, v30.8H
    ldr q30, [x4, #288]
    mul v16.8H, v24.8H, v30.8H
    ldr q30, [x4, #320]
    mul v15.8H, v21.8H, v30.8H
    ldr q30, [x4, #352]
    mul v23.8H, v20.8H, v30.8H
    mls v7.8H, v13.8H, v18.8H
    mls v16.8H, v12.8H, v18.8H
    mls v15.8H, v14.8H, v18.8H
    mls v23.8H, v10.8H, v18.8H
    orr v11.16B, v7.16B, v7.16B
    orr v13.16B, v16.16B, v16.16B
    ext v7.16B, v7.16B, v7.16B, #8
    ext v30.16B, v16.16B, v16.16B, #8
    sub v7.8H, v7.8H, v11.8H
    sub v14.8H, v30.8H, v13.8H
    mov w13, #63902
    dup v10.8H, w13
    mov w13, #50048
    dup v30.8H, w13
    sqrdmulh v16.8H, v7.8H, v30.8H
    sqrdmulh v30.8H, v14.8H, v30.8H
    mul v7.8H, v7.8H, v10.8H
    mul v12.8H, v14.8H, v10.8H
    mls v7.8H, v16.8H, v18.8H
    mls v12.8H, v30.8H, v18.8H
    zip1 v0.2d, v7.2d, v12.2d
    movi v2.8h, #9
    sqrdmulh v1.8h, v0.8h, v2.8h
    mls v0.8h, v1.8h, v18.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v18.16b
    add v0.8h, v0.8h, v1.8h
    ushr v2.8h, v18.8h, #1
    cmgt v1.8h, v0.8h, v2.8h
    and v1.16b, v1.16b, v18.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #1296]
    umov w13, v0.h[1]
    strh w13, [x0, #1302]
    umov w13, v0.h[2]
    strh w13, [x0, #1308]
    umov w13, v0.h[3]
    strh w13, [x0, #1314]
    umov w13, v0.h[4]
    strh w13, [x0, #1350]
    umov w13, v0.h[5]
    strh w13, [x0, #1356]
    umov w13, v0.h[6]
    strh w13, [x0, #1362]
    umov w13, v0.h[7]
    strh w13, [x0, #1368]
    mov w13, #64814
    dup v14.8H, w13
    mov w13, #58692
    dup v30.8H, w13
    sqrdmulh v10.8H, v7.8H, v30.8H
    sqrdmulh v16.8H, v12.8H, v30.8H
    mul v7.8H, v7.8H, v14.8H
    mul v30.8H, v12.8H, v14.8H
    mls v7.8H, v10.8H, v18.8H
    mls v30.8H, v16.8H, v18.8H
    sub v7.8H, v11.8H, v7.8H
    sub v30.8H, v13.8H, v30.8H
    zip1 v0.2d, v7.2d, v30.2d
    movi v2.8h, #9
    sqrdmulh v1.8h, v0.8h, v2.8h
    mls v0.8h, v1.8h, v18.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v18.16b
    add v0.8h, v0.8h, v1.8h
    ushr v2.8h, v18.8h, #1
    cmgt v1.8h, v0.8h, v2.8h
    and v1.16b, v1.16b, v18.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #432]
    umov w13, v0.h[1]
    strh w13, [x0, #438]
    umov w13, v0.h[2]
    strh w13, [x0, #444]
    umov w13, v0.h[3]
    strh w13, [x0, #450]
    umov w13, v0.h[4]
    strh w13, [x0, #486]
    umov w13, v0.h[5]
    strh w13, [x0, #492]
    umov w13, v0.h[6]
    strh w13, [x0, #498]
    umov w13, v0.h[7]
    strh w13, [x0, #504]
    orr v11.16B, v15.16B, v15.16B
    orr v13.16B, v23.16B, v23.16B
    ext v7.16B, v15.16B, v15.16B, #8
    ext v30.16B, v23.16B, v23.16B, #8
    sub v7.8H, v7.8H, v11.8H
    sub v14.8H, v30.8H, v13.8H
    mov w13, #63902
    dup v10.8H, w13
    mov w13, #50048
    dup v30.8H, w13
    sqrdmulh v16.8H, v7.8H, v30.8H
    sqrdmulh v30.8H, v14.8H, v30.8H
    mul v7.8H, v7.8H, v10.8H
    mul v12.8H, v14.8H, v10.8H
    mls v7.8H, v16.8H, v18.8H
    mls v12.8H, v30.8H, v18.8H
    zip1 v0.2d, v7.2d, v12.2d
    movi v2.8h, #9
    sqrdmulh v1.8h, v0.8h, v2.8h
    mls v0.8h, v1.8h, v18.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v18.16b
    add v0.8h, v0.8h, v1.8h
    ushr v2.8h, v18.8h, #1
    cmgt v1.8h, v0.8h, v2.8h
    and v1.16b, v1.16b, v18.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #1404]
    umov w13, v0.h[1]
    strh w13, [x0, #1410]
    umov w13, v0.h[2]
    strh w13, [x0, #1416]
    umov w13, v0.h[3]
    strh w13, [x0, #1422]
    umov w13, v0.h[4]
    strh w13, [x0, #1458]
    umov w13, v0.h[5]
    strh w13, [x0, #1464]
    umov w13, v0.h[6]
    strh w13, [x0, #1470]
    umov w13, v0.h[7]
    strh w13, [x0, #1476]
    mov w13, #64814
    dup v14.8H, w13
    mov w13, #58692
    dup v30.8H, w13
    sqrdmulh v10.8H, v7.8H, v30.8H
    sqrdmulh v16.8H, v12.8H, v30.8H
    mul v7.8H, v7.8H, v14.8H
    mul v30.8H, v12.8H, v14.8H
    mls v7.8H, v10.8H, v18.8H
    mls v30.8H, v16.8H, v18.8H
    sub v7.8H, v11.8H, v7.8H
    sub v30.8H, v13.8H, v30.8H
    zip1 v0.2d, v7.2d, v30.2d
    movi v2.8h, #9
    sqrdmulh v1.8h, v0.8h, v2.8h
    mls v0.8h, v1.8h, v18.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v18.16b
    add v0.8h, v0.8h, v1.8h
    ushr v2.8h, v18.8h, #1
    cmgt v1.8h, v0.8h, v2.8h
    and v1.16b, v1.16b, v18.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #540]
    umov w13, v0.h[1]
    strh w13, [x0, #546]
    umov w13, v0.h[2]
    strh w13, [x0, #552]
    umov w13, v0.h[3]
    strh w13, [x0, #558]
    umov w13, v0.h[4]
    strh w13, [x0, #594]
    umov w13, v0.h[5]
    strh w13, [x0, #600]
    umov w13, v0.h[6]
    strh w13, [x0, #606]
    umov w13, v0.h[7]
    strh w13, [x0, #612]
    ldr q30, [x4, #400]
    sqrdmulh v13.8H, v29.8H, v30.8H
    ldr q30, [x4, #432]
    sqrdmulh v12.8H, v9.8H, v30.8H
    ldr q30, [x4, #464]
    sqrdmulh v14.8H, v4.8H, v30.8H
    ldr q30, [x4, #496]
    sqrdmulh v10.8H, v5.8H, v30.8H
    ldr q30, [x4, #384]
    mul v7.8H, v29.8H, v30.8H
    ldr q30, [x4, #416]
    mul v16.8H, v9.8H, v30.8H
    ldr q30, [x4, #448]
    mul v15.8H, v4.8H, v30.8H
    ldr q30, [x4, #480]
    mul v23.8H, v5.8H, v30.8H
    mls v7.8H, v13.8H, v18.8H
    mls v16.8H, v12.8H, v18.8H
    mls v15.8H, v14.8H, v18.8H
    mls v23.8H, v10.8H, v18.8H
    orr v11.16B, v7.16B, v7.16B
    orr v13.16B, v16.16B, v16.16B
    ext v7.16B, v7.16B, v7.16B, #8
    ext v30.16B, v16.16B, v16.16B, #8
    sub v7.8H, v7.8H, v11.8H
    sub v14.8H, v30.8H, v13.8H
    mov w13, #63902
    dup v10.8H, w13
    mov w13, #50048
    dup v30.8H, w13
    sqrdmulh v16.8H, v7.8H, v30.8H
    sqrdmulh v30.8H, v14.8H, v30.8H
    mul v7.8H, v7.8H, v10.8H
    mul v12.8H, v14.8H, v10.8H
    mls v7.8H, v16.8H, v18.8H
    mls v12.8H, v30.8H, v18.8H
    zip1 v0.2d, v7.2d, v12.2d
    movi v2.8h, #9
    sqrdmulh v1.8h, v0.8h, v2.8h
    mls v0.8h, v1.8h, v18.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v18.16b
    add v0.8h, v0.8h, v1.8h
    ushr v2.8h, v18.8h, #1
    cmgt v1.8h, v0.8h, v2.8h
    and v1.16b, v1.16b, v18.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #1512]
    umov w13, v0.h[1]
    strh w13, [x0, #1518]
    umov w13, v0.h[2]
    strh w13, [x0, #1524]
    umov w13, v0.h[3]
    strh w13, [x0, #1530]
    umov w13, v0.h[4]
    strh w13, [x0, #1566]
    umov w13, v0.h[5]
    strh w13, [x0, #1572]
    umov w13, v0.h[6]
    strh w13, [x0, #1578]
    umov w13, v0.h[7]
    strh w13, [x0, #1584]
    mov w13, #64814
    dup v14.8H, w13
    mov w13, #58692
    dup v30.8H, w13
    sqrdmulh v10.8H, v7.8H, v30.8H
    sqrdmulh v16.8H, v12.8H, v30.8H
    mul v7.8H, v7.8H, v14.8H
    mul v30.8H, v12.8H, v14.8H
    mls v7.8H, v10.8H, v18.8H
    mls v30.8H, v16.8H, v18.8H
    sub v7.8H, v11.8H, v7.8H
    sub v30.8H, v13.8H, v30.8H
    zip1 v0.2d, v7.2d, v30.2d
    movi v2.8h, #9
    sqrdmulh v1.8h, v0.8h, v2.8h
    mls v0.8h, v1.8h, v18.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v18.16b
    add v0.8h, v0.8h, v1.8h
    ushr v2.8h, v18.8h, #1
    cmgt v1.8h, v0.8h, v2.8h
    and v1.16b, v1.16b, v18.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #648]
    umov w13, v0.h[1]
    strh w13, [x0, #654]
    umov w13, v0.h[2]
    strh w13, [x0, #660]
    umov w13, v0.h[3]
    strh w13, [x0, #666]
    umov w13, v0.h[4]
    strh w13, [x0, #702]
    umov w13, v0.h[5]
    strh w13, [x0, #708]
    umov w13, v0.h[6]
    strh w13, [x0, #714]
    umov w13, v0.h[7]
    strh w13, [x0, #720]
    orr v11.16B, v15.16B, v15.16B
    orr v13.16B, v23.16B, v23.16B
    ext v7.16B, v15.16B, v15.16B, #8
    ext v30.16B, v23.16B, v23.16B, #8
    sub v7.8H, v7.8H, v11.8H
    sub v14.8H, v30.8H, v13.8H
    mov w13, #63902
    dup v10.8H, w13
    mov w13, #50048
    dup v30.8H, w13
    sqrdmulh v16.8H, v7.8H, v30.8H
    sqrdmulh v30.8H, v14.8H, v30.8H
    mul v7.8H, v7.8H, v10.8H
    mul v12.8H, v14.8H, v10.8H
    mls v7.8H, v16.8H, v18.8H
    mls v12.8H, v30.8H, v18.8H
    zip1 v0.2d, v7.2d, v12.2d
    movi v2.8h, #9
    sqrdmulh v1.8h, v0.8h, v2.8h
    mls v0.8h, v1.8h, v18.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v18.16b
    add v0.8h, v0.8h, v1.8h
    ushr v2.8h, v18.8h, #1
    cmgt v1.8h, v0.8h, v2.8h
    and v1.16b, v1.16b, v18.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #1620]
    umov w13, v0.h[1]
    strh w13, [x0, #1626]
    umov w13, v0.h[2]
    strh w13, [x0, #1632]
    umov w13, v0.h[3]
    strh w13, [x0, #1638]
    umov w13, v0.h[4]
    strh w13, [x0, #1674]
    umov w13, v0.h[5]
    strh w13, [x0, #1680]
    umov w13, v0.h[6]
    strh w13, [x0, #1686]
    umov w13, v0.h[7]
    strh w13, [x0, #1692]
    mov w13, #64814
    dup v14.8H, w13
    mov w13, #58692
    dup v30.8H, w13
    sqrdmulh v10.8H, v7.8H, v30.8H
    sqrdmulh v16.8H, v12.8H, v30.8H
    mul v7.8H, v7.8H, v14.8H
    mul v30.8H, v12.8H, v14.8H
    mls v7.8H, v10.8H, v18.8H
    mls v30.8H, v16.8H, v18.8H
    sub v7.8H, v11.8H, v7.8H
    sub v30.8H, v13.8H, v30.8H
    zip1 v0.2d, v7.2d, v30.2d
    movi v2.8h, #9
    sqrdmulh v1.8h, v0.8h, v2.8h
    mls v0.8h, v1.8h, v18.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v18.16b
    add v0.8h, v0.8h, v1.8h
    ushr v2.8h, v18.8h, #1
    cmgt v1.8h, v0.8h, v2.8h
    and v1.16b, v1.16b, v18.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #756]
    umov w13, v0.h[1]
    strh w13, [x0, #762]
    umov w13, v0.h[2]
    strh w13, [x0, #768]
    umov w13, v0.h[3]
    strh w13, [x0, #774]
    umov w13, v0.h[4]
    strh w13, [x0, #810]
    umov w13, v0.h[5]
    strh w13, [x0, #816]
    umov w13, v0.h[6]
    strh w13, [x0, #822]
    umov w17, v0.h[7]
    strh w17, [x0, #828]
lazy_i16_slothy_end:
    ret
