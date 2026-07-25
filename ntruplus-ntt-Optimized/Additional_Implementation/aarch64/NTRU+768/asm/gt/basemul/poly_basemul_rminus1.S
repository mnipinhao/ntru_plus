/*
 * GT production raw Montgomery-factor basemul.
 *
 * This compiles the Slothy-scheduled GT basemul body with the final
 * multiply-by-R correction omitted.  The output is the quartic product in GT
 * block-major layout with one extra R^-1 factor.  Production exports this as
 * poly_basemul and pairs it with poly_invntt; experiment-only builds retain
 * the explicit poly_basemul_rminus1 name.
 */
#define GT_BASEMUL_EMIT_BASEMUL 1
#ifdef GT_PRODUCTION_RMINUS1_IS_POLY_API
#define GT_BASEMUL_SYMBOL poly_basemul
#define GT_BASEMUL_DARWIN_SYMBOL _poly_basemul
#else
#define GT_BASEMUL_SYMBOL poly_basemul_rminus1
#define GT_BASEMUL_DARWIN_SYMBOL _poly_basemul_rminus1
#endif
#define GT_BASEMUL_STORE_RMINUS1 1

#include "poly_basemul_body.inc"
