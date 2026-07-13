/* Pre-lazy production rminus1 InvNTT under benchmark-only symbols. */
#define poly_invntt poly_invntt_from_rminus1_baseline
#define _poly_invntt _poly_invntt_from_rminus1_baseline
#define gt_block_major_poly_invntt gt_baseline_block_major_invntt_rminus1
#define _gt_block_major_poly_invntt _gt_baseline_block_major_invntt_rminus1
#define gt_tuple_poly_invntt gt_baseline_tuple_invntt_rminus1
#define _gt_tuple_poly_invntt _gt_baseline_tuple_invntt_rminus1
#define gt_bpq_poly_invntt gt_baseline_bpq_invntt_rminus1
#define _gt_bpq_poly_invntt _gt_baseline_bpq_invntt_rminus1
.equ INVNTT_INPUT_RMINUS1, 1
.equ INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY, 1
.equ INVNTT_POST_DFT3_NO_REDUCE, 1
.equ INVNTT_USE_POST_BRANCHFOLD, 1
.equ INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS, 1
.equ INVNTT_DARWIN_NO_WEAK, 1

#include "../../invntt/poly_invntt.n1.opt.inc"
