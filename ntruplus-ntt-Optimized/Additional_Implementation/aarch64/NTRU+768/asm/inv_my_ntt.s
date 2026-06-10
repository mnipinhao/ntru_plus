/*
 * Production GT inverse NTT.
 *
 * This promotes the Pi 5 validated path:
 *   direct physical loads fused with row stage123
 *   + Slothy-scheduled stage45 row-end reduction fusion
 *   + post-row inverse DFT3 with post-DFT3 reductions removed
 *   + branch-constant folded untwist/final merge with final output reductions.
 *     Exact representative checks pass for forward-produced GT inputs, and
 *     Pi 5 BENCH_MODE=invntt improves from about 5002 to 4044 cycles.
 *
 * The previous no-DFT3-reduce production path remains available as
 * asm/inv_my_ntt_post_n1_nodftreduce.s.  The older post-DFT3-reducing path
 * remains available as asm/inv_my_ntt_post_dft3reduce_fallback.s.
 */
.equ INVNTT_USE_DIRECT_STAGE123, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY, 1
.equ INVNTT_POST_DFT3_NO_REDUCE, 1
.equ INVNTT_USE_POST_BRANCHFOLD, 1
.equ INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS, 1
.include "asm/slothy/invntt_opt.s"
