/*
 * Benchmark-only raw Montgomery-factor GT basemul with the old final-store
 * register contract.
 *
 * This keeps the Slothy-scheduled GT basemul body but restores the former
 *   mov v8,v5; mov v9,v6; mov v10,v18; st4 {v8,v9,v10,v11}
 * final store shape under GT_BASEMUL_STORE_RMINUS1.  It is not a production
 * symbol; use it only to measure the current final-st4 contract patch.
 */
#define GT_BASEMUL_EMIT_BASEMUL 1
#define GT_BASEMUL_SYMBOL poly_basemul_rminus1_oldstore
#define GT_BASEMUL_DARWIN_SYMBOL _poly_basemul_rminus1_oldstore
#define GT_BASEMUL_STORE_RMINUS1 1
#define GT_BASEMUL_STORE_RMINUS1_OLD_MOV_CONTRACT 1

#include "../gt/base_gt_opt_body.inc"
