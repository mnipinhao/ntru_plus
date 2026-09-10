.text
.p2align 2
.global gt864_p6d3_full_asm
.global gt864_p6d3_small_asm
gt864_p6d3_small_asm:
gt864_p6d3_full_asm:
    sub sp, sp, #176
    stp x19, x20, [sp, #0]
    stp x21, x22, [sp, #16]
    stp x23, x24, [sp, #32]
    stp x25, x26, [sp, #48]
    stp x27, x28, [sp, #64]
    stp x29, x30, [sp, #80]
    stp d8, d9, [sp, #96]
    stp d10, d11, [sp, #112]
    stp d12, d13, [sp, #128]
    stp d14, d15, [sp, #144]
    str x0, [sp, #160]
    str x1, [sp, #168]
    adr x30, .Lp6d3_tables
    ldr x29, [sp, #168]
    ldr q12, [x29, #384]
    ldr q10, [x29, #336]
    ext v26.16B, v10.16B, v10.16B, #14
    ldr q10, [x29, #288]
    ext v8.16B, v10.16B, v10.16B, #12
    ldr q10, [x29, #240]
    ext v4.16B, v10.16B, v10.16B, #10
    ldr q10, [x29, #192]
    ext v25.16B, v10.16B, v10.16B, #8
    ldr q10, [x29, #144]
    ext v29.16B, v10.16B, v10.16B, #6
    ldr q10, [x29, #96]
    ext v21.16B, v10.16B, v10.16B, #4
    ldr q10, [x29, #48]
    ext v10.16B, v10.16B, v10.16B, #2
    ldr q19, [x29, #0]
    trn1 v20.8H, v12.8H, v26.8H
    trn2 v12.8H, v12.8H, v26.8H
    trn1 v26.8H, v8.8H, v4.8H
    trn2 v4.8H, v8.8H, v4.8H
    trn1 v6.8H, v25.8H, v29.8H
    trn2 v8.8H, v25.8H, v29.8H
    trn1 v29.8H, v21.8H, v10.8H
    trn2 v10.8H, v21.8H, v10.8H
    trn1 v25.4S, v20.4S, v26.4S
    trn1 v21.4S, v12.4S, v4.4S
    trn2 v20.4S, v20.4S, v26.4S
    trn2 v12.4S, v12.4S, v4.4S
    trn1 v26.4S, v6.4S, v29.4S
    trn1 v4.4S, v8.4S, v10.4S
    trn2 v29.4S, v6.4S, v29.4S
    trn2 v10.4S, v8.4S, v10.4S
    trn1 v18.2D, v25.2D, v26.2D
    trn2 v31.2D, v25.2D, v26.2D
    trn1 v28.2D, v21.2D, v4.2D
    trn2 v22.2D, v21.2D, v4.2D
    trn1 v27.2D, v20.2D, v29.2D
    trn2 v13.2D, v20.2D, v29.2D
    trn1 v14.2D, v12.2D, v10.2D
    trn2 v2.2D, v12.2D, v10.2D
    ldr q12, [x29, #400]
    ldr q10, [x29, #352]
    ext v26.16B, v10.16B, v10.16B, #14
    ldr q10, [x29, #304]
    ext v8.16B, v10.16B, v10.16B, #12
    ldr q10, [x29, #256]
    ext v4.16B, v10.16B, v10.16B, #10
    ldr q10, [x29, #208]
    ext v25.16B, v10.16B, v10.16B, #8
    ldr q10, [x29, #160]
    ext v29.16B, v10.16B, v10.16B, #6
    ldr q10, [x29, #112]
    ext v21.16B, v10.16B, v10.16B, #4
    ldr q10, [x29, #64]
    ext v10.16B, v10.16B, v10.16B, #2
    ldr q15, [x29, #16]
    trn1 v20.8H, v12.8H, v26.8H
    trn2 v12.8H, v12.8H, v26.8H
    trn1 v26.8H, v8.8H, v4.8H
    trn2 v4.8H, v8.8H, v4.8H
    trn1 v6.8H, v25.8H, v29.8H
    trn2 v8.8H, v25.8H, v29.8H
    trn1 v29.8H, v21.8H, v10.8H
    trn2 v10.8H, v21.8H, v10.8H
    trn1 v25.4S, v20.4S, v26.4S
    trn1 v21.4S, v12.4S, v4.4S
    trn2 v20.4S, v20.4S, v26.4S
    trn2 v12.4S, v12.4S, v4.4S
    trn1 v26.4S, v6.4S, v29.4S
    trn1 v4.4S, v8.4S, v10.4S
    trn2 v29.4S, v6.4S, v29.4S
    trn2 v10.4S, v8.4S, v10.4S
    trn1 v7.2D, v25.2D, v26.2D
    trn2 v0.2D, v25.2D, v26.2D
    trn1 v17.2D, v21.2D, v4.2D
    trn2 v11.2D, v21.2D, v4.2D
    trn1 v24.2D, v20.2D, v29.2D
    trn2 v23.2D, v20.2D, v29.2D
    trn1 v8.2D, v12.2D, v10.2D
    trn2 v25.2D, v12.2D, v10.2D
    ldr q21, [x30, #336]
    ldr q20, [x30, #352]
    ldr q4, [x30, #160]
    orr v10.16B, v18.16B, v18.16B
    ins v10.h[0], v19.h[0]
    tbl v29.16B, {v10.16B}, v4.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v26.8H, v29.8H, v10.8H
    orr v10.16B, v7.16B, v7.16B
    ins v10.h[0], v15.h[0]
    tbl v29.16B, {v10.16B}, v4.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    umov x21, v29.d[0]
    umov x24, v29.d[1]
    umov x28, v10.d[0]
    ldr q12, [x30, #176]
    ldr q4, [x30, #0]
    and v29.16B, v18.16B, v4.16B
    bic v10.16B, v28.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[1], v19.h[1]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v26.8H, v29.8H, v10.8H
    and v29.16B, v7.16B, v4.16B
    bic v10.16B, v17.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[1], v15.h[1]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    umov x23, v29.d[0]
    umov x9, v29.d[1]
    umov x7, v10.d[0]
    ldr q12, [x30, #192]
    ldr q4, [x30, #16]
    and v29.16B, v28.16B, v4.16B
    bic v10.16B, v27.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[2], v19.h[2]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v26.8H, v29.8H, v10.8H
    and v29.16B, v17.16B, v4.16B
    bic v10.16B, v24.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[2], v15.h[2]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    umov x6, v29.d[0]
    umov x3, v29.d[1]
    umov x22, v10.d[0]
    ldr q12, [x30, #208]
    ldr q4, [x30, #32]
    and v29.16B, v27.16B, v4.16B
    bic v10.16B, v14.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[3], v19.h[3]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v26.8H, v29.8H, v10.8H
    and v29.16B, v24.16B, v4.16B
    bic v10.16B, v8.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[3], v15.h[3]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    umov x10, v29.d[0]
    umov x1, v29.d[1]
    umov x13, v10.d[0]
    ldr q12, [x30, #224]
    ldr q4, [x30, #48]
    and v29.16B, v14.16B, v4.16B
    bic v10.16B, v31.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[4], v19.h[4]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v26.8H, v29.8H, v10.8H
    and v29.16B, v8.16B, v4.16B
    bic v10.16B, v0.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[4], v15.h[4]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    umov x0, v29.d[0]
    umov x8, v29.d[1]
    umov x17, v10.d[0]
    ldr q12, [x30, #240]
    ldr q4, [x30, #64]
    and v29.16B, v31.16B, v4.16B
    bic v10.16B, v22.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[5], v19.h[5]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v26.8H, v29.8H, v10.8H
    and v29.16B, v0.16B, v4.16B
    bic v10.16B, v11.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[5], v15.h[5]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    umov x14, v29.d[0]
    umov x5, v29.d[1]
    umov x27, v10.d[0]
    ldr q12, [x30, #256]
    ldr q4, [x30, #80]
    and v29.16B, v22.16B, v4.16B
    bic v10.16B, v13.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[6], v19.h[6]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v26.8H, v29.8H, v10.8H
    and v29.16B, v11.16B, v4.16B
    bic v10.16B, v23.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[6], v15.h[6]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    umov x2, v29.d[0]
    umov x19, v29.d[1]
    umov x20, v10.d[0]
    ldr q4, [x30, #272]
    orr v10.16B, v13.16B, v13.16B
    ins v10.h[7], v19.h[7]
    tbl v29.16B, {v10.16B}, v4.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v26.8H, v29.8H, v10.8H
    orr v10.16B, v23.16B, v23.16B
    ins v10.h[7], v15.h[7]
    tbl v29.16B, {v10.16B}, v4.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    umov x15, v29.d[0]
    umov x26, v29.d[1]
    umov x12, v10.d[0]
    ldr q4, [x30, #288]
    orr v10.16B, v2.16B, v2.16B
    tbl v29.16B, {v10.16B}, v4.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v26.8H, v29.8H, v10.8H
    orr v10.16B, v25.16B, v25.16B
    tbl v29.16B, {v10.16B}, v4.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    umov x11, v29.d[0]
    umov x4, v29.d[1]
    umov x25, v10.d[0]
    mov x16, x10
    mov x10, x23
    mov x23, x16
    mov x16, x1
    mov x1, x9
    mov x9, x16
    mov x16, x13
    mov x13, x7
    mov x7, x16
    mov x16, x2
    mov x2, x6
    mov x6, x16
    mov x16, x19
    mov x19, x3
    mov x3, x16
    mov x16, x20
    mov x20, x22
    mov x22, x16
    mov x16, x15
    mov x15, x14
    mov x14, x16
    mov x16, x26
    mov x26, x5
    mov x5, x16
    mov x16, x12
    mov x12, x27
    mov x27, x16
    ldr q6, [x29, #416]
    ldr q10, [x29, #368]
    ext v26.16B, v10.16B, v10.16B, #14
    ldr q10, [x29, #320]
    ext v21.16B, v10.16B, v10.16B, #12
    ldr q10, [x29, #272]
    ext v4.16B, v10.16B, v10.16B, #10
    ldr q10, [x29, #224]
    ext v30.16B, v10.16B, v10.16B, #8
    ldr q10, [x29, #176]
    ext v29.16B, v10.16B, v10.16B, #6
    ldr q10, [x29, #128]
    ext v20.16B, v10.16B, v10.16B, #4
    ldr q10, [x29, #80]
    ext v10.16B, v10.16B, v10.16B, #2
    ldr q1, [x29, #32]
    trn1 v12.8H, v6.8H, v26.8H
    trn2 v6.8H, v6.8H, v26.8H
    trn1 v26.8H, v21.8H, v4.8H
    trn2 v4.8H, v21.8H, v4.8H
    trn1 v8.8H, v30.8H, v29.8H
    trn2 v25.8H, v30.8H, v29.8H
    trn1 v29.8H, v20.8H, v10.8H
    trn2 v10.8H, v20.8H, v10.8H
    trn1 v21.4S, v12.4S, v26.4S
    trn1 v20.4S, v6.4S, v4.4S
    trn2 v12.4S, v12.4S, v26.4S
    trn2 v26.4S, v6.4S, v4.4S
    trn1 v4.4S, v8.4S, v29.4S
    trn1 v18.4S, v25.4S, v10.4S
    trn2 v29.4S, v8.4S, v29.4S
    trn2 v10.4S, v25.4S, v10.4S
    trn1 v11.2D, v21.2D, v4.2D
    trn2 v16.2D, v21.2D, v4.2D
    trn1 v24.2D, v20.2D, v18.2D
    trn2 v9.2D, v20.2D, v18.2D
    trn1 v23.2D, v12.2D, v29.2D
    trn2 v30.2D, v12.2D, v29.2D
    trn1 v3.2D, v26.2D, v10.2D
    trn2 v19.2D, v26.2D, v10.2D
    ldr q12, [x29, #816]
    ldr q10, [x29, #768]
    ext v26.16B, v10.16B, v10.16B, #14
    ldr q10, [x29, #720]
    ext v8.16B, v10.16B, v10.16B, #12
    ldr q10, [x29, #672]
    ext v4.16B, v10.16B, v10.16B, #10
    ldr q10, [x29, #624]
    ext v25.16B, v10.16B, v10.16B, #8
    ldr q10, [x29, #576]
    ext v29.16B, v10.16B, v10.16B, #6
    ldr q10, [x29, #528]
    ext v21.16B, v10.16B, v10.16B, #4
    ldr q10, [x29, #480]
    ext v10.16B, v10.16B, v10.16B, #2
    ldr q18, [x29, #432]
    trn1 v20.8H, v12.8H, v26.8H
    trn2 v12.8H, v12.8H, v26.8H
    trn1 v26.8H, v8.8H, v4.8H
    trn2 v4.8H, v8.8H, v4.8H
    trn1 v6.8H, v25.8H, v29.8H
    trn2 v8.8H, v25.8H, v29.8H
    trn1 v29.8H, v21.8H, v10.8H
    trn2 v10.8H, v21.8H, v10.8H
    trn1 v25.4S, v20.4S, v26.4S
    trn1 v21.4S, v12.4S, v4.4S
    trn2 v20.4S, v20.4S, v26.4S
    trn2 v12.4S, v12.4S, v4.4S
    trn1 v26.4S, v6.4S, v29.4S
    trn1 v4.4S, v8.4S, v10.4S
    trn2 v29.4S, v6.4S, v29.4S
    trn2 v10.4S, v8.4S, v10.4S
    trn1 v8.2D, v25.2D, v26.2D
    trn2 v31.2D, v25.2D, v26.2D
    trn1 v25.2D, v21.2D, v4.2D
    trn2 v28.2D, v21.2D, v4.2D
    trn1 v21.2D, v20.2D, v29.2D
    trn2 v22.2D, v20.2D, v29.2D
    trn1 v20.2D, v12.2D, v10.2D
    trn2 v27.2D, v12.2D, v10.2D
    ldr q13, [x30, #336]
    ldr q14, [x30, #352]
    ldr q4, [x30, #160]
    orr v10.16B, v11.16B, v11.16B
    ins v10.h[0], v1.h[0]
    tbl v29.16B, {v10.16B}, v4.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v26.8H, v29.8H, v10.8H
    orr v10.16B, v8.16B, v8.16B
    ins v10.h[0], v18.h[0]
    tbl v29.16B, {v10.16B}, v4.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    movi v2.16B, #0
    mov v2.d[0], x21
    mov v2.d[1], x24
    movi v15.16B, #0
    mov v15.d[0], x28
    mov v15.d[1], v29.d[0]
    movi v7.16B, #0
    mov v7.d[0], v29.d[1]
    mov v7.d[1], v10.d[0]
    ldr q12, [x30, #176]
    ldr q4, [x30, #0]
    and v29.16B, v11.16B, v4.16B
    bic v10.16B, v24.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[1], v1.h[1]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v26.8H, v29.8H, v10.8H
    and v29.16B, v8.16B, v4.16B
    bic v10.16B, v25.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[1], v18.h[1]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v12.8H, v29.8H, v14.8H
    mls v29.8H, v12.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    movi v0.16B, #0
    mov v0.d[0], x10
    mov v0.d[1], x1
    movi v17.16B, #0
    mov v17.d[0], x13
    mov v17.d[1], v29.d[0]
    movi v11.16B, #0
    mov v11.d[0], v29.d[1]
    mov v11.d[1], v10.d[0]
    ldr q12, [x30, #192]
    ldr q4, [x30, #16]
    and v29.16B, v24.16B, v4.16B
    bic v10.16B, v23.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[2], v1.h[2]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v26.8H, v29.8H, v10.8H
    and v29.16B, v25.16B, v4.16B
    bic v10.16B, v21.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[2], v18.h[2]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q8, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v8.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    umov x28, v29.d[0]
    umov x24, v29.d[1]
    umov x21, v10.d[0]
    ldr q12, [x30, #208]
    ldr q4, [x30, #32]
    and v29.16B, v23.16B, v4.16B
    bic v10.16B, v3.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[3], v1.h[3]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v26.8H, v29.8H, v10.8H
    and v29.16B, v21.16B, v4.16B
    bic v10.16B, v20.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[3], v18.h[3]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    movi v24.16B, #0
    mov v24.d[0], x23
    mov v24.d[1], x9
    movi v23.16B, #0
    mov v23.d[0], x7
    mov v23.d[1], v29.d[0]
    movi v8.16B, #0
    mov v8.d[0], v29.d[1]
    mov v8.d[1], v10.d[0]
    ldr q12, [x30, #224]
    ldr q4, [x30, #48]
    and v29.16B, v3.16B, v4.16B
    bic v10.16B, v16.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[4], v1.h[4]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v26.8H, v29.8H, v10.8H
    and v29.16B, v20.16B, v4.16B
    bic v10.16B, v31.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[4], v18.h[4]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    movi v25.16B, #0
    mov v25.d[0], x0
    mov v25.d[1], x8
    umov x7, v29.d[0]
    umov x9, v29.d[1]
    umov x16, v10.d[0]
    ldr q12, [x30, #240]
    ldr q4, [x30, #64]
    and v29.16B, v16.16B, v4.16B
    bic v10.16B, v9.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[5], v1.h[5]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v26.8H, v29.8H, v10.8H
    and v29.16B, v31.16B, v4.16B
    bic v10.16B, v28.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[5], v18.h[5]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    umov x23, v29.d[0]
    umov x0, v29.d[1]
    umov x8, v10.d[0]
    ldr q12, [x30, #256]
    ldr q4, [x30, #80]
    and v29.16B, v9.16B, v4.16B
    bic v10.16B, v30.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[6], v1.h[6]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v26.8H, v29.8H, v10.8H
    and v29.16B, v28.16B, v4.16B
    bic v10.16B, v22.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[6], v18.h[6]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    movi v21.16B, #0
    mov v21.d[0], x6
    mov v21.d[1], x3
    movi v20.16B, #0
    mov v20.d[0], x22
    mov v20.d[1], v29.d[0]
    movi v12.16B, #0
    mov v12.d[0], v29.d[1]
    mov v12.d[1], v10.d[0]
    ldr q4, [x30, #272]
    orr v10.16B, v30.16B, v30.16B
    ins v10.h[7], v1.h[7]
    tbl v29.16B, {v10.16B}, v4.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v26.8H, v29.8H, v10.8H
    orr v10.16B, v22.16B, v22.16B
    ins v10.h[7], v18.h[7]
    tbl v29.16B, {v10.16B}, v4.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    umov x10, v29.d[0]
    umov x1, v29.d[1]
    umov x13, v10.d[0]
    ldr q4, [x30, #288]
    orr v10.16B, v19.16B, v19.16B
    tbl v29.16B, {v10.16B}, v4.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v26.8H, v29.8H, v10.8H
    orr v10.16B, v27.16B, v27.16B
    tbl v29.16B, {v10.16B}, v4.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    umov x22, v29.d[0]
    umov x6, v29.d[1]
    umov x3, v10.d[0]
    orr v1.16b, v24.16b, v24.16b
    orr v24.16b, v8.16b, v8.16b
    orr v28.16b, v21.16b, v21.16b
    orr v27.16b, v20.16b, v20.16b
    orr v16.16b, v12.16b, v12.16b
    orr v29.16b, v0.16b, v0.16b
    orr v13.16b, v11.16b, v11.16b
    orr v10.16b, v25.16b, v25.16b
    orr v25.16b, v15.16b, v15.16b
    orr v0.16b, v2.16b, v2.16b
    orr v2.16b, v23.16b, v23.16b
    orr v23.16b, v17.16b, v17.16b
    orr v17.16b, v0.16b, v0.16b
    ldr q12, [x29, #832]
    ldr q4, [x29, #784]
    ext v11.16B, v4.16B, v4.16B, #14
    ldr q26, [x29, #736]
    ext v8.16B, v26.16B, v26.16B, #12
    ldr q26, [x29, #688]
    ext v26.16B, v26.16B, v26.16B, #10
    ldr q21, [x29, #640]
    ext v21.16B, v21.16B, v21.16B, #8
    ldr q30, [x29, #592]
    ext v3.16B, v30.16B, v30.16B, #6
    ldr q5, [x29, #544]
    ext v20.16B, v5.16B, v5.16B, #4
    ldr q22, [x29, #496]
    ext v0.16B, v22.16B, v22.16B, #2
    ldr q18, [x29, #448]
    trn1 v6.8H, v12.8H, v11.8H
    trn2 v22.8H, v12.8H, v11.8H
    trn1 v11.8H, v8.8H, v26.8H
    trn2 v14.8H, v8.8H, v26.8H
    trn1 v19.8H, v21.8H, v3.8H
    trn2 v30.8H, v21.8H, v3.8H
    trn1 v12.8H, v20.8H, v0.8H
    trn2 v31.8H, v20.8H, v0.8H
    trn1 v26.4S, v6.4S, v11.4S
    trn2 v3.4S, v6.4S, v11.4S
    trn1 v21.4S, v19.4S, v12.4S
    trn2 v19.4S, v19.4S, v12.4S
    trn1 v6.4S, v22.4S, v14.4S
    trn2 v11.4S, v22.4S, v14.4S
    trn1 v5.4S, v30.4S, v31.4S
    trn2 v9.4S, v30.4S, v31.4S
    trn1 v15.2D, v26.2D, v21.2D
    trn2 v30.2D, v26.2D, v21.2D
    trn1 v14.2D, v6.2D, v5.2D
    trn2 v21.2D, v6.2D, v5.2D
    trn1 v5.2D, v3.2D, v19.2D
    trn2 v20.2D, v3.2D, v19.2D
    trn1 v6.2D, v11.2D, v9.2D
    trn2 v22.2D, v11.2D, v9.2D
    orr v4.16B, v15.16B, v15.16B
    ins v4.h[0], v18.h[0]
    ldr q3, [x30, #160]
    tbl v11.16B, {v4.16B}, v3.16B
    ldr q9, [x30, #0]
    and v8.16B, v15.16B, v9.16B
    bic v31.16B, v14.16B, v9.16B
    orr v4.16B, v8.16B, v31.16B
    ins v4.h[1], v18.h[1]
    ldr q8, [x30, #176]
    tbl v4.16B, {v4.16B}, v8.16B
    ldr q26, [x30, #16]
    and v0.16B, v14.16B, v26.16B
    bic v3.16B, v5.16B, v26.16B
    orr v9.16B, v0.16B, v3.16B
    ins v9.h[2], v18.h[2]
    ldr q14, [x30, #192]
    tbl v0.16B, {v9.16B}, v14.16B
    ldr q31, [x30, #32]
    and v14.16B, v5.16B, v31.16B
    bic v12.16B, v6.16B, v31.16B
    orr v9.16B, v14.16B, v12.16B
    ins v9.h[3], v18.h[3]
    ldr q14, [x30, #208]
    tbl v3.16B, {v9.16B}, v14.16B
    ldr q26, [x30, #48]
    and v19.16B, v6.16B, v26.16B
    bic v31.16B, v30.16B, v26.16B
    orr v9.16B, v19.16B, v31.16B
    ins v9.h[4], v18.h[4]
    ldr q14, [x30, #224]
    tbl v31.16B, {v9.16B}, v14.16B
    ldr q14, [x30, #64]
    and v26.16B, v30.16B, v14.16B
    bic v30.16B, v21.16B, v14.16B
    orr v12.16B, v26.16B, v30.16B
    ins v12.h[5], v18.h[5]
    ldr q5, [x30, #240]
    tbl v14.16B, {v12.16B}, v5.16B
    ldr q5, [x30, #80]
    and v9.16B, v21.16B, v5.16B
    bic v12.16B, v20.16B, v5.16B
    orr v12.16B, v9.16B, v12.16B
    ins v12.h[6], v18.h[6]
    ldr q30, [x30, #256]
    tbl v26.16B, {v12.16B}, v30.16B
    orr v12.16B, v20.16B, v20.16B
    ins v12.h[7], v18.h[7]
    ldr q21, [x30, #272]
    tbl v20.16B, {v12.16B}, v21.16B
    orr v12.16B, v22.16B, v22.16B
    ldr q30, [x30, #288]
    tbl v15.16B, {v12.16B}, v30.16B
    orr v30.16b, v7.16b, v7.16b
    orr v19.16b, v2.16b, v2.16b
    orr v22.16b, v28.16b, v28.16b
    orr v21.16b, v29.16b, v29.16b
    orr v29.16b, v23.16b, v23.16b
    orr v12.16b, v0.16b, v0.16b
    orr v2.16b, v14.16b, v14.16b
    orr v14.16b, v24.16b, v24.16b
    orr v24.16b, v17.16b, v17.16b
    orr v17.16b, v31.16b, v31.16b
    orr v31.16b, v10.16b, v10.16b
    orr v9.16b, v26.16b, v26.16b
    orr v28.16b, v20.16b, v20.16b
    orr v20.16b, v1.16b, v1.16b
    orr v1.16b, v16.16b, v16.16b
    orr v16.16b, v27.16b, v27.16b
    orr v27.16b, v3.16b, v3.16b
    orr v23.16b, v15.16b, v15.16b
    orr v15.16b, v13.16b, v13.16b
    orr v13.16b, v25.16b, v25.16b
    orr v25.16b, v4.16b, v4.16b
    orr v4.16b, v11.16b, v11.16b
    ldr q18, [x30, #336]
    ldr q8, [x30, #352]
    sqrdmulh v0.8H, v4.8H, v8.8H
    mls v4.8H, v0.8H, v18.8H
    sshr v0.8H, v4.8H, #15
    and v0.16B, v0.16B, v18.16B
    add v3.8H, v4.8H, v0.8H
    xtn v0.8B, v3.8H
    movi v7.16B, #0
    mov v7.d[0], v0.d[0]
    ushr v0.8H, v3.8H, #8
    uzp1 v4.8H, v0.8H, v0.8H
    uzp2 v0.8H, v0.8H, v0.8H
    sli v4.8H, v0.8H, #4
    xtn v0.8B, v4.8H
    movi v4.16B, #0
    ins v4.h[0], v0.h[0]
    ins v4.h[1], v0.h[1]
    sqrdmulh v0.8H, v25.8H, v8.8H
    mls v25.8H, v0.8H, v18.8H
    sshr v0.8H, v25.8H, #15
    and v0.16B, v0.16B, v18.16B
    add v3.8H, v25.8H, v0.8H
    xtn v0.8B, v3.8H
    mov v7.d[1], v0.d[0]
    ushr v0.8H, v3.8H, #8
    uzp1 v26.8H, v0.8H, v0.8H
    uzp2 v0.8H, v0.8H, v0.8H
    sli v26.8H, v0.8H, #4
    xtn v0.8B, v26.8H
    ins v4.h[2], v0.h[0]
    ins v4.h[3], v0.h[1]
    sqrdmulh v0.8H, v12.8H, v8.8H
    mls v12.8H, v0.8H, v18.8H
    sshr v0.8H, v12.8H, #15
    and v0.16B, v0.16B, v18.16B
    add v3.8H, v12.8H, v0.8H
    xtn v0.8B, v3.8H
    movi v25.16B, #0
    mov v25.d[0], v0.d[0]
    ushr v0.8H, v3.8H, #8
    uzp1 v11.8H, v0.8H, v0.8H
    uzp2 v0.8H, v0.8H, v0.8H
    sli v11.8H, v0.8H, #4
    xtn v0.8B, v11.8H
    ins v4.h[4], v0.h[0]
    ins v4.h[5], v0.h[1]
    sqrdmulh v0.8H, v27.8H, v8.8H
    mls v27.8H, v0.8H, v18.8H
    sshr v0.8H, v27.8H, #15
    and v0.16B, v0.16B, v18.16B
    add v3.8H, v27.8H, v0.8H
    xtn v0.8B, v3.8H
    mov v25.d[1], v0.d[0]
    ushr v0.8H, v3.8H, #8
    uzp1 v10.8H, v0.8H, v0.8H
    uzp2 v0.8H, v0.8H, v0.8H
    sli v10.8H, v0.8H, #4
    xtn v0.8B, v10.8H
    ins v4.h[6], v0.h[0]
    ins v4.h[7], v0.h[1]
    sqrdmulh v0.8H, v17.8H, v8.8H
    mls v17.8H, v0.8H, v18.8H
    sshr v0.8H, v17.8H, #15
    and v0.16B, v0.16B, v18.16B
    add v3.8H, v17.8H, v0.8H
    xtn v0.8B, v3.8H
    movi v12.16B, #0
    mov v12.d[0], v0.d[0]
    ushr v0.8H, v3.8H, #8
    uzp1 v6.8H, v0.8H, v0.8H
    uzp2 v0.8H, v0.8H, v0.8H
    sli v6.8H, v0.8H, #4
    xtn v0.8B, v6.8H
    movi v27.16B, #0
    ins v27.h[0], v0.h[0]
    ins v27.h[1], v0.h[1]
    sqrdmulh v0.8H, v2.8H, v8.8H
    mls v2.8H, v0.8H, v18.8H
    sshr v0.8H, v2.8H, #15
    and v0.16B, v0.16B, v18.16B
    add v3.8H, v2.8H, v0.8H
    xtn v0.8B, v3.8H
    mov v12.d[1], v0.d[0]
    ushr v0.8H, v3.8H, #8
    uzp1 v6.8H, v0.8H, v0.8H
    uzp2 v0.8H, v0.8H, v0.8H
    sli v6.8H, v0.8H, #4
    xtn v0.8B, v6.8H
    ins v27.h[2], v0.h[0]
    ins v27.h[3], v0.h[1]
    sqrdmulh v0.8H, v9.8H, v8.8H
    mls v9.8H, v0.8H, v18.8H
    sshr v0.8H, v9.8H, #15
    and v0.16B, v0.16B, v18.16B
    add v3.8H, v9.8H, v0.8H
    xtn v0.8B, v3.8H
    movi v17.16B, #0
    mov v17.d[0], v0.d[0]
    ushr v0.8H, v3.8H, #8
    uzp1 v5.8H, v0.8H, v0.8H
    uzp2 v0.8H, v0.8H, v0.8H
    sli v5.8H, v0.8H, #4
    xtn v0.8B, v5.8H
    ins v27.h[4], v0.h[0]
    ins v27.h[5], v0.h[1]
    sqrdmulh v0.8H, v28.8H, v8.8H
    mls v28.8H, v0.8H, v18.8H
    sshr v0.8H, v28.8H, #15
    and v0.16B, v0.16B, v18.16B
    add v3.8H, v28.8H, v0.8H
    xtn v0.8B, v3.8H
    mov v17.d[1], v0.d[0]
    ushr v0.8H, v3.8H, #8
    uzp1 v5.8H, v0.8H, v0.8H
    uzp2 v0.8H, v0.8H, v0.8H
    sli v5.8H, v0.8H, #4
    xtn v0.8B, v5.8H
    ins v27.h[6], v0.h[0]
    ins v27.h[7], v0.h[1]
    sqrdmulh v0.8H, v23.8H, v8.8H
    mls v23.8H, v0.8H, v18.8H
    sshr v0.8H, v23.8H, #15
    and v0.16B, v0.16B, v18.16B
    add v3.8H, v23.8H, v0.8H
    xtn v0.8B, v3.8H
    movi v9.16B, #0
    mov v9.d[0], v0.d[0]
    ushr v0.8H, v3.8H, #8
    uzp1 v18.8H, v0.8H, v0.8H
    uzp2 v0.8H, v0.8H, v0.8H
    sli v18.8H, v0.8H, #4
    xtn v0.8B, v18.8H
    ins v9.h[4], v0.h[0]
    ins v9.h[5], v0.h[1]
    orr v18.16b, v13.16b, v13.16b
    orr v2.16b, v14.16b, v14.16b
    orr v23.16b, v1.16b, v1.16b
    orr v11.16b, v21.16b, v21.16b
    orr v13.16b, v29.16b, v29.16b
    orr v6.16b, v31.16b, v31.16b
    orr v10.16b, v25.16b, v25.16b
    orr v1.16b, v12.16b, v12.16b
    orr v12.16b, v30.16b, v30.16b
    orr v25.16b, v17.16b, v17.16b
    orr v17.16b, v22.16b, v22.16b
    orr v8.16b, v9.16b, v9.16b
    orr v9.16b, v19.16b, v19.16b
    orr v30.16b, v4.16b, v4.16b
    orr v29.16b, v27.16b, v27.16b
    orr v27.16b, v7.16b, v7.16b
    orr v7.16b, v16.16b, v16.16b
    orr v16.16b, v15.16b, v15.16b
    orr v15.16b, v24.16b, v24.16b
    orr v24.16b, v20.16b, v20.16b
    ldr q31, [x29, #848]
    ldr q19, [x29, #800]
    ext v0.16B, v19.16B, v19.16B, #14
    ldr q14, [x29, #752]
    ext v3.16B, v14.16B, v14.16B, #12
    ldr q5, [x29, #704]
    ext v28.16B, v5.16B, v5.16B, #10
    ldr q14, [x29, #656]
    ext v22.16B, v14.16B, v14.16B, #8
    ldr q21, [x29, #608]
    ext v5.16B, v21.16B, v21.16B, #6
    ldr q21, [x29, #560]
    ext v26.16B, v21.16B, v21.16B, #4
    ldr q19, [x29, #512]
    ext v14.16B, v19.16B, v19.16B, #2
    ldr q19, [x29, #464]
    trn1 v21.8H, v31.8H, v0.8H
    trn2 v20.8H, v31.8H, v0.8H
    trn1 v31.8H, v3.8H, v28.8H
    trn2 v3.8H, v3.8H, v28.8H
    trn1 v4.8H, v22.8H, v5.8H
    trn2 v0.8H, v22.8H, v5.8H
    trn1 v5.8H, v26.8H, v14.8H
    trn2 v28.8H, v26.8H, v14.8H
    trn1 v22.4S, v21.4S, v31.4S
    trn2 v26.4S, v21.4S, v31.4S
    trn1 v21.4S, v4.4S, v5.4S
    trn2 v4.4S, v4.4S, v5.4S
    trn1 v14.4S, v20.4S, v3.4S
    trn2 v5.4S, v20.4S, v3.4S
    trn1 v3.4S, v0.4S, v28.4S
    trn2 v0.4S, v0.4S, v28.4S
    trn1 v31.2D, v22.2D, v21.2D
    trn2 v21.2D, v22.2D, v21.2D
    trn1 v28.2D, v14.2D, v3.2D
    trn2 v3.2D, v14.2D, v3.2D
    trn1 v14.2D, v26.2D, v4.2D
    trn2 v20.2D, v26.2D, v4.2D
    trn1 v22.2D, v5.2D, v0.2D
    trn2 v5.2D, v5.2D, v0.2D
    orr v4.16B, v31.16B, v31.16B
    ins v4.h[0], v19.h[0]
    ldr q0, [x30, #160]
    tbl v26.16B, {v4.16B}, v0.16B
    ldr q4, [x30, #0]
    and v0.16B, v31.16B, v4.16B
    bic v31.16B, v28.16B, v4.16B
    orr v4.16B, v0.16B, v31.16B
    ins v4.h[1], v19.h[1]
    ldr q0, [x30, #176]
    tbl v0.16B, {v4.16B}, v0.16B
    ldr q4, [x30, #16]
    and v31.16B, v28.16B, v4.16B
    bic v4.16B, v14.16B, v4.16B
    orr v4.16B, v31.16B, v4.16B
    ins v4.h[2], v19.h[2]
    ldr q31, [x30, #192]
    tbl v31.16B, {v4.16B}, v31.16B
    ldr q28, [x30, #32]
    and v14.16B, v14.16B, v28.16B
    bic v4.16B, v22.16B, v28.16B
    orr v4.16B, v14.16B, v4.16B
    ins v4.h[3], v19.h[3]
    ldr q14, [x30, #208]
    tbl v28.16B, {v4.16B}, v14.16B
    ldr q4, [x30, #48]
    and v22.16B, v22.16B, v4.16B
    bic v14.16B, v21.16B, v4.16B
    orr v4.16B, v22.16B, v14.16B
    ins v4.h[4], v19.h[4]
    ldr q22, [x30, #224]
    tbl v22.16B, {v4.16B}, v22.16B
    ldr q4, [x30, #64]
    and v14.16B, v21.16B, v4.16B
    bic v21.16B, v3.16B, v4.16B
    orr v4.16B, v14.16B, v21.16B
    ins v4.h[5], v19.h[5]
    ldr q14, [x30, #240]
    tbl v21.16B, {v4.16B}, v14.16B
    ldr q4, [x30, #80]
    and v14.16B, v3.16B, v4.16B
    bic v3.16B, v20.16B, v4.16B
    orr v4.16B, v14.16B, v3.16B
    ins v4.h[6], v19.h[6]
    ldr q14, [x30, #256]
    tbl v14.16B, {v4.16B}, v14.16B
    orr v4.16B, v20.16B, v20.16B
    ins v4.h[7], v19.h[7]
    ldr q20, [x30, #272]
    tbl v20.16B, {v4.16B}, v20.16B
    orr v4.16B, v5.16B, v5.16B
    ldr q19, [x30, #288]
    tbl v4.16B, {v4.16B}, v19.16B
    ldr x29, [sp, #160]
    orr v5.16b, v24.16b, v24.16b
    orr v3.16b, v11.16b, v11.16b
    orr v24.16b, v13.16b, v13.16b
    orr v13.16b, v2.16b, v2.16b
    orr v19.16b, v10.16b, v10.16b
    orr v11.16b, v30.16b, v30.16b
    orr v30.16b, v12.16b, v12.16b
    orr v12.16b, v28.16b, v28.16b
    orr v28.16b, v15.16b, v15.16b
    orr v15.16b, v6.16b, v6.16b
    orr v6.16b, v17.16b, v17.16b
    orr v2.16b, v14.16b, v14.16b
    orr v14.16b, v23.16b, v23.16b
    orr v23.16b, v0.16b, v0.16b
    orr v10.16b, v4.16b, v4.16b
    orr v4.16b, v22.16b, v22.16b
    orr v22.16b, v21.16b, v21.16b
    orr v21.16b, v8.16b, v8.16b
    orr v8.16b, v9.16b, v9.16b
    orr v9.16b, v7.16b, v7.16b
    orr v7.16b, v29.16b, v29.16b
    orr v29.16b, v18.16b, v18.16b
    orr v0.16b, v16.16b, v16.16b
    orr v16.16b, v27.16b, v27.16b
    orr v27.16b, v0.16b, v0.16b
    orr v0.16b, v1.16b, v1.16b
    orr v1.16b, v31.16b, v31.16b
    orr v31.16b, v26.16b, v26.16b
    orr v26.16b, v20.16b, v20.16b
    orr v20.16b, v0.16b, v0.16b
    ldr q18, [x30, #336]
    ldr q0, [x30, #352]
    sqrdmulh v17.8H, v31.8H, v0.8H
    mls v31.8H, v17.8H, v18.8H
    sshr v17.8H, v31.8H, #15
    and v0.16B, v17.16B, v18.16B
    add v31.8H, v31.8H, v0.8H
    eor v18.16B, v18.16B, v18.16B
    sli v18.8H, v31.8H, #4
    xtn v0.8B, v18.8H
    ushr v18.8H, v31.8H, #4
    xtn v18.8B, v18.8H
    ldr q17, [x30, #608]
    and v31.16B, v11.16B, v17.16B
    ushr v17.16B, v11.16B, #4
    zip1 v17.16B, v31.16B, v17.16B
    orr v17.8B, v0.8B, v17.8B
    ldr q31, [x30, #368]
    tbl v31.16B, {v28.16B, v29.16B}, v31.16B
    ldr q0, [x30, #384]
    tbl v0.16B, {v29.16B, v30.16B}, v0.16B
    orr v0.16B, v31.16B, v0.16B
    ldr q31, [x30, #400]
    tbl v31.16b, {v16.16b, v17.16b, v18.16b}, v31.16b
    orr v0.16B, v0.16B, v31.16B
    str q0, [x29, #0]
    ldr q0, [x30, #416]
    tbl v0.16B, {v28.16B, v29.16B}, v0.16B
    ldr q31, [x30, #432]
    tbl v31.16B, {v29.16B, v30.16B}, v31.16B
    orr v0.16B, v0.16B, v31.16B
    ldr q31, [x30, #448]
    tbl v31.16b, {v16.16b, v17.16b, v18.16b}, v31.16b
    orr v0.16B, v0.16B, v31.16B
    str q0, [x29, #16]
    ldr q0, [x30, #464]
    tbl v0.16B, {v28.16B, v29.16B}, v0.16B
    ldr q31, [x30, #480]
    tbl v31.16B, {v29.16B, v30.16B}, v31.16B
    orr v31.16B, v0.16B, v31.16B
    ldr q0, [x30, #496]
    tbl v0.16b, {v16.16b, v17.16b, v18.16b}, v0.16b
    orr v0.16B, v31.16B, v0.16B
    str q0, [x29, #32]
    ldr q31, [x30, #512]
    tbl v0.16B, {v28.16B, v29.16B}, v31.16B
    ldr q31, [x30, #528]
    tbl v31.16B, {v29.16B, v30.16B}, v31.16B
    orr v31.16B, v0.16B, v31.16B
    ldr q0, [x30, #544]
    tbl v0.16b, {v16.16b, v17.16b, v18.16b}, v0.16b
    orr v0.16B, v31.16B, v0.16B
    str q0, [x29, #48]
    ldr q0, [x30, #560]
    tbl v0.16B, {v28.16B, v29.16B}, v0.16B
    ldr q31, [x30, #576]
    tbl v28.16B, {v29.16B, v30.16B}, v31.16B
    orr v0.16B, v0.16B, v28.16B
    ldr q28, [x30, #592]
    tbl v30.16b, {v16.16b, v17.16b, v18.16b}, v28.16b
    orr v17.16B, v0.16B, v30.16B
    add x29, x29, #64
    orr v18.16b, v27.16b, v27.16b
    orr v27.16b, v6.16b, v6.16b
    orr v6.16b, v1.16b, v1.16b
    orr v1.16b, v15.16b, v15.16b
    orr v15.16b, v5.16b, v5.16b
    orr v31.16b, v4.16b, v4.16b
    orr v4.16b, v20.16b, v20.16b
    orr v5.16b, v22.16b, v22.16b
    orr v20.16b, v10.16b, v10.16b
    orr v10.16b, v23.16b, v23.16b
    orr v23.16b, v25.16b, v25.16b
    orr v25.16b, v3.16b, v3.16b
    orr v3.16b, v12.16b, v12.16b
    orr v12.16b, v24.16b, v24.16b
    orr v24.16b, v16.16b, v16.16b
    orr v16.16b, v8.16b, v8.16b
    orr v8.16b, v26.16b, v26.16b
    orr v26.16b, v11.16b, v11.16b
    orr v11.16b, v7.16b, v7.16b
    orr v7.16b, v14.16b, v14.16b
    orr v0.16b, v13.16b, v13.16b
    orr v13.16b, v21.16b, v21.16b
    orr v21.16b, v17.16b, v17.16b
    orr v17.16b, v0.16b, v0.16b
    orr v0.16b, v19.16b, v19.16b
    orr v19.16b, v2.16b, v2.16b
    orr v2.16b, v0.16b, v0.16b
    ldr q14, [x30, #336]
    ldr q0, [x30, #352]
    sqrdmulh v0.8H, v3.8H, v0.8H
    mls v3.8H, v0.8H, v14.8H
    sshr v0.8H, v3.8H, #15
    and v0.16B, v0.16B, v14.16B
    add v3.8H, v3.8H, v0.8H
    eor v0.16B, v14.16B, v14.16B
    sli v0.8H, v3.8H, #4
    xtn v22.8B, v0.8H
    ushr v0.8H, v3.8H, #4
    xtn v30.8B, v0.8H
    ext v28.16B, v2.16B, v2.16B, #8
    ext v14.16B, v26.16B, v26.16B, #12
    ldr q0, [x30, #608]
    and v3.16B, v14.16B, v0.16B
    ushr v0.16B, v14.16B, #4
    zip1 v0.16B, v3.16B, v0.16B
    orr v29.8B, v22.8B, v0.8B
    ldr q0, [x30, #368]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #384]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #400]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v22.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v21.d[0]
    mov v0.d[1], v22.d[0]
    str q0, [x29, #0]
    ldr q0, [x30, #416]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #432]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #448]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v14.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v22.d[1]
    mov v0.d[1], v14.d[0]
    str q0, [x29, #16]
    ldr q0, [x30, #464]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #480]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #496]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v22.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v14.d[1]
    mov v0.d[1], v22.d[0]
    str q0, [x29, #32]
    ldr q0, [x30, #512]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #528]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #544]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v14.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v22.d[1]
    mov v0.d[1], v14.d[0]
    str q0, [x29, #48]
    ldr q0, [x30, #560]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #576]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #592]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v3.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v14.d[1]
    mov v0.d[1], v3.d[0]
    str q0, [x29, #64]
    add x29, x29, #80
    orr v15.16b, v27.16b, v27.16b
    orr v16.16b, v9.16b, v9.16b
    orr v17.16b, v7.16b, v7.16b
    orr v27.16b, v1.16b, v1.16b
    orr v1.16b, v25.16b, v25.16b
    orr v28.16b, v24.16b, v24.16b
    orr v24.16b, v12.16b, v12.16b
    orr v3.16b, v19.16b, v19.16b
    orr v19.16b, v6.16b, v6.16b
    orr v6.16b, v26.16b, v26.16b
    orr v26.16b, v4.16b, v4.16b
    orr v21.16b, v8.16b, v8.16b
    orr v8.16b, v31.16b, v31.16b
    orr v31.16b, v11.16b, v11.16b
    orr v11.16b, v23.16b, v23.16b
    orr v23.16b, v2.16b, v2.16b
    orr v2.16b, v18.16b, v18.16b
    orr v30.16b, v20.16b, v20.16b
    orr v20.16b, v5.16b, v5.16b
    orr v5.16b, v10.16b, v10.16b
    orr v10.16b, v13.16b, v13.16b
    ldr q14, [x30, #336]
    ldr q0, [x30, #352]
    sqrdmulh v0.8H, v3.8H, v0.8H
    mls v3.8H, v0.8H, v14.8H
    sshr v0.8H, v3.8H, #15
    and v0.16B, v0.16B, v14.16B
    add v3.8H, v3.8H, v0.8H
    eor v0.16B, v14.16B, v14.16B
    sli v0.8H, v3.8H, #4
    xtn v22.8B, v0.8H
    ushr v0.8H, v3.8H, #4
    xtn v13.8B, v0.8H
    ext v14.16B, v31.16B, v31.16B, #8
    ldr q0, [x30, #608]
    and v3.16B, v14.16B, v0.16B
    ushr v0.16B, v14.16B, #4
    zip1 v0.16B, v3.16B, v0.16B
    orr v12.8B, v22.8B, v0.8B
    ldr q0, [x30, #368]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #384]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #400]
    tbl v0.16b, {v11.16b, v12.16b, v13.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #0]
    ldr q0, [x30, #416]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #432]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #448]
    tbl v0.16b, {v11.16b, v12.16b, v13.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #16]
    ldr q0, [x30, #464]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #480]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #496]
    tbl v0.16b, {v11.16b, v12.16b, v13.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #32]
    ldr q0, [x30, #512]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #528]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #544]
    tbl v0.16b, {v11.16b, v12.16b, v13.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #48]
    ldr q0, [x30, #560]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #576]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #592]
    tbl v0.16b, {v11.16b, v12.16b, v13.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    add x29, x29, #64
    orr v15.16b, v1.16b, v1.16b
    orr v16.16b, v24.16b, v24.16b
    orr v17.16b, v2.16b, v2.16b
    orr v2.16b, v27.16b, v27.16b
    orr v13.16b, v26.16b, v26.16b
    orr v26.16b, v11.16b, v11.16b
    orr v11.16b, v10.16b, v10.16b
    orr v10.16b, v6.16b, v6.16b
    orr v6.16b, v31.16b, v31.16b
    orr v3.16b, v5.16b, v5.16b
    orr v31.16b, v19.16b, v19.16b
    orr v5.16b, v8.16b, v8.16b
    orr v19.16b, v20.16b, v20.16b
    orr v8.16b, v21.16b, v21.16b
    orr v20.16b, v30.16b, v30.16b
    orr v21.16b, v0.16b, v0.16b
    ldr q14, [x30, #336]
    ldr q0, [x30, #352]
    sqrdmulh v0.8H, v3.8H, v0.8H
    mls v3.8H, v0.8H, v14.8H
    sshr v0.8H, v3.8H, #15
    and v0.16B, v0.16B, v14.16B
    add v3.8H, v3.8H, v0.8H
    eor v0.16B, v14.16B, v14.16B
    sli v0.8H, v3.8H, #4
    xtn v22.8B, v0.8H
    ushr v0.8H, v3.8H, #4
    xtn v30.8B, v0.8H
    ext v28.16B, v28.16B, v28.16B, #8
    ext v14.16B, v10.16B, v10.16B, #4
    ldr q0, [x30, #608]
    and v3.16B, v14.16B, v0.16B
    ushr v0.16B, v14.16B, #4
    zip1 v0.16B, v3.16B, v0.16B
    orr v29.8B, v22.8B, v0.8B
    ldr q0, [x30, #368]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #384]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #400]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v22.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v21.d[0]
    mov v0.d[1], v22.d[0]
    str q0, [x29, #0]
    ldr q0, [x30, #416]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #432]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #448]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v14.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v22.d[1]
    mov v0.d[1], v14.d[0]
    str q0, [x29, #16]
    ldr q0, [x30, #464]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #480]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #496]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v22.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v14.d[1]
    mov v0.d[1], v22.d[0]
    str q0, [x29, #32]
    ldr q0, [x30, #512]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #528]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #544]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v14.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v22.d[1]
    mov v0.d[1], v14.d[0]
    str q0, [x29, #48]
    ldr q0, [x30, #560]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #576]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #592]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v3.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v14.d[1]
    mov v0.d[1], v3.d[0]
    str q0, [x29, #64]
    add x29, x29, #80
    orr v3.16b, v5.16b, v5.16b
    orr v5.16b, v11.16b, v11.16b
    orr v21.16b, v19.16b, v19.16b
    orr v19.16b, v10.16b, v10.16b
    orr v10.16b, v13.16b, v13.16b
    orr v30.16b, v8.16b, v8.16b
    orr v8.16b, v6.16b, v6.16b
    orr v6.16b, v23.16b, v23.16b
    orr v22.16b, v20.16b, v20.16b
    orr v20.16b, v31.16b, v31.16b
    orr v31.16b, v26.16b, v26.16b
    orr v26.16b, v2.16b, v2.16b
    movi v27.16B, #0
    mov v27.d[0], x17
    mov v27.d[1], x7
    movi v28.16B, #0
    mov v28.d[0], x9
    mov v28.d[1], x16
    ldr q14, [x30, #336]
    ldr q0, [x30, #352]
    sqrdmulh v0.8H, v3.8H, v0.8H
    mls v3.8H, v0.8H, v14.8H
    sshr v0.8H, v3.8H, #15
    and v0.16B, v0.16B, v14.16B
    add v3.8H, v3.8H, v0.8H
    eor v0.16B, v14.16B, v14.16B
    sli v0.8H, v3.8H, #4
    xtn v14.8B, v0.8H
    ushr v0.8H, v3.8H, #4
    xtn v12.8B, v0.8H
    ldr q0, [x30, #608]
    and v3.16B, v8.16B, v0.16B
    ushr v0.16B, v8.16B, #4
    zip1 v0.16B, v3.16B, v0.16B
    orr v11.8B, v14.8B, v0.8B
    ldr q0, [x30, #368]
    tbl v3.16B, {v26.16B, v27.16B}, v0.16B
    ldr q0, [x30, #384]
    tbl v0.16B, {v27.16B, v28.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #400]
    tbl v0.16b, {v10.16b, v11.16b, v12.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #0]
    ldr q0, [x30, #416]
    tbl v3.16B, {v26.16B, v27.16B}, v0.16B
    ldr q0, [x30, #432]
    tbl v0.16B, {v27.16B, v28.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #448]
    tbl v0.16b, {v10.16b, v11.16b, v12.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #16]
    ldr q0, [x30, #464]
    tbl v3.16B, {v26.16B, v27.16B}, v0.16B
    ldr q0, [x30, #480]
    tbl v0.16B, {v27.16B, v28.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #496]
    tbl v0.16b, {v10.16b, v11.16b, v12.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #32]
    ldr q0, [x30, #512]
    tbl v3.16B, {v26.16B, v27.16B}, v0.16B
    ldr q0, [x30, #528]
    tbl v0.16B, {v27.16B, v28.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #544]
    tbl v0.16b, {v10.16b, v11.16b, v12.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #48]
    ldr q0, [x30, #560]
    tbl v3.16B, {v26.16B, v27.16B}, v0.16B
    ldr q0, [x30, #576]
    tbl v0.16B, {v27.16B, v28.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #592]
    tbl v0.16b, {v10.16b, v11.16b, v12.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    add x29, x29, #64
    orr v23.16b, v6.16b, v6.16b
    orr v13.16b, v10.16b, v10.16b
    orr v26.16b, v31.16b, v31.16b
    orr v11.16b, v5.16b, v5.16b
    orr v6.16b, v19.16b, v19.16b
    orr v31.16b, v8.16b, v8.16b
    orr v5.16b, v20.16b, v20.16b
    orr v19.16b, v21.16b, v21.16b
    orr v3.16b, v30.16b, v30.16b
    orr v20.16b, v22.16b, v22.16b
    orr v21.16b, v0.16b, v0.16b
    movi v8.16B, #0
    mov v8.d[0], x14
    mov v8.d[1], x5
    movi v9.16B, #0
    mov v9.d[0], x27
    mov v9.d[1], x10
    movi v10.16B, #0
    mov v10.d[0], x1
    mov v10.d[1], x13
    ldr q14, [x30, #336]
    ldr q0, [x30, #352]
    sqrdmulh v0.8H, v3.8H, v0.8H
    mls v3.8H, v0.8H, v14.8H
    sshr v0.8H, v3.8H, #15
    and v0.16B, v0.16B, v14.16B
    add v3.8H, v3.8H, v0.8H
    eor v0.16B, v14.16B, v14.16B
    sli v0.8H, v3.8H, #4
    xtn v22.8B, v0.8H
    ushr v0.8H, v3.8H, #4
    xtn v30.8B, v0.8H
    ext v28.16B, v26.16B, v26.16B, #8
    ext v14.16B, v31.16B, v31.16B, #12
    ldr q0, [x30, #608]
    and v3.16B, v14.16B, v0.16B
    ushr v0.16B, v14.16B, #4
    zip1 v0.16B, v3.16B, v0.16B
    orr v29.8B, v22.8B, v0.8B
    ldr q0, [x30, #368]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #384]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #400]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v22.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v21.d[0]
    mov v0.d[1], v22.d[0]
    str q0, [x29, #0]
    ldr q0, [x30, #416]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #432]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #448]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v14.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v22.d[1]
    mov v0.d[1], v14.d[0]
    str q0, [x29, #16]
    ldr q0, [x30, #464]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #480]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #496]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v22.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v14.d[1]
    mov v0.d[1], v22.d[0]
    str q0, [x29, #32]
    ldr q0, [x30, #512]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #528]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #544]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v14.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v22.d[1]
    mov v0.d[1], v14.d[0]
    str q0, [x29, #48]
    ldr q0, [x30, #560]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #576]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #592]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v3.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v14.d[1]
    mov v0.d[1], v3.d[0]
    str q0, [x29, #64]
    add x29, x29, #80
    orr v3.16b, v5.16b, v5.16b
    orr v5.16b, v11.16b, v11.16b
    orr v11.16b, v23.16b, v23.16b
    orr v21.16b, v19.16b, v19.16b
    orr v19.16b, v6.16b, v6.16b
    orr v30.16b, v20.16b, v20.16b
    orr v20.16b, v31.16b, v31.16b
    orr v31.16b, v13.16b, v13.16b
    movi v8.16B, #0
    mov v8.d[0], x2
    mov v8.d[1], x19
    movi v9.16B, #0
    mov v9.d[0], x20
    mov v9.d[1], x28
    movi v10.16B, #0
    mov v10.d[0], x24
    mov v10.d[1], x21
    ldr q14, [x30, #336]
    ldr q0, [x30, #352]
    sqrdmulh v0.8H, v3.8H, v0.8H
    mls v3.8H, v0.8H, v14.8H
    sshr v0.8H, v3.8H, #15
    and v0.16B, v0.16B, v14.16B
    add v3.8H, v3.8H, v0.8H
    eor v0.16B, v14.16B, v14.16B
    sli v0.8H, v3.8H, #4
    xtn v22.8B, v0.8H
    ushr v0.8H, v3.8H, #4
    xtn v13.8B, v0.8H
    ext v14.16B, v19.16B, v19.16B, #8
    ldr q0, [x30, #608]
    and v3.16B, v14.16B, v0.16B
    ushr v0.16B, v14.16B, #4
    zip1 v0.16B, v3.16B, v0.16B
    orr v12.8B, v22.8B, v0.8B
    ldr q0, [x30, #368]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #384]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #400]
    tbl v0.16b, {v11.16b, v12.16b, v13.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #0]
    ldr q0, [x30, #416]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #432]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #448]
    tbl v0.16b, {v11.16b, v12.16b, v13.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #16]
    ldr q0, [x30, #464]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #480]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #496]
    tbl v0.16b, {v11.16b, v12.16b, v13.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #32]
    ldr q0, [x30, #512]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #528]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #544]
    tbl v0.16b, {v11.16b, v12.16b, v13.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #48]
    ldr q0, [x30, #560]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #576]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #592]
    tbl v0.16b, {v11.16b, v12.16b, v13.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    add x29, x29, #64
    orr v1.16b, v20.16b, v20.16b
    orr v20.16b, v5.16b, v5.16b
    orr v23.16b, v21.16b, v21.16b
    orr v21.16b, v30.16b, v30.16b
    orr v26.16b, v0.16b, v0.16b
    orr v0.16b, v31.16b, v31.16b
    movi v8.16B, #0
    mov v8.d[0], x15
    mov v8.d[1], x26
    movi v9.16B, #0
    mov v9.d[0], x12
    mov v9.d[1], x23
    movi v10.16B, #0
    mov v10.d[0], x0
    mov v10.d[1], x8
    ldr q4, [x30, #336]
    ldr q29, [x30, #352]
    sqrdmulh v19.8H, v23.8H, v29.8H
    mls v23.8H, v19.8H, v4.8H
    sshr v2.8H, v23.8H, #15
    and v3.16B, v2.16B, v4.16B
    add v28.8H, v23.8H, v3.8H
    eor v5.16B, v4.16B, v4.16B
    sli v5.8H, v28.8H, #4
    xtn v15.8B, v5.8H
    ushr v30.8H, v28.8H, #4
    xtn v16.8B, v30.8H
    ext v14.16B, v0.16B, v0.16B, #8
    ext v0.16B, v1.16B, v1.16B, #4
    ldr q28, [x30, #608]
    and v27.16B, v0.16B, v28.16B
    ushr v29.16B, v0.16B, #4
    zip1 v27.16B, v27.16B, v29.16B
    orr v15.8B, v15.8B, v27.8B
    ldr q11, [x30, #368]
    tbl v30.16B, {v8.16B, v9.16B}, v11.16B
    ldr q6, [x30, #384]
    tbl v13.16B, {v9.16B, v10.16B}, v6.16B
    orr v30.16B, v30.16B, v13.16B
    ldr q4, [x30, #400]
    tbl v25.16b, {v14.16b, v15.16b, v16.16b}, v4.16b
    orr v23.16B, v30.16B, v25.16B
    movi v0.16B, #0
    mov v0.d[0], v26.d[0]
    mov v0.d[1], v23.d[0]
    str q0, [x29, #0]
    ldr q22, [x30, #416]
    tbl v30.16B, {v8.16B, v9.16B}, v22.16B
    ldr q29, [x30, #432]
    tbl v31.16B, {v9.16B, v10.16B}, v29.16B
    orr v19.16B, v30.16B, v31.16B
    ldr q29, [x30, #448]
    tbl v26.16b, {v14.16b, v15.16b, v16.16b}, v29.16b
    orr v13.16B, v19.16B, v26.16B
    movi v3.16B, #0
    mov v3.d[0], v23.d[1]
    mov v3.d[1], v13.d[0]
    str q3, [x29, #16]
    ldr q23, [x30, #464]
    tbl v19.16B, {v8.16B, v9.16B}, v23.16B
    ldr q24, [x30, #480]
    tbl v5.16B, {v9.16B, v10.16B}, v24.16B
    orr v12.16B, v19.16B, v5.16B
    ldr q4, [x30, #496]
    tbl v17.16b, {v14.16b, v15.16b, v16.16b}, v4.16b
    orr v25.16B, v12.16B, v17.16B
    movi v4.16B, #0
    mov v4.d[0], v13.d[1]
    mov v4.d[1], v25.d[0]
    str q4, [x29, #32]
    ldr q6, [x30, #512]
    tbl v18.16B, {v8.16B, v9.16B}, v6.16B
    ldr q4, [x30, #528]
    tbl v1.16B, {v9.16B, v10.16B}, v4.16B
    orr v3.16B, v18.16B, v1.16B
    ldr q13, [x30, #544]
    tbl v26.16b, {v14.16b, v15.16b, v16.16b}, v13.16b
    orr v12.16B, v3.16B, v26.16B
    movi v19.16B, #0
    mov v19.d[0], v25.d[1]
    mov v19.d[1], v12.d[0]
    str q19, [x29, #48]
    ldr q30, [x30, #560]
    tbl v8.16B, {v8.16B, v9.16B}, v30.16B
    ldr q5, [x30, #576]
    tbl v0.16B, {v9.16B, v10.16B}, v5.16B
    orr v7.16B, v8.16B, v0.16B
    ldr q5, [x30, #592]
    tbl v15.16b, {v14.16b, v15.16b, v16.16b}, v5.16b
    orr v16.16B, v7.16B, v15.16B
    movi v25.16B, #0
    mov v25.d[0], v12.d[1]
    mov v25.d[1], v16.d[0]
    str q25, [x29, #64]
    add x29, x29, #80
    orr v3.16b, v21.16b, v21.16b
    orr v21.16b, v20.16b, v20.16b
    movi v8.16B, #0
    mov v8.d[0], x11
    mov v8.d[1], x4
    movi v9.16B, #0
    mov v9.d[0], x25
    mov v9.d[1], x22
    movi v10.16B, #0
    mov v10.d[0], x6
    mov v10.d[1], x3
    ldr q14, [x30, #336]
    ldr q0, [x30, #352]
    sqrdmulh v0.8H, v3.8H, v0.8H
    mls v3.8H, v0.8H, v14.8H
    sshr v0.8H, v3.8H, #15
    and v0.16B, v0.16B, v14.16B
    add v3.8H, v3.8H, v0.8H
    eor v0.16B, v14.16B, v14.16B
    sli v0.8H, v3.8H, #4
    xtn v22.8B, v0.8H
    ushr v0.8H, v3.8H, #4
    xtn v23.8B, v0.8H
    ext v14.16B, v21.16B, v21.16B, #8
    ldr q0, [x30, #608]
    and v3.16B, v14.16B, v0.16B
    ushr v0.16B, v14.16B, #4
    zip1 v0.16B, v3.16B, v0.16B
    orr v22.8B, v22.8B, v0.8B
    ldr q0, [x30, #368]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #384]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #400]
    tbl v0.16b, {v21.16b, v22.16b, v23.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #0]
    ldr q0, [x30, #416]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #432]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #448]
    tbl v0.16b, {v21.16b, v22.16b, v23.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #16]
    ldr q0, [x30, #464]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #480]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #496]
    tbl v0.16b, {v21.16b, v22.16b, v23.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #32]
    ldr q0, [x30, #512]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #528]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #544]
    tbl v0.16b, {v21.16b, v22.16b, v23.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #48]
    ldr q0, [x30, #560]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #576]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #592]
    tbl v0.16b, {v21.16b, v22.16b, v23.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str d0, [x29, #64]
    ldr x29, [sp, #168]
    add x29, x29, #864
    ldr q12, [x29, #384]
    ldr q10, [x29, #336]
    ext v26.16B, v10.16B, v10.16B, #14
    ldr q10, [x29, #288]
    ext v8.16B, v10.16B, v10.16B, #12
    ldr q10, [x29, #240]
    ext v4.16B, v10.16B, v10.16B, #10
    ldr q10, [x29, #192]
    ext v25.16B, v10.16B, v10.16B, #8
    ldr q10, [x29, #144]
    ext v29.16B, v10.16B, v10.16B, #6
    ldr q10, [x29, #96]
    ext v21.16B, v10.16B, v10.16B, #4
    ldr q10, [x29, #48]
    ext v10.16B, v10.16B, v10.16B, #2
    ldr q19, [x29, #0]
    trn1 v20.8H, v12.8H, v26.8H
    trn2 v12.8H, v12.8H, v26.8H
    trn1 v26.8H, v8.8H, v4.8H
    trn2 v4.8H, v8.8H, v4.8H
    trn1 v6.8H, v25.8H, v29.8H
    trn2 v8.8H, v25.8H, v29.8H
    trn1 v29.8H, v21.8H, v10.8H
    trn2 v10.8H, v21.8H, v10.8H
    trn1 v25.4S, v20.4S, v26.4S
    trn1 v21.4S, v12.4S, v4.4S
    trn2 v20.4S, v20.4S, v26.4S
    trn2 v12.4S, v12.4S, v4.4S
    trn1 v26.4S, v6.4S, v29.4S
    trn1 v4.4S, v8.4S, v10.4S
    trn2 v29.4S, v6.4S, v29.4S
    trn2 v10.4S, v8.4S, v10.4S
    trn1 v18.2D, v25.2D, v26.2D
    trn2 v31.2D, v25.2D, v26.2D
    trn1 v28.2D, v21.2D, v4.2D
    trn2 v22.2D, v21.2D, v4.2D
    trn1 v27.2D, v20.2D, v29.2D
    trn2 v13.2D, v20.2D, v29.2D
    trn1 v14.2D, v12.2D, v10.2D
    trn2 v2.2D, v12.2D, v10.2D
    ldr q12, [x29, #400]
    ldr q10, [x29, #352]
    ext v26.16B, v10.16B, v10.16B, #14
    ldr q10, [x29, #304]
    ext v8.16B, v10.16B, v10.16B, #12
    ldr q10, [x29, #256]
    ext v4.16B, v10.16B, v10.16B, #10
    ldr q10, [x29, #208]
    ext v25.16B, v10.16B, v10.16B, #8
    ldr q10, [x29, #160]
    ext v29.16B, v10.16B, v10.16B, #6
    ldr q10, [x29, #112]
    ext v21.16B, v10.16B, v10.16B, #4
    ldr q10, [x29, #64]
    ext v10.16B, v10.16B, v10.16B, #2
    ldr q15, [x29, #16]
    trn1 v20.8H, v12.8H, v26.8H
    trn2 v12.8H, v12.8H, v26.8H
    trn1 v26.8H, v8.8H, v4.8H
    trn2 v4.8H, v8.8H, v4.8H
    trn1 v6.8H, v25.8H, v29.8H
    trn2 v8.8H, v25.8H, v29.8H
    trn1 v29.8H, v21.8H, v10.8H
    trn2 v10.8H, v21.8H, v10.8H
    trn1 v25.4S, v20.4S, v26.4S
    trn1 v21.4S, v12.4S, v4.4S
    trn2 v20.4S, v20.4S, v26.4S
    trn2 v12.4S, v12.4S, v4.4S
    trn1 v26.4S, v6.4S, v29.4S
    trn1 v4.4S, v8.4S, v10.4S
    trn2 v29.4S, v6.4S, v29.4S
    trn2 v10.4S, v8.4S, v10.4S
    trn1 v7.2D, v25.2D, v26.2D
    trn2 v0.2D, v25.2D, v26.2D
    trn1 v17.2D, v21.2D, v4.2D
    trn2 v11.2D, v21.2D, v4.2D
    trn1 v24.2D, v20.2D, v29.2D
    trn2 v23.2D, v20.2D, v29.2D
    trn1 v8.2D, v12.2D, v10.2D
    trn2 v25.2D, v12.2D, v10.2D
    ldr q21, [x30, #336]
    ldr q20, [x30, #352]
    ldr q4, [x30, #160]
    orr v10.16B, v18.16B, v18.16B
    ins v10.h[0], v19.h[0]
    tbl v29.16B, {v10.16B}, v4.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v26.8H, v29.8H, v10.8H
    orr v10.16B, v7.16B, v7.16B
    ins v10.h[0], v15.h[0]
    tbl v29.16B, {v10.16B}, v4.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    umov x21, v29.d[0]
    umov x24, v29.d[1]
    umov x28, v10.d[0]
    ldr q12, [x30, #176]
    ldr q4, [x30, #0]
    and v29.16B, v18.16B, v4.16B
    bic v10.16B, v28.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[1], v19.h[1]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v26.8H, v29.8H, v10.8H
    and v29.16B, v7.16B, v4.16B
    bic v10.16B, v17.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[1], v15.h[1]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    umov x23, v29.d[0]
    umov x9, v29.d[1]
    umov x7, v10.d[0]
    ldr q12, [x30, #192]
    ldr q4, [x30, #16]
    and v29.16B, v28.16B, v4.16B
    bic v10.16B, v27.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[2], v19.h[2]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v26.8H, v29.8H, v10.8H
    and v29.16B, v17.16B, v4.16B
    bic v10.16B, v24.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[2], v15.h[2]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    umov x6, v29.d[0]
    umov x3, v29.d[1]
    umov x22, v10.d[0]
    ldr q12, [x30, #208]
    ldr q4, [x30, #32]
    and v29.16B, v27.16B, v4.16B
    bic v10.16B, v14.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[3], v19.h[3]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v26.8H, v29.8H, v10.8H
    and v29.16B, v24.16B, v4.16B
    bic v10.16B, v8.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[3], v15.h[3]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    umov x10, v29.d[0]
    umov x1, v29.d[1]
    umov x13, v10.d[0]
    ldr q12, [x30, #224]
    ldr q4, [x30, #48]
    and v29.16B, v14.16B, v4.16B
    bic v10.16B, v31.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[4], v19.h[4]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v26.8H, v29.8H, v10.8H
    and v29.16B, v8.16B, v4.16B
    bic v10.16B, v0.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[4], v15.h[4]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    umov x0, v29.d[0]
    umov x8, v29.d[1]
    umov x17, v10.d[0]
    ldr q12, [x30, #240]
    ldr q4, [x30, #64]
    and v29.16B, v31.16B, v4.16B
    bic v10.16B, v22.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[5], v19.h[5]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v26.8H, v29.8H, v10.8H
    and v29.16B, v0.16B, v4.16B
    bic v10.16B, v11.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[5], v15.h[5]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    umov x14, v29.d[0]
    umov x5, v29.d[1]
    umov x27, v10.d[0]
    ldr q12, [x30, #256]
    ldr q4, [x30, #80]
    and v29.16B, v22.16B, v4.16B
    bic v10.16B, v13.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[6], v19.h[6]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v26.8H, v29.8H, v10.8H
    and v29.16B, v11.16B, v4.16B
    bic v10.16B, v23.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[6], v15.h[6]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    umov x2, v29.d[0]
    umov x19, v29.d[1]
    umov x20, v10.d[0]
    ldr q4, [x30, #272]
    orr v10.16B, v13.16B, v13.16B
    ins v10.h[7], v19.h[7]
    tbl v29.16B, {v10.16B}, v4.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v26.8H, v29.8H, v10.8H
    orr v10.16B, v23.16B, v23.16B
    ins v10.h[7], v15.h[7]
    tbl v29.16B, {v10.16B}, v4.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    umov x15, v29.d[0]
    umov x26, v29.d[1]
    umov x12, v10.d[0]
    ldr q4, [x30, #288]
    orr v10.16B, v2.16B, v2.16B
    tbl v29.16B, {v10.16B}, v4.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v26.8H, v29.8H, v10.8H
    orr v10.16B, v25.16B, v25.16B
    tbl v29.16B, {v10.16B}, v4.16B
    sqrdmulh v10.8H, v29.8H, v20.8H
    mls v29.8H, v10.8H, v21.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v21.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    umov x11, v29.d[0]
    umov x4, v29.d[1]
    umov x25, v10.d[0]
    mov x16, x10
    mov x10, x23
    mov x23, x16
    mov x16, x1
    mov x1, x9
    mov x9, x16
    mov x16, x13
    mov x13, x7
    mov x7, x16
    mov x16, x2
    mov x2, x6
    mov x6, x16
    mov x16, x19
    mov x19, x3
    mov x3, x16
    mov x16, x20
    mov x20, x22
    mov x22, x16
    mov x16, x15
    mov x15, x14
    mov x14, x16
    mov x16, x26
    mov x26, x5
    mov x5, x16
    mov x16, x12
    mov x12, x27
    mov x27, x16
    ldr q6, [x29, #416]
    ldr q10, [x29, #368]
    ext v26.16B, v10.16B, v10.16B, #14
    ldr q10, [x29, #320]
    ext v21.16B, v10.16B, v10.16B, #12
    ldr q10, [x29, #272]
    ext v4.16B, v10.16B, v10.16B, #10
    ldr q10, [x29, #224]
    ext v30.16B, v10.16B, v10.16B, #8
    ldr q10, [x29, #176]
    ext v29.16B, v10.16B, v10.16B, #6
    ldr q10, [x29, #128]
    ext v20.16B, v10.16B, v10.16B, #4
    ldr q10, [x29, #80]
    ext v10.16B, v10.16B, v10.16B, #2
    ldr q1, [x29, #32]
    trn1 v12.8H, v6.8H, v26.8H
    trn2 v6.8H, v6.8H, v26.8H
    trn1 v26.8H, v21.8H, v4.8H
    trn2 v4.8H, v21.8H, v4.8H
    trn1 v8.8H, v30.8H, v29.8H
    trn2 v25.8H, v30.8H, v29.8H
    trn1 v29.8H, v20.8H, v10.8H
    trn2 v10.8H, v20.8H, v10.8H
    trn1 v21.4S, v12.4S, v26.4S
    trn1 v20.4S, v6.4S, v4.4S
    trn2 v12.4S, v12.4S, v26.4S
    trn2 v26.4S, v6.4S, v4.4S
    trn1 v4.4S, v8.4S, v29.4S
    trn1 v18.4S, v25.4S, v10.4S
    trn2 v29.4S, v8.4S, v29.4S
    trn2 v10.4S, v25.4S, v10.4S
    trn1 v11.2D, v21.2D, v4.2D
    trn2 v16.2D, v21.2D, v4.2D
    trn1 v24.2D, v20.2D, v18.2D
    trn2 v9.2D, v20.2D, v18.2D
    trn1 v23.2D, v12.2D, v29.2D
    trn2 v30.2D, v12.2D, v29.2D
    trn1 v3.2D, v26.2D, v10.2D
    trn2 v19.2D, v26.2D, v10.2D
    ldr q12, [x29, #816]
    ldr q10, [x29, #768]
    ext v26.16B, v10.16B, v10.16B, #14
    ldr q10, [x29, #720]
    ext v8.16B, v10.16B, v10.16B, #12
    ldr q10, [x29, #672]
    ext v4.16B, v10.16B, v10.16B, #10
    ldr q10, [x29, #624]
    ext v25.16B, v10.16B, v10.16B, #8
    ldr q10, [x29, #576]
    ext v29.16B, v10.16B, v10.16B, #6
    ldr q10, [x29, #528]
    ext v21.16B, v10.16B, v10.16B, #4
    ldr q10, [x29, #480]
    ext v10.16B, v10.16B, v10.16B, #2
    ldr q18, [x29, #432]
    trn1 v20.8H, v12.8H, v26.8H
    trn2 v12.8H, v12.8H, v26.8H
    trn1 v26.8H, v8.8H, v4.8H
    trn2 v4.8H, v8.8H, v4.8H
    trn1 v6.8H, v25.8H, v29.8H
    trn2 v8.8H, v25.8H, v29.8H
    trn1 v29.8H, v21.8H, v10.8H
    trn2 v10.8H, v21.8H, v10.8H
    trn1 v25.4S, v20.4S, v26.4S
    trn1 v21.4S, v12.4S, v4.4S
    trn2 v20.4S, v20.4S, v26.4S
    trn2 v12.4S, v12.4S, v4.4S
    trn1 v26.4S, v6.4S, v29.4S
    trn1 v4.4S, v8.4S, v10.4S
    trn2 v29.4S, v6.4S, v29.4S
    trn2 v10.4S, v8.4S, v10.4S
    trn1 v8.2D, v25.2D, v26.2D
    trn2 v31.2D, v25.2D, v26.2D
    trn1 v25.2D, v21.2D, v4.2D
    trn2 v28.2D, v21.2D, v4.2D
    trn1 v21.2D, v20.2D, v29.2D
    trn2 v22.2D, v20.2D, v29.2D
    trn1 v20.2D, v12.2D, v10.2D
    trn2 v27.2D, v12.2D, v10.2D
    ldr q13, [x30, #336]
    ldr q14, [x30, #352]
    ldr q4, [x30, #160]
    orr v10.16B, v11.16B, v11.16B
    ins v10.h[0], v1.h[0]
    tbl v29.16B, {v10.16B}, v4.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v26.8H, v29.8H, v10.8H
    orr v10.16B, v8.16B, v8.16B
    ins v10.h[0], v18.h[0]
    tbl v29.16B, {v10.16B}, v4.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    movi v2.16B, #0
    mov v2.d[0], x21
    mov v2.d[1], x24
    movi v15.16B, #0
    mov v15.d[0], x28
    mov v15.d[1], v29.d[0]
    movi v7.16B, #0
    mov v7.d[0], v29.d[1]
    mov v7.d[1], v10.d[0]
    ldr q12, [x30, #176]
    ldr q4, [x30, #0]
    and v29.16B, v11.16B, v4.16B
    bic v10.16B, v24.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[1], v1.h[1]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v26.8H, v29.8H, v10.8H
    and v29.16B, v8.16B, v4.16B
    bic v10.16B, v25.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[1], v18.h[1]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v12.8H, v29.8H, v14.8H
    mls v29.8H, v12.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    movi v0.16B, #0
    mov v0.d[0], x10
    mov v0.d[1], x1
    movi v17.16B, #0
    mov v17.d[0], x13
    mov v17.d[1], v29.d[0]
    movi v11.16B, #0
    mov v11.d[0], v29.d[1]
    mov v11.d[1], v10.d[0]
    ldr q12, [x30, #192]
    ldr q4, [x30, #16]
    and v29.16B, v24.16B, v4.16B
    bic v10.16B, v23.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[2], v1.h[2]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v26.8H, v29.8H, v10.8H
    and v29.16B, v25.16B, v4.16B
    bic v10.16B, v21.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[2], v18.h[2]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q8, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v8.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    umov x28, v29.d[0]
    umov x24, v29.d[1]
    umov x21, v10.d[0]
    ldr q12, [x30, #208]
    ldr q4, [x30, #32]
    and v29.16B, v23.16B, v4.16B
    bic v10.16B, v3.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[3], v1.h[3]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v26.8H, v29.8H, v10.8H
    and v29.16B, v21.16B, v4.16B
    bic v10.16B, v20.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[3], v18.h[3]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    movi v24.16B, #0
    mov v24.d[0], x23
    mov v24.d[1], x9
    movi v23.16B, #0
    mov v23.d[0], x7
    mov v23.d[1], v29.d[0]
    movi v8.16B, #0
    mov v8.d[0], v29.d[1]
    mov v8.d[1], v10.d[0]
    ldr q12, [x30, #224]
    ldr q4, [x30, #48]
    and v29.16B, v3.16B, v4.16B
    bic v10.16B, v16.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[4], v1.h[4]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v26.8H, v29.8H, v10.8H
    and v29.16B, v20.16B, v4.16B
    bic v10.16B, v31.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[4], v18.h[4]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    movi v25.16B, #0
    mov v25.d[0], x0
    mov v25.d[1], x8
    umov x7, v29.d[0]
    umov x9, v29.d[1]
    umov x16, v10.d[0]
    ldr q12, [x30, #240]
    ldr q4, [x30, #64]
    and v29.16B, v16.16B, v4.16B
    bic v10.16B, v9.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[5], v1.h[5]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v26.8H, v29.8H, v10.8H
    and v29.16B, v31.16B, v4.16B
    bic v10.16B, v28.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[5], v18.h[5]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    umov x23, v29.d[0]
    umov x0, v29.d[1]
    umov x8, v10.d[0]
    ldr q12, [x30, #256]
    ldr q4, [x30, #80]
    and v29.16B, v9.16B, v4.16B
    bic v10.16B, v30.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[6], v1.h[6]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v26.8H, v29.8H, v10.8H
    and v29.16B, v28.16B, v4.16B
    bic v10.16B, v22.16B, v4.16B
    orr v10.16B, v29.16B, v10.16B
    ins v10.h[6], v18.h[6]
    tbl v29.16B, {v10.16B}, v12.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    movi v21.16B, #0
    mov v21.d[0], x6
    mov v21.d[1], x3
    movi v20.16B, #0
    mov v20.d[0], x22
    mov v20.d[1], v29.d[0]
    movi v12.16B, #0
    mov v12.d[0], v29.d[1]
    mov v12.d[1], v10.d[0]
    ldr q4, [x30, #272]
    orr v10.16B, v30.16B, v30.16B
    ins v10.h[7], v1.h[7]
    tbl v29.16B, {v10.16B}, v4.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v26.8H, v29.8H, v10.8H
    orr v10.16B, v22.16B, v22.16B
    ins v10.h[7], v18.h[7]
    tbl v29.16B, {v10.16B}, v4.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    umov x10, v29.d[0]
    umov x1, v29.d[1]
    umov x13, v10.d[0]
    ldr q4, [x30, #288]
    orr v10.16B, v19.16B, v19.16B
    tbl v29.16B, {v10.16B}, v4.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v26.8H, v29.8H, v10.8H
    orr v10.16B, v27.16B, v27.16B
    tbl v29.16B, {v10.16B}, v4.16B
    sqrdmulh v10.8H, v29.8H, v14.8H
    mls v29.8H, v10.8H, v13.8H
    sshr v10.8H, v29.8H, #15
    and v10.16B, v10.16B, v13.16B
    add v29.8H, v29.8H, v10.8H
    xtn v4.8B, v26.8H
    ushr v10.8H, v26.8H, #8
    sli v10.8H, v29.8H, #4
    xtn v5.8B, v10.8H
    ushr v10.8H, v29.8H, #4
    xtn v6.8B, v10.8H
    ldr q10, [x30, #304]
    tbl v29.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    ldr q10, [x30, #320]
    tbl v10.16b, {v4.16b, v5.16b, v6.16b}, v10.16b
    umov x22, v29.d[0]
    umov x6, v29.d[1]
    umov x3, v10.d[0]
    orr v1.16b, v24.16b, v24.16b
    orr v24.16b, v8.16b, v8.16b
    orr v28.16b, v21.16b, v21.16b
    orr v27.16b, v20.16b, v20.16b
    orr v16.16b, v12.16b, v12.16b
    orr v29.16b, v0.16b, v0.16b
    orr v13.16b, v11.16b, v11.16b
    orr v10.16b, v25.16b, v25.16b
    orr v25.16b, v15.16b, v15.16b
    orr v0.16b, v2.16b, v2.16b
    orr v2.16b, v23.16b, v23.16b
    orr v23.16b, v17.16b, v17.16b
    orr v17.16b, v0.16b, v0.16b
    ldr q12, [x29, #832]
    ldr q4, [x29, #784]
    ext v11.16B, v4.16B, v4.16B, #14
    ldr q26, [x29, #736]
    ext v8.16B, v26.16B, v26.16B, #12
    ldr q26, [x29, #688]
    ext v26.16B, v26.16B, v26.16B, #10
    ldr q21, [x29, #640]
    ext v21.16B, v21.16B, v21.16B, #8
    ldr q30, [x29, #592]
    ext v3.16B, v30.16B, v30.16B, #6
    ldr q5, [x29, #544]
    ext v20.16B, v5.16B, v5.16B, #4
    ldr q22, [x29, #496]
    ext v0.16B, v22.16B, v22.16B, #2
    ldr q18, [x29, #448]
    trn1 v6.8H, v12.8H, v11.8H
    trn2 v22.8H, v12.8H, v11.8H
    trn1 v11.8H, v8.8H, v26.8H
    trn2 v14.8H, v8.8H, v26.8H
    trn1 v19.8H, v21.8H, v3.8H
    trn2 v30.8H, v21.8H, v3.8H
    trn1 v12.8H, v20.8H, v0.8H
    trn2 v31.8H, v20.8H, v0.8H
    trn1 v26.4S, v6.4S, v11.4S
    trn2 v3.4S, v6.4S, v11.4S
    trn1 v21.4S, v19.4S, v12.4S
    trn2 v19.4S, v19.4S, v12.4S
    trn1 v6.4S, v22.4S, v14.4S
    trn2 v11.4S, v22.4S, v14.4S
    trn1 v5.4S, v30.4S, v31.4S
    trn2 v9.4S, v30.4S, v31.4S
    trn1 v15.2D, v26.2D, v21.2D
    trn2 v30.2D, v26.2D, v21.2D
    trn1 v14.2D, v6.2D, v5.2D
    trn2 v21.2D, v6.2D, v5.2D
    trn1 v5.2D, v3.2D, v19.2D
    trn2 v20.2D, v3.2D, v19.2D
    trn1 v6.2D, v11.2D, v9.2D
    trn2 v22.2D, v11.2D, v9.2D
    orr v4.16B, v15.16B, v15.16B
    ins v4.h[0], v18.h[0]
    ldr q3, [x30, #160]
    tbl v11.16B, {v4.16B}, v3.16B
    ldr q9, [x30, #0]
    and v8.16B, v15.16B, v9.16B
    bic v31.16B, v14.16B, v9.16B
    orr v4.16B, v8.16B, v31.16B
    ins v4.h[1], v18.h[1]
    ldr q8, [x30, #176]
    tbl v4.16B, {v4.16B}, v8.16B
    ldr q26, [x30, #16]
    and v0.16B, v14.16B, v26.16B
    bic v3.16B, v5.16B, v26.16B
    orr v9.16B, v0.16B, v3.16B
    ins v9.h[2], v18.h[2]
    ldr q14, [x30, #192]
    tbl v0.16B, {v9.16B}, v14.16B
    ldr q31, [x30, #32]
    and v14.16B, v5.16B, v31.16B
    bic v12.16B, v6.16B, v31.16B
    orr v9.16B, v14.16B, v12.16B
    ins v9.h[3], v18.h[3]
    ldr q14, [x30, #208]
    tbl v3.16B, {v9.16B}, v14.16B
    ldr q26, [x30, #48]
    and v19.16B, v6.16B, v26.16B
    bic v31.16B, v30.16B, v26.16B
    orr v9.16B, v19.16B, v31.16B
    ins v9.h[4], v18.h[4]
    ldr q14, [x30, #224]
    tbl v31.16B, {v9.16B}, v14.16B
    ldr q14, [x30, #64]
    and v26.16B, v30.16B, v14.16B
    bic v30.16B, v21.16B, v14.16B
    orr v12.16B, v26.16B, v30.16B
    ins v12.h[5], v18.h[5]
    ldr q5, [x30, #240]
    tbl v14.16B, {v12.16B}, v5.16B
    ldr q5, [x30, #80]
    and v9.16B, v21.16B, v5.16B
    bic v12.16B, v20.16B, v5.16B
    orr v12.16B, v9.16B, v12.16B
    ins v12.h[6], v18.h[6]
    ldr q30, [x30, #256]
    tbl v26.16B, {v12.16B}, v30.16B
    orr v12.16B, v20.16B, v20.16B
    ins v12.h[7], v18.h[7]
    ldr q21, [x30, #272]
    tbl v20.16B, {v12.16B}, v21.16B
    orr v12.16B, v22.16B, v22.16B
    ldr q30, [x30, #288]
    tbl v15.16B, {v12.16B}, v30.16B
    orr v30.16b, v7.16b, v7.16b
    orr v19.16b, v2.16b, v2.16b
    orr v22.16b, v28.16b, v28.16b
    orr v21.16b, v29.16b, v29.16b
    orr v29.16b, v23.16b, v23.16b
    orr v12.16b, v0.16b, v0.16b
    orr v2.16b, v14.16b, v14.16b
    orr v14.16b, v24.16b, v24.16b
    orr v24.16b, v17.16b, v17.16b
    orr v17.16b, v31.16b, v31.16b
    orr v31.16b, v10.16b, v10.16b
    orr v9.16b, v26.16b, v26.16b
    orr v28.16b, v20.16b, v20.16b
    orr v20.16b, v1.16b, v1.16b
    orr v1.16b, v16.16b, v16.16b
    orr v16.16b, v27.16b, v27.16b
    orr v27.16b, v3.16b, v3.16b
    orr v23.16b, v15.16b, v15.16b
    orr v15.16b, v13.16b, v13.16b
    orr v13.16b, v25.16b, v25.16b
    orr v25.16b, v4.16b, v4.16b
    orr v4.16b, v11.16b, v11.16b
    ldr q18, [x30, #336]
    ldr q8, [x30, #352]
    sqrdmulh v0.8H, v4.8H, v8.8H
    mls v4.8H, v0.8H, v18.8H
    sshr v0.8H, v4.8H, #15
    and v0.16B, v0.16B, v18.16B
    add v3.8H, v4.8H, v0.8H
    xtn v0.8B, v3.8H
    movi v7.16B, #0
    mov v7.d[0], v0.d[0]
    ushr v0.8H, v3.8H, #8
    uzp1 v4.8H, v0.8H, v0.8H
    uzp2 v0.8H, v0.8H, v0.8H
    sli v4.8H, v0.8H, #4
    xtn v0.8B, v4.8H
    movi v4.16B, #0
    ins v4.h[0], v0.h[0]
    ins v4.h[1], v0.h[1]
    sqrdmulh v0.8H, v25.8H, v8.8H
    mls v25.8H, v0.8H, v18.8H
    sshr v0.8H, v25.8H, #15
    and v0.16B, v0.16B, v18.16B
    add v3.8H, v25.8H, v0.8H
    xtn v0.8B, v3.8H
    mov v7.d[1], v0.d[0]
    ushr v0.8H, v3.8H, #8
    uzp1 v26.8H, v0.8H, v0.8H
    uzp2 v0.8H, v0.8H, v0.8H
    sli v26.8H, v0.8H, #4
    xtn v0.8B, v26.8H
    ins v4.h[2], v0.h[0]
    ins v4.h[3], v0.h[1]
    sqrdmulh v0.8H, v12.8H, v8.8H
    mls v12.8H, v0.8H, v18.8H
    sshr v0.8H, v12.8H, #15
    and v0.16B, v0.16B, v18.16B
    add v3.8H, v12.8H, v0.8H
    xtn v0.8B, v3.8H
    movi v25.16B, #0
    mov v25.d[0], v0.d[0]
    ushr v0.8H, v3.8H, #8
    uzp1 v11.8H, v0.8H, v0.8H
    uzp2 v0.8H, v0.8H, v0.8H
    sli v11.8H, v0.8H, #4
    xtn v0.8B, v11.8H
    ins v4.h[4], v0.h[0]
    ins v4.h[5], v0.h[1]
    sqrdmulh v0.8H, v27.8H, v8.8H
    mls v27.8H, v0.8H, v18.8H
    sshr v0.8H, v27.8H, #15
    and v0.16B, v0.16B, v18.16B
    add v3.8H, v27.8H, v0.8H
    xtn v0.8B, v3.8H
    mov v25.d[1], v0.d[0]
    ushr v0.8H, v3.8H, #8
    uzp1 v10.8H, v0.8H, v0.8H
    uzp2 v0.8H, v0.8H, v0.8H
    sli v10.8H, v0.8H, #4
    xtn v0.8B, v10.8H
    ins v4.h[6], v0.h[0]
    ins v4.h[7], v0.h[1]
    sqrdmulh v0.8H, v17.8H, v8.8H
    mls v17.8H, v0.8H, v18.8H
    sshr v0.8H, v17.8H, #15
    and v0.16B, v0.16B, v18.16B
    add v3.8H, v17.8H, v0.8H
    xtn v0.8B, v3.8H
    movi v12.16B, #0
    mov v12.d[0], v0.d[0]
    ushr v0.8H, v3.8H, #8
    uzp1 v6.8H, v0.8H, v0.8H
    uzp2 v0.8H, v0.8H, v0.8H
    sli v6.8H, v0.8H, #4
    xtn v0.8B, v6.8H
    movi v27.16B, #0
    ins v27.h[0], v0.h[0]
    ins v27.h[1], v0.h[1]
    sqrdmulh v0.8H, v2.8H, v8.8H
    mls v2.8H, v0.8H, v18.8H
    sshr v0.8H, v2.8H, #15
    and v0.16B, v0.16B, v18.16B
    add v3.8H, v2.8H, v0.8H
    xtn v0.8B, v3.8H
    mov v12.d[1], v0.d[0]
    ushr v0.8H, v3.8H, #8
    uzp1 v6.8H, v0.8H, v0.8H
    uzp2 v0.8H, v0.8H, v0.8H
    sli v6.8H, v0.8H, #4
    xtn v0.8B, v6.8H
    ins v27.h[2], v0.h[0]
    ins v27.h[3], v0.h[1]
    sqrdmulh v0.8H, v9.8H, v8.8H
    mls v9.8H, v0.8H, v18.8H
    sshr v0.8H, v9.8H, #15
    and v0.16B, v0.16B, v18.16B
    add v3.8H, v9.8H, v0.8H
    xtn v0.8B, v3.8H
    movi v17.16B, #0
    mov v17.d[0], v0.d[0]
    ushr v0.8H, v3.8H, #8
    uzp1 v5.8H, v0.8H, v0.8H
    uzp2 v0.8H, v0.8H, v0.8H
    sli v5.8H, v0.8H, #4
    xtn v0.8B, v5.8H
    ins v27.h[4], v0.h[0]
    ins v27.h[5], v0.h[1]
    sqrdmulh v0.8H, v28.8H, v8.8H
    mls v28.8H, v0.8H, v18.8H
    sshr v0.8H, v28.8H, #15
    and v0.16B, v0.16B, v18.16B
    add v3.8H, v28.8H, v0.8H
    xtn v0.8B, v3.8H
    mov v17.d[1], v0.d[0]
    ushr v0.8H, v3.8H, #8
    uzp1 v5.8H, v0.8H, v0.8H
    uzp2 v0.8H, v0.8H, v0.8H
    sli v5.8H, v0.8H, #4
    xtn v0.8B, v5.8H
    ins v27.h[6], v0.h[0]
    ins v27.h[7], v0.h[1]
    sqrdmulh v0.8H, v23.8H, v8.8H
    mls v23.8H, v0.8H, v18.8H
    sshr v0.8H, v23.8H, #15
    and v0.16B, v0.16B, v18.16B
    add v3.8H, v23.8H, v0.8H
    xtn v0.8B, v3.8H
    movi v9.16B, #0
    mov v9.d[0], v0.d[0]
    ushr v0.8H, v3.8H, #8
    uzp1 v18.8H, v0.8H, v0.8H
    uzp2 v0.8H, v0.8H, v0.8H
    sli v18.8H, v0.8H, #4
    xtn v0.8B, v18.8H
    ins v9.h[4], v0.h[0]
    ins v9.h[5], v0.h[1]
    orr v18.16b, v13.16b, v13.16b
    orr v2.16b, v14.16b, v14.16b
    orr v23.16b, v1.16b, v1.16b
    orr v11.16b, v21.16b, v21.16b
    orr v13.16b, v29.16b, v29.16b
    orr v6.16b, v31.16b, v31.16b
    orr v10.16b, v25.16b, v25.16b
    orr v1.16b, v12.16b, v12.16b
    orr v12.16b, v30.16b, v30.16b
    orr v25.16b, v17.16b, v17.16b
    orr v17.16b, v22.16b, v22.16b
    orr v8.16b, v9.16b, v9.16b
    orr v9.16b, v19.16b, v19.16b
    orr v30.16b, v4.16b, v4.16b
    orr v29.16b, v27.16b, v27.16b
    orr v27.16b, v7.16b, v7.16b
    orr v7.16b, v16.16b, v16.16b
    orr v16.16b, v15.16b, v15.16b
    orr v15.16b, v24.16b, v24.16b
    orr v24.16b, v20.16b, v20.16b
    ldr q31, [x29, #848]
    ldr q19, [x29, #800]
    ext v0.16B, v19.16B, v19.16B, #14
    ldr q14, [x29, #752]
    ext v3.16B, v14.16B, v14.16B, #12
    ldr q5, [x29, #704]
    ext v28.16B, v5.16B, v5.16B, #10
    ldr q14, [x29, #656]
    ext v22.16B, v14.16B, v14.16B, #8
    ldr q21, [x29, #608]
    ext v5.16B, v21.16B, v21.16B, #6
    ldr q21, [x29, #560]
    ext v26.16B, v21.16B, v21.16B, #4
    ldr q19, [x29, #512]
    ext v14.16B, v19.16B, v19.16B, #2
    ldr q19, [x29, #464]
    trn1 v21.8H, v31.8H, v0.8H
    trn2 v20.8H, v31.8H, v0.8H
    trn1 v31.8H, v3.8H, v28.8H
    trn2 v3.8H, v3.8H, v28.8H
    trn1 v4.8H, v22.8H, v5.8H
    trn2 v0.8H, v22.8H, v5.8H
    trn1 v5.8H, v26.8H, v14.8H
    trn2 v28.8H, v26.8H, v14.8H
    trn1 v22.4S, v21.4S, v31.4S
    trn2 v26.4S, v21.4S, v31.4S
    trn1 v21.4S, v4.4S, v5.4S
    trn2 v4.4S, v4.4S, v5.4S
    trn1 v14.4S, v20.4S, v3.4S
    trn2 v5.4S, v20.4S, v3.4S
    trn1 v3.4S, v0.4S, v28.4S
    trn2 v0.4S, v0.4S, v28.4S
    trn1 v31.2D, v22.2D, v21.2D
    trn2 v21.2D, v22.2D, v21.2D
    trn1 v28.2D, v14.2D, v3.2D
    trn2 v3.2D, v14.2D, v3.2D
    trn1 v14.2D, v26.2D, v4.2D
    trn2 v20.2D, v26.2D, v4.2D
    trn1 v22.2D, v5.2D, v0.2D
    trn2 v5.2D, v5.2D, v0.2D
    orr v4.16B, v31.16B, v31.16B
    ins v4.h[0], v19.h[0]
    ldr q0, [x30, #160]
    tbl v26.16B, {v4.16B}, v0.16B
    ldr q4, [x30, #0]
    and v0.16B, v31.16B, v4.16B
    bic v31.16B, v28.16B, v4.16B
    orr v4.16B, v0.16B, v31.16B
    ins v4.h[1], v19.h[1]
    ldr q0, [x30, #176]
    tbl v0.16B, {v4.16B}, v0.16B
    ldr q4, [x30, #16]
    and v31.16B, v28.16B, v4.16B
    bic v4.16B, v14.16B, v4.16B
    orr v4.16B, v31.16B, v4.16B
    ins v4.h[2], v19.h[2]
    ldr q31, [x30, #192]
    tbl v31.16B, {v4.16B}, v31.16B
    ldr q28, [x30, #32]
    and v14.16B, v14.16B, v28.16B
    bic v4.16B, v22.16B, v28.16B
    orr v4.16B, v14.16B, v4.16B
    ins v4.h[3], v19.h[3]
    ldr q14, [x30, #208]
    tbl v28.16B, {v4.16B}, v14.16B
    ldr q4, [x30, #48]
    and v22.16B, v22.16B, v4.16B
    bic v14.16B, v21.16B, v4.16B
    orr v4.16B, v22.16B, v14.16B
    ins v4.h[4], v19.h[4]
    ldr q22, [x30, #224]
    tbl v22.16B, {v4.16B}, v22.16B
    ldr q4, [x30, #64]
    and v14.16B, v21.16B, v4.16B
    bic v21.16B, v3.16B, v4.16B
    orr v4.16B, v14.16B, v21.16B
    ins v4.h[5], v19.h[5]
    ldr q14, [x30, #240]
    tbl v21.16B, {v4.16B}, v14.16B
    ldr q4, [x30, #80]
    and v14.16B, v3.16B, v4.16B
    bic v3.16B, v20.16B, v4.16B
    orr v4.16B, v14.16B, v3.16B
    ins v4.h[6], v19.h[6]
    ldr q14, [x30, #256]
    tbl v14.16B, {v4.16B}, v14.16B
    orr v4.16B, v20.16B, v20.16B
    ins v4.h[7], v19.h[7]
    ldr q20, [x30, #272]
    tbl v20.16B, {v4.16B}, v20.16B
    orr v4.16B, v5.16B, v5.16B
    ldr q19, [x30, #288]
    tbl v4.16B, {v4.16B}, v19.16B
    ldr x29, [sp, #160]
    add x29, x29, #648
    orr v5.16b, v24.16b, v24.16b
    orr v3.16b, v11.16b, v11.16b
    orr v24.16b, v13.16b, v13.16b
    orr v13.16b, v2.16b, v2.16b
    orr v19.16b, v10.16b, v10.16b
    orr v11.16b, v30.16b, v30.16b
    orr v30.16b, v12.16b, v12.16b
    orr v12.16b, v28.16b, v28.16b
    orr v28.16b, v15.16b, v15.16b
    orr v15.16b, v6.16b, v6.16b
    orr v6.16b, v17.16b, v17.16b
    orr v2.16b, v14.16b, v14.16b
    orr v14.16b, v23.16b, v23.16b
    orr v23.16b, v0.16b, v0.16b
    orr v10.16b, v4.16b, v4.16b
    orr v4.16b, v22.16b, v22.16b
    orr v22.16b, v21.16b, v21.16b
    orr v21.16b, v8.16b, v8.16b
    orr v8.16b, v9.16b, v9.16b
    orr v9.16b, v7.16b, v7.16b
    orr v7.16b, v29.16b, v29.16b
    orr v29.16b, v18.16b, v18.16b
    orr v0.16b, v16.16b, v16.16b
    orr v16.16b, v27.16b, v27.16b
    orr v27.16b, v0.16b, v0.16b
    orr v0.16b, v1.16b, v1.16b
    orr v1.16b, v31.16b, v31.16b
    orr v31.16b, v26.16b, v26.16b
    orr v26.16b, v20.16b, v20.16b
    orr v20.16b, v0.16b, v0.16b
    ldr q18, [x30, #336]
    ldr q0, [x30, #352]
    sqrdmulh v17.8H, v31.8H, v0.8H
    mls v31.8H, v17.8H, v18.8H
    sshr v17.8H, v31.8H, #15
    and v0.16B, v17.16B, v18.16B
    add v31.8H, v31.8H, v0.8H
    eor v18.16B, v18.16B, v18.16B
    sli v18.8H, v31.8H, #4
    xtn v0.8B, v18.8H
    ushr v18.8H, v31.8H, #4
    xtn v18.8B, v18.8H
    ldr q17, [x30, #608]
    and v31.16B, v11.16B, v17.16B
    ushr v17.16B, v11.16B, #4
    zip1 v17.16B, v31.16B, v17.16B
    orr v17.8B, v0.8B, v17.8B
    ldr q31, [x30, #368]
    tbl v31.16B, {v28.16B, v29.16B}, v31.16B
    ldr q0, [x30, #384]
    tbl v0.16B, {v29.16B, v30.16B}, v0.16B
    orr v0.16B, v31.16B, v0.16B
    ldr q31, [x30, #400]
    tbl v31.16b, {v16.16b, v17.16b, v18.16b}, v31.16b
    orr v0.16B, v0.16B, v31.16B
    str q0, [x29, #0]
    ldr q0, [x30, #416]
    tbl v0.16B, {v28.16B, v29.16B}, v0.16B
    ldr q31, [x30, #432]
    tbl v31.16B, {v29.16B, v30.16B}, v31.16B
    orr v0.16B, v0.16B, v31.16B
    ldr q31, [x30, #448]
    tbl v31.16b, {v16.16b, v17.16b, v18.16b}, v31.16b
    orr v0.16B, v0.16B, v31.16B
    str q0, [x29, #16]
    ldr q0, [x30, #464]
    tbl v0.16B, {v28.16B, v29.16B}, v0.16B
    ldr q31, [x30, #480]
    tbl v31.16B, {v29.16B, v30.16B}, v31.16B
    orr v31.16B, v0.16B, v31.16B
    ldr q0, [x30, #496]
    tbl v0.16b, {v16.16b, v17.16b, v18.16b}, v0.16b
    orr v0.16B, v31.16B, v0.16B
    str q0, [x29, #32]
    ldr q31, [x30, #512]
    tbl v0.16B, {v28.16B, v29.16B}, v31.16B
    ldr q31, [x30, #528]
    tbl v31.16B, {v29.16B, v30.16B}, v31.16B
    orr v31.16B, v0.16B, v31.16B
    ldr q0, [x30, #544]
    tbl v0.16b, {v16.16b, v17.16b, v18.16b}, v0.16b
    orr v0.16B, v31.16B, v0.16B
    str q0, [x29, #48]
    ldr q0, [x30, #560]
    tbl v0.16B, {v28.16B, v29.16B}, v0.16B
    ldr q31, [x30, #576]
    tbl v28.16B, {v29.16B, v30.16B}, v31.16B
    orr v0.16B, v0.16B, v28.16B
    ldr q28, [x30, #592]
    tbl v30.16b, {v16.16b, v17.16b, v18.16b}, v28.16b
    orr v17.16B, v0.16B, v30.16B
    add x29, x29, #64
    orr v18.16b, v27.16b, v27.16b
    orr v27.16b, v6.16b, v6.16b
    orr v6.16b, v1.16b, v1.16b
    orr v1.16b, v15.16b, v15.16b
    orr v15.16b, v5.16b, v5.16b
    orr v31.16b, v4.16b, v4.16b
    orr v4.16b, v20.16b, v20.16b
    orr v5.16b, v22.16b, v22.16b
    orr v20.16b, v10.16b, v10.16b
    orr v10.16b, v23.16b, v23.16b
    orr v23.16b, v25.16b, v25.16b
    orr v25.16b, v3.16b, v3.16b
    orr v3.16b, v12.16b, v12.16b
    orr v12.16b, v24.16b, v24.16b
    orr v24.16b, v16.16b, v16.16b
    orr v16.16b, v8.16b, v8.16b
    orr v8.16b, v26.16b, v26.16b
    orr v26.16b, v11.16b, v11.16b
    orr v11.16b, v7.16b, v7.16b
    orr v7.16b, v14.16b, v14.16b
    orr v0.16b, v13.16b, v13.16b
    orr v13.16b, v21.16b, v21.16b
    orr v21.16b, v17.16b, v17.16b
    orr v17.16b, v0.16b, v0.16b
    orr v0.16b, v19.16b, v19.16b
    orr v19.16b, v2.16b, v2.16b
    orr v2.16b, v0.16b, v0.16b
    ldr q14, [x30, #336]
    ldr q0, [x30, #352]
    sqrdmulh v0.8H, v3.8H, v0.8H
    mls v3.8H, v0.8H, v14.8H
    sshr v0.8H, v3.8H, #15
    and v0.16B, v0.16B, v14.16B
    add v3.8H, v3.8H, v0.8H
    eor v0.16B, v14.16B, v14.16B
    sli v0.8H, v3.8H, #4
    xtn v22.8B, v0.8H
    ushr v0.8H, v3.8H, #4
    xtn v30.8B, v0.8H
    ext v28.16B, v2.16B, v2.16B, #8
    ext v14.16B, v26.16B, v26.16B, #12
    ldr q0, [x30, #608]
    and v3.16B, v14.16B, v0.16B
    ushr v0.16B, v14.16B, #4
    zip1 v0.16B, v3.16B, v0.16B
    orr v29.8B, v22.8B, v0.8B
    ldr q0, [x30, #368]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #384]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #400]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v22.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v21.d[0]
    mov v0.d[1], v22.d[0]
    str q0, [x29, #0]
    ldr q0, [x30, #416]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #432]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #448]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v14.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v22.d[1]
    mov v0.d[1], v14.d[0]
    str q0, [x29, #16]
    ldr q0, [x30, #464]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #480]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #496]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v22.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v14.d[1]
    mov v0.d[1], v22.d[0]
    str q0, [x29, #32]
    ldr q0, [x30, #512]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #528]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #544]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v14.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v22.d[1]
    mov v0.d[1], v14.d[0]
    str q0, [x29, #48]
    ldr q0, [x30, #560]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #576]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #592]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v3.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v14.d[1]
    mov v0.d[1], v3.d[0]
    str q0, [x29, #64]
    add x29, x29, #80
    orr v15.16b, v27.16b, v27.16b
    orr v16.16b, v9.16b, v9.16b
    orr v17.16b, v7.16b, v7.16b
    orr v27.16b, v1.16b, v1.16b
    orr v1.16b, v25.16b, v25.16b
    orr v28.16b, v24.16b, v24.16b
    orr v24.16b, v12.16b, v12.16b
    orr v3.16b, v19.16b, v19.16b
    orr v19.16b, v6.16b, v6.16b
    orr v6.16b, v26.16b, v26.16b
    orr v26.16b, v4.16b, v4.16b
    orr v21.16b, v8.16b, v8.16b
    orr v8.16b, v31.16b, v31.16b
    orr v31.16b, v11.16b, v11.16b
    orr v11.16b, v23.16b, v23.16b
    orr v23.16b, v2.16b, v2.16b
    orr v2.16b, v18.16b, v18.16b
    orr v30.16b, v20.16b, v20.16b
    orr v20.16b, v5.16b, v5.16b
    orr v5.16b, v10.16b, v10.16b
    orr v10.16b, v13.16b, v13.16b
    ldr q14, [x30, #336]
    ldr q0, [x30, #352]
    sqrdmulh v0.8H, v3.8H, v0.8H
    mls v3.8H, v0.8H, v14.8H
    sshr v0.8H, v3.8H, #15
    and v0.16B, v0.16B, v14.16B
    add v3.8H, v3.8H, v0.8H
    eor v0.16B, v14.16B, v14.16B
    sli v0.8H, v3.8H, #4
    xtn v22.8B, v0.8H
    ushr v0.8H, v3.8H, #4
    xtn v13.8B, v0.8H
    ext v14.16B, v31.16B, v31.16B, #8
    ldr q0, [x30, #608]
    and v3.16B, v14.16B, v0.16B
    ushr v0.16B, v14.16B, #4
    zip1 v0.16B, v3.16B, v0.16B
    orr v12.8B, v22.8B, v0.8B
    ldr q0, [x30, #368]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #384]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #400]
    tbl v0.16b, {v11.16b, v12.16b, v13.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #0]
    ldr q0, [x30, #416]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #432]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #448]
    tbl v0.16b, {v11.16b, v12.16b, v13.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #16]
    ldr q0, [x30, #464]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #480]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #496]
    tbl v0.16b, {v11.16b, v12.16b, v13.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #32]
    ldr q0, [x30, #512]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #528]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #544]
    tbl v0.16b, {v11.16b, v12.16b, v13.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #48]
    ldr q0, [x30, #560]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #576]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #592]
    tbl v0.16b, {v11.16b, v12.16b, v13.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    add x29, x29, #64
    orr v15.16b, v1.16b, v1.16b
    orr v16.16b, v24.16b, v24.16b
    orr v17.16b, v2.16b, v2.16b
    orr v2.16b, v27.16b, v27.16b
    orr v13.16b, v26.16b, v26.16b
    orr v26.16b, v11.16b, v11.16b
    orr v11.16b, v10.16b, v10.16b
    orr v10.16b, v6.16b, v6.16b
    orr v6.16b, v31.16b, v31.16b
    orr v3.16b, v5.16b, v5.16b
    orr v31.16b, v19.16b, v19.16b
    orr v5.16b, v8.16b, v8.16b
    orr v19.16b, v20.16b, v20.16b
    orr v8.16b, v21.16b, v21.16b
    orr v20.16b, v30.16b, v30.16b
    orr v21.16b, v0.16b, v0.16b
    ldr q14, [x30, #336]
    ldr q0, [x30, #352]
    sqrdmulh v0.8H, v3.8H, v0.8H
    mls v3.8H, v0.8H, v14.8H
    sshr v0.8H, v3.8H, #15
    and v0.16B, v0.16B, v14.16B
    add v3.8H, v3.8H, v0.8H
    eor v0.16B, v14.16B, v14.16B
    sli v0.8H, v3.8H, #4
    xtn v22.8B, v0.8H
    ushr v0.8H, v3.8H, #4
    xtn v30.8B, v0.8H
    ext v28.16B, v28.16B, v28.16B, #8
    ext v14.16B, v10.16B, v10.16B, #4
    ldr q0, [x30, #608]
    and v3.16B, v14.16B, v0.16B
    ushr v0.16B, v14.16B, #4
    zip1 v0.16B, v3.16B, v0.16B
    orr v29.8B, v22.8B, v0.8B
    ldr q0, [x30, #368]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #384]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #400]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v22.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v21.d[0]
    mov v0.d[1], v22.d[0]
    str q0, [x29, #0]
    ldr q0, [x30, #416]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #432]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #448]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v14.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v22.d[1]
    mov v0.d[1], v14.d[0]
    str q0, [x29, #16]
    ldr q0, [x30, #464]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #480]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #496]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v22.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v14.d[1]
    mov v0.d[1], v22.d[0]
    str q0, [x29, #32]
    ldr q0, [x30, #512]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #528]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #544]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v14.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v22.d[1]
    mov v0.d[1], v14.d[0]
    str q0, [x29, #48]
    ldr q0, [x30, #560]
    tbl v3.16B, {v15.16B, v16.16B}, v0.16B
    ldr q0, [x30, #576]
    tbl v0.16B, {v16.16B, v17.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #592]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v3.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v14.d[1]
    mov v0.d[1], v3.d[0]
    str q0, [x29, #64]
    add x29, x29, #80
    orr v3.16b, v5.16b, v5.16b
    orr v5.16b, v11.16b, v11.16b
    orr v21.16b, v19.16b, v19.16b
    orr v19.16b, v10.16b, v10.16b
    orr v10.16b, v13.16b, v13.16b
    orr v30.16b, v8.16b, v8.16b
    orr v8.16b, v6.16b, v6.16b
    orr v6.16b, v23.16b, v23.16b
    orr v22.16b, v20.16b, v20.16b
    orr v20.16b, v31.16b, v31.16b
    orr v31.16b, v26.16b, v26.16b
    orr v26.16b, v2.16b, v2.16b
    movi v27.16B, #0
    mov v27.d[0], x17
    mov v27.d[1], x7
    movi v28.16B, #0
    mov v28.d[0], x9
    mov v28.d[1], x16
    ldr q14, [x30, #336]
    ldr q0, [x30, #352]
    sqrdmulh v0.8H, v3.8H, v0.8H
    mls v3.8H, v0.8H, v14.8H
    sshr v0.8H, v3.8H, #15
    and v0.16B, v0.16B, v14.16B
    add v3.8H, v3.8H, v0.8H
    eor v0.16B, v14.16B, v14.16B
    sli v0.8H, v3.8H, #4
    xtn v14.8B, v0.8H
    ushr v0.8H, v3.8H, #4
    xtn v12.8B, v0.8H
    ldr q0, [x30, #608]
    and v3.16B, v8.16B, v0.16B
    ushr v0.16B, v8.16B, #4
    zip1 v0.16B, v3.16B, v0.16B
    orr v11.8B, v14.8B, v0.8B
    ldr q0, [x30, #368]
    tbl v3.16B, {v26.16B, v27.16B}, v0.16B
    ldr q0, [x30, #384]
    tbl v0.16B, {v27.16B, v28.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #400]
    tbl v0.16b, {v10.16b, v11.16b, v12.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #0]
    ldr q0, [x30, #416]
    tbl v3.16B, {v26.16B, v27.16B}, v0.16B
    ldr q0, [x30, #432]
    tbl v0.16B, {v27.16B, v28.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #448]
    tbl v0.16b, {v10.16b, v11.16b, v12.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #16]
    ldr q0, [x30, #464]
    tbl v3.16B, {v26.16B, v27.16B}, v0.16B
    ldr q0, [x30, #480]
    tbl v0.16B, {v27.16B, v28.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #496]
    tbl v0.16b, {v10.16b, v11.16b, v12.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #32]
    ldr q0, [x30, #512]
    tbl v3.16B, {v26.16B, v27.16B}, v0.16B
    ldr q0, [x30, #528]
    tbl v0.16B, {v27.16B, v28.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #544]
    tbl v0.16b, {v10.16b, v11.16b, v12.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #48]
    ldr q0, [x30, #560]
    tbl v3.16B, {v26.16B, v27.16B}, v0.16B
    ldr q0, [x30, #576]
    tbl v0.16B, {v27.16B, v28.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #592]
    tbl v0.16b, {v10.16b, v11.16b, v12.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    add x29, x29, #64
    orr v23.16b, v6.16b, v6.16b
    orr v13.16b, v10.16b, v10.16b
    orr v26.16b, v31.16b, v31.16b
    orr v11.16b, v5.16b, v5.16b
    orr v6.16b, v19.16b, v19.16b
    orr v31.16b, v8.16b, v8.16b
    orr v5.16b, v20.16b, v20.16b
    orr v19.16b, v21.16b, v21.16b
    orr v3.16b, v30.16b, v30.16b
    orr v20.16b, v22.16b, v22.16b
    orr v21.16b, v0.16b, v0.16b
    movi v8.16B, #0
    mov v8.d[0], x14
    mov v8.d[1], x5
    movi v9.16B, #0
    mov v9.d[0], x27
    mov v9.d[1], x10
    movi v10.16B, #0
    mov v10.d[0], x1
    mov v10.d[1], x13
    ldr q14, [x30, #336]
    ldr q0, [x30, #352]
    sqrdmulh v0.8H, v3.8H, v0.8H
    mls v3.8H, v0.8H, v14.8H
    sshr v0.8H, v3.8H, #15
    and v0.16B, v0.16B, v14.16B
    add v3.8H, v3.8H, v0.8H
    eor v0.16B, v14.16B, v14.16B
    sli v0.8H, v3.8H, #4
    xtn v22.8B, v0.8H
    ushr v0.8H, v3.8H, #4
    xtn v30.8B, v0.8H
    ext v28.16B, v26.16B, v26.16B, #8
    ext v14.16B, v31.16B, v31.16B, #12
    ldr q0, [x30, #608]
    and v3.16B, v14.16B, v0.16B
    ushr v0.16B, v14.16B, #4
    zip1 v0.16B, v3.16B, v0.16B
    orr v29.8B, v22.8B, v0.8B
    ldr q0, [x30, #368]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #384]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #400]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v22.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v21.d[0]
    mov v0.d[1], v22.d[0]
    str q0, [x29, #0]
    ldr q0, [x30, #416]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #432]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #448]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v14.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v22.d[1]
    mov v0.d[1], v14.d[0]
    str q0, [x29, #16]
    ldr q0, [x30, #464]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #480]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #496]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v22.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v14.d[1]
    mov v0.d[1], v22.d[0]
    str q0, [x29, #32]
    ldr q0, [x30, #512]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #528]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #544]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v14.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v22.d[1]
    mov v0.d[1], v14.d[0]
    str q0, [x29, #48]
    ldr q0, [x30, #560]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #576]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #592]
    tbl v0.16b, {v28.16b, v29.16b, v30.16b}, v0.16b
    orr v3.16B, v3.16B, v0.16B
    movi v0.16B, #0
    mov v0.d[0], v14.d[1]
    mov v0.d[1], v3.d[0]
    str q0, [x29, #64]
    add x29, x29, #80
    orr v3.16b, v5.16b, v5.16b
    orr v5.16b, v11.16b, v11.16b
    orr v11.16b, v23.16b, v23.16b
    orr v21.16b, v19.16b, v19.16b
    orr v19.16b, v6.16b, v6.16b
    orr v30.16b, v20.16b, v20.16b
    orr v20.16b, v31.16b, v31.16b
    orr v31.16b, v13.16b, v13.16b
    movi v8.16B, #0
    mov v8.d[0], x2
    mov v8.d[1], x19
    movi v9.16B, #0
    mov v9.d[0], x20
    mov v9.d[1], x28
    movi v10.16B, #0
    mov v10.d[0], x24
    mov v10.d[1], x21
    ldr q14, [x30, #336]
    ldr q0, [x30, #352]
    sqrdmulh v0.8H, v3.8H, v0.8H
    mls v3.8H, v0.8H, v14.8H
    sshr v0.8H, v3.8H, #15
    and v0.16B, v0.16B, v14.16B
    add v3.8H, v3.8H, v0.8H
    eor v0.16B, v14.16B, v14.16B
    sli v0.8H, v3.8H, #4
    xtn v22.8B, v0.8H
    ushr v0.8H, v3.8H, #4
    xtn v13.8B, v0.8H
    ext v14.16B, v19.16B, v19.16B, #8
    ldr q0, [x30, #608]
    and v3.16B, v14.16B, v0.16B
    ushr v0.16B, v14.16B, #4
    zip1 v0.16B, v3.16B, v0.16B
    orr v12.8B, v22.8B, v0.8B
    ldr q0, [x30, #368]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #384]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #400]
    tbl v0.16b, {v11.16b, v12.16b, v13.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #0]
    ldr q0, [x30, #416]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #432]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #448]
    tbl v0.16b, {v11.16b, v12.16b, v13.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #16]
    ldr q0, [x30, #464]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #480]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #496]
    tbl v0.16b, {v11.16b, v12.16b, v13.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #32]
    ldr q0, [x30, #512]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #528]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #544]
    tbl v0.16b, {v11.16b, v12.16b, v13.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #48]
    ldr q0, [x30, #560]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #576]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #592]
    tbl v0.16b, {v11.16b, v12.16b, v13.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    add x29, x29, #64
    orr v1.16b, v20.16b, v20.16b
    orr v20.16b, v5.16b, v5.16b
    orr v23.16b, v21.16b, v21.16b
    orr v21.16b, v30.16b, v30.16b
    orr v26.16b, v0.16b, v0.16b
    orr v0.16b, v31.16b, v31.16b
    movi v8.16B, #0
    mov v8.d[0], x15
    mov v8.d[1], x26
    movi v9.16B, #0
    mov v9.d[0], x12
    mov v9.d[1], x23
    movi v10.16B, #0
    mov v10.d[0], x0
    mov v10.d[1], x8
    ldr q4, [x30, #336]
    ldr q29, [x30, #352]
    sqrdmulh v19.8H, v23.8H, v29.8H
    mls v23.8H, v19.8H, v4.8H
    sshr v2.8H, v23.8H, #15
    and v3.16B, v2.16B, v4.16B
    add v28.8H, v23.8H, v3.8H
    eor v5.16B, v4.16B, v4.16B
    sli v5.8H, v28.8H, #4
    xtn v15.8B, v5.8H
    ushr v30.8H, v28.8H, #4
    xtn v16.8B, v30.8H
    ext v14.16B, v0.16B, v0.16B, #8
    ext v0.16B, v1.16B, v1.16B, #4
    ldr q28, [x30, #608]
    and v27.16B, v0.16B, v28.16B
    ushr v29.16B, v0.16B, #4
    zip1 v27.16B, v27.16B, v29.16B
    orr v15.8B, v15.8B, v27.8B
    ldr q11, [x30, #368]
    tbl v30.16B, {v8.16B, v9.16B}, v11.16B
    ldr q6, [x30, #384]
    tbl v13.16B, {v9.16B, v10.16B}, v6.16B
    orr v30.16B, v30.16B, v13.16B
    ldr q4, [x30, #400]
    tbl v25.16b, {v14.16b, v15.16b, v16.16b}, v4.16b
    orr v23.16B, v30.16B, v25.16B
    movi v0.16B, #0
    mov v0.d[0], v26.d[0]
    mov v0.d[1], v23.d[0]
    str q0, [x29, #0]
    ldr q22, [x30, #416]
    tbl v30.16B, {v8.16B, v9.16B}, v22.16B
    ldr q29, [x30, #432]
    tbl v31.16B, {v9.16B, v10.16B}, v29.16B
    orr v19.16B, v30.16B, v31.16B
    ldr q29, [x30, #448]
    tbl v26.16b, {v14.16b, v15.16b, v16.16b}, v29.16b
    orr v13.16B, v19.16B, v26.16B
    movi v3.16B, #0
    mov v3.d[0], v23.d[1]
    mov v3.d[1], v13.d[0]
    str q3, [x29, #16]
    ldr q23, [x30, #464]
    tbl v19.16B, {v8.16B, v9.16B}, v23.16B
    ldr q24, [x30, #480]
    tbl v5.16B, {v9.16B, v10.16B}, v24.16B
    orr v12.16B, v19.16B, v5.16B
    ldr q4, [x30, #496]
    tbl v17.16b, {v14.16b, v15.16b, v16.16b}, v4.16b
    orr v25.16B, v12.16B, v17.16B
    movi v4.16B, #0
    mov v4.d[0], v13.d[1]
    mov v4.d[1], v25.d[0]
    str q4, [x29, #32]
    ldr q6, [x30, #512]
    tbl v18.16B, {v8.16B, v9.16B}, v6.16B
    ldr q4, [x30, #528]
    tbl v1.16B, {v9.16B, v10.16B}, v4.16B
    orr v3.16B, v18.16B, v1.16B
    ldr q13, [x30, #544]
    tbl v26.16b, {v14.16b, v15.16b, v16.16b}, v13.16b
    orr v12.16B, v3.16B, v26.16B
    movi v19.16B, #0
    mov v19.d[0], v25.d[1]
    mov v19.d[1], v12.d[0]
    str q19, [x29, #48]
    ldr q30, [x30, #560]
    tbl v8.16B, {v8.16B, v9.16B}, v30.16B
    ldr q5, [x30, #576]
    tbl v0.16B, {v9.16B, v10.16B}, v5.16B
    orr v7.16B, v8.16B, v0.16B
    ldr q5, [x30, #592]
    tbl v15.16b, {v14.16b, v15.16b, v16.16b}, v5.16b
    orr v16.16B, v7.16B, v15.16B
    movi v25.16B, #0
    mov v25.d[0], v12.d[1]
    mov v25.d[1], v16.d[0]
    str q25, [x29, #64]
    add x29, x29, #80
    orr v3.16b, v21.16b, v21.16b
    orr v21.16b, v20.16b, v20.16b
    movi v8.16B, #0
    mov v8.d[0], x11
    mov v8.d[1], x4
    movi v9.16B, #0
    mov v9.d[0], x25
    mov v9.d[1], x22
    movi v10.16B, #0
    mov v10.d[0], x6
    mov v10.d[1], x3
    ldr q14, [x30, #336]
    ldr q0, [x30, #352]
    sqrdmulh v0.8H, v3.8H, v0.8H
    mls v3.8H, v0.8H, v14.8H
    sshr v0.8H, v3.8H, #15
    and v0.16B, v0.16B, v14.16B
    add v3.8H, v3.8H, v0.8H
    eor v0.16B, v14.16B, v14.16B
    sli v0.8H, v3.8H, #4
    xtn v22.8B, v0.8H
    ushr v0.8H, v3.8H, #4
    xtn v23.8B, v0.8H
    ext v14.16B, v21.16B, v21.16B, #8
    ldr q0, [x30, #608]
    and v3.16B, v14.16B, v0.16B
    ushr v0.16B, v14.16B, #4
    zip1 v0.16B, v3.16B, v0.16B
    orr v22.8B, v22.8B, v0.8B
    ldr q0, [x30, #368]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #384]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #400]
    tbl v0.16b, {v21.16b, v22.16b, v23.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #0]
    ldr q0, [x30, #416]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #432]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #448]
    tbl v0.16b, {v21.16b, v22.16b, v23.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #16]
    ldr q0, [x30, #464]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #480]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #496]
    tbl v0.16b, {v21.16b, v22.16b, v23.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #32]
    ldr q0, [x30, #512]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #528]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #544]
    tbl v0.16b, {v21.16b, v22.16b, v23.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str q0, [x29, #48]
    ldr q0, [x30, #560]
    tbl v3.16B, {v8.16B, v9.16B}, v0.16B
    ldr q0, [x30, #576]
    tbl v0.16B, {v9.16B, v10.16B}, v0.16B
    orr v3.16B, v3.16B, v0.16B
    ldr q0, [x30, #592]
    tbl v0.16b, {v21.16b, v22.16b, v23.16b}, v0.16b
    orr v0.16B, v3.16B, v0.16B
    str d0, [x29, #64]
    ldr x0, [sp, #160]
    ldp d8, d9, [sp, #96]
    ldp d10, d11, [sp, #112]
    ldp d12, d13, [sp, #128]
    ldp d14, d15, [sp, #144]
    ldp x19, x20, [sp, #0]
    ldp x21, x22, [sp, #16]
    ldp x23, x24, [sp, #32]
    ldp x25, x26, [sp, #48]
    ldp x27, x28, [sp, #64]
    ldp x29, x30, [sp, #80]
    add sp, sp, #176
    ret
.p2align 4
.Lp6d3_tables:
    .byte 255, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    .byte 255, 255, 255, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    .byte 255, 255, 255, 255, 255, 255, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    .byte 255, 255, 255, 255, 255, 255, 255, 255, 0, 0, 0, 0, 0, 0, 0, 0
    .byte 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 0, 0, 0, 0, 0, 0
    .byte 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 0, 0, 0, 0
    .byte 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 0, 0
    .byte 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    .byte 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    .byte 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0
    .byte 0, 1, 8, 9, 12, 13, 4, 5, 14, 15, 6, 7, 10, 11, 2, 3
    .byte 2, 3, 8, 9, 12, 13, 4, 5, 14, 15, 6, 7, 10, 11, 0, 1
    .byte 4, 5, 8, 9, 12, 13, 2, 3, 14, 15, 6, 7, 10, 11, 0, 1
    .byte 6, 7, 8, 9, 12, 13, 2, 3, 14, 15, 4, 5, 10, 11, 0, 1
    .byte 8, 9, 6, 7, 12, 13, 2, 3, 14, 15, 4, 5, 10, 11, 0, 1
    .byte 10, 11, 6, 7, 12, 13, 2, 3, 14, 15, 4, 5, 8, 9, 0, 1
    .byte 12, 13, 6, 7, 10, 11, 2, 3, 14, 15, 4, 5, 8, 9, 0, 1
    .byte 14, 15, 6, 7, 10, 11, 2, 3, 12, 13, 4, 5, 8, 9, 0, 1
    .byte 14, 15, 6, 7, 10, 11, 2, 3, 12, 13, 4, 5, 8, 9, 0, 1
    .byte 0, 16, 32, 1, 17, 33, 2, 18, 34, 3, 19, 35, 4, 20, 36, 5
    .byte 21, 37, 6, 22, 38, 7, 23, 39, 255, 255, 255, 255, 255, 255, 255, 255
    .byte 129, 13, 129, 13, 129, 13, 129, 13, 129, 13, 129, 13, 129, 13, 129, 13
    .byte 9, 0, 9, 0, 9, 0, 9, 0, 9, 0, 9, 0, 9, 0, 9, 0
    .byte 0, 1, 2, 255, 255, 255, 255, 255, 255, 3, 4, 5, 255, 255, 255, 255
    .byte 255, 255, 255, 8, 9, 10, 255, 255, 255, 255, 255, 255, 11, 12, 13, 255
    .byte 255, 255, 255, 255, 255, 255, 0, 16, 32, 255, 255, 255, 255, 255, 255, 1
    .byte 255, 255, 6, 7, 8, 255, 255, 255, 255, 255, 255, 9, 10, 11, 255, 255
    .byte 255, 255, 255, 255, 255, 14, 15, 16, 255, 255, 255, 255, 255, 255, 17, 18
    .byte 17, 33, 255, 255, 255, 255, 255, 255, 2, 18, 34, 255, 255, 255, 255, 255
    .byte 255, 255, 255, 255, 12, 13, 14, 255, 255, 255, 255, 255, 255, 15, 16, 17
    .byte 19, 255, 255, 255, 255, 255, 255, 20, 21, 22, 255, 255, 255, 255, 255, 255
    .byte 255, 3, 19, 35, 255, 255, 255, 255, 255, 255, 4, 20, 36, 255, 255, 255
    .byte 255, 255, 255, 255, 255, 255, 18, 19, 20, 255, 255, 255, 255, 255, 255, 21
    .byte 23, 24, 25, 255, 255, 255, 255, 255, 255, 26, 27, 28, 255, 255, 255, 255
    .byte 255, 255, 255, 5, 21, 37, 255, 255, 255, 255, 255, 255, 6, 22, 38, 255
    .byte 22, 23, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255
    .byte 255, 255, 29, 30, 31, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255, 255
    .byte 255, 255, 255, 255, 255, 7, 23, 39, 255, 255, 255, 255, 255, 255, 255, 255
    .byte 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15, 15
