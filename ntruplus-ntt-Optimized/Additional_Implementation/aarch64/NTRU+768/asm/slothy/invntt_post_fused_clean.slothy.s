/*
 * Symbolic Slothy source for one fused post-row inverse stripe.
 *
 * Contract at entry:
 *   row0,row1,row2 are natural k32 order after inverse row NTT32
 *   lanes = [branch0 q0..q3, branch1 q0..q3]
 *   row scale factor 32 is present
 *
 * This region performs one natural k32 stripe:
 *   1. load row0[k32], row1[k32], row2[k32]
 *   2. inverse DFT3 in registers, leaving factor 3
 *   3. untwist each of the three resulting logical k vectors by F_b^k
 *   4. final branch merge with 1/96 or 1/192 scale folded in
 *   5. store final natural coefficients using fixed immediate offsets
 *
 * Constants are normal centered multipliers plus sqrdmulh precompute.
 * v0.h[0] = q, v0.h[1] = Barrett multiplier,
 * v0.h[2:3] = omega3/precompute,
 * v0.h[4:5] = ZMINUSZ5INV/precompute,
 * v0.h[6:7] = 1/192/precompute,
 * v15.h[0:1] = 1/96/precompute.
 *
 * The production kernel stores d-register halves.  This local Slothy AArch64
 * model does not parse symbolic d-register stores to general addresses, so
 * this clean source uses q stores to keep the same value/address dependencies
 * for scheduling and register allocation.  Do not assemble this helper as the
 * production implementation.
 */

.global invntt_post_fused_symbolic
invntt_post_fused_symbolic:
slothy_start_invntt_post_fused_stripe:
    ldr Q<r0>, [x8], #16
    ldr Q<r1>, [x9], #16
    ldr Q<r2>, [x10], #16

    sub      V<d>.8h, V<r2>.8h, V<r1>.8h
    sqrdmulh V<d_q>.8h, V<d>.8h, v0.h[3]
    mul      V<t>.8h, V<d>.8h, v0.h[2]
    mls      V<t>.8h, V<d_q>.8h, v0.h[0]

    add      V<dft0_raw>.8h, V<r0>.8h, V<r1>.8h
    add      V<dft0>.8h, V<dft0_raw>.8h, V<r2>.8h
    sqdmulh  V<dft0_red>.8h, V<dft0>.8h, v0.h[1]
    srshr    V<dft0_red>.8h, V<dft0_red>.8h, #11
    mls      V<dft0>.8h, V<dft0_red>.8h, v0.h[0]

    sub      V<dft1_raw>.8h, V<r0>.8h, V<r1>.8h
    add      V<dft1>.8h, V<dft1_raw>.8h, V<t>.8h
    sqdmulh  V<dft1_red>.8h, V<dft1>.8h, v0.h[1]
    srshr    V<dft1_red>.8h, V<dft1_red>.8h, #11
    mls      V<dft1>.8h, V<dft1_red>.8h, v0.h[0]

    sub      V<dft2_raw>.8h, V<r0>.8h, V<r2>.8h
    sub      V<dft2>.8h, V<dft2_raw>.8h, V<t>.8h
    sqdmulh  V<dft2_red>.8h, V<dft2>.8h, v0.h[1]
    srshr    V<dft2_red>.8h, V<dft2_red>.8h, #11
    mls      V<dft2>.8h, V<dft2_red>.8h, v0.h[0]

    ldr Q<tw0>, [x3], #16
    ldr Q<pre0>, [x3], #16
    sqrdmulh V<u0_q>.8h, V<dft0>.8h, V<pre0>.8h
    mul      V<u0>.8h, V<dft0>.8h, V<tw0>.8h
    mls      V<u0>.8h, V<u0_q>.8h, v0.h[0]
    ext      V<u0_sw>.16b, V<u0>.16b, V<u0>.16b, #8
    add      V<u0_sum>.8h, V<u0>.8h, V<u0_sw>.8h
    sub      V<u0_diff>.8h, V<u0>.8h, V<u0_sw>.8h
    sqrdmulh V<u0_z_q>.8h, V<u0_diff>.8h, v0.h[5]
    mul      V<u0_z>.8h, V<u0_diff>.8h, v0.h[4]
    mls      V<u0_z>.8h, V<u0_z_q>.8h, v0.h[0]
    sub      V<u0_lo_in>.8h, V<u0_sum>.8h, V<u0_z>.8h
    sqrdmulh V<u0_lo_q>.8h, V<u0_lo_in>.8h, v0.h[7]
    mul      V<u0_lo>.8h, V<u0_lo_in>.8h, v0.h[6]
    mls      V<u0_lo>.8h, V<u0_lo_q>.8h, v0.h[0]
    sqrdmulh V<u0_hi_q>.8h, V<u0_z>.8h, v15.h[1]
    mul      V<u0_hi>.8h, V<u0_z>.8h, v15.h[0]
    mls      V<u0_hi>.8h, V<u0_hi_q>.8h, v0.h[0]
    str      Q<u0_lo>, [x0, #0]
    str      Q<u0_hi>, [x0, #768]

    ldr Q<tw1>, [x3], #16
    ldr Q<pre1>, [x3], #16
    sqrdmulh V<u1_q>.8h, V<dft1>.8h, V<pre1>.8h
    mul      V<u1>.8h, V<dft1>.8h, V<tw1>.8h
    mls      V<u1>.8h, V<u1_q>.8h, v0.h[0]
    ext      V<u1_sw>.16b, V<u1>.16b, V<u1>.16b, #8
    add      V<u1_sum>.8h, V<u1>.8h, V<u1_sw>.8h
    sub      V<u1_diff>.8h, V<u1>.8h, V<u1_sw>.8h
    sqrdmulh V<u1_z_q>.8h, V<u1_diff>.8h, v0.h[5]
    mul      V<u1_z>.8h, V<u1_diff>.8h, v0.h[4]
    mls      V<u1_z>.8h, V<u1_z_q>.8h, v0.h[0]
    sub      V<u1_lo_in>.8h, V<u1_sum>.8h, V<u1_z>.8h
    sqrdmulh V<u1_lo_q>.8h, V<u1_lo_in>.8h, v0.h[7]
    mul      V<u1_lo>.8h, V<u1_lo_in>.8h, v0.h[6]
    mls      V<u1_lo>.8h, V<u1_lo_q>.8h, v0.h[0]
    sqrdmulh V<u1_hi_q>.8h, V<u1_z>.8h, v15.h[1]
    mul      V<u1_hi>.8h, V<u1_z>.8h, v15.h[0]
    mls      V<u1_hi>.8h, V<u1_hi_q>.8h, v0.h[0]
    str      Q<u1_lo>, [x0, #512]
    str      Q<u1_hi>, [x0, #1280]

    ldr Q<tw2>, [x3], #16
    ldr Q<pre2>, [x3], #16
    sqrdmulh V<u2_q>.8h, V<dft2>.8h, V<pre2>.8h
    mul      V<u2>.8h, V<dft2>.8h, V<tw2>.8h
    mls      V<u2>.8h, V<u2_q>.8h, v0.h[0]
    ext      V<u2_sw>.16b, V<u2>.16b, V<u2>.16b, #8
    add      V<u2_sum>.8h, V<u2>.8h, V<u2_sw>.8h
    sub      V<u2_diff>.8h, V<u2>.8h, V<u2_sw>.8h
    sqrdmulh V<u2_z_q>.8h, V<u2_diff>.8h, v0.h[5]
    mul      V<u2_z>.8h, V<u2_diff>.8h, v0.h[4]
    mls      V<u2_z>.8h, V<u2_z_q>.8h, v0.h[0]
    sub      V<u2_lo_in>.8h, V<u2_sum>.8h, V<u2_z>.8h
    sqrdmulh V<u2_lo_q>.8h, V<u2_lo_in>.8h, v0.h[7]
    mul      V<u2_lo>.8h, V<u2_lo_in>.8h, v0.h[6]
    mls      V<u2_lo>.8h, V<u2_lo_q>.8h, v0.h[0]
    sqrdmulh V<u2_hi_q>.8h, V<u2_z>.8h, v15.h[1]
    mul      V<u2_hi>.8h, V<u2_z>.8h, v15.h[0]
    mls      V<u2_hi>.8h, V<u2_hi_q>.8h, v0.h[0]
    str      Q<u2_lo>, [x0, #256]
    str      Q<u2_hi>, [x0, #1024]
slothy_end_invntt_post_fused_stripe:
    ret
