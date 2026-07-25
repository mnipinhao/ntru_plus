/*
 * Experiment-only rminus1 InvNTT with one shared Stage45 row helper.
 *
 * Stage123, row-buffer layout, Stage45 arithmetic, branchfold post-processing,
 * constants, and the public ABI match production. Only the three identical
 * Stage45 macro expansions are replaced with internal bl/ret calls.
 */
#define poly_invntt poly_invntt_rminus1_stage45_row_helper
#define _poly_invntt _poly_invntt_rminus1_stage45_row_helper
#define gt_block_major_poly_invntt \
    gt_block_major_poly_invntt_rminus1_stage45_row_helper
#define _gt_block_major_poly_invntt \
    _gt_block_major_poly_invntt_rminus1_stage45_row_helper

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
.equ INVNTT_BLOCK_MAJOR_ONLY, 1
.equ INVNTT_USE_STAGE45_ROW_HELPER, 1
#ifdef __APPLE__
.equ INVNTT_DARWIN_NO_WEAK, 1
#endif

#include "../../invntt/poly_invntt.n1.opt.inc"
