/*
 * Benchmark-only scaled-r-input GT basemul with the old final-store register
 * contract.
 *
 * Production uses asm/gt/base_gt_scaled_r_input_opt_wrapper.S.  This wrapper only
 * exists so the PMU harness can compare the final st4 register-contract patch
 * before and after, without changing the live KEM path.
 */
#define poly_basemul poly_basemul_scaled_r_input_oldstore
#define _poly_basemul _poly_basemul_scaled_r_input_oldstore
#define poly_basemul_add poly_basemul_add_scaled_r_input_oldstore_unused
#define _poly_basemul_add _poly_basemul_add_scaled_r_input_oldstore_unused
#define GT_BASEMUL_STORE_RMINUS1 1
#define GT_BASEMUL_STORE_RMINUS1_OLD_MOV_CONTRACT 1

#include "../gt/base_gt.opt.s"
