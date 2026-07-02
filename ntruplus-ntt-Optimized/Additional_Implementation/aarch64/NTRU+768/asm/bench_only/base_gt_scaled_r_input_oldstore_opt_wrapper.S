/*
 * Benchmark-only scaled-r-input GT basemul with the old final-store register
 * contract.
 *
 * Production uses asm/gt/poly_basemul_scaled_r_input_gt_production.s.  This wrapper only
 * exists so the PMU harness can compare the final st4 register-contract patch
 * before and after, without changing the live KEM path.
 */
#define GT_BASEMUL_EMIT_BASEMUL 1
#define GT_BASEMUL_SYMBOL poly_basemul_scaled_r_input_oldstore
#define GT_BASEMUL_DARWIN_SYMBOL _poly_basemul_scaled_r_input_oldstore
#define GT_BASEMUL_STORE_RMINUS1 1
#define GT_BASEMUL_STORE_RMINUS1_OLD_MOV_CONTRACT 1

#include "../gt/base_gt_opt_body.inc"
