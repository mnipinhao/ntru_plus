/*
 * Clean Slothy source for one production-equivalent fused post-row stripe.
 *
 * Contract:
 *   x8/x9/x10 load row0/row1/row2 in natural k32 order with post-increment.
 *   x3 points at inv_untwist_vecs for this stripe and advances by 96 bytes.
 *   x11/x12/x13 are output store bases for this stripe.
 *   v0 holds q/Barrett/DFT3/merge scale constants.
 *   v15 holds final 1/96 constants.
 *
 * This source preserves the production d-store behavior exactly.
 */

.global invntt_post_fused_dstore_symbolic
invntt_post_fused_dstore_symbolic:
slothy_start_invntt_post_fused_dstore:
    ldr Q<row0>, [x8], #16
    ldr Q<row1>, [x9], #16
    ldr Q<row2>, [x10], #16

    sub      V<diff21>.8h, V<row2>.8h, V<row1>.8h
    sqrdmulh V<q_dft>.8h, V<diff21>.8h, v0.h[3]
    mul      V<t_dft>.8h, V<diff21>.8h, v0.h[2]
    mls      V<t_dft>.8h, V<q_dft>.8h, v0.h[0]

    add      V<dft0_a>.8h, V<row0>.8h, V<row1>.8h
    add      V<dft0>.8h, V<dft0_a>.8h, V<row2>.8h
    sqdmulh  V<r_dft0>.8h, V<dft0>.8h, v0.h[1]
    srshr    V<r_dft0>.8h, V<r_dft0>.8h, #11
    mls      V<dft0>.8h, V<r_dft0>.8h, v0.h[0]

    sub      V<dft1_a>.8h, V<row0>.8h, V<row1>.8h
    add      V<dft1>.8h, V<dft1_a>.8h, V<t_dft>.8h
    sqdmulh  V<r_dft1>.8h, V<dft1>.8h, v0.h[1]
    srshr    V<r_dft1>.8h, V<r_dft1>.8h, #11
    mls      V<dft1>.8h, V<r_dft1>.8h, v0.h[0]

    sub      V<dft2_a>.8h, V<row0>.8h, V<row2>.8h
    sub      V<dft2>.8h, V<dft2_a>.8h, V<t_dft>.8h
    sqdmulh  V<r_dft2>.8h, V<dft2>.8h, v0.h[1]
    srshr    V<r_dft2>.8h, V<r_dft2>.8h, #11
    mls      V<dft2>.8h, V<r_dft2>.8h, v0.h[0]

    ldr      Q<tw0>, [x3], #16
    ldr      Q<pre0>, [x3], #16
    sqrdmulh V<uq0>.8h, V<dft0>.8h, V<pre0>.8h
    mul      V<u0>.8h, V<dft0>.8h, V<tw0>.8h
    mls      V<u0>.8h, V<uq0>.8h, v0.h[0]
    ext      V<u0_sw>.16b, V<u0>.16b, V<u0>.16b, #8
    add      V<u0_sum>.8h, V<u0>.8h, V<u0_sw>.8h
    sub      V<u0_diff>.8h, V<u0>.8h, V<u0_sw>.8h
    sqrdmulh V<u0_mq>.8h, V<u0_diff>.8h, v0.h[5]
    mul      V<u0_m>.8h, V<u0_diff>.8h, v0.h[4]
    mls      V<u0_m>.8h, V<u0_mq>.8h, v0.h[0]
    sub      V<u0_o0_in>.8h, V<u0_sum>.8h, V<u0_m>.8h
    sqrdmulh V<u0_o0_q>.8h, V<u0_o0_in>.8h, v0.h[7]
    mul      V<u0_o0>.8h, V<u0_o0_in>.8h, v0.h[6]
    mls      V<u0_o0>.8h, V<u0_o0_q>.8h, v0.h[0]
    sqrdmulh V<u0_o1_q>.8h, V<u0_m>.8h, v15.h[1]
    mul      V<u0_o1>.8h, V<u0_m>.8h, v15.h[0]
    mls      V<u0_o1>.8h, V<u0_o1_q>.8h, v0.h[0]

    ldr      Q<tw1>, [x3], #16
    ldr      Q<pre1>, [x3], #16
    sqrdmulh V<uq1>.8h, V<dft1>.8h, V<pre1>.8h
    mul      V<u1>.8h, V<dft1>.8h, V<tw1>.8h
    mls      V<u1>.8h, V<uq1>.8h, v0.h[0]
    ext      V<u1_sw>.16b, V<u1>.16b, V<u1>.16b, #8
    add      V<u1_sum>.8h, V<u1>.8h, V<u1_sw>.8h
    sub      V<u1_diff>.8h, V<u1>.8h, V<u1_sw>.8h
    sqrdmulh V<u1_mq>.8h, V<u1_diff>.8h, v0.h[5]
    mul      V<u1_m>.8h, V<u1_diff>.8h, v0.h[4]
    mls      V<u1_m>.8h, V<u1_mq>.8h, v0.h[0]
    sub      V<u1_o0_in>.8h, V<u1_sum>.8h, V<u1_m>.8h
    sqrdmulh V<u1_o0_q>.8h, V<u1_o0_in>.8h, v0.h[7]
    mul      V<u1_o0>.8h, V<u1_o0_in>.8h, v0.h[6]
    mls      V<u1_o0>.8h, V<u1_o0_q>.8h, v0.h[0]
    sqrdmulh V<u1_o1_q>.8h, V<u1_m>.8h, v15.h[1]
    mul      V<u1_o1>.8h, V<u1_m>.8h, v15.h[0]
    mls      V<u1_o1>.8h, V<u1_o1_q>.8h, v0.h[0]

    ldr      Q<tw2>, [x3], #16
    ldr      Q<pre2>, [x3], #16
    sqrdmulh V<uq2>.8h, V<dft2>.8h, V<pre2>.8h
    mul      V<u2>.8h, V<dft2>.8h, V<tw2>.8h
    mls      V<u2>.8h, V<uq2>.8h, v0.h[0]
    ext      V<u2_sw>.16b, V<u2>.16b, V<u2>.16b, #8
    add      V<u2_sum>.8h, V<u2>.8h, V<u2_sw>.8h
    sub      V<u2_diff>.8h, V<u2>.8h, V<u2_sw>.8h
    sqrdmulh V<u2_mq>.8h, V<u2_diff>.8h, v0.h[5]
    mul      V<u2_m>.8h, V<u2_diff>.8h, v0.h[4]
    mls      V<u2_m>.8h, V<u2_mq>.8h, v0.h[0]
    sub      V<u2_o0_in>.8h, V<u2_sum>.8h, V<u2_m>.8h
    sqrdmulh V<u2_o0_q>.8h, V<u2_o0_in>.8h, v0.h[7]
    mul      V<u2_o0>.8h, V<u2_o0_in>.8h, v0.h[6]
    mls      V<u2_o0>.8h, V<u2_o0_q>.8h, v0.h[0]
    sqrdmulh V<u2_o1_q>.8h, V<u2_m>.8h, v15.h[1]
    mul      V<u2_o1>.8h, V<u2_m>.8h, v15.h[0]
    mls      V<u2_o1>.8h, V<u2_o1_q>.8h, v0.h[0]

    /*
     * Slothy's current AArch64 model in this checkout lacks non-stack d-store
     * parsing, so the clean source uses q stores as live-out placeholders.  The
     * integrated opt-in macro keeps production's final d stores.
     */
    str Q<u0_o0>, [x11, #0]
    str Q<u0_o1>, [x11, #768]
    str Q<u1_o0>, [x12, #0]
    str Q<u1_o1>, [x12, #768]
    str Q<u2_o0>, [x13, #0]
    str Q<u2_o1>, [x13, #768]
slothy_end_invntt_post_fused_dstore:

    ret
