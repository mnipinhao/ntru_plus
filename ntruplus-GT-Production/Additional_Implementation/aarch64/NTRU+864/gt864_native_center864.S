/* Imported scheduled core: experiments/gt864-native-asm/inverse-p3-center864/candidate.opt.S */
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
    ldr q3, [x0, #0]
    ldr q4, [x0, #16]
    ldr q5, [x0, #32]
    ldr q6, [x0, #48]
    sqrdmulh v7.8H, v3.8H, v1.8H
    sqrdmulh v8.8H, v4.8H, v1.8H
    sqrdmulh v9.8H, v5.8H, v1.8H
    mls v3.8H, v7.8H, v0.8H
    sqrdmulh v10.8H, v6.8H, v1.8H
    mls v4.8H, v8.8H, v0.8H
    sshr v7.8H, v3.8H, #15
    mls v5.8H, v9.8H, v0.8H
    and v7.16B, v7.16B, v0.16B
    mls v6.8H, v10.8H, v0.8H
    add v3.8H, v3.8H, v7.8H
    sshr v8.8H, v4.8H, #15
    cmgt v7.8H, v3.8H, v2.8H
    sshr v9.8H, v5.8H, #15
    and v8.16B, v8.16B, v0.16B
    and v7.16B, v7.16B, v0.16B
    sshr v10.8H, v6.8H, #15
    add v4.8H, v4.8H, v8.8H
    and v9.16B, v9.16B, v0.16B
    sub v3.8H, v3.8H, v7.8H
    and v10.16B, v10.16B, v0.16B
    cmgt v8.8H, v4.8H, v2.8H
    add v5.8H, v5.8H, v9.8H
    add v6.8H, v6.8H, v10.8H
    str q3, [x0, #0]
    cmgt v9.8H, v5.8H, v2.8H
    and v8.16B, v8.16B, v0.16B
    cmgt v10.8H, v6.8H, v2.8H
    and v9.16B, v9.16B, v0.16B
    sub v4.8H, v4.8H, v8.8H
    and v10.16B, v10.16B, v0.16B
    sub v5.8H, v5.8H, v9.8H
    sub v6.8H, v6.8H, v10.8H
    str q4, [x0, #16]
    str q5, [x0, #32]
    str q6, [x0, #48]
    add x0, x0, #64
    subs x8, x8, #1
    b.ne .Lcenter864_loop
    ret
