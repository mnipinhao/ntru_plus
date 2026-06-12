/*
 * Legacy GT inverse NTT wrapper.
 *
 * This preserves the pre-stripe-scratch production path for benchmark
 * comparisons and PMU attribution:
 *   direct physical stage123 loads
 *   + Slothy-scheduled stage45 row-end reduction fusion
 *   + post-row inverse DFT3 with post-DFT3 reductions removed
 *   + branch-constant folded untwist/final merge with final output reductions.
 */
.equ INVNTT_USE_DIRECT_STAGE123, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY, 1
.equ INVNTT_POST_DFT3_NO_REDUCE, 1
.equ INVNTT_USE_POST_BRANCHFOLD, 1
.equ INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS, 1
.include "asm/slothy/invntt_opt.s"
