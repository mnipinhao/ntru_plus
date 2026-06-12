/*
 * Post-row branchfold 3-stripe constants candidate.
 *
 * The branchfold table is already emitted in post consumption order.  This
 * variant keeps that 3-stripe grouping and changes each normal/precompute
 * pair load from two q loads to one q-pair load.
 */

.equ INVNTT_USE_DIRECT_STAGE123, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY, 1
.equ INVNTT_POST_DFT3_NO_REDUCE, 1
.equ INVNTT_USE_POST_BRANCHFOLD, 1
.equ INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS, 1
.equ INVNTT_USE_POST_BRANCHFOLD_LDP_CONSTS, 1
.include "asm/slothy/invntt_opt.s"
