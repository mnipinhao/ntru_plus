/*
 * Production GT inverse NTT for inputs carrying one extra R^-1 factor.
 *
 * This production entry is paired with poly_basemul_rminus1() and returns
 * normal R^0 coefficients.  Proof-gated multiplier-1 reductions are deferred
 * through inverse NTT32 transform size 16; size 32 remains reduced.
 */
#define poly_invntt poly_invntt_from_rminus1
#define _poly_invntt _poly_invntt_from_rminus1
#define gt_block_major_poly_invntt gt_block_major_poly_invntt_from_rminus1
#define _gt_block_major_poly_invntt _gt_block_major_poly_invntt_from_rminus1
#define gt_tuple_poly_invntt gt_tuple_poly_invntt_from_rminus1
#define _gt_tuple_poly_invntt _gt_tuple_poly_invntt_from_rminus1
#define gt_bpq_poly_invntt gt_bpq_poly_invntt_from_rminus1
#define _gt_bpq_poly_invntt _gt_bpq_poly_invntt_from_rminus1
.equ INVNTT_INPUT_RMINUS1, 1
.equ INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY, 1
.equ INVNTT_POST_DFT3_NO_REDUCE, 1
.equ INVNTT_USE_POST_BRANCHFOLD, 1
.equ INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS, 1
.equ INVNTT_USE_LAZY_TWIDDLE1_STAGE123, 1
.equ INVNTT_USE_LAZY_TWIDDLE1_LEN16, 1
.equ INVNTT_PRESERVE_CALLEE_SAVED_SIMD, 1
#ifdef __APPLE__
.equ INVNTT_DARWIN_NO_WEAK, 1
#endif

#include "../slothy/production/invntt_opt.production.s"
