// SLOTHY, cortex_a76, from ntruplus1152_clean/src/baseinv_num.sym.S.
// Do not edit; regenerate with `make cortex_a76`.
.text
.global baseinv_num_kernel
baseinv_num_kernel:
    mov w8, #3457
    dup v0.8h, w8
    mov w8, #-12929
    dup v1.8h, w8
    mov x4, #36
.p2align 5
baseinv_num_loop:
        ldr q20, [x2, #0]
        ldr q19, [x2, #16]
        ldr q17, [x2, #32]
        ldr q18, [x2, #48]
        ldr q16, [x3, #0]
        smull v25.4S, v17.4H, v17.4H
        smull2 v26.4S, v17.8H, v17.8H
        smlsl v25.4S, v19.4H, v18.4H
        smlsl2 v26.4S, v19.8H, v18.8H
        smlsl v25.4S, v19.4H, v18.4H
        smlsl2 v26.4S, v19.8H, v18.8H
        uzp1 v21.8H, v25.8H, v26.8H
        mul v21.8H, v21.8H, v1.8H
        smlal v25.4S, v21.4H, v0.4H
        smlal2 v26.4S, v21.8H, v0.8H
        uzp2 v5.8H, v25.8H, v26.8H
        smull v24.4S, v18.4H, v18.4H
        smull2 v6.4S, v18.8H, v18.8H
        uzp1 v21.8H, v24.8H, v6.8H
        mul v21.8H, v21.8H, v1.8H
        smlal v24.4S, v21.4H, v0.4H
        smlal2 v6.4S, v21.8H, v0.8H
        uzp2 v6.8H, v24.8H, v6.8H
        smull v23.4S, v20.4H, v20.4H
        smull2 v7.4S, v20.8H, v20.8H
        smlal v23.4S, v5.4H, v16.4H
        smlal2 v7.4S, v5.8H, v16.8H
        uzp1 v21.8H, v23.8H, v7.8H
        mul v21.8H, v21.8H, v1.8H
        smlal v23.4S, v21.4H, v0.4H
        smlal2 v7.4S, v21.8H, v0.8H
        uzp2 v7.8H, v23.8H, v7.8H
        smull v25.4S, v19.4H, v19.4H
        smull2 v26.4S, v19.8H, v19.8H
        smlal v25.4S, v6.4H, v16.4H
        smlal2 v26.4S, v6.8H, v16.8H
        smlsl v25.4S, v20.4H, v17.4H
        smlsl2 v26.4S, v20.8H, v17.8H
        smlsl v25.4S, v20.4H, v17.4H
        smlsl2 v26.4S, v20.8H, v17.8H
        uzp1 v21.8H, v25.8H, v26.8H
        mul v21.8H, v21.8H, v1.8H
        smlal v25.4S, v21.4H, v0.4H
        smlal2 v26.4S, v21.8H, v0.8H
        uzp2 v5.8H, v25.8H, v26.8H
        smull v24.4S, v5.4H, v16.4H
        smull2 v6.4S, v5.8H, v16.8H
        uzp1 v21.8H, v24.8H, v6.8H
        mul v21.8H, v21.8H, v1.8H
        smlal v24.4S, v21.4H, v0.4H
        smlal2 v6.4S, v21.8H, v0.8H
        uzp2 v6.8H, v24.8H, v6.8H
        smull v31.4S, v7.4H, v7.4H
        smull2 v28.4S, v7.8H, v7.8H
        smlsl v31.4S, v5.4H, v6.4H
        smlsl2 v28.4S, v5.8H, v6.8H
        uzp1 v21.8H, v31.8H, v28.8H
        mul v21.8H, v21.8H, v1.8H
        smlal v31.4S, v21.4H, v0.4H
        smlal2 v28.4S, v21.8H, v0.8H
        uzp2 v21.8H, v31.8H, v28.8H
        str q21, [x1, #0]
        smull v27.4S, v20.4H, v7.4H
        smull2 v22.4S, v20.8H, v7.8H
        smlal v27.4S, v17.4H, v6.4H
        smlal2 v22.4S, v17.8H, v6.8H
        uzp1 v21.8H, v27.8H, v22.8H
        mul v21.8H, v21.8H, v1.8H
        smlal v27.4S, v21.4H, v0.4H
        smlal2 v22.4S, v21.8H, v0.8H
        uzp2 v21.8H, v27.8H, v22.8H
        str q21, [x0, #0]
        smull v30.4S, v18.4H, v6.4H
        smull2 v29.4S, v18.8H, v6.8H
        smlal v30.4S, v19.4H, v7.4H
        smlal2 v29.4S, v19.8H, v7.8H
        uzp1 v21.8H, v30.8H, v29.8H
        mul v21.8H, v21.8H, v1.8H
        smlal v30.4S, v21.4H, v0.4H
        smlal2 v29.4S, v21.8H, v0.8H
        uzp2 v21.8H, v30.8H, v29.8H
        str q21, [x0, #16]
        smull v16.4S, v17.4H, v7.4H
        smull2 v17.4S, v17.8H, v7.8H
        smlal v16.4S, v20.4H, v5.4H
        smlal2 v17.4S, v20.8H, v5.8H
        uzp1 v21.8H, v16.8H, v17.8H
        mul v21.8H, v21.8H, v1.8H
        smlal v16.4S, v21.4H, v0.4H
        smlal2 v17.4S, v21.8H, v0.8H
        uzp2 v21.8H, v16.8H, v17.8H
        str q21, [x0, #32]
        smull v20.4S, v19.4H, v5.4H
        smull2 v5.4S, v19.8H, v5.8H
        smlal v20.4S, v18.4H, v7.4H
        smlal2 v5.4S, v18.8H, v7.8H
        uzp1 v21.8H, v20.8H, v5.8H
        mul v21.8H, v21.8H, v1.8H
        smlal v20.4S, v21.4H, v0.4H
        smlal2 v5.4S, v21.8H, v0.8H
        uzp2 v21.8H, v20.8H, v5.8H
        str q21, [x0, #48]
        add x0, x0, #64
        add x1, x1, #16
        add x2, x2, #64
        add x3, x3, #16
        subs x4, x4, #1
        b.ne baseinv_num_loop
    ret
