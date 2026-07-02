/*
 * Benchmark-only raw Montgomery-factor GT basemul with the old final-store
 * register contract.
 *
 * This keeps the Slothy-scheduled base_gt.opt.s body but restores the former
 *   mov v8,v5; mov v9,v6; mov v10,v18; st4 {v8,v9,v10,v11}
 * final store shape under GT_BASEMUL_STORE_RMINUS1.  It is not a production
 * symbol; use it only to measure the current final-st4 contract patch.
 */
#define poly_basemul poly_basemul_rminus1_oldstore
#define _poly_basemul _poly_basemul_rminus1_oldstore
#define poly_basemul_add poly_basemul_add_rminus1_oldstore_unused
#define _poly_basemul_add _poly_basemul_add_rminus1_oldstore_unused
#define GT_BASEMUL_STORE_RMINUS1 1
#define GT_BASEMUL_STORE_RMINUS1_OLD_MOV_CONTRACT 1

#include "../gt/base_gt.opt.s"
