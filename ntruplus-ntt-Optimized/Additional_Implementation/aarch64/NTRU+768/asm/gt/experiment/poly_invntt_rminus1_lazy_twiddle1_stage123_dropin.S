/* Default-off KEM drop-in for the proof-gated Stage123 twiddle=1 candidate. */
#define poly_invntt poly_invntt_rminus1_lazy_twiddle1_stage123_dropin_core
#define _poly_invntt _poly_invntt_rminus1_lazy_twiddle1_stage123_dropin_core
#define gt_block_major_poly_invntt gt_lazy_twiddle1_dropin_block_major_core
#define _gt_block_major_poly_invntt _gt_lazy_twiddle1_dropin_block_major_core
#define gt_tuple_poly_invntt gt_lazy_twiddle1_dropin_tuple_core
#define _gt_tuple_poly_invntt _gt_lazy_twiddle1_dropin_tuple_core
#define gt_bpq_poly_invntt gt_lazy_twiddle1_dropin_bpq_core
#define _gt_bpq_poly_invntt _gt_lazy_twiddle1_dropin_bpq_core

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
.global poly_invntt_from_rminus1
.global _poly_invntt_from_rminus1
.type poly_invntt_from_rminus1, %function
poly_invntt_from_rminus1:
_poly_invntt_from_rminus1:
    stp x29, x30, [sp, #-80]!
    stp d8, d9, [sp, #16]
    stp d10, d11, [sp, #32]
    stp d12, d13, [sp, #48]
    stp d14, d15, [sp, #64]
    bl poly_invntt_rminus1_lazy_twiddle1_stage123_dropin_core
    ldp d8, d9, [sp, #16]
    ldp d10, d11, [sp, #32]
    ldp d12, d13, [sp, #48]
    ldp d14, d15, [sp, #64]
    ldp x29, x30, [sp], #80
    ret
.size poly_invntt_from_rminus1, .-poly_invntt_from_rminus1
