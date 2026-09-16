/* P51: constant-time equality of two FR0 R0 polynomials modulo q=3457. */
#ifdef __APPLE__
#define C(name) _##name
#else
#define C(name) name
#endif

.text
.p2align 4
.global C(gt864_fr0_equal_modq_asm)
C(gt864_fr0_equal_modq_asm):
    mov w8, #3457
    dup v30.8h, w8
    mov w8, #9
    dup v31.8h, w8
    movi v0.16b, #0
    movi v5.16b, #0
    movi v6.16b, #0
    mov w8, #9

.p2align 4
.Lp51_loop:
    /* Six 16-coefficient chunks; three accumulators shorten the OR chains. */
    ldp q1, q2, [x0], #32
    ldp q3, q4, [x1], #32
    sub v1.8h, v1.8h, v3.8h
    sub v2.8h, v2.8h, v4.8h
    sqrdmulh v3.8h, v1.8h, v31.8h
    sqrdmulh v4.8h, v2.8h, v31.8h
    mls v1.8h, v3.8h, v30.8h
    mls v2.8h, v4.8h, v30.8h
    orr v0.16b, v0.16b, v1.16b
    orr v0.16b, v0.16b, v2.16b

    ldp q1, q2, [x0], #32
    ldp q3, q4, [x1], #32
    sub v1.8h, v1.8h, v3.8h
    sub v2.8h, v2.8h, v4.8h
    sqrdmulh v3.8h, v1.8h, v31.8h
    sqrdmulh v4.8h, v2.8h, v31.8h
    mls v1.8h, v3.8h, v30.8h
    mls v2.8h, v4.8h, v30.8h
    orr v5.16b, v5.16b, v1.16b
    orr v5.16b, v5.16b, v2.16b

    ldp q1, q2, [x0], #32
    ldp q3, q4, [x1], #32
    sub v1.8h, v1.8h, v3.8h
    sub v2.8h, v2.8h, v4.8h
    sqrdmulh v3.8h, v1.8h, v31.8h
    sqrdmulh v4.8h, v2.8h, v31.8h
    mls v1.8h, v3.8h, v30.8h
    mls v2.8h, v4.8h, v30.8h
    orr v6.16b, v6.16b, v1.16b
    orr v6.16b, v6.16b, v2.16b

    ldp q1, q2, [x0], #32
    ldp q3, q4, [x1], #32
    sub v1.8h, v1.8h, v3.8h
    sub v2.8h, v2.8h, v4.8h
    sqrdmulh v3.8h, v1.8h, v31.8h
    sqrdmulh v4.8h, v2.8h, v31.8h
    mls v1.8h, v3.8h, v30.8h
    mls v2.8h, v4.8h, v30.8h
    orr v0.16b, v0.16b, v1.16b
    orr v0.16b, v0.16b, v2.16b

    ldp q1, q2, [x0], #32
    ldp q3, q4, [x1], #32
    sub v1.8h, v1.8h, v3.8h
    sub v2.8h, v2.8h, v4.8h
    sqrdmulh v3.8h, v1.8h, v31.8h
    sqrdmulh v4.8h, v2.8h, v31.8h
    mls v1.8h, v3.8h, v30.8h
    mls v2.8h, v4.8h, v30.8h
    orr v5.16b, v5.16b, v1.16b
    orr v5.16b, v5.16b, v2.16b

    ldp q1, q2, [x0], #32
    ldp q3, q4, [x1], #32
    sub v1.8h, v1.8h, v3.8h
    sub v2.8h, v2.8h, v4.8h
    sqrdmulh v3.8h, v1.8h, v31.8h
    sqrdmulh v4.8h, v2.8h, v31.8h
    mls v1.8h, v3.8h, v30.8h
    mls v2.8h, v4.8h, v30.8h
    orr v6.16b, v6.16b, v1.16b
    orr v6.16b, v6.16b, v2.16b

    subs w8, w8, #1
    b.ne .Lp51_loop

    orr v0.16b, v0.16b, v5.16b
    orr v0.16b, v0.16b, v6.16b
    umaxv h0, v0.8h
    umov w0, v0.h[0]
    cmp w0, #0
    cset w0, ne

    /* Do not retain secret differences in volatile SIMD state. */
    movi v0.16b, #0
    movi v1.16b, #0
    movi v2.16b, #0
    movi v3.16b, #0
    movi v4.16b, #0
    movi v5.16b, #0
    movi v6.16b, #0
    movi v30.16b, #0
    movi v31.16b, #0
    ret
