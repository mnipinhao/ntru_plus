/*
 * Clean Slothy source for one inverse NTT32 stage45 stripe with row-end
 * reduction fused before the row-buffer store.
 *
 * Contract:
 *   row_base x2 points at one row buffer.
 *   const_ptr x3 points at this stripe's two q-vector twiddle table entries.
 *   v0.h[0] is q and v0.h[1] is the Barrett constant.
 *   Output representatives match INVNTT_USE_STAGE45_REDUCE_FUSION.
 */

row_base .req x2
const_ptr .req x3

.global invntt32_stage45_reduce_fused_symbolic
invntt32_stage45_reduce_fused_symbolic:
slothy_start_invntt32_stage45_reduce_fused:
    ldr Q<tw>, [const_ptr]
    ldr Q<pre>, [const_ptr, #16]
    ldr Q<a0>, [row_base, #0]
    ldr Q<a1>, [row_base, #128]
    ldr Q<a2>, [row_base, #256]
    ldr Q<a3>, [row_base, #384]

    sqrdmulh V<q0>.8h, V<a1>.8h, V<pre>.h[0]
    mul      V<p0>.8h, V<a1>.8h, V<tw>.h[0]
    mls      V<p0>.8h, V<q0>.8h, v0.h[0]
    add      V<b0>.8h, V<a0>.8h, V<p0>.8h
    sub      V<b1>.8h, V<a0>.8h, V<p0>.8h

    sqrdmulh V<q1>.8h, V<a3>.8h, V<pre>.h[0]
    mul      V<p1>.8h, V<a3>.8h, V<tw>.h[0]
    mls      V<p1>.8h, V<q1>.8h, v0.h[0]
    add      V<b2>.8h, V<a2>.8h, V<p1>.8h
    sub      V<b3>.8h, V<a2>.8h, V<p1>.8h

    sqrdmulh V<q2>.8h, V<b2>.8h, V<pre>.h[1]
    mul      V<p2>.8h, V<b2>.8h, V<tw>.h[1]
    mls      V<p2>.8h, V<q2>.8h, v0.h[0]
    add      V<c0>.8h, V<b0>.8h, V<p2>.8h
    sub      V<c2>.8h, V<b0>.8h, V<p2>.8h

    sqrdmulh V<q3>.8h, V<b3>.8h, V<pre>.h[2]
    mul      V<p3>.8h, V<b3>.8h, V<tw>.h[2]
    mls      V<p3>.8h, V<q3>.8h, v0.h[0]
    add      V<c1>.8h, V<b1>.8h, V<p3>.8h
    sub      V<c3>.8h, V<b1>.8h, V<p3>.8h

    sqdmulh V<r0>.8h, V<c0>.8h, v0.h[1]
    sqdmulh V<r1>.8h, V<c1>.8h, v0.h[1]
    sqdmulh V<r2>.8h, V<c2>.8h, v0.h[1]
    sqdmulh V<r3>.8h, V<c3>.8h, v0.h[1]
    srshr   V<r0>.8h, V<r0>.8h, #11
    srshr   V<r1>.8h, V<r1>.8h, #11
    srshr   V<r2>.8h, V<r2>.8h, #11
    srshr   V<r3>.8h, V<r3>.8h, #11
    mls     V<c0>.8h, V<r0>.8h, v0.h[0]
    mls     V<c1>.8h, V<r1>.8h, v0.h[0]
    mls     V<c2>.8h, V<r2>.8h, v0.h[0]
    mls     V<c3>.8h, V<r3>.8h, v0.h[0]

    str Q<c0>, [row_base, #0]
    str Q<c1>, [row_base, #128]
    str Q<c2>, [row_base, #256]
    str Q<c3>, [row_base, #384]
slothy_end_invntt32_stage45_reduce_fused:

    ret

.unreq row_base
.unreq const_ptr
