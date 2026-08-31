/*
 * M5A fused fixed-row NTT9 microkernel for one 8-column block.
 *
 * AAPCS64 register policy:
 *   v0-v7,v16       nine coefficient vectors (f0..f8 / transformed states)
 *   v17             current public Montgomery constant
 *   v18-v21         widening Montgomery scratch
 *   v22-v29         transpose/B3 output scratch
 *   v30             q=3457 in every halfword
 *   v31             -q^-1 mod 2^16 = -12929 in every halfword
 *
 * v8-v15 are not touched, so the function is a stackless leaf and has no
 * coefficient spill.  x0..x3 are public pointers; w8 is public-constant
 * construction scratch.
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

/* Positive-exponent B3, in place: (a,b,c) -> (o0,o1,o2). */
.macro B3 a, b, c
    add     v22.8h, \a\().8h, \b\().8h
    add     v22.8h, v22.8h, \c\().8h

    mov     w8, #64650              /* rho*R = -886 */
    dup     v17.8h, w8
    FQMUL   v23, \b
    mov     w8, #1033               /* rho^2*R */
    dup     v17.8h, w8
    FQMUL   v24, \c
    add     v25.8h, v23.8h, v24.8h
    add     v25.8h, \a\().8h, v25.8h

    mov     w8, #1033
    dup     v17.8h, w8
    FQMUL   v23, \b
    mov     w8, #64650
    dup     v17.8h, w8
    FQMUL   v24, \c
    add     v26.8h, v23.8h, v24.8h
    add     v26.8h, \a\().8h, v26.8h

    mov     \a\().16b, v22.16b
    mov     \b\().16b, v25.16b
    mov     \c\().16b, v26.16b
.endm

.global _gt864_fr0_block_asm
_gt864_fr0_block_asm:
    /* Modulus constants used by every widening Montgomery multiplication. */
    mov     w8, #3457
    dup     v30.8h, w8
    mov     w8, #52607              /* int16(-12929) */
    dup     v31.8h, w8

    /* Eight columns, each holding s=0..7. */
    ldp     q0, q1, [x1, #0]
    ldp     q2, q3, [x1, #32]
    ldp     q4, q5, [x1, #64]
    ldp     q6, q7, [x1, #96]

    /* 8x8 int16 transpose: column registers -> row registers. */
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
    mov     v0.16b, v22.16b
    mov     v1.16b, v23.16b
    mov     v2.16b, v24.16b
    mov     v3.16b, v25.16b
    mov     v4.16b, v26.16b
    mov     v5.16b, v27.16b
    mov     v6.16b, v28.16b
    mov     v7.16b, v29.16b

    /* Exact s=8 vector: one public-stride halfword from each tail column. */
    movi    v16.8h, #0
    mov     x4, #16
    ld1     {v16.h}[0], [x2], x4
    ld1     {v16.h}[1], [x2], x4
    ld1     {v16.h}[2], [x2], x4
    ld1     {v16.h}[3], [x2], x4
    ld1     {v16.h}[4], [x2], x4
    ld1     {v16.h}[5], [x2], x4
    ld1     {v16.h}[6], [x2], x4
    ld1     {v16.h}[7], [x2]

    /* f_s <- U_s * lambda_c^s.  s=0 is the identity and is skipped. */
    ldr     q17, [x3, #16]
    FQMUL   v1, v1
    ldr     q17, [x3, #32]
    FQMUL   v2, v2
    ldr     q17, [x3, #48]
    FQMUL   v3, v3
    ldr     q17, [x3, #64]
    FQMUL   v4, v4
    ldr     q17, [x3, #80]
    FQMUL   v5, v5
    ldr     q17, [x3, #96]
    FQMUL   v6, v6
    ldr     q17, [x3, #112]
    FQMUL   v7, v7
    ldr     q17, [x3, #128]
    FQMUL   v16, v16

    /* First oriented radix-3 layer. */
    B3      v0, v3, v6
    B3      v1, v4, v7
    B3      v16, v2, v5

    /* Second layer group 0: (F0,F3,F6). */
    B3      v0, v1, v16

    /* Group 1: B3(a1, eta*b1, eta^-1*c1) -> (F1,F4,F7). */
    mov     w8, #708
    dup     v17.8h, w8
    FQMUL   v4, v4
    mov     w8, #1510
    dup     v17.8h, w8
    FQMUL   v2, v2
    B3      v3, v4, v2

    /* Group 2: B3(a2, eta^-1*b2, eta*c2) -> (F8,F2,F5). */
    mov     w8, #1510
    dup     v17.8h, w8
    FQMUL   v7, v7
    mov     w8, #708
    dup     v17.8h, w8
    FQMUL   v5, v5
    B3      v6, v7, v5

    /* Natural physical-row order; one row step is two 48-byte SoA groups. */
    str     q0,  [x0, #0]           /* F0 */
    str     q3,  [x0, #96]          /* F1 */
    str     q7,  [x0, #192]         /* F2 */
    str     q1,  [x0, #288]         /* F3 */
    str     q4,  [x0, #384]         /* F4 */
    str     q5,  [x0, #480]         /* F5 */
    str     q16, [x0, #576]         /* F6 */
    str     q2,  [x0, #672]         /* F7 */
    str     q6,  [x0, #768]         /* F8 */
    ret
