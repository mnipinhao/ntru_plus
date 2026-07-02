/*
 * GT production keypair basemul for one input scaled by R.
 *
 * Contract:
 *   b_scaled_r = b * R mod q
 *   output     = a * b mod q
 *
 * The included GT basemul body normally computes raw = a*b*R^-1 before its
 * final correction.  With b_scaled_r, that raw value is already the normal
 * product, so this wrapper deliberately omits the final correction block.
 */
#define GT_BASEMUL_EMIT_BASEMUL 1
#define GT_BASEMUL_SYMBOL poly_basemul_scaled_r_input
#define GT_BASEMUL_DARWIN_SYMBOL _poly_basemul_scaled_r_input
#define GT_BASEMUL_STORE_RMINUS1 1

#include "base_gt_opt_body.inc"
