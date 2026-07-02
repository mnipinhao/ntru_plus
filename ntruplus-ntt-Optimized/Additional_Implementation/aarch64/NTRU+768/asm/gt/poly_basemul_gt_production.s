/*
 * Production GT poly_basemul wrapper.
 *
 * This exports only the generic poly_basemul ABI from the shared
 * Slothy-scheduled GT basemul body.  Production links poly_basemul_add from
 * poly_basemul_add_gt_production.s.
 */
#define GT_BASEMUL_EMIT_BASEMUL 1
#define GT_BASEMUL_SYMBOL poly_basemul
#define GT_BASEMUL_DARWIN_SYMBOL _poly_basemul

#include "base_gt_opt_body.inc"
