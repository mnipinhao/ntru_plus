#ifdef __APPLE__
#define center864 _center864
#endif

.text
.p2align 2
.global center864
center864:
    // v0-v2 remain live for all 27 public iterations.
    mov w4, #3457
    dup v0.8h, w4
    mov w4, #9
    dup v1.8h, w4
    mov w4, #1728
    dup v2.8h, w4
    mov x8, #27
.Lcenter864_loop:
center864_body_slothy_start:
    ldr q3, [x0, #0]
    ldr q4, [x0, #16]
    ldr q5, [x0, #32]
    ldr q6, [x0, #48]
    sqrdmulh v7.8h, v3.8h, v1.8h
    mls v3.8h, v7.8h, v0.8h
    sshr v7.8h, v3.8h, #15
    and v7.16b, v7.16b, v0.16b
    add v3.8h, v3.8h, v7.8h
    cmgt v7.8h, v3.8h, v2.8h
    and v7.16b, v7.16b, v0.16b
    sub v3.8h, v3.8h, v7.8h
    sqrdmulh v8.8h, v4.8h, v1.8h
    mls v4.8h, v8.8h, v0.8h
    sshr v8.8h, v4.8h, #15
    and v8.16b, v8.16b, v0.16b
    add v4.8h, v4.8h, v8.8h
    cmgt v8.8h, v4.8h, v2.8h
    and v8.16b, v8.16b, v0.16b
    sub v4.8h, v4.8h, v8.8h
    sqrdmulh v9.8h, v5.8h, v1.8h
    mls v5.8h, v9.8h, v0.8h
    sshr v9.8h, v5.8h, #15
    and v9.16b, v9.16b, v0.16b
    add v5.8h, v5.8h, v9.8h
    cmgt v9.8h, v5.8h, v2.8h
    and v9.16b, v9.16b, v0.16b
    sub v5.8h, v5.8h, v9.8h
    sqrdmulh v10.8h, v6.8h, v1.8h
    mls v6.8h, v10.8h, v0.8h
    sshr v10.8h, v6.8h, #15
    and v10.16b, v10.16b, v0.16b
    add v6.8h, v6.8h, v10.8h
    cmgt v10.8h, v6.8h, v2.8h
    and v10.16b, v10.16b, v0.16b
    sub v6.8h, v6.8h, v10.8h
    str q3, [x0, #0]
    str q4, [x0, #16]
    str q5, [x0, #32]
    str q6, [x0, #48]
center864_body_slothy_end:
    add x0, x0, #64
    subs x8, x8, #1
    b.ne .Lcenter864_loop
    ret
