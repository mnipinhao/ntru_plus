/*
 * Experiment-only drop-in wrapper for isolated full-KEM measurement.
 * Production remains unchanged unless this source is selected explicitly.
 */
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
