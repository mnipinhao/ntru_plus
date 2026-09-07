.text
.align 4

#ifdef __APPLE__
#define C_SYM_1(sym) _##sym
#define C_SYM(sym) C_SYM_1(sym)
#define LOAD_ADDR_PAGE(reg, sym) adrp reg, C_SYM(sym)@PAGE
#define LOAD_ADDR_OFF(reg, sym) add reg, reg, C_SYM(sym)@PAGEOFF
#else
#define C_SYM(sym) sym
#define LOAD_ADDR_PAGE(reg, sym) adrp reg, C_SYM(sym)
#define LOAD_ADDR_OFF(reg, sym) add reg, reg, :lo12:C_SYM(sym)
#endif

#define GT_RMINUS1_PAIR_SYMBOL poly_basemul
#define GT_RMINUS1_PAIR_DARWIN_SYMBOL _poly_basemul
.global GT_RMINUS1_PAIR_SYMBOL
.global GT_RMINUS1_PAIR_DARWIN_SYMBOL
GT_RMINUS1_PAIR_SYMBOL:
GT_RMINUS1_PAIR_DARWIN_SYMBOL:
    sub sp, sp, #64
    stp d8, d9, [sp, #0]
    stp d10, d11, [sp, #16]
    stp d12, d13, [sp, #32]
    stp d14, d15, [sp, #48]
    adr x3, .Lrminus1_pair_consts
    ld1 {v0.8h}, [x3]
    LOAD_ADDR_PAGE(x4, gt_rowbitrev_lambda)
    LOAD_ADDR_OFF(x4, gt_rowbitrev_lambda)
    mov x8, #12
.Lrminus1_pair_production_loop:
        .Lrminus1_pair_slothy_start:
        ld4 {v28.8H, v29.8H, v30.8H, v31.8H}, [x1], #64
        ld4 {v10.8H, v11.8H, v12.8H, v13.8H}, [x2], #64
        smull2 v27.4S, v29.8H, v13.8H
        ld1 {v4.8H}, [x4], #16
        smull v21.4S, v29.4H, v13.4H
        smull v5.4S, v31.4H, v13.4H
        smull2 v26.4S, v31.8H, v13.8H
        smull v17.4S, v30.4H, v13.4H
        smlal v21.4S, v30.4H, v12.4H
        uzp1 v15.8H, v5.8H, v26.8H
        smlal v17.4S, v31.4H, v12.4H
        smlal2 v27.4S, v30.8H, v12.8H
        smlal v21.4S, v31.4H, v11.4H
        smlal2 v27.4S, v31.8H, v11.8H
        smull2 v6.4S, v30.8H, v13.8H
        smlal2 v6.4S, v31.8H, v12.8H
        uzp1 v8.8H, v21.8H, v27.8H
        smull v1.4S, v31.4H, v10.4H
        mul v8.8H, v8.8H, v0.H[2]
        mul v15.8H, v15.8H, v0.H[2]
        uzp1 v2.8H, v17.8H, v6.8H
        mul v2.8H, v2.8H, v0.H[2]
        smlal2 v27.4S, v8.8H, v0.H[0]
        smlal v17.4S, v2.4H, v0.H[0]
        smlal v5.4S, v15.4H, v0.H[0]
        smlal2 v26.4S, v15.8H, v0.H[0]
        smlal v21.4S, v8.4H, v0.H[0]
        smlal2 v6.4S, v2.8H, v0.H[0]
        smlal v1.4S, v28.4H, v13.4H
        uzp2 v15.8H, v5.8H, v26.8H
        smull2 v24.4S, v31.8H, v10.8H
        uzp2 v2.8H, v21.8H, v27.8H
        smlal2 v24.4S, v28.8H, v13.8H
        smlal v1.4S, v29.4H, v12.4H
        uzp2 v8.8H, v17.8H, v6.8H
        smlal2 v24.4S, v29.8H, v12.8H
        smull2 v21.4S, v15.8H, v4.8H
        smull v20.4S, v15.4H, v4.4H
        smlal v20.4S, v28.4H, v12.4H
        ld1 {v7.8H}, [x4], #16
        smlal2 v21.4S, v28.8H, v12.8H
        smull2 v17.4S, v8.8H, v4.8H
        smlal2 v17.4S, v28.8H, v11.8H
        smull2 v5.4S, v2.8H, v4.8H
        smlal2 v5.4S, v28.8H, v10.8H
        smull v27.4S, v8.4H, v4.4H
        smlal v27.4S, v28.4H, v11.4H
        smlal2 v17.4S, v29.8H, v10.8H
        smlal2 v21.4S, v29.8H, v11.8H
        smlal v20.4S, v29.4H, v11.4H
        smlal v27.4S, v29.4H, v10.4H
        smlal2 v21.4S, v30.8H, v10.8H
        smull v6.4S, v2.4H, v4.4H
        smlal v6.4S, v28.4H, v10.4H
        smlal2 v24.4S, v30.8H, v11.8H
        uzp1 v15.8H, v27.8H, v17.8H
        smlal v20.4S, v30.4H, v10.4H
        uzp1 v26.8H, v6.8H, v5.8H
        smlal v1.4S, v30.4H, v11.4H
        ld4 {v28.8H, v29.8H, v30.8H, v31.8H}, [x1], #64
        mul v15.8H, v15.8H, v0.H[2]
        mul v26.8H, v26.8H, v0.H[2]
        smlal v27.4S, v15.4H, v0.H[0]
        uzp1 v8.8H, v20.8H, v21.8H
        smlal2 v5.4S, v26.8H, v0.H[0]
        uzp1 v2.8H, v1.8H, v24.8H
        smlal2 v17.4S, v15.8H, v0.H[0]
        ld4 {v10.8H, v11.8H, v12.8H, v13.8H}, [x2], #64
        mul v8.8H, v8.8H, v0.H[2]
        uzp2 v3.8H, v27.8H, v17.8H
        mul v2.8H, v2.8H, v0.H[2]
        smlal v6.4S, v26.4H, v0.H[0]
        smlal2 v21.4S, v8.8H, v0.H[0]
        smlal v20.4S, v8.4H, v0.H[0]
        smlal v1.4S, v2.4H, v0.H[0]
        smlal2 v24.4S, v2.8H, v0.H[0]
        uzp2 v2.8H, v6.8H, v5.8H
        uzp2 v4.8H, v20.8H, v21.8H
        smull2 v26.4S, v31.8H, v13.8H
        uzp2 v5.8H, v1.8H, v24.8H
        smull2 v27.4S, v29.8H, v13.8H
        smull v21.4S, v29.4H, v13.4H
        st4 {v2.8H, v3.8H, v4.8H, v5.8H}, [x0], #64
        smull v5.4S, v31.4H, v13.4H
        smlal2 v27.4S, v30.8H, v12.8H
        smlal v21.4S, v30.4H, v12.4H
        uzp1 v15.8H, v5.8H, v26.8H
        smlal2 v27.4S, v31.8H, v11.8H
        smlal v21.4S, v31.4H, v11.4H
        smull2 v6.4S, v30.8H, v13.8H
        smull v17.4S, v30.4H, v13.4H
        smlal2 v6.4S, v31.8H, v12.8H
        smlal v17.4S, v31.4H, v12.4H
        uzp1 v2.8H, v21.8H, v27.8H
        mul v15.8H, v15.8H, v0.H[2]
        mul v2.8H, v2.8H, v0.H[2]
        uzp1 v8.8H, v17.8H, v6.8H
        smull2 v20.4S, v31.8H, v10.8H
        smlal2 v26.4S, v15.8H, v0.H[0]
        mul v8.8H, v8.8H, v0.H[2]
        smlal v17.4S, v8.4H, v0.H[0]
        smlal v5.4S, v15.4H, v0.H[0]
        smlal2 v27.4S, v2.8H, v0.H[0]
        smlal v21.4S, v2.4H, v0.H[0]
        smlal2 v6.4S, v8.8H, v0.H[0]
        uzp2 v15.8H, v5.8H, v26.8H
        smlal2 v20.4S, v28.8H, v13.8H
        smull v24.4S, v31.4H, v10.4H
        uzp2 v2.8H, v21.8H, v27.8H
        smlal2 v20.4S, v29.8H, v12.8H
        uzp2 v8.8H, v17.8H, v6.8H
        smlal v24.4S, v28.4H, v13.4H
        smull v21.4S, v15.4H, v7.4H
        smull2 v27.4S, v15.8H, v7.8H
        smlal2 v27.4S, v28.8H, v12.8H
        smlal v24.4S, v29.4H, v12.4H
        smlal v21.4S, v28.4H, v12.4H
        smlal2 v27.4S, v29.8H, v11.8H
        smlal v24.4S, v30.4H, v11.4H
        smull v17.4S, v8.4H, v7.4H
        smull2 v6.4S, v8.8H, v7.8H
        smull2 v26.4S, v2.8H, v7.8H
        smlal v17.4S, v28.4H, v11.4H
        smlal v17.4S, v29.4H, v10.4H
        smlal2 v20.4S, v30.8H, v11.8H
        smlal2 v26.4S, v28.8H, v10.8H
        smull v5.4S, v2.4H, v7.4H
        smlal v5.4S, v28.4H, v10.4H
        smlal2 v6.4S, v28.8H, v11.8H
        uzp1 v2.8H, v24.8H, v20.8H
        smlal2 v27.4S, v30.8H, v10.8H
        mul v2.8H, v2.8H, v0.H[2]
        uzp1 v12.8H, v5.8H, v26.8H
        smlal v21.4S, v29.4H, v11.4H
        smlal2 v6.4S, v29.8H, v10.8H
        smlal v21.4S, v30.4H, v10.4H
        smlal v24.4S, v2.4H, v0.H[0]
        smlal2 v20.4S, v2.8H, v0.H[0]
        mul v12.8H, v12.8H, v0.H[2]
        smlal2 v26.4S, v12.8H, v0.H[0]
        uzp1 v15.8H, v17.8H, v6.8H
        smlal v5.4S, v12.4H, v0.H[0]
        uzp1 v8.8H, v21.8H, v27.8H
        mul v15.8H, v15.8H, v0.H[2]
        mul v8.8H, v8.8H, v0.H[2]
        uzp2 v2.8H, v5.8H, v26.8H
        uzp2 v5.8H, v24.8H, v20.8H
        smlal2 v6.4S, v15.8H, v0.H[0]
        smlal v17.4S, v15.4H, v0.H[0]
        smlal v21.4S, v8.4H, v0.H[0]
        smlal2 v27.4S, v8.8H, v0.H[0]
        uzp2 v3.8H, v17.8H, v6.8H
        uzp2 v4.8H, v21.8H, v27.8H
        st4 {v2.8H, v3.8H, v4.8H, v5.8H}, [x0], #64
        .Lrminus1_pair_slothy_end:
    subs x8, x8, #1
    b.ne .Lrminus1_pair_production_loop
    ldp d14, d15, [sp, #48]
    ldp d12, d13, [sp, #32]
    ldp d10, d11, [sp, #16]
    ldp d8, d9, [sp, #0]
    add sp, sp, #64
    ret
.align 4
.Lrminus1_pair_consts:
    .hword 0x0d81, 0x4bd4, 0xcd7f, 0xff6d
    .hword 0xfa8f, 0xf9dd, 0xc5d5, 0x0000

#undef C_SYM
#ifdef __APPLE__
#undef C_SYM_1
#endif
#undef LOAD_ADDR_PAGE
#undef LOAD_ADDR_OFF
