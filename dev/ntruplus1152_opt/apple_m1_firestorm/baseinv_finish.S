// SLOTHY, apple_m1_firestorm, from ntruplus1152_clean/src/baseinv_finish.sym.S.
// Do not edit; regenerate with `make apple_m1_firestorm`.
#ifdef __APPLE__
#define baseinv_finish_kernel _baseinv_finish_kernel
#endif
.text
.p2align 4
.global baseinv_finish_kernel
baseinv_finish_kernel:
    mov w8, #3457
    dup v0.8h, w8
    mov w8, #-12929
    dup v1.8h, w8
    movi v4.16b, #0
    mov x4, #36
        ldr q6, [x1, #0]
        add x1, x1, #16
        ldr q26, [x0, #32]
        ldr q29, [x0, #0]
        sub v22.8H, v4.8H, v6.8H
        ldr q7, [x0, #16]
        smull v18.4S, v26.4H, v6.4H
        smull2 v16.4S, v26.8H, v6.8H
        ldr q26, [x0, #48]
        smull v19.4S, v29.4H, v6.4H
        smull2 v31.4S, v29.8H, v6.8H
        smull2 v25.4S, v7.8H, v22.8H
        smull v30.4S, v7.4H, v22.4H
        smull v27.4S, v26.4H, v22.4H
        smull2 v6.4S, v26.8H, v22.8H
        uzp1 v26.8H, v18.8H, v16.8H
        uzp1 v5.8H, v19.8H, v31.8H
        uzp1 v17.8H, v30.8H, v25.8H
        mul v26.8H, v26.8H, v1.8H
        mul v20.8H, v17.8H, v1.8H
        smlal v18.4S, v26.4H, v0.4H
        smlal2 v16.4S, v26.8H, v0.8H
        uzp1 v26.8H, v27.8H, v6.8H
        mul v24.8H, v5.8H, v1.8H
        smlal v30.4S, v20.4H, v0.4H
        smlal2 v25.4S, v20.8H, v0.8H
        mul v26.8H, v26.8H, v1.8H
        smlal2 v31.4S, v24.8H, v0.8H
        smlal v19.4S, v24.4H, v0.4H
        smlal v27.4S, v26.4H, v0.4H
        smlal2 v6.4S, v26.8H, v0.8H
        uzp2 v23.8H, v30.8H, v25.8H
        uzp2 v26.8H, v18.8H, v16.8H
        uzp2 v28.8H, v19.8H, v31.8H
        str q26, [x0, #32]
        uzp2 v26.8H, v27.8H, v6.8H
        str q23, [x0, #16]
        sub x4, x4, #1
baseinv_finish_loop:
        ldr q6, [x1, #0]
        add x1, x1, #16
        str q28, [x0, #0]
        str q26, [x0, #48]
        add x0, x0, #64
        ldr q26, [x0, #32]
        ldr q29, [x0, #0]
        ldr q7, [x0, #16]
        sub v22.8H, v4.8H, v6.8H
        smull v18.4S, v26.4H, v6.4H
        smull2 v16.4S, v26.8H, v6.8H
        ldr q26, [x0, #48]
        smull v19.4S, v29.4H, v6.4H
        smull2 v31.4S, v29.8H, v6.8H
        smull2 v25.4S, v7.8H, v22.8H
        smull v30.4S, v7.4H, v22.4H
        smull v27.4S, v26.4H, v22.4H
        smull2 v6.4S, v26.8H, v22.8H
        uzp1 v26.8H, v18.8H, v16.8H
        uzp1 v5.8H, v19.8H, v31.8H
        uzp1 v17.8H, v30.8H, v25.8H
        mul v26.8H, v26.8H, v1.8H
        mul v20.8H, v17.8H, v1.8H
        smlal v18.4S, v26.4H, v0.4H
        smlal2 v16.4S, v26.8H, v0.8H
        uzp1 v26.8H, v27.8H, v6.8H
        mul v24.8H, v5.8H, v1.8H
        mul v26.8H, v26.8H, v1.8H
        smlal v30.4S, v20.4H, v0.4H
        smlal2 v25.4S, v20.8H, v0.8H
        smlal v27.4S, v26.4H, v0.4H
        smlal2 v31.4S, v24.8H, v0.8H
        smlal2 v6.4S, v26.8H, v0.8H
        smlal v19.4S, v24.4H, v0.4H
        uzp2 v26.8H, v18.8H, v16.8H
        uzp2 v23.8H, v30.8H, v25.8H
        str q26, [x0, #32]
        uzp2 v26.8H, v27.8H, v6.8H
        uzp2 v28.8H, v19.8H, v31.8H
        str q23, [x0, #16]
        subs x4, x4, #1
        b.ne baseinv_finish_loop
        str q28, [x0, #0]
        str q26, [x0, #48]
        add x0, x0, #64
    ret
