/*
 * Benchmark-only renamed ldp+uzp input-load experiment for base_gt.opt.s.
 *
 * Existing asm/base_gt_opt_ldrtrn_noadd_wrapper.S preserves the public
 * poly_basemul ABI, so it cannot be linked into the same PMU binary as the
 * production poly_basemul symbol.  This wrapper keeps the same body but exports
 * a distinct symbol for current-vs-ldrtrn_noadd benchmarking.
 */
#define GT_BASEMUL_USE_LDPTRN_LOAD4 1
#define poly_basemul poly_basemul_ldrtrn_noadd
#define _poly_basemul _poly_basemul_ldrtrn_noadd
#define poly_basemul_add poly_basemul_add_ldrtrn_noadd_unused
#define _poly_basemul_add _poly_basemul_add_ldrtrn_noadd_unused

#include "base_gt.opt.s"
