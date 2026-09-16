/* P51 wide-register timing candidate: FR0 equality modulo q=3457. */
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
p51_loop_slothy_start:
    /* Bank 0: independent registers expose cross-bank ILP. */
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

    /* Bank 1: independent registers expose cross-bank ILP. */
    ldp q7, q8, [x0], #32
    ldp q9, q10, [x1], #32
    sub v7.8h, v7.8h, v9.8h
    sub v8.8h, v8.8h, v10.8h
    sqrdmulh v9.8h, v7.8h, v31.8h
    sqrdmulh v10.8h, v8.8h, v31.8h
    mls v7.8h, v9.8h, v30.8h
    mls v8.8h, v10.8h, v30.8h
    orr v5.16b, v5.16b, v7.16b
    orr v5.16b, v5.16b, v8.16b

    /* Bank 2: independent registers expose cross-bank ILP. */
    ldp q11, q12, [x0], #32
    ldp q13, q14, [x1], #32
    sub v11.8h, v11.8h, v13.8h
    sub v12.8h, v12.8h, v14.8h
    sqrdmulh v13.8h, v11.8h, v31.8h
    sqrdmulh v14.8h, v12.8h, v31.8h
    mls v11.8h, v13.8h, v30.8h
    mls v12.8h, v14.8h, v30.8h
    orr v6.16b, v6.16b, v11.16b
    orr v6.16b, v6.16b, v12.16b

    /* Bank 3: independent registers expose cross-bank ILP. */
    ldp q15, q16, [x0], #32
    ldp q17, q18, [x1], #32
    sub v15.8h, v15.8h, v17.8h
    sub v16.8h, v16.8h, v18.8h
    sqrdmulh v17.8h, v15.8h, v31.8h
    sqrdmulh v18.8h, v16.8h, v31.8h
    mls v15.8h, v17.8h, v30.8h
    mls v16.8h, v18.8h, v30.8h
    orr v0.16b, v0.16b, v15.16b
    orr v0.16b, v0.16b, v16.16b

    /* Bank 4: independent registers expose cross-bank ILP. */
    ldp q19, q20, [x0], #32
    ldp q21, q22, [x1], #32
    sub v19.8h, v19.8h, v21.8h
    sub v20.8h, v20.8h, v22.8h
    sqrdmulh v21.8h, v19.8h, v31.8h
    sqrdmulh v22.8h, v20.8h, v31.8h
    mls v19.8h, v21.8h, v30.8h
    mls v20.8h, v22.8h, v30.8h
    orr v5.16b, v5.16b, v19.16b
    orr v5.16b, v5.16b, v20.16b

    /* Bank 5: independent registers expose cross-bank ILP. */
    ldp q23, q24, [x0], #32
    ldp q25, q26, [x1], #32
    sub v23.8h, v23.8h, v25.8h
    sub v24.8h, v24.8h, v26.8h
    sqrdmulh v25.8h, v23.8h, v31.8h
    sqrdmulh v26.8h, v24.8h, v31.8h
    mls v23.8h, v25.8h, v30.8h
    mls v24.8h, v26.8h, v30.8h
    orr v6.16b, v6.16b, v23.16b
    orr v6.16b, v6.16b, v24.16b
p51_loop_slothy_end:
    subs w8, w8, #1
    b.ne .Lp51_loop

    orr v0.16b, v0.16b, v5.16b
    orr v0.16b, v0.16b, v6.16b
    umaxv h0, v0.8h
    umov w0, v0.h[0]
    cmp w0, #0
    cset w0, ne

    /* Erase every vector which held a secret difference or residue. */
    movi v0.16b, #0
    movi v1.16b, #0
    movi v2.16b, #0
    movi v3.16b, #0
    movi v4.16b, #0
    movi v5.16b, #0
    movi v6.16b, #0
    movi v7.16b, #0
    movi v8.16b, #0
    movi v9.16b, #0
    movi v10.16b, #0
    movi v11.16b, #0
    movi v12.16b, #0
    movi v13.16b, #0
    movi v14.16b, #0
    movi v15.16b, #0
    movi v16.16b, #0
    movi v17.16b, #0
    movi v18.16b, #0
    movi v19.16b, #0
    movi v20.16b, #0
    movi v21.16b, #0
    movi v22.16b, #0
    movi v23.16b, #0
    movi v24.16b, #0
    movi v25.16b, #0
    movi v26.16b, #0
    movi v30.16b, #0
    movi v31.16b, #0
    ret
