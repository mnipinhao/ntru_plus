/*
 * Production GT inverse NTT.
 *
 * This promotes the Pi 5 validated path:
 *   direct physical loads routed through the stage123 stripe-scratch layout
 *   + Slothy-scheduled stage45 row-end reduction fusion
 *   + post-row inverse DFT3 with post-DFT3 reductions removed
 *   + branch-constant folded untwist/final merge with final output reductions.
 *     Exact representative checks pass for forward-produced GT inputs, and
 *     the current Pi 5 median is about 4039 cycles in the base-N1 combined
 *     matrix, with the best observed pipeline/KEM medians.
 */
.equ INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY, 1
.equ INVNTT_POST_DFT3_NO_REDUCE, 1
.equ INVNTT_USE_POST_BRANCHFOLD, 1
.equ INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS, 1
.equ INVNTT_PRESERVE_CALLEE_SAVED_SIMD, 1
#ifdef __APPLE__
.equ INVNTT_DARWIN_NO_WEAK, 1
#endif
.include "asm/gt/invntt/poly_invntt.n1.opt.inc"
