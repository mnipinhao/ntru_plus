#ifndef C_SYM
#ifdef __APPLE__
#define C_SYM_1(sym) _##sym
#define C_SYM(sym) C_SYM_1(sym)
#else
#define C_SYM(sym) sym
#endif
#endif

/* Requires every input coefficient in [-3,4]; this is not a general-input API. */
.text
.p2align 2

.global C_SYM(ntt_top_asm)
C_SYM(ntt_top_asm):
    /*
     * x0: 896-int16 output in the transform-plus-tail layout
     * x1: 864-int16 natural-order input
     *
     * For m=s+9*t, the second LD3 is 432 coefficients above the first:
     *   low  = a[3*(s+9*t)+branch]
     *   high = a[3*(s+9*(t+16))+branch]
     */
    mov x2, x1
    add x3, x1, #864

    /* Six contiguous 16-vector banks: (alpha,b0..b2), (beta,b0..b2). */
    mov x4, x0
    add x5, x0, #256
    add x6, x0, #512
    add x7, x0, #768
    add x8, x0, #1024
    add x9, x0, #1280
    add x10, x0, #1536

    /* q, alpha, round(alpha*2^15/q), copied from official Neon level 0. */
    mov w11, #0x0d81
    dup v29.8h, w11
    mov w11, #0xfd2e
    dup v30.8h, w11
    mov w11, #0xe544
    dup v31.8h, w11

    mov w12, #16
.Ltop_split_loop:
    /* lanes 0..7 are residues s=0..7; val[0..2] are cubic branches. */
    ld3 {v0.8h, v1.8h, v2.8h}, [x2]
    ld3 {v3.8h, v4.8h, v5.8h}, [x3]

    /* t_b = alpha * high_b mod q, with the official reciprocal reduction. */
    mul v6.8h, v3.8h, v30.8h
    mul v7.8h, v4.8h, v30.8h
    mul v16.8h, v5.8h, v30.8h

    /* alpha output = low+t; beta output = low+high-t, beta=1-alpha. */
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

    /* s=8: load exactly three halfwords; do not read beyond input at t=15. */
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

    /* One vector holds all six (top,branch) tails; two lanes are padding. */
    movi v5.8h, #0
    ins v5.h[0], v2.h[0]
    ins v5.h[1], v2.h[1]
    ins v5.h[2], v2.h[2]
    ins v5.h[3], v4.h[0]
    ins v5.h[4], v4.h[1]
    ins v5.h[5], v4.h[2]
    str q5, [x10], #16

    /* 9 values of m times 3 interleaved branches = 54 bytes per t. */
    add x2, x2, #54
    add x3, x3, #54
    subs w12, w12, #1
    b.ne .Ltop_split_loop
    ret
