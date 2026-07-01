/*
 * Benchmark-only decap verify basemul->tobytes direct-byte candidate.
 *
 * Contract:
 *   gt_decap_verify_basemul_tobytes_direct_candidate(out, c_minus_m2, hinv)
 *     == poly_tobytes(poly_basemul(c_minus_m2, hinv))
 *
 * This is not a generic poly_basemul replacement.  It compiles the current
 * base_gt.opt.s plain basemul arithmetic with a default-off final-store hook:
 * two consecutive 32-coefficient basemul output halves are combined and packed
 * directly into one 96-byte poly_tobytes chunk.
 */

#define poly_basemul gt_decap_verify_basemul_tobytes_direct_candidate
#define _poly_basemul _gt_decap_verify_basemul_tobytes_direct_candidate
#define poly_basemul_add gt_decap_verify_basemul_tobytes_direct_add_unused
#define _poly_basemul_add _gt_decap_verify_basemul_tobytes_direct_add_unused
#define GT_BASEMUL_DIRECT_TOBYTES 1

#include "base_gt.opt.s"
