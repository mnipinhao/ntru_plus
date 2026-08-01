/*
 * Production GT inverse NTT for inputs carrying one extra R^-1 factor.
 *
 * This entry is paired with the raw-factor basemul and returns normal R^0
 * coefficients. Production exports the pair as poly_basemul/poly_invntt.
 * Proof-gated multiplier-1 reductions are deferred through inverse NTT32
 * transform size 16; size 32 remains reduced.
 */

/*
 * Production-only AArch64 NEON inverse NTT for the Good-Thomas row-bitrev
 * layout produced by asm/ntt.S.
 *
 * This file keeps only the path currently wired into production wrappers:
 *   - direct physical input -> inverse NTT32 stage123
 *   - stage123 stripe scratch laid out for stage45 consumption
 *   - Slothy-scheduled stage45 + row-end Barrett reduction fusion
 *   - branchfold post path with final output reductions
 *   - fixed rminus1 branchfold constants
 */

.macro BARRETT_REDUCE reg, tmp
    sqdmulh \tmp\().8h, \reg\().8h, v0.h[1]
    srshr   \tmp\().8h, \tmp\().8h, #11
    mls     \reg\().8h, \tmp\().8h, v0.h[0]
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
.endm

.macro INV_BUTTERFLY_IDENTITY_LAZY lo, hi, tmp
    /* Proof-gated twiddle=1 path with the reduction intentionally deferred. */
    mov      \tmp\().16b, \lo\().16b
    add      \lo\().8h, \lo\().8h, \hi\().8h
    sub      \hi\().8h, \tmp\().8h, \hi\().8h
.endm

.macro DIRECT_STAGE123_VEC dst, srcoff
    ldr d\dst, [x3, #\srcoff]
    ldr d12, [x4, #\srcoff]
    mov v\dst\().d[1], v12.d[0]
.endm

.macro STORE_STAGE123_STRIPE_SCRATCH group
    /*
     * Store one 8-vector stage123 block in stage45 stripe-major order:
     *   scratch[64*j + 16*group] = stage123_output[j + 8*group]
     *
     * stage45 consumes each stripe as four contiguous q-vectors
     *   [j, j+8, j+16, j+24].
     *
     * This scratch cannot be overlaid with the final row buffer.  The final
     * natural-order stage45 stores would otherwise clobber unconsumed scratch
     * stripes in a cyclic dependency.
     */
    str q3,  [x14, #(64 * 0 + 16 * \group)]
    str q4,  [x14, #(64 * 1 + 16 * \group)]
    str q5,  [x14, #(64 * 2 + 16 * \group)]
    str q6,  [x14, #(64 * 3 + 16 * \group)]
    str q7,  [x14, #(64 * 4 + 16 * \group)]
    str q8,  [x14, #(64 * 5 + 16 * \group)]
    str q9,  [x14, #(64 * 6 + 16 * \group)]
    str q10, [x14, #(64 * 7 + 16 * \group)]
.endm

.macro DIRECT_STAGE123_BLOCK_TO_SCRATCH group, off0, off1, off2, off3, off4, off5, off6, off7
    DIRECT_STAGE123_VEC 3, \off0
    DIRECT_STAGE123_VEC 4, \off1
    DIRECT_STAGE123_VEC 5, \off2
    DIRECT_STAGE123_VEC 6, \off3
    DIRECT_STAGE123_VEC 7, \off4
    DIRECT_STAGE123_VEC 8, \off5
    DIRECT_STAGE123_VEC 9, \off6
    DIRECT_STAGE123_VEC 10, \off7

    /* len=2 */
    INV_BUTTERFLY_IDENTITY_LAZY v3, v4, v12
    INV_BUTTERFLY_IDENTITY_LAZY v5, v6, v12
    INV_BUTTERFLY_IDENTITY_LAZY v7, v8, v12
    INV_BUTTERFLY_IDENTITY_LAZY v9, v10, v12

    /* len=4 */
    INV_BUTTERFLY_IDENTITY_LAZY v3, v5, v12
    INV_BUTTERFLY_LANE v4, v6, v1, 1, v2, 1, v11, v12
    INV_BUTTERFLY_IDENTITY_LAZY v7, v9, v12
    INV_BUTTERFLY_LANE v8, v10, v1, 1, v2, 1, v11, v12

    /* len=8 */
    INV_BUTTERFLY_IDENTITY_LAZY v3, v7, v12
    INV_BUTTERFLY_LANE v4, v8, v1, 2, v2, 2, v11, v12
    INV_BUTTERFLY_LANE v5, v9, v1, 3, v2, 3, v11, v12
    INV_BUTTERFLY_LANE v6, v10, v1, 4, v2, 4, v11, v12

    STORE_STAGE123_STRIPE_SCRATCH \group
.endm

.macro DIRECT_STAGE123_CONSTS
    adr x7, invntt32_stage123_consts
    ldr q1, [x7]
    ldr q2, [x7, #16]
.endm

.macro DIRECT_STAGE123_STRIPE_SCRATCH_ROW0_BODY
    /*
     * Production row input path: direct physical load -> stage123 ->
     * stripe-major scratch for stage45.  This keeps stage123 math unchanged
     * but stores the temporary in the order consumed by stage45.
     */
    DIRECT_STAGE123_CONSTS
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 0,   0,  24,  48,  72,  96, 120, 144, 168
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 1, 192, 216, 240, 264, 288, 312, 336, 360
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 2, 384, 408, 432, 456, 480, 504, 528, 552
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 3, 576, 600, 624, 648, 672, 696, 720, 744
.endm

.macro DIRECT_STAGE123_STRIPE_SCRATCH_ROW0
    add x14, sp, #1568
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW0_BODY
.endm

.macro DIRECT_STAGE123_STRIPE_SCRATCH_ROW1_BODY
    /* k3=1 physical bytes: 256,280,...,760 then 16,40,...,232 */
    DIRECT_STAGE123_CONSTS
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 0, 256, 280, 304, 328, 352, 376, 400, 424
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 1, 448, 472, 496, 520, 544, 568, 592, 616
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 2, 640, 664, 688, 712, 736, 760,  16,  40
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 3,  64,  88, 112, 136, 160, 184, 208, 232
.endm

.macro DIRECT_STAGE123_STRIPE_SCRATCH_ROW1
    add x14, sp, #1568
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW1_BODY
.endm

.macro DIRECT_STAGE123_STRIPE_SCRATCH_ROW2_BODY
    /* k3=2 physical bytes: 512,536,...,752 then 8,32,...,488 */
    DIRECT_STAGE123_CONSTS
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 0, 512, 536, 560, 584, 608, 632, 656, 680
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 1, 704, 728, 752,   8,  32,  56,  80, 104
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 2, 128, 152, 176, 200, 224, 248, 272, 296
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 3, 320, 344, 368, 392, 416, 440, 464, 488
.endm

.macro DIRECT_STAGE123_STRIPE_SCRATCH_ROW2
    add x14, sp, #1568
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW2_BODY
.endm

.macro RUN_INVNTT32_STAGE45_SCRATCH_ROW
    /*
     * Slothy N1 schedule for all eight stage45 stripes as one row kernel.
     * Contract: x14 = stage123 stripe scratch, x2 = row output buffer,
     * v0 = q/reduction constants.  x3 is set here to the stage45 const base.
     */
    adr x3, invntt32_stage45_consts
        ldr q14, [x3, #16]
        ldr q17, [x14, #48]
        ldr q8, [x14, #0]
        ldr q21, [x14, #16]
        ldr q13, [x3, #0]
        ldr q29, [x14, #32]
        sub v30.8H, v29.8H, v17.8H
        add v26.8H, v29.8H, v17.8H
        sqrdmulh v7.8H, v30.8H, v14.H[2]
        mul v17.8H, v30.8H, v13.H[2]
        add v20.8H, v8.8H, v21.8H
        sub v21.8H, v8.8H, v21.8H
        sqrdmulh v24.8H, v26.8H, v14.H[1]
        ldr q4, [x3, #48]
        ldr q18, [x14, #112]
        mls v17.8H, v7.8H, v0.H[0]
        ldr q7, [x3, #32]
        mul v14.8H, v26.8H, v13.H[1]
        mls v14.8H, v24.8H, v0.H[0]
        add v13.8H, v21.8H, v17.8H
        sqrdmulh v12.8H, v18.8H, v4.H[0]
        sub v22.8H, v21.8H, v17.8H
        sqdmulh v15.8H, v13.8H, v0.H[1]
        add v26.8H, v20.8H, v14.8H
        sub v29.8H, v20.8H, v14.8H
        sqdmulh v10.8H, v22.8H, v0.H[1]
        sqdmulh v16.8H, v29.8H, v0.H[1]
        srshr v24.8H, v15.8H, #11
        srshr v21.8H, v16.8H, #11
        mls v13.8H, v24.8H, v0.H[0]
        ldr q17, [x14, #96]
        ldr q15, [x14, #80]
        ldr q8, [x14, #64]
        mul v14.8H, v18.8H, v7.H[0]
        mls v14.8H, v12.8H, v0.H[0]
        str q13, [x2, #128]
        mls v29.8H, v21.8H, v0.H[0]
        mul v3.8H, v15.8H, v7.H[0]
        sub v9.8H, v17.8H, v14.8H
        add v14.8H, v17.8H, v14.8H
        sqrdmulh v21.8H, v15.8H, v4.H[0]
        str q29, [x2, #256]
        mul v24.8H, v14.8H, v7.H[1]
        sqrdmulh v14.8H, v14.8H, v4.H[1]
        sqrdmulh v1.8H, v9.8H, v4.H[2]
        ldr q2, [x14, #128]
        ldr q25, [x14, #160]
        srshr v16.8H, v10.8H, #11
        mul v7.8H, v9.8H, v7.H[2]
        mls v3.8H, v21.8H, v0.H[0]
        mls v24.8H, v14.8H, v0.H[0]
        mls v22.8H, v16.8H, v0.H[0]
        sub v15.8H, v8.8H, v3.8H
        mls v7.8H, v1.8H, v0.H[0]
        add v23.8H, v8.8H, v3.8H
        sqdmulh v14.8H, v26.8H, v0.H[1]
        sub v12.8H, v23.8H, v24.8H
        add v29.8H, v23.8H, v24.8H
        sqdmulh v21.8H, v12.8H, v0.H[1]
        add v9.8H, v15.8H, v7.8H
        sqdmulh v23.8H, v29.8H, v0.H[1]
        srshr v24.8H, v14.8H, #11
        sub v1.8H, v15.8H, v7.8H
        srshr v14.8H, v23.8H, #11
        sqdmulh v16.8H, v9.8H, v0.H[1]
        ldr q13, [x3, #80]
        srshr v15.8H, v21.8H, #11
        sqdmulh v28.8H, v1.8H, v0.H[1]
        ldr q5, [x3, #64]
        ldr q17, [x14, #176]
        str q22, [x2, #384]
        mls v26.8H, v24.8H, v0.H[0]
        srshr v19.8H, v16.8H, #11
        mls v12.8H, v15.8H, v0.H[0]
        srshr v30.8H, v28.8H, #11
        mls v29.8H, v14.8H, v0.H[0]
        ldr q14, [x14, #144]
        str q26, [x2, #0]
        sqrdmulh v11.8H, v17.8H, v13.H[0]
        str q12, [x2, #272]
        str q29, [x2, #16]
        mul v3.8H, v17.8H, v5.H[0]
        sqrdmulh v16.8H, v14.8H, v13.H[0]
        mls v3.8H, v11.8H, v0.H[0]
        mls v9.8H, v19.8H, v0.H[0]
        mul v12.8H, v14.8H, v5.H[0]
        add v20.8H, v25.8H, v3.8H
        mls v12.8H, v16.8H, v0.H[0]
        sub v28.8H, v25.8H, v3.8H
        str q9, [x2, #144]
        sqrdmulh v6.8H, v20.8H, v13.H[1]
        sqrdmulh v23.8H, v28.8H, v13.H[2]
        sub v21.8H, v2.8H, v12.8H
        mul v10.8H, v20.8H, v5.H[1]
        add v3.8H, v2.8H, v12.8H
        ldr q9, [x3, #112]
        mul v17.8H, v28.8H, v5.H[2]
        ldr q2, [x14, #192]
        ldr q27, [x14, #240]
        mls v17.8H, v23.8H, v0.H[0]
        ldr q23, [x14, #208]
        ldr q7, [x3, #96]
        mls v10.8H, v6.8H, v0.H[0]
        mls v1.8H, v30.8H, v0.H[0]
        sub v13.8H, v21.8H, v17.8H
        add v11.8H, v21.8H, v17.8H
        mul v21.8H, v27.8H, v7.H[0]
        add v5.8H, v3.8H, v10.8H
        sqdmulh v26.8H, v11.8H, v0.H[1]
        sub v3.8H, v3.8H, v10.8H
        str q1, [x2, #400]
        sqrdmulh v19.8H, v27.8H, v9.H[0]
        mls v21.8H, v19.8H, v0.H[0]
        srshr v27.8H, v26.8H, #11
        ldr q15, [x14, #224]
        sqrdmulh v12.8H, v23.8H, v9.H[0]
        mul v26.8H, v23.8H, v7.H[0]
        sub v24.8H, v15.8H, v21.8H
        sqdmulh v14.8H, v3.8H, v0.H[1]
        add v8.8H, v15.8H, v21.8H
        sqrdmulh v23.8H, v24.8H, v9.H[2]
        mul v19.8H, v24.8H, v7.H[2]
        srshr v14.8H, v14.8H, #11
        mul v1.8H, v8.8H, v7.H[1]
        mls v26.8H, v12.8H, v0.H[0]
        sqrdmulh v15.8H, v8.8H, v9.H[1]
        mls v11.8H, v27.8H, v0.H[0]
        sub v18.8H, v2.8H, v26.8H
        ldr q9, [x14, #304]
        mls v1.8H, v15.8H, v0.H[0]
        add v25.8H, v2.8H, v26.8H
        str q11, [x2, #160]
        mls v19.8H, v23.8H, v0.H[0]
        ldr q6, [x3, #144]
        sqdmulh v26.8H, v13.8H, v0.H[1]
        sub v17.8H, v25.8H, v1.8H
        sqdmulh v7.8H, v5.8H, v0.H[1]
        sub v11.8H, v18.8H, v19.8H
        add v1.8H, v25.8H, v1.8H
        sqdmulh v12.8H, v17.8H, v0.H[1]
        add v15.8H, v18.8H, v19.8H
        srshr v23.8H, v26.8H, #11
        sqdmulh v8.8H, v11.8H, v0.H[1]
        srshr v4.8H, v7.8H, #11
        sqdmulh v26.8H, v15.8H, v0.H[1]
        mls v3.8H, v14.8H, v0.H[0]
        ldr q27, [x14, #256]
        ldr q22, [x14, #288]
        srshr v21.8H, v8.8H, #11
        ldr q7, [x14, #272]
        sqrdmulh v14.8H, v9.8H, v6.H[0]
        srshr v18.8H, v26.8H, #11
        ldr q2, [x3, #128]
        mls v13.8H, v23.8H, v0.H[0]
        srshr v26.8H, v12.8H, #11
        str q3, [x2, #288]
        sqrdmulh v29.8H, v7.8H, v6.H[0]
        mls v15.8H, v18.8H, v0.H[0]
        str q13, [x2, #416]
        mul v25.8H, v7.8H, v2.H[0]
        mls v25.8H, v29.8H, v0.H[0]
        str q15, [x2, #176]
        mul v9.8H, v9.8H, v2.H[0]
        sub v3.8H, v27.8H, v25.8H
        add v7.8H, v27.8H, v25.8H
        mls v9.8H, v14.8H, v0.H[0]
        mls v17.8H, v26.8H, v0.H[0]
        mls v5.8H, v4.8H, v0.H[0]
        sub v25.8H, v22.8H, v9.8H
        sqdmulh v24.8H, v1.8H, v0.H[1]
        str q17, [x2, #304]
        add v17.8H, v22.8H, v9.8H
        sqrdmulh v9.8H, v25.8H, v6.H[2]
        str q5, [x2, #32]
        sqrdmulh v20.8H, v17.8H, v6.H[1]
        mul v27.8H, v25.8H, v2.H[2]
        srshr v8.8H, v24.8H, #11
        mls v27.8H, v9.8H, v0.H[0]
        mul v25.8H, v17.8H, v2.H[1]
        ldr q14, [x3, #176]
        mls v25.8H, v20.8H, v0.H[0]
        ldr q2, [x14, #336]
        sub v29.8H, v3.8H, v27.8H
        mls v11.8H, v21.8H, v0.H[0]
        add v13.8H, v3.8H, v27.8H
        ldr q6, [x14, #352]
        ldr q12, [x14, #368]
        sqdmulh v26.8H, v13.8H, v0.H[1]
        sub v3.8H, v7.8H, v25.8H
        sqrdmulh v17.8H, v2.8H, v14.H[0]
        add v27.8H, v7.8H, v25.8H
        str q11, [x2, #432]
        sqdmulh v21.8H, v29.8H, v0.H[1]
        ldr q7, [x3, #160]
        sqrdmulh v18.8H, v12.8H, v14.H[0]
        mul v10.8H, v2.8H, v7.H[0]
        mul v12.8H, v12.8H, v7.H[0]
        srshr v11.8H, v21.8H, #11
        ldr q25, [x14, #320]
        mls v12.8H, v18.8H, v0.H[0]
        mls v10.8H, v17.8H, v0.H[0]
        mls v1.8H, v8.8H, v0.H[0]
        add v23.8H, v6.8H, v12.8H
        sqdmulh v21.8H, v3.8H, v0.H[1]
        sqrdmulh v5.8H, v23.8H, v14.H[1]
        sub v18.8H, v6.8H, v12.8H
        str q1, [x2, #48]
        mul v16.8H, v23.8H, v7.H[1]
        mul v17.8H, v18.8H, v7.H[2]
        mls v16.8H, v5.8H, v0.H[0]
        srshr v9.8H, v21.8H, #11
        sqrdmulh v20.8H, v18.8H, v14.H[2]
        sub v5.8H, v25.8H, v10.8H
        mls v29.8H, v11.8H, v0.H[0]
        add v24.8H, v25.8H, v10.8H
        ldr q7, [x3, #192]
        srshr v30.8H, v26.8H, #11
        mls v3.8H, v9.8H, v0.H[0]
        add v15.8H, v24.8H, v16.8H
        ldr q8, [x14, #432]
        mls v17.8H, v20.8H, v0.H[0]
        ldr q6, [x3, #208]
        sub v10.8H, v24.8H, v16.8H
        ldr q2, [x14, #384]
        str q29, [x2, #448]
        mls v13.8H, v30.8H, v0.H[0]
        ldr q4, [x14, #416]
        str q3, [x2, #320]
        sqdmulh v25.8H, v27.8H, v0.H[1]
        srshr v25.8H, v25.8H, #11
        sqdmulh v18.8H, v15.8H, v0.H[1]
        str q13, [x2, #192]
        ldr q29, [x14, #400]
        sqdmulh v1.8H, v10.8H, v0.H[1]
        add v3.8H, v5.8H, v17.8H
        mls v27.8H, v25.8H, v0.H[0]
        srshr v9.8H, v18.8H, #11
        sub v5.8H, v5.8H, v17.8H
        sqrdmulh v13.8H, v29.8H, v6.H[0]
        srshr v30.8H, v1.8H, #11
        sqrdmulh v28.8H, v8.8H, v6.H[0]
        mul v1.8H, v29.8H, v7.H[0]
        mls v1.8H, v13.8H, v0.H[0]
        sqdmulh v21.8H, v3.8H, v0.H[1]
        sqdmulh v20.8H, v5.8H, v0.H[1]
        add v12.8H, v2.8H, v1.8H
        srshr v11.8H, v21.8H, #11
        mul v21.8H, v8.8H, v7.H[0]
        str q27, [x2, #64]
        srshr v27.8H, v20.8H, #11
        sub v29.8H, v2.8H, v1.8H
        mls v21.8H, v28.8H, v0.H[0]
        mls v3.8H, v11.8H, v0.H[0]
        mls v15.8H, v9.8H, v0.H[0]
        sub v28.8H, v4.8H, v21.8H
        add v8.8H, v4.8H, v21.8H
        mls v5.8H, v27.8H, v0.H[0]
        str q3, [x2, #208]
        sqrdmulh v13.8H, v28.8H, v6.H[2]
        str q15, [x2, #80]
        sqrdmulh v25.8H, v8.8H, v6.H[1]
        mul v1.8H, v28.8H, v7.H[2]
        mls v1.8H, v13.8H, v0.H[0]
        mls v10.8H, v30.8H, v0.H[0]
        ldr q22, [x14, #496]
        add v3.8H, v29.8H, v1.8H
        str q5, [x2, #464]
        sub v5.8H, v29.8H, v1.8H
        mul v1.8H, v8.8H, v7.H[1]
        ldr q15, [x3, #240]
        ldr q29, [x14, #464]
        mls v1.8H, v25.8H, v0.H[0]
        ldr q11, [x3, #224]
        str q10, [x2, #336]
        ldr q21, [x14, #480]
        ldr q17, [x14, #448]
        sqdmulh v8.8H, v3.8H, v0.H[1]
        sqrdmulh v25.8H, v22.8H, v15.H[0]
        sub v30.8H, v12.8H, v1.8H
        add v18.8H, v12.8H, v1.8H
        mul v7.8H, v22.8H, v11.H[0]
        srshr v16.8H, v8.8H, #11
        mls v7.8H, v25.8H, v0.H[0]
        sqrdmulh v10.8H, v29.8H, v15.H[0]
        mul v1.8H, v29.8H, v11.H[0]
        add v13.8H, v21.8H, v7.8H
        sub v20.8H, v21.8H, v7.8H
        sqdmulh v22.8H, v18.8H, v0.H[1]
        mul v12.8H, v20.8H, v11.H[2]
        sqrdmulh v24.8H, v13.8H, v15.H[1]
        srshr v27.8H, v22.8H, #11
        sqrdmulh v29.8H, v20.8H, v15.H[2]
        mls v1.8H, v10.8H, v0.H[0]
        mls v3.8H, v16.8H, v0.H[0]
        mul v7.8H, v13.8H, v11.H[1]
        sub v13.8H, v17.8H, v1.8H
        add v15.8H, v17.8H, v1.8H
        sqdmulh v20.8H, v5.8H, v0.H[1]
        str q3, [x2, #224]
        sqdmulh v22.8H, v30.8H, v0.H[1]
        mls v12.8H, v29.8H, v0.H[0]
        mls v7.8H, v24.8H, v0.H[0]
        srshr v24.8H, v20.8H, #11
        mls v18.8H, v27.8H, v0.H[0]
        sub v11.8H, v13.8H, v12.8H
        add v3.8H, v13.8H, v12.8H
        mls v5.8H, v24.8H, v0.H[0]
        sub v24.8H, v15.8H, v7.8H
        add v20.8H, v15.8H, v7.8H
        sqdmulh v1.8H, v11.8H, v0.H[1]
        str q18, [x2, #96]
        sqdmulh v17.8H, v3.8H, v0.H[1]
        str q5, [x2, #480]
        srshr v5.8H, v22.8H, #11
        sqdmulh v13.8H, v20.8H, v0.H[1]
        srshr v6.8H, v1.8H, #11
        sqdmulh v1.8H, v24.8H, v0.H[1]
        srshr v29.8H, v17.8H, #11
        mls v30.8H, v5.8H, v0.H[0]
        srshr v9.8H, v13.8H, #11
        mls v11.8H, v6.8H, v0.H[0]
        srshr v21.8H, v1.8H, #11
        mls v3.8H, v29.8H, v0.H[0]
        str q30, [x2, #352]
        mls v20.8H, v9.8H, v0.H[0]
        str q11, [x2, #496]
        mls v24.8H, v21.8H, v0.H[0]
        str q3, [x2, #240]
        str q20, [x2, #112]
        str q24, [x2, #368]
.endm

.macro POST_STORE_PTR xvec, ptr, off_lo, off_hi
    POST_STORE_PTR_BRANCHFOLD \xvec, \ptr, \off_lo, \off_hi
.endm

.macro LOAD_BRANCHFOLD_CONSTS
    ldr     q10, [x3, #0]     // low normal constants
    ldr     q11, [x3, #16]    // low sqrdmulh precompute
    ldr     q12, [x3, #32]    // high normal constants
    ldr     q13, [x3, #48]    // high sqrdmulh precompute
    add     x3, x3, #64
.endm

.macro POST_STORE_PTR_BRANCHFOLD xvec, ptr, off_lo, off_hi
    /*
     * Branch-constant folded final merge:
     *
     *   out_low =
     *     b0 * F0^k * (1 - ZMINUSZ5INV) / 192
     *   + b1 * F1^k * (1 + ZMINUSZ5INV) / 192
     *
     *   out_high =
     *     b0 * F0^k * ZMINUSZ5INV / 96
     *   - b1 * F1^k * ZMINUSZ5INV / 96
     *
     * That folds untwist, branch merge, and final scaling into two fqmul
     * operations plus cross-half adds.  The unreduced branchfold form changes
     * representatives and is not safe for poly_crepmod3.  Production therefore
     * performs final Barrett reductions here; this matches the exact C-reference
     * output for forward-produced GT inputs.
     */
    LOAD_BRANCHFOLD_CONSTS

    sqrdmulh v17.8h, \xvec\().8h, v11.8h
    mul      v18.8h, \xvec\().8h, v10.8h
    mls      v18.8h, v17.8h, v0.h[0]
    ext      v19.16b, v18.16b, v18.16b, #8
    add      v21.8h, v18.8h, v19.8h

    sqrdmulh v20.8h, \xvec\().8h, v13.8h
    mul      v23.8h, \xvec\().8h, v12.8h
    mls      v23.8h, v20.8h, v0.h[0]
    ext      v24.16b, v23.16b, v23.16b, #8
    add      v23.8h, v23.8h, v24.8h

    BARRETT_REDUCE v21, v20
    BARRETT_REDUCE v23, v20

    str      d21, [\ptr, #\off_lo]
    str      d23, [\ptr, #\off_hi]
.endm

.macro FUSED_POST_STRIPE ptr0, off0_lo, off0_hi, ptr1, off1_lo, off1_hi, ptr2, off2_lo, off2_hi
    ldr q1, [x8]
    ldr q2, [x9]
    ldr q3, [x10]
    add x8, x8, #16
    add x9, x9, #16
    add x10, x10, #16

    sub      v4.8h, v3.8h, v2.8h
    sqrdmulh v5.8h, v4.8h, v0.h[3]
    mul      v6.8h, v4.8h, v0.h[2]
    mls      v6.8h, v5.8h, v0.h[0]

    /*
     * Production branchfold path skips the three immediate post-DFT3 Barrett
     * reductions and relies on the branchfold final-output reductions below.
     * This is only valid because the full KEM path has been checked for the
     * signed representative convention consumed by poly_crepmod3.
     */
    add      v7.8h, v1.8h, v2.8h
    add      v7.8h, v7.8h, v3.8h

    sub      v8.8h, v1.8h, v2.8h
    add      v8.8h, v8.8h, v6.8h

    sub      v9.8h, v1.8h, v3.8h
    sub      v9.8h, v9.8h, v6.8h

    POST_STORE_PTR v7, \ptr0, \off0_lo, \off0_hi
    POST_STORE_PTR v8, \ptr1, \off1_lo, \off1_hi
    POST_STORE_PTR v9, \ptr2, \off2_lo, \off2_hi
.endm

.macro RUN_FUSED_POST_STRIPE ptr0, off0_lo, off0_hi, ptr1, off1_lo, off1_hi, ptr2, off2_lo, off2_hi
    FUSED_POST_STRIPE \ptr0, \off0_lo, \off0_hi, \ptr1, \off1_lo, \off1_hi, \ptr2, \off2_lo, \off2_hi
.endm

.macro RUN_FUSED_POST_3STRIPE_GROUP
    RUN_FUSED_POST_STRIPE x11, 0, 768, x12, 0, 768, x13, 0, 768
    RUN_FUSED_POST_STRIPE x13, 8, 776, x11, 8, 776, x12, 8, 776
    RUN_FUSED_POST_STRIPE x12, 16, 784, x13, 16, 784, x11, 16, 784
.endm

.macro RUN_FUSED_POST_3STRIPE_LOOP loop_label
    mov x5, #10
\loop_label:
    RUN_FUSED_POST_3STRIPE_GROUP
    add x11, x11, #24
    add x12, x12, #24
    add x13, x13, #24
    subs x5, x5, #1
    b.ne \loop_label\()b
    RUN_FUSED_POST_STRIPE x11, 0, 768, x12, 0, 768, x13, 0, 768
    RUN_FUSED_POST_STRIPE x13, 8, 776, x11, 8, 776, x12, 8, 776
.endm

.macro RUN_FUSED_POST_LOOP loop_label
    RUN_FUSED_POST_3STRIPE_LOOP \loop_label
.endm

.equ INVNTT_SIMD_SAVE_OFFSET, 2080
.equ INVNTT_STACK_SIZE, 2144
.equ INVNTT_SAVED_X0_OFFSET, (INVNTT_STACK_SIZE + 8)

.macro INVNTT_SAVE_CALLEE_SAVED_SIMD
    add x16, sp, #INVNTT_SIMD_SAVE_OFFSET
    stp d8, d9, [x16, #0]
    stp d10, d11, [x16, #16]
    stp d12, d13, [x16, #32]
    stp d14, d15, [x16, #48]
.endm

.macro INVNTT_RESTORE_CALLEE_SAVED_SIMD
    add x16, sp, #INVNTT_SIMD_SAVE_OFFSET
    ldp d8, d9, [x16, #0]
    ldp d10, d11, [x16, #16]
    ldp d12, d13, [x16, #32]
    ldp d14, d15, [x16, #48]
.endm

#ifndef __APPLE__
	.weak poly_invntt
	.weak _poly_invntt
#endif
	.global poly_invntt
	.global _poly_invntt
		.global gt_block_major_poly_invntt
		.global _gt_block_major_poly_invntt

poly_invntt:
_poly_invntt:
gt_block_major_poly_invntt:
_gt_block_major_poly_invntt:
    stp x30, x0, [sp, #-16]!
    sub sp, sp, #INVNTT_STACK_SIZE
    INVNTT_SAVE_CALLEE_SAVED_SIMD

    adr x3, inv_consts
    ldr q0, [x3]

    add x3, x1, #0
    add x4, x1, #768
    add x2, sp, #32
    /* The final branchfold table is fixed for inputs carrying R^-1. */
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW0
    /*
     * live-in: x14 = stage123 stripe scratch at sp+1568,
     *          x2 = row0 row-buffer base at sp+32,
     *          q0 = q / Barrett constants.
     * live-out: row0 natural-order stage45 output at [x2].
     */
    bl .Linvntt32_stage45_scratch_row_helper

    add x3, x1, #0
    add x4, x1, #768
    add x2, sp, #544
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW1
    /*
     * live-in: x14 = stage123 stripe scratch at sp+1568,
     *          x2 = row1 row-buffer base at sp+544,
     *          q0 = q / Barrett constants.
     * live-out: row1 natural-order stage45 output at [x2].
     */
    bl .Linvntt32_stage45_scratch_row_helper

    add x3, x1, #0
    add x4, x1, #768
    add x2, sp, #1056
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW2
    /*
     * live-in: x14 = stage123 stripe scratch at sp+1568,
     *          x2 = row2 row-buffer base at sp+1056,
     *          q0 = q / Barrett constants.
     * live-out: row2 natural-order stage45 output at [x2].
     */
    bl .Linvntt32_stage45_scratch_row_helper
    b L_invntt_post_tail

	L_invntt_post_tail:
    adr x3, inv_consts
    ldr q15, [x3, #16]
    ldr x0, [sp, #INVNTT_SAVED_X0_OFFSET]
    add x8, sp, #32
    add x9, sp, #544
    add x10, sp, #1056
    adr x3, inv_branchfold_vecs

    add x11, x0, #0
    add x12, x0, #512
    add x13, x0, #256
    RUN_FUSED_POST_LOOP 4

    INVNTT_RESTORE_CALLEE_SAVED_SIMD
    /* P0-B: erase 2,144 bytes of inverse-NTT scratch. */
    movi v0.16b, #0
    mov x16, sp
    mov x17, #134
.Lp0b_invntt_clear:
    str q0, [x16], #16
    subs x17, x17, #1
    b.ne .Lp0b_invntt_clear
    add sp, sp, #INVNTT_STACK_SIZE
    ldp x30, x0, [sp]
    stp xzr, xzr, [sp]
    add sp, sp, #16
    ret

.p2align 4
.Linvntt32_stage45_scratch_row_helper:
    RUN_INVNTT32_STAGE45_SCRATCH_ROW
    ret

.align 4
inv_consts:
    .hword 3457, 19412, -723, -6853, 1634, 15488, -18, -171
    .hword -36, -341, 1701, 16123, 0, 0, 0, 0

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

.align 4
inv_branchfold_vecs:
/* Generated branchfold constants for inverse NTT inputs with an extra R^-1 factor.
 * Normal multipliers are the production branchfold constants multiplied
 * by R=2^16 mod q, so the final post stage returns normal R^0 output.
 * Order must match POST_STORE_PTR calls.
 */
    // k=0: low/high branch-fold constants for R^-1 input
    .hword    332,    332,    332,    332,   1503,   1503,   1503,   1503
    .hword   3147,   3147,   3147,   3147,  14247,  14247,  14247,  14247
    .hword   1171,   1171,   1171,   1171,  -1171,  -1171,  -1171,  -1171
    .hword  11100,  11100,  11100,  11100, -11100, -11100, -11100, -11100
    // k=64: low/high branch-fold constants for R^-1 input
    .hword    -82,    -82,    -82,    -82,    913,    913,    913,    913
    .hword   -777,   -777,   -777,   -777,   8654,   8654,   8654,   8654
    .hword   -435,   -435,   -435,   -435,    188,    188,    188,    188
    .hword  -4123,  -4123,  -4123,  -4123,   1782,   1782,   1782,   1782
    // k=32: low/high branch-fold constants for R^-1 input
    .hword    913,    913,    913,    913,    -82,    -82,    -82,    -82
    .hword   8654,   8654,   8654,   8654,   -777,   -777,   -777,   -777
    .hword  -1101,  -1101,  -1101,  -1101,    517,    517,    517,    517
    .hword -10436, -10436, -10436, -10436,   4901,   4901,   4901,   4901
    // k=33: low/high branch-fold constants for R^-1 input
    .hword  -1631,  -1631,  -1631,  -1631,   1653,   1653,   1653,   1653
    .hword -15460, -15460, -15460, -15460,  15668,  15668,  15668,  15668
    .hword   1255,   1255,   1255,   1255,   1003,   1003,   1003,   1003
    .hword  11896,  11896,  11896,  11896,   9507,   9507,   9507,   9507
    // k=1: low/high branch-fold constants for R^-1 input
    .hword    664,    664,    664,    664,  -1504,  -1504,  -1504,  -1504
    .hword   6294,   6294,   6294,   6294, -14256, -14256, -14256, -14256
    .hword  -1115,  -1115,  -1115,  -1115,  -1563,  -1563,  -1563,  -1563
    .hword -10569, -10569, -10569, -10569, -14815, -14815, -14815, -14815
    // k=65: low/high branch-fold constants for R^-1 input
    .hword   -164,   -164,   -164,   -164,   -656,   -656,   -656,   -656
    .hword  -1555,  -1555,  -1555,  -1555,  -6218,  -6218,  -6218,  -6218
    .hword   -870,   -870,   -870,   -870,    679,    679,    679,    679
    .hword  -8247,  -8247,  -8247,  -8247,   6436,   6436,   6436,   6436
    // k=66: low/high branch-fold constants for R^-1 input
    .hword   -328,   -328,   -328,   -328,   -604,   -604,   -604,   -604
    .hword  -3109,  -3109,  -3109,  -3109,  -5725,  -5725,  -5725,  -5725
    .hword   1717,   1717,   1717,   1717,   1110,   1110,   1110,   1110
    .hword  16275,  16275,  16275,  16275,  10521,  10521,  10521,  10521
    // k=34: low/high branch-fold constants for R^-1 input
    .hword    195,    195,    195,    195,  -1661,  -1661,  -1661,  -1661
    .hword   1848,   1848,   1848,   1848, -15744, -15744, -15744, -15744
    .hword   -947,   -947,   -947,   -947,   1324,   1324,   1324,   1324
    .hword  -8976,  -8976,  -8976,  -8976,  12550,  12550,  12550,  12550
    // k=2: low/high branch-fold constants for R^-1 input
    .hword   1328,   1328,   1328,   1328,   1482,   1482,   1482,   1482
    .hword  12588,  12588,  12588,  12588,  14047,  14047,  14047,  14047
    .hword   1227,   1227,   1227,   1227,    184,    184,    184,    184
    .hword  11630,  11630,  11630,  11630,   1744,   1744,   1744,   1744
    // k=3: low/high branch-fold constants for R^-1 input
    .hword   -801,   -801,   -801,   -801,   1491,   1491,   1491,   1491
    .hword  -7592,  -7592,  -7592,  -7592,  14133,  14133,  14133,  14133
    .hword  -1003,  -1003,  -1003,  -1003,    591,    591,    591,    591
    .hword  -9507,  -9507,  -9507,  -9507,   5602,   5602,   5602,   5602
    // k=67: low/high branch-fold constants for R^-1 input
    .hword   -656,   -656,   -656,   -656,    540,    540,    540,    540
    .hword  -6218,  -6218,  -6218,  -6218,   5119,   5119,   5119,   5119
    .hword    -23,    -23,    -23,    -23,    221,    221,    221,    221
    .hword   -218,   -218,   -218,   -218,   2095,   2095,   2095,   2095
    // k=35: low/high branch-fold constants for R^-1 input
    .hword    390,    390,    390,    390,   1485,   1485,   1485,   1485
    .hword   3697,   3697,   3697,   3697,  14076,  14076,  14076,  14076
    .hword   1563,   1563,   1563,   1563,   1472,   1472,   1472,   1472
    .hword  14815,  14815,  14815,  14815,  13953,  13953,  13953,  13953
    // k=36: low/high branch-fold constants for R^-1 input
    .hword    780,    780,    780,    780,   1557,   1557,   1557,   1557
    .hword   7393,   7393,   7393,   7393,  14758,  14758,  14758,  14758
    .hword   -331,   -331,   -331,   -331,   1271,   1271,   1271,   1271
    .hword  -3137,  -3137,  -3137,  -3137,  12047,  12047,  12047,  12047
    // k=4: low/high branch-fold constants for R^-1 input
    .hword  -1602,  -1602,  -1602,  -1602,   1689,   1689,   1689,   1689
    .hword -15185, -15185, -15185, -15185,  16010,  16010,  16010,  16010
    .hword   1451,   1451,   1451,   1451,   -826,   -826,   -826,   -826
    .hword  13754,  13754,  13754,  13754,  -7829,  -7829,  -7829,  -7829
    // k=68: low/high branch-fold constants for R^-1 input
    .hword  -1312,  -1312,  -1312,  -1312,   1509,   1509,   1509,   1509
    .hword -12436, -12436, -12436, -12436,  14303,  14303,  14303,  14303
    .hword    -46,    -46,    -46,    -46,   1405,   1405,   1405,   1405
    .hword   -436,   -436,   -436,   -436,  13318,  13318,  13318,  13318
    // k=69: low/high branch-fold constants for R^-1 input
    .hword    833,    833,    833,    833,  -1372,  -1372,  -1372,  -1372
    .hword   7896,   7896,   7896,   7896, -13005, -13005, -13005, -13005
    .hword    -92,    -92,    -92,    -92,   -203,   -203,   -203,   -203
    .hword   -872,   -872,   -872,   -872,  -1924,  -1924,  -1924,  -1924
    // k=37: low/high branch-fold constants for R^-1 input
    .hword   1560,   1560,   1560,   1560,   -316,   -316,   -316,   -316
    .hword  14787,  14787,  14787,  14787,  -2995,  -2995,  -2995,  -2995
    .hword   -662,   -662,   -662,   -662,    306,    306,    306,    306
    .hword  -6275,  -6275,  -6275,  -6275,   2900,   2900,   2900,   2900
    // k=5: low/high branch-fold constants for R^-1 input
    .hword    253,    253,    253,    253,   -869,   -869,   -869,   -869
    .hword   2398,   2398,   2398,   2398,  -8237,  -8237,  -8237,  -8237
    .hword   -555,   -555,   -555,   -555,   -887,   -887,   -887,   -887
    .hword  -5261,  -5261,  -5261,  -5261,  -8408,  -8408,  -8408,  -8408
    // k=6: low/high branch-fold constants for R^-1 input
    .hword    506,    506,    506,    506,   1624,   1624,   1624,   1624
    .hword   4796,   4796,   4796,   4796,  15393,  15393,  15393,  15393
    .hword  -1110,  -1110,  -1110,  -1110,   1228,   1228,   1228,   1228
    .hword -10521, -10521, -10521, -10521,  11640,  11640,  11640,  11640
    // k=70: low/high branch-fold constants for R^-1 input
    .hword   1666,   1666,   1666,   1666,    929,    929,    929,    929
    .hword  15792,  15792,  15792,  15792,   8806,   8806,   8806,   8806
    .hword   -184,   -184,   -184,   -184,  -1009,  -1009,  -1009,  -1009
    .hword  -1744,  -1744,  -1744,  -1744,  -9564,  -9564,  -9564,  -9564
    // k=38: low/high branch-fold constants for R^-1 input
    .hword   -337,   -337,   -337,   -337,    -38,    -38,    -38,    -38
    .hword  -3194,  -3194,  -3194,  -3194,   -360,   -360,   -360,   -360
    .hword  -1324,  -1324,  -1324,  -1324,   -182,   -182,   -182,   -182
    .hword -12550, -12550, -12550, -12550,  -1725,  -1725,  -1725,  -1725
    // k=39: low/high branch-fold constants for R^-1 input
    .hword   -674,   -674,   -674,   -674,   -836,   -836,   -836,   -836
    .hword  -6389,  -6389,  -6389,  -6389,  -7924,  -7924,  -7924,  -7924
    .hword    809,    809,    809,    809,   -547,   -547,   -547,   -547
    .hword   7668,   7668,   7668,   7668,  -5185,  -5185,  -5185,  -5185
    // k=7: low/high branch-fold constants for R^-1 input
    .hword   1012,   1012,   1012,   1012,   1158,   1158,   1158,   1158
    .hword   9592,   9592,   9592,   9592,  10976,  10976,  10976,  10976
    .hword   1237,   1237,   1237,   1237,   -640,   -640,   -640,   -640
    .hword  11725,  11725,  11725,  11725,  -6066,  -6066,  -6066,  -6066
    // k=71: low/high branch-fold constants for R^-1 input
    .hword   -125,   -125,   -125,   -125,   -304,   -304,   -304,   -304
    .hword  -1185,  -1185,  -1185,  -1185,  -2882,  -2882,  -2882,  -2882
    .hword   -368,   -368,   -368,   -368,  -1456,  -1456,  -1456,  -1456
    .hword  -3488,  -3488,  -3488,  -3488, -13801, -13801, -13801, -13801
    // k=72: low/high branch-fold constants for R^-1 input
    .hword   -250,   -250,   -250,   -250,    226,    226,    226,    226
    .hword  -2370,  -2370,  -2370,  -2370,   2142,   2142,   2142,   2142
    .hword   -736,   -736,   -736,   -736,   -919,   -919,   -919,   -919
    .hword  -6976,  -6976,  -6976,  -6976,  -8711,  -8711,  -8711,  -8711
    // k=40: low/high branch-fold constants for R^-1 input
    .hword  -1348,  -1348,  -1348,  -1348,  -1107,  -1107,  -1107,  -1107
    .hword -12777, -12777, -12777, -12777, -10493, -10493, -10493, -10493
    .hword   1618,   1618,   1618,   1618,  -1663,  -1663,  -1663,  -1663
    .hword  15337,  15337,  15337,  15337, -15763, -15763, -15763, -15763
    // k=8: low/high branch-fold constants for R^-1 input
    .hword  -1433,  -1433,  -1433,  -1433,   1277,   1277,   1277,   1277
    .hword -13583, -13583, -13583, -13583,  12104,  12104,  12104,  12104
    .hword   -983,   -983,   -983,   -983,   -252,   -252,   -252,   -252
    .hword  -9318,  -9318,  -9318,  -9318,  -2389,  -2389,  -2389,  -2389
    // k=9: low/high branch-fold constants for R^-1 input
    .hword    591,    591,    591,    591,    438,    438,    438,    438
    .hword   5602,   5602,   5602,   5602,   4152,   4152,   4152,   4152
    .hword   1491,   1491,   1491,   1491,   1370,   1370,   1370,   1370
    .hword  14133,  14133,  14133,  14133,  12986,  12986,  12986,  12986
    // k=73: low/high branch-fold constants for R^-1 input
    .hword   -500,   -500,   -500,   -500,   1515,   1515,   1515,   1515
    .hword  -4739,  -4739,  -4739,  -4739,  14360,  14360,  14360,  14360
    .hword  -1472,  -1472,  -1472,  -1472,    524,    524,    524,    524
    .hword -13953, -13953, -13953, -13953,   4967,   4967,   4967,   4967
    // k=41: low/high branch-fold constants for R^-1 input
    .hword    761,    761,    761,    761,   -155,   -155,   -155,   -155
    .hword   7213,   7213,   7213,   7213,  -1469,  -1469,  -1469,  -1469
    .hword   -221,   -221,   -221,   -221,   1441,   1441,   1441,   1441
    .hword  -2095,  -2095,  -2095,  -2095,  13659,  13659,  13659,  13659
    // k=42: low/high branch-fold constants for R^-1 input
    .hword   1522,   1522,   1522,   1522,     47,     47,     47,     47
    .hword  14427,  14427,  14427,  14427,    446,    446,    446,    446
    .hword   -442,   -442,   -442,   -442,    589,    589,    589,    589
    .hword  -4190,  -4190,  -4190,  -4190,   5583,   5583,   5583,   5583
    // k=10: low/high branch-fold constants for R^-1 input
    .hword   1182,   1182,   1182,   1182,   -735,   -735,   -735,   -735
    .hword  11204,  11204,  11204,  11204,  -6967,  -6967,  -6967,  -6967
    .hword   -475,   -475,   -475,   -475,   -973,   -973,   -973,   -973
    .hword  -4502,  -4502,  -4502,  -4502,  -9223,  -9223,  -9223,  -9223
    // k=74: low/high branch-fold constants for R^-1 input
    .hword  -1000,  -1000,  -1000,  -1000,  -1240,  -1240,  -1240,  -1240
    .hword  -9479,  -9479,  -9479,  -9479, -11754, -11754, -11754, -11754
    .hword    513,    513,    513,    513,   1157,   1157,   1157,   1157
    .hword   4863,   4863,   4863,   4863,  10967,  10967,  10967,  10967
    // k=75: low/high branch-fold constants for R^-1 input
    .hword   1457,   1457,   1457,   1457,    376,    376,    376,    376
    .hword  13811,  13811,  13811,  13811,   3564,   3564,   3564,   3564
    .hword   1026,   1026,   1026,   1026,   1255,   1255,   1255,   1255
    .hword   9725,   9725,   9725,   9725,  11896,  11896,  11896,  11896
    // k=43: low/high branch-fold constants for R^-1 input
    .hword   -413,   -413,   -413,   -413,   1034,   1034,   1034,   1034
    .hword  -3915,  -3915,  -3915,  -3915,   9801,   9801,   9801,   9801
    .hword   -884,   -884,   -884,   -884,   -870,   -870,   -870,   -870
    .hword  -8379,  -8379,  -8379,  -8379,  -8247,  -8247,  -8247,  -8247
    // k=11: low/high branch-fold constants for R^-1 input
    .hword  -1093,  -1093,  -1093,  -1093,   1115,   1115,   1115,   1115
    .hword -10360, -10360, -10360, -10360,  10569,  10569,  10569,  10569
    .hword   -950,   -950,   -950,   -950,   -664,   -664,   -664,   -664
    .hword  -9005,  -9005,  -9005,  -9005,  -6294,  -6294,  -6294,  -6294
    // k=12: low/high branch-fold constants for R^-1 input
    .hword   1271,   1271,   1271,   1271,    331,    331,    331,    331
    .hword  12047,  12047,  12047,  12047,   3137,   3137,   3137,   3137
    .hword   1557,   1557,   1557,   1557,   -780,   -780,   -780,   -780
    .hword  14758,  14758,  14758,  14758,  -7393,  -7393,  -7393,  -7393
    // k=76: low/high branch-fold constants for R^-1 input
    .hword   -543,   -543,   -543,   -543,   1358,   1358,   1358,   1358
    .hword  -5147,  -5147,  -5147,  -5147,  12872,  12872,  12872,  12872
    .hword  -1405,  -1405,  -1405,  -1405,    -46,    -46,    -46,    -46
    .hword -13318, -13318, -13318, -13318,   -436,   -436,   -436,   -436
    // k=44: low/high branch-fold constants for R^-1 input
    .hword   -826,   -826,   -826,   -826,  -1451,  -1451,  -1451,  -1451
    .hword  -7829,  -7829,  -7829,  -7829, -13754, -13754, -13754, -13754
    .hword   1689,   1689,   1689,   1689,   1602,   1602,   1602,   1602
    .hword  16010,  16010,  16010,  16010,  15185,  15185,  15185,  15185
    // k=45: low/high branch-fold constants for R^-1 input
    .hword  -1652,  -1652,  -1652,  -1652,   -809,   -809,   -809,   -809
    .hword -15659, -15659, -15659, -15659,  -7668,  -7668,  -7668,  -7668
    .hword    -79,    -79,    -79,    -79,    674,    674,    674,    674
    .hword   -749,   -749,   -749,   -749,   6389,   6389,   6389,   6389
    // k=13: low/high branch-fold constants for R^-1 input
    .hword   -915,   -915,   -915,   -915,    368,    368,    368,    368
    .hword  -8673,  -8673,  -8673,  -8673,   3488,   3488,   3488,   3488
    .hword   -343,   -343,   -343,   -343,    125,    125,    125,    125
    .hword  -3251,  -3251,  -3251,  -3251,   1185,   1185,   1185,   1185
    // k=77: low/high branch-fold constants for R^-1 input
    .hword  -1086,  -1086,  -1086,  -1086,  -1237,  -1237,  -1237,  -1237
    .hword -10294, -10294, -10294, -10294, -11725, -11725, -11725, -11725
    .hword    647,    647,    647,    647,  -1012,  -1012,  -1012,  -1012
    .hword   6133,   6133,   6133,   6133,  -9592,  -9592,  -9592,  -9592
    // k=78: low/high branch-fold constants for R^-1 input
    .hword   1285,   1285,   1285,   1285,    442,    442,    442,    442
    .hword  12180,  12180,  12180,  12180,   4190,   4190,   4190,   4190
    .hword   1294,   1294,   1294,   1294,  -1522,  -1522,  -1522,  -1522
    .hword  12265,  12265,  12265,  12265, -14427, -14427, -14427, -14427
    // k=46: low/high branch-fold constants for R^-1 input
    .hword    153,    153,    153,    153,   -513,   -513,   -513,   -513
    .hword   1450,   1450,   1450,   1450,  -4863,  -4863,  -4863,  -4863
    .hword   -158,   -158,   -158,   -158,   1000,   1000,   1000,   1000
    .hword  -1498,  -1498,  -1498,  -1498,   9479,   9479,   9479,   9479
    // k=14: low/high branch-fold constants for R^-1 input
    .hword   1627,   1627,   1627,   1627,   1182,   1182,   1182,   1182
    .hword  15422,  15422,  15422,  15422,  11204,  11204,  11204,  11204
    .hword   -686,   -686,   -686,   -686,   -707,   -707,   -707,   -707
    .hword  -6502,  -6502,  -6502,  -6502,  -6701,  -6701,  -6701,  -6701
    // k=15: low/high branch-fold constants for R^-1 input
    .hword   -203,   -203,   -203,   -203,  -1652,  -1652,  -1652,  -1652
    .hword  -1924,  -1924,  -1924,  -1924, -15659, -15659, -15659, -15659
    .hword  -1372,  -1372,  -1372,  -1372,  -1726,  -1726,  -1726,  -1726
    .hword -13005, -13005, -13005, -13005, -16360, -16360, -16360, -16360
    // k=79: low/high branch-fold constants for R^-1 input
    .hword   -887,   -887,   -887,   -887,   -647,   -647,   -647,   -647
    .hword  -8408,  -8408,  -8408,  -8408,  -6133,  -6133,  -6133,  -6133
    .hword   -869,   -869,   -869,   -869,   1086,   1086,   1086,   1086
    .hword  -8237,  -8237,  -8237,  -8237,  10294,  10294,  10294,  10294
    // k=47: low/high branch-fold constants for R^-1 input
    .hword    306,    306,    306,    306,   -915,   -915,   -915,   -915
    .hword   2900,   2900,   2900,   2900,  -8673,  -8673,  -8673,  -8673
    .hword   -316,   -316,   -316,   -316,   1258,   1258,   1258,   1258
    .hword  -2995,  -2995,  -2995,  -2995,  11924,  11924,  11924,  11924
    // k=48: low/high branch-fold constants for R^-1 input
    .hword    612,    612,    612,    612,    612,    612,    612,    612
    .hword   5801,   5801,   5801,   5801,   5801,   5801,   5801,   5801
    .hword   -632,   -632,   -632,   -632,     20,     20,     20,     20
    .hword  -5991,  -5991,  -5991,  -5991,    190,    190,    190,    190
    // k=16: low/high branch-fold constants for R^-1 input
    .hword   -406,   -406,   -406,   -406,   1683,   1683,   1683,   1683
    .hword  -3848,  -3848,  -3848,  -3848,  15953,  15953,  15953,  15953
    .hword    713,    713,    713,    713,     55,     55,     55,     55
    .hword   6758,   6758,   6758,   6758,    521,    521,    521,    521
    // k=80: low/high branch-fold constants for R^-1 input
    .hword   1683,   1683,   1683,   1683,   -406,   -406,   -406,   -406
    .hword  15953,  15953,  15953,  15953,  -3848,  -3848,  -3848,  -3848
    .hword   1719,   1719,   1719,   1719,   -307,   -307,   -307,   -307
    .hword  16294,  16294,  16294,  16294,  -2910,  -2910,  -2910,  -2910
    // k=81: low/high branch-fold constants for R^-1 input
    .hword    -91,    -91,    -91,    -91,   1439,   1439,   1439,   1439
    .hword   -863,   -863,   -863,   -863,  13640,  13640,  13640,  13640
    .hword    -19,    -19,    -19,    -19,    160,    160,    160,    160
    .hword   -180,   -180,   -180,   -180,   1517,   1517,   1517,   1517
    // k=49: low/high branch-fold constants for R^-1 input
    .hword   1224,   1224,   1224,   1224,   -364,   -364,   -364,   -364
    .hword  11602,  11602,  11602,  11602,  -3450,  -3450,  -3450,  -3450
    .hword  -1264,  -1264,  -1264,  -1264,    440,    440,    440,    440
    .hword -11981, -11981, -11981, -11981,   4171,   4171,   4171,   4171
    // k=17: low/high branch-fold constants for R^-1 input
    .hword   -812,   -812,   -812,   -812,  -1001,  -1001,  -1001,  -1001
    .hword  -7697,  -7697,  -7697,  -7697,  -9488,  -9488,  -9488,  -9488
    .hword   1426,   1426,   1426,   1426,   1210,   1210,   1210,   1210
    .hword  13517,  13517,  13517,  13517,  11469,  11469,  11469,  11469
    // k=18: low/high branch-fold constants for R^-1 input
    .hword  -1624,  -1624,  -1624,  -1624,  -1280,  -1280,  -1280,  -1280
    .hword -15393, -15393, -15393, -15393, -12133, -12133, -12133, -12133
    .hword   -605,   -605,   -605,   -605,  -1036,  -1036,  -1036,  -1036
    .hword  -5735,  -5735,  -5735,  -5735,  -9820,  -9820,  -9820,  -9820
    // k=82: low/high branch-fold constants for R^-1 input
    .hword   -182,   -182,   -182,   -182,    545,    545,    545,    545
    .hword  -1725,  -1725,  -1725,  -1725,   5166,   5166,   5166,   5166
    .hword    -38,    -38,    -38,    -38,     63,     63,     63,     63
    .hword   -360,   -360,   -360,   -360,    597,    597,    597,    597
    // k=50: low/high branch-fold constants for R^-1 input
    .hword  -1009,  -1009,  -1009,  -1009,  -1094,  -1094,  -1094,  -1094
    .hword  -9564,  -9564,  -9564,  -9564, -10370, -10370, -10370, -10370
    .hword    929,    929,    929,    929,   -691,   -691,   -691,   -691
    .hword   8806,   8806,   8806,   8806,  -6550,  -6550,  -6550,  -6550
    // k=51: low/high branch-fold constants for R^-1 input
    .hword   1439,   1439,   1439,   1439,    131,    131,    131,    131
    .hword  13640,  13640,  13640,  13640,   1242,   1242,   1242,   1242
    .hword  -1599,  -1599,  -1599,  -1599,  -1374,  -1374,  -1374,  -1374
    .hword -15157, -15157, -15157, -15157, -13024, -13024, -13024, -13024
    // k=19: low/high branch-fold constants for R^-1 input
    .hword    209,    209,    209,    209,   -504,   -504,   -504,   -504
    .hword   1981,   1981,   1981,   1981,  -4777,  -4777,  -4777,  -4777
    .hword  -1210,  -1210,  -1210,  -1210,   1407,   1407,   1407,   1407
    .hword -11469, -11469, -11469, -11469,  13337,  13337,  13337,  13337
    // k=83: low/high branch-fold constants for R^-1 input
    .hword   -364,   -364,   -364,   -364,   1619,   1619,   1619,   1619
    .hword  -3450,  -3450,  -3450,  -3450,  15346,  15346,  15346,  15346
    .hword    -76,    -76,    -76,    -76,   1386,   1386,   1386,   1386
    .hword   -720,   -720,   -720,   -720,  13138,  13138,  13138,  13138
    // k=84: low/high branch-fold constants for R^-1 input
    .hword   -728,   -728,   -728,   -728,   1048,   1048,   1048,   1048
    .hword  -6901,  -6901,  -6901,  -6901,   9934,   9934,   9934,   9934
    .hword   -152,   -152,   -152,   -152,   -621,   -621,   -621,   -621
    .hword  -1441,  -1441,  -1441,  -1441,  -5886,  -5886,  -5886,  -5886
    // k=52: low/high branch-fold constants for R^-1 input
    .hword   -579,   -579,   -579,   -579,   -575,   -575,   -575,   -575
    .hword  -5488,  -5488,  -5488,  -5488,  -5450,  -5450,  -5450,  -5450
    .hword    259,    259,    259,    259,    885,    885,    885,    885
    .hword   2455,   2455,   2455,   2455,   8389,   8389,   8389,   8389
    // k=20: low/high branch-fold constants for R^-1 input
    .hword    418,    418,    418,    418,   -717,   -717,   -717,   -717
    .hword   3962,   3962,   3962,   3962,  -6796,  -6796,  -6796,  -6796
    .hword   1037,   1037,   1037,   1037,   -159,   -159,   -159,   -159
    .hword   9829,   9829,   9829,   9829,  -1507,  -1507,  -1507,  -1507
    // k=21: low/high branch-fold constants for R^-1 input
    .hword    836,    836,    836,    836,   1511,   1511,   1511,   1511
    .hword   7924,   7924,   7924,   7924,  14322,  14322,  14322,  14322
    .hword  -1383,  -1383,  -1383,  -1383,    -41,    -41,    -41,    -41
    .hword -13109, -13109, -13109, -13109,   -389,   -389,   -389,   -389
    // k=85: low/high branch-fold constants for R^-1 input
    .hword  -1456,  -1456,  -1456,  -1456,  -1143,  -1143,  -1143,  -1143
    .hword -13801, -13801, -13801, -13801, -10834, -10834, -10834, -10834
    .hword   -304,   -304,   -304,   -304,    166,    166,    166,    166
    .hword  -2882,  -2882,  -2882,  -2882,   1573,   1573,   1573,   1573
    // k=53: low/high branch-fold constants for R^-1 input
    .hword  -1158,  -1158,  -1158,  -1158,   1178,   1178,   1178,   1178
    .hword -10976, -10976, -10976, -10976,  11166,  11166,  11166,  11166
    .hword    518,    518,    518,    518,  -1272,  -1272,  -1272,  -1272
    .hword   4910,   4910,   4910,   4910, -12057, -12057, -12057, -12057
    // k=54: low/high branch-fold constants for R^-1 input
    .hword   1141,   1141,   1141,   1141,   1717,   1717,   1717,   1717
    .hword  10815,  10815,  10815,  10815,  16275,  16275,  16275,  16275
    .hword   1036,   1036,   1036,   1036,   -328,   -328,   -328,   -328
    .hword   9820,   9820,   9820,   9820,  -3109,  -3109,  -3109,  -3109
    // k=22: low/high branch-fold constants for R^-1 input
    .hword   1672,   1672,   1672,   1672,  -1328,  -1328,  -1328,  -1328
    .hword  15848,  15848,  15848,  15848, -12588, -12588, -12588, -12588
    .hword    691,    691,    691,    691,   -902,   -902,   -902,   -902
    .hword   6550,   6550,   6550,   6550,  -8550,  -8550,  -8550,  -8550
    // k=86: low/high branch-fold constants for R^-1 input
    .hword    545,    545,    545,    545,   -947,   -947,   -947,   -947
    .hword   5166,   5166,   5166,   5166,  -8976,  -8976,  -8976,  -8976
    .hword   -608,   -608,   -608,   -608,    195,    195,    195,    195
    .hword  -5763,  -5763,  -5763,  -5763,   1848,   1848,   1848,   1848
    // k=87: low/high branch-fold constants for R^-1 input
    .hword   1090,   1090,   1090,   1090,    -92,    -92,    -92,    -92
    .hword  10332,  10332,  10332,  10332,   -872,   -872,   -872,   -872
    .hword  -1216,  -1216,  -1216,  -1216,    833,    833,    833,    833
    .hword -11526, -11526, -11526, -11526,   7896,   7896,   7896,   7896
    // k=55: low/high branch-fold constants for R^-1 input
    .hword  -1175,  -1175,  -1175,  -1175,   -253,   -253,   -253,   -253
    .hword -11138, -11138, -11138, -11138,  -2398,  -2398,  -2398,  -2398
    .hword  -1385,  -1385,  -1385,  -1385,   -302,   -302,   -302,   -302
    .hword -13128, -13128, -13128, -13128,  -2863,  -2863,  -2863,  -2863
    // k=23: low/high branch-fold constants for R^-1 input
    .hword   -113,   -113,   -113,   -113,  -1560,  -1560,  -1560,  -1560
    .hword  -1071,  -1071,  -1071,  -1071, -14787, -14787, -14787, -14787
    .hword   1382,   1382,   1382,   1382,    898,    898,    898,    898
    .hword  13100,  13100,  13100,  13100,   8512,   8512,   8512,   8512
    // k=24: low/high branch-fold constants for R^-1 input
    .hword   -226,   -226,   -226,   -226,    250,    250,    250,    250
    .hword  -2142,  -2142,  -2142,  -2142,   2370,   2370,   2370,   2370
    .hword   -693,   -693,   -693,   -693,   -986,   -986,   -986,   -986
    .hword  -6569,  -6569,  -6569,  -6569,  -9346,  -9346,  -9346,  -9346
    // k=88: low/high branch-fold constants for R^-1 input
    .hword  -1277,  -1277,  -1277,  -1277,   1433,   1433,   1433,   1433
    .hword -12104, -12104, -12104, -12104,  13583,  13583,  13583,  13583
    .hword   1025,   1025,   1025,   1025,   1041,   1041,   1041,   1041
    .hword   9716,   9716,   9716,   9716,   9867,   9867,   9867,   9867
    // k=56: low/high branch-fold constants for R^-1 input
    .hword   1107,   1107,   1107,   1107,   1348,   1348,   1348,   1348
    .hword  10493,  10493,  10493,  10493,  12777,  12777,  12777,  12777
    .hword    687,    687,    687,    687,    270,    270,    270,    270
    .hword   6512,   6512,   6512,   6512,   2559,   2559,   2559,   2559
    // k=57: low/high branch-fold constants for R^-1 input
    .hword  -1243,  -1243,  -1243,  -1243,  -1457,  -1457,  -1457,  -1457
    .hword -11782, -11782, -11782, -11782, -13811, -13811, -13811, -13811
    .hword   1374,   1374,   1374,   1374,   -974,   -974,   -974,   -974
    .hword  13024,  13024,  13024,  13024,  -9232,  -9232,  -9232,  -9232
    // k=25: low/high branch-fold constants for R^-1 input
    .hword   -452,   -452,   -452,   -452,  -1414,  -1414,  -1414,  -1414
    .hword  -4284,  -4284,  -4284,  -4284, -13403, -13403, -13403, -13403
    .hword  -1386,  -1386,  -1386,  -1386,   -950,   -950,   -950,   -950
    .hword -13138, -13138, -13138, -13138,  -9005,  -9005,  -9005,  -9005
    // k=89: low/high branch-fold constants for R^-1 input
    .hword    903,    903,    903,    903,    413,    413,    413,    413
    .hword   8559,   8559,   8559,   8559,   3915,   3915,   3915,   3915
    .hword  -1407,  -1407,  -1407,  -1407,  -1297,  -1297,  -1297,  -1297
    .hword -13337, -13337, -13337, -13337, -12294, -12294, -12294, -12294
    // k=90: low/high branch-fold constants for R^-1 input
    .hword  -1651,  -1651,  -1651,  -1651,  -1285,  -1285,  -1285,  -1285
    .hword -15649, -15649, -15649, -15649, -12180, -12180, -12180, -12180
    .hword    643,    643,    643,    643,   -878,   -878,   -878,   -878
    .hword   6095,   6095,   6095,   6095,  -8322,  -8322,  -8322,  -8322
    // k=58: low/high branch-fold constants for R^-1 input
    .hword    971,    971,    971,    971,   -941,   -941,   -941,   -941
    .hword   9204,   9204,   9204,   9204,  -8919,  -8919,  -8919,  -8919
    .hword   -709,   -709,   -709,   -709,   -686,   -686,   -686,   -686
    .hword  -6720,  -6720,  -6720,  -6720,  -6502,  -6502,  -6502,  -6502
    // k=26: low/high branch-fold constants for R^-1 input
    .hword   -904,   -904,   -904,   -904,      5,      5,      5,      5
    .hword  -8569,  -8569,  -8569,  -8569,     47,     47,     47,     47
    .hword    685,    685,    685,    685,   -158,   -158,   -158,   -158
    .hword   6493,   6493,   6493,   6493,  -1498,  -1498,  -1498,  -1498
    // k=27: low/high branch-fold constants for R^-1 input
    .hword   1649,   1649,   1649,   1649,    110,    110,    110,    110
    .hword  15630,  15630,  15630,  15630,   1043,   1043,   1043,   1043
    .hword   1370,   1370,   1370,   1370,    -19,    -19,    -19,    -19
    .hword  12986,  12986,  12986,  12986,   -180,   -180,   -180,   -180
    // k=91: low/high branch-fold constants for R^-1 input
    .hword    155,    155,    155,    155,   -614,   -614,   -614,   -614
    .hword   1469,   1469,   1469,   1469,  -5820,  -5820,  -5820,  -5820
    .hword   1286,   1286,   1286,   1286,   1426,   1426,   1426,   1426
    .hword  12190,  12190,  12190,  12190,  13517,  13517,  13517,  13517
    // k=59: low/high branch-fold constants for R^-1 input
    .hword  -1515,  -1515,  -1515,  -1515,     40,     40,     40,     40
    .hword -14360, -14360, -14360, -14360,    379,    379,    379,    379
    .hword  -1418,  -1418,  -1418,  -1418,  -1264,  -1264,  -1264,  -1264
    .hword -13441, -13441, -13441, -13441, -11981, -11981, -11981, -11981
    // k=60: low/high branch-fold constants for R^-1 input
    .hword    427,    427,    427,    427,    880,    880,    880,    880
    .hword   4047,   4047,   4047,   4047,   8341,   8341,   8341,   8341
    .hword    621,    621,    621,    621,   -152,   -152,   -152,   -152
    .hword   5886,   5886,   5886,   5886,  -1441,  -1441,  -1441,  -1441
    // k=28: low/high branch-fold constants for R^-1 input
    .hword   -159,   -159,   -159,   -159,  -1037,  -1037,  -1037,  -1037
    .hword  -1507,  -1507,  -1507,  -1507,  -9829,  -9829,  -9829,  -9829
    .hword   -717,   -717,   -717,   -717,   -418,   -418,   -418,   -418
    .hword  -6796,  -6796,  -6796,  -6796,  -3962,  -3962,  -3962,  -3962
    // k=92: low/high branch-fold constants for R^-1 input
    .hword    310,    310,    310,    310,    320,    320,    320,    320
    .hword   2938,   2938,   2938,   2938,   3033,   3033,   3033,   3033
    .hword   -885,   -885,   -885,   -885,    259,    259,    259,    259
    .hword  -8389,  -8389,  -8389,  -8389,   2455,   2455,   2455,   2455
    // k=93: low/high branch-fold constants for R^-1 input
    .hword    620,    620,    620,    620,    126,    126,    126,    126
    .hword   5877,   5877,   5877,   5877,   1194,   1194,   1194,   1194
    .hword   1687,   1687,   1687,   1687,  -1216,  -1216,  -1216,  -1216
    .hword  15991,  15991,  15991,  15991, -11526, -11526, -11526, -11526
    // k=61: low/high branch-fold constants for R^-1 input
    .hword    854,    854,    854,    854,  -1382,  -1382,  -1382,  -1382
    .hword   8095,   8095,   8095,   8095, -13100, -13100, -13100, -13100
    .hword   1242,   1242,   1242,   1242,    113,    113,    113,    113
    .hword  11773,  11773,  11773,  11773,   1071,   1071,   1071,   1071
    // k=29: low/high branch-fold constants for R^-1 input
    .hword   -318,   -318,   -318,   -318,   1385,   1385,   1385,   1385
    .hword  -3014,  -3014,  -3014,  -3014,  13128,  13128,  13128,  13128
    .hword  -1434,  -1434,  -1434,  -1434,   1175,   1175,   1175,   1175
    .hword -13593, -13593, -13593, -13593,  11138,  11138,  11138,  11138
    // k=30: low/high branch-fold constants for R^-1 input
    .hword   -636,   -636,   -636,   -636,   -643,   -643,   -643,   -643
    .hword  -6028,  -6028,  -6028,  -6028,  -6095,  -6095,  -6095,  -6095
    .hword    589,    589,    589,    589,   1651,   1651,   1651,   1651
    .hword   5583,   5583,   5583,   5583,  15649,  15649,  15649,  15649
    // k=94: low/high branch-fold constants for R^-1 input
    .hword   1240,   1240,   1240,   1240,   -685,   -685,   -685,   -685
    .hword  11754,  11754,  11754,  11754,  -6493,  -6493,  -6493,  -6493
    .hword    -83,    -83,    -83,    -83,    904,    904,    904,    904
    .hword   -787,   -787,   -787,   -787,   8569,   8569,   8569,   8569
    // k=62: low/high branch-fold constants for R^-1 input
    .hword   1708,   1708,   1708,   1708,    709,    709,    709,    709
    .hword  16190,  16190,  16190,  16190,   6720,   6720,   6720,   6720
    .hword   -973,   -973,   -973,   -973,   -971,   -971,   -971,   -971
    .hword  -9223,  -9223,  -9223,  -9223,  -9204,  -9204,  -9204,  -9204
    // k=63: low/high branch-fold constants for R^-1 input
    .hword    -41,    -41,    -41,    -41,  -1687,  -1687,  -1687,  -1687
    .hword   -389,   -389,   -389,   -389, -15991, -15991, -15991, -15991
    .hword   1511,   1511,   1511,   1511,   -620,   -620,   -620,   -620
    .hword  14322,  14322,  14322,  14322,  -5877,  -5877,  -5877,  -5877
    // k=31: low/high branch-fold constants for R^-1 input
    .hword  -1272,  -1272,  -1272,  -1272,   -318,   -318,   -318,   -318
    .hword -12057, -12057, -12057, -12057,  -3014,  -3014,  -3014,  -3014
    .hword   1178,   1178,   1178,   1178,  -1705,  -1705,  -1705,  -1705
    .hword  11166,  11166,  11166,  11166, -16161, -16161, -16161, -16161
    // k=95: low/high branch-fold constants for R^-1 input
    .hword   -977,   -977,   -977,   -977,  -1242,  -1242,  -1242,  -1242
    .hword  -9261,  -9261,  -9261,  -9261, -11773, -11773, -11773, -11773
    .hword   -166,   -166,   -166,   -166,   -854,   -854,   -854,   -854
    .hword  -1573,  -1573,  -1573,  -1573,  -8095,  -8095,  -8095,  -8095

.purgem BARRETT_REDUCE
.purgem FQMUL_LANE
.purgem INV_BUTTERFLY_LANE
.purgem DIRECT_STAGE123_VEC
.purgem STORE_STAGE123_STRIPE_SCRATCH
.purgem DIRECT_STAGE123_BLOCK_TO_SCRATCH
.purgem DIRECT_STAGE123_CONSTS
.purgem DIRECT_STAGE123_STRIPE_SCRATCH_ROW0_BODY
.purgem DIRECT_STAGE123_STRIPE_SCRATCH_ROW0
.purgem DIRECT_STAGE123_STRIPE_SCRATCH_ROW1_BODY
.purgem DIRECT_STAGE123_STRIPE_SCRATCH_ROW1
.purgem DIRECT_STAGE123_STRIPE_SCRATCH_ROW2_BODY
.purgem DIRECT_STAGE123_STRIPE_SCRATCH_ROW2
.purgem RUN_INVNTT32_STAGE45_SCRATCH_ROW
.purgem POST_STORE_PTR
.purgem LOAD_BRANCHFOLD_CONSTS
.purgem POST_STORE_PTR_BRANCHFOLD
.purgem FUSED_POST_STRIPE
.purgem RUN_FUSED_POST_STRIPE
.purgem RUN_FUSED_POST_3STRIPE_GROUP
.purgem RUN_FUSED_POST_3STRIPE_LOOP
.purgem RUN_FUSED_POST_LOOP
.purgem INVNTT_SAVE_CALLEE_SAVED_SIMD
.purgem INVNTT_RESTORE_CALLEE_SAVED_SIMD
