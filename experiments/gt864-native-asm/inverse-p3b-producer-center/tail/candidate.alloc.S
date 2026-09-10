.text
.global lazy_itail
lazy_itail:
// P3-B inherited P3-A physical allocation with dead-register reuse; final stores are centered in producer registers.
// live-in: x0 output, x1 packed scratch, x3 stage table, x4 scale table, and documented vector inputs.
// live-out: x0 and the centered natural-order coefficient output in memory.
// coefficient range: I9 <= 3456; I16 <= 30939; terminal <= 6912; stored centered <= 1728.
// reserved physical registers: x18-x30, sp, and xzr; no stack spill is permitted.
lazy_itail_slothy_start:
    mov w5, #3457
    dup v10.8H, w5
    ldr q8, [x1, #0]
    ldr q28, [x1, #16]
    ldr q3, [x1, #32]
    ldr q20, [x1, #48]
    ldr q0, [x1, #64]
    ldr q21, [x1, #80]
    ldr q5, [x1, #96]
    ldr q16, [x1, #112]
    ldr q6, [x1, #128]
    ldr q15, [x1, #144]
    ldr q29, [x1, #160]
    ldr q24, [x1, #176]
    ldr q14, [x1, #192]
    ldr q23, [x1, #208]
    ldr q1, [x1, #224]
    ldr q17, [x1, #240]
    orr v19.16B, v8.16B, v8.16B
    add v30.8H, v8.8H, v6.8H
    sub v22.8H, v19.8H, v6.8H
    orr v19.16B, v0.16B, v0.16B
    add v13.8H, v0.8H, v14.8H
    sub v26.8H, v19.8H, v14.8H
    orr v19.16B, v3.16B, v3.16B
    add v8.8H, v3.8H, v29.8H
    sub v2.8H, v19.8H, v29.8H
    orr v19.16B, v5.16B, v5.16B
    add v5.8H, v5.8H, v1.8H
    sub v6.8H, v19.8H, v1.8H
    orr v19.16B, v28.16B, v28.16B
    add v3.8H, v28.8H, v15.8H
    sub v0.8H, v19.8H, v15.8H
    orr v19.16B, v21.16B, v21.16B
    add v21.8H, v21.8H, v23.8H
    sub v15.8H, v19.8H, v23.8H
    orr v19.16B, v20.16B, v20.16B
    add v29.8H, v20.8H, v24.8H
    sub v24.8H, v19.8H, v24.8H
    orr v19.16B, v16.16B, v16.16B
    add v14.8H, v16.8H, v17.8H
    sub v23.8H, v19.8H, v17.8H
    ldr q1, [x3, #32]
    sqrdmulh v17.8H, v26.8H, v1.H[3]
    sqrdmulh v19.8H, v6.8H, v1.H[7]
    mul v18.8H, v26.8H, v1.H[2]
    mul v25.8H, v6.8H, v1.H[6]
    mls v18.8H, v17.8H, v10.8H
    mls v25.8H, v19.8H, v10.8H
    orr v19.16B, v30.16B, v30.16B
    add v16.8H, v30.8H, v13.8H
    sub v30.8H, v19.8H, v13.8H
    orr v19.16B, v22.16B, v22.16B
    add v22.8H, v22.8H, v18.8H
    sub v13.8H, v19.8H, v18.8H
    orr v19.16B, v8.16B, v8.16B
    add v26.8H, v8.8H, v5.8H
    sub v8.8H, v19.8H, v5.8H
    orr v19.16B, v2.16B, v2.16B
    add v5.8H, v2.8H, v25.8H
    sub v6.8H, v19.8H, v25.8H
    ldr q1, [x3, #48]
    sqrdmulh v17.8H, v15.8H, v1.H[3]
    sqrdmulh v19.8H, v23.8H, v1.H[7]
    mul v9.8H, v15.8H, v1.H[2]
    mul v31.8H, v23.8H, v1.H[6]
    mls v9.8H, v17.8H, v10.8H
    mls v31.8H, v19.8H, v10.8H
    orr v19.16B, v3.16B, v3.16B
    add v3.8H, v3.8H, v21.8H
    sub v4.8H, v19.8H, v21.8H
    orr v19.16B, v0.16B, v0.16B
    add v0.8H, v0.8H, v9.8H
    sub v21.8H, v19.8H, v9.8H
    orr v19.16B, v29.16B, v29.16B
    add v15.8H, v29.8H, v14.8H
    sub v29.8H, v19.8H, v14.8H
    orr v19.16B, v24.16B, v24.16B
    add v24.8H, v24.8H, v31.8H
    sub v23.8H, v19.8H, v31.8H
    ldr q14, [x3, #64]
    sqrdmulh v1.8H, v5.8H, v14.H[3]
    sqrdmulh v17.8H, v8.8H, v14.H[5]
    sqrdmulh v19.8H, v6.8H, v14.H[7]
    mul v28.8H, v5.8H, v14.H[2]
    mul v20.8H, v8.8H, v14.H[4]
    mul v2.8H, v6.8H, v14.H[6]
    mls v28.8H, v1.8H, v10.8H
    mls v20.8H, v17.8H, v10.8H
    mls v2.8H, v19.8H, v10.8H
    orr v19.16B, v16.16B, v16.16B
    add v16.8H, v16.8H, v26.8H
    sub v25.8H, v19.8H, v26.8H
    orr v19.16B, v22.16B, v22.16B
    add v22.8H, v22.8H, v28.8H
    sub v27.8H, v19.8H, v28.8H
    orr v19.16B, v30.16B, v30.16B
    add v5.8H, v30.8H, v20.8H
    sub v9.8H, v19.8H, v20.8H
    orr v19.16B, v13.16B, v13.16B
    add v6.8H, v13.8H, v2.8H
    sub v11.8H, v19.8H, v2.8H
    ldr q14, [x3, #80]
    sqrdmulh v1.8H, v24.8H, v14.H[3]
    sqrdmulh v17.8H, v29.8H, v14.H[5]
    sqrdmulh v19.8H, v23.8H, v14.H[7]
    mul v30.8H, v24.8H, v14.H[2]
    mul v2.8H, v29.8H, v14.H[4]
    mul v13.8H, v23.8H, v14.H[6]
    mls v30.8H, v1.8H, v10.8H
    mls v2.8H, v17.8H, v10.8H
    mls v13.8H, v19.8H, v10.8H
    orr v19.16B, v3.16B, v3.16B
    add v26.8H, v3.8H, v15.8H
    sub v8.8H, v19.8H, v15.8H
    orr v19.16B, v0.16B, v0.16B
    add v29.8H, v0.8H, v30.8H
    sub v3.8H, v19.8H, v30.8H
    orr v19.16B, v4.16B, v4.16B
    add v24.8H, v4.8H, v2.8H
    sub v0.8H, v19.8H, v2.8H
    orr v19.16B, v21.16B, v21.16B
    add v23.8H, v21.8H, v13.8H
    sub v21.8H, v19.8H, v13.8H
    ldr q15, [x3, #96]
    sqrdmulh v14.8H, v26.8H, v15.H[1]
    sqrdmulh v1.8H, v29.8H, v15.H[3]
    sqrdmulh v17.8H, v24.8H, v15.H[5]
    sqrdmulh v19.8H, v23.8H, v15.H[7]
    mul v29.8H, v29.8H, v15.H[2]
    mul v24.8H, v24.8H, v15.H[4]
    mul v23.8H, v23.8H, v15.H[6]
    mls v26.8H, v14.8H, v10.8H
    mls v29.8H, v1.8H, v10.8H
    mls v24.8H, v17.8H, v10.8H
    mls v23.8H, v19.8H, v10.8H
    orr v19.16B, v16.16B, v16.16B
    add v7.8H, v16.8H, v26.8H
    sub v31.8H, v19.8H, v26.8H
    orr v19.16B, v22.16B, v22.16B
    add v4.8H, v22.8H, v29.8H
    sub v28.8H, v19.8H, v29.8H
    orr v19.16B, v5.16B, v5.16B
    add v5.8H, v5.8H, v24.8H
    sub v20.8H, v19.8H, v24.8H
    orr v19.16B, v6.16B, v6.16B
    add v16.8H, v6.8H, v23.8H
    sub v30.8H, v19.8H, v23.8H
    ldr q6, [x3, #112]
    sqrdmulh v15.8H, v8.8H, v6.H[1]
    sqrdmulh v29.8H, v3.8H, v6.H[3]
    sqrdmulh v24.8H, v0.8H, v6.H[5]
    sqrdmulh v19.8H, v21.8H, v6.H[7]
    mul v14.8H, v8.8H, v6.H[0]
    mul v23.8H, v3.8H, v6.H[2]
    mul v1.8H, v0.8H, v6.H[4]
    mul v17.8H, v21.8H, v6.H[6]
    mls v14.8H, v15.8H, v10.8H
    mls v23.8H, v29.8H, v10.8H
    mls v1.8H, v24.8H, v10.8H
    mls v17.8H, v19.8H, v10.8H
    orr v19.16B, v25.16B, v25.16B
    add v22.8H, v25.8H, v14.8H
    sub v2.8H, v19.8H, v14.8H
    orr v19.16B, v27.16B, v27.16B
    add v13.8H, v27.8H, v23.8H
    sub v26.8H, v19.8H, v23.8H
    orr v19.16B, v9.16B, v9.16B
    add v8.8H, v9.8H, v1.8H
    sub v3.8H, v19.8H, v1.8H
    orr v19.16B, v11.16B, v11.16B
    add v0.8H, v11.8H, v17.8H
    sub v21.8H, v19.8H, v17.8H
    ldr q19, [x4, #16]
    sqrdmulh v29.8H, v7.8H, v19.8H
    ldr q19, [x4, #48]
    sqrdmulh v24.8H, v4.8H, v19.8H
    ldr q19, [x4, #80]
    sqrdmulh v14.8H, v5.8H, v19.8H
    ldr q19, [x4, #112]
    sqrdmulh v23.8H, v16.8H, v19.8H
    ldr q19, [x4, #0]
    mul v17.8H, v7.8H, v19.8H
    ldr q19, [x4, #32]
    mul v1.8H, v4.8H, v19.8H
    ldr q19, [x4, #64]
    mul v5.8H, v5.8H, v19.8H
    ldr q19, [x4, #96]
    mul v6.8H, v16.8H, v19.8H
    mls v17.8H, v29.8H, v10.8H
    mls v1.8H, v24.8H, v10.8H
    mls v5.8H, v14.8H, v10.8H
    mls v6.8H, v23.8H, v10.8H
    orr v15.16B, v17.16B, v17.16B
    orr v29.16B, v1.16B, v1.16B
    ext v17.16B, v17.16B, v17.16B, #6
    ext v19.16B, v1.16B, v1.16B, #6
    sub v17.8H, v17.8H, v15.8H
    sub v14.8H, v19.8H, v29.8H
    mov w14, #63902
    dup v23.8H, w14
    mov w16, #50048
    dup v19.8H, w16
    sqrdmulh v1.8H, v17.8H, v19.8H
    sqrdmulh v19.8H, v14.8H, v19.8H
    mul v17.8H, v17.8H, v23.8H
    mul v24.8H, v14.8H, v23.8H
    mls v17.8H, v1.8H, v10.8H
    mls v24.8H, v19.8H, v10.8H
    zip1 v1.2d, v17.2d, v24.2d
    movi v7.8h, #9
    sqrdmulh v4.8h, v1.8h, v7.8h
    mls v1.8h, v4.8h, v10.8h
    sshr v4.8h, v1.8h, #15
    and v4.16b, v4.16b, v10.16b
    add v1.8h, v1.8h, v4.8h
    ushr v7.8h, v10.8h, #1
    cmgt v4.8h, v1.8h, v7.8h
    and v4.16b, v4.16b, v10.16b
    sub v1.8h, v1.8h, v4.8h
    umov w17, v1.h[0]
    strh w17, [x0, #864]
    umov w9, v1.h[1]
    strh w9, [x0, #866]
    umov w7, v1.h[2]
    strh w7, [x0, #868]
    umov w8, v1.h[4]
    strh w8, [x0, #918]
    umov w2, v1.h[5]
    strh w2, [x0, #920]
    umov w6, v1.h[6]
    strh w6, [x0, #922]
    mov w12, #64814
    dup v14.8H, w12
    mov w11, #58692
    dup v19.8H, w11
    sqrdmulh v23.8H, v17.8H, v19.8H
    sqrdmulh v1.8H, v24.8H, v19.8H
    mul v17.8H, v17.8H, v14.8H
    mul v19.8H, v24.8H, v14.8H
    mls v17.8H, v23.8H, v10.8H
    mls v19.8H, v1.8H, v10.8H
    sub v17.8H, v15.8H, v17.8H
    sub v19.8H, v29.8H, v19.8H
    zip1 v1.2d, v17.2d, v19.2d
    movi v7.8h, #9
    sqrdmulh v4.8h, v1.8h, v7.8h
    mls v1.8h, v4.8h, v10.8h
    sshr v4.8h, v1.8h, #15
    and v4.16b, v4.16b, v10.16b
    add v1.8h, v1.8h, v4.8h
    ushr v7.8h, v10.8h, #1
    cmgt v4.8h, v1.8h, v7.8h
    and v4.16b, v4.16b, v10.16b
    sub v1.8h, v1.8h, v4.8h
    umov w15, v1.h[0]
    strh w15, [x0, #0]
    umov w13, v1.h[1]
    strh w13, [x0, #2]
    umov w13, v1.h[2]
    strh w13, [x0, #4]
    umov w13, v1.h[4]
    strh w13, [x0, #54]
    umov w13, v1.h[5]
    strh w13, [x0, #56]
    umov w13, v1.h[6]
    strh w13, [x0, #58]
    orr v15.16B, v5.16B, v5.16B
    orr v29.16B, v6.16B, v6.16B
    ext v17.16B, v5.16B, v5.16B, #6
    ext v19.16B, v6.16B, v6.16B, #6
    sub v17.8H, v17.8H, v15.8H
    sub v14.8H, v19.8H, v29.8H
    mov w13, #63902
    dup v23.8H, w13
    mov w13, #50048
    dup v19.8H, w13
    sqrdmulh v1.8H, v17.8H, v19.8H
    sqrdmulh v19.8H, v14.8H, v19.8H
    mul v17.8H, v17.8H, v23.8H
    mul v24.8H, v14.8H, v23.8H
    mls v17.8H, v1.8H, v10.8H
    mls v24.8H, v19.8H, v10.8H
    zip1 v1.2d, v17.2d, v24.2d
    movi v5.8h, #9
    sqrdmulh v4.8h, v1.8h, v5.8h
    mls v1.8h, v4.8h, v10.8h
    sshr v4.8h, v1.8h, #15
    and v4.16b, v4.16b, v10.16b
    add v1.8h, v1.8h, v4.8h
    ushr v5.8h, v10.8h, #1
    cmgt v4.8h, v1.8h, v5.8h
    and v4.16b, v4.16b, v10.16b
    sub v1.8h, v1.8h, v4.8h
    umov w13, v1.h[0]
    strh w13, [x0, #972]
    umov w13, v1.h[1]
    strh w13, [x0, #974]
    umov w13, v1.h[2]
    strh w13, [x0, #976]
    umov w13, v1.h[4]
    strh w13, [x0, #1026]
    umov w13, v1.h[5]
    strh w13, [x0, #1028]
    umov w13, v1.h[6]
    strh w13, [x0, #1030]
    mov w13, #64814
    dup v14.8H, w13
    mov w13, #58692
    dup v19.8H, w13
    sqrdmulh v23.8H, v17.8H, v19.8H
    sqrdmulh v1.8H, v24.8H, v19.8H
    mul v17.8H, v17.8H, v14.8H
    mul v19.8H, v24.8H, v14.8H
    mls v17.8H, v23.8H, v10.8H
    mls v19.8H, v1.8H, v10.8H
    sub v17.8H, v15.8H, v17.8H
    sub v19.8H, v29.8H, v19.8H
    zip1 v1.2d, v17.2d, v19.2d
    movi v5.8h, #9
    sqrdmulh v4.8h, v1.8h, v5.8h
    mls v1.8h, v4.8h, v10.8h
    sshr v4.8h, v1.8h, #15
    and v4.16b, v4.16b, v10.16b
    add v1.8h, v1.8h, v4.8h
    ushr v5.8h, v10.8h, #1
    cmgt v4.8h, v1.8h, v5.8h
    and v4.16b, v4.16b, v10.16b
    sub v1.8h, v1.8h, v4.8h
    umov w13, v1.h[0]
    strh w13, [x0, #108]
    umov w13, v1.h[1]
    strh w13, [x0, #110]
    umov w13, v1.h[2]
    strh w13, [x0, #112]
    umov w13, v1.h[4]
    strh w13, [x0, #162]
    umov w13, v1.h[5]
    strh w13, [x0, #164]
    umov w13, v1.h[6]
    strh w13, [x0, #166]
    ldr q19, [x4, #144]
    sqrdmulh v29.8H, v22.8H, v19.8H
    ldr q19, [x4, #176]
    sqrdmulh v24.8H, v13.8H, v19.8H
    ldr q19, [x4, #208]
    sqrdmulh v14.8H, v8.8H, v19.8H
    ldr q19, [x4, #240]
    sqrdmulh v23.8H, v0.8H, v19.8H
    ldr q19, [x4, #128]
    mul v17.8H, v22.8H, v19.8H
    ldr q19, [x4, #160]
    mul v1.8H, v13.8H, v19.8H
    ldr q19, [x4, #192]
    mul v5.8H, v8.8H, v19.8H
    ldr q19, [x4, #224]
    mul v6.8H, v0.8H, v19.8H
    mls v17.8H, v29.8H, v10.8H
    mls v1.8H, v24.8H, v10.8H
    mls v5.8H, v14.8H, v10.8H
    mls v6.8H, v23.8H, v10.8H
    orr v15.16B, v17.16B, v17.16B
    orr v29.16B, v1.16B, v1.16B
    ext v17.16B, v17.16B, v17.16B, #6
    ext v19.16B, v1.16B, v1.16B, #6
    sub v17.8H, v17.8H, v15.8H
    sub v14.8H, v19.8H, v29.8H
    mov w13, #63902
    dup v23.8H, w13
    mov w13, #50048
    dup v19.8H, w13
    sqrdmulh v1.8H, v17.8H, v19.8H
    sqrdmulh v19.8H, v14.8H, v19.8H
    mul v17.8H, v17.8H, v23.8H
    mul v24.8H, v14.8H, v23.8H
    mls v17.8H, v1.8H, v10.8H
    mls v24.8H, v19.8H, v10.8H
    zip1 v0.2d, v17.2d, v24.2d
    movi v4.8h, #9
    sqrdmulh v1.8h, v0.8h, v4.8h
    mls v0.8h, v1.8h, v10.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v10.16b
    add v0.8h, v0.8h, v1.8h
    ushr v4.8h, v10.8h, #1
    cmgt v1.8h, v0.8h, v4.8h
    and v1.16b, v1.16b, v10.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #1080]
    umov w13, v0.h[1]
    strh w13, [x0, #1082]
    umov w13, v0.h[2]
    strh w13, [x0, #1084]
    umov w13, v0.h[4]
    strh w13, [x0, #1134]
    umov w13, v0.h[5]
    strh w13, [x0, #1136]
    umov w13, v0.h[6]
    strh w13, [x0, #1138]
    mov w13, #64814
    dup v14.8H, w13
    mov w13, #58692
    dup v19.8H, w13
    sqrdmulh v23.8H, v17.8H, v19.8H
    sqrdmulh v1.8H, v24.8H, v19.8H
    mul v17.8H, v17.8H, v14.8H
    mul v19.8H, v24.8H, v14.8H
    mls v17.8H, v23.8H, v10.8H
    mls v19.8H, v1.8H, v10.8H
    sub v17.8H, v15.8H, v17.8H
    sub v19.8H, v29.8H, v19.8H
    zip1 v0.2d, v17.2d, v19.2d
    movi v4.8h, #9
    sqrdmulh v1.8h, v0.8h, v4.8h
    mls v0.8h, v1.8h, v10.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v10.16b
    add v0.8h, v0.8h, v1.8h
    ushr v4.8h, v10.8h, #1
    cmgt v1.8h, v0.8h, v4.8h
    and v1.16b, v1.16b, v10.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #216]
    umov w13, v0.h[1]
    strh w13, [x0, #218]
    umov w13, v0.h[2]
    strh w13, [x0, #220]
    umov w13, v0.h[4]
    strh w13, [x0, #270]
    umov w13, v0.h[5]
    strh w13, [x0, #272]
    umov w13, v0.h[6]
    strh w13, [x0, #274]
    orr v15.16B, v5.16B, v5.16B
    orr v29.16B, v6.16B, v6.16B
    ext v17.16B, v5.16B, v5.16B, #6
    ext v19.16B, v6.16B, v6.16B, #6
    sub v17.8H, v17.8H, v15.8H
    sub v14.8H, v19.8H, v29.8H
    mov w13, #63902
    dup v23.8H, w13
    mov w13, #50048
    dup v19.8H, w13
    sqrdmulh v1.8H, v17.8H, v19.8H
    sqrdmulh v19.8H, v14.8H, v19.8H
    mul v17.8H, v17.8H, v23.8H
    mul v24.8H, v14.8H, v23.8H
    mls v17.8H, v1.8H, v10.8H
    mls v24.8H, v19.8H, v10.8H
    zip1 v0.2d, v17.2d, v24.2d
    movi v4.8h, #9
    sqrdmulh v1.8h, v0.8h, v4.8h
    mls v0.8h, v1.8h, v10.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v10.16b
    add v0.8h, v0.8h, v1.8h
    ushr v4.8h, v10.8h, #1
    cmgt v1.8h, v0.8h, v4.8h
    and v1.16b, v1.16b, v10.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #1188]
    umov w13, v0.h[1]
    strh w13, [x0, #1190]
    umov w13, v0.h[2]
    strh w13, [x0, #1192]
    umov w13, v0.h[4]
    strh w13, [x0, #1242]
    umov w13, v0.h[5]
    strh w13, [x0, #1244]
    umov w13, v0.h[6]
    strh w13, [x0, #1246]
    mov w13, #64814
    dup v14.8H, w13
    mov w13, #58692
    dup v19.8H, w13
    sqrdmulh v23.8H, v17.8H, v19.8H
    sqrdmulh v1.8H, v24.8H, v19.8H
    mul v17.8H, v17.8H, v14.8H
    mul v19.8H, v24.8H, v14.8H
    mls v17.8H, v23.8H, v10.8H
    mls v19.8H, v1.8H, v10.8H
    sub v17.8H, v15.8H, v17.8H
    sub v19.8H, v29.8H, v19.8H
    zip1 v0.2d, v17.2d, v19.2d
    movi v4.8h, #9
    sqrdmulh v1.8h, v0.8h, v4.8h
    mls v0.8h, v1.8h, v10.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v10.16b
    add v0.8h, v0.8h, v1.8h
    ushr v4.8h, v10.8h, #1
    cmgt v1.8h, v0.8h, v4.8h
    and v1.16b, v1.16b, v10.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #324]
    umov w13, v0.h[1]
    strh w13, [x0, #326]
    umov w13, v0.h[2]
    strh w13, [x0, #328]
    umov w13, v0.h[4]
    strh w13, [x0, #378]
    umov w13, v0.h[5]
    strh w13, [x0, #380]
    umov w13, v0.h[6]
    strh w13, [x0, #382]
    ldr q19, [x4, #272]
    sqrdmulh v29.8H, v31.8H, v19.8H
    ldr q19, [x4, #304]
    sqrdmulh v24.8H, v28.8H, v19.8H
    ldr q19, [x4, #336]
    sqrdmulh v14.8H, v20.8H, v19.8H
    ldr q19, [x4, #368]
    sqrdmulh v23.8H, v30.8H, v19.8H
    ldr q19, [x4, #256]
    mul v17.8H, v31.8H, v19.8H
    ldr q19, [x4, #288]
    mul v1.8H, v28.8H, v19.8H
    ldr q19, [x4, #320]
    mul v5.8H, v20.8H, v19.8H
    ldr q19, [x4, #352]
    mul v6.8H, v30.8H, v19.8H
    mls v17.8H, v29.8H, v10.8H
    mls v1.8H, v24.8H, v10.8H
    mls v5.8H, v14.8H, v10.8H
    mls v6.8H, v23.8H, v10.8H
    orr v15.16B, v17.16B, v17.16B
    orr v29.16B, v1.16B, v1.16B
    ext v17.16B, v17.16B, v17.16B, #6
    ext v19.16B, v1.16B, v1.16B, #6
    sub v17.8H, v17.8H, v15.8H
    sub v14.8H, v19.8H, v29.8H
    mov w13, #63902
    dup v23.8H, w13
    mov w13, #50048
    dup v19.8H, w13
    sqrdmulh v1.8H, v17.8H, v19.8H
    sqrdmulh v19.8H, v14.8H, v19.8H
    mul v17.8H, v17.8H, v23.8H
    mul v24.8H, v14.8H, v23.8H
    mls v17.8H, v1.8H, v10.8H
    mls v24.8H, v19.8H, v10.8H
    zip1 v0.2d, v17.2d, v24.2d
    movi v4.8h, #9
    sqrdmulh v1.8h, v0.8h, v4.8h
    mls v0.8h, v1.8h, v10.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v10.16b
    add v0.8h, v0.8h, v1.8h
    ushr v4.8h, v10.8h, #1
    cmgt v1.8h, v0.8h, v4.8h
    and v1.16b, v1.16b, v10.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #1296]
    umov w13, v0.h[1]
    strh w13, [x0, #1298]
    umov w13, v0.h[2]
    strh w13, [x0, #1300]
    umov w13, v0.h[4]
    strh w13, [x0, #1350]
    umov w13, v0.h[5]
    strh w13, [x0, #1352]
    umov w13, v0.h[6]
    strh w13, [x0, #1354]
    mov w13, #64814
    dup v14.8H, w13
    mov w13, #58692
    dup v19.8H, w13
    sqrdmulh v23.8H, v17.8H, v19.8H
    sqrdmulh v1.8H, v24.8H, v19.8H
    mul v17.8H, v17.8H, v14.8H
    mul v19.8H, v24.8H, v14.8H
    mls v17.8H, v23.8H, v10.8H
    mls v19.8H, v1.8H, v10.8H
    sub v17.8H, v15.8H, v17.8H
    sub v19.8H, v29.8H, v19.8H
    zip1 v0.2d, v17.2d, v19.2d
    movi v4.8h, #9
    sqrdmulh v1.8h, v0.8h, v4.8h
    mls v0.8h, v1.8h, v10.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v10.16b
    add v0.8h, v0.8h, v1.8h
    ushr v4.8h, v10.8h, #1
    cmgt v1.8h, v0.8h, v4.8h
    and v1.16b, v1.16b, v10.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #432]
    umov w13, v0.h[1]
    strh w13, [x0, #434]
    umov w13, v0.h[2]
    strh w13, [x0, #436]
    umov w13, v0.h[4]
    strh w13, [x0, #486]
    umov w13, v0.h[5]
    strh w13, [x0, #488]
    umov w13, v0.h[6]
    strh w13, [x0, #490]
    orr v15.16B, v5.16B, v5.16B
    orr v29.16B, v6.16B, v6.16B
    ext v17.16B, v5.16B, v5.16B, #6
    ext v19.16B, v6.16B, v6.16B, #6
    sub v17.8H, v17.8H, v15.8H
    sub v14.8H, v19.8H, v29.8H
    mov w13, #63902
    dup v23.8H, w13
    mov w13, #50048
    dup v19.8H, w13
    sqrdmulh v1.8H, v17.8H, v19.8H
    sqrdmulh v19.8H, v14.8H, v19.8H
    mul v17.8H, v17.8H, v23.8H
    mul v24.8H, v14.8H, v23.8H
    mls v17.8H, v1.8H, v10.8H
    mls v24.8H, v19.8H, v10.8H
    zip1 v0.2d, v17.2d, v24.2d
    movi v4.8h, #9
    sqrdmulh v1.8h, v0.8h, v4.8h
    mls v0.8h, v1.8h, v10.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v10.16b
    add v0.8h, v0.8h, v1.8h
    ushr v4.8h, v10.8h, #1
    cmgt v1.8h, v0.8h, v4.8h
    and v1.16b, v1.16b, v10.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #1404]
    umov w13, v0.h[1]
    strh w13, [x0, #1406]
    umov w13, v0.h[2]
    strh w13, [x0, #1408]
    umov w13, v0.h[4]
    strh w13, [x0, #1458]
    umov w13, v0.h[5]
    strh w13, [x0, #1460]
    umov w13, v0.h[6]
    strh w13, [x0, #1462]
    mov w13, #64814
    dup v14.8H, w13
    mov w13, #58692
    dup v19.8H, w13
    sqrdmulh v23.8H, v17.8H, v19.8H
    sqrdmulh v1.8H, v24.8H, v19.8H
    mul v17.8H, v17.8H, v14.8H
    mul v19.8H, v24.8H, v14.8H
    mls v17.8H, v23.8H, v10.8H
    mls v19.8H, v1.8H, v10.8H
    sub v17.8H, v15.8H, v17.8H
    sub v19.8H, v29.8H, v19.8H
    zip1 v0.2d, v17.2d, v19.2d
    movi v4.8h, #9
    sqrdmulh v1.8h, v0.8h, v4.8h
    mls v0.8h, v1.8h, v10.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v10.16b
    add v0.8h, v0.8h, v1.8h
    ushr v4.8h, v10.8h, #1
    cmgt v1.8h, v0.8h, v4.8h
    and v1.16b, v1.16b, v10.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #540]
    umov w13, v0.h[1]
    strh w13, [x0, #542]
    umov w13, v0.h[2]
    strh w13, [x0, #544]
    umov w13, v0.h[4]
    strh w13, [x0, #594]
    umov w13, v0.h[5]
    strh w13, [x0, #596]
    umov w13, v0.h[6]
    strh w13, [x0, #598]
    ldr q19, [x4, #400]
    sqrdmulh v29.8H, v2.8H, v19.8H
    ldr q19, [x4, #432]
    sqrdmulh v24.8H, v26.8H, v19.8H
    ldr q19, [x4, #464]
    sqrdmulh v14.8H, v3.8H, v19.8H
    ldr q19, [x4, #496]
    sqrdmulh v23.8H, v21.8H, v19.8H
    ldr q19, [x4, #384]
    mul v17.8H, v2.8H, v19.8H
    ldr q19, [x4, #416]
    mul v1.8H, v26.8H, v19.8H
    ldr q19, [x4, #448]
    mul v5.8H, v3.8H, v19.8H
    ldr q19, [x4, #480]
    mul v6.8H, v21.8H, v19.8H
    mls v17.8H, v29.8H, v10.8H
    mls v1.8H, v24.8H, v10.8H
    mls v5.8H, v14.8H, v10.8H
    mls v6.8H, v23.8H, v10.8H
    orr v15.16B, v17.16B, v17.16B
    orr v29.16B, v1.16B, v1.16B
    ext v17.16B, v17.16B, v17.16B, #6
    ext v19.16B, v1.16B, v1.16B, #6
    sub v17.8H, v17.8H, v15.8H
    sub v14.8H, v19.8H, v29.8H
    mov w13, #63902
    dup v23.8H, w13
    mov w13, #50048
    dup v19.8H, w13
    sqrdmulh v1.8H, v17.8H, v19.8H
    sqrdmulh v19.8H, v14.8H, v19.8H
    mul v17.8H, v17.8H, v23.8H
    mul v24.8H, v14.8H, v23.8H
    mls v17.8H, v1.8H, v10.8H
    mls v24.8H, v19.8H, v10.8H
    zip1 v0.2d, v17.2d, v24.2d
    movi v2.8h, #9
    sqrdmulh v1.8h, v0.8h, v2.8h
    mls v0.8h, v1.8h, v10.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v10.16b
    add v0.8h, v0.8h, v1.8h
    ushr v2.8h, v10.8h, #1
    cmgt v1.8h, v0.8h, v2.8h
    and v1.16b, v1.16b, v10.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #1512]
    umov w13, v0.h[1]
    strh w13, [x0, #1514]
    umov w13, v0.h[2]
    strh w13, [x0, #1516]
    umov w13, v0.h[4]
    strh w13, [x0, #1566]
    umov w13, v0.h[5]
    strh w13, [x0, #1568]
    umov w13, v0.h[6]
    strh w13, [x0, #1570]
    mov w13, #64814
    dup v14.8H, w13
    mov w13, #58692
    dup v19.8H, w13
    sqrdmulh v23.8H, v17.8H, v19.8H
    sqrdmulh v1.8H, v24.8H, v19.8H
    mul v17.8H, v17.8H, v14.8H
    mul v19.8H, v24.8H, v14.8H
    mls v17.8H, v23.8H, v10.8H
    mls v19.8H, v1.8H, v10.8H
    sub v17.8H, v15.8H, v17.8H
    sub v19.8H, v29.8H, v19.8H
    zip1 v0.2d, v17.2d, v19.2d
    movi v2.8h, #9
    sqrdmulh v1.8h, v0.8h, v2.8h
    mls v0.8h, v1.8h, v10.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v10.16b
    add v0.8h, v0.8h, v1.8h
    ushr v2.8h, v10.8h, #1
    cmgt v1.8h, v0.8h, v2.8h
    and v1.16b, v1.16b, v10.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #648]
    umov w13, v0.h[1]
    strh w13, [x0, #650]
    umov w13, v0.h[2]
    strh w13, [x0, #652]
    umov w13, v0.h[4]
    strh w13, [x0, #702]
    umov w13, v0.h[5]
    strh w13, [x0, #704]
    umov w13, v0.h[6]
    strh w13, [x0, #706]
    orr v15.16B, v5.16B, v5.16B
    orr v29.16B, v6.16B, v6.16B
    ext v17.16B, v5.16B, v5.16B, #6
    ext v19.16B, v6.16B, v6.16B, #6
    sub v17.8H, v17.8H, v15.8H
    sub v14.8H, v19.8H, v29.8H
    mov w13, #63902
    dup v23.8H, w13
    mov w13, #50048
    dup v19.8H, w13
    sqrdmulh v1.8H, v17.8H, v19.8H
    sqrdmulh v19.8H, v14.8H, v19.8H
    mul v17.8H, v17.8H, v23.8H
    mul v24.8H, v14.8H, v23.8H
    mls v17.8H, v1.8H, v10.8H
    mls v24.8H, v19.8H, v10.8H
    zip1 v0.2d, v17.2d, v24.2d
    movi v2.8h, #9
    sqrdmulh v1.8h, v0.8h, v2.8h
    mls v0.8h, v1.8h, v10.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v10.16b
    add v0.8h, v0.8h, v1.8h
    ushr v2.8h, v10.8h, #1
    cmgt v1.8h, v0.8h, v2.8h
    and v1.16b, v1.16b, v10.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #1620]
    umov w13, v0.h[1]
    strh w13, [x0, #1622]
    umov w13, v0.h[2]
    strh w13, [x0, #1624]
    umov w13, v0.h[4]
    strh w13, [x0, #1674]
    umov w13, v0.h[5]
    strh w13, [x0, #1676]
    umov w13, v0.h[6]
    strh w13, [x0, #1678]
    mov w13, #64814
    dup v14.8H, w13
    mov w13, #58692
    dup v19.8H, w13
    sqrdmulh v23.8H, v17.8H, v19.8H
    sqrdmulh v1.8H, v24.8H, v19.8H
    mul v17.8H, v17.8H, v14.8H
    mul v19.8H, v24.8H, v14.8H
    mls v17.8H, v23.8H, v10.8H
    mls v19.8H, v1.8H, v10.8H
    sub v17.8H, v15.8H, v17.8H
    sub v19.8H, v29.8H, v19.8H
    zip1 v0.2d, v17.2d, v19.2d
    movi v2.8h, #9
    sqrdmulh v1.8h, v0.8h, v2.8h
    mls v0.8h, v1.8h, v10.8h
    sshr v1.8h, v0.8h, #15
    and v1.16b, v1.16b, v10.16b
    add v0.8h, v0.8h, v1.8h
    ushr v2.8h, v10.8h, #1
    cmgt v1.8h, v0.8h, v2.8h
    and v1.16b, v1.16b, v10.16b
    sub v0.8h, v0.8h, v1.8h
    umov w13, v0.h[0]
    strh w13, [x0, #756]
    umov w13, v0.h[1]
    strh w13, [x0, #758]
    umov w13, v0.h[2]
    strh w13, [x0, #760]
    umov w13, v0.h[4]
    strh w13, [x0, #810]
    umov w13, v0.h[5]
    strh w13, [x0, #812]
    umov w5, v0.h[6]
    strh w5, [x0, #814]
lazy_itail_slothy_end:
    ret
