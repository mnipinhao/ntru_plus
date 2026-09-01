/*
 * Stackless inverse FR-0 NTT9 block.
 *
 * x0 main_out: eight contiguous P8 column vectors
 * x1 tail_out: first scalar tail slot, next columns are +16 bytes
 * x2 rows: row-0 vector, next FR-0 rows are +96 bytes
 * x3 inverse_twist: nine public vectors
 *
 * v0-v7,v16  nine row/state vectors
 * v17         current public Montgomery constant
 * v18-v21     widening Montgomery scratch
 * v22-v29     radix-3 / transpose scratch
 * v30,v31     q and -q^-1
 *
 * v8-v15 are untouched; no stack or coefficient spill is permitted.
 */

.text
.p2align 2

.macro FQMUL dst, src
    smull   v18.4s, \src\().4h, v17.4h
    smull2  v19.4s, \src\().8h, v17.8h
    uzp1    v20.8h, v18.8h, v19.8h
    mul     v20.8h, v20.8h, v31.8h
    smlal   v18.4s, v20.4h, v30.4h
    smlal2  v19.4s, v20.8h, v30.8h
    uzp2    \dst\().8h, v18.8h, v19.8h
.endm

/* Unscaled negative-exponent B3, destructive on (a,b,c). */
.macro B3INV a, b, c
    add     v22.8h, \a\().8h, \b\().8h
    add     v22.8h, v22.8h, \c\().8h

    mov     w8, #1033
    dup     v17.8h, w8
    FQMUL   v23, \b
    mov     w8, #64650              /* rho*R = -886 */
    dup     v17.8h, w8
    FQMUL   v24, \c
    add     v25.8h, v23.8h, v24.8h
    add     v25.8h, \a\().8h, v25.8h

    mov     w8, #64650
    dup     v17.8h, w8
    FQMUL   v23, \b
    mov     w8, #1033
    dup     v17.8h, w8
    FQMUL   v24, \c
    add     v26.8h, v23.8h, v24.8h
    add     v26.8h, \a\().8h, v26.8h

    mov     \a\().16b, v22.16b
    mov     \b\().16b, v25.16b
    mov     \c\().16b, v26.16b
.endm

.macro TWIST reg, offset
    ldr     q17, [x3, #\offset]
    FQMUL   \reg, \reg
.endm

.global gt864_fr0_inverse9_block_asm
.global _gt864_fr0_inverse9_block_asm
gt864_fr0_inverse9_block_asm:
_gt864_fr0_inverse9_block_asm:
    mov     w8, #3457
    dup     v30.8h, w8
    mov     w8, #52607
    dup     v31.8h, w8

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

    mov     w8, #1510              /* undo eta on group-1 b */
    dup     v17.8h, w8
    FQMUL   v4, v4
    mov     w8, #708               /* undo eta^-1 on group-2 b */
    dup     v17.8h, w8
    FQMUL   v7, v7
    FQMUL   v2, v2                 /* undo eta^-1 on group-1 c */
    mov     w8, #1510
    dup     v17.8h, w8
    FQMUL   v5, v5                 /* undo eta on group-2 c */

    B3INV   v0, v1, v16
    B3INV   v3, v4, v2
    B3INV   v6, v7, v5

    /* Logical s order is v0,v3,v7,v1,v4,v5,v16,v2,v6. */
    TWIST   v0, 0
    TWIST   v3, 16
    TWIST   v7, 32
    TWIST   v1, 48
    TWIST   v4, 64
    TWIST   v5, 80
    TWIST   v16, 96
    TWIST   v2, 112
    TWIST   v6, 128

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
