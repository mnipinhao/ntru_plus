/*
 * Promoted-equivalent GT inverse NTT wrapper.
 *
 * Same output layout and representative contract as production, but uses a
 * Neoverse-N1 Slothy schedule for the fused post-row stripe with the three
 * post-DFT3 Barrett reductions omitted.  This is the same gate set now used
 * by production asm/inv_my_ntt.s and remains as an explicit benchmark source.
 */
.equ INVNTT_USE_DIRECT_STAGE123, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY, 1
.equ INVNTT_USE_POST_FUSED_N1_NODFTREDUCE_SLOTHY, 1
.include "asm/slothy/invntt_opt.s"
