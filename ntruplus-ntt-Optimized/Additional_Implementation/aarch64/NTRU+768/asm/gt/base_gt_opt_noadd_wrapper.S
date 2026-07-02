/*
 * Slothy-scheduled GT basemul/baseinv body with poly_basemul_add renamed away.
 *
 * This lets an experiment keep the fast production poly_basemul symbol while
 * providing a different poly_basemul_add implementation from another object.
 */
#define poly_basemul_add poly_basemul_add_gt_opt_unused
#define _poly_basemul_add _poly_basemul_add_gt_opt_unused

#include "base_gt.opt.s"
