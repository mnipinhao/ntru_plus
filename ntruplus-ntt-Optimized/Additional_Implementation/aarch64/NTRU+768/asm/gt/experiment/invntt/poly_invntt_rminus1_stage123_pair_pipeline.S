/* Default-off rminus1 InvNTT Stage123 two-group scheduling candidate. */
#define poly_invntt poly_invntt_rminus1_stage123_pair_pipeline
#define _poly_invntt _poly_invntt_rminus1_stage123_pair_pipeline
#define gt_block_major_poly_invntt gt_stage123_pair_block_major_core
#define _gt_block_major_poly_invntt _gt_stage123_pair_block_major_core
#define gt_tuple_poly_invntt gt_stage123_pair_tuple_core
#define _gt_tuple_poly_invntt _gt_stage123_pair_tuple_core
#define gt_bpq_poly_invntt gt_stage123_pair_bpq_core
#define _gt_bpq_poly_invntt _gt_stage123_pair_bpq_core

.equ INVNTT_INPUT_RMINUS1, 1
.equ INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY, 1
.equ INVNTT_POST_DFT3_NO_REDUCE, 1
.equ INVNTT_USE_POST_BRANCHFOLD, 1
.equ INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS, 1
.equ INVNTT_USE_LAZY_TWIDDLE1_STAGE123, 1
.equ INVNTT_USE_LAZY_TWIDDLE1_LEN16, 1
.equ INVNTT_USE_STAGE123_PAIR_PIPELINE, 1
.equ INVNTT_PRESERVE_CALLEE_SAVED_SIMD, 1
.equ INVNTT_DARWIN_NO_WEAK, 1

#include "../../../../experiments/invntt_stage123_pair_pipeline/stage123_pair_pipeline.opt.inc"
#include "../../invntt/poly_invntt.n1.opt.inc"
