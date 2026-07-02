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
#define poly_basemul poly_basemul_scaled_r_input
#define _poly_basemul _poly_basemul_scaled_r_input
#define poly_basemul_add poly_basemul_add_scaled_r_input_unused
#define _poly_basemul_add _poly_basemul_add_scaled_r_input_unused
#define GT_BASEMUL_STORE_RMINUS1 1

#include "base_gt.opt.s"
