/*
 * Fallback GT inverse NTT.
 *
 * This is the previous production path before promoting
 * INVNTT_USE_POST_FUSED_N1_NODFTREDUCE_SLOTHY.  It keeps the three post-DFT3
 * Barrett reductions inside the fused post stripe.
 */
.equ INVNTT_USE_DIRECT_STAGE123, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY, 1
.equ INVNTT_USE_POST_FUSED_SLOTHY, 1
.include "asm/slothy/invntt_opt.s"
