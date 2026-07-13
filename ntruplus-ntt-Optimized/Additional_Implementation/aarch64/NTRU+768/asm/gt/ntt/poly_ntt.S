/*
 * Public production entry for the GT forward NTT.
 *
 * Keep the public symbol contract here. The baseline implementation body is
 * included from poly_ntt_body.inc and does not decide weak/global alias policy.
 */

.global poly_ntt
.global _poly_ntt
.global gt_block_major_poly_ntt
.global _gt_block_major_poly_ntt
poly_ntt:
_poly_ntt:
gt_block_major_poly_ntt:
_gt_block_major_poly_ntt:
    .include "asm/gt/ntt/poly_ntt_body.inc"
