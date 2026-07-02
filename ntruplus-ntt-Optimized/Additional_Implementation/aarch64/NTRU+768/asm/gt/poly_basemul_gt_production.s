/*
 * Production GT poly_basemul wrapper.
 *
 * This exports only the generic poly_basemul ABI from the shared
 * Slothy-scheduled GT basemul body.  poly_basemul_add is renamed away because
 * production links the add32 full-pipeline implementation from
 * poly_basemul_add_gt_production.s.
 */
#define poly_basemul_add poly_basemul_add_gt_opt_unused
#define _poly_basemul_add _poly_basemul_add_gt_opt_unused

#include "base_gt.opt.s"
