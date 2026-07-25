/*
 * Production GT poly_basemul wrapper.
 *
 * This exports only the generic poly_basemul ABI from the shared
 * Slothy-scheduled GT basemul body.  Production links poly_basemul_add from
 * poly_basemul_add.s.
 */
#define GT_BASEMUL_EMIT_BASEMUL 1
#ifdef GT_PRODUCTION_RMINUS1_IS_POLY_API
#define GT_BASEMUL_SYMBOL poly_basemul_normal
#define GT_BASEMUL_DARWIN_SYMBOL _poly_basemul_normal
#else
#define GT_BASEMUL_SYMBOL poly_basemul
#define GT_BASEMUL_DARWIN_SYMBOL _poly_basemul
#endif

#include "poly_basemul_body.inc"
