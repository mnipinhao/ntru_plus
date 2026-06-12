/*
 * Post-row branchfold 6-stripe harness.
 *
 * This doubles the runtime post-loop window from one natural 3-stripe mapping
 * cycle to two cycles before the loop branch and pointer update.  It is an
 * opt-in pressure test for whether a larger post-row scope helps or starts
 * losing to front-end/register pressure.
 */

.equ INVNTT_USE_DIRECT_STAGE123, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY, 1
.equ INVNTT_POST_DFT3_NO_REDUCE, 1
.equ INVNTT_USE_POST_BRANCHFOLD, 1
.equ INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS, 1
.equ INVNTT_USE_POST_6STRIPE_LOOP, 1
.include "asm/slothy/invntt_opt.s"
