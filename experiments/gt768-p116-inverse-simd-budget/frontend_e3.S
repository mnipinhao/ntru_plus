/* Section: decap_packed64.S; private namespace e3fe_ */
#ifdef __APPLE__
.text
#else
.section .text.e3fe_body,"ax",%progbits
#endif
/*
 * GT Production checked packed ct/f consumer.
 *
 * int e3_poly_frombytes_basemul_decap_scale(
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
.section .text.e3fe_body,"ax",%progbits
#endif
.p2align 4

#ifdef __APPLE__
#define C_SYM_1(sym) _##sym
#define C_SYM(sym) C_SYM_1(sym)
#else
#define C_SYM(sym) sym
#endif

.global C_SYM(e3_poly_frombytes_basemul_decap_scale)
#ifndef __APPLE__
.type C_SYM(e3_poly_frombytes_basemul_decap_scale), %function
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
.macro e3fe_W22_DECODE64 src, h0, h1, h2, h3, t0, t1, t2, t3
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
.macro e3fe_W22_BASEMUL_SCALE a0, a1, a2, a3, b0, b1, b2, b3
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

C_SYM(e3_poly_frombytes_basemul_decap_scale):
    stp d8,  d9,  [sp, #-64]!
    stp d10, d11, [sp, #16]
    stp d12, d13, [sp, #32]
    stp d14, d15, [sp, #48]

    adr x4, e3fe_.Lgt_decap_zetas_mul
    ld1 {v0.8h}, [x4], #16
    adr x5, e3fe_.Lgt_decap_mask_0fff
    ldr q31, [x5]
    movi v29.16b, #0
    mov x8, #1536

.p2align 4
e3fe_.Lgt_decap_checked_ct_f_basemul_scale64_loop64:
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
        st4 {v12.8H, v13.8H, v14.8H, v15.8H}, [x0], #64  /* P116 E3: product as AoS elements */
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
        st4 {v12.8H, v13.8H, v14.8H, v15.8H}, [x0], #64  /* P116 E3: product as AoS elements */

    subs x8, x8, #128
    b.ne e3fe_.Lgt_decap_checked_ct_f_basemul_scale64_loop64

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
.size C_SYM(e3_poly_frombytes_basemul_decap_scale), \
      .-C_SYM(e3_poly_frombytes_basemul_decap_scale)
#endif

.p2align 4
e3fe_.Lgt_decap_zetas_mul:
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
e3fe_.Lgt_decap_mask_0fff:
    .hword 0x0fff, 0x0fff, 0x0fff, 0x0fff
    .hword 0x0fff, 0x0fff, 0x0fff, 0x0fff

#undef C_SYM
#ifdef __APPLE__
#undef C_SYM_1
#endif

/* End section: decap_packed64.S */
