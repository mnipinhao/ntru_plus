/* Typed P-SoA BaseInv instantiation returning inverse*R (e=1). */
#include <stdint.h>

#include "../../gt_ntt/gt_basemul_soa.h"

/* The current P BaseInv instantiation owns the shared P lambda tables. */

/* Replace only the final fixed factor in field_inverse(). */
#define GT_RINV 1
#define GT_RINV_QINV 12929
#define GT_BATCH_INVERSE_EXTERNAL gt32_p_j1_batch_inverse_tree_asm

#define gt_baseinv_center_l8_test_avx2 gt32_p_j1_baseinv_center_l8_test_avx2
#define gt_baseinv_native_centered_avx2 gt32_p_j1_baseinv_direct_avx2
#define gt_baseinv_native_center_on_load_avx2 gt32_p_j1_baseinv_center_on_load_avx2
#define gt_baseinv_native_quadratic_centered_avx2 gt32_p_j1_baseinv_quad_centered_avx2
#define gt_baseinv_native_quadratic_center_on_load_avx2 gt32_p_j1_baseinv_quad_center_on_load_avx2
#define gt_baseinv_native_quadratic_abi_avx2 gt32_p_j1_baseinv_quad_abi_avx2
#define gt_baseinv_native_centered_asm_avx2 gt32_p_j1_baseinv_direct_asm_avx2
#define gt_baseinv_native_center_on_load_asm_avx2 gt32_p_j1_baseinv_center_on_load_asm_avx2
#include "../../gt_ntt/gt_baseinv_native.c"
