/*
 * Generated AArch64 NEON inverse NTT for the Good-Thomas row-bitrev
 * layout produced by asm/my_ntt.s.  The retained clean Slothy component
 * sources for the promoted scheduled regions are
 * invntt32_stage45_reduce_fused_clean.slothy.s and
 * invntt_post_fused_dstore_clean.slothy.s.
 *
 * Constant tables here are normal centered multipliers plus sqrdmulh
 * precompute constants.  They are not Montgomery-form tables.
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
	 * Contract: rowlazy is production-correct for forward-produced GT
	 * row-bitrev inputs with the expected coefficient bounds.  It is not a
	 * general-purpose inverse NTT for arbitrary int16 representatives.
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

.ifdef INVNTT_USE_STAGE45_REDUCE_FUSION
    /*
     * Opt-in experiment: fuse the production row-end Barrett reduction into
     * stage45.  This is algebraically the same REDUCE_ROW_ALL operation, but
     * avoids storing lazy stage45 outputs only to reload them for reduction.
     */
    BARRETT_REDUCE v3, v12
    BARRETT_REDUCE v4, v12
    BARRETT_REDUCE v5, v12
    BARRETT_REDUCE v6, v12
.endif

    str q3, [x2, #(16 * \j)]
    str q4, [x2, #(16 * (\j + 8))]
    str q5, [x2, #(16 * (\j + 16))]
    str q6, [x2, #(16 * (\j + 24))]
.endm

.macro INVNTT32_STAGE45_STRIPE_SLOTHY j
    /*
     * A72 Slothy schedule for INVNTT_USE_STAGE45_REDUCE_FUSION.  Source:
     * asm/slothy/invntt32_stage45_reduce_fused_clean.slothy.s, generated as
     * asm/slothy/invntt32_stage45_reduce_fused.opt.s with allow_spills=false.
     */
    ldr q11, [x2, #(16 * (\j + 24))]
    ldr q7, [x3, #16]
    ldr q30, [x2, #(16 * (\j + 16))]
    ldr q5, [x3]
    ldr q26, [x2, #(16 * (\j + 8))]
    ldr q17, [x2, #(16 * \j)]
    sqrdmulh v29.8h, v11.8h, v7.h[0]
    mul v23.8h, v11.8h, v5.h[0]
    mls v23.8h, v29.8h, v0.h[0]
    sqrdmulh v20.8h, v26.8h, v7.h[0]
    mul v10.8h, v26.8h, v5.h[0]
    add v19.8h, v30.8h, v23.8h
    sub v21.8h, v30.8h, v23.8h
    mls v10.8h, v20.8h, v0.h[0]
    sqrdmulh v6.8h, v19.8h, v7.h[1]
    sqrdmulh v22.8h, v21.8h, v7.h[2]
    mul v25.8h, v19.8h, v5.h[1]
    mls v25.8h, v6.8h, v0.h[0]
    add v9.8h, v17.8h, v10.8h
    mul v14.8h, v21.8h, v5.h[2]
    sub v7.8h, v17.8h, v10.8h
    mls v14.8h, v22.8h, v0.h[0]
    sub v29.8h, v9.8h, v25.8h
    add v17.8h, v9.8h, v25.8h
    sqdmulh v8.8h, v29.8h, v0.h[1]
    sub v23.8h, v7.8h, v14.8h
    sqdmulh v22.8h, v17.8h, v0.h[1]
    add v10.8h, v7.8h, v14.8h
    sqdmulh v3.8h, v23.8h, v0.h[1]
    srshr v13.8h, v8.8h, #11
    sqdmulh v28.8h, v10.8h, v0.h[1]
    srshr v9.8h, v22.8h, #11
    mls v29.8h, v13.8h, v0.h[0]
    srshr v18.8h, v3.8h, #11
    mls v17.8h, v9.8h, v0.h[0]
    srshr v27.8h, v28.8h, #11
    mls v23.8h, v18.8h, v0.h[0]
    mls v10.8h, v27.8h, v0.h[0]
    str q17, [x2, #(16 * \j)]
    str q23, [x2, #(16 * (\j + 24))]
    str q29, [x2, #(16 * (\j + 16))]
    str q10, [x2, #(16 * (\j + 8))]
    add x3, x3, #32
.endm

.macro INVNTT32_STAGE45_STRIPE_SCRATCH j
    ldr q1, [x3], #16
    ldr q2, [x3], #16

    ldr q3, [x14, #(64 * \j + 0)]
    ldr q4, [x14, #(64 * \j + 16)]
    ldr q5, [x14, #(64 * \j + 32)]
    ldr q6, [x14, #(64 * \j + 48)]

    /* len=16 for the lower and upper halves, then len=32. */
    INV_BUTTERFLY_LANE v3, v4, v1, 0, v2, 0, v11, v12
    INV_BUTTERFLY_LANE v5, v6, v1, 0, v2, 0, v11, v12
    INV_BUTTERFLY_LANE v3, v5, v1, 1, v2, 1, v11, v12
    INV_BUTTERFLY_LANE v4, v6, v1, 2, v2, 2, v11, v12

.ifdef INVNTT_USE_STAGE45_REDUCE_FUSION
    BARRETT_REDUCE v3, v12
    BARRETT_REDUCE v4, v12
    BARRETT_REDUCE v5, v12
    BARRETT_REDUCE v6, v12
.endif

    str q3, [x2, #(16 * \j)]
    str q4, [x2, #(16 * (\j + 8))]
    str q5, [x2, #(16 * (\j + 16))]
    str q6, [x2, #(16 * (\j + 24))]
.endm

.macro INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH j
    /*
     * Same A72 stage45+row-end-reduce schedule as
     * INVNTT32_STAGE45_STRIPE_SLOTHY, but it reads the stage123 outputs from
     * stripe-major scratch:
     *   [j, j+8, j+16, j+24] at x14 + 64*j.
     */
    ldr q11, [x14, #(64 * \j + 48)]
    ldr q7, [x3, #16]
    ldr q30, [x14, #(64 * \j + 32)]
    ldr q5, [x3]
    ldr q26, [x14, #(64 * \j + 16)]
    ldr q17, [x14, #(64 * \j + 0)]
    sqrdmulh v29.8h, v11.8h, v7.h[0]
    mul v23.8h, v11.8h, v5.h[0]
    mls v23.8h, v29.8h, v0.h[0]
    sqrdmulh v20.8h, v26.8h, v7.h[0]
    mul v10.8h, v26.8h, v5.h[0]
    add v19.8h, v30.8h, v23.8h
    sub v21.8h, v30.8h, v23.8h
    mls v10.8h, v20.8h, v0.h[0]
    sqrdmulh v6.8h, v19.8h, v7.h[1]
    sqrdmulh v22.8h, v21.8h, v7.h[2]
    mul v25.8h, v19.8h, v5.h[1]
    mls v25.8h, v6.8h, v0.h[0]
    add v9.8h, v17.8h, v10.8h
    mul v14.8h, v21.8h, v5.h[2]
    sub v7.8h, v17.8h, v10.8h
    mls v14.8h, v22.8h, v0.h[0]
    sub v29.8h, v9.8h, v25.8h
    add v17.8h, v9.8h, v25.8h
    sqdmulh v8.8h, v29.8h, v0.h[1]
    sub v23.8h, v7.8h, v14.8h
    sqdmulh v22.8h, v17.8h, v0.h[1]
    add v10.8h, v7.8h, v14.8h
    sqdmulh v3.8h, v23.8h, v0.h[1]
    srshr v13.8h, v8.8h, #11
    sqdmulh v28.8h, v10.8h, v0.h[1]
    srshr v9.8h, v22.8h, #11
    mls v29.8h, v13.8h, v0.h[0]
    srshr v18.8h, v3.8h, #11
    mls v17.8h, v9.8h, v0.h[0]
    srshr v27.8h, v28.8h, #11
    mls v23.8h, v18.8h, v0.h[0]
    mls v10.8h, v27.8h, v0.h[0]
    str q17, [x2, #(16 * \j)]
    str q23, [x2, #(16 * (\j + 24))]
    str q29, [x2, #(16 * (\j + 16))]
    str q10, [x2, #(16 * (\j + 8))]
    add x3, x3, #32
.endm

.macro DIRECT_LOAD_VEC dstidx, srcoff
    ldr d1, [x3, #\srcoff]
    ldr d2, [x4, #\srcoff]
    mov v1.d[1], v2.d[0]
    str q1, [x2, #(16 * \dstidx)]
.endm

.macro DIRECT_STAGE123_VEC dst, srcoff
    ldr d\dst, [x3, #\srcoff]
    ldr d12, [x4, #\srcoff]
    mov v\dst\().d[1], v12.d[0]
.endm

.macro DIRECT_STAGE123_BLOCK base, off0, off1, off2, off3, off4, off5, off6, off7
    DIRECT_STAGE123_VEC 3, \off0
    DIRECT_STAGE123_VEC 4, \off1
    DIRECT_STAGE123_VEC 5, \off2
    DIRECT_STAGE123_VEC 6, \off3
    DIRECT_STAGE123_VEC 7, \off4
    DIRECT_STAGE123_VEC 8, \off5
    DIRECT_STAGE123_VEC 9, \off6
    DIRECT_STAGE123_VEC 10, \off7

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

    STORE_STAGE123_STRIPE_SCRATCH \group
.endm

.macro DIRECT_STAGE123_CONSTS
    adr x7, invntt32_stage123_consts
    ldr q1, [x7]
    ldr q2, [x7, #16]
.endm

.macro DIRECT_STAGE123_ROW0
    /*
     * Fused direct physical load -> inverse row stage123 for k3=0.
     * This skips the temporary row-bitrev input row materialization:
     *   old path: direct d/d loads -> str q row -> stage123 ldr q
     *   this path: direct d/d loads -> stage123 -> str q stage123 output
     */
    DIRECT_STAGE123_CONSTS
    DIRECT_STAGE123_BLOCK 0,   0,  24,  48,  72,  96, 120, 144, 168
    DIRECT_STAGE123_BLOCK 128, 192, 216, 240, 264, 288, 312, 336, 360
    DIRECT_STAGE123_BLOCK 256, 384, 408, 432, 456, 480, 504, 528, 552
    DIRECT_STAGE123_BLOCK 384, 576, 600, 624, 648, 672, 696, 720, 744
.endm

.macro DIRECT_STAGE123_ROW1
    /* k3=1 physical bytes: 256,280,...,760 then 16,40,...,232 */
    DIRECT_STAGE123_CONSTS
    DIRECT_STAGE123_BLOCK 0,   256, 280, 304, 328, 352, 376, 400, 424
    DIRECT_STAGE123_BLOCK 128, 448, 472, 496, 520, 544, 568, 592, 616
    DIRECT_STAGE123_BLOCK 256, 640, 664, 688, 712, 736, 760,  16,  40
    DIRECT_STAGE123_BLOCK 384,  64,  88, 112, 136, 160, 184, 208, 232
.endm

.macro DIRECT_STAGE123_ROW2
    /* k3=2 physical bytes: 512,536,...,752 then 8,32,...,488 */
    DIRECT_STAGE123_CONSTS
    DIRECT_STAGE123_BLOCK 0,   512, 536, 560, 584, 608, 632, 656, 680
    DIRECT_STAGE123_BLOCK 128, 704, 728, 752,   8,  32,  56,  80, 104
    DIRECT_STAGE123_BLOCK 256, 128, 152, 176, 200, 224, 248, 272, 296
    DIRECT_STAGE123_BLOCK 384, 320, 344, 368, 392, 416, 440, 464, 488
.endm

.macro DIRECT_STAGE123_STRIPE_SCRATCH_ROW0
    /*
     * Opt-in experiment: direct physical load -> stage123 -> stripe-major
     * scratch for stage45.  This keeps stage123 math unchanged but changes
     * only the temporary stage123 layout consumed by the stage45 helper.
     */
    add x14, sp, #1568
    DIRECT_STAGE123_CONSTS
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 0,   0,  24,  48,  72,  96, 120, 144, 168
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 1, 192, 216, 240, 264, 288, 312, 336, 360
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 2, 384, 408, 432, 456, 480, 504, 528, 552
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 3, 576, 600, 624, 648, 672, 696, 720, 744
.endm

.macro DIRECT_STAGE123_STRIPE_SCRATCH_ROW1
    /* k3=1 physical bytes: 256,280,...,760 then 16,40,...,232 */
    add x14, sp, #1568
    DIRECT_STAGE123_CONSTS
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 0, 256, 280, 304, 328, 352, 376, 400, 424
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 1, 448, 472, 496, 520, 544, 568, 592, 616
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 2, 640, 664, 688, 712, 736, 760,  16,  40
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 3,  64,  88, 112, 136, 160, 184, 208, 232
.endm

.macro DIRECT_STAGE123_STRIPE_SCRATCH_ROW2
    /* k3=2 physical bytes: 512,536,...,752 then 8,32,...,488 */
    add x14, sp, #1568
    DIRECT_STAGE123_CONSTS
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 0, 512, 536, 560, 584, 608, 632, 656, 680
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 1, 704, 728, 752,   8,  32,  56,  80, 104
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 2, 128, 152, 176, 200, 224, 248, 272, 296
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 3, 320, 344, 368, 392, 416, 440, 464, 488
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

.macro RUN_INVNTT32_STAGE45_ROW
    bl _invntt32_8way_stage45_only
.endm

.macro RUN_INVNTT32_STAGE45_SCRATCH_ROW
    bl _invntt32_8way_stage45_from_scratch
.endm

.macro POST_STORE_PTR xvec, ptr, off_lo, off_hi
.ifdef INVNTT_USE_POST_BRANCHFOLD
    POST_STORE_PTR_BRANCHFOLD \xvec, \ptr, \off_lo, \off_hi
.else
.ifdef INVNTT_USE_POST_FASTSCALE
    POST_STORE_PTR_FASTSCALE \xvec, \ptr, \off_lo, \off_hi
.else
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

    str      d21, [\ptr, #\off_lo]
    str      d23, [\ptr, #\off_hi]
.endif
.endif
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
     * representatives and is not safe for poly_crepmod3.  The production gate
     * always pairs this with INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS, which adds
     * final Barrett reductions and matched the exact C-reference output for
     * forward-produced GT inputs.
     */
    ldr     q10, [x3], #16    // low normal constants
    ldr     q11, [x3], #16    // low sqrdmulh precompute
    ldr     q12, [x3], #16    // high normal constants
    ldr     q13, [x3], #16    // high sqrdmulh precompute

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

.ifdef INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS
    BARRETT_REDUCE v21, v20
    BARRETT_REDUCE v23, v20
.endif

    str      d21, [\ptr, #\off_lo]
    str      d23, [\ptr, #\off_hi]
.endm

.macro POST_STORE_PTR_FASTSCALE xvec, ptr, off_lo, off_hi
    /*
     * Experimental exactness probe:
     *
     * old:
     *   t2       = fqmul(ZMINUSZ5INV, diff)
     *   out_low  = fqmul(1/192, sum - t2)
     *   out_high = fqmul(1/96,  t2)
     *
     * new:
     *   t        = fqmul(ZMINUSZ5INV/192, diff)
     *   s        = fqmul(1/192, sum)
     *   out_low  = s - t
     *   out_high = 2*t
     *
     * This saves one fqmul per output vector but changes reduction order, so
     * exact representative tests decide whether it is usable.
     */
    ldr     q10, [x3], #16
    ldr     q11, [x3], #16
    sqrdmulh v12.8h, \xvec\().8h, v11.8h
    mul      v13.8h, \xvec\().8h, v10.8h
    mls      v13.8h, v12.8h, v0.h[0]

    ext      v14.16b, v13.16b, v13.16b, #8
    add      v24.8h, v13.8h, v14.8h
    sub      v16.8h, v13.8h, v14.8h

    sqrdmulh v17.8h, v16.8h, v15.h[3]
    mul      v18.8h, v16.8h, v15.h[2]
    mls      v18.8h, v17.8h, v0.h[0]

    sqrdmulh v20.8h, v24.8h, v0.h[7]
    mul      v21.8h, v24.8h, v0.h[6]
    mls      v21.8h, v20.8h, v0.h[0]

    sub      v21.8h, v21.8h, v18.8h
    add      v23.8h, v18.8h, v18.8h

.ifdef INVNTT_POST_FASTSCALE_REDUCE_OUTPUTS
    BARRETT_REDUCE v21, v20
    BARRETT_REDUCE v23, v20
.endif

    str      d21, [\ptr, #\off_lo]
    str      d23, [\ptr, #\off_hi]
.endm

.macro POST_FINAL_STORE_PTR xvec, ptr, off_lo, off_hi
    ext      v14.16b, \xvec\().16b, \xvec\().16b, #8
    add      v24.8h, \xvec\().8h, v14.8h
    sub      v16.8h, \xvec\().8h, v14.8h

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
	 * these reductions into the later untwist/merge fqmul chain.  Postlazy can
	 * be ring-correct modulo q, but it is not exact-representative identical,
	 * so it is intentionally not default and must remain experimental.
	 *
	 * This matters for scheme integration: q = 3457 == 1 (mod 3), and
	 * poly_crepmod3 reduces the raw signed representative modulo 3.  Two
	 * representatives equal modulo q need not be equal modulo 3; x and x+q
	 * differ by 1 modulo 3.  A final postlazy value alone does not identify
	 * whether it should be corrected by 0, +q, or -q relative to rowlazy, so a
	 * final-value-only crepmod3 fix is not mathematically equivalent.
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

.macro POST_DFT3_STRIPE reduce
    ldr q1, [x8], #16
    ldr q2, [x9], #16
    ldr q3, [x10], #16

    sub      v4.8h, v3.8h, v2.8h
    sqrdmulh v5.8h, v4.8h, v0.h[3]
    mul      v6.8h, v4.8h, v0.h[2]
    mls      v6.8h, v5.8h, v0.h[0]

    add      v7.8h, v1.8h, v2.8h
    add      v7.8h, v7.8h, v3.8h
.if \reduce
    BARRETT_REDUCE v7, v24
.endif

    sub      v8.8h, v1.8h, v2.8h
    add      v8.8h, v8.8h, v6.8h
.if \reduce
    BARRETT_REDUCE v8, v24
.endif

    sub      v9.8h, v1.8h, v3.8h
    sub      v9.8h, v9.8h, v6.8h
.if \reduce
    BARRETT_REDUCE v9, v24
.endif

    str q7, [x2], #16
    str q8, [x2], #16
    str q9, [x2], #16
.endm

.macro POST_UNTWIST_STRIPE
    ldr q7, [x1], #16
    ldr q10, [x3], #16
    ldr q11, [x3], #16
    sqrdmulh v12.8h, v7.8h, v11.8h
    mul      v13.8h, v7.8h, v10.8h
    mls      v13.8h, v12.8h, v0.h[0]
    str q13, [x2], #16
.endm

.macro POST_FINAL_MERGE_STRIPE ptr0, off0_lo, off0_hi, ptr1, off1_lo, off1_hi, ptr2, off2_lo, off2_hi
    ldr q7, [x8], #16
    ldr q8, [x8], #16
    ldr q9, [x8], #16
    POST_FINAL_STORE_PTR v7, \ptr0, \off0_lo, \off0_hi
    POST_FINAL_STORE_PTR v8, \ptr1, \off1_lo, \off1_hi
    POST_FINAL_STORE_PTR v9, \ptr2, \off2_lo, \off2_hi
.endm

.macro FUSED_POST_STRIPE_SLOTHY ptr0, off0_lo, off0_hi, ptr1, off1_lo, off1_hi, ptr2, off2_lo, off2_hi
    /*
     * A72 Slothy schedule for one production-equivalent fused post-row stripe.
     * Source: asm/slothy/invntt_post_fused_dstore_clean.slothy.s, generated as
     * asm/slothy/invntt_post_fused_dstore.opt.s with allow_spills=false.
     *
     * The Slothy clean source uses q stores as live-out placeholders because
     * this checkout's target model does not parse non-stack d stores.  The
     * integrated path below keeps production's final d stores exactly.
     */
    ldr q7, [x9], #16
    ldr q20, [x10], #16
    ldr q17, [x8], #16
    ldr q30, [x3], #16
    ldr q11, [x3], #16
    ldr q6, [x3], #16
    ldr q29, [x3], #16
    ldr q3, [x3], #16
    sub v13.8h, v20.8h, v7.8h
    ldr q2, [x3], #16
    add v28.8h, v17.8h, v7.8h
    sub v5.8h, v17.8h, v7.8h
    sub v18.8h, v17.8h, v20.8h
    sqrdmulh v24.8h, v13.8h, v0.h[3]
    add v9.8h, v28.8h, v20.8h
    mul v21.8h, v13.8h, v0.h[2]
    sqdmulh v1.8h, v9.8h, v0.h[1]
    mls v21.8h, v24.8h, v0.h[0]
    srshr v13.8h, v1.8h, #11
    add v20.8h, v5.8h, v21.8h
    sub v21.8h, v18.8h, v21.8h
    mls v9.8h, v13.8h, v0.h[0]
    sqdmulh v13.8h, v20.8h, v0.h[1]
    sqdmulh v1.8h, v21.8h, v0.h[1]
    mul v17.8h, v9.8h, v30.8h
    srshr v8.8h, v13.8h, #11
    sqrdmulh v10.8h, v9.8h, v11.8h
    srshr v23.8h, v1.8h, #11
    mls v20.8h, v8.8h, v0.h[0]
    mls v21.8h, v23.8h, v0.h[0]
    mls v17.8h, v10.8h, v0.h[0]
    sqrdmulh v5.8h, v20.8h, v29.8h
    mul v27.8h, v20.8h, v6.8h
    ext v9.16b, v17.16b, v17.16b, #8
    mul v16.8h, v21.8h, v3.8h
    mls v27.8h, v5.8h, v0.h[0]
    sub v26.8h, v17.8h, v9.8h
    add v13.8h, v17.8h, v9.8h
    sqrdmulh v9.8h, v21.8h, v2.8h
    sqrdmulh v5.8h, v26.8h, v0.h[5]
    ext v11.16b, v27.16b, v27.16b, #8
    mul v20.8h, v26.8h, v0.h[4]
    mls v16.8h, v9.8h, v0.h[0]
    sub v28.8h, v27.8h, v11.8h
    add v23.8h, v27.8h, v11.8h
    mls v20.8h, v5.8h, v0.h[0]
    mul v11.8h, v28.8h, v0.h[4]
    ext v5.16b, v16.16b, v16.16b, #8
    sqrdmulh v29.8h, v28.8h, v0.h[5]
    sub v27.8h, v13.8h, v20.8h
    sub v8.8h, v16.8h, v5.8h
    sqrdmulh v30.8h, v20.8h, v15.h[1]
    add v14.8h, v16.8h, v5.8h
    sqrdmulh v18.8h, v27.8h, v0.h[7]
    sqrdmulh v25.8h, v8.8h, v0.h[5]
    mul v5.8h, v8.8h, v0.h[4]
    mls v11.8h, v29.8h, v0.h[0]
    mls v5.8h, v25.8h, v0.h[0]
    mul v20.8h, v20.8h, v15.h[0]
    sub v16.8h, v23.8h, v11.8h
    sqrdmulh v1.8h, v11.8h, v15.h[1]
    sub v4.8h, v14.8h, v5.8h
    sqrdmulh v22.8h, v16.8h, v0.h[7]
    sqrdmulh v19.8h, v4.8h, v0.h[7]
    sqrdmulh v3.8h, v5.8h, v15.h[1]
    mul v21.8h, v27.8h, v0.h[6]
    mul v29.8h, v11.8h, v15.h[0]
    mul v11.8h, v16.8h, v0.h[6]
    mul v16.8h, v4.8h, v0.h[6]
    mul v17.8h, v5.8h, v15.h[0]
    mls v16.8h, v19.8h, v0.h[0]
    mls v21.8h, v18.8h, v0.h[0]
    mls v20.8h, v30.8h, v0.h[0]
    str d16, [\ptr2, #\off2_lo]
    mls v17.8h, v3.8h, v0.h[0]
    str d21, [\ptr0, #\off0_lo]
    mls v29.8h, v1.8h, v0.h[0]
    str d20, [\ptr0, #\off0_hi]
    mls v11.8h, v22.8h, v0.h[0]
    str d17, [\ptr2, #\off2_hi]
    str d29, [\ptr1, #\off1_hi]
    str d11, [\ptr1, #\off1_lo]
.endm

.macro FUSED_POST_STRIPE_N1_SLOTHY ptr0, off0_lo, off0_hi, ptr1, off1_lo, off1_hi, ptr2, off2_lo, off2_hi
    /*
     * Neoverse-N1 Slothy schedule used as a Cortex-A76-adjacent experiment
     * for Raspberry Pi 5.  The generated stream is embedded here directly;
     * the Slothy q-store live-out placeholders are converted back to the
     * production d stores below.
     */
    ldr q3, [x9], #16
    ldr q6, [x10], #16
    ldr q17, [x8], #16
    ldr q1, [x3], #16
    ldr q23, [x3], #16
    ldr q11, [x3], #16
    ldr q10, [x3], #16
    ldr q20, [x3], #16
    sub v29.8h, v6.8h, v3.8h
    ldr q28, [x3], #16
    add v27.8h, v17.8h, v3.8h
    sub v24.8h, v17.8h, v3.8h
    sub v14.8h, v17.8h, v6.8h
    add v8.8h, v27.8h, v6.8h
    sqrdmulh v13.8h, v29.8h, v0.h[3]
    sqdmulh v21.8h, v8.8h, v0.h[1]
    mul v17.8h, v29.8h, v0.h[2]
    mls v17.8h, v13.8h, v0.h[0]
    srshr v25.8h, v21.8h, #11
    add v21.8h, v24.8h, v17.8h
    mls v8.8h, v25.8h, v0.h[0]
    sub v13.8h, v14.8h, v17.8h
    sqdmulh v24.8h, v21.8h, v0.h[1]
    sqdmulh v26.8h, v13.8h, v0.h[1]
    mul v17.8h, v8.8h, v1.8h
    srshr v18.8h, v24.8h, #11
    sqrdmulh v24.8h, v8.8h, v23.8h
    srshr v19.8h, v26.8h, #11
    mls v21.8h, v18.8h, v0.h[0]
    mls v13.8h, v19.8h, v0.h[0]
    mls v17.8h, v24.8h, v0.h[0]
    mul v6.8h, v21.8h, v11.8h
    sqrdmulh v8.8h, v21.8h, v10.8h
    ext v16.16b, v17.16b, v17.16b, #8
    mul v21.8h, v13.8h, v20.8h
    sub v3.8h, v17.8h, v16.8h
    sqrdmulh v24.8h, v13.8h, v28.8h
    add v4.8h, v17.8h, v16.8h
    mls v6.8h, v8.8h, v0.h[0]
    sqrdmulh v28.8h, v3.8h, v0.h[5]
    mul v8.8h, v3.8h, v0.h[4]
    ext v17.16b, v6.16b, v6.16b, #8
    mls v21.8h, v24.8h, v0.h[0]
    sub v11.8h, v6.8h, v17.8h
    add v5.8h, v6.8h, v17.8h
    mls v8.8h, v28.8h, v0.h[0]
    sqrdmulh v10.8h, v11.8h, v0.h[5]
    ext v13.16b, v21.16b, v21.16b, #8
    mul v9.8h, v11.8h, v0.h[4]
    sub v28.8h, v21.8h, v13.8h
    add v14.8h, v21.8h, v13.8h
    sqrdmulh v20.8h, v8.8h, v15.h[1]
    sub v12.8h, v4.8h, v8.8h
    sqrdmulh v1.8h, v28.8h, v0.h[5]
    mul v3.8h, v28.8h, v0.h[4]
    mls v9.8h, v10.8h, v0.h[0]
    mls v3.8h, v1.8h, v0.h[0]
    sqrdmulh v6.8h, v12.8h, v0.h[7]
    sub v19.8h, v5.8h, v9.8h
    sqrdmulh v27.8h, v9.8h, v15.h[1]
    sub v17.8h, v14.8h, v3.8h
    sqrdmulh v23.8h, v3.8h, v15.h[1]
    sqrdmulh v28.8h, v19.8h, v0.h[7]
    sqrdmulh v29.8h, v17.8h, v0.h[7]
    mul v21.8h, v12.8h, v0.h[6]
    mul v24.8h, v3.8h, v15.h[0]
    mul v25.8h, v19.8h, v0.h[6]
    mul v3.8h, v8.8h, v15.h[0]
    mul v17.8h, v17.8h, v0.h[6]
    mul v14.8h, v9.8h, v15.h[0]
    mls v3.8h, v20.8h, v0.h[0]
    mls v17.8h, v29.8h, v0.h[0]
    mls v25.8h, v28.8h, v0.h[0]
    str d3, [\ptr0, #\off0_hi]
    mls v14.8h, v27.8h, v0.h[0]
    str d17, [\ptr2, #\off2_lo]
    mls v21.8h, v6.8h, v0.h[0]
    str d25, [\ptr1, #\off1_lo]
    mls v24.8h, v23.8h, v0.h[0]
    str d14, [\ptr1, #\off1_hi]
    str d21, [\ptr0, #\off0_lo]
    str d24, [\ptr2, #\off2_hi]
.endm

.macro FUSED_POST_STRIPE_N1_NODFTREDUCE_SLOTHY ptr0, off0_lo, off0_hi, ptr1, off1_lo, off1_hi, ptr2, off2_lo, off2_hi
    /*
     * Neoverse-N1 Slothy schedule with the three post-DFT3 Barrett reductions
     * removed.  The generated stream is embedded here directly; final q-store
     * placeholders are converted back to production d stores.
     */
    ldr q9, [x9], #16
    ldr q3, [x10], #16
    ldr q12, [x3], #16
    ldr q28, [x8], #16
    ldr q16, [x3], #16
    ldr q30, [x3], #16
    ldr q18, [x3], #16
    ldr q27, [x3], #16
    ldr q13, [x3], #16
    sub v24.8h, v3.8h, v9.8h
    add v1.8h, v28.8h, v9.8h
    sub v20.8h, v28.8h, v3.8h
    sub v4.8h, v28.8h, v9.8h
    sqrdmulh v11.8h, v24.8h, v0.h[3]
    add v19.8h, v1.8h, v3.8h
    mul v24.8h, v24.8h, v0.h[2]
    sqrdmulh v28.8h, v19.8h, v16.8h
    mls v24.8h, v11.8h, v0.h[0]
    mul v12.8h, v19.8h, v12.8h
    mls v12.8h, v28.8h, v0.h[0]
    add v21.8h, v4.8h, v24.8h
    mul v3.8h, v21.8h, v30.8h
    sqrdmulh v28.8h, v21.8h, v18.8h
    sub v23.8h, v20.8h, v24.8h
    ext v19.16b, v12.16b, v12.16b, #8
    mul v9.8h, v23.8h, v27.8h
    add v29.8h, v12.8h, v19.8h
    sub v21.8h, v12.8h, v19.8h
    sqrdmulh v12.8h, v23.8h, v13.8h
    mls v3.8h, v28.8h, v0.h[0]
    sqrdmulh v5.8h, v21.8h, v0.h[5]
    mls v9.8h, v12.8h, v0.h[0]
    ext v12.16b, v3.16b, v3.16b, #8
    mul v24.8h, v21.8h, v0.h[4]
    sub v8.8h, v3.8h, v12.8h
    add v10.8h, v3.8h, v12.8h
    mls v24.8h, v5.8h, v0.h[0]
    ext v26.16b, v9.16b, v9.16b, #8
    sqrdmulh v27.8h, v8.8h, v0.h[5]
    sub v3.8h, v9.8h, v26.8h
    add v13.8h, v9.8h, v26.8h
    mul v23.8h, v8.8h, v0.h[4]
    sqrdmulh v8.8h, v3.8h, v0.h[5]
    mul v12.8h, v3.8h, v0.h[4]
    sub v2.8h, v29.8h, v24.8h
    mls v23.8h, v27.8h, v0.h[0]
    mls v12.8h, v8.8h, v0.h[0]
    sqrdmulh v14.8h, v2.8h, v0.h[7]
    sub v5.8h, v10.8h, v23.8h
    sqrdmulh v9.8h, v24.8h, v15.h[1]
    sub v13.8h, v13.8h, v12.8h
    sqrdmulh v16.8h, v23.8h, v15.h[1]
    sqrdmulh v6.8h, v5.8h, v0.h[7]
    sqrdmulh v20.8h, v13.8h, v0.h[7]
    sqrdmulh v1.8h, v12.8h, v15.h[1]
    mul v11.8h, v2.8h, v0.h[6]
    mul v3.8h, v13.8h, v0.h[6]
    mul v12.8h, v12.8h, v15.h[0]
    mul v13.8h, v23.8h, v15.h[0]
    mul v24.8h, v24.8h, v15.h[0]
    mul v19.8h, v5.8h, v0.h[6]
    mls v3.8h, v20.8h, v0.h[0]
    mls v12.8h, v1.8h, v0.h[0]
    mls v19.8h, v6.8h, v0.h[0]
    mls v24.8h, v9.8h, v0.h[0]
    mls v13.8h, v16.8h, v0.h[0]
    str d3, [\ptr2, #\off2_lo]
    mls v11.8h, v14.8h, v0.h[0]
    str d12, [\ptr2, #\off2_hi]
    str d24, [\ptr0, #\off0_hi]
    str d19, [\ptr1, #\off1_lo]
    str d13, [\ptr1, #\off1_hi]
    str d11, [\ptr0, #\off0_lo]
.endm

.macro RUN_FUSED_POST_STRIPE ptr0, off0_lo, off0_hi, ptr1, off1_lo, off1_hi, ptr2, off2_lo, off2_hi
.ifdef INVNTT_USE_POST_FUSED_N1_NODFTREDUCE_SLOTHY
    FUSED_POST_STRIPE_N1_NODFTREDUCE_SLOTHY \ptr0, \off0_lo, \off0_hi, \ptr1, \off1_lo, \off1_hi, \ptr2, \off2_lo, \off2_hi
.else
.ifdef INVNTT_USE_POST_FUSED_N1_SLOTHY
    FUSED_POST_STRIPE_N1_SLOTHY \ptr0, \off0_lo, \off0_hi, \ptr1, \off1_lo, \off1_hi, \ptr2, \off2_lo, \off2_hi
.else
.ifdef INVNTT_USE_POST_FUSED_SLOTHY
    FUSED_POST_STRIPE_SLOTHY \ptr0, \off0_lo, \off0_hi, \ptr1, \off1_lo, \off1_hi, \ptr2, \off2_lo, \off2_hi
.else
    FUSED_POST_STRIPE \ptr0, \off0_lo, \off0_hi, \ptr1, \off1_lo, \off1_hi, \ptr2, \off2_lo, \off2_hi
.endif
.endif
.endif
.endm

.ifdef INVNTT_COMPARE_OLD_SYMBOL
.global poly_invntt_old
.global _poly_invntt_old
poly_invntt_old:
_poly_invntt_old:
.else
.ifdef INVNTT_COMPARE_NEW_SYMBOL
.global poly_invntt_new
.global _poly_invntt_new
poly_invntt_new:
_poly_invntt_new:
.else
.global poly_invntt
.global _poly_invntt
poly_invntt:
_poly_invntt:
.endif
.endif
.ifdef INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH
.equ INVNTT_STACK_SIZE, 2080
.equ INVNTT_SAVED_X0_OFFSET, 2088
.else
.equ INVNTT_STACK_SIZE, 1568
.equ INVNTT_SAVED_X0_OFFSET, 1576
.endif
    stp x30, x0, [sp, #-16]!
    sub sp, sp, #INVNTT_STACK_SIZE

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
.ifdef INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW0
    RUN_INVNTT32_STAGE45_SCRATCH_ROW
.else
.ifdef INVNTT_USE_DIRECT_STAGE123
    DIRECT_STAGE123_ROW0
    RUN_INVNTT32_STAGE45_ROW
.else
    DIRECT_LOAD_ROW0
    RUN_INVNTT32_ROW
.endif
.endif

    add x3, x1, #0
    add x4, x1, #768
    add x2, sp, #544
.ifdef INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW1
    RUN_INVNTT32_STAGE45_SCRATCH_ROW
.else
.ifdef INVNTT_USE_DIRECT_STAGE123
    DIRECT_STAGE123_ROW1
    RUN_INVNTT32_STAGE45_ROW
.else
    DIRECT_LOAD_ROW1
    RUN_INVNTT32_ROW
.endif
.endif

    add x3, x1, #0
    add x4, x1, #768
    add x2, sp, #1056
.ifdef INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW2
    RUN_INVNTT32_STAGE45_SCRATCH_ROW
.else
.ifdef INVNTT_USE_DIRECT_STAGE123
    DIRECT_STAGE123_ROW2
    RUN_INVNTT32_STAGE45_ROW
.else
    DIRECT_LOAD_ROW2
    RUN_INVNTT32_ROW
.endif
.endif
.endif

    /* Steps 3-5: inverse DFT3, untwist F_b^k, remove scale 96 in merge. */
    adr x3, inv_consts
    ldr q15, [x3, #16]
    ldr x0, [sp, #INVNTT_SAVED_X0_OFFSET]
    add x8, sp, #32
    add x9, sp, #544
    add x10, sp, #1056
.ifdef INVNTT_USE_POST_BRANCHFOLD
    adr x3, inv_branchfold_vecs
.else
    adr x3, inv_untwist_vecs
.endif

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
    RUN_FUSED_POST_STRIPE x11, 0, 768, x12, 0, 768, x13, 0, 768
    RUN_FUSED_POST_STRIPE x13, 8, 776, x11, 8, 776, x12, 8, 776
    RUN_FUSED_POST_STRIPE x12, 16, 784, x13, 16, 784, x11, 16, 784
    add x11, x11, #24
    add x12, x12, #24
    add x13, x13, #24
    subs x5, x5, #1
    b.ne 4b
    RUN_FUSED_POST_STRIPE x11, 0, 768, x12, 0, 768, x13, 0, 768
    RUN_FUSED_POST_STRIPE x13, 8, 776, x11, 8, 776, x12, 8, 776
slothy_end_invntt_post_fused:

    add sp, sp, #INVNTT_STACK_SIZE
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
.ifdef INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY
    INVNTT32_STAGE45_STRIPE_SLOTHY 0
    INVNTT32_STAGE45_STRIPE_SLOTHY 1
    INVNTT32_STAGE45_STRIPE_SLOTHY 2
    INVNTT32_STAGE45_STRIPE_SLOTHY 3
    INVNTT32_STAGE45_STRIPE_SLOTHY 4
    INVNTT32_STAGE45_STRIPE_SLOTHY 5
    INVNTT32_STAGE45_STRIPE_SLOTHY 6
    INVNTT32_STAGE45_STRIPE_SLOTHY 7
.else
    INVNTT32_STAGE45_STRIPE 0
    INVNTT32_STAGE45_STRIPE 1
    INVNTT32_STAGE45_STRIPE 2
    INVNTT32_STAGE45_STRIPE 3
    INVNTT32_STAGE45_STRIPE 4
    INVNTT32_STAGE45_STRIPE 5
    INVNTT32_STAGE45_STRIPE 6
    INVNTT32_STAGE45_STRIPE 7
.endif
.ifndef INVNTT_ROW_REDUCE_EAGER
.ifndef INVNTT_USE_STAGE45_REDUCE_FUSION
    REDUCE_ROW_ALL
.endif
.endif
slothy_end_invntt32_fixed_stage45:
    ret

_invntt32_8way_stage45_only:
slothy_start_invntt32_stage45_only:
    adr x3, invntt32_stage45_consts
.ifdef INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY
    INVNTT32_STAGE45_STRIPE_SLOTHY 0
    INVNTT32_STAGE45_STRIPE_SLOTHY 1
    INVNTT32_STAGE45_STRIPE_SLOTHY 2
    INVNTT32_STAGE45_STRIPE_SLOTHY 3
    INVNTT32_STAGE45_STRIPE_SLOTHY 4
    INVNTT32_STAGE45_STRIPE_SLOTHY 5
    INVNTT32_STAGE45_STRIPE_SLOTHY 6
    INVNTT32_STAGE45_STRIPE_SLOTHY 7
.else
    INVNTT32_STAGE45_STRIPE 0
    INVNTT32_STAGE45_STRIPE 1
    INVNTT32_STAGE45_STRIPE 2
    INVNTT32_STAGE45_STRIPE 3
    INVNTT32_STAGE45_STRIPE 4
    INVNTT32_STAGE45_STRIPE 5
    INVNTT32_STAGE45_STRIPE 6
    INVNTT32_STAGE45_STRIPE 7
.endif
.ifndef INVNTT_ROW_REDUCE_EAGER
.ifndef INVNTT_USE_STAGE45_REDUCE_FUSION
    REDUCE_ROW_ALL
.endif
.endif
slothy_end_invntt32_stage45_only:
    ret

_invntt32_8way_stage45_from_scratch:
slothy_start_invntt32_stage45_from_scratch:
    adr x3, invntt32_stage45_consts
.ifdef INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH 0
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH 1
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH 2
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH 3
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH 4
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH 5
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH 6
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH 7
.else
    INVNTT32_STAGE45_STRIPE_SCRATCH 0
    INVNTT32_STAGE45_STRIPE_SCRATCH 1
    INVNTT32_STAGE45_STRIPE_SCRATCH 2
    INVNTT32_STAGE45_STRIPE_SCRATCH 3
    INVNTT32_STAGE45_STRIPE_SCRATCH 4
    INVNTT32_STAGE45_STRIPE_SCRATCH 5
    INVNTT32_STAGE45_STRIPE_SCRATCH 6
    INVNTT32_STAGE45_STRIPE_SCRATCH 7
.endif
.ifndef INVNTT_ROW_REDUCE_EAGER
.ifndef INVNTT_USE_STAGE45_REDUCE_FUSION
    REDUCE_ROW_ALL
.endif
.endif
slothy_end_invntt32_stage45_from_scratch:
    ret

.ifdef INVNTT_BENCH_STAGES
.global poly_invntt_bench_rows
.global _poly_invntt_bench_rows
poly_invntt_bench_rows:
_poly_invntt_bench_rows:
    stp x30, x0, [sp, #-16]!
    adr x3, inv_consts
    ldr q0, [x3]

    add x3, x1, #0
    add x4, x1, #768
    add x2, x0, #0
    DIRECT_STAGE123_ROW0
    RUN_INVNTT32_STAGE45_ROW

    ldr x0, [sp, #8]
    add x3, x1, #0
    add x4, x1, #768
    add x2, x0, #512
    DIRECT_STAGE123_ROW1
    RUN_INVNTT32_STAGE45_ROW

    ldr x0, [sp, #8]
    add x3, x1, #0
    add x4, x1, #768
    add x2, x0, #1024
    DIRECT_STAGE123_ROW2
    RUN_INVNTT32_STAGE45_ROW

    ldp x30, x0, [sp], #16
    ret

.global poly_invntt_bench_row0
.global _poly_invntt_bench_row0
poly_invntt_bench_row0:
_poly_invntt_bench_row0:
    stp x30, x0, [sp, #-16]!
    adr x3, inv_consts
    ldr q0, [x3]
    add x3, x1, #0
    add x4, x1, #768
    add x2, x0, #0
    DIRECT_STAGE123_ROW0
    RUN_INVNTT32_STAGE45_ROW
    ldp x30, x0, [sp], #16
    ret

.global poly_invntt_bench_row1
.global _poly_invntt_bench_row1
poly_invntt_bench_row1:
_poly_invntt_bench_row1:
    stp x30, x0, [sp, #-16]!
    adr x3, inv_consts
    ldr q0, [x3]
    add x3, x1, #0
    add x4, x1, #768
    add x2, x0, #0
    DIRECT_STAGE123_ROW1
    RUN_INVNTT32_STAGE45_ROW
    ldp x30, x0, [sp], #16
    ret

.global poly_invntt_bench_row2
.global _poly_invntt_bench_row2
poly_invntt_bench_row2:
_poly_invntt_bench_row2:
    stp x30, x0, [sp, #-16]!
    adr x3, inv_consts
    ldr q0, [x3]
    add x3, x1, #0
    add x4, x1, #768
    add x2, x0, #0
    DIRECT_STAGE123_ROW2
    RUN_INVNTT32_STAGE45_ROW
    ldp x30, x0, [sp], #16
    ret

.global poly_invntt_bench_post
.global _poly_invntt_bench_post
poly_invntt_bench_post:
_poly_invntt_bench_post:
    adr x3, inv_consts
    ldr q0, [x3]
    ldr q15, [x3, #16]
    add x8, x1, #0
    add x9, x1, #512
    add x10, x1, #1024
    adr x3, inv_untwist_vecs
.ifdef INVNTT_USE_POST_FASTSCALE
    // v15.h[2:3] contain ZMINUSZ5INV/192 and its precompute.
.endif
    add x11, x0, #0
    add x12, x0, #512
    add x13, x0, #256
    mov x5, #10
5:
    RUN_FUSED_POST_STRIPE x11, 0, 768, x12, 0, 768, x13, 0, 768
    RUN_FUSED_POST_STRIPE x13, 8, 776, x11, 8, 776, x12, 8, 776
    RUN_FUSED_POST_STRIPE x12, 16, 784, x13, 16, 784, x11, 16, 784
    add x11, x11, #24
    add x12, x12, #24
    add x13, x13, #24
    subs x5, x5, #1
    b.ne 5b
    RUN_FUSED_POST_STRIPE x11, 0, 768, x12, 0, 768, x13, 0, 768
    RUN_FUSED_POST_STRIPE x13, 8, 776, x11, 8, 776, x12, 8, 776
    ret

.global poly_invntt_bench_post_dft3_raw
.global _poly_invntt_bench_post_dft3_raw
poly_invntt_bench_post_dft3_raw:
_poly_invntt_bench_post_dft3_raw:
    adr x3, inv_consts
    ldr q0, [x3]
    mov x2, x0
    add x8, x1, #0
    add x9, x1, #512
    add x10, x1, #1024
    mov x5, #32
6:
    POST_DFT3_STRIPE 0
    subs x5, x5, #1
    b.ne 6b
    ret

.global poly_invntt_bench_post_dft3_reduce
.global _poly_invntt_bench_post_dft3_reduce
poly_invntt_bench_post_dft3_reduce:
_poly_invntt_bench_post_dft3_reduce:
    adr x3, inv_consts
    ldr q0, [x3]
    mov x2, x0
    add x8, x1, #0
    add x9, x1, #512
    add x10, x1, #1024
    mov x5, #32
7:
    POST_DFT3_STRIPE 1
    subs x5, x5, #1
    b.ne 7b
    ret

.global poly_invntt_bench_post_untwist
.global _poly_invntt_bench_post_untwist
poly_invntt_bench_post_untwist:
_poly_invntt_bench_post_untwist:
    adr x3, inv_consts
    ldr q0, [x3]
    adr x3, inv_untwist_vecs
    mov x2, x0
    mov x5, #96
8:
    POST_UNTWIST_STRIPE
    subs x5, x5, #1
    b.ne 8b
    ret

.global poly_invntt_bench_post_finalmerge
.global _poly_invntt_bench_post_finalmerge
poly_invntt_bench_post_finalmerge:
_poly_invntt_bench_post_finalmerge:
    adr x3, inv_consts
    ldr q0, [x3]
    ldr q15, [x3, #16]
    mov x8, x1
    add x11, x0, #0
    add x12, x0, #512
    add x13, x0, #256
    mov x5, #10
9:
    POST_FINAL_MERGE_STRIPE x11, 0, 768, x12, 0, 768, x13, 0, 768
    POST_FINAL_MERGE_STRIPE x13, 8, 776, x11, 8, 776, x12, 8, 776
    POST_FINAL_MERGE_STRIPE x12, 16, 784, x13, 16, 784, x11, 16, 784
    add x11, x11, #24
    add x12, x12, #24
    add x13, x13, #24
    subs x5, x5, #1
    b.ne 9b
    POST_FINAL_MERGE_STRIPE x11, 0, 768, x12, 0, 768, x13, 0, 768
    POST_FINAL_MERGE_STRIPE x13, 8, 776, x11, 8, 776, x12, 8, 776
    ret
.endif

.align 4
inv_consts:
    .hword 3457, 19412, -723, -6853, 1634, 15488, -18, -171
    // h[2:3] are only used by opt-in INVNTT_USE_POST_FASTSCALE.
    .hword -36, -341, 1701, 16123, 0, 0, 0, 0

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

.align 4
inv_branchfold_vecs:
    .include "asm/slothy/invntt_branchfold_vecs.inc"

.purgem BARRETT_REDUCE
.purgem FQMUL_LANE
.purgem INV_BUTTERFLY_LANE
.purgem REDUCE_ROW_VEC
.purgem REDUCE_ROW_ALL
.purgem INVNTT32_STAGE123_BLOCK
.purgem INVNTT32_STAGE45_STRIPE
.purgem INVNTT32_STAGE45_STRIPE_SLOTHY
.purgem INVNTT32_STAGE45_STRIPE_SCRATCH
.purgem INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH
.purgem DIRECT_LOAD_VEC
.purgem DIRECT_STAGE123_VEC
.purgem DIRECT_STAGE123_BLOCK
.purgem STORE_STAGE123_STRIPE_SCRATCH
.purgem DIRECT_STAGE123_BLOCK_TO_SCRATCH
.purgem DIRECT_STAGE123_CONSTS
.purgem DIRECT_STAGE123_ROW0
.purgem DIRECT_STAGE123_ROW1
.purgem DIRECT_STAGE123_ROW2
.purgem DIRECT_STAGE123_STRIPE_SCRATCH_ROW0
.purgem DIRECT_STAGE123_STRIPE_SCRATCH_ROW1
.purgem DIRECT_STAGE123_STRIPE_SCRATCH_ROW2
.purgem DIRECT_LOAD_ROW0
.purgem DIRECT_LOAD_ROW1
.purgem DIRECT_LOAD_ROW2
.purgem RUN_INVNTT32_ROW
.purgem RUN_INVNTT32_STAGE45_ROW
.purgem RUN_INVNTT32_STAGE45_SCRATCH_ROW
.purgem POST_STORE_PTR
.purgem POST_STORE_PTR_BRANCHFOLD
.purgem POST_STORE_PTR_FASTSCALE
.purgem POST_FINAL_STORE_PTR
.purgem FUSED_POST_STRIPE
.purgem POST_DFT3_STRIPE
.purgem POST_UNTWIST_STRIPE
.purgem POST_FINAL_MERGE_STRIPE
.purgem FUSED_POST_STRIPE_SLOTHY
.purgem FUSED_POST_STRIPE_N1_SLOTHY
.purgem FUSED_POST_STRIPE_N1_NODFTREDUCE_SLOTHY
.purgem RUN_FUSED_POST_STRIPE
