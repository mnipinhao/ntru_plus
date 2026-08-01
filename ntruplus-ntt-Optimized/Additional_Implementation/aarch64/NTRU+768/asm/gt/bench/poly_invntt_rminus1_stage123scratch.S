/*
 * Benchmark-only split ABI for the rminus1 InvNTT stage123-scratch experiment.
 *
 * This keeps the production rminus1 wrapper narrow while still allowing the
 * component profiler and aarch64-bench to measure the historical split:
 *
 *   block-major rminus1 product -> stage123 stripe scratch -> stage45/post
 */

#define gt_block_major_to_stage123_stripe_scratch gt_rminus1_block_major_to_stage123_stripe_scratch
#define _gt_block_major_to_stage123_stripe_scratch _gt_rminus1_block_major_to_stage123_stripe_scratch
#define gt_tuple_to_stage123_stripe_scratch gt_rminus1_tuple_to_stage123_stripe_scratch
#define _gt_tuple_to_stage123_stripe_scratch _gt_rminus1_tuple_to_stage123_stripe_scratch
#define poly_invntt_stage45scratch poly_invntt_from_rminus1_stage45scratch
#define _poly_invntt_stage45scratch _poly_invntt_from_rminus1_stage45scratch

.equ INVNTT_INPUT_RMINUS1, 1
.equ INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY, 1
.equ INVNTT_POST_DFT3_NO_REDUCE, 1
.equ INVNTT_USE_POST_BRANCHFOLD, 1
.equ INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS, 1
.equ INVNTT_USE_LAZY_TWIDDLE1_STAGE123, 1
.equ INVNTT_STAGE123_SCRATCH_ONLY, 1
.equ INVNTT_EXPOSE_STAGE123_SCRATCH_ABI, 1
.equ INVNTT_PRESERVE_CALLEE_SAVED_SIMD, 1
.equ INVNTT_STAGE123_SCRATCH_SECURE_CLEAR, 1
#ifdef __APPLE__
.equ INVNTT_DARWIN_NO_WEAK, 1
#endif

#include "../invntt/poly_invntt.n1.opt.inc"
