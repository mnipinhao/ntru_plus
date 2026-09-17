
.text
.p2align 2
.global ntt_top_asm
.global _ntt_top_asm
ntt_top_asm:
_ntt_top_asm:
    mov x2, x1
    add x3, x1, #864
    mov x4, x0
    add x5, x0, #256
    add x6, x0, #512
    add x7, x0, #768
    add x8, x0, #1024
    add x9, x0, #1280
    add x10, x0, #1536
    mov w11, #0x0d81
    dup v29.8h, w11
    mov w11, #0xfd2e
    dup v30.8h, w11
    mov w11, #0xe544
    dup v31.8h, w11
    mov w12, #16
.Ltop_split_loop:
    ld3 {v0.8h, v1.8h, v2.8h}, [x2]
    ld3 {v3.8h, v4.8h, v5.8h}, [x3]
    mul v6.8h, v3.8h, v30.8h
    mul v7.8h, v4.8h, v30.8h
    mul v16.8h, v5.8h, v30.8h
    add v17.8h, v0.8h, v3.8h
    add v18.8h, v1.8h, v4.8h
    add v19.8h, v2.8h, v5.8h
    sub v17.8h, v17.8h, v6.8h
    sub v18.8h, v18.8h, v7.8h
    sub v19.8h, v19.8h, v16.8h
    add v6.8h, v0.8h, v6.8h
    add v7.8h, v1.8h, v7.8h
    add v16.8h, v2.8h, v16.8h
    str q6, [x4], #16
    str q7, [x5], #16
    str q16, [x6], #16
    str q17, [x7], #16
    str q18, [x8], #16
    str q19, [x9], #16
    add x13, x2, #48
    add x14, x3, #48
    ldr s0, [x13]
    add x15, x13, #4
    ld1 {v0.h}[2], [x15]
    ldr s1, [x14]
    add x15, x14, #4
    ld1 {v1.h}[2], [x15]
    mul v2.8h, v1.8h, v30.8h
    add v4.8h, v0.8h, v1.8h
    sub v4.8h, v4.8h, v2.8h
    add v2.8h, v0.8h, v2.8h
    movi v5.8h, #0
    ins v5.h[0], v2.h[0]
    ins v5.h[1], v2.h[1]
    ins v5.h[2], v2.h[2]
    ins v5.h[3], v4.h[0]
    ins v5.h[4], v4.h[1]
    ins v5.h[5], v4.h[2]
    str q5, [x10], #16
    add x2, x2, #54
    add x3, x3, #54
    subs w12, w12, #1
    b.ne .Ltop_split_loop
    ret
