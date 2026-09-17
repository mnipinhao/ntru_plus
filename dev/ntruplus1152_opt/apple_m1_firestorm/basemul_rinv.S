// SLOTHY, apple_m1_firestorm, from ntruplus1152_clean/src/basemul_rinv.sym.S.
// Do not edit; regenerate with `make apple_m1_firestorm`.
.text
.global basemul_rinv_kernel
basemul_rinv_kernel:
    mov w8, #3457
    dup v0.8h, w8
    mov w8, #-12929
    dup v1.8h, w8
    mov w8, #1728
    dup v2.8h, w8
    mov w8, #-1728
    dup v3.8h, w8
    mov x4, #36
basemul_rinv_loop:
        ldr q24, [x1, #0]
        ldr q19, [x1, #16]
        ldr q7, [x1, #32]
        ldr q16, [x1, #48]
        ldr q22, [x2, #0]
        ldr q25, [x2, #16]
        ldr q18, [x2, #32]
        ldr q6, [x2, #48]
        ldr q21, [x3, #0]
        smull v28.4S, v21.4H, v25.4H
        smull2 v5.4S, v21.8H, v25.8H
        uzp1 v23.8H, v28.8H, v5.8H
        mul v23.8H, v23.8H, v1.8H
        smlal v28.4S, v23.4H, v0.4H
        smlal2 v5.4S, v23.8H, v0.8H
        uzp2 v29.8H, v28.8H, v5.8H
        smull v17.4S, v21.4H, v18.4H
        smull2 v5.4S, v21.8H, v18.8H
        uzp1 v23.8H, v17.8H, v5.8H
        mul v23.8H, v23.8H, v1.8H
        smlal v17.4S, v23.4H, v0.4H
        smlal2 v5.4S, v23.8H, v0.8H
        uzp2 v5.8H, v17.8H, v5.8H
        smull v31.4S, v21.4H, v6.4H
        smull2 v30.4S, v21.8H, v6.8H
        uzp1 v23.8H, v31.8H, v30.8H
        mul v23.8H, v23.8H, v1.8H
        smlal v31.4S, v23.4H, v0.4H
        smlal2 v30.4S, v23.8H, v0.8H
        uzp2 v21.8H, v31.8H, v30.8H
        smull v31.4S, v24.4H, v22.4H
        smull2 v20.4S, v24.8H, v22.8H
        smlal v31.4S, v19.4H, v21.4H
        smlal2 v20.4S, v19.8H, v21.8H
        smlal v31.4S, v7.4H, v5.4H
        smlal2 v20.4S, v7.8H, v5.8H
        smlal v31.4S, v16.4H, v29.4H
        smlal2 v20.4S, v16.8H, v29.8H
        uzp1 v23.8H, v31.8H, v20.8H
        mul v23.8H, v23.8H, v1.8H
        smlal v31.4S, v23.4H, v0.4H
        smlal2 v20.4S, v23.8H, v0.8H
        uzp2 v29.8H, v31.8H, v20.8H
        cmgt v23.8H, v29.8H, v2.8H
        and v23.16B, v23.16B, v0.16B
        sub v29.8H, v29.8H, v23.8H
        cmgt v23.8H, v3.8H, v29.8H
        and v23.16B, v23.16B, v0.16B
        add v23.8H, v29.8H, v23.8H
        str q23, [x0, #0]
        smull v27.4S, v24.4H, v25.4H
        smull2 v17.4S, v24.8H, v25.8H
        smlal v27.4S, v19.4H, v22.4H
        smlal2 v17.4S, v19.8H, v22.8H
        smlal v27.4S, v7.4H, v21.4H
        smlal2 v17.4S, v7.8H, v21.8H
        smlal v27.4S, v16.4H, v5.4H
        smlal2 v17.4S, v16.8H, v5.8H
        uzp1 v23.8H, v27.8H, v17.8H
        mul v23.8H, v23.8H, v1.8H
        smlal v27.4S, v23.4H, v0.4H
        smlal2 v17.4S, v23.8H, v0.8H
        uzp2 v29.8H, v27.8H, v17.8H
        cmgt v23.8H, v29.8H, v2.8H
        and v23.16B, v23.16B, v0.16B
        sub v29.8H, v29.8H, v23.8H
        cmgt v23.8H, v3.8H, v29.8H
        and v23.16B, v23.16B, v0.16B
        add v23.8H, v29.8H, v23.8H
        str q23, [x0, #16]
        smull v26.4S, v24.4H, v18.4H
        smull2 v28.4S, v24.8H, v18.8H
        smlal v26.4S, v19.4H, v25.4H
        smlal2 v28.4S, v19.8H, v25.8H
        smlal v26.4S, v7.4H, v22.4H
        smlal2 v28.4S, v7.8H, v22.8H
        smlal v26.4S, v16.4H, v21.4H
        smlal2 v28.4S, v16.8H, v21.8H
        uzp1 v23.8H, v26.8H, v28.8H
        mul v23.8H, v23.8H, v1.8H
        smlal v26.4S, v23.4H, v0.4H
        smlal2 v28.4S, v23.8H, v0.8H
        uzp2 v29.8H, v26.8H, v28.8H
        cmgt v23.8H, v29.8H, v2.8H
        and v23.16B, v23.16B, v0.16B
        sub v29.8H, v29.8H, v23.8H
        cmgt v23.8H, v3.8H, v29.8H
        and v23.16B, v23.16B, v0.16B
        add v23.8H, v29.8H, v23.8H
        str q23, [x0, #32]
        smull v5.4S, v24.4H, v6.4H
        smull2 v24.4S, v24.8H, v6.8H
        smlal v5.4S, v19.4H, v18.4H
        smlal2 v24.4S, v19.8H, v18.8H
        smlal v5.4S, v7.4H, v25.4H
        smlal2 v24.4S, v7.8H, v25.8H
        smlal v5.4S, v16.4H, v22.4H
        smlal2 v24.4S, v16.8H, v22.8H
        uzp1 v23.8H, v5.8H, v24.8H
        mul v23.8H, v23.8H, v1.8H
        smlal v5.4S, v23.4H, v0.4H
        smlal2 v24.4S, v23.8H, v0.8H
        uzp2 v29.8H, v5.8H, v24.8H
        cmgt v23.8H, v29.8H, v2.8H
        and v23.16B, v23.16B, v0.16B
        sub v29.8H, v29.8H, v23.8H
        cmgt v23.8H, v3.8H, v29.8H
        and v23.16B, v23.16B, v0.16B
        add v19.8H, v29.8H, v23.8H
        str q19, [x0, #48]
        add x0, x0, #64
        add x1, x1, #64
        add x2, x2, #64
        add x3, x3, #16
        subs x4, x4, #1
        b.ne basemul_rinv_loop
    ret
