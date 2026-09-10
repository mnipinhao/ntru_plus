.text
.p2align 4
.global p6_empty_bridge
p6_empty_bridge:
1:  subs x0, x0, #1
    b.ne 1b
    ret

/* Current per-top scratch boundary: 18 full 3xD stores and 36 Q/D loads. */
.p2align 4
.global p6_memory_bridge
p6_memory_bridge:
    movi v0.16b, #1
    movi v1.16b, #2
    movi v2.16b, #3
1:  mov x2, x0
    .rept 18
    st3 {v0.8b, v1.8b, v2.8b}, [x2], #24
    .endr
    mov x2, x0
    .rept 18
    ldr q16, [x2], #16
    ldr d17, [x2], #8
    .endr
    subs x1, x1, #1
    b.ne 1b
    ret

/*
 * Optimistic minimum register bridge. x18 is used only by this Linux timing
 * proxy so all 28 remaining data GPRs are available; production must remain
 * cross-platform and therefore cannot claim this as an allocated kernel.
 */
.p2align 4
.global p6_gpr_bridge
p6_gpr_bridge:
    sub sp, sp, #80
    stp x19, x20, [sp, #0]
    stp x21, x22, [sp, #16]
    stp x23, x24, [sp, #32]
    stp x25, x26, [sp, #48]
    stp x27, x28, [sp, #64]
    mov x18, x0
    movi v0.16b, #1
    movi v1.16b, #2
    movi v2.16b, #3
    movi v3.16b, #4
    movi v4.16b, #5
    movi v5.16b, #6
    movi v6.16b, #7
    movi v7.16b, #8
    movi v8.16b, #9
    movi v9.16b, #10
    movi v10.16b, #11
    movi v11.16b, #12
    movi v12.16b, #13
    movi v13.16b, #14
1:
    umov x0, v0.d[0]
    umov x1, v0.d[1]
    umov x2, v1.d[0]
    umov x3, v1.d[1]
    umov x4, v2.d[0]
    umov x5, v2.d[1]
    umov x6, v3.d[0]
    umov x7, v3.d[1]
    umov x8, v4.d[0]
    umov x9, v4.d[1]
    umov x10, v5.d[0]
    umov x11, v5.d[1]
    umov x12, v6.d[0]
    umov x13, v6.d[1]
    umov x14, v7.d[0]
    umov x15, v7.d[1]
    umov x16, v8.d[0]
    umov x17, v8.d[1]
    umov x19, v9.d[0]
    umov x20, v9.d[1]
    umov x21, v10.d[0]
    umov x22, v10.d[1]
    umov x23, v11.d[0]
    umov x24, v11.d[1]
    umov x25, v12.d[0]
    umov x26, v12.d[1]
    umov x27, v13.d[0]
    umov x28, v13.d[1]
    fmov d16, x0
    ins v16.d[1], x1
    fmov d17, x2
    ins v17.d[1], x3
    fmov d19, x4
    ins v19.d[1], x5
    fmov d20, x6
    ins v20.d[1], x7
    fmov d21, x8
    ins v21.d[1], x9
    fmov d22, x10
    ins v22.d[1], x11
    fmov d23, x12
    ins v23.d[1], x13
    fmov d24, x14
    ins v24.d[1], x15
    fmov d25, x16
    ins v25.d[1], x17
    fmov d26, x19
    ins v26.d[1], x20
    fmov d27, x21
    ins v27.d[1], x22
    fmov d28, x23
    ins v28.d[1], x24
    fmov d29, x25
    ins v29.d[1], x26
    fmov d30, x27
    ins v30.d[1], x28
    subs x18, x18, #1
    b.ne 1b
    ldp x19, x20, [sp, #0]
    ldp x21, x22, [sp, #16]
    ldp x23, x24, [sp, #32]
    ldp x25, x26, [sp, #48]
    ldp x27, x28, [sp, #64]
    add sp, sp, #80
    ret
