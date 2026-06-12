/*
 * Post-row branchfold 3-stripe harness.
 *
 * This keeps the production arithmetic and constants, but routes the post
 * phase through the explicit 3-stripe loop macro so it can be compared against
 * the 1-stripe A72 Slothy wrapper and the 6-stripe loop candidate.
 */

.equ INVNTT_USE_DIRECT_STAGE123, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY, 1
.equ INVNTT_POST_DFT3_NO_REDUCE, 1
.equ INVNTT_USE_POST_BRANCHFOLD, 1
.equ INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS, 1
.include "asm/slothy/invntt_opt.s"
