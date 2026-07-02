/*
 * Opt-in GT inverse NTT wrapper.
 *
 * Same mathematical contract as production branchfold-reduce, but selects an
 * A72 Slothy schedule for the fused post-row branchfold stripe.  Default
 * production remains asm/gt/inv_my_ntt.s until Pi 5 measurements prove this path
 * is faster.
 */
.equ INVNTT_USE_DIRECT_STAGE123, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY, 1
.equ INVNTT_POST_DFT3_NO_REDUCE, 1
.equ INVNTT_USE_POST_BRANCHFOLD, 1
.equ INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS, 1
.equ INVNTT_USE_POST_BRANCHFOLD_A72_SLOTHY, 1
.include "asm/slothy/legacy/invntt_opt.s"
