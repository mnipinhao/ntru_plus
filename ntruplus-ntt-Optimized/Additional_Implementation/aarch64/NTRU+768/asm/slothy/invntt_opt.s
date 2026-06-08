/*
 * Generated AArch64 NEON inverse NTT for the Good-Thomas row-bitrev
 * layout produced by asm/my_ntt.s.  The retained clean Slothy component
 * sources are invntt32_fixed_clean.slothy.s and
 * invntt_post_fused_clean.slothy.s.
 *
 * Constant tables here are normal centered multipliers plus sqrdmulh
 * precompute constants.  They are not Montgomery-form tables.
 */

.macro BARRETT_REDUCE reg, tmp
    sqdmulh \tmp\().8h, \reg\().8h, v0.h[1]
    srshr   \tmp\().8h, \tmp\().8h, #11
    mls     \reg\().8h, \tmp\().8h, v0.h[0]
.endm

.macro CENTER_NORMALIZE_Q reg, qvec, hi, lo, mask
    cmgt \mask\().8h, \reg\().8h, \hi\().8h
    and  \mask\().16b, \mask\().16b, \qvec\().16b
    sub  \reg\().8h, \reg\().8h, \mask\().8h
    cmgt \mask\().8h, \lo\().8h, \reg\().8h
    and  \mask\().16b, \mask\().16b, \qvec\().16b
    add  \reg\().8h, \reg\().8h, \mask\().8h
.endm

.macro FQMUL_LANE out, in, tw, twlane, pre, prelane, tmp
    sqrdmulh \tmp\().8h, \in\().8h, \pre\().h[\prelane]
    mul      \out\().8h, \in\().8h, \tw\().h[\twlane]
    mls      \out\().8h, \tmp\().8h, v0.h[0]
.endm

.macro INV_BUTTERFLY_LANE lo, hi, tw, twlane, pre, prelane, prod, tmp
    FQMUL_LANE \prod, \hi, \tw, \twlane, \pre, \prelane, \tmp
    mov      \tmp\().16b, \lo\().16b
    add      \lo\().8h, \lo\().8h, \prod\().8h
    sub      \hi\().8h, \tmp\().8h, \prod\().8h
.ifdef INVNTT_ROW_REDUCE_EAGER
    BARRETT_REDUCE \lo, \tmp
    BARRETT_REDUCE \hi, \tmp
.endif
.endm

.macro REDUCE_ROW_VEC off
    ldr q3, [x2, #\off]
    BARRETT_REDUCE v3, v12
    str q3, [x2, #\off]
.endm

.macro REDUCE_ROW_ALL
    /*
     * Default inverse row lazy-reduction policy.
     *
     * The inverse row NTT32 leaves all five stages lazy, then reduces the
     * 32 natural-order row vectors once before the post-row DFT3/untwist/merge
     * pipeline consumes them.  The range analyzer models valid row inputs from
     * the production forward contract and observes a maximum pre-reduction
     * absolute value of about 9766 with no signed int16 add/sub wrap.  This
     * final row reduction restores the expected centered range for post-row.
     *
     * Define INVNTT_ROW_REDUCE_EAGER to restore the old regression fallback:
     * reduce both outputs after every inverse row butterfly and skip this pass.
     */
    .irp i,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31
        REDUCE_ROW_VEC (16 * \i)
    .endr
.endm

.macro INVNTT32_STAGE123_BLOCK base
    ldr q3,  [x2, #(\base + 0)]
    ldr q4,  [x2, #(\base + 16)]
    ldr q5,  [x2, #(\base + 32)]
    ldr q6,  [x2, #(\base + 48)]
    ldr q7,  [x2, #(\base + 64)]
    ldr q8,  [x2, #(\base + 80)]
    ldr q9,  [x2, #(\base + 96)]
    ldr q10, [x2, #(\base + 112)]

    /* len=2 */
    INV_BUTTERFLY_LANE v3, v4, v1, 0, v2, 0, v11, v12
    INV_BUTTERFLY_LANE v5, v6, v1, 0, v2, 0, v11, v12
    INV_BUTTERFLY_LANE v7, v8, v1, 0, v2, 0, v11, v12
    INV_BUTTERFLY_LANE v9, v10, v1, 0, v2, 0, v11, v12

    /* len=4 */
    INV_BUTTERFLY_LANE v3, v5, v1, 0, v2, 0, v11, v12
    INV_BUTTERFLY_LANE v4, v6, v1, 1, v2, 1, v11, v12
    INV_BUTTERFLY_LANE v7, v9, v1, 0, v2, 0, v11, v12
    INV_BUTTERFLY_LANE v8, v10, v1, 1, v2, 1, v11, v12

    /* len=8 */
    INV_BUTTERFLY_LANE v3, v7, v1, 0, v2, 0, v11, v12
    INV_BUTTERFLY_LANE v4, v8, v1, 2, v2, 2, v11, v12
    INV_BUTTERFLY_LANE v5, v9, v1, 3, v2, 3, v11, v12
    INV_BUTTERFLY_LANE v6, v10, v1, 4, v2, 4, v11, v12

    str q3,  [x2, #(\base + 0)]
    str q4,  [x2, #(\base + 16)]
    str q5,  [x2, #(\base + 32)]
    str q6,  [x2, #(\base + 48)]
    str q7,  [x2, #(\base + 64)]
    str q8,  [x2, #(\base + 80)]
    str q9,  [x2, #(\base + 96)]
    str q10, [x2, #(\base + 112)]
.endm

.macro INVNTT32_STAGE45_STRIPE j
    ldr q1, [x3], #16
    ldr q2, [x3], #16

    ldr q3, [x2, #(16 * \j)]
    ldr q4, [x2, #(16 * (\j + 8))]
    ldr q5, [x2, #(16 * (\j + 16))]
    ldr q6, [x2, #(16 * (\j + 24))]

    /* len=16 for the lower and upper halves, then len=32. */
    INV_BUTTERFLY_LANE v3, v4, v1, 0, v2, 0, v11, v12
    INV_BUTTERFLY_LANE v5, v6, v1, 0, v2, 0, v11, v12
    INV_BUTTERFLY_LANE v3, v5, v1, 1, v2, 1, v11, v12
    INV_BUTTERFLY_LANE v4, v6, v1, 2, v2, 2, v11, v12

    str q3, [x2, #(16 * \j)]
    str q4, [x2, #(16 * (\j + 8))]
    str q5, [x2, #(16 * (\j + 16))]
    str q6, [x2, #(16 * (\j + 24))]
.endm

.macro DIRECT_LOAD_VEC dstidx, srcoff
    ldr d1, [x3, #\srcoff]
    ldr d2, [x4, #\srcoff]
    mov v1.d[1], v2.d[0]
    str q1, [x2, #(16 * \dstidx)]
.endm

.macro DIRECT_LOAD_ROW0
    /* k3=0 physical bytes: 0,24,48,...,744 */
    .irp i,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31
        DIRECT_LOAD_VEC \i, (24 * \i)
    .endr
.endm

.macro DIRECT_LOAD_ROW1
    /* k3=1 physical bytes: 256,280,...,760 then 16,40,...,232 */
    .irp i,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21
        DIRECT_LOAD_VEC \i, (256 + 24 * \i)
    .endr
    .irp i,22,23,24,25,26,27,28,29,30,31
        DIRECT_LOAD_VEC \i, (16 + 24 * (\i - 22))
    .endr
.endm

.macro DIRECT_LOAD_ROW2
    /* k3=2 physical bytes: 512,536,...,752 then 8,32,...,488 */
    .irp i,0,1,2,3,4,5,6,7,8,9,10
        DIRECT_LOAD_VEC \i, (512 + 24 * \i)
    .endr
    .irp i,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31
        DIRECT_LOAD_VEC \i, (8 + 24 * (\i - 11))
    .endr
.endm

.macro RUN_INVNTT32_ROW
    bl _invntt32_8way_fixed
.endm

.macro POST_STORE_PTR xvec, ptr, off_lo, off_hi
    ldr     q10, [x3], #16
    ldr     q11, [x3], #16
    sqrdmulh v12.8h, \xvec\().8h, v11.8h
    mul      v13.8h, \xvec\().8h, v10.8h
    mls      v13.8h, v12.8h, v0.h[0]

    ext      v14.16b, v13.16b, v13.16b, #8
    add      v24.8h, v13.8h, v14.8h
    sub      v16.8h, v13.8h, v14.8h

    sqrdmulh v17.8h, v16.8h, v0.h[5]
    mul      v18.8h, v16.8h, v0.h[4]
    mls      v18.8h, v17.8h, v0.h[0]

    sub      v19.8h, v24.8h, v18.8h
    sqrdmulh v20.8h, v19.8h, v0.h[7]
    mul      v21.8h, v19.8h, v0.h[6]
    mls      v21.8h, v20.8h, v0.h[0]

    sqrdmulh v22.8h, v18.8h, v15.h[1]
    mul      v23.8h, v18.8h, v15.h[0]
    mls      v23.8h, v22.8h, v0.h[0]

.ifdef INVNTT_POST_FINAL_NORMALIZE
    /*
     * Optional postlazy scheme-safety variant.
     *
     * INVNTT_POST_DFT3_NO_REDUCE removes the 96 standalone DFT3 Barrett
     * reductions and leaves final outputs in a lazy mod-q representative range
     * of about [-1916,1915].  This opt-in pass normalizes only the final stored
     * coefficients into centered canonical [-1728,1728], so representative-
     * sensitive callers such as poly_crepmod3 can consume the output without
     * restoring the DFT3 reductions.
     */
    dup      v25.8h, v0.h[0]
    dup      v26.8h, v15.h[2]
    dup      v27.8h, v15.h[3]
    CENTER_NORMALIZE_Q v21, v25, v26, v27, v28
    CENTER_NORMALIZE_Q v23, v25, v26, v27, v28
.endif

    str      d21, [\ptr, #\off_lo]
    str      d23, [\ptr, #\off_hi]
.endm

.macro FUSED_POST_STRIPE ptr0, off0_lo, off0_hi, ptr1, off1_lo, off1_hi, ptr2, off2_lo, off2_hi
    ldr q1, [x8], #16
    ldr q2, [x9], #16
    ldr q3, [x10], #16

    sub      v4.8h, v3.8h, v2.8h
    sqrdmulh v5.8h, v4.8h, v0.h[3]
    mul      v6.8h, v4.8h, v0.h[2]
    mls      v6.8h, v5.8h, v0.h[0]

    /*
     * Production reduces the three inverse DFT3 outputs before untwist.
     * INVNTT_POST_DFT3_NO_REDUCE is an opt-in benchmark variant that delays
     * these reductions into the later untwist/merge fqmul chain.  The post
     * range analyzer found it mod-q equivalent with no int16 wraps, but not
     * exact-representative identical, so it is intentionally not default.
     *
     * This matters for scheme integration: q = 3457 == 1 (mod 3), and
     * poly_crepmod3 reduces the raw signed representative modulo 3.  A final
     * postlazy value alone does not identify whether it should be corrected by
     * 0, +q, or -q relative to rowlazy, so a final-value-only crepmod3 fix is
     * not mathematically equivalent.
     */
    add      v7.8h, v1.8h, v2.8h
    add      v7.8h, v7.8h, v3.8h
.ifndef INVNTT_POST_DFT3_NO_REDUCE
    BARRETT_REDUCE v7, v24
.endif

    sub      v8.8h, v1.8h, v2.8h
    add      v8.8h, v8.8h, v6.8h
.ifndef INVNTT_POST_DFT3_NO_REDUCE
    BARRETT_REDUCE v8, v24
.endif

    sub      v9.8h, v1.8h, v3.8h
    sub      v9.8h, v9.8h, v6.8h
.ifndef INVNTT_POST_DFT3_NO_REDUCE
    BARRETT_REDUCE v9, v24
.endif

    POST_STORE_PTR v7, \ptr0, \off0_lo, \off0_hi
    POST_STORE_PTR v8, \ptr1, \off1_lo, \off1_hi
    POST_STORE_PTR v9, \ptr2, \off2_lo, \off2_hi
.endm

.global poly_invntt
.global _poly_invntt
poly_invntt:
_poly_invntt:
    stp x30, x0, [sp, #-16]!
    sub sp, sp, #1568

    adr x3, inv_consts
    ldr q0, [x3]

    /*
     * Step 1/2 row input path.
     *
     * Direct path:
     *   physical_j(k3,k32_br) = (32*k3 + 3*k32_br) mod 96
     *   branch0 byte = src + 8*physical_j
     *   branch1 byte = src + 768 + 8*physical_j
     *
     * Each direct load builds lanes
     *   [branch0 q0..q3, branch1 q0..q3]
     * in row-bitrev k32 order, then immediately runs the existing inverse
     * row NTT32.  This avoids materializing all three input rows before the
     * row NTT while keeping the fixed row kernel and post-row pipeline intact.
     */
.ifdef INVNTT_USE_OLD_GATHER
    add x2, sp, #32
    adr x3, inv_gather_offsets
    add x4, x1, #768
    mov x5, #96
1:
    ldrh w6, [x3], #2
    add x7, x2, x6
    ldr d1, [x1], #8
    ldr d2, [x4], #8
    mov v1.d[1], v2.d[0]
    str q1, [x7]
    subs x5, x5, #1
    b.ne 1b

    /* Step 2: inverse row NTT32, bit-reversed k32 input -> natural k32 output. */
    add x2, sp, #32
    RUN_INVNTT32_ROW
    add x2, sp, #544
    RUN_INVNTT32_ROW
    add x2, sp, #1056
    RUN_INVNTT32_ROW
.else
    add x3, x1, #0
    add x4, x1, #768
    add x2, sp, #32
    DIRECT_LOAD_ROW0
    RUN_INVNTT32_ROW

    add x3, x1, #0
    add x4, x1, #768
    add x2, sp, #544
    DIRECT_LOAD_ROW1
    RUN_INVNTT32_ROW

    add x3, x1, #0
    add x4, x1, #768
    add x2, sp, #1056
    DIRECT_LOAD_ROW2
    RUN_INVNTT32_ROW
.endif

    /* Steps 3-5: inverse DFT3, untwist F_b^k, remove scale 96 in merge. */
    adr x3, inv_consts
    ldr q15, [x3, #16]
    ldr x0, [sp, #1576]
    add x8, sp, #32
    add x9, sp, #544
    add x10, sp, #1056
    adr x3, inv_untwist_vecs

    /*
     * Fixed/generated natural-output store pattern.  For natural k32:
     *   k32 mod 3 == 0: v7->A, v8->B, v9->C
     *   k32 mod 3 == 1: v7->C+8, v8->A+8, v9->B+8
     *   k32 mod 3 == 2: v7->B+16, v8->C+16, v9->A+16
     * where A=x0+k32_group*24, B=x0+512+k32_group*24,
     * C=x0+256+k32_group*24.  The branch1 half is stored +768.
     */
    add x11, x0, #0
    add x12, x0, #512
    add x13, x0, #256
    mov x5, #10
slothy_start_invntt_post_fused:
4:
    FUSED_POST_STRIPE x11, 0, 768, x12, 0, 768, x13, 0, 768
    FUSED_POST_STRIPE x13, 8, 776, x11, 8, 776, x12, 8, 776
    FUSED_POST_STRIPE x12, 16, 784, x13, 16, 784, x11, 16, 784
    add x11, x11, #24
    add x12, x12, #24
    add x13, x13, #24
    subs x5, x5, #1
    b.ne 4b
    FUSED_POST_STRIPE x11, 0, 768, x12, 0, 768, x13, 0, 768
    FUSED_POST_STRIPE x13, 8, 776, x11, 8, 776, x12, 8, 776
slothy_end_invntt_post_fused:

    add sp, sp, #1568
    ldp x30, x0, [sp], #16
    ret

_invntt32_8way_fixed:
slothy_start_invntt32_fixed_stage123:
    adr x3, invntt32_stage123_consts
    ldr q1, [x3]
    ldr q2, [x3, #16]
    INVNTT32_STAGE123_BLOCK 0
    INVNTT32_STAGE123_BLOCK 128
    INVNTT32_STAGE123_BLOCK 256
    INVNTT32_STAGE123_BLOCK 384
slothy_end_invntt32_fixed_stage123:

slothy_start_invntt32_fixed_stage45:
    adr x3, invntt32_stage45_consts
    INVNTT32_STAGE45_STRIPE 0
    INVNTT32_STAGE45_STRIPE 1
    INVNTT32_STAGE45_STRIPE 2
    INVNTT32_STAGE45_STRIPE 3
    INVNTT32_STAGE45_STRIPE 4
    INVNTT32_STAGE45_STRIPE 5
    INVNTT32_STAGE45_STRIPE 6
    INVNTT32_STAGE45_STRIPE 7
.ifndef INVNTT_ROW_REDUCE_EAGER
    REDUCE_ROW_ALL
.endif
slothy_end_invntt32_fixed_stage45:
    ret

.align 4
inv_consts:
    .hword 3457, 19412, -723, -6853, 1634, 15488, -18, -171
    .hword -36, -341, 1728, -1728, 0, 0, 0, 0

.align 4
inv_gather_offsets:
    .hword      0,   1200,    864,     16,   1216,    880,     32,   1232
    .hword    896,     48,   1248,    912,     64,   1264,    928,     80
    .hword   1280,    944,     96,   1296,    960,    112,   1312,    976
    .hword    128,   1328,    992,    144,   1344,   1008,    160,   1360
    .hword    512,    176,   1376,    528,    192,   1392,    544,    208
    .hword   1408,    560,    224,   1424,    576,    240,   1440,    592
    .hword    256,   1456,    608,    272,   1472,    624,    288,   1488
    .hword    640,    304,   1504,    656,    320,   1520,    672,    336
    .hword   1024,    688,    352,   1040,    704,    368,   1056,    720
    .hword    384,   1072,    736,    400,   1088,    752,    416,   1104
    .hword    768,    432,   1120,    784,    448,   1136,    800,    464
    .hword   1152,    816,    480,   1168,    832,    496,   1184,    848

.align 4
invntt32_stage123_consts:
    .hword      1,    708,   1521,    708,  -1716,      0,      0,      0
    .hword      9,   6711,  14417,   6711, -16266,      0,      0,      0

.align 4
invntt32_stage45_consts:
    // j=0: len16[j], len32[j], len32[j+8] normal multipliers and precompute
    .hword      1,      1,    708,      0,      0,      0,      0,      0
    .hword      9,      9,   6711,      0,      0,      0,      0,      0
    // j=1
    .hword    -39,   -436,  -1015,      0,      0,      0,      0,      0
    .hword   -370,  -4133,  -9621,      0,      0,      0,      0,      0
    // j=2
    .hword   1521,    -39,     44,      0,      0,      0,      0,      0
    .hword  14417,   -370,    417,      0,      0,      0,      0,      0
    // j=3
    .hword   -550,   -281,   1558,      0,      0,      0,      0,      0
    .hword  -5213,  -2664,  14768,      0,      0,      0,      0,      0
    // j=4
    .hword    708,   1521,  -1716,      0,      0,      0,      0,      0
    .hword   6711,  14417, -16266,      0,      0,      0,      0,      0
    // j=5
    .hword     44,    588,   1464,      0,      0,      0,      0,      0
    .hword    417,   5573,  13877,      0,      0,      0,      0,      0
    // j=6
    .hword  -1716,   -550,   1241,      0,      0,      0,      0,      0
    .hword -16266,  -5213,  11763,      0,      0,      0,      0,      0
    // j=7
    .hword   1241,   1267,   1673,      0,      0,      0,      0,      0
    .hword  11763,  12010,  15858,      0,      0,      0,      0,      0

.align 4
inv_untwist_vecs:
    // k=0: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword      1,      1,      1,      1,      1,      1,      1,      1
    .hword      9,      9,      9,      9,      9,      9,      9,      9
    // k=64: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1520,   1520,   1520,   1520,   -257,   -257,   -257,   -257
    .hword  14408,  14408,  14408,  14408,  -2436,  -2436,  -2436,  -2436
    // k=32: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    867,    867,    867,    867,  -1571,  -1571,  -1571,  -1571
    .hword   8218,   8218,   8218,   8218, -14891, -14891, -14891, -14891
    // k=33: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1723,  -1723,  -1723,  -1723,      8,      8,      8,      8
    .hword -16332, -16332, -16332, -16332,     76,     76,     76,     76
    // k=1: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword      2,      2,      2,      2,     22,     22,     22,     22
    .hword     19,     19,     19,     19,    209,    209,    209,    209
    // k=65: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -417,   -417,   -417,   -417,   1260,   1260,   1260,   1260
    .hword  -3953,  -3953,  -3953,  -3953,  11943,  11943,  11943,  11943
    // k=66: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -834,   -834,   -834,   -834,     64,     64,     64,     64
    .hword  -7905,  -7905,  -7905,  -7905,    607,    607,    607,    607
    // k=34: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword     11,     11,     11,     11,    176,    176,    176,    176
    .hword    104,    104,    104,    104,   1668,   1668,   1668,   1668
    // k=2: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword      4,      4,      4,      4,    484,    484,    484,    484
    .hword     38,     38,     38,     38,   4588,   4588,   4588,   4588
    // k=3: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword      8,      8,      8,      8,    277,    277,    277,    277
    .hword     76,     76,     76,     76,   2626,   2626,   2626,   2626
    // k=67: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1668,  -1668,  -1668,  -1668,   1408,   1408,   1408,   1408
    .hword -15811, -15811, -15811, -15811,  13346,  13346,  13346,  13346
    // k=35: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword     22,     22,     22,     22,    415,    415,    415,    415
    .hword    209,    209,    209,    209,   3934,   3934,   3934,   3934
    // k=36: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword     44,     44,     44,     44,  -1241,  -1241,  -1241,  -1241
    .hword    417,    417,    417,    417, -11763, -11763, -11763, -11763
    // k=4: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword     16,     16,     16,     16,   -820,   -820,   -820,   -820
    .hword    152,    152,    152,    152,  -7773,  -7773,  -7773,  -7773
    // k=68: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    121,    121,    121,    121,   -137,   -137,   -137,   -137
    .hword   1147,   1147,   1147,   1147,  -1299,  -1299,  -1299,  -1299
    // k=69: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    242,    242,    242,    242,    443,    443,    443,    443
    .hword   2294,   2294,   2294,   2294,   4199,   4199,   4199,   4199
    // k=37: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword     88,     88,     88,     88,    354,    354,    354,    354
    .hword    834,    834,    834,    834,   3355,   3355,   3355,   3355
    // k=5: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword     32,     32,     32,     32,   -755,   -755,   -755,   -755
    .hword    303,    303,    303,    303,  -7156,  -7156,  -7156,  -7156
    // k=6: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword     64,     64,     64,     64,    675,    675,    675,    675
    .hword    607,    607,    607,    607,   6398,   6398,   6398,   6398
    // k=70: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    484,    484,    484,    484,   -625,   -625,   -625,   -625
    .hword   4588,   4588,   4588,   4588,  -5924,  -5924,  -5924,  -5924
    // k=38: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    176,    176,    176,    176,    874,    874,    874,    874
    .hword   1668,   1668,   1668,   1668,   8284,   8284,   8284,   8284
    // k=39: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    352,    352,    352,    352,  -1514,  -1514,  -1514,  -1514
    .hword   3337,   3337,   3337,   3337, -14351, -14351, -14351, -14351
    // k=7: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    128,    128,    128,    128,   1022,   1022,   1022,   1022
    .hword   1213,   1213,   1213,   1213,   9687,   9687,   9687,   9687
    // k=71: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    968,    968,    968,    968,     78,     78,     78,     78
    .hword   9175,   9175,   9175,   9175,    739,    739,    739,    739
    // k=72: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1521,  -1521,  -1521,  -1521,   1716,   1716,   1716,   1716
    .hword -14417, -14417, -14417, -14417,  16266,  16266,  16266,  16266
    // k=40: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    704,    704,    704,    704,   1262,   1262,   1262,   1262
    .hword   6673,   6673,   6673,   6673,  11962,  11962,  11962,  11962
    // k=8: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    256,    256,    256,    256,  -1715,  -1715,  -1715,  -1715
    .hword   2427,   2427,   2427,   2427, -16256, -16256, -16256, -16256
    // k=9: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    512,    512,    512,    512,    297,    297,    297,    297
    .hword   4853,   4853,   4853,   4853,   2815,   2815,   2815,   2815
    // k=73: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    415,    415,    415,    415,   -275,   -275,   -275,   -275
    .hword   3934,   3934,   3934,   3934,  -2607,  -2607,  -2607,  -2607
    // k=41: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1408,   1408,   1408,   1408,    108,    108,    108,    108
    .hword  13346,  13346,  13346,  13346,   1024,   1024,   1024,   1024
    // k=42: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -641,   -641,   -641,   -641,  -1081,  -1081,  -1081,  -1081
    .hword  -6076,  -6076,  -6076,  -6076, -10247, -10247, -10247, -10247
    // k=10: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1024,   1024,   1024,   1024,   -380,   -380,   -380,   -380
    .hword   9706,   9706,   9706,   9706,  -3602,  -3602,  -3602,  -3602
    // k=74: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    830,    830,    830,    830,    864,    864,    864,    864
    .hword   7867,   7867,   7867,   7867,   8190,   8190,   8190,   8190
    // k=75: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1660,   1660,   1660,   1660,   1723,   1723,   1723,   1723
    .hword  15735,  15735,  15735,  15735,  16332,  16332,  16332,  16332
    // k=43: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1282,  -1282,  -1282,  -1282,    417,    417,    417,    417
    .hword -12152, -12152, -12152, -12152,   3953,   3953,   3953,   3953
    // k=11: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1409,  -1409,  -1409,  -1409,  -1446,  -1446,  -1446,  -1446
    .hword -13356, -13356, -13356, -13356, -13706, -13706, -13706, -13706
    // k=12: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    639,    639,    639,    639,   -699,   -699,   -699,   -699
    .hword   6057,   6057,   6057,   6057,  -6626,  -6626,  -6626,  -6626
    // k=76: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -137,   -137,   -137,   -137,   -121,   -121,   -121,   -121
    .hword  -1299,  -1299,  -1299,  -1299,  -1147,  -1147,  -1147,  -1147
    // k=44: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    893,    893,    893,    893,  -1197,  -1197,  -1197,  -1197
    .hword   8465,   8465,   8465,   8465, -11346, -11346, -11346, -11346
    // k=45: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1671,  -1671,  -1671,  -1671,   1322,   1322,   1322,   1322
    .hword -15839, -15839, -15839, -15839,  12531,  12531,  12531,  12531
    // k=13: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1278,   1278,   1278,   1278,  -1550,  -1550,  -1550,  -1550
    .hword  12114,  12114,  12114,  12114, -14692, -14692, -14692, -14692
    // k=77: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -274,   -274,   -274,   -274,    795,    795,    795,    795
    .hword  -2597,  -2597,  -2597,  -2597,   7536,   7536,   7536,   7536
    // k=78: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -548,   -548,   -548,   -548,    205,    205,    205,    205
    .hword  -5194,  -5194,  -5194,  -5194,   1943,   1943,   1943,   1943
    // k=46: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    115,    115,    115,    115,   1428,   1428,   1428,   1428
    .hword   1090,   1090,   1090,   1090,  13536,  13536,  13536,  13536
    // k=14: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -901,   -901,   -901,   -901,    470,    470,    470,    470
    .hword  -8540,  -8540,  -8540,  -8540,   4455,   4455,   4455,   4455
    // k=15: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1655,   1655,   1655,   1655,    -31,    -31,    -31,    -31
    .hword  15687,  15687,  15687,  15687,   -294,   -294,   -294,   -294
    // k=79: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1096,  -1096,  -1096,  -1096,   1053,   1053,   1053,   1053
    .hword -10389, -10389, -10389, -10389,   9981,   9981,   9981,   9981
    // k=47: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    230,    230,    230,    230,    303,    303,    303,    303
    .hword   2180,   2180,   2180,   2180,   2872,   2872,   2872,   2872
    // k=48: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    460,    460,    460,    460,   -248,   -248,   -248,   -248
    .hword   4360,   4360,   4360,   4360,  -2351,  -2351,  -2351,  -2351
    // k=16: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -147,   -147,   -147,   -147,   -682,   -682,   -682,   -682
    .hword  -1393,  -1393,  -1393,  -1393,  -6464,  -6464,  -6464,  -6464
    // k=80: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1265,   1265,   1265,   1265,  -1033,  -1033,  -1033,  -1033
    .hword  11991,  11991,  11991,  11991,  -9792,  -9792,  -9792,  -9792
    // k=81: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -927,   -927,   -927,   -927,   1473,   1473,   1473,   1473
    .hword  -8787,  -8787,  -8787,  -8787,  13962,  13962,  13962,  13962
    // k=49: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    920,    920,    920,    920,   1458,   1458,   1458,   1458
    .hword   8720,   8720,   8720,   8720,  13820,  13820,  13820,  13820
    // k=17: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -294,   -294,   -294,   -294,  -1176,  -1176,  -1176,  -1176
    .hword  -2787,  -2787,  -2787,  -2787, -11147, -11147, -11147, -11147
    // k=18: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -588,   -588,   -588,   -588,  -1673,  -1673,  -1673,  -1673
    .hword  -5573,  -5573,  -5573,  -5573, -15858, -15858, -15858, -15858
    // k=82: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1603,   1603,   1603,   1603,   1293,   1293,   1293,   1293
    .hword  15194,  15194,  15194,  15194,  12256,  12256,  12256,  12256
    // k=50: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1617,  -1617,  -1617,  -1617,    963,    963,    963,    963
    .hword -15327, -15327, -15327, -15327,   9128,   9128,   9128,   9128
    // k=51: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    223,    223,    223,    223,    444,    444,    444,    444
    .hword   2114,   2114,   2114,   2114,   4209,   4209,   4209,   4209
    // k=19: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1176,  -1176,  -1176,  -1176,   1221,   1221,   1221,   1221
    .hword -11147, -11147, -11147, -11147,  11574,  11574,  11574,  11574
    // k=83: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -251,   -251,   -251,   -251,    790,    790,    790,    790
    .hword  -2379,  -2379,  -2379,  -2379,   7488,   7488,   7488,   7488
    // k=84: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -502,   -502,   -502,   -502,     95,     95,     95,     95
    .hword  -4758,  -4758,  -4758,  -4758,    900,    900,    900,    900
    // k=52: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    446,    446,    446,    446,   -603,   -603,   -603,   -603
    .hword   4228,   4228,   4228,   4228,  -5716,  -5716,  -5716,  -5716
    // k=20: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1105,   1105,   1105,   1105,   -794,   -794,   -794,   -794
    .hword  10474,  10474,  10474,  10474,  -7526,  -7526,  -7526,  -7526
    // k=21: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1247,  -1247,  -1247,  -1247,   -183,   -183,   -183,   -183
    .hword -11820, -11820, -11820, -11820,  -1735,  -1735,  -1735,  -1735
    // k=85: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1004,  -1004,  -1004,  -1004,  -1367,  -1367,  -1367,  -1367
    .hword  -9517,  -9517,  -9517,  -9517, -12957, -12957, -12957, -12957
    // k=53: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    892,    892,    892,    892,    562,    562,    562,    562
    .hword   8455,   8455,   8455,   8455,   5327,   5327,   5327,   5327
    // k=54: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1673,  -1673,  -1673,  -1673,  -1464,  -1464,  -1464,  -1464
    .hword -15858, -15858, -15858, -15858, -13877, -13877, -13877, -13877
    // k=22: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    963,    963,    963,    963,   -569,   -569,   -569,   -569
    .hword   9128,   9128,   9128,   9128,  -5393,  -5393,  -5393,  -5393
    // k=86: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1449,   1449,   1449,   1449,   1039,   1039,   1039,   1039
    .hword  13735,  13735,  13735,  13735,   9848,   9848,   9848,   9848
    // k=87: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -559,   -559,   -559,   -559,  -1341,  -1341,  -1341,  -1341
    .hword  -5299,  -5299,  -5299,  -5299, -12711, -12711, -12711, -12711
    // k=55: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    111,    111,    111,    111,  -1095,  -1095,  -1095,  -1095
    .hword   1052,   1052,   1052,   1052, -10379, -10379, -10379, -10379
    // k=23: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1531,  -1531,  -1531,  -1531,   1310,   1310,   1310,   1310
    .hword -14512, -14512, -14512, -14512,  12417,  12417,  12417,  12417
    // k=24: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    395,    395,    395,    395,   1164,   1164,   1164,   1164
    .hword   3744,   3744,   3744,   3744,  11033,  11033,  11033,  11033
    // k=88: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1118,  -1118,  -1118,  -1118,   1611,   1611,   1611,   1611
    .hword -10597, -10597, -10597, -10597,  15270,  15270,  15270,  15270
    // k=56: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    222,    222,    222,    222,    109,    109,    109,    109
    .hword   2104,   2104,   2104,   2104,   1033,   1033,   1033,   1033
    // k=57: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    444,    444,    444,    444,  -1059,  -1059,  -1059,  -1059
    .hword   4209,   4209,   4209,   4209, -10038, -10038, -10038, -10038
    // k=25: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    790,    790,    790,    790,   1409,   1409,   1409,   1409
    .hword   7488,   7488,   7488,   7488,  13356,  13356,  13356,  13356
    // k=89: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1221,   1221,   1221,   1221,    872,    872,    872,    872
    .hword  11574,  11574,  11574,  11574,   8265,   8265,   8265,   8265
    // k=90: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1015,  -1015,  -1015,  -1015,  -1558,  -1558,  -1558,  -1558
    .hword  -9621,  -9621,  -9621,  -9621, -14768, -14768, -14768, -14768
    // k=58: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    888,    888,    888,    888,    901,    901,    901,    901
    .hword   8417,   8417,   8417,   8417,   8540,   8540,   8540,   8540
    // k=26: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1580,   1580,   1580,   1580,   -115,   -115,   -115,   -115
    .hword  14976,  14976,  14976,  14976,  -1090,  -1090,  -1090,  -1090
    // k=27: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -297,   -297,   -297,   -297,    927,    927,    927,    927
    .hword  -2815,  -2815,  -2815,  -2815,   8787,   8787,   8787,   8787
    // k=91: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1427,   1427,   1427,   1427,    294,    294,    294,    294
    .hword  13526,  13526,  13526,  13526,   2787,   2787,   2787,   2787
    // k=59: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1681,  -1681,  -1681,  -1681,   -920,   -920,   -920,   -920
    .hword -15934, -15934, -15934, -15934,  -8720,  -8720,  -8720,  -8720
    // k=60: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword     95,     95,     95,     95,    502,    502,    502,    502
    .hword    900,    900,    900,    900,   4758,   4758,   4758,   4758
    // k=28: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -594,   -594,   -594,   -594,   -348,   -348,   -348,   -348
    .hword  -5630,  -5630,  -5630,  -5630,  -3299,  -3299,  -3299,  -3299
    // k=92: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   -603,   -603,   -603,   -603,   -446,   -446,   -446,   -446
    .hword  -5716,  -5716,  -5716,  -5716,  -4228,  -4228,  -4228,  -4228
    // k=93: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1206,  -1206,  -1206,  -1206,    559,    559,    559,    559
    .hword -11431, -11431, -11431, -11431,   5299,   5299,   5299,   5299
    // k=61: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    190,    190,    190,    190,    673,    673,    673,    673
    .hword   1801,   1801,   1801,   1801,   6379,   6379,   6379,   6379
    // k=29: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1188,  -1188,  -1188,  -1188,   -742,   -742,   -742,   -742
    .hword -11261, -11261, -11261, -11261,  -7033,  -7033,  -7033,  -7033
    // k=30: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1081,   1081,   1081,   1081,    961,    961,    961,    961
    .hword  10247,  10247,  10247,  10247,   9109,   9109,   9109,   9109
    // k=94: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword   1045,   1045,   1045,   1045,  -1530,  -1530,  -1530,  -1530
    .hword   9905,   9905,   9905,   9905, -14502, -14502, -14502, -14502
    // k=62: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    380,    380,    380,    380,    978,    978,    978,    978
    .hword   3602,   3602,   3602,   3602,   9270,   9270,   9270,   9270
    // k=63: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword    760,    760,    760,    760,    774,    774,    774,    774
    .hword   7204,   7204,   7204,   7204,   7337,   7337,   7337,   7337
    // k=31: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1295,  -1295,  -1295,  -1295,    400,    400,    400,    400
    .hword -12275, -12275, -12275, -12275,   3791,   3791,   3791,   3791
    // k=95: normal multipliers for F0^k/F1^k and sqrdmulh precompute
    .hword  -1367,  -1367,  -1367,  -1367,    910,    910,    910,    910
    .hword -12957, -12957, -12957, -12957,   8626,   8626,   8626,   8626

.purgem BARRETT_REDUCE
.purgem FQMUL_LANE
.purgem INV_BUTTERFLY_LANE
.purgem REDUCE_ROW_VEC
.purgem REDUCE_ROW_ALL
.purgem INVNTT32_STAGE123_BLOCK
.purgem INVNTT32_STAGE45_STRIPE
.purgem DIRECT_LOAD_VEC
.purgem DIRECT_LOAD_ROW0
.purgem DIRECT_LOAD_ROW1
.purgem DIRECT_LOAD_ROW2
.purgem RUN_INVNTT32_ROW
.purgem POST_STORE_PTR
.purgem FUSED_POST_STRIPE
