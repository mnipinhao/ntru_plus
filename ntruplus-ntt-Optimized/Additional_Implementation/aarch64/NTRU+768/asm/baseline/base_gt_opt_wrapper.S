/*
 * Compile the Slothy-scheduled base_gt.opt.s body through the C preprocessor.
 *
 * The optimized body needs a small target-specific LOAD_ADDR macro: Linux/GNU
 * uses adrp/add with :lo12:, while Darwin/Mach-O requires @PAGE/@PAGEOFF and
 * a leading underscore for C-visible symbols.
 */
#include "../gt/base_gt.opt.s"
