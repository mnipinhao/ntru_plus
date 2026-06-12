/*
 * Benchmark-only GT inverse NTT wrapper.
 *
 * This selects the production stage123 stripe-scratch inverse path and
 * additionally exports stage timing entry points:
 *   poly_invntt_bench_rows
 *   poly_invntt_bench_row0
 *   poly_invntt_bench_row1
 *   poly_invntt_bench_row2
 *   poly_invntt_bench_post
 *   poly_invntt_bench_post_dft3_raw
 *   poly_invntt_bench_post_dft3_reduce
 *   poly_invntt_bench_post_untwist
 *   poly_invntt_bench_post_finalmerge
 *
 * Do not use this as the production KEM source; it is for aarch64-bench stage
 * ablation only.
 */
.equ INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY, 1
.equ INVNTT_POST_DFT3_NO_REDUCE, 1
.equ INVNTT_USE_POST_BRANCHFOLD, 1
.equ INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS, 1
.equ INVNTT_BENCH_STAGES, 1
.include "asm/slothy/invntt_opt.s"
