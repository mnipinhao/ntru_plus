.text
.align 4
.global poly_basemul_rminus1_pair_slothy
.global _poly_basemul_rminus1_pair_slothy
poly_basemul_rminus1_pair_slothy:
_poly_basemul_rminus1_pair_slothy:
    sub sp, sp, #64
    stp d8, d9, [sp, #0]
    stp d10, d11, [sp, #16]
    stp d12, d13, [sp, #32]
    stp d14, d15, [sp, #48]
    adr x3, .Lrminus1_pair_consts
    ld1 {v0.8h}, [x3]
    adrp x4, gt_rowbitrev_lambda
    add x4, x4, :lo12:gt_rowbitrev_lambda
    mov x8, #12
.Lpoly_basemul_rminus1_pair_slothy_loop:
    // live-in: x0, x1, x2, x4, and fixed v0 constants
    // live-out: x0/x1/x2 +128, x4 +32, and two output groups
    // range: unchanged production raw R^-1 basemul contract
    // reserved physical registers: v0, x5-x30, and sp
    // ld4 outputs: Q<i0_a0>, Q<i0_a1>, Q<i0_a2>, Q<i0_a3>,
    // Q<i0_b0>, Q<i0_b1>, Q<i0_b2>, Q<i0_b3>, Q<i1_a0>,
    // Q<i1_a1>, Q<i1_a2>, Q<i1_a3>, Q<i1_b0>, Q<i1_b1>,
    // Q<i1_b2>, Q<i1_b3>.
rminus1_pair_slothy_start:
    ld1 {V<i0_lam>.8h}, [x4], #16
    ld4 {V<i0_a0>.8h, V<i0_a1>.8h, V<i0_a2>.8h, V<i0_a3>.8h}, [x1], #64
    ld4 {V<i0_b0>.8h, V<i0_b1>.8h, V<i0_b2>.8h, V<i0_b3>.8h}, [x2], #64
    smull  V<i0_w0_lo>.4s, V<i0_a1>.4h, V<i0_b3>.4h
    smull2 V<i0_w0_hi>.4s, V<i0_a1>.8h, V<i0_b3>.8h
    smull  V<i0_w1_lo>.4s, V<i0_a2>.4h, V<i0_b3>.4h
    smull2 V<i0_w1_hi>.4s, V<i0_a2>.8h, V<i0_b3>.8h
    smull  V<i0_w2_lo>.4s, V<i0_a3>.4h, V<i0_b3>.4h
    smull2 V<i0_w2_hi>.4s, V<i0_a3>.8h, V<i0_b3>.8h
    smlal  V<i0_w0_lo>.4s, V<i0_a2>.4h, V<i0_b2>.4h
    smlal2 V<i0_w0_hi>.4s, V<i0_a2>.8h, V<i0_b2>.8h
    smlal  V<i0_w1_lo>.4s, V<i0_a3>.4h, V<i0_b2>.4h
    smlal2 V<i0_w1_hi>.4s, V<i0_a3>.8h, V<i0_b2>.8h
    smlal  V<i0_w0_lo>.4s, V<i0_a3>.4h, V<i0_b1>.4h
    smlal2 V<i0_w0_hi>.4s, V<i0_a3>.8h, V<i0_b1>.8h
    uzp1 V<i0_w2_mlow>.8h, V<i0_w2_lo>.8h, V<i0_w2_hi>.8h
    uzp1 V<i0_w1_mlow>.8h, V<i0_w1_lo>.8h, V<i0_w1_hi>.8h
    uzp1 V<i0_w0_mlow>.8h, V<i0_w0_lo>.8h, V<i0_w0_hi>.8h
    mul V<i0_w2_m>.8h, V<i0_w2_mlow>.8h, v0.h[2]
    mul V<i0_w1_m>.8h, V<i0_w1_mlow>.8h, v0.h[2]
    mul V<i0_w0_m>.8h, V<i0_w0_mlow>.8h, v0.h[2]
    smlal  V<i0_w2_lo>.4s, V<i0_w2_m>.4h, v0.h[0]
    smlal2 V<i0_w2_hi>.4s, V<i0_w2_m>.8h, v0.h[0]
    smlal  V<i0_w1_lo>.4s, V<i0_w1_m>.4h, v0.h[0]
    smlal2 V<i0_w1_hi>.4s, V<i0_w1_m>.8h, v0.h[0]
    smlal  V<i0_w0_lo>.4s, V<i0_w0_m>.4h, v0.h[0]
    smlal2 V<i0_w0_hi>.4s, V<i0_w0_m>.8h, v0.h[0]
    uzp2 V<i0_w2_red>.8h, V<i0_w2_lo>.8h, V<i0_w2_hi>.8h
    uzp2 V<i0_w1_red>.8h, V<i0_w1_lo>.8h, V<i0_w1_hi>.8h
    uzp2 V<i0_w0_red>.8h, V<i0_w0_lo>.8h, V<i0_w0_hi>.8h
    smull  V<i0_r3_lo>.4s, V<i0_a3>.4h, V<i0_b0>.4h
    smull2 V<i0_r3_hi>.4s, V<i0_a3>.8h, V<i0_b0>.8h
    smull  V<i0_r2_lo>.4s, V<i0_w2_red>.4h, V<i0_lam>.4h
    smull2 V<i0_r2_hi>.4s, V<i0_w2_red>.8h, V<i0_lam>.8h
    smull  V<i0_r1_lo>.4s, V<i0_w1_red>.4h, V<i0_lam>.4h
    smull2 V<i0_r1_hi>.4s, V<i0_w1_red>.8h, V<i0_lam>.8h
    smull  V<i0_r0_lo>.4s, V<i0_w0_red>.4h, V<i0_lam>.4h
    smull2 V<i0_r0_hi>.4s, V<i0_w0_red>.8h, V<i0_lam>.8h
    smlal  V<i0_r3_lo>.4s, V<i0_a0>.4h, V<i0_b3>.4h
    smlal2 V<i0_r3_hi>.4s, V<i0_a0>.8h, V<i0_b3>.8h
    smlal  V<i0_r2_lo>.4s, V<i0_a0>.4h, V<i0_b2>.4h
    smlal2 V<i0_r2_hi>.4s, V<i0_a0>.8h, V<i0_b2>.8h
    smlal  V<i0_r1_lo>.4s, V<i0_a0>.4h, V<i0_b1>.4h
    smlal2 V<i0_r1_hi>.4s, V<i0_a0>.8h, V<i0_b1>.8h
    smlal  V<i0_r0_lo>.4s, V<i0_a0>.4h, V<i0_b0>.4h
    smlal2 V<i0_r0_hi>.4s, V<i0_a0>.8h, V<i0_b0>.8h
    smlal  V<i0_r3_lo>.4s, V<i0_a1>.4h, V<i0_b2>.4h
    smlal2 V<i0_r3_hi>.4s, V<i0_a1>.8h, V<i0_b2>.8h
    smlal  V<i0_r2_lo>.4s, V<i0_a1>.4h, V<i0_b1>.4h
    smlal2 V<i0_r2_hi>.4s, V<i0_a1>.8h, V<i0_b1>.8h
    smlal  V<i0_r1_lo>.4s, V<i0_a1>.4h, V<i0_b0>.4h
    smlal2 V<i0_r1_hi>.4s, V<i0_a1>.8h, V<i0_b0>.8h
    smlal  V<i0_r3_lo>.4s, V<i0_a2>.4h, V<i0_b1>.4h
    smlal2 V<i0_r3_hi>.4s, V<i0_a2>.8h, V<i0_b1>.8h
    smlal  V<i0_r2_lo>.4s, V<i0_a2>.4h, V<i0_b0>.4h
    smlal2 V<i0_r2_hi>.4s, V<i0_a2>.8h, V<i0_b0>.8h
    ld1 {V<i1_lam>.8h}, [x4], #16
    ld4 {V<i1_a0>.8h, V<i1_a1>.8h, V<i1_a2>.8h, V<i1_a3>.8h}, [x1], #64
    ld4 {V<i1_b0>.8h, V<i1_b1>.8h, V<i1_b2>.8h, V<i1_b3>.8h}, [x2], #64
    uzp1 V<i0_r0_mlow>.8h, V<i0_r0_lo>.8h, V<i0_r0_hi>.8h
    uzp1 V<i0_r1_mlow>.8h, V<i0_r1_lo>.8h, V<i0_r1_hi>.8h
    uzp1 V<i0_r2_mlow>.8h, V<i0_r2_lo>.8h, V<i0_r2_hi>.8h
    uzp1 V<i0_r3_mlow>.8h, V<i0_r3_lo>.8h, V<i0_r3_hi>.8h
    mul V<i0_r0_m>.8h, V<i0_r0_mlow>.8h, v0.h[2]
    mul V<i0_r1_m>.8h, V<i0_r1_mlow>.8h, v0.h[2]
    mul V<i0_r2_m>.8h, V<i0_r2_mlow>.8h, v0.h[2]
    mul V<i0_r3_m>.8h, V<i0_r3_mlow>.8h, v0.h[2]
    smlal  V<i0_r0_lo>.4s, V<i0_r0_m>.4h, v0.h[0]
    smlal2 V<i0_r0_hi>.4s, V<i0_r0_m>.8h, v0.h[0]
    smlal  V<i0_r1_lo>.4s, V<i0_r1_m>.4h, v0.h[0]
    smlal2 V<i0_r1_hi>.4s, V<i0_r1_m>.8h, v0.h[0]
    smlal  V<i0_r2_lo>.4s, V<i0_r2_m>.4h, v0.h[0]
    smlal2 V<i0_r2_hi>.4s, V<i0_r2_m>.8h, v0.h[0]
    smlal  V<i0_r3_lo>.4s, V<i0_r3_m>.4h, v0.h[0]
    smlal2 V<i0_r3_hi>.4s, V<i0_r3_m>.8h, v0.h[0]
    uzp2 V<i0_raw0>.8h, V<i0_r0_lo>.8h, V<i0_r0_hi>.8h
    uzp2 V<i0_raw1>.8h, V<i0_r1_lo>.8h, V<i0_r1_hi>.8h
    uzp2 V<i0_raw2>.8h, V<i0_r2_lo>.8h, V<i0_r2_hi>.8h
    uzp2 V<i0_raw3>.8h, V<i0_r3_lo>.8h, V<i0_r3_hi>.8h
    st4 {V<i0_raw0>.8h, V<i0_raw1>.8h, V<i0_raw2>.8h, V<i0_raw3>.8h}, [x0], #64
    smull  V<i1_w0_lo>.4s, V<i1_a1>.4h, V<i1_b3>.4h
    smull2 V<i1_w0_hi>.4s, V<i1_a1>.8h, V<i1_b3>.8h
    smull  V<i1_w1_lo>.4s, V<i1_a2>.4h, V<i1_b3>.4h
    smull2 V<i1_w1_hi>.4s, V<i1_a2>.8h, V<i1_b3>.8h
    smull  V<i1_w2_lo>.4s, V<i1_a3>.4h, V<i1_b3>.4h
    smull2 V<i1_w2_hi>.4s, V<i1_a3>.8h, V<i1_b3>.8h
    smlal  V<i1_w0_lo>.4s, V<i1_a2>.4h, V<i1_b2>.4h
    smlal2 V<i1_w0_hi>.4s, V<i1_a2>.8h, V<i1_b2>.8h
    smlal  V<i1_w1_lo>.4s, V<i1_a3>.4h, V<i1_b2>.4h
    smlal2 V<i1_w1_hi>.4s, V<i1_a3>.8h, V<i1_b2>.8h
    smlal  V<i1_w0_lo>.4s, V<i1_a3>.4h, V<i1_b1>.4h
    smlal2 V<i1_w0_hi>.4s, V<i1_a3>.8h, V<i1_b1>.8h
    uzp1 V<i1_w2_mlow>.8h, V<i1_w2_lo>.8h, V<i1_w2_hi>.8h
    uzp1 V<i1_w1_mlow>.8h, V<i1_w1_lo>.8h, V<i1_w1_hi>.8h
    uzp1 V<i1_w0_mlow>.8h, V<i1_w0_lo>.8h, V<i1_w0_hi>.8h
    mul V<i1_w2_m>.8h, V<i1_w2_mlow>.8h, v0.h[2]
    mul V<i1_w1_m>.8h, V<i1_w1_mlow>.8h, v0.h[2]
    mul V<i1_w0_m>.8h, V<i1_w0_mlow>.8h, v0.h[2]
    smlal  V<i1_w2_lo>.4s, V<i1_w2_m>.4h, v0.h[0]
    smlal2 V<i1_w2_hi>.4s, V<i1_w2_m>.8h, v0.h[0]
    smlal  V<i1_w1_lo>.4s, V<i1_w1_m>.4h, v0.h[0]
    smlal2 V<i1_w1_hi>.4s, V<i1_w1_m>.8h, v0.h[0]
    smlal  V<i1_w0_lo>.4s, V<i1_w0_m>.4h, v0.h[0]
    smlal2 V<i1_w0_hi>.4s, V<i1_w0_m>.8h, v0.h[0]
    uzp2 V<i1_w2_red>.8h, V<i1_w2_lo>.8h, V<i1_w2_hi>.8h
    uzp2 V<i1_w1_red>.8h, V<i1_w1_lo>.8h, V<i1_w1_hi>.8h
    uzp2 V<i1_w0_red>.8h, V<i1_w0_lo>.8h, V<i1_w0_hi>.8h
    smull  V<i1_r3_lo>.4s, V<i1_a3>.4h, V<i1_b0>.4h
    smull2 V<i1_r3_hi>.4s, V<i1_a3>.8h, V<i1_b0>.8h
    smull  V<i1_r2_lo>.4s, V<i1_w2_red>.4h, V<i1_lam>.4h
    smull2 V<i1_r2_hi>.4s, V<i1_w2_red>.8h, V<i1_lam>.8h
    smull  V<i1_r1_lo>.4s, V<i1_w1_red>.4h, V<i1_lam>.4h
    smull2 V<i1_r1_hi>.4s, V<i1_w1_red>.8h, V<i1_lam>.8h
    smull  V<i1_r0_lo>.4s, V<i1_w0_red>.4h, V<i1_lam>.4h
    smull2 V<i1_r0_hi>.4s, V<i1_w0_red>.8h, V<i1_lam>.8h
    smlal  V<i1_r3_lo>.4s, V<i1_a0>.4h, V<i1_b3>.4h
    smlal2 V<i1_r3_hi>.4s, V<i1_a0>.8h, V<i1_b3>.8h
    smlal  V<i1_r2_lo>.4s, V<i1_a0>.4h, V<i1_b2>.4h
    smlal2 V<i1_r2_hi>.4s, V<i1_a0>.8h, V<i1_b2>.8h
    smlal  V<i1_r1_lo>.4s, V<i1_a0>.4h, V<i1_b1>.4h
    smlal2 V<i1_r1_hi>.4s, V<i1_a0>.8h, V<i1_b1>.8h
    smlal  V<i1_r0_lo>.4s, V<i1_a0>.4h, V<i1_b0>.4h
    smlal2 V<i1_r0_hi>.4s, V<i1_a0>.8h, V<i1_b0>.8h
    smlal  V<i1_r3_lo>.4s, V<i1_a1>.4h, V<i1_b2>.4h
    smlal2 V<i1_r3_hi>.4s, V<i1_a1>.8h, V<i1_b2>.8h
    smlal  V<i1_r2_lo>.4s, V<i1_a1>.4h, V<i1_b1>.4h
    smlal2 V<i1_r2_hi>.4s, V<i1_a1>.8h, V<i1_b1>.8h
    smlal  V<i1_r1_lo>.4s, V<i1_a1>.4h, V<i1_b0>.4h
    smlal2 V<i1_r1_hi>.4s, V<i1_a1>.8h, V<i1_b0>.8h
    smlal  V<i1_r3_lo>.4s, V<i1_a2>.4h, V<i1_b1>.4h
    smlal2 V<i1_r3_hi>.4s, V<i1_a2>.8h, V<i1_b1>.8h
    smlal  V<i1_r2_lo>.4s, V<i1_a2>.4h, V<i1_b0>.4h
    smlal2 V<i1_r2_hi>.4s, V<i1_a2>.8h, V<i1_b0>.8h
    uzp1 V<i1_r0_mlow>.8h, V<i1_r0_lo>.8h, V<i1_r0_hi>.8h
    uzp1 V<i1_r1_mlow>.8h, V<i1_r1_lo>.8h, V<i1_r1_hi>.8h
    uzp1 V<i1_r2_mlow>.8h, V<i1_r2_lo>.8h, V<i1_r2_hi>.8h
    uzp1 V<i1_r3_mlow>.8h, V<i1_r3_lo>.8h, V<i1_r3_hi>.8h
    mul V<i1_r0_m>.8h, V<i1_r0_mlow>.8h, v0.h[2]
    mul V<i1_r1_m>.8h, V<i1_r1_mlow>.8h, v0.h[2]
    mul V<i1_r2_m>.8h, V<i1_r2_mlow>.8h, v0.h[2]
    mul V<i1_r3_m>.8h, V<i1_r3_mlow>.8h, v0.h[2]
    smlal  V<i1_r0_lo>.4s, V<i1_r0_m>.4h, v0.h[0]
    smlal2 V<i1_r0_hi>.4s, V<i1_r0_m>.8h, v0.h[0]
    smlal  V<i1_r1_lo>.4s, V<i1_r1_m>.4h, v0.h[0]
    smlal2 V<i1_r1_hi>.4s, V<i1_r1_m>.8h, v0.h[0]
    smlal  V<i1_r2_lo>.4s, V<i1_r2_m>.4h, v0.h[0]
    smlal2 V<i1_r2_hi>.4s, V<i1_r2_m>.8h, v0.h[0]
    smlal  V<i1_r3_lo>.4s, V<i1_r3_m>.4h, v0.h[0]
    smlal2 V<i1_r3_hi>.4s, V<i1_r3_m>.8h, v0.h[0]
    uzp2 V<i1_raw0>.8h, V<i1_r0_lo>.8h, V<i1_r0_hi>.8h
    uzp2 V<i1_raw1>.8h, V<i1_r1_lo>.8h, V<i1_r1_hi>.8h
    uzp2 V<i1_raw2>.8h, V<i1_r2_lo>.8h, V<i1_r2_hi>.8h
    uzp2 V<i1_raw3>.8h, V<i1_r3_lo>.8h, V<i1_r3_hi>.8h
    st4 {V<i1_raw0>.8h, V<i1_raw1>.8h, V<i1_raw2>.8h, V<i1_raw3>.8h}, [x0], #64
rminus1_pair_slothy_end:
    subs x8, x8, #1
    b.ne .Lpoly_basemul_rminus1_pair_slothy_loop
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
