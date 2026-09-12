/* Test-only P19 probe for the complete P18 public assembly boundary. */
.text
.p2align 4
.global p19_probe
.type p19_probe, %function
p19_probe:
    stp x29, x30, [sp, #-128]!
    mov x29, sp
    stp x19, x20, [sp, #16]
    str x21, [sp, #32]
    stp d8, d9, [sp, #48]
    stp d10, d11, [sp, #64]
    stp d12, d13, [sp, #80]
    stp d14, d15, [sp, #96]
    mov x19, x0
    mov x20, x1
    mov x21, x2

    movi v0.16b, #0x5a
    movi v1.16b, #0x5a
    movi v2.16b, #0x5a
    movi v3.16b, #0x5a
    movi v4.16b, #0x5a
    movi v5.16b, #0x5a
    movi v6.16b, #0x5a
    movi v7.16b, #0x5a
    movi v8.16b, #0x5a
    movi v9.16b, #0x5a
    movi v10.16b, #0x5a
    movi v11.16b, #0x5a
    movi v12.16b, #0x5a
    movi v13.16b, #0x5a
    movi v14.16b, #0x5a
    movi v15.16b, #0x5a
    movi v16.16b, #0x5a
    movi v17.16b, #0x5a
    movi v18.16b, #0x5a
    movi v19.16b, #0x5a
    movi v20.16b, #0x5a
    movi v21.16b, #0x5a
    movi v22.16b, #0x5a
    movi v23.16b, #0x5a
    movi v24.16b, #0x5a
    movi v25.16b, #0x5a
    movi v26.16b, #0x5a
    movi v27.16b, #0x5a
    movi v28.16b, #0x5a
    movi v29.16b, #0x5a
    movi v30.16b, #0x5a
    movi v31.16b, #0x5a
    movz x9, #0x7788
    movk x9, #0x5566, lsl #16
    movk x9, #0x3344, lsl #32
    movk x9, #0x1122, lsl #48
    fmov d8, x9
    fmov d9, x9
    fmov d10, x9
    fmov d11, x9
    fmov d12, x9
    fmov d13, x9
    fmov d14, x9
    fmov d15, x9

    mov x0, x20
    mov x1, x21
    blr x19

    movz x9, #0x7788
    movk x9, #0x5566, lsl #16
    movk x9, #0x3344, lsl #32
    movk x9, #0x1122, lsl #48
    umov x10, v8.d[0]
    cmp x10, x9
    b.ne .Lp19_fail
    umov x10, v8.d[1]
    cbnz x10, .Lp19_fail
    umov x10, v9.d[0]
    cmp x10, x9
    b.ne .Lp19_fail
    umov x10, v9.d[1]
    cbnz x10, .Lp19_fail
    umov x10, v10.d[0]
    cmp x10, x9
    b.ne .Lp19_fail
    umov x10, v10.d[1]
    cbnz x10, .Lp19_fail
    umov x10, v11.d[0]
    cmp x10, x9
    b.ne .Lp19_fail
    umov x10, v11.d[1]
    cbnz x10, .Lp19_fail
    umov x10, v12.d[0]
    cmp x10, x9
    b.ne .Lp19_fail
    umov x10, v12.d[1]
    cbnz x10, .Lp19_fail
    umov x10, v13.d[0]
    cmp x10, x9
    b.ne .Lp19_fail
    umov x10, v13.d[1]
    cbnz x10, .Lp19_fail
    umov x10, v14.d[0]
    cmp x10, x9
    b.ne .Lp19_fail
    umov x10, v14.d[1]
    cbnz x10, .Lp19_fail
    umov x10, v15.d[0]
    cmp x10, x9
    b.ne .Lp19_fail
    umov x10, v15.d[1]
    cbnz x10, .Lp19_fail

    orr v0.16b, v0.16b, v1.16b
    orr v0.16b, v0.16b, v2.16b
    orr v0.16b, v0.16b, v3.16b
    orr v0.16b, v0.16b, v4.16b
    orr v0.16b, v0.16b, v5.16b
    orr v0.16b, v0.16b, v6.16b
    orr v0.16b, v0.16b, v7.16b
    orr v0.16b, v0.16b, v16.16b
    orr v0.16b, v0.16b, v17.16b
    orr v0.16b, v0.16b, v18.16b
    orr v0.16b, v0.16b, v19.16b
    orr v0.16b, v0.16b, v20.16b
    orr v0.16b, v0.16b, v21.16b
    orr v0.16b, v0.16b, v22.16b
    orr v0.16b, v0.16b, v23.16b
    orr v0.16b, v0.16b, v24.16b
    orr v0.16b, v0.16b, v25.16b
    orr v0.16b, v0.16b, v26.16b
    orr v0.16b, v0.16b, v27.16b
    orr v0.16b, v0.16b, v28.16b
    orr v0.16b, v0.16b, v29.16b
    orr v0.16b, v0.16b, v30.16b
    orr v0.16b, v0.16b, v31.16b
    umov x10, v0.d[0]
    cbnz x10, .Lp19_fail
    umov x10, v0.d[1]
    cbnz x10, .Lp19_fail
    mov w0, #0
    b .Lp19_restore
.Lp19_fail:
    mov w0, #1
.Lp19_restore:
    ldp d8, d9, [sp, #48]
    ldp d10, d11, [sp, #64]
    ldp d12, d13, [sp, #80]
    ldp d14, d15, [sp, #96]
    ldr x21, [sp, #32]
    ldp x19, x20, [sp, #16]
    ldp x29, x30, [sp], #128
    ret
.size p19_probe, .-p19_probe
