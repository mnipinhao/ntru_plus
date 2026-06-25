/*
 * Production-only AArch64 NEON inverse NTT for the Good-Thomas row-bitrev
 * layout produced by asm/my_ntt.s.
 *
 * This file is intentionally smaller than asm/slothy/invntt_opt.s.  It keeps
 * only the path currently wired into production wrappers:
 *   - direct physical input -> inverse NTT32 stage123
 *   - stage123 stripe scratch laid out for stage45 consumption
 *   - Slothy-scheduled stage45 + row-end Barrett reduction fusion
 *   - branchfold post path with final output reductions
 *   - rminus1 branchfold table switch through INVNTT_INPUT_RMINUS1
 *
 * Rowstage45/post prototypes, bench-only symbols, old gather, and fastscale
 * experiments live in asm/slothy/archive/invntt_rowstage45_post_prototypes.s
 * and the legacy superset asm/slothy/invntt_opt.s.
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
     * Candidate A direct-tuple input already stores each GT row contiguously:
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

.macro RUN_INVNTT32_STAGE45_SCRATCH_ROW
    bl _invntt32_8way_stage45_from_scratch
.endm

.macro POST_STORE_PTR xvec, ptr, off_lo, off_hi
    POST_STORE_PTR_BRANCHFOLD \xvec, \ptr, \off_lo, \off_hi
.endm

.macro LOAD_BRANCHFOLD_CONSTS
    ldr     q10, [x3], #16    // low normal constants
    ldr     q11, [x3], #16    // low sqrdmulh precompute
    ldr     q12, [x3], #16    // high normal constants
    ldr     q13, [x3], #16    // high sqrdmulh precompute
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

.macro FUSED_POST_STRIPE ptr0, off0_lo, off0_hi, ptr1, off1_lo, off1_hi, ptr2, off2_lo, off2_hi
    ldr q1, [x8], #16
    ldr q2, [x9], #16
    ldr q3, [x10], #16

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

.ifndef INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH
.error "invntt_opt.production.s requires INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH"
.endif
.ifndef INVNTT_USE_STAGE45_REDUCE_FUSION
.error "invntt_opt.production.s requires INVNTT_USE_STAGE45_REDUCE_FUSION"
.endif
.ifndef INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY
.error "invntt_opt.production.s requires INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY"
.endif
.ifndef INVNTT_USE_POST_BRANCHFOLD
.error "invntt_opt.production.s requires INVNTT_USE_POST_BRANCHFOLD"
.endif
.ifndef INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS
.error "invntt_opt.production.s requires INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS"
.endif

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
.global gt_tuple_poly_invntt
.global _gt_tuple_poly_invntt

.ifndef INVNTT_NO_POLY_ALIAS
poly_invntt:
_poly_invntt:
.endif
gt_block_major_poly_invntt:
_gt_block_major_poly_invntt:
    mov w15, #0
    b L_invntt_entry_common
gt_tuple_poly_invntt:
_gt_tuple_poly_invntt:
    mov w15, #1
    b L_invntt_entry_common

L_invntt_entry_common:
.equ INVNTT_STACK_SIZE, 2080
.equ INVNTT_SAVED_X0_OFFSET, 2088
    stp x30, x0, [sp, #-16]!
    sub sp, sp, #INVNTT_STACK_SIZE
    str w15, [sp]

    adr x3, inv_consts
    ldr q0, [x3]

    ldr w15, [sp]
    cbnz w15, L_invntt_tuple_row0
    add x3, x1, #0
    add x4, x1, #768
    add x2, sp, #32
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW0
    b L_invntt_row0_done
L_invntt_tuple_row0:
    add x3, x1, #0
    add x4, x1, #768
    add x2, sp, #32
    add x14, sp, #1568
    TUPLE_STAGE123_STRIPE_SCRATCH_ROW_BODY
L_invntt_row0_done:
    RUN_INVNTT32_STAGE45_SCRATCH_ROW

    ldr w15, [sp]
    cbnz w15, L_invntt_tuple_row1
    add x3, x1, #0
    add x4, x1, #768
    add x2, sp, #544
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW1
    b L_invntt_row1_done
L_invntt_tuple_row1:
    add x3, x1, #256
    add x4, x1, #1024
    add x2, sp, #544
    add x14, sp, #1568
    TUPLE_STAGE123_STRIPE_SCRATCH_ROW_BODY
L_invntt_row1_done:
    RUN_INVNTT32_STAGE45_SCRATCH_ROW

    ldr w15, [sp]
    cbnz w15, L_invntt_tuple_row2
    add x3, x1, #0
    add x4, x1, #768
    add x2, sp, #1056
    DIRECT_STAGE123_STRIPE_SCRATCH_ROW2
    b L_invntt_row2_done
L_invntt_tuple_row2:
    add x3, x1, #512
    add x4, x1, #1280
    add x2, sp, #1056
    add x14, sp, #1568
    TUPLE_STAGE123_STRIPE_SCRATCH_ROW_BODY
L_invntt_row2_done:
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
slothy_start_invntt_post_fused:
    RUN_FUSED_POST_LOOP 4
slothy_end_invntt_post_fused:

    add sp, sp, #INVNTT_STACK_SIZE
    ldp x30, x0, [sp], #16
    ret

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
    str x1, [sp]

    adr x3, inv_consts
    ldr q0, [x3]

    ldr x14, [sp]
    add x2, sp, #32
    RUN_INVNTT32_STAGE45_SCRATCH_ROW

    ldr x14, [sp]
    add x14, x14, #512
    add x2, sp, #544
    RUN_INVNTT32_STAGE45_SCRATCH_ROW

    ldr x14, [sp]
    add x14, x14, #1024
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

    add sp, sp, #INVNTT_STACK_SIZE
    ldp x30, x0, [sp], #16
    ret
.endif

_invntt32_8way_stage45_from_scratch:
slothy_start_invntt32_stage45_from_scratch:
    adr x3, invntt32_stage45_consts
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH 0
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH 1
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH 2
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH 3
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH 4
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH 5
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH 6
    INVNTT32_STAGE45_STRIPE_SLOTHY_SCRATCH 7
slothy_end_invntt32_stage45_from_scratch:
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
.ifdef INVNTT_INPUT_RMINUS1
    .include "asm/slothy/invntt_branchfold_vecs_rminus1.inc"
.else
    .include "asm/slothy/invntt_branchfold_vecs.inc"
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
.purgem RUN_INVNTT32_STAGE45_SCRATCH_ROW
.purgem POST_STORE_PTR
.purgem LOAD_BRANCHFOLD_CONSTS
.purgem POST_STORE_PTR_BRANCHFOLD
.purgem FUSED_POST_STRIPE
.purgem RUN_FUSED_POST_STRIPE
.purgem RUN_FUSED_POST_3STRIPE_GROUP
.purgem RUN_FUSED_POST_3STRIPE_LOOP
.purgem RUN_FUSED_POST_LOOP
