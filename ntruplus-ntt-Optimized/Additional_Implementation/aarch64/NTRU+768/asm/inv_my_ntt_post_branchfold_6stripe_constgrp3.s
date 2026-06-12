/*
 * Post-row branchfold 6-stripe + constants candidate.
 *
 * Combines the 6-stripe loop pressure test with q-pair branchfold constant
 * loads.  This is intentionally separate from the pure 6-stripe wrapper so
 * the Pi 5 matrix can attribute any gain/loss to loop scope vs load shape.
 */

.equ INVNTT_USE_DIRECT_STAGE123, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY, 1
.equ INVNTT_POST_DFT3_NO_REDUCE, 1
.equ INVNTT_USE_POST_BRANCHFOLD, 1
.equ INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS, 1
.equ INVNTT_USE_POST_BRANCHFOLD_LDP_CONSTS, 1
.equ INVNTT_USE_POST_6STRIPE_LOOP, 1
.include "asm/slothy/invntt_opt.s"
