/*
 * Decap-only GT inverse NTT for inputs carrying one extra R^-1 factor.
 *
 * This entry returns the same output convention as:
 *   poly_invntt_from_rminus1(tmp, a);
 *   poly_crepmod3(r, tmp);
 *
 * It reuses the final q-Barrett quotient in the branchfold post stage and
 * stores the centered mod-3 representative directly.
 */
#define poly_invntt poly_invntt_from_rminus1_crepmod3
#define _poly_invntt _poly_invntt_from_rminus1_crepmod3
#define gt_block_major_poly_invntt gt_block_major_poly_invntt_from_rminus1_crepmod3
#define _gt_block_major_poly_invntt _gt_block_major_poly_invntt_from_rminus1_crepmod3
#define gt_tuple_poly_invntt gt_tuple_poly_invntt_from_rminus1_crepmod3
#define _gt_tuple_poly_invntt _gt_tuple_poly_invntt_from_rminus1_crepmod3
#define gt_bpq_poly_invntt gt_bpq_poly_invntt_from_rminus1_crepmod3
#define _gt_bpq_poly_invntt _gt_bpq_poly_invntt_from_rminus1_crepmod3
#define poly_invntt_stage45scratch poly_invntt_from_rminus1_crepmod3_stage45scratch
#define _poly_invntt_stage45scratch _poly_invntt_from_rminus1_crepmod3_stage45scratch
#define gt_block_major_to_stage123_stripe_scratch gt_rminus1_crepmod3_block_major_to_stage123_stripe_scratch
#define _gt_block_major_to_stage123_stripe_scratch _gt_rminus1_crepmod3_block_major_to_stage123_stripe_scratch
#define gt_tuple_to_stage123_stripe_scratch gt_rminus1_crepmod3_tuple_to_stage123_stripe_scratch
#define _gt_tuple_to_stage123_stripe_scratch _gt_rminus1_crepmod3_tuple_to_stage123_stripe_scratch

.equ INVNTT_INPUT_RMINUS1, 1
.equ INVNTT_FUSED_CREP3_OUTPUT, 1
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

#include "slothy/invntt_opt.production.s"
