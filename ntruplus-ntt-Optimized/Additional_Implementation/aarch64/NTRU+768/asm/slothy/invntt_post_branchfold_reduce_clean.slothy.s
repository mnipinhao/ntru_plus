/*
 * Clean Slothy source for one branchfold-reduce fused post-row stripe.
 *
 * Contract:
 *   x8/x9/x10 load row0/row1/row2 in natural k32 order with post-increment.
 *   x3 points at inv_branchfold_vecs for this stripe and advances by 192 bytes.
 *   x11/x12/x13 are output store bases for this stripe.
 *   v0 holds q/Barrett/DFT3 constants.
 *
 * This source models the promoted branchfold path:
 *   inverse DFT3 without post-DFT3 reductions,
 *   branch-constant folded untwist/final merge,
 *   final output Barrett reductions.
 *
 * The clean source uses q stores as live-out placeholders because the local
 * Slothy parser is more reliable for q stores than non-stack d stores.  The
 * integrated macro converts these back to production d stores.
 */

.global invntt_post_branchfold_reduce_symbolic
invntt_post_branchfold_reduce_symbolic:
slothy_start_invntt_post_branchfold_reduce:
    ldr Q<row0>, [x8], #16
    ldr Q<row1>, [x9], #16
    ldr Q<row2>, [x10], #16

    sub      V<diff21>.8h, V<row2>.8h, V<row1>.8h
    sqrdmulh V<q_dft>.8h, V<diff21>.8h, v0.h[3]
    mul      V<t_dft>.8h, V<diff21>.8h, v0.h[2]
    mls      V<t_dft>.8h, V<q_dft>.8h, v0.h[0]

    add      V<dft0_a>.8h, V<row0>.8h, V<row1>.8h
    add      V<dft0>.8h, V<dft0_a>.8h, V<row2>.8h

    sub      V<dft1_a>.8h, V<row0>.8h, V<row1>.8h
    add      V<dft1>.8h, V<dft1_a>.8h, V<t_dft>.8h

    sub      V<dft2_a>.8h, V<row0>.8h, V<row2>.8h
    sub      V<dft2>.8h, V<dft2_a>.8h, V<t_dft>.8h

    ldr      Q<lo0>, [x3], #16
    ldr      Q<lopre0>, [x3], #16
    ldr      Q<hi0>, [x3], #16
    ldr      Q<hipre0>, [x3], #16
    sqrdmulh V<loq0>.8h, V<dft0>.8h, V<lopre0>.8h
    mul      V<loprod0>.8h, V<dft0>.8h, V<lo0>.8h
    mls      V<loprod0>.8h, V<loq0>.8h, v0.h[0]
    ext      V<losw0>.16b, V<loprod0>.16b, V<loprod0>.16b, #8
    add      V<outlo0>.8h, V<loprod0>.8h, V<losw0>.8h
    sqrdmulh V<hiq0>.8h, V<dft0>.8h, V<hipre0>.8h
    mul      V<hiprod0>.8h, V<dft0>.8h, V<hi0>.8h
    mls      V<hiprod0>.8h, V<hiq0>.8h, v0.h[0]
    ext      V<hisw0>.16b, V<hiprod0>.16b, V<hiprod0>.16b, #8
    add      V<outhi0>.8h, V<hiprod0>.8h, V<hisw0>.8h
    sqdmulh  V<redlo0>.8h, V<outlo0>.8h, v0.h[1]
    srshr    V<redlo0>.8h, V<redlo0>.8h, #11
    mls      V<outlo0>.8h, V<redlo0>.8h, v0.h[0]
    sqdmulh  V<redhi0>.8h, V<outhi0>.8h, v0.h[1]
    srshr    V<redhi0>.8h, V<redhi0>.8h, #11
    mls      V<outhi0>.8h, V<redhi0>.8h, v0.h[0]

    ldr      Q<lo1>, [x3], #16
    ldr      Q<lopre1>, [x3], #16
    ldr      Q<hi1>, [x3], #16
    ldr      Q<hipre1>, [x3], #16
    sqrdmulh V<loq1>.8h, V<dft1>.8h, V<lopre1>.8h
    mul      V<loprod1>.8h, V<dft1>.8h, V<lo1>.8h
    mls      V<loprod1>.8h, V<loq1>.8h, v0.h[0]
    ext      V<losw1>.16b, V<loprod1>.16b, V<loprod1>.16b, #8
    add      V<outlo1>.8h, V<loprod1>.8h, V<losw1>.8h
    sqrdmulh V<hiq1>.8h, V<dft1>.8h, V<hipre1>.8h
    mul      V<hiprod1>.8h, V<dft1>.8h, V<hi1>.8h
    mls      V<hiprod1>.8h, V<hiq1>.8h, v0.h[0]
    ext      V<hisw1>.16b, V<hiprod1>.16b, V<hiprod1>.16b, #8
    add      V<outhi1>.8h, V<hiprod1>.8h, V<hisw1>.8h
    sqdmulh  V<redlo1>.8h, V<outlo1>.8h, v0.h[1]
    srshr    V<redlo1>.8h, V<redlo1>.8h, #11
    mls      V<outlo1>.8h, V<redlo1>.8h, v0.h[0]
    sqdmulh  V<redhi1>.8h, V<outhi1>.8h, v0.h[1]
    srshr    V<redhi1>.8h, V<redhi1>.8h, #11
    mls      V<outhi1>.8h, V<redhi1>.8h, v0.h[0]

    ldr      Q<lo2>, [x3], #16
    ldr      Q<lopre2>, [x3], #16
    ldr      Q<hi2>, [x3], #16
    ldr      Q<hipre2>, [x3], #16
    sqrdmulh V<loq2>.8h, V<dft2>.8h, V<lopre2>.8h
    mul      V<loprod2>.8h, V<dft2>.8h, V<lo2>.8h
    mls      V<loprod2>.8h, V<loq2>.8h, v0.h[0]
    ext      V<losw2>.16b, V<loprod2>.16b, V<loprod2>.16b, #8
    add      V<outlo2>.8h, V<loprod2>.8h, V<losw2>.8h
    sqrdmulh V<hiq2>.8h, V<dft2>.8h, V<hipre2>.8h
    mul      V<hiprod2>.8h, V<dft2>.8h, V<hi2>.8h
    mls      V<hiprod2>.8h, V<hiq2>.8h, v0.h[0]
    ext      V<hisw2>.16b, V<hiprod2>.16b, V<hiprod2>.16b, #8
    add      V<outhi2>.8h, V<hiprod2>.8h, V<hisw2>.8h
    sqdmulh  V<redlo2>.8h, V<outlo2>.8h, v0.h[1]
    srshr    V<redlo2>.8h, V<redlo2>.8h, #11
    mls      V<outlo2>.8h, V<redlo2>.8h, v0.h[0]
    sqdmulh  V<redhi2>.8h, V<outhi2>.8h, v0.h[1]
    srshr    V<redhi2>.8h, V<redhi2>.8h, #11
    mls      V<outhi2>.8h, V<redhi2>.8h, v0.h[0]

    str Q<outlo0>, [x11, #0]
    str Q<outhi0>, [x11, #768]
    str Q<outlo1>, [x12, #0]
    str Q<outhi1>, [x12, #768]
    str Q<outlo2>, [x13, #0]
    str Q<outhi2>, [x13, #768]
slothy_end_invntt_post_branchfold_reduce:

    ret
