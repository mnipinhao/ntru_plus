/*
 * Benchmark-only stock poly_basemul_add wrapper.
 *
 * This includes stock asm/base.s but renames every public stock arithmetic
 * symbol except poly_basemul_add, which is exported under an experimental
 * cross-backend name.  It lets GT production benchmarks call stock
 * poly_basemul_add without replacing the rest of the GT arithmetic path.
 */

#define poly_basemul poly_basemul_stock_noce_unused
#define _poly_basemul _poly_basemul_stock_noce_unused
#define poly_basemul_add poly_basemul_add_stock_noce_experimental
#define _poly_basemul_add _poly_basemul_add_stock_noce_experimental
#define poly_baseinv_1 poly_baseinv_1_stock_noce_unused
#define _poly_baseinv_1 _poly_baseinv_1_stock_noce_unused
#define poly_ntt poly_ntt_stock_noce_unused
#define _poly_ntt _poly_ntt_stock_noce_unused
#define poly_invntt poly_invntt_stock_noce_unused
#define _poly_invntt _poly_invntt_stock_noce_unused

#include "ntruplus/asm/base.s"
