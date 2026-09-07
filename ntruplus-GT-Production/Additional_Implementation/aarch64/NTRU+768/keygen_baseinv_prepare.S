/*
 * Production direct-CQ two-block Baseinv prepare.
 *
 * Arithmetic schedule adapted from NTRU+ Official Main commit
 * 0c249d5828b90e8dd5de2c8405323d5ee2a0ce41, asm/base.s SHA-256
 * b7ddd7c0859769c7d35d875717f09b90f303c04b415b6d1ec2ea274f893ba872.
 * The fixed-register two-block loop was rescheduled for Cortex-A76 by the
 * Wave 19 Slothy workflow; its exact 199-instruction multiset is unchanged.
 *
 * ABI:
 *   x0 = numerator[24][32]
 *   x1 = den[24][8]
 *   x2 = direct-CQ input[24][32]
 *
 * Arithmetic is adapted from Official poly_baseinv_1, but lambda vectors are
 * loaded from the Production direct-CQ table. No layout adapter is present.
 */
.text
.p2align 5

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

.global C_SYM(gt_keygen_baseinv_cq_prepare)
#ifndef __APPLE__
.type C_SYM(gt_keygen_baseinv_cq_prepare), %function
#endif
C_SYM(gt_keygen_baseinv_cq_prepare):
    stp d8,  d9,  [sp, #-64]!
    stp d10, d11, [sp, #16]
    stp d12, d13, [sp, #32]
    stp d14, d15, [sp, #48]

    dst       .req x0
    den       .req x1
    src       .req x2
    zetas_ptr .req x3
    counter   .req x8

    adr x4, Lgt_keygen_baseinv_prepare_constants
    ldr q0, [x4]
    LOAD_ADDR_PAGE(zetas_ptr, gt_keygen_bpq_lambda8)
    LOAD_ADDR_OFF(zetas_ptr, gt_keygen_bpq_lambda8)

    mov counter, #1536

Lgt_keygen_baseinv_cq_prepare_loop:
    ld1 {v3.8H, v4.8H, v5.8H, v6.8H}, [src], #64
    ld1 {v1.8H, v2.8H}, [zetas_ptr], #32
    ld1 {v7.8H, v8.8H, v9.8H, v10.8H}, [src], #64
    neg v26.8H, v6.8H
    smull v15.4S, v6.4H, v6.4H
    neg v27.8H, v5.8H
    smull2 v16.4S, v6.8H, v6.8H
    shl v26.8H, v26.8H, #1
    smull2 v12.4S, v5.8H, v5.8H
    shl v27.8H, v27.8H, #1
    smlal2 v12.4S, v4.8H, v26.8H
    uzp1 v21.8H, v15.8H, v16.8H
    neg v30.8H, v10.8H
    smull v17.4S, v10.4H, v10.4H
    mul v21.8H, v21.8H, v0.H[2]
    neg v31.8H, v9.8H
    shl v30.8H, v30.8H, #1
    shl v31.8H, v31.8H, #1
    smull2 v18.4S, v10.8H, v10.8H
    smull v13.4S, v9.4H, v9.4H
    smlal v15.4S, v21.4H, v0.H[0]
    uzp1 v22.8H, v17.8H, v18.8H
    smlal v13.4S, v8.4H, v30.4H
    smull v11.4S, v5.4H, v5.4H
    smlal v11.4S, v4.4H, v26.4H
    smull2 v14.4S, v9.8H, v9.8H
    smlal2 v14.4S, v8.8H, v30.8H
    smlal2 v16.4S, v21.8H, v0.H[0]
    mul v22.8H, v22.8H, v0.H[2]
    uzp1 v19.8H, v11.8H, v12.8H
    uzp2 v25.8H, v15.8H, v16.8H
    mul v19.8H, v19.8H, v0.H[2]
    uzp1 v20.8H, v13.8H, v14.8H
    smlal2 v18.4S, v22.8H, v0.H[0]
    smlal v17.4S, v22.4H, v0.H[0]
    smull v15.4S, v25.4H, v1.4H
    smlal v11.4S, v19.4H, v0.H[0]
    smlal2 v12.4S, v19.8H, v0.H[0]
    mul v20.8H, v20.8H, v0.H[2]
    uzp2 v29.8H, v17.8H, v18.8H
    uzp2 v24.8H, v11.8H, v12.8H
    smlal2 v14.4S, v20.8H, v0.H[0]
    smlal v13.4S, v20.4H, v0.H[0]
    smlal v15.4S, v4.4H, v4.4H
    smull2 v12.4S, v24.8H, v1.8H
    smull v11.4S, v24.4H, v1.4H
    uzp2 v28.8H, v13.8H, v14.8H
    smlal v11.4S, v3.4H, v3.4H
    smlal2 v12.4S, v3.8H, v3.8H
    smull2 v14.4S, v28.8H, v2.8H
    smlal v15.4S, v3.4H, v27.4H
    uzp1 v19.8H, v11.8H, v12.8H
    smlal2 v14.4S, v7.8H, v7.8H
    mul v19.8H, v19.8H, v0.H[2]
    smull v13.4S, v28.4H, v2.4H
    smlal v13.4S, v7.4H, v7.4H
    smull2 v16.4S, v25.8H, v1.8H
    smlal v11.4S, v19.4H, v0.H[0]
    smull2 v18.4S, v29.8H, v2.8H
    uzp1 v20.8H, v13.8H, v14.8H
    smull v17.4S, v29.4H, v2.4H
    smlal2 v16.4S, v4.8H, v4.8H
    smlal2 v18.4S, v8.8H, v8.8H
    smlal v17.4S, v8.4H, v8.4H
    smlal2 v16.4S, v3.8H, v27.8H
    smlal2 v18.4S, v7.8H, v31.8H
    smlal v17.4S, v7.4H, v31.4H
    smlal2 v12.4S, v19.8H, v0.H[0]
    mul v20.8H, v20.8H, v0.H[2]
    uzp1 v21.8H, v15.8H, v16.8H
    mul v21.8H, v21.8H, v0.H[2]
    uzp1 v22.8H, v17.8H, v18.8H
    uzp2 v24.8H, v11.8H, v12.8H
    mul v22.8H, v22.8H, v0.H[2]
    smlal2 v14.4S, v20.8H, v0.H[0]
    smlal2 v16.4S, v21.8H, v0.H[0]
    smlal v15.4S, v21.4H, v0.H[0]
    smlal2 v18.4S, v22.8H, v0.H[0]
    smlal v17.4S, v22.4H, v0.H[0]
    smlal v13.4S, v20.4H, v0.H[0]
    uzp2 v28.8H, v13.8H, v14.8H
    uzp2 v29.8H, v17.8H, v18.8H
    uzp2 v25.8H, v15.8H, v16.8H
    smull2 v14.4S, v29.8H, v2.8H
    neg v31.8H, v29.8H
    smull v13.4S, v29.4H, v2.4H
    neg v27.8H, v25.8H
    smull2 v12.4S, v25.8H, v1.8H
    smull v11.4S, v25.4H, v1.4H
    uzp1 v20.8H, v13.8H, v14.8H
    mul v20.8H, v20.8H, v0.H[2]
    uzp1 v19.8H, v11.8H, v12.8H
    mul v19.8H, v19.8H, v0.H[2]
    smlal2 v14.4S, v20.8H, v0.H[0]
    smlal v13.4S, v20.4H, v0.H[0]
    smlal v11.4S, v19.4H, v0.H[0]
    smlal2 v12.4S, v19.8H, v0.H[0]
    uzp2 v30.8H, v13.8H, v14.8H
    smull v13.4S, v28.4H, v28.4H
    uzp2 v26.8H, v11.8H, v12.8H
    smlal v13.4S, v31.4H, v30.4H
    smull2 v14.4S, v28.8H, v28.8H
    smlal2 v14.4S, v31.8H, v30.8H
    smull2 v12.4S, v24.8H, v24.8H
    smull v11.4S, v24.4H, v24.4H
    smlal2 v12.4S, v27.8H, v26.8H
    smlal v11.4S, v27.4H, v26.4H
    uzp1 v20.8H, v13.8H, v14.8H
    smull2 v16.4S, v5.8H, v24.8H
    mul v20.8H, v20.8H, v0.H[2]
    uzp1 v19.8H, v11.8H, v12.8H
    smlal2 v16.4S, v3.8H, v25.8H
    mul v19.8H, v19.8H, v0.H[2]
    smlal v13.4S, v20.4H, v0.H[0]
    smlal2 v14.4S, v20.8H, v0.H[0]
    smull v15.4S, v5.4H, v24.4H
    smlal2 v12.4S, v19.8H, v0.H[0]
    smlal v11.4S, v19.4H, v0.H[0]
    uzp2 v20.8H, v13.8H, v14.8H
    uzp2 v19.8H, v11.8H, v12.8H
    smlal v15.4S, v3.4H, v25.4H
    smull2 v12.4S, v3.8H, v24.8H
    st1 {v19.8H, v20.8H}, [den], #32
    smull v11.4S, v3.4H, v24.4H
    smlal2 v12.4S, v5.8H, v26.8H
    smlal v11.4S, v5.4H, v26.4H
    uzp1 v21.8H, v15.8H, v16.8H
    smull2 v14.4S, v6.8H, v26.8H
    smull v13.4S, v6.4H, v26.4H
    mul v21.8H, v21.8H, v0.H[2]
    uzp1 v19.8H, v11.8H, v12.8H
    smlal2 v14.4S, v4.8H, v24.8H
    smlal v13.4S, v4.4H, v24.4H
    smull2 v18.4S, v4.8H, v25.8H
    smlal v15.4S, v21.4H, v0.H[0]
    smlal2 v18.4S, v6.8H, v24.8H
    smull v17.4S, v4.4H, v25.4H
    uzp1 v20.8H, v13.8H, v14.8H
    smlal v17.4S, v6.4H, v24.4H
    mul v19.8H, v19.8H, v0.H[2]
    mul v20.8H, v20.8H, v0.H[2]
    uzp1 v22.8H, v17.8H, v18.8H
    mul v22.8H, v22.8H, v0.H[2]
    smlal2 v12.4S, v19.8H, v0.H[0]
    smlal v11.4S, v19.4H, v0.H[0]
    smlal v13.4S, v20.4H, v0.H[0]
    smlal2 v14.4S, v20.8H, v0.H[0]
    smlal2 v18.4S, v22.8H, v0.H[0]
    smlal2 v16.4S, v21.8H, v0.H[0]
    uzp2 v11.8H, v11.8H, v12.8H
    smlal v17.4S, v22.4H, v0.H[0]
    uzp2 v12.8H, v13.8H, v14.8H
    uzp2 v13.8H, v15.8H, v16.8H
    smull v15.4S, v9.4H, v28.4H
    smull2 v16.4S, v9.8H, v28.8H
    uzp2 v14.8H, v17.8H, v18.8H
    smull2 v18.4S, v8.8H, v29.8H
    str q11, [dst, #0]
    smull v11.4S, v7.4H, v28.4H
    smlal v15.4S, v7.4H, v29.4H
    str q14, [dst, #48]
    smlal2 v16.4S, v7.8H, v29.8H
    str q12, [dst, #16]
    smlal v11.4S, v9.4H, v30.4H
    smlal2 v18.4S, v10.8H, v28.8H
    str q13, [dst, #32]
    smull2 v12.4S, v7.8H, v28.8H
    smlal2 v12.4S, v9.8H, v30.8H
    uzp1 v21.8H, v15.8H, v16.8H
    mul v21.8H, v21.8H, v0.H[2]
    uzp1 v19.8H, v11.8H, v12.8H
    smull v13.4S, v10.4H, v30.4H
    smull v17.4S, v8.4H, v29.4H
    smlal v17.4S, v10.4H, v28.4H
    smlal2 v16.4S, v21.8H, v0.H[0]
    smull2 v14.4S, v10.8H, v30.8H
    smlal v13.4S, v8.4H, v28.4H
    uzp1 v22.8H, v17.8H, v18.8H
    smlal2 v14.4S, v8.8H, v28.8H
    mul v19.8H, v19.8H, v0.H[2]
    uzp1 v20.8H, v13.8H, v14.8H
    mul v20.8H, v20.8H, v0.H[2]
    mul v22.8H, v22.8H, v0.H[2]
    smlal v11.4S, v19.4H, v0.H[0]
    smlal2 v12.4S, v19.8H, v0.H[0]
    smlal v13.4S, v20.4H, v0.H[0]
    smlal2 v14.4S, v20.8H, v0.H[0]
    smlal v17.4S, v22.4H, v0.H[0]
    smlal v15.4S, v21.4H, v0.H[0]
    uzp2 v11.8H, v11.8H, v12.8H
    smlal2 v18.4S, v22.8H, v0.H[0]
    uzp2 v12.8H, v13.8H, v14.8H
    str q11, [dst, #64]
    uzp2 v13.8H, v15.8H, v16.8H
    str q12, [dst, #80]
    uzp2 v14.8H, v17.8H, v18.8H
    str q13, [dst, #96]
    str q14, [dst, #112]
    add dst, dst, #128
    subs counter, counter, #128
    b.ne Lgt_keygen_baseinv_cq_prepare_loop

    .unreq    dst
    .unreq    den
    .unreq    src
    .unreq    zetas_ptr
    .unreq    counter

    ldp d10, d11, [sp, #16]
    ldp d12, d13, [sp, #32]
    ldp d14, d15, [sp, #48]
    ldp d8,  d9,  [sp], #64

    ins v8.d[1], xzr
    ins v9.d[1], xzr
    ins v10.d[1], xzr
    ins v11.d[1], xzr
    ins v12.d[1], xzr
    ins v13.d[1], xzr
    ins v14.d[1], xzr
    ins v15.d[1], xzr
    movi v0.16b, #0
    movi v1.16b, #0
    movi v2.16b, #0
    movi v3.16b, #0
    movi v4.16b, #0
    movi v5.16b, #0
    movi v6.16b, #0
    movi v7.16b, #0
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
    movi v27.16b, #0
    movi v28.16b, #0
    movi v29.16b, #0
    movi v30.16b, #0
    movi v31.16b, #0
    ret
#ifndef __APPLE__
.size C_SYM(gt_keygen_baseinv_cq_prepare), .-C_SYM(gt_keygen_baseinv_cq_prepare)
#endif

.p2align 4
Lgt_keygen_baseinv_prepare_constants:
    .hword 3457, 19412, -12929, -147, -1393, -682, -6464, 0
