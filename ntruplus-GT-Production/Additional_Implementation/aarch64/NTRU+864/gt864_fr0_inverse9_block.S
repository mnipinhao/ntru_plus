/*
 * Stackless inverse FR-0 NTT9 block.
 *
 * x0 main_out: eight contiguous P8 column vectors
 * x1 tail_out: first scalar tail slot, next columns are +16 bytes
 * x2 rows: row-0 vector, next FR-0 rows are +96 bytes
 * x3 inverse_twist: nine public (b,b') vector pairs for Algorithm 10
 *
 * v0-v7,v16  nine row/state vectors
 * v17-v22     public fixed-Barrett constants
 * v23-v29     radix-3 / quotient / transpose scratch
 * v22-v29     radix-3 / transpose scratch
 * v30         q
 *
 * v8-v15 are untouched; no stack or coefficient spill is permitted.
 */

.text
.p2align 2

.macro LOAD_PAIR lo, hi, blo, bhi
    mov     w8, #((\blo) & 0xffff)
    dup     \lo\().8h, w8
    mov     w8, #((\bhi) & 0xffff)
    dup     \hi\().8h, w8
.endm

/* Algorithm 10, grouped so the two independent quotient chains overlap. */
.macro FQMUL2 d0, s0, lo0, hi0, q0, d1, s1, lo1, hi1, q1
    sqrdmulh \q0\().8h, \s0\().8h, \hi0\().8h
    sqrdmulh \q1\().8h, \s1\().8h, \hi1\().8h
    mul     \d0\().8h, \s0\().8h, \lo0\().8h
    mul     \d1\().8h, \s1\().8h, \lo1\().8h
    mls     \d0\().8h, \q0\().8h, v30.8h
    mls     \d1\().8h, \q1\().8h, v30.8h
.endm

.macro FQMUL3 d0, s0, lo0, hi0, q0, d1, s1, lo1, hi1, q1, d2, s2, lo2, hi2, q2
    sqrdmulh \q0\().8h, \s0\().8h, \hi0\().8h
    sqrdmulh \q1\().8h, \s1\().8h, \hi1\().8h
    sqrdmulh \q2\().8h, \s2\().8h, \hi2\().8h
    mul     \d0\().8h, \s0\().8h, \lo0\().8h
    mul     \d1\().8h, \s1\().8h, \lo1\().8h
    mul     \d2\().8h, \s2\().8h, \lo2\().8h
    mls     \d0\().8h, \q0\().8h, v30.8h
    mls     \d1\().8h, \q1\().8h, v30.8h
    mls     \d2\().8h, \q2\().8h, v30.8h
.endm

/* Unscaled negative-exponent B3, destructive on (a,b,c). */
.macro B3INV a, b, c
    add     v22.8h, \a\().8h, \b\().8h
    add     v22.8h, v22.8h, \c\().8h

    LOAD_PAIR v17, v18, 722, 6844
    LOAD_PAIR v19, v20, -723, -6853
    FQMUL2 v23, \b, v17, v18, v27, v24, \c, v19, v20, v28
    add     v25.8h, v23.8h, v24.8h
    add     v25.8h, \a\().8h, v25.8h

    FQMUL2 v23, \b, v19, v20, v27, v24, \c, v17, v18, v28
    add     v26.8h, v23.8h, v24.8h
    add     v26.8h, \a\().8h, v26.8h

    mov     \a\().16b, v22.16b
    mov     \b\().16b, v25.16b
    mov     \c\().16b, v26.16b
.endm

.macro TWIST3 r0, r1, r2, offset
    ldr     q17, [x3, #(\offset + 0)]
    ldr     q18, [x3, #(\offset + 16)]
    ldr     q19, [x3, #(\offset + 32)]
    ldr     q20, [x3, #(\offset + 48)]
    ldr     q21, [x3, #(\offset + 64)]
    ldr     q22, [x3, #(\offset + 80)]
    FQMUL3 \r0, \r0, v17, v18, v23, \
           \r1, \r1, v19, v20, v24, \
           \r2, \r2, v21, v22, v25
.endm

.global gt864_fr0_inverse9_block_asm
.global _gt864_fr0_inverse9_block_asm
gt864_fr0_inverse9_block_asm:
_gt864_fr0_inverse9_block_asm:
    mov     w8, #3457
    dup     v30.8h, w8

    ldr     q0,  [x2, #0]
    ldr     q1,  [x2, #96]
    ldr     q2,  [x2, #192]
    ldr     q3,  [x2, #288]
    ldr     q4,  [x2, #384]
    ldr     q5,  [x2, #480]
    ldr     q6,  [x2, #576]
    ldr     q7,  [x2, #672]
    ldr     q16, [x2, #768]

    B3INV   v0, v3, v6
    B3INV   v1, v4, v7
    B3INV   v16, v2, v5

    LOAD_PAIR v17, v18, 366, 3469   /* eta^-1 */
    FQMUL2 v4, v4, v17, v18, v27, v5, v5, v17, v18, v28
    LOAD_PAIR v17, v18, 1124, 10654 /* eta */
    FQMUL2 v7, v7, v17, v18, v27, v2, v2, v17, v18, v28

    B3INV   v0, v1, v16
    B3INV   v3, v4, v2
    B3INV   v6, v7, v5

    /* Logical s order is v0,v3,v7,v1,v4,v5,v16,v2,v6. */
    TWIST3  v0, v3, v7, 0
    TWIST3  v1, v4, v5, 96
    TWIST3  v16, v2, v6, 192

    mov     v22.16b, v1.16b
    mov     v1.16b, v3.16b
    mov     v3.16b, v22.16b
    mov     v22.16b, v2.16b
    mov     v2.16b, v7.16b
    mov     v7.16b, v22.16b
    mov     v22.16b, v6.16b
    mov     v6.16b, v16.16b
    mov     v16.16b, v22.16b       /* exact s=8 vector */

    /* 8x8 transpose: s registers -> P8 column registers. */
    trn1    v22.8h, v0.8h, v1.8h
    trn2    v23.8h, v0.8h, v1.8h
    trn1    v24.8h, v2.8h, v3.8h
    trn2    v25.8h, v2.8h, v3.8h
    trn1    v26.8h, v4.8h, v5.8h
    trn2    v27.8h, v4.8h, v5.8h
    trn1    v28.8h, v6.8h, v7.8h
    trn2    v29.8h, v6.8h, v7.8h

    trn1    v0.4s, v22.4s, v24.4s
    trn2    v4.4s, v22.4s, v24.4s
    trn1    v1.4s, v23.4s, v25.4s
    trn2    v5.4s, v23.4s, v25.4s
    trn1    v2.4s, v26.4s, v28.4s
    trn2    v6.4s, v26.4s, v28.4s
    trn1    v3.4s, v27.4s, v29.4s
    trn2    v7.4s, v27.4s, v29.4s

    trn1    v22.2d, v0.2d, v2.2d
    trn1    v23.2d, v1.2d, v3.2d
    trn1    v24.2d, v4.2d, v6.2d
    trn1    v25.2d, v5.2d, v7.2d
    trn2    v26.2d, v0.2d, v2.2d
    trn2    v27.2d, v1.2d, v3.2d
    trn2    v28.2d, v4.2d, v6.2d
    trn2    v29.2d, v5.2d, v7.2d

    stp     q22, q23, [x0, #0]
    stp     q24, q25, [x0, #32]
    stp     q26, q27, [x0, #64]
    stp     q28, q29, [x0, #96]

    mov     x4, #16
    st1     {v16.h}[0], [x1], x4
    st1     {v16.h}[1], [x1], x4
    st1     {v16.h}[2], [x1], x4
    st1     {v16.h}[3], [x1], x4
    st1     {v16.h}[4], [x1], x4
    st1     {v16.h}[5], [x1], x4
    st1     {v16.h}[6], [x1], x4
    st1     {v16.h}[7], [x1]
    ret
