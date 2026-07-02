/*
 * GT production raw Montgomery-factor basemul.
 *
 * This compiles the Slothy-scheduled GT basemul body with the public symbols
 * remapped and the final multiply-by-R correction omitted.  The output is the
 * quartic product in GT block-major layout with one extra R^-1 factor.  It is
 * only valid when the caller immediately feeds the result to an inverse NTT
 * entrypoint whose final branchfold constants compensate that factor.
 */
#define GT_BASEMUL_EMIT_BASEMUL 1
#define GT_BASEMUL_SYMBOL poly_basemul_rminus1
#define GT_BASEMUL_DARWIN_SYMBOL _poly_basemul_rminus1
#define GT_BASEMUL_STORE_RMINUS1 1

#include "base_gt_opt_body.inc"
