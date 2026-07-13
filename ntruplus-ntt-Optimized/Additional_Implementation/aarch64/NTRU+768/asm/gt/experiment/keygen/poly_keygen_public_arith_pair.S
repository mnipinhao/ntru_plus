/*
 * Benchmark-only keygen public arithmetic pair candidate.
 *
 * Contract:
 *   h    = poly_basemul_scaled_r_input(g, finv)
 *   hinv = poly_basemul_scaled_r_input(f, ginv)
 *
 * ABI:
 *   x0 = h
 *   x1 = hinv
 *   x2 = f
 *   x3 = g
 *   x4 = finv
 *   x5 = ginv
 *
 * This does not replace poly_basemul_scaled_r_input.  It keeps the production
 * ld4/st4 GT block-major layout and shares one lambda load per physical_j batch
 * across the two scaled basemul products.  v19 is reserved as the lambda shadow
 * between the first and second product in each loop.
 */

.text
.align 2

#include "../common.inc"

.macro KEYGEN_PAIR_BASEGT_PRODUCT dst, src1, src2
        ld4 {v24.8H, v25.8H, v26.8H, v27.8H}, [\src2], #64
        ld4 {v4.8H, v5.8H, v6.8H, v7.8H}, [\src1], #64
        smull v16.4S, v7.4H, v27.4H
        smull2 v20.4S, v7.8H, v27.8H
        smull v17.4S, v5.4H, v27.4H
        smull2 v28.4S, v5.8H, v27.8H
        smull v30.4S, v7.4H, v24.4H
        smlal v17.4S, v6.4H, v26.4H
        uzp1 v13.8H, v16.8H, v20.8H
        smull2 v29.4S, v6.8H, v27.8H
        smull v3.4S, v6.4H, v27.4H
        smlal2 v29.4S, v7.8H, v26.8H
        mul v23.8H, v13.8H, v0.H[2]
        smlal v3.4S, v7.4H, v26.4H
        smull2 v12.4S, v7.8H, v24.8H
        smlal2 v12.4S, v4.8H, v27.8H
        smlal2 v20.4S, v23.8H, v0.H[0]
        uzp1 v14.8H, v3.8H, v29.8H
        smlal v16.4S, v23.4H, v0.H[0]
        smlal v30.4S, v4.4H, v27.4H
        smlal2 v12.4S, v5.8H, v26.8H
        mul v21.8H, v14.8H, v0.H[2]
        uzp2 v22.8H, v16.8H, v20.8H
        smlal v30.4S, v5.4H, v26.4H
        smull2 v11.4S, v22.8H, v9.8H
        smull v1.4S, v22.4H, v9.4H
        smlal2 v11.4S, v4.8H, v26.8H
        smlal v30.4S, v6.4H, v25.4H
        smlal2 v12.4S, v6.8H, v25.8H
        smlal v1.4S, v4.4H, v26.4H
        smlal2 v11.4S, v5.8H, v25.8H
        smlal v1.4S, v5.4H, v25.4H
        smlal2 v11.4S, v6.8H, v24.8H
        uzp1 v20.8H, v30.8H, v12.8H
        smlal v1.4S, v6.4H, v24.4H
        smlal v3.4S, v21.4H, v0.H[0]
        smlal2 v29.4S, v21.8H, v0.H[0]
        smlal2 v28.4S, v6.8H, v26.8H
        smlal v17.4S, v7.4H, v25.4H
        uzp1 v2.8H, v1.8H, v11.8H
        smlal2 v28.4S, v7.8H, v25.8H
        mul v22.8H, v20.8H, v0.H[2]
        uzp2 v15.8H, v3.8H, v29.8H
        smull v13.4S, v15.4H, v9.4H
        smull2 v21.4S, v15.8H, v9.8H
        uzp1 v31.8H, v17.8H, v28.8H
        smlal v13.4S, v4.4H, v25.4H
        mul v6.8H, v31.8H, v0.H[2]
        smlal2 v21.4S, v4.8H, v25.8H
        smlal2 v21.4S, v5.8H, v24.8H
        smlal v13.4S, v5.4H, v24.4H
        smlal2 v28.4S, v6.8H, v0.H[0]
        smlal v17.4S, v6.4H, v0.H[0]
        mul v29.8H, v2.8H, v0.H[2]
        uzp1 v6.8H, v13.8H, v21.8H
        smlal v30.4S, v22.4H, v0.H[0]
        uzp2 v14.8H, v17.8H, v28.8H
        mul v18.8H, v6.8H, v0.H[2]
        smull2 v26.4S, v14.8H, v9.8H
        smull v28.4S, v14.4H, v9.4H
        smlal2 v26.4S, v4.8H, v24.8H
        smlal v28.4S, v4.4H, v24.4H
        smlal v13.4S, v18.4H, v0.H[0]
        smlal2 v21.4S, v18.8H, v0.H[0]
        smlal v1.4S, v29.4H, v0.H[0]
        smlal2 v11.4S, v29.8H, v0.H[0]
        uzp1 v18.8H, v28.8H, v26.8H
        smlal2 v12.4S, v22.8H, v0.H[0]
        uzp2 v9.8H, v13.8H, v21.8H
        mul v5.8H, v18.8H, v0.H[2]
        uzp2 v10.8H, v1.8H, v11.8H
        uzp2 v11.8H, v30.8H, v12.8H
        smlal v28.4S, v5.4H, v0.H[0]
        smlal2 v26.4S, v5.8H, v0.H[0]
        uzp2 v8.8H, v28.8H, v26.8H
        st4 {v8.8H, v9.8H, v10.8H, v11.8H}, [\dst], #64
.endm

.global poly_keygen_public_arith_pair_asm
.global _poly_keygen_public_arith_pair_asm
poly_keygen_public_arith_pair_asm:
_poly_keygen_public_arith_pair_asm:
        mov x9, x0
        mov x10, x1
        mov x11, x2
        mov x12, x3
        mov x13, x4
        mov x14, x5

        adr x6, Lkeygen_pair_base_consts
        ld1 {v0.8H}, [x6]

        LOAD_ADDR_PAGE(x15, gt_rowbitrev_lambda)
        LOAD_ADDR_OFF(x15, gt_rowbitrev_lambda)

        mov x8, #24

Lkeygen_public_arith_pair_loop:
        ld1 {v9.8H}, [x15], #16
        mov v19.16B, v9.16B
        KEYGEN_PAIR_BASEGT_PRODUCT x9, x12, x13
        mov v9.16B, v19.16B
        KEYGEN_PAIR_BASEGT_PRODUCT x10, x11, x14
        subs x8, x8, #1
        b.ne Lkeygen_public_arith_pair_loop

        ret

.align 4
Lkeygen_pair_base_consts:
        .hword 0x0d81, 0x4bd4, 0xcd7f, 0xff6d, 0xfa8f, 0xf9dd, 0xc5d5, 0x0000
