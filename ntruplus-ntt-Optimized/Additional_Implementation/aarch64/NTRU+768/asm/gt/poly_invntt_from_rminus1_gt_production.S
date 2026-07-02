/*
 * Production GT inverse NTT for inputs carrying one extra R^-1 factor.
 *
 * The row kernels and post pipeline are identical to
 * asm/gt/poly_invntt_gt_production.s.  Only the public symbols and branchfold
 * constant table are changed.  This entry is paired with poly_basemul_rminus1()
 * and returns normal R^0 coefficients.
 */
#define poly_invntt poly_invntt_from_rminus1
#define _poly_invntt _poly_invntt_from_rminus1
#define gt_block_major_poly_invntt gt_block_major_poly_invntt_from_rminus1
#define _gt_block_major_poly_invntt _gt_block_major_poly_invntt_from_rminus1
#define gt_tuple_poly_invntt gt_tuple_poly_invntt_from_rminus1
#define _gt_tuple_poly_invntt _gt_tuple_poly_invntt_from_rminus1
#define gt_bpq_poly_invntt gt_bpq_poly_invntt_from_rminus1
#define _gt_bpq_poly_invntt _gt_bpq_poly_invntt_from_rminus1
#define poly_invntt_stage45scratch poly_invntt_from_rminus1_stage45scratch
#define _poly_invntt_stage45scratch _poly_invntt_from_rminus1_stage45scratch
#define gt_block_major_to_stage123_stripe_scratch gt_rminus1_block_major_to_stage123_stripe_scratch
#define _gt_block_major_to_stage123_stripe_scratch _gt_rminus1_block_major_to_stage123_stripe_scratch
#define gt_tuple_to_stage123_stripe_scratch gt_rminus1_tuple_to_stage123_stripe_scratch
#define _gt_tuple_to_stage123_stripe_scratch _gt_rminus1_tuple_to_stage123_stripe_scratch

.equ INVNTT_INPUT_RMINUS1, 1
.equ INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY, 1
.equ INVNTT_POST_DFT3_NO_REDUCE, 1
.equ INVNTT_USE_POST_BRANCHFOLD, 1
.equ INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS, 1
.equ INVNTT_EXPOSE_STAGE123_SCRATCH_ABI, 1
#ifdef __APPLE__
.equ INVNTT_DARWIN_NO_WEAK, 1
#endif

#include "../slothy/production/invntt_opt.production.s"
