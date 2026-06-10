/*
 * Production-equivalent GT inverse NTT wrapper.
 *
 * Branch-constant folded final merge with final output Barrett reductions.
 * This matches the promoted production gates and is kept as an explicit
 * benchmark/regression source.
 */
.equ INVNTT_USE_DIRECT_STAGE123, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY, 1
.equ INVNTT_POST_DFT3_NO_REDUCE, 1
.equ INVNTT_USE_POST_BRANCHFOLD, 1
.equ INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS, 1
.include "asm/slothy/invntt_opt.s"
