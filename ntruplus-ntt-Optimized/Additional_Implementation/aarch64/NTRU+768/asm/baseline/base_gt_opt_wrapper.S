/*
 * Compile the Slothy-scheduled GT basemul body through the C preprocessor.
 *
 * The optimized body needs a small target-specific LOAD_ADDR macro: Linux/GNU
 * uses adrp/add with :lo12:, while Darwin/Mach-O requires @PAGE/@PAGEOFF and
 * a leading underscore for C-visible symbols.
 */
#define GT_BASEMUL_EMIT_BASEMUL 1
#define GT_BASEMUL_SYMBOL poly_basemul
#define GT_BASEMUL_DARWIN_SYMBOL _poly_basemul
#define GT_BASEMUL_EMIT_ADD 1
#define GT_BASEMUL_ADD_SYMBOL poly_basemul_add
#define GT_BASEMUL_ADD_DARWIN_SYMBOL _poly_basemul_add

#include "../gt/base_gt_opt_body.inc"
