#define poly_basemul gt_poly_basemul
#define _poly_basemul _gt_poly_basemul
#define poly_basemul_add gt_poly_basemul_add
#define _poly_basemul_add _gt_poly_basemul_add
#define poly_baseinv_1 gt_poly_baseinv_1
#define _poly_baseinv_1 _gt_poly_baseinv_1

#ifndef BENCH_PMU_GT_BASE_INCLUDE
#define BENCH_PMU_GT_BASE_INCLUDE "../asm/base_gt.S"
#endif

#include BENCH_PMU_GT_BASE_INCLUDE
