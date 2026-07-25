/*
 * Production-only AArch64 NEON inverse NTT for the Good-Thomas row-bitrev
 * layout produced by asm/gt/ntt/poly_ntt_body.inc.
 *
 * This file keeps only the path currently wired into production wrappers:
 *   - direct physical input -> inverse NTT32 stage123
 *   - stage123 stripe scratch laid out for stage45 consumption
 *   - Slothy-scheduled stage45 + row-end Barrett reduction fusion
 *   - branchfold post path with final output reductions
 *   - rminus1 branchfold table switch through INVNTT_INPUT_RMINUS1
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

.ifdef INVNTT_EXPERIMENT_LAZY_TWIDDLE1_STAGE123
.ifndef INVNTT_USE_LAZY_TWIDDLE1_STAGE123
.equ INVNTT_USE_LAZY_TWIDDLE1_STAGE123, 1
.endif
.endif
.ifdef INVNTT_EXPERIMENT_LAZY_TWIDDLE1_LEN16
.ifndef INVNTT_USE_LAZY_TWIDDLE1_LEN16
.equ INVNTT_USE_LAZY_TWIDDLE1_LEN16, 1
.endif
.endif

.macro INV_BUTTERFLY_IDENTITY_LAZY lo, hi, tmp
    /* Proof-gated twiddle=1 path with the reduction intentionally deferred. */
    mov      \tmp\().16b, \lo\().16b
    add      \lo\().8h, \lo\().8h, \hi\().8h
    sub      \hi\().8h, \tmp\().8h, \hi\().8h
.endm

.macro INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH j
    /*
     * Same A72 stage45+row-end-reduce schedule as
     * INVNTT32_STAGE45_STRIPE_SLOTHY, but it reads the stage123 outputs from
     * stripe-major scratch:
     *   [j, j+8, j+16, j+24] at x14 + 64*j.
     */
    ldr q11, [x14, #(64 * \j + 48)]
    ldr q7, [x3, #(32 * \j + 16)]
    ldr q30, [x14, #(64 * \j + 32)]
    ldr q5, [x3, #(32 * \j)]
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
.ifdef INVNTT_USE_LAZY_TWIDDLE1_STAGE123
    INV_BUTTERFLY_IDENTITY_LAZY v3, v4, v12
    INV_BUTTERFLY_IDENTITY_LAZY v5, v6, v12
    INV_BUTTERFLY_IDENTITY_LAZY v7, v8, v12
    INV_BUTTERFLY_IDENTITY_LAZY v9, v10, v12
.else
    INV_BUTTERFLY_LANE v3, v4, v1, 0, v2, 0, v11, v12
    INV_BUTTERFLY_LANE v5, v6, v1, 0, v2, 0, v11, v12
    INV_BUTTERFLY_LANE v7, v8, v1, 0, v2, 0, v11, v12
    INV_BUTTERFLY_LANE v9, v10, v1, 0, v2, 0, v11, v12
.endif

    /* len=4 */
.ifdef INVNTT_USE_LAZY_TWIDDLE1_STAGE123
    INV_BUTTERFLY_IDENTITY_LAZY v3, v5, v12
.else
    INV_BUTTERFLY_LANE v3, v5, v1, 0, v2, 0, v11, v12
.endif
    INV_BUTTERFLY_LANE v4, v6, v1, 1, v2, 1, v11, v12
.ifdef INVNTT_USE_LAZY_TWIDDLE1_STAGE123
    INV_BUTTERFLY_IDENTITY_LAZY v7, v9, v12
.else
    INV_BUTTERFLY_LANE v7, v9, v1, 0, v2, 0, v11, v12
.endif
    INV_BUTTERFLY_LANE v8, v10, v1, 1, v2, 1, v11, v12

    /* len=8 */
.ifdef INVNTT_USE_LAZY_TWIDDLE1_STAGE123
    INV_BUTTERFLY_IDENTITY_LAZY v3, v7, v12
.else
    INV_BUTTERFLY_LANE v3, v7, v1, 0, v2, 0, v11, v12
.endif
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

	.macro TUPLE_STAGE123_STRIPE_SCRATCH_ROW_BODY
    /*
     * Row-contiguous tuple input already stores each GT row contiguously:
     *   tuple[branch][row][k32][quartic_lane].
     *
     * Point x3/x4 at the branch0/branch1 row bases before invoking this macro.
     * Then the inverse row-stage123 input order is simply k32 = 0..31, i.e.
     * byte offsets 8*k32, while block-major input needs the physical
     * 3-stride offsets used by DIRECT_STAGE123_STRIPE_SCRATCH_ROW{0,1,2}.
     */
    DIRECT_STAGE123_CONSTS
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 0,   0,   8,  16,  24,  32,  40,  48,  56
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 1,  64,  72,  80,  88,  96, 104, 112, 120
    DIRECT_STAGE123_BLOCK_TO_SCRATCH 2, 128, 136, 144, 152, 160, 168, 176, 184
	    DIRECT_STAGE123_BLOCK_TO_SCRATCH 3, 192, 200, 208, 216, 224, 232, 240, 248
	.endm

	.macro BPQ_STAGE123_VEC dst, srcoff
	    /*
	     * Candidate B branch-pair-Q input stores one inverse NTT32 vector as:
	     *   q = [branch0 quartic lane0..3 | branch1 quartic lane0..3].
	     *
	     * That is exactly the register shape stage123 wants after the old
	     * block-major/tuple loaders had paired two D halves, so BPQ can use a
	     * single Q load per k32.
	     */
	    ldr q\dst, [x3, #\srcoff]
	.endm

	.macro BPQ_STAGE123_BLOCK_TO_SCRATCH group, off0, off1, off2, off3, off4, off5, off6, off7
	    BPQ_STAGE123_VEC 3, \off0
	    BPQ_STAGE123_VEC 4, \off1
	    BPQ_STAGE123_VEC 5, \off2
	    BPQ_STAGE123_VEC 6, \off3
	    BPQ_STAGE123_VEC 7, \off4
	    BPQ_STAGE123_VEC 8, \off5
	    BPQ_STAGE123_VEC 9, \off6
	    BPQ_STAGE123_VEC 10, \off7

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

	.macro BPQ_STAGE123_STRIPE_SCRATCH_ROW_BODY
	    /*
	     * Candidate B BPQ row layout:
	     *   bpq[row][k32] = q{branch0 lanes0..3, branch1 lanes0..3}
	     *
	     * Each row is 32 Q records = 512 bytes.  The inverse stage123 order is
	     * k32 = 0..31, so the offsets are simply 16*k32.
	     */
	    DIRECT_STAGE123_CONSTS
	    /* Direct-BPQ block0 physical order is [3,2,5,0,7,6,4,1]. */
	    BPQ_STAGE123_BLOCK_TO_SCRATCH 0,  48, 112,  16,   0,  96,  32,  80,  64
	    BPQ_STAGE123_BLOCK_TO_SCRATCH 1, 128, 144, 160, 176, 192, 208, 224, 240
	    BPQ_STAGE123_BLOCK_TO_SCRATCH 2, 256, 272, 288, 304, 320, 336, 352, 368
	    BPQ_STAGE123_BLOCK_TO_SCRATCH 3, 384, 400, 416, 432, 448, 464, 480, 496
	.endm

	.ifdef INVNTT_EXPOSE_BPQ_CQ
	.macro BPQ_CQ_LOAD4 out0, out1, out2, out3, base
	    ldp q\out0, q\out1, [x3, #(\base + 0)]
	    ldp q\out2, q\out3, [x3, #(\base + 32)]
	    trn1 v11.8h, v\out0\().8h, v\out1\().8h
	    trn2 v12.8h, v\out0\().8h, v\out1\().8h
	    trn1 v13.8h, v\out2\().8h, v\out3\().8h
	    trn2 v14.8h, v\out2\().8h, v\out3\().8h
	    trn1 v\out0\().4s, v11.4s, v13.4s
	    trn2 v\out2\().4s, v11.4s, v13.4s
	    trn1 v\out1\().4s, v12.4s, v14.4s
	    trn2 v\out3\().4s, v12.4s, v14.4s
	.endm

	.macro BPQ_CQ_STAGE123_REGS_TO_SCRATCH group
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

	.macro BPQ_CQ_STAGE123_BLOCK_TO_SCRATCH group, base
	    /* Undo two adjacent 4x4 CQ tiles entirely in registers. */
	    BPQ_CQ_LOAD4 3, 4, 5, 6, \base
	    BPQ_CQ_LOAD4 7, 8, 9, 10, (\base + 64)
	    BPQ_CQ_STAGE123_REGS_TO_SCRATCH \group
	.endm

	.macro BPQ_CQ_STAGE123_BLOCK0_TO_SCRATCH
	    /*
	     * Map BPQ slots [0..7] directly to inverse k32 register order
	     * [3,7,1,0,6,2,5,4] while undoing the two CQ transposes.
	     */
	    BPQ_CQ_LOAD4 6, 5, 8, 3, 0
	    BPQ_CQ_LOAD4 10, 9, 7, 4, 64
	    BPQ_CQ_STAGE123_REGS_TO_SCRATCH 0
	.endm

	.macro BPQ_CQ_STAGE123_STRIPE_SCRATCH_ROW_BODY
	    /* 32 k32 values are stored as eight consecutive 4x4 CQ tiles. */
	    DIRECT_STAGE123_CONSTS
	    BPQ_CQ_STAGE123_BLOCK0_TO_SCRATCH
	    BPQ_CQ_STAGE123_BLOCK_TO_SCRATCH 1, 128
	    BPQ_CQ_STAGE123_BLOCK_TO_SCRATCH 2, 256
	    BPQ_CQ_STAGE123_BLOCK_TO_SCRATCH 3, 384
	.endm
	.endif

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
.ifndef INVNTT_USE_LAZY_TWIDDLE1_LEN16
        sqrdmulh v24.8H, v17.8H, v14.H[0]
        sqrdmulh v20.8H, v21.8H, v14.H[0]
        mul v3.8H, v17.8H, v13.H[0]
        mls v3.8H, v24.8H, v0.H[0]
        mul v1.8H, v21.8H, v13.H[0]
        mls v1.8H, v20.8H, v0.H[0]
.endif
.ifdef INVNTT_USE_LAZY_TWIDDLE1_LEN16
        sub v30.8H, v29.8H, v17.8H
        add v26.8H, v29.8H, v17.8H
.else
        sub v30.8H, v29.8H, v3.8H
        add v26.8H, v29.8H, v3.8H
.endif
        sqrdmulh v7.8H, v30.8H, v14.H[2]
        mul v17.8H, v30.8H, v13.H[2]
.ifdef INVNTT_USE_LAZY_TWIDDLE1_LEN16
        add v20.8H, v8.8H, v21.8H
        sub v21.8H, v8.8H, v21.8H
.else
        sub v21.8H, v8.8H, v1.8H
.endif
        sqrdmulh v24.8H, v26.8H, v14.H[1]
        ldr q4, [x3, #48]
        ldr q18, [x14, #112]
        mls v17.8H, v7.8H, v0.H[0]
        ldr q7, [x3, #32]
        mul v14.8H, v26.8H, v13.H[1]
        mls v14.8H, v24.8H, v0.H[0]
.ifndef INVNTT_USE_LAZY_TWIDDLE1_LEN16
        add v20.8H, v8.8H, v1.8H
.endif
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

.macro INVOKE_INVNTT32_STAGE45_SCRATCH_ROW
.ifdef INVNTT_USE_STAGE45_ROW_HELPER
    bl .Linvntt32_stage45_scratch_row_helper
.else
    RUN_INVNTT32_STAGE45_SCRATCH_ROW
.endif
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
     * representatives and is not safe for poly_crepmod3.  The production gate
     * always pairs this with INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS, which adds
     * final Barrett reductions and matched the exact C-reference output for
     * forward-produced GT inputs.
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

.ifdef INVNTT_EXPERIMENT_POST_BRANCHFOLD_THREE_SLOTHY
    .include "asm/gt/invntt/poly_invntt_post_branchfold.n1.opt.inc"
.endif

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

.ifdef INVNTT_EXPERIMENT_POST_BRANCHFOLD_THREE_SLOTHY
    INVNTT_POST_BRANCHFOLD_THREE_SLOTHY \ptr0, \off0_lo, \off0_hi, \ptr1, \off1_lo, \off1_hi, \ptr2, \off2_lo, \off2_hi
.else
    POST_STORE_PTR v7, \ptr0, \off0_lo, \off0_hi
    POST_STORE_PTR v8, \ptr1, \off1_lo, \off1_hi
    POST_STORE_PTR v9, \ptr2, \off2_lo, \off2_hi
.endif
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

.ifndef INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH
.error "poly_invntt.n1.opt.inc requires INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH"
.endif
.ifndef INVNTT_USE_STAGE45_REDUCE_FUSION
.error "poly_invntt.n1.opt.inc requires INVNTT_USE_STAGE45_REDUCE_FUSION"
.endif
.ifndef INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY
.error "poly_invntt.n1.opt.inc requires INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY"
.endif
.ifndef INVNTT_USE_POST_BRANCHFOLD
.error "poly_invntt.n1.opt.inc requires INVNTT_USE_POST_BRANCHFOLD"
.endif
.ifndef INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS
.error "poly_invntt.n1.opt.inc requires INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS"
.endif

.ifdef INVNTT_PRESERVE_CALLEE_SAVED_SIMD
.equ INVNTT_SIMD_SAVE_OFFSET, 2080
.equ INVNTT_STACK_SIZE, 2144
.else
.equ INVNTT_STACK_SIZE, 2080
.endif
.equ INVNTT_SAVED_X0_OFFSET, (INVNTT_STACK_SIZE + 8)

.macro INVNTT_SAVE_CALLEE_SAVED_SIMD
.ifdef INVNTT_PRESERVE_CALLEE_SAVED_SIMD
    add x16, sp, #INVNTT_SIMD_SAVE_OFFSET
    stp d8, d9, [x16, #0]
    stp d10, d11, [x16, #16]
    stp d12, d13, [x16, #32]
    stp d14, d15, [x16, #48]
.endif
.endm

.macro INVNTT_RESTORE_CALLEE_SAVED_SIMD
.ifdef INVNTT_PRESERVE_CALLEE_SAVED_SIMD
    add x16, sp, #INVNTT_SIMD_SAVE_OFFSET
    ldp d8, d9, [x16, #0]
    ldp d10, d11, [x16, #16]
    ldp d12, d13, [x16, #32]
    ldp d14, d15, [x16, #48]
.endif
.endm

.ifndef INVNTT_STAGE123_SCRATCH_ONLY
.ifndef INVNTT_NO_POLY_ALIAS
.ifndef INVNTT_DARWIN_NO_WEAK
.weak poly_invntt
.weak _poly_invntt
.else
.global poly_invntt
.global _poly_invntt
.endif
.endif
	.global gt_block_major_poly_invntt
	.global _gt_block_major_poly_invntt
	.ifndef INVNTT_BLOCK_MAJOR_ONLY
	.global gt_tuple_poly_invntt
	.global _gt_tuple_poly_invntt
	.global gt_bpq_poly_invntt
	.global _gt_bpq_poly_invntt
	.ifdef INVNTT_EXPOSE_BPQ_CQ
	.global gt_bpq_cq_poly_invntt
	.global _gt_bpq_cq_poly_invntt
	.endif
	.endif

.ifndef INVNTT_NO_POLY_ALIAS
poly_invntt:
_poly_invntt:
.endif
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
    /*
     * Slothy target markers for the production block-major path.  The
     * rminus1 wrapper aliases this same code and only switches the final
     * branchfold constant table through INVNTT_INPUT_RMINUS1.
     *
     * These labels are markers only: do not move prologue, epilogue, or
     * branchfold post code into a first Slothy pass.
     */
slothy_start_invntt_block_row0_stage123:
.ifdef INVNTT_USE_STAGE123_PAIR_PIPELINE
    INVNTT_STAGE123_PAIR_ROW0_BODY
.else
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW0
.endif
slothy_end_invntt_block_row0_stage123:
    /*
     * live-in: x14 = stage123 stripe scratch at sp+1568,
     *          x2 = row0 row-buffer base at sp+32,
     *          q0 = q / Barrett constants.
     * live-out: row0 natural-order stage45 output at [x2].
     */
slothy_start_invntt_block_row0_stage45:
    INVOKE_INVNTT32_STAGE45_SCRATCH_ROW
slothy_end_invntt_block_row0_stage45:

    add x3, x1, #0
    add x4, x1, #768
    add x2, sp, #544
slothy_start_invntt_block_row1_stage123:
.ifdef INVNTT_USE_STAGE123_PAIR_PIPELINE
    INVNTT_STAGE123_PAIR_ROW1_BODY
.else
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW1
.endif
slothy_end_invntt_block_row1_stage123:
    /*
     * live-in: x14 = stage123 stripe scratch at sp+1568,
     *          x2 = row1 row-buffer base at sp+544,
     *          q0 = q / Barrett constants.
     * live-out: row1 natural-order stage45 output at [x2].
     */
slothy_start_invntt_block_row1_stage45:
    INVOKE_INVNTT32_STAGE45_SCRATCH_ROW
slothy_end_invntt_block_row1_stage45:

    add x3, x1, #0
    add x4, x1, #768
    add x2, sp, #1056
slothy_start_invntt_block_row2_stage123:
.ifdef INVNTT_USE_STAGE123_PAIR_PIPELINE
    INVNTT_STAGE123_PAIR_ROW2_BODY
.else
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW2
.endif
slothy_end_invntt_block_row2_stage123:
    /*
     * live-in: x14 = stage123 stripe scratch at sp+1568,
     *          x2 = row2 row-buffer base at sp+1056,
     *          q0 = q / Barrett constants.
     * live-out: row2 natural-order stage45 output at [x2].
     */
slothy_start_invntt_block_row2_stage45:
    INVOKE_INVNTT32_STAGE45_SCRATCH_ROW
slothy_end_invntt_block_row2_stage45:
    b L_invntt_post_tail

	.ifndef INVNTT_BLOCK_MAJOR_ONLY
gt_tuple_poly_invntt:
_gt_tuple_poly_invntt:
    stp x30, x0, [sp, #-16]!
    sub sp, sp, #INVNTT_STACK_SIZE
    INVNTT_SAVE_CALLEE_SAVED_SIMD

    adr x3, inv_consts
    ldr q0, [x3]

    add x3, x1, #0
    add x4, x1, #768
    add x2, sp, #32
    add x14, sp, #1568
    TUPLE_STAGE123_STRIPE_SCRATCH_ROW_BODY
    RUN_INVNTT32_STAGE45_SCRATCH_ROW

    add x3, x1, #256
    add x4, x1, #1024
    add x2, sp, #544
    add x14, sp, #1568
    TUPLE_STAGE123_STRIPE_SCRATCH_ROW_BODY
    RUN_INVNTT32_STAGE45_SCRATCH_ROW

	    add x3, x1, #512
	    add x4, x1, #1280
	    add x2, sp, #1056
	    add x14, sp, #1568
	    TUPLE_STAGE123_STRIPE_SCRATCH_ROW_BODY
	    RUN_INVNTT32_STAGE45_SCRATCH_ROW
	    b L_invntt_post_tail

	gt_bpq_poly_invntt:
	_gt_bpq_poly_invntt:
	    stp x30, x0, [sp, #-16]!
	    sub sp, sp, #INVNTT_STACK_SIZE
	    INVNTT_SAVE_CALLEE_SAVED_SIMD

	    adr x3, inv_consts
	    ldr q0, [x3]

	    add x3, x1, #0
	    add x2, sp, #32
	    add x14, sp, #1568
	    BPQ_STAGE123_STRIPE_SCRATCH_ROW_BODY
	    RUN_INVNTT32_STAGE45_SCRATCH_ROW

	    add x3, x1, #512
	    add x2, sp, #544
	    add x14, sp, #1568
	    BPQ_STAGE123_STRIPE_SCRATCH_ROW_BODY
	    RUN_INVNTT32_STAGE45_SCRATCH_ROW

	    add x3, x1, #1024
	    add x2, sp, #1056
	    add x14, sp, #1568
	    BPQ_STAGE123_STRIPE_SCRATCH_ROW_BODY
	    RUN_INVNTT32_STAGE45_SCRATCH_ROW
	.ifdef INVNTT_EXPOSE_BPQ_CQ
	    b L_invntt_post_tail
	.endif

	.ifdef INVNTT_EXPOSE_BPQ_CQ
	gt_bpq_cq_poly_invntt:
	_gt_bpq_cq_poly_invntt:
	    stp x30, x0, [sp, #-16]!
	    sub sp, sp, #INVNTT_STACK_SIZE
	    INVNTT_SAVE_CALLEE_SAVED_SIMD

	    adr x3, inv_consts
	    ldr q0, [x3]

	    add x3, x1, #0
	    add x2, sp, #32
	    add x14, sp, #1568
	    BPQ_CQ_STAGE123_STRIPE_SCRATCH_ROW_BODY
	    RUN_INVNTT32_STAGE45_SCRATCH_ROW

	    add x3, x1, #512
	    add x2, sp, #544
	    add x14, sp, #1568
	    BPQ_CQ_STAGE123_STRIPE_SCRATCH_ROW_BODY
	    RUN_INVNTT32_STAGE45_SCRATCH_ROW

	    add x3, x1, #1024
	    add x2, sp, #1056
	    add x14, sp, #1568
	    BPQ_CQ_STAGE123_STRIPE_SCRATCH_ROW_BODY
	    RUN_INVNTT32_STAGE45_SCRATCH_ROW
	.endif
	.endif

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
slothy_start_invntt_post_fused:
    RUN_FUSED_POST_LOOP 4
slothy_end_invntt_post_fused:

    INVNTT_RESTORE_CALLEE_SAVED_SIMD
    add sp, sp, #INVNTT_STACK_SIZE
    ldp x30, x0, [sp], #16
    ret

.ifdef INVNTT_USE_STAGE45_ROW_HELPER
.p2align 4
.Linvntt32_stage45_scratch_row_helper:
    RUN_INVNTT32_STAGE45_SCRATCH_ROW
    ret
.endif
.endif

.ifdef INVNTT_EXPOSE_STAGE123_SCRATCH_ABI
.global gt_block_major_to_stage123_stripe_scratch
.global _gt_block_major_to_stage123_stripe_scratch
gt_block_major_to_stage123_stripe_scratch:
_gt_block_major_to_stage123_stripe_scratch:
    adr x5, inv_consts
    ldr q0, [x5]

    add x3, x1, #0
    add x4, x1, #768
    add x14, x0, #0
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW0_BODY

    add x3, x1, #0
    add x4, x1, #768
    add x14, x0, #512
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW1_BODY

    add x3, x1, #0
    add x4, x1, #768
    add x14, x0, #1024
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW2_BODY
    ret

.global gt_tuple_to_stage123_stripe_scratch
.global _gt_tuple_to_stage123_stripe_scratch
gt_tuple_to_stage123_stripe_scratch:
_gt_tuple_to_stage123_stripe_scratch:
    adr x5, inv_consts
    ldr q0, [x5]

    add x3, x1, #0
    add x4, x1, #768
    add x14, x0, #0
    TUPLE_STAGE123_STRIPE_SCRATCH_ROW_BODY

    add x3, x1, #256
    add x4, x1, #1024
    add x14, x0, #512
    TUPLE_STAGE123_STRIPE_SCRATCH_ROW_BODY

    add x3, x1, #512
    add x4, x1, #1280
    add x14, x0, #1024
    TUPLE_STAGE123_STRIPE_SCRATCH_ROW_BODY
    ret

.global poly_invntt_stage45scratch
.global _poly_invntt_stage45scratch
poly_invntt_stage45scratch:
_poly_invntt_stage45scratch:
    stp x30, x0, [sp, #-16]!
    sub sp, sp, #INVNTT_STACK_SIZE
    INVNTT_SAVE_CALLEE_SAVED_SIMD
    mov x15, x1

    adr x3, inv_consts
    ldr q0, [x3]

    mov x14, x15
    add x2, sp, #32
    RUN_INVNTT32_STAGE45_SCRATCH_ROW

    add x14, x15, #512
    add x2, sp, #544
    RUN_INVNTT32_STAGE45_SCRATCH_ROW

    add x14, x15, #1024
    add x2, sp, #1056
    RUN_INVNTT32_STAGE45_SCRATCH_ROW

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
    add sp, sp, #INVNTT_STACK_SIZE
    ldp x30, x0, [sp], #16
    ret
.endif

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
.ifdef INVNTT_INPUT_RMINUS1
    .include "asm/gt/invntt/poly_invntt_branchfold_constants_rminus1.inc"
.else
    .include "asm/gt/invntt/poly_invntt_branchfold_constants.inc"
.endif

.purgem BARRETT_REDUCE
.purgem FQMUL_LANE
.purgem INV_BUTTERFLY_LANE
.purgem INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH
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
.purgem TUPLE_STAGE123_STRIPE_SCRATCH_ROW_BODY
.purgem BPQ_STAGE123_VEC
.purgem BPQ_STAGE123_BLOCK_TO_SCRATCH
.purgem BPQ_STAGE123_STRIPE_SCRATCH_ROW_BODY
.ifdef INVNTT_EXPOSE_BPQ_CQ
.purgem BPQ_CQ_LOAD4
.purgem BPQ_CQ_STAGE123_REGS_TO_SCRATCH
.purgem BPQ_CQ_STAGE123_BLOCK_TO_SCRATCH
.purgem BPQ_CQ_STAGE123_BLOCK0_TO_SCRATCH
.purgem BPQ_CQ_STAGE123_STRIPE_SCRATCH_ROW_BODY
.endif
.purgem RUN_INVNTT32_STAGE45_SCRATCH_ROW
.purgem INVOKE_INVNTT32_STAGE45_SCRATCH_ROW
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
.ifdef INVNTT_EXPERIMENT_POST_BRANCHFOLD_THREE_SLOTHY
.purgem INVNTT_POST_BRANCHFOLD_THREE_SLOTHY
.endif
