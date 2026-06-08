/*
 * Symbolic Slothy source for the fixed-stage inverse NTT32 row kernel.
 *
 * Contract is identical to _invntt32_8way_table:
 *   input order  = row-bitrev k32 order
 *   output order = natural k32 order
 *   lanes        = [branch0 q0..q3, branch1 q0..q3]
 *   scale        = 32, unnormalized
 *   constants    = normal centered multipliers + sqrdmulh precompute
 *
 * Production asm/slothy/invntt_opt.s repeats the stage123 block four times
 * and the stage45 stripe eight times with fixed offsets.  These two regions
 * are the Slothy allocation/scheduling source for those repeated bodies.
 */

row_base .req x2
const_ptr .req x3

.global invntt32_fixed_symbolic
invntt32_fixed_symbolic:
slothy_start_invntt32_fixed_stage123:
    ldr Q<tw>, [const_ptr]
    ldr Q<pre>, [const_ptr, #16]
    ldr Q<a0_s0>, [row_base, #16*0]
    ldr Q<a1_s0>, [row_base, #16*1]
    ldr Q<a2_s0>, [row_base, #16*2]
    ldr Q<a3_s0>, [row_base, #16*3]
    ldr Q<a4_s0>, [row_base, #16*4]
    ldr Q<a5_s0>, [row_base, #16*5]
    ldr Q<a6_s0>, [row_base, #16*6]
    ldr Q<a7_s0>, [row_base, #16*7]
    sqrdmulh V<q_s1_0>.8h, V<a1_s0>.8h, V<pre>.h[0]
    mul      V<p_s1_0>.8h, V<a1_s0>.8h, V<tw>.h[0]
    mls      V<p_s1_0>.8h, V<q_s1_0>.8h, v0.h[0]
    add      V<a0_s1>.8h, V<a0_s0>.8h, V<p_s1_0>.8h
    sub      V<a1_s1>.8h, V<a0_s0>.8h, V<p_s1_0>.8h
    sqdmulh  V<sr_s1_0>.8h, V<a0_s1>.8h, v0.h[1]
    sqdmulh  V<dr_s1_0>.8h, V<a1_s1>.8h, v0.h[1]
    srshr    V<sr_s1_0>.8h, V<sr_s1_0>.8h, #11
    srshr    V<dr_s1_0>.8h, V<dr_s1_0>.8h, #11
    mls      V<a0_s1>.8h, V<sr_s1_0>.8h, v0.h[0]
    mls      V<a1_s1>.8h, V<dr_s1_0>.8h, v0.h[0]
    sqrdmulh V<q_s1_1>.8h, V<a3_s0>.8h, V<pre>.h[0]
    mul      V<p_s1_1>.8h, V<a3_s0>.8h, V<tw>.h[0]
    mls      V<p_s1_1>.8h, V<q_s1_1>.8h, v0.h[0]
    add      V<a2_s1>.8h, V<a2_s0>.8h, V<p_s1_1>.8h
    sub      V<a3_s1>.8h, V<a2_s0>.8h, V<p_s1_1>.8h
    sqdmulh  V<sr_s1_1>.8h, V<a2_s1>.8h, v0.h[1]
    sqdmulh  V<dr_s1_1>.8h, V<a3_s1>.8h, v0.h[1]
    srshr    V<sr_s1_1>.8h, V<sr_s1_1>.8h, #11
    srshr    V<dr_s1_1>.8h, V<dr_s1_1>.8h, #11
    mls      V<a2_s1>.8h, V<sr_s1_1>.8h, v0.h[0]
    mls      V<a3_s1>.8h, V<dr_s1_1>.8h, v0.h[0]
    sqrdmulh V<q_s1_2>.8h, V<a5_s0>.8h, V<pre>.h[0]
    mul      V<p_s1_2>.8h, V<a5_s0>.8h, V<tw>.h[0]
    mls      V<p_s1_2>.8h, V<q_s1_2>.8h, v0.h[0]
    add      V<a4_s1>.8h, V<a4_s0>.8h, V<p_s1_2>.8h
    sub      V<a5_s1>.8h, V<a4_s0>.8h, V<p_s1_2>.8h
    sqdmulh  V<sr_s1_2>.8h, V<a4_s1>.8h, v0.h[1]
    sqdmulh  V<dr_s1_2>.8h, V<a5_s1>.8h, v0.h[1]
    srshr    V<sr_s1_2>.8h, V<sr_s1_2>.8h, #11
    srshr    V<dr_s1_2>.8h, V<dr_s1_2>.8h, #11
    mls      V<a4_s1>.8h, V<sr_s1_2>.8h, v0.h[0]
    mls      V<a5_s1>.8h, V<dr_s1_2>.8h, v0.h[0]
    sqrdmulh V<q_s1_3>.8h, V<a7_s0>.8h, V<pre>.h[0]
    mul      V<p_s1_3>.8h, V<a7_s0>.8h, V<tw>.h[0]
    mls      V<p_s1_3>.8h, V<q_s1_3>.8h, v0.h[0]
    add      V<a6_s1>.8h, V<a6_s0>.8h, V<p_s1_3>.8h
    sub      V<a7_s1>.8h, V<a6_s0>.8h, V<p_s1_3>.8h
    sqdmulh  V<sr_s1_3>.8h, V<a6_s1>.8h, v0.h[1]
    sqdmulh  V<dr_s1_3>.8h, V<a7_s1>.8h, v0.h[1]
    srshr    V<sr_s1_3>.8h, V<sr_s1_3>.8h, #11
    srshr    V<dr_s1_3>.8h, V<dr_s1_3>.8h, #11
    mls      V<a6_s1>.8h, V<sr_s1_3>.8h, v0.h[0]
    mls      V<a7_s1>.8h, V<dr_s1_3>.8h, v0.h[0]
    sqrdmulh V<q_s2_0>.8h, V<a2_s1>.8h, V<pre>.h[0]
    mul      V<p_s2_0>.8h, V<a2_s1>.8h, V<tw>.h[0]
    mls      V<p_s2_0>.8h, V<q_s2_0>.8h, v0.h[0]
    add      V<a0_s2>.8h, V<a0_s1>.8h, V<p_s2_0>.8h
    sub      V<a2_s2>.8h, V<a0_s1>.8h, V<p_s2_0>.8h
    sqdmulh  V<sr_s2_0>.8h, V<a0_s2>.8h, v0.h[1]
    sqdmulh  V<dr_s2_0>.8h, V<a2_s2>.8h, v0.h[1]
    srshr    V<sr_s2_0>.8h, V<sr_s2_0>.8h, #11
    srshr    V<dr_s2_0>.8h, V<dr_s2_0>.8h, #11
    mls      V<a0_s2>.8h, V<sr_s2_0>.8h, v0.h[0]
    mls      V<a2_s2>.8h, V<dr_s2_0>.8h, v0.h[0]
    sqrdmulh V<q_s2_1>.8h, V<a3_s1>.8h, V<pre>.h[1]
    mul      V<p_s2_1>.8h, V<a3_s1>.8h, V<tw>.h[1]
    mls      V<p_s2_1>.8h, V<q_s2_1>.8h, v0.h[0]
    add      V<a1_s2>.8h, V<a1_s1>.8h, V<p_s2_1>.8h
    sub      V<a3_s2>.8h, V<a1_s1>.8h, V<p_s2_1>.8h
    sqdmulh  V<sr_s2_1>.8h, V<a1_s2>.8h, v0.h[1]
    sqdmulh  V<dr_s2_1>.8h, V<a3_s2>.8h, v0.h[1]
    srshr    V<sr_s2_1>.8h, V<sr_s2_1>.8h, #11
    srshr    V<dr_s2_1>.8h, V<dr_s2_1>.8h, #11
    mls      V<a1_s2>.8h, V<sr_s2_1>.8h, v0.h[0]
    mls      V<a3_s2>.8h, V<dr_s2_1>.8h, v0.h[0]
    sqrdmulh V<q_s2_2>.8h, V<a6_s1>.8h, V<pre>.h[0]
    mul      V<p_s2_2>.8h, V<a6_s1>.8h, V<tw>.h[0]
    mls      V<p_s2_2>.8h, V<q_s2_2>.8h, v0.h[0]
    add      V<a4_s2>.8h, V<a4_s1>.8h, V<p_s2_2>.8h
    sub      V<a6_s2>.8h, V<a4_s1>.8h, V<p_s2_2>.8h
    sqdmulh  V<sr_s2_2>.8h, V<a4_s2>.8h, v0.h[1]
    sqdmulh  V<dr_s2_2>.8h, V<a6_s2>.8h, v0.h[1]
    srshr    V<sr_s2_2>.8h, V<sr_s2_2>.8h, #11
    srshr    V<dr_s2_2>.8h, V<dr_s2_2>.8h, #11
    mls      V<a4_s2>.8h, V<sr_s2_2>.8h, v0.h[0]
    mls      V<a6_s2>.8h, V<dr_s2_2>.8h, v0.h[0]
    sqrdmulh V<q_s2_3>.8h, V<a7_s1>.8h, V<pre>.h[1]
    mul      V<p_s2_3>.8h, V<a7_s1>.8h, V<tw>.h[1]
    mls      V<p_s2_3>.8h, V<q_s2_3>.8h, v0.h[0]
    add      V<a5_s2>.8h, V<a5_s1>.8h, V<p_s2_3>.8h
    sub      V<a7_s2>.8h, V<a5_s1>.8h, V<p_s2_3>.8h
    sqdmulh  V<sr_s2_3>.8h, V<a5_s2>.8h, v0.h[1]
    sqdmulh  V<dr_s2_3>.8h, V<a7_s2>.8h, v0.h[1]
    srshr    V<sr_s2_3>.8h, V<sr_s2_3>.8h, #11
    srshr    V<dr_s2_3>.8h, V<dr_s2_3>.8h, #11
    mls      V<a5_s2>.8h, V<sr_s2_3>.8h, v0.h[0]
    mls      V<a7_s2>.8h, V<dr_s2_3>.8h, v0.h[0]
    sqrdmulh V<q_s3_0>.8h, V<a4_s2>.8h, V<pre>.h[0]
    mul      V<p_s3_0>.8h, V<a4_s2>.8h, V<tw>.h[0]
    mls      V<p_s3_0>.8h, V<q_s3_0>.8h, v0.h[0]
    add      V<a0_s3>.8h, V<a0_s2>.8h, V<p_s3_0>.8h
    sub      V<a4_s3>.8h, V<a0_s2>.8h, V<p_s3_0>.8h
    sqdmulh  V<sr_s3_0>.8h, V<a0_s3>.8h, v0.h[1]
    sqdmulh  V<dr_s3_0>.8h, V<a4_s3>.8h, v0.h[1]
    srshr    V<sr_s3_0>.8h, V<sr_s3_0>.8h, #11
    srshr    V<dr_s3_0>.8h, V<dr_s3_0>.8h, #11
    mls      V<a0_s3>.8h, V<sr_s3_0>.8h, v0.h[0]
    mls      V<a4_s3>.8h, V<dr_s3_0>.8h, v0.h[0]
    sqrdmulh V<q_s3_1>.8h, V<a5_s2>.8h, V<pre>.h[2]
    mul      V<p_s3_1>.8h, V<a5_s2>.8h, V<tw>.h[2]
    mls      V<p_s3_1>.8h, V<q_s3_1>.8h, v0.h[0]
    add      V<a1_s3>.8h, V<a1_s2>.8h, V<p_s3_1>.8h
    sub      V<a5_s3>.8h, V<a1_s2>.8h, V<p_s3_1>.8h
    sqdmulh  V<sr_s3_1>.8h, V<a1_s3>.8h, v0.h[1]
    sqdmulh  V<dr_s3_1>.8h, V<a5_s3>.8h, v0.h[1]
    srshr    V<sr_s3_1>.8h, V<sr_s3_1>.8h, #11
    srshr    V<dr_s3_1>.8h, V<dr_s3_1>.8h, #11
    mls      V<a1_s3>.8h, V<sr_s3_1>.8h, v0.h[0]
    mls      V<a5_s3>.8h, V<dr_s3_1>.8h, v0.h[0]
    sqrdmulh V<q_s3_2>.8h, V<a6_s2>.8h, V<pre>.h[3]
    mul      V<p_s3_2>.8h, V<a6_s2>.8h, V<tw>.h[3]
    mls      V<p_s3_2>.8h, V<q_s3_2>.8h, v0.h[0]
    add      V<a2_s3>.8h, V<a2_s2>.8h, V<p_s3_2>.8h
    sub      V<a6_s3>.8h, V<a2_s2>.8h, V<p_s3_2>.8h
    sqdmulh  V<sr_s3_2>.8h, V<a2_s3>.8h, v0.h[1]
    sqdmulh  V<dr_s3_2>.8h, V<a6_s3>.8h, v0.h[1]
    srshr    V<sr_s3_2>.8h, V<sr_s3_2>.8h, #11
    srshr    V<dr_s3_2>.8h, V<dr_s3_2>.8h, #11
    mls      V<a2_s3>.8h, V<sr_s3_2>.8h, v0.h[0]
    mls      V<a6_s3>.8h, V<dr_s3_2>.8h, v0.h[0]
    sqrdmulh V<q_s3_3>.8h, V<a7_s2>.8h, V<pre>.h[4]
    mul      V<p_s3_3>.8h, V<a7_s2>.8h, V<tw>.h[4]
    mls      V<p_s3_3>.8h, V<q_s3_3>.8h, v0.h[0]
    add      V<a3_s3>.8h, V<a3_s2>.8h, V<p_s3_3>.8h
    sub      V<a7_s3>.8h, V<a3_s2>.8h, V<p_s3_3>.8h
    sqdmulh  V<sr_s3_3>.8h, V<a3_s3>.8h, v0.h[1]
    sqdmulh  V<dr_s3_3>.8h, V<a7_s3>.8h, v0.h[1]
    srshr    V<sr_s3_3>.8h, V<sr_s3_3>.8h, #11
    srshr    V<dr_s3_3>.8h, V<dr_s3_3>.8h, #11
    mls      V<a3_s3>.8h, V<sr_s3_3>.8h, v0.h[0]
    mls      V<a7_s3>.8h, V<dr_s3_3>.8h, v0.h[0]
    str Q<a0_s3>, [row_base, #16*0]
    str Q<a1_s3>, [row_base, #16*1]
    str Q<a2_s3>, [row_base, #16*2]
    str Q<a3_s3>, [row_base, #16*3]
    str Q<a4_s3>, [row_base, #16*4]
    str Q<a5_s3>, [row_base, #16*5]
    str Q<a6_s3>, [row_base, #16*6]
    str Q<a7_s3>, [row_base, #16*7]
slothy_end_invntt32_fixed_stage123:

slothy_start_invntt32_fixed_stage45:
    ldr Q<tw45>, [const_ptr]
    ldr Q<pre45>, [const_ptr, #16]
    ldr Q<b0_s0>, [row_base, #16*0]
    ldr Q<b1_s0>, [row_base, #16*8]
    ldr Q<b2_s0>, [row_base, #16*16]
    ldr Q<b3_s0>, [row_base, #16*24]
    sqrdmulh V<q45_s4_lo>.8h, V<b1_s0>.8h, V<pre45>.h[0]
    mul      V<p45_s4_lo>.8h, V<b1_s0>.8h, V<tw45>.h[0]
    mls      V<p45_s4_lo>.8h, V<q45_s4_lo>.8h, v0.h[0]
    add      V<b0_s4>.8h, V<b0_s0>.8h, V<p45_s4_lo>.8h
    sub      V<b1_s4>.8h, V<b0_s0>.8h, V<p45_s4_lo>.8h
    sqdmulh  V<sr45_s4_lo>.8h, V<b0_s4>.8h, v0.h[1]
    sqdmulh  V<dr45_s4_lo>.8h, V<b1_s4>.8h, v0.h[1]
    srshr    V<sr45_s4_lo>.8h, V<sr45_s4_lo>.8h, #11
    srshr    V<dr45_s4_lo>.8h, V<dr45_s4_lo>.8h, #11
    mls      V<b0_s4>.8h, V<sr45_s4_lo>.8h, v0.h[0]
    mls      V<b1_s4>.8h, V<dr45_s4_lo>.8h, v0.h[0]
    sqrdmulh V<q45_s4_hi>.8h, V<b3_s0>.8h, V<pre45>.h[0]
    mul      V<p45_s4_hi>.8h, V<b3_s0>.8h, V<tw45>.h[0]
    mls      V<p45_s4_hi>.8h, V<q45_s4_hi>.8h, v0.h[0]
    add      V<b2_s4>.8h, V<b2_s0>.8h, V<p45_s4_hi>.8h
    sub      V<b3_s4>.8h, V<b2_s0>.8h, V<p45_s4_hi>.8h
    sqdmulh  V<sr45_s4_hi>.8h, V<b2_s4>.8h, v0.h[1]
    sqdmulh  V<dr45_s4_hi>.8h, V<b3_s4>.8h, v0.h[1]
    srshr    V<sr45_s4_hi>.8h, V<sr45_s4_hi>.8h, #11
    srshr    V<dr45_s4_hi>.8h, V<dr45_s4_hi>.8h, #11
    mls      V<b2_s4>.8h, V<sr45_s4_hi>.8h, v0.h[0]
    mls      V<b3_s4>.8h, V<dr45_s4_hi>.8h, v0.h[0]
    sqrdmulh V<q45_s5_lo>.8h, V<b2_s4>.8h, V<pre45>.h[1]
    mul      V<p45_s5_lo>.8h, V<b2_s4>.8h, V<tw45>.h[1]
    mls      V<p45_s5_lo>.8h, V<q45_s5_lo>.8h, v0.h[0]
    add      V<b0_s5>.8h, V<b0_s4>.8h, V<p45_s5_lo>.8h
    sub      V<b2_s5>.8h, V<b0_s4>.8h, V<p45_s5_lo>.8h
    sqdmulh  V<sr45_s5_lo>.8h, V<b0_s5>.8h, v0.h[1]
    sqdmulh  V<dr45_s5_lo>.8h, V<b2_s5>.8h, v0.h[1]
    srshr    V<sr45_s5_lo>.8h, V<sr45_s5_lo>.8h, #11
    srshr    V<dr45_s5_lo>.8h, V<dr45_s5_lo>.8h, #11
    mls      V<b0_s5>.8h, V<sr45_s5_lo>.8h, v0.h[0]
    mls      V<b2_s5>.8h, V<dr45_s5_lo>.8h, v0.h[0]
    sqrdmulh V<q45_s5_hi>.8h, V<b3_s4>.8h, V<pre45>.h[2]
    mul      V<p45_s5_hi>.8h, V<b3_s4>.8h, V<tw45>.h[2]
    mls      V<p45_s5_hi>.8h, V<q45_s5_hi>.8h, v0.h[0]
    add      V<b1_s5>.8h, V<b1_s4>.8h, V<p45_s5_hi>.8h
    sub      V<b3_s5>.8h, V<b1_s4>.8h, V<p45_s5_hi>.8h
    sqdmulh  V<sr45_s5_hi>.8h, V<b1_s5>.8h, v0.h[1]
    sqdmulh  V<dr45_s5_hi>.8h, V<b3_s5>.8h, v0.h[1]
    srshr    V<sr45_s5_hi>.8h, V<sr45_s5_hi>.8h, #11
    srshr    V<dr45_s5_hi>.8h, V<dr45_s5_hi>.8h, #11
    mls      V<b1_s5>.8h, V<sr45_s5_hi>.8h, v0.h[0]
    mls      V<b3_s5>.8h, V<dr45_s5_hi>.8h, v0.h[0]
    str Q<b0_s5>, [row_base, #16*0]
    str Q<b1_s5>, [row_base, #16*8]
    str Q<b2_s5>, [row_base, #16*16]
    str Q<b3_s5>, [row_base, #16*24]
slothy_end_invntt32_fixed_stage45:

    ret

.unreq row_base
.unreq const_ptr
