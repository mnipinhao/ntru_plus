/*
 * Post-row branchfold d-half constants candidate.
 *
 * C1 compression probe: consume the existing [C0 x4, C1 x4] vectors as two
 * d-half loads and rebuild the q vector with one ins.  This isolates whether
 * reducing q-load pressure can pay for the extra instructions before changing
 * the table generator.
 */

.equ INVNTT_USE_DIRECT_STAGE123, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION, 1
.equ INVNTT_USE_STAGE45_REDUCE_FUSION_SLOTHY, 1
.equ INVNTT_POST_DFT3_NO_REDUCE, 1
.equ INVNTT_USE_POST_BRANCHFOLD, 1
.equ INVNTT_POST_BRANCHFOLD_REDUCE_OUTPUTS, 1
.equ INVNTT_USE_POST_BRANCHFOLD_DHALF_CONSTS, 1
.include "asm/slothy/invntt_opt.s"
