/* Experiment-only rminus1 InvNTT with Stage123 twiddle=1 reductions deferred. */
#define poly_invntt poly_invntt_rminus1_lazy_twiddle1_stage123_core
#define _poly_invntt _poly_invntt_rminus1_lazy_twiddle1_stage123_core
#define gt_block_major_poly_invntt gt_block_major_poly_invntt_rminus1_lazy_twiddle1_stage123
#define _gt_block_major_poly_invntt _gt_block_major_poly_invntt_rminus1_lazy_twiddle1_stage123
#define gt_tuple_poly_invntt gt_tuple_poly_invntt_rminus1_lazy_twiddle1_stage123
#define _gt_tuple_poly_invntt _gt_tuple_poly_invntt_rminus1_lazy_twiddle1_stage123
#define gt_bpq_poly_invntt gt_bpq_poly_invntt_rminus1_lazy_twiddle1_stage123
#define _gt_bpq_poly_invntt _gt_bpq_poly_invntt_rminus1_lazy_twiddle1_stage123
#define gt_block_major_to_stage123_stripe_scratch gt_lazy_twiddle1_block_major_to_stage123_stripe_scratch
#define _gt_block_major_to_stage123_stripe_scratch _gt_lazy_twiddle1_block_major_to_stage123_stripe_scratch
#define gt_tuple_to_stage123_stripe_scratch gt_lazy_twiddle1_tuple_to_stage123_stripe_scratch
#define _gt_tuple_to_stage123_stripe_scratch _gt_lazy_twiddle1_tuple_to_stage123_stripe_scratch
#define poly_invntt_stage45scratch poly_invntt_lazy_twiddle1_stage45scratch
#define _poly_invntt_stage45scratch _poly_invntt_lazy_twiddle1_stage45scratch

.equ INVNTT_INPUT_RMINUS1, 1
.equ INVNTT_USE_DIRECT_STAGE123_STRIPE_SCRATCH, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY, 1
.equ INVNTT_POST_DFT3_NO_REDUCE, 1
.equ INVNTT_USE_POST_BRANCHFOLD, 1
.equ INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS, 1
.equ INVNTT_EXPERIMENT_LAZY_TWIDDLE1_STAGE123, 1
.equ INVNTT_DARWIN_NO_WEAK, 1

#include "../../slothy/production/invntt_opt.production.s"

.text
.align 2
.global poly_invntt_rminus1_lazy_twiddle1_stage123
.global _poly_invntt_rminus1_lazy_twiddle1_stage123
.type poly_invntt_rminus1_lazy_twiddle1_stage123, %function
poly_invntt_rminus1_lazy_twiddle1_stage123:
_poly_invntt_rminus1_lazy_twiddle1_stage123:
    stp x29, x30, [sp, #-80]!
    stp d8, d9, [sp, #16]
    stp d10, d11, [sp, #32]
    stp d12, d13, [sp, #48]
    stp d14, d15, [sp, #64]
    bl poly_invntt_rminus1_lazy_twiddle1_stage123_core
    ldp d8, d9, [sp, #16]
    ldp d10, d11, [sp, #32]
    ldp d12, d13, [sp, #48]
    ldp d14, d15, [sp, #64]
    ldp x29, x30, [sp], #80
    ret
.size poly_invntt_rminus1_lazy_twiddle1_stage123, .-poly_invntt_rminus1_lazy_twiddle1_stage123
