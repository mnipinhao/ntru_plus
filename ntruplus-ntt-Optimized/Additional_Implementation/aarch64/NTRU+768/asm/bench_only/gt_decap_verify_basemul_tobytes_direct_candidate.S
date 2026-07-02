/*
 * Benchmark-only decap verify basemul->tobytes direct-byte candidate.
 *
 * Contract:
 *   gt_decap_verify_basemul_tobytes_direct_candidate(out, c_minus_m2, hinv)
 *     == poly_tobytes(poly_basemul(c_minus_m2, hinv))
 *
 * This is not a generic poly_basemul replacement.  It compiles the current
 * GT plain basemul arithmetic with a default-off final-store hook:
 * two consecutive 32-coefficient basemul output halves are combined and packed
 * directly into one 96-byte poly_tobytes chunk.
 */

#define GT_BASEMUL_EMIT_BASEMUL 1
#define GT_BASEMUL_SYMBOL gt_decap_verify_basemul_tobytes_direct_candidate
#define GT_BASEMUL_DARWIN_SYMBOL _gt_decap_verify_basemul_tobytes_direct_candidate
#define GT_BASEMUL_DIRECT_TOBYTES 1

#include "../gt/base_gt_opt_body.inc"
