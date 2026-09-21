
/* Section: keygen_baseinv_prepare.S; private namespace module_keygen_baseinv_prepare_ */
#ifdef __APPLE__
.text
#else
.section .text.module_keygen_baseinv_prepare_body,"ax",%progbits
#endif
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
 *   x1 = module_keygen_baseinv_prepare_den[24][8]
 *   x2 = direct-CQ input[24][32]
 *
 * Arithmetic is adapted from Official poly_baseinv_1, but lambda vectors are
 * loaded from the Production direct-CQ table. No layout adapter is present.
 */
#ifdef __APPLE__
.text
#else
.section .text.module_keygen_baseinv_prepare_body,"ax",%progbits
#endif
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

    module_keygen_baseinv_prepare_dst       .req x0
    module_keygen_baseinv_prepare_den       .req x1
    module_keygen_baseinv_prepare_src       .req x2
    module_keygen_baseinv_prepare_zetas_ptr .req x3
    module_keygen_baseinv_prepare_counter   .req x8

    adr x4, module_keygen_baseinv_prepare_Lgt_keygen_baseinv_prepare_constants
    ldr q0, [x4]
    LOAD_ADDR_PAGE(module_keygen_baseinv_prepare_zetas_ptr, gt_keygen_bpq_lambda8)
    LOAD_ADDR_OFF(module_keygen_baseinv_prepare_zetas_ptr, gt_keygen_bpq_lambda8)

    mov module_keygen_baseinv_prepare_counter, #1536

module_keygen_baseinv_prepare_Lgt_keygen_baseinv_cq_prepare_loop:
    ld1 {v3.8H, v4.8H, v5.8H, v6.8H}, [module_keygen_baseinv_prepare_src], #64
    ld1 {v1.8H, v2.8H}, [module_keygen_baseinv_prepare_zetas_ptr], #32
    ld1 {v7.8H, v8.8H, v9.8H, v10.8H}, [module_keygen_baseinv_prepare_src], #64
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
    st1 {v19.8H, v20.8H}, [module_keygen_baseinv_prepare_den], #32
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
    str q11, [module_keygen_baseinv_prepare_dst, #0]
    smull v11.4S, v7.4H, v28.4H
    smlal v15.4S, v7.4H, v29.4H
    str q14, [module_keygen_baseinv_prepare_dst, #48]
    smlal2 v16.4S, v7.8H, v29.8H
    str q12, [module_keygen_baseinv_prepare_dst, #16]
    smlal v11.4S, v9.4H, v30.4H
    smlal2 v18.4S, v10.8H, v28.8H
    str q13, [module_keygen_baseinv_prepare_dst, #32]
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
    str q11, [module_keygen_baseinv_prepare_dst, #64]
    uzp2 v13.8H, v15.8H, v16.8H
    str q12, [module_keygen_baseinv_prepare_dst, #80]
    uzp2 v14.8H, v17.8H, v18.8H
    str q13, [module_keygen_baseinv_prepare_dst, #96]
    str q14, [module_keygen_baseinv_prepare_dst, #112]
    add module_keygen_baseinv_prepare_dst, module_keygen_baseinv_prepare_dst, #128
    subs module_keygen_baseinv_prepare_counter, module_keygen_baseinv_prepare_counter, #128
    b.ne module_keygen_baseinv_prepare_Lgt_keygen_baseinv_cq_prepare_loop

    .unreq    module_keygen_baseinv_prepare_dst
    .unreq    module_keygen_baseinv_prepare_den
    .unreq    module_keygen_baseinv_prepare_src
    .unreq    module_keygen_baseinv_prepare_zetas_ptr
    .unreq    module_keygen_baseinv_prepare_counter

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
module_keygen_baseinv_prepare_Lgt_keygen_baseinv_prepare_constants:
    .hword 3457, 19412, -12929, -147, -1393, -682, -6464, 0

/* End section: keygen_baseinv_prepare.S */

/* Section: keygen_baseinv_tree.S; private namespace module_keygen_baseinv_tree_ */
#ifdef __APPLE__
.text
#else
.section .text.module_keygen_baseinv_tree_body,"ax",%progbits
#endif
/*
 * Production keygen balanced HIER_K8 tree for 24 CQ denominators.
 *
 * ABI:
 *   x0 = int16_t den[24][8]
 *   w0 = 0 on success, 1 if any denominator product is zero
 *
 * The input/output layout is the coefficient-Q scratch layout used by the
 * fixed Direct-CQ key-generation pipeline.
 */
#ifdef __APPLE__
.text
#else
.section .text.module_keygen_baseinv_tree_body,"ax",%progbits
#endif
.align 2

/*
 * Common symbol and address helpers for GT production assembly.
 */

#ifndef GT_COMMON_INC
#define GT_COMMON_INC

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

#endif

.equ module_keygen_baseinv_tree_BPQ_TREE_C01_OFFSET, 0
.equ module_keygen_baseinv_tree_BPQ_TREE_GROUP_OFFSET, 128
.equ module_keygen_baseinv_tree_BPQ_TREE_LOCAL_BYTES, 256

.macro module_keygen_baseinv_tree_fqmul dst, lhs, rhs
	smull v16.4s, \lhs\().4h, \rhs\().4h
	smull2 v17.4s, \lhs\().8h, \rhs\().8h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal v16.4s, v18.4h, v1.h[0]
	smlal2 v17.4s, v18.8h, v1.h[0]
	uzp2 \dst\().8h, v16.8h, v17.8h
.endm

.macro module_keygen_baseinv_tree_fqmul2 d0, l0, r0, d1, l1, r1
	smull v16.4s, \l0\().4h, \r0\().4h
	smull2 v17.4s, \l0\().8h, \r0\().8h
	smull v18.4s, \l1\().4h, \r1\().4h
	smull2 v19.4s, \l1\().8h, \r1\().8h
	uzp1 v20.8h, v16.8h, v17.8h
	uzp1 v21.8h, v18.8h, v19.8h
	mul v20.8h, v20.8h, v1.h[2]
	mul v21.8h, v21.8h, v1.h[2]
	smlal v16.4s, v20.4h, v1.h[0]
	smlal2 v17.4s, v20.8h, v1.h[0]
	smlal v18.4s, v21.4h, v1.h[0]
	smlal2 v19.4s, v21.8h, v1.h[0]
	uzp2 \d0\().8h, v16.8h, v17.8h
	uzp2 \d1\().8h, v18.8h, v19.8h
.endm

.macro module_keygen_baseinv_tree_fqmul4 d0, l0, r0, d1, l1, r1, d2, l2, r2, d3, l3, r3
	smull v16.4s, \l0\().4h, \r0\().4h
	smull2 v17.4s, \l0\().8h, \r0\().8h
	smull v18.4s, \l1\().4h, \r1\().4h
	smull2 v19.4s, \l1\().8h, \r1\().8h
	smull v20.4s, \l2\().4h, \r2\().4h
	smull2 v21.4s, \l2\().8h, \r2\().8h
	smull v22.4s, \l3\().4h, \r3\().4h
	smull2 v23.4s, \l3\().8h, \r3\().8h
	uzp1 v24.8h, v16.8h, v17.8h
	uzp1 v25.8h, v18.8h, v19.8h
	uzp1 v26.8h, v20.8h, v21.8h
	uzp1 v27.8h, v22.8h, v23.8h
	mul v24.8h, v24.8h, v1.h[2]
	mul v25.8h, v25.8h, v1.h[2]
	mul v26.8h, v26.8h, v1.h[2]
	mul v27.8h, v27.8h, v1.h[2]
	smlal v16.4s, v24.4h, v1.h[0]
	smlal2 v17.4s, v24.8h, v1.h[0]
	smlal v18.4s, v25.4h, v1.h[0]
	smlal2 v19.4s, v25.8h, v1.h[0]
	smlal v20.4s, v26.4h, v1.h[0]
	smlal2 v21.4s, v26.8h, v1.h[0]
	smlal v22.4s, v27.4h, v1.h[0]
	smlal2 v23.4s, v27.8h, v1.h[0]
	uzp2 \d0\().8h, v16.8h, v17.8h
	uzp2 \d1\().8h, v18.8h, v19.8h
	uzp2 \d2\().8h, v20.8h, v21.8h
	uzp2 \d3\().8h, v22.8h, v23.8h
.endm

.macro module_keygen_baseinv_tree_form_group_pair denoff, scratchoff
	ldp q2, q3, [x19, #(\denoff)]
	ldr q4, [x19, #(\denoff + 32)]
	ldp q5, q6, [x19, #(\denoff + 48)]
	ldr q7, [x19, #(\denoff + 80)]
	module_keygen_baseinv_tree_fqmul2 v8, v2, v3, v9, v5, v6
	stp q8, q9, [sp, #(module_keygen_baseinv_tree_BPQ_TREE_C01_OFFSET + \scratchoff)]
	module_keygen_baseinv_tree_fqmul2 v10, v8, v4, v11, v9, v7
	stp q10, q11, [sp, #(module_keygen_baseinv_tree_BPQ_TREE_GROUP_OFFSET + \scratchoff)]
.endm

/* Recover two adjacent three-denominator groups from two group inverses. */
.macro module_keygen_baseinv_tree_recover_group_pair denoff, c01off, group_inv0, group_inv1
	ldp q2, q3, [x19, #(\denoff)]
	ldr q4, [x19, #(\denoff + 32)]
	ldp q5, q6, [x19, #(\denoff + 48)]
	ldr q7, [x19, #(\denoff + 80)]
	ldp q8, q9, [sp, #(module_keygen_baseinv_tree_BPQ_TREE_C01_OFFSET + \c01off)]

	module_keygen_baseinv_tree_fqmul4 v10, v8, \group_inv0, v11, \group_inv0, v4, \
	         v12, v9, \group_inv1, v13, \group_inv1, v7
	module_keygen_baseinv_tree_fqmul4 v2, v2, v11, v3, v11, v3, \
	         v5, v5, v13, v6, v13, v6

	stp q3, q2, [x19, #(\denoff)]
	str q10, [x19, #(\denoff + 32)]
	stp q6, q5, [x19, #(\denoff + 48)]
	str q12, [x19, #(\denoff + 80)]
.endm

.global C_SYM(gt_keygen_baseinv_hier_k8)
#ifndef __APPLE__
.type C_SYM(gt_keygen_baseinv_hier_k8), %function
#endif
C_SYM(gt_keygen_baseinv_hier_k8):
	stp x30, x19, [sp, #-16]!
	stp d8, d9, [sp, #-16]!
	stp d10, d11, [sp, #-16]!
	stp d12, d13, [sp, #-16]!
	stp d14, d15, [sp, #-16]!
	sub sp, sp, #module_keygen_baseinv_tree_BPQ_TREE_LOCAL_BYTES

	mov x19, x0
	ldr q1, module_keygen_baseinv_tree_Lbpq_tree_scaled_r_consts

	/* Form c01[8] and the eight three-denominator group products. */
	module_keygen_baseinv_tree_form_group_pair 0, 0
	module_keygen_baseinv_tree_form_group_pair 96, 32
	module_keygen_baseinv_tree_form_group_pair 192, 64
	module_keygen_baseinv_tree_form_group_pair 288, 96

	/* Balanced forward tree: 8 -> 4 -> 2 -> 1. */
	ldp q2, q3, [sp, #module_keygen_baseinv_tree_BPQ_TREE_GROUP_OFFSET]
	ldp q4, q5, [sp, #(module_keygen_baseinv_tree_BPQ_TREE_GROUP_OFFSET + 32)]
	ldp q6, q7, [sp, #(module_keygen_baseinv_tree_BPQ_TREE_GROUP_OFFSET + 64)]
	ldp q14, q15, [sp, #(module_keygen_baseinv_tree_BPQ_TREE_GROUP_OFFSET + 96)]
	module_keygen_baseinv_tree_fqmul4 v8, v2, v3, v9, v4, v5, \
	         v10, v6, v7, v11, v14, v15
	module_keygen_baseinv_tree_fqmul2 v12, v8, v9, v13, v10, v11
	module_keygen_baseinv_tree_fqmul v0, v12, v13

	uminv h2, v0.8h
	umov w8, v2.h[0]
	cbz w8, module_keygen_baseinv_tree_Lbpq_tree_failure

	bl C_SYM(gt_fqinv15_asm)
	ldr q1, module_keygen_baseinv_tree_Lbpq_tree_scaled_r_consts

	/* Balanced backward tree: 1 -> 2 -> 4 -> 8. */
	module_keygen_baseinv_tree_fqmul2 v2, v0, v13, v3, v0, v12
	module_keygen_baseinv_tree_fqmul4 v4, v2, v9, v5, v2, v8, \
	         v6, v3, v11, v7, v3, v10

	ldp q2, q3, [sp, #module_keygen_baseinv_tree_BPQ_TREE_GROUP_OFFSET]
	ldp q8, q9, [sp, #(module_keygen_baseinv_tree_BPQ_TREE_GROUP_OFFSET + 32)]
	module_keygen_baseinv_tree_fqmul4 v12, v3, v4, v13, v2, v4, \
	         v14, v9, v5, v15, v8, v5
	ldp q2, q3, [sp, #(module_keygen_baseinv_tree_BPQ_TREE_GROUP_OFFSET + 64)]
	ldp q8, q9, [sp, #(module_keygen_baseinv_tree_BPQ_TREE_GROUP_OFFSET + 96)]
	module_keygen_baseinv_tree_fqmul4 v28, v3, v6, v29, v2, v6, \
	         v30, v9, v7, v31, v8, v7

	module_keygen_baseinv_tree_recover_group_pair 0, 0, v12, v13
	module_keygen_baseinv_tree_recover_group_pair 96, 32, v14, v15
	module_keygen_baseinv_tree_recover_group_pair 192, 64, v28, v29
	module_keygen_baseinv_tree_recover_group_pair 288, 96, v30, v31

	mov w0, wzr
	b module_keygen_baseinv_tree_Lbpq_tree_return

module_keygen_baseinv_tree_Lbpq_tree_failure:
	mov w0, #1

module_keygen_baseinv_tree_Lbpq_tree_return:
	ldp d14, d15, [sp, #(module_keygen_baseinv_tree_BPQ_TREE_LOCAL_BYTES + 0)]
	ldp d12, d13, [sp, #(module_keygen_baseinv_tree_BPQ_TREE_LOCAL_BYTES + 16)]
	ldp d10, d11, [sp, #(module_keygen_baseinv_tree_BPQ_TREE_LOCAL_BYTES + 32)]
	ldp d8, d9, [sp, #(module_keygen_baseinv_tree_BPQ_TREE_LOCAL_BYTES + 48)]
	ldp x30, x19, [sp, #(module_keygen_baseinv_tree_BPQ_TREE_LOCAL_BYTES + 64)]
	add sp, sp, #(module_keygen_baseinv_tree_BPQ_TREE_LOCAL_BYTES + 80)
	ret
#ifndef __APPLE__
.size C_SYM(gt_keygen_baseinv_hier_k8), \
	.-C_SYM(gt_keygen_baseinv_hier_k8)
#endif

.p2align 4
module_keygen_baseinv_tree_Lbpq_tree_scaled_r_consts:
	.hword 3457, 19412, -12929, -147, -1393, -682, -6464, 0

/* End section: keygen_baseinv_tree.S */

/* Section: keygen_baseinv_finish.S; private namespace module_keygen_baseinv_finish_ */
#ifdef __APPLE__
.text
#else
.section .text.module_keygen_baseinv_finish_body,"ax",%progbits
#endif
/* Production keygen baseinv finish: CQ output for mixed basemul. */
#ifdef __APPLE__
.text
#else
.section .text.module_keygen_baseinv_finish_body,"ax",%progbits
#endif
.align 2

/*
 * Common symbol and address helpers for GT production assembly.
 */

#ifndef GT_COMMON_INC
#define GT_COMMON_INC

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

#endif

.macro module_keygen_baseinv_finish_fqmul4 d0, l0, r0, d1, l1, r1, d2, l2, r2, d3, l3, r3
	smull v16.4s, \l0\().4h, \r0\().4h
	smull2 v17.4s, \l0\().8h, \r0\().8h
	smull v18.4s, \l1\().4h, \r1\().4h
	smull2 v19.4s, \l1\().8h, \r1\().8h
	smull v20.4s, \l2\().4h, \r2\().4h
	smull2 v21.4s, \l2\().8h, \r2\().8h
	smull v22.4s, \l3\().4h, \r3\().4h
	smull2 v23.4s, \l3\().8h, \r3\().8h
	uzp1 v24.8h, v16.8h, v17.8h
	uzp1 v25.8h, v18.8h, v19.8h
	uzp1 v26.8h, v20.8h, v21.8h
	uzp1 v27.8h, v22.8h, v23.8h
	mul v24.8h, v24.8h, v1.h[2]
	mul v25.8h, v25.8h, v1.h[2]
	mul v26.8h, v26.8h, v1.h[2]
	mul v27.8h, v27.8h, v1.h[2]
	smlal v16.4s, v24.4h, v1.h[0]
	smlal2 v17.4s, v24.8h, v1.h[0]
	smlal v18.4s, v25.4h, v1.h[0]
	smlal2 v19.4s, v25.8h, v1.h[0]
	smlal v20.4s, v26.4h, v1.h[0]
	smlal2 v21.4s, v26.8h, v1.h[0]
	smlal v22.4s, v27.4h, v1.h[0]
	smlal2 v23.4s, v27.8h, v1.h[0]
	uzp2 \d0\().8h, v16.8h, v17.8h
	uzp2 \d1\().8h, v18.8h, v19.8h
	uzp2 \d2\().8h, v20.8h, v21.8h
	uzp2 \d3\().8h, v22.8h, v23.8h
.endm

/* x0=CQ output, x1=CQ numerator scratch, x2=inverted denominators. */
.global C_SYM(gt_keygen_baseinv_cq_finish)
#ifndef __APPLE__
.type C_SYM(gt_keygen_baseinv_cq_finish), %function
#endif
C_SYM(gt_keygen_baseinv_cq_finish):
	ldr q1, module_keygen_baseinv_finish_Lbpq_finish_scaled_r_consts
	mov w3, #24

module_keygen_baseinv_finish_Lbpq_finish_cq_loop:
	ldp q2, q3, [x1], #32
	ldp q4, q5, [x1], #32
	ldr q6, [x2], #16
	neg v7.8h, v6.8h

	module_keygen_baseinv_finish_fqmul4 v28, v2, v6, v29, v3, v7, \
	         v30, v4, v6, v31, v5, v7

	stp q28, q29, [x0], #32
	stp q30, q31, [x0], #32
	subs w3, w3, #1
	b.ne module_keygen_baseinv_finish_Lbpq_finish_cq_loop
	ret
#ifndef __APPLE__
.size C_SYM(gt_keygen_baseinv_cq_finish), \
	.-C_SYM(gt_keygen_baseinv_cq_finish)
#endif

.p2align 4
module_keygen_baseinv_finish_Lbpq_finish_scaled_r_consts:
	.hword 3457, 19412, -12929, -147, -1393, -682, -6464, 0

/* End section: keygen_baseinv_finish.S */

/* Section: fqinv.S; private namespace module_fqinv_ */
#ifdef __APPLE__
.text
#else
.section .text.module_fqinv_body,"ax",%progbits
#endif
/*
 * GT batch baseinv scalar-field inversion core.
 *
 * ABI:
 *   v0 = input vector a
 *   v1 = constants vector:
 *        h[0] = q, h[2] = qinv, h[5]/h[6] = final scale/precompute
 *   returns v0 = a^{-1} in the same Montgomery/scaled representation as the
 *                existing C Neon fqinv_neon().
 *
 * Caller-saved vector registers only: v0-v7 and v16-v21.
 *
 * The 15-multiplication exponent DAG and instruction order were scheduled for
 * Cortex-A76 with fixed-register Slothy scheduling.
 */
#ifdef __APPLE__
.text
#else
.section .text.module_fqinv_body,"ax",%progbits
#endif
.p2align 5

/*
 * Common symbol and address helpers for GT production assembly.
 */

#ifndef GT_COMMON_INC
#define GT_COMMON_INC

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

#endif

.global C_SYM(gt_fqinv15_asm)
C_SYM(gt_fqinv15_asm):
	smull v16.4s, v0.4h, v0.4h
	orr v2.16b, v0.16b, v0.16b
	smull2 v17.4s, v0.8h, v0.8h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal v16.4s, v18.4h, v1.h[0]
	smlal2 v17.4s, v18.8h, v1.h[0]
	uzp2 v0.8h, v16.8h, v17.8h
	smull v16.4s, v0.4h, v0.4h
	smull2 v17.4s, v0.8h, v0.8h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal2 v17.4s, v18.8h, v1.h[0]
	smlal v16.4s, v18.4h, v1.h[0]
	uzp2 v0.8h, v16.8h, v17.8h
	smull v16.4s, v0.4h, v0.4h
	smull2 v17.4s, v0.8h, v0.8h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal2 v17.4s, v18.8h, v1.h[0]
	smlal v16.4s, v18.4h, v1.h[0]
	uzp2 v0.8h, v16.8h, v17.8h
	smull2 v17.4s, v0.8h, v0.8h
	smull v16.4s, v0.4h, v0.4h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal v16.4s, v18.4h, v1.h[0]
	smlal2 v17.4s, v18.8h, v1.h[0]
	uzp2 v3.8h, v16.8h, v17.8h
	smull v19.4s, v3.4h, v3.4h
	smull2 v20.4s, v3.8h, v3.8h
	smull v16.4s, v3.4h, v2.4h
	smull2 v17.4s, v3.8h, v2.8h
	uzp1 v21.8h, v19.8h, v20.8h
	mul v21.8h, v21.8h, v1.h[2]
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal v19.4s, v21.4h, v1.h[0]
	smlal2 v20.4s, v21.8h, v1.h[0]
	smlal2 v17.4s, v18.8h, v1.h[0]
	smlal v16.4s, v18.4h, v1.h[0]
	uzp2 v5.8h, v19.8h, v20.8h
	uzp2 v4.8h, v16.8h, v17.8h
	smull v16.4s, v5.4h, v5.4h
	smull2 v17.4s, v5.8h, v5.8h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal2 v17.4s, v18.8h, v1.h[0]
	smlal v16.4s, v18.4h, v1.h[0]
	uzp2 v0.8h, v16.8h, v17.8h
	smull2 v17.4s, v0.8h, v0.8h
	smull v16.4s, v0.4h, v0.4h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal2 v17.4s, v18.8h, v1.h[0]
	smlal v16.4s, v18.4h, v1.h[0]
	uzp2 v6.8h, v16.8h, v17.8h
	smull2 v17.4s, v6.8h, v4.8h
	smull v16.4s, v6.4h, v4.4h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal v16.4s, v18.4h, v1.h[0]
	smlal2 v17.4s, v18.8h, v1.h[0]
	uzp2 v4.8h, v16.8h, v17.8h
	smull v16.4s, v4.4h, v6.4h
	smull2 v17.4s, v4.8h, v6.8h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal2 v17.4s, v18.8h, v1.h[0]
	smlal v16.4s, v18.4h, v1.h[0]
	uzp2 v0.8h, v16.8h, v17.8h
	smull v16.4s, v0.4h, v0.4h
	smull2 v17.4s, v0.8h, v0.8h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal2 v17.4s, v18.8h, v1.h[0]
	smlal v16.4s, v18.4h, v1.h[0]
	uzp2 v0.8h, v16.8h, v17.8h
	smull2 v17.4s, v0.8h, v4.8h
	smull v16.4s, v0.4h, v4.4h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal2 v17.4s, v18.8h, v1.h[0]
	smlal v16.4s, v18.4h, v1.h[0]
	uzp2 v7.8h, v16.8h, v17.8h
	smull v16.4s, v7.4h, v7.4h
	smull2 v17.4s, v7.8h, v7.8h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal v16.4s, v18.4h, v1.h[0]
	smlal2 v17.4s, v18.8h, v1.h[0]
	uzp2 v0.8h, v16.8h, v17.8h
	smull2 v17.4s, v0.8h, v0.8h
	smull v16.4s, v0.4h, v0.4h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal v16.4s, v18.4h, v1.h[0]
	smlal2 v17.4s, v18.8h, v1.h[0]
	uzp2 v0.8h, v16.8h, v17.8h
	smull v16.4s, v0.4h, v7.4h
	smull2 v17.4s, v0.8h, v7.8h
	uzp1 v18.8h, v16.8h, v17.8h
	mul v18.8h, v18.8h, v1.h[2]
	smlal2 v17.4s, v18.8h, v1.h[0]
	smlal v16.4s, v18.4h, v1.h[0]
	uzp2 v0.8h, v16.8h, v17.8h
	sqrdmulh v3.8h, v0.8h, v1.h[6]
	mul v0.8h, v0.8h, v1.h[5]
	mls v0.8h, v3.8h, v1.h[0]
	/* v0 is the return value; erase the remaining exponent DAG. */
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
	ret

/* End section: fqinv.S */

/* Section: encap_muladd.S; private namespace module_encap_muladd_ */
#ifdef __APPLE__
.text
#else
.section .text.module_encap_muladd_body,"ax",%progbits
#endif
/*
 * GT encap-only poly_basemul_add_encap direct32 Q31 byte-contract path.
 *
 * This is the fixed production poly_basemul_add_encap endpoint used by the
 * encapsulation ciphertext path.  It keeps the selected register allocation
 * through the quartic product accumulator boundary, then replaces the product
 * Montgomery fold plus add32 finalizer with:
 *
 *   out = tobytes-contract reduce(P + c)
 *
 * The reducer uses the exhaustively-checked Q31 constant C=621199 for q=3457:
 *
 *   t = sqrdmulh_s32(x, C)
 *   y = x - t * q
 *
 * The output is byte-equivalent under poly_tobytes_encap, not a general centered
 * representative contract.  Callers must consume the result immediately with
 * poly_tobytes_encap in the encap ciphertext path.
 */

/* Instruction scheduling was generated with Slothy; release annotations removed. */
#ifdef __APPLE__
.text
#else
.section .text.module_encap_muladd_body,"ax",%progbits
#endif
.align 2

/*
 * Common symbol and address helpers for GT production assembly.
 */

#ifndef GT_COMMON_INC
#define GT_COMMON_INC

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

#endif

.global poly_basemul_add_encap
.global _poly_basemul_add_encap
poly_basemul_add_encap:
_poly_basemul_add_encap:
 sub sp, sp, #64
 stp d8, d9, [sp, #0]
 stp d10, d11, [sp, #16]
 stp d12, d13, [sp, #32]
 stp d14, d15, [sp, #48]
 LOAD_ADDR_PAGE(x4, gt_rowbitrev_lambda)
 LOAD_ADDR_OFF(x4, gt_rowbitrev_lambda)
 adr x5, module_encap_muladd_Lpoly_basemul_add_consts
 ldr q11, [x5]
 mov x6, #24

module_encap_muladd_Lpoly_basemul_add_loop:
 ld4 {v24.8H, v25.8H, v26.8H, v27.8H}, [x1], #64
 ld4 {v28.8H, v29.8H, v30.8H, v31.8H}, [x2], #64
 smull v1.4S, v27.4H, v31.4H
 ldr q16, [x4], #16
 smull2 v6.4S, v27.8H, v31.8H
 smull v15.4S, v25.4H, v31.4H
 ld4 {v19.8H, v20.8H, v21.8H, v22.8H}, [x3], #64
 smull2 v23.4S, v25.8H, v31.8H
 smlal2 v23.4S, v26.8H, v30.8H
 smlal v15.4S, v26.4H, v30.4H
 uzp1 v4.8H, v1.8H, v6.8H
 smull v17.4S, v26.4H, v31.4H
 smull2 v10.4S, v26.8H, v31.8H
 smlal2 v23.4S, v27.8H, v29.8H
 smlal v17.4S, v27.4H, v30.4H
 smull v13.4S, v27.4H, v28.4H
 smull2 v14.4S, v27.8H, v28.8H
 smlal v15.4S, v27.4H, v29.4H
 smlal2 v10.4S, v27.8H, v30.8H
 mul v2.8H, v4.8H, v11.H[2]
 smlal v13.4S, v24.4H, v31.4H
 uzp1 v12.8H, v15.8H, v23.8H
 smlal2 v14.4S, v24.8H, v31.8H
 uzp1 v31.8H, v17.8H, v10.8H
 smlal v13.4S, v25.4H, v30.4H
 smlal2 v6.4S, v2.8H, v11.H[0]
 smlal v1.4S, v2.4H, v11.H[0]
 smlal2 v14.4S, v25.8H, v30.8H
 mul v5.8H, v31.8H, v11.H[2]
 uzp2 v27.8H, v1.8H, v6.8H
 smlal2 v14.4S, v26.8H, v29.8H
 smlal v13.4S, v26.4H, v29.4H
 smull v6.4S, v27.4H, v16.4H
 smull2 v3.4S, v27.8H, v16.8H
 smlal2 v3.4S, v24.8H, v30.8H
 smlal v6.4S, v24.4H, v30.4H
 smlal v6.4S, v25.4H, v29.4H
 smlal2 v3.4S, v25.8H, v29.8H
 smlal v17.4S, v5.4H, v11.H[0]
 smlal2 v10.4S, v5.8H, v11.H[0]
 mul v27.8H, v12.8H, v11.H[2]
 smlal2 v3.4S, v26.8H, v28.8H
 smlal v6.4S, v26.4H, v28.4H
 uzp2 v1.8H, v17.8H, v10.8H
 smull2 v9.4S, v1.8H, v16.8H
 smull v4.4S, v1.4H, v16.4H
 smlal2 v9.4S, v24.8H, v29.8H
 smlal v4.4S, v24.4H, v29.4H
 smlal v15.4S, v27.4H, v11.H[0]
 smlal2 v23.4S, v27.8H, v11.H[0]
 smlal2 v9.4S, v25.8H, v28.8H
 smlal v4.4S, v25.4H, v28.4H
 uzp2 v5.8H, v15.8H, v23.8H
 smull v31.4S, v5.4H, v16.4H
 smull2 v10.4S, v5.8H, v16.8H
 smlal v31.4S, v24.4H, v28.4H
 smlal2 v10.4S, v24.8H, v28.8H

 // live-in: x0-x4, v11, and iteration-N accumulators/c vectors
 // live-out: advanced x0-x4 and iteration-N+1 Q31 accumulators/c vectors
 // coefficient range: identical to the audited production Q31 byte contract
 // reserved physical registers: x7-x30 and sp; physical vector allocation fixed
 // Packed-16 Barrett finalizer: preserve x low16, pack Q31 quotients, then
 // apply one eight-lane halfword correction.  The region is Slothy scheduled.
 saddw2 v10.4S, v10.4S, v19.8H
 saddw v31.4S, v31.4S, v19.4H
 saddw v4.4S, v4.4S, v20.4H
 saddw2 v9.4S, v9.4S, v20.8H
 uzp1 v19.8H, v31.8H, v10.8H
 sqrdmulh v10.4S, v10.4S, v11.S[2]
 saddw v6.4S, v6.4S, v21.4H
 saddw2 v3.4S, v3.4S, v21.8H
 sqrdmulh v31.4S, v31.4S, v11.S[2]
 uzp1 v20.8H, v4.8H, v9.8H
 sqrdmulh v4.4S, v4.4S, v11.S[2]
 saddw2 v14.4S, v14.4S, v22.8H
 uzp1 v31.8H, v31.8H, v10.8H
 sqrdmulh v9.4S, v9.4S, v11.S[2]
 saddw v13.4S, v13.4S, v22.4H
 mls v19.8H, v31.8H, v11.H[0]
 uzp1 v21.8H, v6.8H, v3.8H
 uzp1 v22.8H, v13.8H, v14.8H
 sqrdmulh v6.4S, v6.4S, v11.S[2]
 uzp1 v4.8H, v4.8H, v9.8H
 ld4 {v28.8H, v29.8H, v30.8H, v31.8H}, [x2], #64
 sqrdmulh v3.4S, v3.4S, v11.S[2]
 ld4 {v24.8H, v25.8H, v26.8H, v27.8H}, [x1], #64
 sqrdmulh v14.4S, v14.4S, v11.S[2]
 sqrdmulh v13.4S, v13.4S, v11.S[2]
 uzp1 v6.8H, v6.8H, v3.8H
 uzp1 v13.8H, v13.8H, v14.8H
 mls v20.8H, v4.8H, v11.H[0]
 ldr q16, [x4], #16
 mls v21.8H, v6.8H, v11.H[0]
 mls v22.8H, v13.8H, v11.H[0]
 smull v1.4S, v27.4H, v31.4H
 smull2 v23.4S, v25.8H, v31.8H
 smull2 v6.4S, v27.8H, v31.8H
 st4 {v19.8H, v20.8H, v21.8H, v22.8H}, [x0], #64
 smlal2 v23.4S, v26.8H, v30.8H
 smlal2 v23.4S, v27.8H, v29.8H
 ld4 {v19.8H, v20.8H, v21.8H, v22.8H}, [x3], #64
 smull v15.4S, v25.4H, v31.4H
 smlal v15.4S, v26.4H, v30.4H
 smull v17.4S, v26.4H, v31.4H
 smlal v17.4S, v27.4H, v30.4H
 uzp1 v4.8H, v1.8H, v6.8H
 smlal v15.4S, v27.4H, v29.4H
 smull2 v10.4S, v26.8H, v31.8H
 smlal2 v10.4S, v27.8H, v30.8H
 smull2 v14.4S, v27.8H, v28.8H
 uzp1 v12.8H, v15.8H, v23.8H
 smull v13.4S, v27.4H, v28.4H
 smlal2 v14.4S, v24.8H, v31.8H
 smlal v13.4S, v24.4H, v31.4H
 smlal v13.4S, v25.4H, v30.4H
 uzp1 v31.8H, v17.8H, v10.8H
 mul v2.8H, v4.8H, v11.H[2]
 smlal2 v14.4S, v25.8H, v30.8H
 smlal v13.4S, v26.4H, v29.4H
 smlal2 v14.4S, v26.8H, v29.8H
 smlal v1.4S, v2.4H, v11.H[0]
 smlal2 v6.4S, v2.8H, v11.H[0]
 mul v5.8H, v31.8H, v11.H[2]
 uzp2 v27.8H, v1.8H, v6.8H
 smlal2 v10.4S, v5.8H, v11.H[0]
 smlal v17.4S, v5.4H, v11.H[0]
 smull v6.4S, v27.4H, v16.4H
 smull2 v3.4S, v27.8H, v16.8H
 smlal v6.4S, v24.4H, v30.4H
 uzp2 v1.8H, v17.8H, v10.8H
 smlal2 v3.4S, v24.8H, v30.8H
 smlal v6.4S, v25.4H, v29.4H
 mul v27.8H, v12.8H, v11.H[2]
 smlal2 v3.4S, v25.8H, v29.8H
 smlal v6.4S, v26.4H, v28.4H
 smull v4.4S, v1.4H, v16.4H
 smlal2 v23.4S, v27.8H, v11.H[0]
 smlal v15.4S, v27.4H, v11.H[0]
 smull2 v9.4S, v1.8H, v16.8H
 smlal2 v3.4S, v26.8H, v28.8H
 smlal v4.4S, v24.4H, v29.4H
 smlal2 v9.4S, v24.8H, v29.8H
 smlal v4.4S, v25.4H, v28.4H
 uzp2 v5.8H, v15.8H, v23.8H
 smlal2 v9.4S, v25.8H, v28.8H
 smull v31.4S, v5.4H, v16.4H
 smlal v31.4S, v24.4H, v28.4H
 smull2 v10.4S, v5.8H, v16.8H
 smlal2 v10.4S, v24.8H, v28.8H
 saddw v31.4S, v31.4S, v19.4H
 saddw2 v10.4S, v10.4S, v19.8H
 uzp1 v19.8H, v31.8H, v10.8H
 saddw v4.4S, v4.4S, v20.4H
 sqrdmulh v31.4S, v31.4S, v11.S[2]
 saddw2 v9.4S, v9.4S, v20.8H
 sqrdmulh v10.4S, v10.4S, v11.S[2]
 uzp1 v31.8H, v31.8H, v10.8H
 mls v19.8H, v31.8H, v11.H[0]
 saddw v6.4S, v6.4S, v21.4H
 uzp1 v20.8H, v4.8H, v9.8H
 sqrdmulh v4.4S, v4.4S, v11.S[2]
 sqrdmulh v9.4S, v9.4S, v11.S[2]
 saddw2 v3.4S, v3.4S, v21.8H
 uzp1 v4.8H, v4.8H, v9.8H
 uzp1 v21.8H, v6.8H, v3.8H
 sqrdmulh v6.4S, v6.4S, v11.S[2]
 saddw2 v14.4S, v14.4S, v22.8H
 mls v20.8H, v4.8H, v11.H[0]
 saddw v13.4S, v13.4S, v22.4H
 sqrdmulh v3.4S, v3.4S, v11.S[2]
 uzp1 v22.8H, v13.8H, v14.8H
 uzp1 v6.8H, v6.8H, v3.8H
 sqrdmulh v14.4S, v14.4S, v11.S[2]
 sqrdmulh v13.4S, v13.4S, v11.S[2]
 mls v21.8H, v6.8H, v11.H[0]
 uzp1 v13.8H, v13.8H, v14.8H
 mls v22.8H, v13.8H, v11.H[0]
 st4 {v19.8H, v20.8H, v21.8H, v22.8H}, [x0], #64

 subs x6, x6, #2
 b.ne module_encap_muladd_Lpoly_basemul_add_loop

 ldp d14, d15, [sp, #48]
 ldp d12, d13, [sp, #32]
 ldp d10, d11, [sp, #16]
 ldp d8, d9, [sp, #0]
 add sp, sp, #64
 ret

.align 4
module_encap_muladd_Lpoly_basemul_add_consts:
 /* h[0]=q, h[2]=Montgomery qinv constant, s[2]=C32, s[0]=Q32. */
 .hword 0x0d81, 0x0000, 0xcd7f, 0xff6d
 .hword 0x7a8f, 0x0009, 0x0000, 0x0363

/* End section: encap_muladd.S */



/* Section: decap_packed64.S; private namespace module_decap_packed64_ */
#ifdef __APPLE__
.text
#else
.section .text.module_decap_packed64_body,"ax",%progbits
#endif
/*
 * GT Production checked packed ct/f consumer.
 *
 * int poly_frombytes_basemul_decap_scale(
 *     int16_t out[768], int16_t decoded_ct[768],
 *     const uint8_t packed_ct[1152], const uint8_t packed_f[1152]);
 *
 * One fixed trip decodes 64 canonical coefficients from each operand into the
 * Decap 8x8-transposed layout and executes two consecutive scaled basemul
 * groups.  decoded_ct is retained for re-encryption.  packed_f is never
 * materialized: its second group stays live in v24-v27 while the first group
 * is consumed.
 */
#ifdef __APPLE__
.text
#else
.section .text.module_decap_packed64_body,"ax",%progbits
#endif
.p2align 4

#ifdef __APPLE__
#define C_SYM_1(sym) _##sym
#define C_SYM(sym) C_SYM_1(sym)
#else
#define C_SYM(sym) sym
#endif

.global C_SYM(poly_frombytes_basemul_decap_scale)
#ifndef __APPLE__
.type C_SYM(poly_frombytes_basemul_decap_scale), %function
#endif

/*
 * Decode one 96-byte / 64-coefficient canonical block.
 *
 * Persistent registers:
 *   v0  = Decap basemul Montgomery constants
 *   v29 = running maximum for canonical validation
 *   v31 = 0x0fff mask
 *
 * Output:
 *   v8-v11 and v<h0>-v<h3> = two consecutive Decap basemul groups.
 *   t0-t3 are scratch registers used only by validation.
 */
.macro module_decap_packed64_W22_DECODE64 src, h0, h1, h2, h3, t0, t1, t2, t3
    ld1 {v1.8h-v3.8h}, [\src], #48
    ld1 {v4.8h-v6.8h}, [\src], #48

    trn1 v7.2d,  v1.2d, v4.2d
    trn2 v8.2d,  v1.2d, v4.2d
    trn1 v9.2d,  v2.2d, v5.2d
    trn2 v10.2d, v2.2d, v5.2d
    trn1 v11.2d, v3.2d, v6.2d
    trn2 v12.2d, v3.2d, v6.2d

    trn1 v13.4s, v7.4s, v10.4s
    trn2 v14.4s, v7.4s, v10.4s
    trn1 v15.4s, v8.4s, v11.4s
    trn2 v16.4s, v8.4s, v11.4s
    trn1 v17.4s, v9.4s, v12.4s
    trn2 v18.4s, v9.4s, v12.4s

    trn1 v19.8h, v13.8h, v16.8h
    trn2 v20.8h, v13.8h, v16.8h
    trn1 v21.8h, v14.8h, v17.8h
    trn2 v22.8h, v14.8h, v17.8h
    trn1 v23.8h, v15.8h, v18.8h
    trn2 v24.8h, v15.8h, v18.8h

    ushr v25.8h, v19.8h, #12
    sli  v25.8h, v20.8h, #4
    ushr v27.8h, v20.8h, #8
    sli  v27.8h, v21.8h, #8
    ushr v11.8h, v21.8h, #4

    ushr v30.8h, v22.8h, #12
    sli  v30.8h, v23.8h, #4
    ushr v1.8h,  v23.8h, #8
    sli  v1.8h,  v24.8h, #8
    and v8.16b,  v19.16b, v31.16b
    and v9.16b,  v25.16b, v31.16b
    and v10.16b, v27.16b, v31.16b
    ushr v\h3\().8h, v24.8h, #4
    and v\h0\().16b, v22.16b, v31.16b
    and v\h1\().16b, v30.16b, v31.16b
    and v\h2\().16b, v1.16b,  v31.16b

    umax v\t0\().8h, v8.8h, v9.8h
    umax v\t1\().8h, v10.8h, v11.8h
    umax v\t2\().8h, v\h0\().8h, v\h1\().8h
    umax v\t3\().8h, v\h2\().8h, v\h3\().8h
    umax v\t0\().8h, v\t0\().8h, v\t1\().8h
    umax v\t2\().8h, v\t2\().8h, v\t3\().8h
    umax v\t0\().8h, v\t0\().8h, v\t2\().8h
    umax v29.8h, v29.8h, v\t0\().8h
.endm

/*
 * Exact Decap poly_basemul_scale arithmetic for one 32-coefficient group.
 * v24-v27 are deliberately not used as temporaries so that the next f group
 * may remain live across the first invocation.  v2 replaces Decap's v29
 * temporary because v29 owns the validation maximum.
 */
.macro module_decap_packed64_W22_BASEMUL_SCALE a0, a1, a2, a3, b0, b1, b2, b3
    smull   v12.4s, v\a1\().4h, v\b3\().4h
    smull2  v13.4s, v\a1\().8h, v\b3\().8h
    smull   v14.4s, v\a2\().4h, v\b3\().4h
    smull2  v15.4s, v\a2\().8h, v\b3\().8h
    smull   v16.4s, v\a3\().4h, v\b3\().4h
    smull2  v17.4s, v\a3\().8h, v\b3\().8h

    smlal   v12.4s, v\a2\().4h, v\b2\().4h
    smlal2  v13.4s, v\a2\().8h, v\b2\().8h
    smlal   v14.4s, v\a3\().4h, v\b2\().4h
    smlal2  v15.4s, v\a3\().8h, v\b2\().8h
    smlal   v12.4s, v\a3\().4h, v\b1\().4h
    smlal2  v13.4s, v\a3\().8h, v\b1\().8h

    uzp1    v20.8h, v16.8h, v17.8h
    uzp1    v19.8h, v14.8h, v15.8h
    uzp1    v18.8h, v12.8h, v13.8h
    mul     v20.8h, v20.8h, v0.h[2]
    mul     v19.8h, v19.8h, v0.h[2]
    mul     v18.8h, v18.8h, v0.h[2]
    smlal   v16.4s, v20.4h, v0.h[0]
    smlal2  v17.4s, v20.8h, v0.h[0]
    smlal   v14.4s, v19.4h, v0.h[0]
    smlal2  v15.4s, v19.8h, v0.h[0]
    smlal   v12.4s, v18.4h, v0.h[0]
    smlal2  v13.4s, v18.8h, v0.h[0]

    uzp2    v30.8h, v16.8h, v17.8h
    uzp2    v2.8h,  v14.8h, v15.8h
    uzp2    v28.8h, v12.8h, v13.8h

    smull   v18.4s, v\a3\().4h, v\b0\().4h
    smull2  v19.4s, v\a3\().8h, v\b0\().8h
    smull   v16.4s, v30.4h, v1.4h
    smull2  v17.4s, v30.8h, v1.8h
    smull   v14.4s, v2.4h,  v1.4h
    smull2  v15.4s, v2.8h,  v1.8h
    smull   v12.4s, v28.4h, v1.4h
    smull2  v13.4s, v28.8h, v1.8h

    smlal   v18.4s, v\a0\().4h, v\b3\().4h
    smlal2  v19.4s, v\a0\().8h, v\b3\().8h
    smlal   v16.4s, v\a0\().4h, v\b2\().4h
    smlal2  v17.4s, v\a0\().8h, v\b2\().8h
    smlal   v14.4s, v\a0\().4h, v\b1\().4h
    smlal2  v15.4s, v\a0\().8h, v\b1\().8h
    smlal   v12.4s, v\a0\().4h, v\b0\().4h
    smlal2  v13.4s, v\a0\().8h, v\b0\().8h

    smlal   v18.4s, v\a1\().4h, v\b2\().4h
    smlal2  v19.4s, v\a1\().8h, v\b2\().8h
    smlal   v16.4s, v\a1\().4h, v\b1\().4h
    smlal2  v17.4s, v\a1\().8h, v\b1\().8h
    smlal   v14.4s, v\a1\().4h, v\b0\().4h
    smlal2  v15.4s, v\a1\().8h, v\b0\().8h
    smlal   v18.4s, v\a2\().4h, v\b1\().4h
    smlal2  v19.4s, v\a2\().8h, v\b1\().8h
    smlal   v16.4s, v\a2\().4h, v\b0\().4h
    smlal2  v17.4s, v\a2\().8h, v\b0\().8h

    uzp1    v23.8h, v18.8h, v19.8h
    uzp1    v22.8h, v16.8h, v17.8h
    uzp1    v21.8h, v14.8h, v15.8h
    uzp1    v20.8h, v12.8h, v13.8h
    mul     v23.8h, v23.8h, v0.h[2]
    mul     v22.8h, v22.8h, v0.h[2]
    mul     v21.8h, v21.8h, v0.h[2]
    mul     v20.8h, v20.8h, v0.h[2]
    smlal   v18.4s, v23.4h, v0.h[0]
    smlal   v16.4s, v22.4h, v0.h[0]
    smlal   v14.4s, v21.4h, v0.h[0]
    smlal   v12.4s, v20.4h, v0.h[0]
    smlal2  v19.4s, v23.8h, v0.h[0]
    smlal2  v17.4s, v22.8h, v0.h[0]
    smlal2  v15.4s, v21.8h, v0.h[0]
    smlal2  v13.4s, v20.8h, v0.h[0]

    uzp2    v7.8h, v18.8h, v19.8h
    uzp2    v6.8h, v16.8h, v17.8h
    uzp2    v5.8h, v14.8h, v15.8h
    uzp2    v4.8h, v12.8h, v13.8h
.endm

C_SYM(poly_frombytes_basemul_decap_scale):
    stp d8,  d9,  [sp, #-64]!
    stp d10, d11, [sp, #16]
    stp d12, d13, [sp, #32]
    stp d14, d15, [sp, #48]

    adr x4, module_decap_packed64_.Lgt_decap_zetas_mul
    ld1 {v0.8h}, [x4], #16
    adr x5, module_decap_packed64_.Lgt_decap_mask_0fff
    ldr q31, [x5]
    movi v29.16b, #0
    mov x8, #1536

.p2align 4
module_decap_packed64_.Lgt_decap_checked_ct_f_basemul_scale64_loop64:
    /* A76 Slothy rename schedule promoted after full-path validation. */
        ld1 {v1.8H, v2.8H, v3.8H}, [x2], #48
        ld1 {v4.8H, v5.8H, v6.8H}, [x2], #48
        trn1 v25.2D, v1.2D, v4.2D
        trn2 v20.2D, v1.2D, v4.2D
        trn2 v9.2D, v2.2D, v5.2D
        trn1 v8.2D, v2.2D, v5.2D
        trn1 v15.2D, v3.2D, v6.2D
        trn2 v18.2D, v3.2D, v6.2D
        trn1 v12.4S, v25.4S, v9.4S
        trn2 v1.4S, v25.4S, v9.4S
        trn1 v9.4S, v20.4S, v15.4S
        trn2 v3.4S, v20.4S, v15.4S
        trn1 v15.4S, v8.4S, v18.4S
        trn2 v18.4S, v8.4S, v18.4S
        trn1 v8.8H, v12.8H, v3.8H
        trn2 v12.8H, v12.8H, v3.8H
        trn1 v3.8H, v1.8H, v15.8H
        trn2 v1.8H, v1.8H, v15.8H
        trn1 v15.8H, v9.8H, v18.8H
        trn2 v9.8H, v9.8H, v18.8H
        ushr v18.8H, v8.8H, #12
        and v22.16B, v8.16B, v31.16B
        ushr v25.8H, v3.8H, #4
        and v6.16B, v1.16B, v31.16B
        sli v18.8H, v12.8H, #4
        mov x6, x1
        ushr v12.8H, v12.8H, #8
        and v23.16B, v18.16B, v31.16B
        sli v12.8H, v3.8H, #8
        ushr v3.8H, v1.8H, #12
        umax v18.8H, v22.8H, v23.8H
        and v24.16B, v12.16B, v31.16B
        sli v3.8H, v15.8H, #4
        ushr v15.8H, v15.8H, #8
        and v7.16B, v3.16B, v31.16B
        sli v15.8H, v9.8H, #8
        ushr v9.8H, v9.8H, #4
        and v8.16B, v15.16B, v31.16B
        umax v3.8H, v24.8H, v25.8H
        umax v12.8H, v6.8H, v7.8H
        umax v15.8H, v8.8H, v9.8H
        st1 {v22.8H, v23.8H, v24.8H, v25.8H}, [x1], #64
        umax v3.8H, v18.8H, v3.8H
        umax v15.8H, v12.8H, v15.8H
        umax v15.8H, v3.8H, v15.8H
        ld1 {v1.8H, v2.8H, v3.8H}, [x3], #48
        umax v29.8H, v29.8H, v15.8H
        st1 {v6.8H, v7.8H, v8.8H, v9.8H}, [x1], #64
        ld1 {v4.8H, v5.8H, v6.8H}, [x3], #48
        trn1 v25.2D, v1.2D, v4.2D
        trn2 v20.2D, v1.2D, v4.2D
        trn1 v15.2D, v3.2D, v6.2D
        trn1 v8.2D, v2.2D, v5.2D
        trn2 v18.2D, v3.2D, v6.2D
        trn2 v9.2D, v2.2D, v5.2D
        trn2 v3.4S, v20.4S, v15.4S
        trn1 v12.4S, v25.4S, v9.4S
        trn2 v1.4S, v25.4S, v9.4S
        trn1 v9.4S, v20.4S, v15.4S
        trn1 v15.4S, v8.4S, v18.4S
        trn2 v18.4S, v8.4S, v18.4S
        trn1 v8.8H, v12.8H, v3.8H
        trn2 v12.8H, v12.8H, v3.8H
        trn1 v3.8H, v1.8H, v15.8H
        trn2 v1.8H, v1.8H, v15.8H
        trn1 v15.8H, v9.8H, v18.8H
        trn2 v9.8H, v9.8H, v18.8H
        ushr v18.8H, v8.8H, #12
        and v26.16B, v1.16B, v31.16B
        and v17.16B, v8.16B, v31.16B
        ushr v19.8H, v3.8H, #4
        sli v18.8H, v12.8H, #4
        ushr v12.8H, v12.8H, #8
        and v22.16B, v18.16B, v31.16B
        sli v12.8H, v3.8H, #8
        ld1 {v4.8H, v5.8H, v6.8H, v7.8H}, [x6], #64
        ushr v3.8H, v1.8H, #12
        and v30.16B, v12.16B, v31.16B
        umax v18.8H, v17.8H, v22.8H
        ld1 {v16.8H}, [x4], #16
        sli v3.8H, v15.8H, #4
        ushr v15.8H, v15.8H, #8
        and v27.16B, v3.16B, v31.16B
        ushr v10.8H, v9.8H, #4
        sli v15.8H, v9.8H, #8
        and v23.16B, v15.16B, v31.16B
        smull2 v1.4S, v6.8H, v19.8H
        smlal2 v1.4S, v7.8H, v30.8H
        umax v3.8H, v30.8H, v19.8H
        smull v8.4S, v6.4H, v19.4H
        umax v15.8H, v23.8H, v10.8H
        umax v3.8H, v18.8H, v3.8H
        smull v9.4S, v7.4H, v19.4H
        smlal v8.4S, v7.4H, v30.4H
        umax v12.8H, v26.8H, v27.8H
        smull2 v18.4S, v7.8H, v19.8H
        umax v15.8H, v12.8H, v15.8H
        umax v15.8H, v3.8H, v15.8H
        smull2 v20.4S, v5.8H, v19.8H
        smlal2 v20.4S, v6.8H, v30.8H
        uzp1 v3.8H, v8.8H, v1.8H
        umax v29.8H, v29.8H, v15.8H
        smull v25.4S, v5.4H, v19.4H
        mul v3.8H, v3.8H, v0.H[2]
        uzp1 v12.8H, v9.8H, v18.8H
        smlal2 v20.4S, v7.8H, v22.8H
        smlal v25.4S, v6.4H, v30.4H
        smlal v25.4S, v7.4H, v22.4H
        smlal2 v1.4S, v3.8H, v0.H[0]
        smlal v8.4S, v3.4H, v0.H[0]
        uzp1 v15.8H, v25.8H, v20.8H
        mul v12.8H, v12.8H, v0.H[2]
        mul v15.8H, v15.8H, v0.H[2]
        uzp2 v3.8H, v8.8H, v1.8H
        smull v21.4S, v7.4H, v17.4H
        smlal v9.4S, v12.4H, v0.H[0]
        smlal2 v18.4S, v12.8H, v0.H[0]
        smlal2 v20.4S, v15.8H, v0.H[0]
        smlal v25.4S, v15.4H, v0.H[0]
        smull2 v11.4S, v7.8H, v17.8H
        uzp2 v12.8H, v9.8H, v18.8H
        smlal2 v11.4S, v4.8H, v19.8H
        uzp2 v15.8H, v25.8H, v20.8H
        smull v20.4S, v3.4H, v16.4H
        smull2 v8.4S, v3.8H, v16.8H
        smlal v21.4S, v4.4H, v19.4H
        smull2 v25.4S, v12.8H, v16.8H
        smull v2.4S, v12.4H, v16.4H
        smlal2 v11.4S, v5.8H, v30.8H
        smull v1.4S, v15.4H, v16.4H
        smull2 v9.4S, v15.8H, v16.8H
        smlal v20.4S, v4.4H, v22.4H
        smlal2 v8.4S, v4.8H, v22.8H
        smlal2 v25.4S, v4.8H, v30.8H
        smlal2 v8.4S, v5.8H, v17.8H
        smlal2 v9.4S, v4.8H, v17.8H
        smlal v21.4S, v5.4H, v30.4H
        smlal v1.4S, v4.4H, v17.4H
        smlal2 v11.4S, v6.8H, v22.8H
        smlal v2.4S, v4.4H, v30.4H
        smlal2 v25.4S, v5.8H, v22.8H
        smlal v21.4S, v6.4H, v22.4H
        uzp1 v15.8H, v1.8H, v9.8H
        smlal v2.4S, v5.4H, v22.4H
        smlal2 v25.4S, v6.8H, v17.8H
        smlal v2.4S, v6.4H, v17.4H
        smlal v20.4S, v5.4H, v17.4H
        ld1 {v4.8H, v5.8H, v6.8H, v7.8H}, [x6]
        uzp1 v12.8H, v2.8H, v25.8H
        mul v15.8H, v15.8H, v0.H[2]
        uzp1 v18.8H, v21.8H, v11.8H
        ld1 {v16.8H}, [x4], #16
        mul v12.8H, v12.8H, v0.H[2]
        uzp1 v3.8H, v20.8H, v8.8H
        mul v18.8H, v18.8H, v0.H[2]
        smlal v1.4S, v15.4H, v0.H[0]
        smlal2 v25.4S, v12.8H, v0.H[0]
        smlal v2.4S, v12.4H, v0.H[0]
        uzp2 v14.8H, v2.8H, v25.8H
        smlal v21.4S, v18.4H, v0.H[0]
        smlal2 v11.4S, v18.8H, v0.H[0]
        smlal2 v9.4S, v15.8H, v0.H[0]
        mul v3.8H, v3.8H, v0.H[2]
        uzp2 v15.8H, v21.8H, v11.8H
        smull2 v18.4S, v7.8H, v10.8H
        uzp2 v12.8H, v1.8H, v9.8H
        smull v9.4S, v7.4H, v10.4H
        smull v25.4S, v5.4H, v10.4H
        smlal v20.4S, v3.4H, v0.H[0]
        smlal2 v8.4S, v3.8H, v0.H[0]
        uzp2 v13.8H, v20.8H, v8.8H
        smlal v25.4S, v6.4H, v23.4H
        smull v8.4S, v6.4H, v10.4H
        smull2 v1.4S, v6.8H, v10.8H
        smlal2 v1.4S, v7.8H, v23.8H
        smlal v8.4S, v7.4H, v23.4H
        smlal v25.4S, v7.4H, v27.4H
        smull2 v20.4S, v5.8H, v10.8H
        smlal2 v20.4S, v6.8H, v23.8H
        smlal2 v20.4S, v7.8H, v27.8H
        uzp1 v3.8H, v8.8H, v1.8H
        st1 {v12.8H, v13.8H, v14.8H, v15.8H}, [x0], #64
        mul v3.8H, v3.8H, v0.H[2]
        uzp1 v15.8H, v25.8H, v20.8H
        uzp1 v12.8H, v9.8H, v18.8H
        mul v15.8H, v15.8H, v0.H[2]
        smull v21.4S, v7.4H, v26.4H
        smlal2 v1.4S, v3.8H, v0.H[0]
        smlal v8.4S, v3.4H, v0.H[0]
        smlal v25.4S, v15.4H, v0.H[0]
        smlal2 v20.4S, v15.8H, v0.H[0]
        mul v12.8H, v12.8H, v0.H[2]
        uzp2 v3.8H, v8.8H, v1.8H
        smlal v21.4S, v4.4H, v10.4H
        uzp2 v15.8H, v25.8H, v20.8H
        smull2 v8.4S, v3.8H, v16.8H
        smull v20.4S, v3.4H, v16.4H
        smlal v9.4S, v12.4H, v0.H[0]
        smlal2 v18.4S, v12.8H, v0.H[0]
        smlal v21.4S, v5.4H, v23.4H
        smlal2 v8.4S, v4.8H, v27.8H
        smlal v20.4S, v4.4H, v27.4H
        uzp2 v12.8H, v9.8H, v18.8H
        smull2 v11.4S, v7.8H, v26.8H
        smlal2 v11.4S, v4.8H, v10.8H
        smull v2.4S, v12.4H, v16.4H
        smull2 v25.4S, v12.8H, v16.8H
        smlal v21.4S, v6.4H, v27.4H
        smlal2 v25.4S, v4.8H, v23.8H
        smlal2 v11.4S, v5.8H, v23.8H
        smlal v2.4S, v4.4H, v23.4H
        smull2 v9.4S, v15.8H, v16.8H
        smull v1.4S, v15.4H, v16.4H
        smlal2 v8.4S, v5.8H, v26.8H
        smlal v20.4S, v5.4H, v26.4H
        smlal2 v11.4S, v6.8H, v27.8H
        smlal2 v25.4S, v5.8H, v27.8H
        smlal v2.4S, v5.4H, v27.4H
        smlal v2.4S, v6.4H, v26.4H
        smlal2 v25.4S, v6.8H, v26.8H
        uzp1 v18.8H, v21.8H, v11.8H
        smlal v1.4S, v4.4H, v26.4H
        smlal2 v9.4S, v4.8H, v26.8H
        mul v18.8H, v18.8H, v0.H[2]
        uzp1 v3.8H, v20.8H, v8.8H
        uzp1 v12.8H, v2.8H, v25.8H
        mul v3.8H, v3.8H, v0.H[2]
        uzp1 v15.8H, v1.8H, v9.8H
        mul v12.8H, v12.8H, v0.H[2]
        smlal v21.4S, v18.4H, v0.H[0]
        smlal2 v8.4S, v3.8H, v0.H[0]
        smlal v20.4S, v3.4H, v0.H[0]
        mul v15.8H, v15.8H, v0.H[2]
        smlal2 v11.4S, v18.8H, v0.H[0]
        smlal v2.4S, v12.4H, v0.H[0]
        uzp2 v13.8H, v20.8H, v8.8H
        smlal2 v25.4S, v12.8H, v0.H[0]
        smlal v1.4S, v15.4H, v0.H[0]
        smlal2 v9.4S, v15.8H, v0.H[0]
        uzp2 v15.8H, v21.8H, v11.8H
        uzp2 v14.8H, v2.8H, v25.8H
        uzp2 v12.8H, v1.8H, v9.8H
        st1 {v12.8H, v13.8H, v14.8H, v15.8H}, [x0], #64

    subs x8, x8, #128
    b.ne module_decap_packed64_.Lgt_decap_checked_ct_f_basemul_scale64_loop64

    umaxv h29, v29.8h
    umov w9, v29.h[0]
    cmp w9, #3457
    cset w0, hs

    ldp d10, d11, [sp, #16]
    ldp d12, d13, [sp, #32]
    ldp d14, d15, [sp, #48]
    ldp d8,  d9,  [sp]
    add sp, sp, #64
    ret

#ifndef __APPLE__
.size C_SYM(poly_frombytes_basemul_decap_scale), \
      .-C_SYM(poly_frombytes_basemul_decap_scale)
#endif

.p2align 4
module_decap_packed64_.Lgt_decap_zetas_mul:
    .hword 0x0d81, 0x4bd4, 0xcd7f, 0xff6d, 0xfa8f, 0xf9dd, 0xc5d5, 0x0000
    .hword 0x00df, 0x0472, 0xfbdd, 0xfe73, 0xff49, 0x0677, 0x022f, 0xf976
    .hword 0xff21, 0xfb8e, 0x0423, 0x018d, 0x00b7, 0xf989, 0xfdd1, 0x068a
    .hword 0x0115, 0x03a5, 0x06bb, 0x01b5, 0xfa16, 0x00f2, 0x0668, 0x01b0
    .hword 0xfeeb, 0xfc5b, 0xf945, 0xfe4b, 0x05ea, 0xff0e, 0xf998, 0xfe50
    .hword 0xf9d1, 0x02b8, 0x0306, 0x0687, 0x039f, 0x0202, 0x0200, 0x01e9
    .hword 0x062f, 0xfd48, 0xfcfa, 0xf979, 0xfc61, 0xfdfe, 0xfe00, 0xfe17
    .hword 0x0129, 0x0259, 0x05c1, 0x046a, 0x052a, 0x0367, 0x02f8, 0x04bc
    .hword 0xfed7, 0xfda7, 0xfa3f, 0xfb96, 0xfad6, 0xfc99, 0xfd08, 0xfb44
    .hword 0xfec8, 0xfea0, 0x01bb, 0x03af, 0x0008, 0x04e2, 0xff9c, 0x067c
    .hword 0x0138, 0x0160, 0xfe45, 0xfc51, 0xfff8, 0xfb1e, 0x0064, 0xf984
    .hword 0xffe1, 0x04b6, 0xfac3, 0xfb21, 0x01bc, 0x00eb, 0x0554, 0xfb47
    .hword 0x001f, 0xfb4a, 0x053d, 0x04df, 0xfe44, 0xff15, 0xfaac, 0x04b9
    .hword 0x0169, 0x00e6, 0x02a1, 0x0246, 0x0581, 0x05dd, 0x0579, 0x00fb
    .hword 0xfe97, 0xff1a, 0xfd5f, 0xfdba, 0xfa7f, 0xfa23, 0xfa87, 0xff05
    .hword 0x03fe, 0xfbd9, 0x041d, 0x04a4, 0x01a1, 0xfa91, 0xffe5, 0xf9a6
    .hword 0xfc02, 0x0427, 0xfbe3, 0xfb5c, 0xfe5f, 0x056f, 0x001b, 0x065a
    .hword 0x0695, 0xfec5, 0x0580, 0xfb20, 0x0190, 0x0112, 0xf9f9, 0x0020
    .hword 0xf96b, 0x013b, 0xfa80, 0x04e0, 0xfe70, 0xfeee, 0x0607, 0xffe0
    .hword 0xf9f2, 0x05fb, 0xfaa9, 0xff84, 0x05b2, 0x0563, 0xfc54, 0xf96f
    .hword 0x060e, 0xfa05, 0x0557, 0x007c, 0xfa4e, 0xfa9d, 0x03ac, 0x0691
    .hword 0x0016, 0x06ad, 0xfeed, 0x0454, 0x0162, 0xf940, 0xfc38, 0x035a
    .hword 0xffea, 0xf953, 0x0113, 0xfbac, 0xfe9e, 0x06c0, 0x03c8, 0xfca6
    .hword 0x04c5, 0xff26, 0x0126, 0xfd24, 0xfbb9, 0x037c, 0x0634, 0xfcf5
    .hword 0xfb3b, 0x00da, 0xfeda, 0x02dc, 0x0447, 0xfc84, 0xf9cc, 0x030b

.p2align 4
module_decap_packed64_.Lgt_decap_mask_0fff:
    .hword 0x0fff, 0x0fff, 0x0fff, 0x0fff
    .hword 0x0fff, 0x0fff, 0x0fff, 0x0fff

#undef C_SYM
#ifdef __APPLE__
#undef C_SYM_1
#endif

/* End section: decap_packed64.S */

/* Section: decap_base.S; private namespace module_decap_base_ */
#ifdef __APPLE__
.text
#else
.section .text.module_decap_base_body,"ax",%progbits
#endif
/*************************************************
* Name:        poly_basemul_decap
*
* Description: Multiplication of two polynomials in the NTT domain.
*
* Arguments:   - poly *r:       pointer to the output polynomial
*              - const poly *a: pointer to the first input polynomial;
*                               coefficients must lie in (-2q,2q)
*              - const poly *b: pointer to the second input polynomial;
*                               coefficients must lie in (-2q,2q)
*
* Returns:     none. Output coefficients lie in (-3q/2,3q/2) and are
*              reduced by poly_tobytes_decap before serialization.
**************************************************/
#ifdef __APPLE__
.section __TEXT,__text,regular,pure_instructions
#else
.section .text.gt_decap_poly_basemul,"ax",%progbits
#endif

.global poly_basemul_decap
.global _poly_basemul_decap
poly_basemul_decap:
_poly_basemul_decap:
    stp d8,  d9,  [sp, #-64]!
    stp d10, d11, [sp, #16]
    stp d12, d13, [sp, #32]
    stp d14, d15, [sp, #48]

    module_decap_base_dst       .req x0
    module_decap_base_src1      .req x1
    module_decap_base_src2      .req x2
    module_decap_base_zetas_ptr .req x3
    module_decap_base_counter   .req x8

    adr module_decap_base_zetas_ptr, module_decap_base_zetas_mul

    #load
    ld1  {v0.8h}, [module_decap_base_zetas_ptr], #16
    adr x9, module_decap_base_.Ldecap_basemul_q31_consts
    ldr q24, [x9]

    mov module_decap_base_counter, #1536

module_decap_base__looptop:
    #load
    ld1  {v1.8h}, [module_decap_base_zetas_ptr], #16

    #load
    ld1 {v4.8h - v7.8h}, [module_decap_base_src1], #64
    ld1 {v8.8h - v11.8h}, [module_decap_base_src2], #64

    smull   v12.4s, v5.4h, v11.4h //a1*b3
    smull2  v13.4s, v5.8h, v11.8h //a1*b3
    smull   v14.4s, v6.4h, v11.4h //a2*b3
    smull2  v15.4s, v6.8h, v11.8h //a2*b3
    smull   v16.4s, v7.4h, v11.4h //a3*b3
    smull2  v17.4s, v7.8h, v11.8h //a3*b3

    smlal   v12.4s, v6.4h, v10.4h //a2*b2
    smlal2  v13.4s, v6.8h, v10.8h //a2*b2
    smlal   v14.4s, v7.4h, v10.4h //a3*b2
    smlal2  v15.4s, v7.8h, v10.8h //a3*b2

    smlal   v12.4s, v7.4h, v9.4h //a3*b1
    smlal2  v13.4s, v7.8h, v9.8h //a3*b1

    uzp1    v20.8h, v16.8h, v17.8h
    uzp1    v19.8h, v14.8h, v15.8h
    uzp1    v18.8h, v12.8h, v13.8h

    mul     v20.8h, v20.8h, v0.h[2]
    mul     v19.8h, v19.8h, v0.h[2]
    mul     v18.8h, v18.8h, v0.h[2]

    smlal   v16.4s, v20.4h, v0.h[0]
    smlal2  v17.4s, v20.8h, v0.h[0]
    smlal   v14.4s, v19.4h, v0.h[0]
    smlal2  v15.4s, v19.8h, v0.h[0]
    smlal   v12.4s, v18.4h, v0.h[0]
    smlal2  v13.4s, v18.8h, v0.h[0]

    uzp2    v30.8h, v16.8h, v17.8h
    uzp2    v29.8h, v14.8h, v15.8h
    uzp2    v28.8h, v12.8h, v13.8h

    smull   v18.4s, v7.4h, v8.4h //a3*b0
    smull2  v19.4s, v7.8h, v8.8h //a3*b0
    smull   v16.4s, v30.4h, v1.4h //r[2]*zeta
    smull2  v17.4s, v30.8h, v1.8h //r[2]*zeta
    smull   v14.4s, v29.4h, v1.4h //r[1]*zeta
    smull2  v15.4s, v29.8h, v1.8h //r[1]*zeta
    smull   v12.4s, v28.4h, v1.4h //r[0]*zeta
    smull2  v13.4s, v28.8h, v1.8h //r[0]*zeta

    smlal   v18.4s, v4.4h,  v11.4h //a0*b3
    smlal2  v19.4s, v4.8h,  v11.8h //a0*b3
    smlal   v16.4s, v4.4h, v10.4h //a0*b2
    smlal2  v17.4s, v4.8h, v10.8h //a0*b2
    smlal   v14.4s, v4.4h, v9.4h //a0*b1
    smlal2  v15.4s, v4.8h, v9.8h //a0*b1
    smlal   v12.4s, v4.4h, v8.4h //a0*b0
    smlal2  v13.4s, v4.8h, v8.8h //a0*b0

    smlal   v18.4s, v5.4h, v10.4h //a1*b2
    smlal2  v19.4s, v5.8h, v10.8h //a1*b2
    smlal   v16.4s, v5.4h, v9.4h //a1*b1
    smlal2  v17.4s, v5.8h, v9.8h //a1*b1
    smlal   v14.4s, v5.4h, v8.4h //a1*b0
    smlal2  v15.4s, v5.8h, v8.8h //a1*b0

    smlal   v18.4s, v6.4h, v9.4h //a2*b1
    smlal2  v19.4s, v6.8h, v9.8h //a2*b1
    smlal   v16.4s, v6.4h, v8.4h //a2*b0
    smlal2  v17.4s, v6.8h, v8.8h //a2*b0

    /*
     * D1: v12/v13 through v18/v19 are the four normal-domain int32
     * accumulators.  Reduce them directly instead of taking the second
     * Montgomery reduction followed by multiplication back by R.
     * q24.s[0] = q = 3457; q24.s[2] = C = 621199.
     */
    sqrdmulh v4.4s, v12.4s, v24.s[2]
    sqrdmulh v5.4s, v13.4s, v24.s[2]
    sqrdmulh v6.4s, v14.4s, v24.s[2]
    sqrdmulh v7.4s, v15.4s, v24.s[2]
    mls v12.4s, v4.4s, v24.s[0]
    mls v13.4s, v5.4s, v24.s[0]
    mls v14.4s, v6.4s, v24.s[0]
    mls v15.4s, v7.4s, v24.s[0]
    xtn v8.4h, v12.4s
    xtn2 v8.8h, v13.4s
    xtn v9.4h, v14.4s
    xtn2 v9.8h, v15.4s

    sqrdmulh v4.4s, v16.4s, v24.s[2]
    sqrdmulh v5.4s, v17.4s, v24.s[2]
    sqrdmulh v6.4s, v18.4s, v24.s[2]
    sqrdmulh v7.4s, v19.4s, v24.s[2]
    mls v16.4s, v4.4s, v24.s[0]
    mls v17.4s, v5.4s, v24.s[0]
    mls v18.4s, v6.4s, v24.s[0]
    mls v19.4s, v7.4s, v24.s[0]
    xtn v10.4h, v16.4s
    xtn2 v10.8h, v17.4s
    xtn v11.4h, v18.4s
    xtn2 v11.8h, v19.4s

    #store
    st1 {v8.8h - v11.8h}, [module_decap_base_dst], #64

    subs module_decap_base_counter, module_decap_base_counter, #64
    b.ne module_decap_base__looptop

    .unreq    module_decap_base_dst
    .unreq    module_decap_base_src1
    .unreq    module_decap_base_src2
    .unreq    module_decap_base_zetas_ptr
    .unreq    module_decap_base_counter

    ldp d10, d11, [sp, #16]
    ldp d12, d13, [sp, #32]
    ldp d14, d15, [sp, #48]
    ldp d8,  d9,  [sp]
    add sp, sp, #64
    ret


#ifdef __APPLE__
.section __TEXT,__text,regular,pure_instructions
#else
.section .rodata.gt_decap_base,"a",%progbits
#endif
.align 4
module_decap_base_zetas_mul:
    .hword 0x0d81, 0x4bd4, 0xcd7f, 0xff6d, 0xfa8f, 0xf9dd, 0xc5d5, 0x0000
    .hword 0x00df, 0x0472, 0xfbdd, 0xfe73, 0xff49, 0x0677, 0x022f, 0xf976
    .hword 0xff21, 0xfb8e, 0x0423, 0x018d, 0x00b7, 0xf989, 0xfdd1, 0x068a
    .hword 0x0115, 0x03a5, 0x06bb, 0x01b5, 0xfa16, 0x00f2, 0x0668, 0x01b0
    .hword 0xfeeb, 0xfc5b, 0xf945, 0xfe4b, 0x05ea, 0xff0e, 0xf998, 0xfe50
    .hword 0xf9d1, 0x02b8, 0x0306, 0x0687, 0x039f, 0x0202, 0x0200, 0x01e9
    .hword 0x062f, 0xfd48, 0xfcfa, 0xf979, 0xfc61, 0xfdfe, 0xfe00, 0xfe17
    .hword 0x0129, 0x0259, 0x05c1, 0x046a, 0x052a, 0x0367, 0x02f8, 0x04bc
    .hword 0xfed7, 0xfda7, 0xfa3f, 0xfb96, 0xfad6, 0xfc99, 0xfd08, 0xfb44
    .hword 0xfec8, 0xfea0, 0x01bb, 0x03af, 0x0008, 0x04e2, 0xff9c, 0x067c
    .hword 0x0138, 0x0160, 0xfe45, 0xfc51, 0xfff8, 0xfb1e, 0x0064, 0xf984
    .hword 0xffe1, 0x04b6, 0xfac3, 0xfb21, 0x01bc, 0x00eb, 0x0554, 0xfb47
    .hword 0x001f, 0xfb4a, 0x053d, 0x04df, 0xfe44, 0xff15, 0xfaac, 0x04b9
    .hword 0x0169, 0x00e6, 0x02a1, 0x0246, 0x0581, 0x05dd, 0x0579, 0x00fb
    .hword 0xfe97, 0xff1a, 0xfd5f, 0xfdba, 0xfa7f, 0xfa23, 0xfa87, 0xff05
    .hword 0x03fe, 0xfbd9, 0x041d, 0x04a4, 0x01a1, 0xfa91, 0xffe5, 0xf9a6
    .hword 0xfc02, 0x0427, 0xfbe3, 0xfb5c, 0xfe5f, 0x056f, 0x001b, 0x065a
    .hword 0x0695, 0xfec5, 0x0580, 0xfb20, 0x0190, 0x0112, 0xf9f9, 0x0020
    .hword 0xf96b, 0x013b, 0xfa80, 0x04e0, 0xfe70, 0xfeee, 0x0607, 0xffe0
    .hword 0xf9f2, 0x05fb, 0xfaa9, 0xff84, 0x05b2, 0x0563, 0xfc54, 0xf96f
    .hword 0x060e, 0xfa05, 0x0557, 0x007c, 0xfa4e, 0xfa9d, 0x03ac, 0x0691
    .hword 0x0016, 0x06ad, 0xfeed, 0x0454, 0x0162, 0xf940, 0xfc38, 0x035a
    .hword 0xffea, 0xf953, 0x0113, 0xfbac, 0xfe9e, 0x06c0, 0x03c8, 0xfca6
    .hword 0x04c5, 0xff26, 0x0126, 0xfd24, 0xfbb9, 0x037c, 0x0634, 0xfcf5
    .hword 0xfb3b, 0x00da, 0xfeda, 0x02dc, 0x0447, 0xfc84, 0xf9cc, 0x030b

.align 4
module_decap_base_.Ldecap_basemul_q31_consts:
    .word 3457, 0, 621199, 0

/* End section: decap_base.S */
