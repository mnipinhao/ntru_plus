// SLOTHY, neoverse_n1, from ntruplus1152_clean/src/basemul_rinv.sym.S.
// Do not edit; regenerate with `make neoverse_n1`.
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
        ldr q30, [x1, #0]
        ldr q24, [x1, #16]
        ldr q18, [x1, #32]
        ldr q17, [x1, #48]
        ldr q27, [x2, #0]
        ldr q19, [x2, #16]
        ldr q20, [x2, #32]
        ldr q31, [x2, #48]
        ldr q26, [x3, #0]
        smull v29.4S, v26.4H, v19.4H
        smull2 v22.4S, v26.8H, v19.8H
        uzp1 v16.8H, v29.8H, v22.8H
        mul v16.8H, v16.8H, v1.8H
        smlal v29.4S, v16.4H, v0.4H
        smlal2 v22.4S, v16.8H, v0.8H
        uzp2 v25.8H, v29.8H, v22.8H
        smull v6.4S, v26.4H, v20.4H
        smull2 v22.4S, v26.8H, v20.8H
        uzp1 v16.8H, v6.8H, v22.8H
        mul v16.8H, v16.8H, v1.8H
        smlal v6.4S, v16.4H, v0.4H
        smlal2 v22.4S, v16.8H, v0.8H
        uzp2 v22.8H, v6.8H, v22.8H
        smull v7.4S, v26.4H, v31.4H
        smull2 v23.4S, v26.8H, v31.8H
        uzp1 v16.8H, v7.8H, v23.8H
        mul v16.8H, v16.8H, v1.8H
        smlal v7.4S, v16.4H, v0.4H
        smlal2 v23.4S, v16.8H, v0.8H
        uzp2 v26.8H, v7.8H, v23.8H
        smull v7.4S, v30.4H, v27.4H
        smull2 v28.4S, v30.8H, v27.8H
        smlal v7.4S, v24.4H, v26.4H
        smlal2 v28.4S, v24.8H, v26.8H
        smlal v7.4S, v18.4H, v22.4H
        smlal2 v28.4S, v18.8H, v22.8H
        smlal v7.4S, v17.4H, v25.4H
        smlal2 v28.4S, v17.8H, v25.8H
        uzp1 v16.8H, v7.8H, v28.8H
        mul v16.8H, v16.8H, v1.8H
        smlal v7.4S, v16.4H, v0.4H
        smlal2 v28.4S, v16.8H, v0.8H
        uzp2 v25.8H, v7.8H, v28.8H
        cmgt v16.8H, v25.8H, v2.8H
        and v16.16B, v16.16B, v0.16B
        sub v25.8H, v25.8H, v16.8H
        cmgt v16.8H, v3.8H, v25.8H
        and v16.16B, v16.16B, v0.16B
        add v16.8H, v25.8H, v16.8H
        str q16, [x0, #0]
        smull v5.4S, v30.4H, v19.4H
        smull2 v6.4S, v30.8H, v19.8H
        smlal v5.4S, v24.4H, v27.4H
        smlal2 v6.4S, v24.8H, v27.8H
        smlal v5.4S, v18.4H, v26.4H
        smlal2 v6.4S, v18.8H, v26.8H
        smlal v5.4S, v17.4H, v22.4H
        smlal2 v6.4S, v17.8H, v22.8H
        uzp1 v16.8H, v5.8H, v6.8H
        mul v16.8H, v16.8H, v1.8H
        smlal v5.4S, v16.4H, v0.4H
        smlal2 v6.4S, v16.8H, v0.8H
        uzp2 v25.8H, v5.8H, v6.8H
        cmgt v16.8H, v25.8H, v2.8H
        and v16.16B, v16.16B, v0.16B
        sub v25.8H, v25.8H, v16.8H
        cmgt v16.8H, v3.8H, v25.8H
        and v16.16B, v16.16B, v0.16B
        add v16.8H, v25.8H, v16.8H
        str q16, [x0, #16]
        smull v21.4S, v30.4H, v20.4H
        smull2 v29.4S, v30.8H, v20.8H
        smlal v21.4S, v24.4H, v19.4H
        smlal2 v29.4S, v24.8H, v19.8H
        smlal v21.4S, v18.4H, v27.4H
        smlal2 v29.4S, v18.8H, v27.8H
        smlal v21.4S, v17.4H, v26.4H
        smlal2 v29.4S, v17.8H, v26.8H
        uzp1 v16.8H, v21.8H, v29.8H
        mul v16.8H, v16.8H, v1.8H
        smlal v21.4S, v16.4H, v0.4H
        smlal2 v29.4S, v16.8H, v0.8H
        uzp2 v25.8H, v21.8H, v29.8H
        cmgt v16.8H, v25.8H, v2.8H
        and v16.16B, v16.16B, v0.16B
        sub v25.8H, v25.8H, v16.8H
        cmgt v16.8H, v3.8H, v25.8H
        and v16.16B, v16.16B, v0.16B
        add v16.8H, v25.8H, v16.8H
        str q16, [x0, #32]
        smull v22.4S, v30.4H, v31.4H
        smull2 v30.4S, v30.8H, v31.8H
        smlal v22.4S, v24.4H, v20.4H
        smlal2 v30.4S, v24.8H, v20.8H
        smlal v22.4S, v18.4H, v19.4H
        smlal2 v30.4S, v18.8H, v19.8H
        smlal v22.4S, v17.4H, v27.4H
        smlal2 v30.4S, v17.8H, v27.8H
        uzp1 v16.8H, v22.8H, v30.8H
        mul v16.8H, v16.8H, v1.8H
        smlal v22.4S, v16.4H, v0.4H
        smlal2 v30.4S, v16.8H, v0.8H
        uzp2 v25.8H, v22.8H, v30.8H
        cmgt v16.8H, v25.8H, v2.8H
        and v16.16B, v16.16B, v0.16B
        sub v25.8H, v25.8H, v16.8H
        cmgt v16.8H, v3.8H, v25.8H
        and v16.16B, v16.16B, v0.16B
        add v24.8H, v25.8H, v16.8H
        str q24, [x0, #48]
        add x0, x0, #64
        add x1, x1, #64
        add x2, x2, #64
        add x3, x3, #16
        subs x4, x4, #1
        b.ne basemul_rinv_loop
    ret
