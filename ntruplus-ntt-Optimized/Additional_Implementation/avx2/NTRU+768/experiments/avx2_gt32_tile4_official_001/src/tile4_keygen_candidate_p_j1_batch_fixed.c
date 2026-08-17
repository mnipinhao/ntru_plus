/* Fixed-source-set SUPERcop selector for compiler-C versus product-tree batch. */
#include "gt32_p_j1_batch_select.h"

#include <stdint.h>

extern int gt32_p_j1_baseinv_direct_avx2(int16_t *, const int16_t *);
extern int gt32_p_j1_c_baseinv_direct_avx2(int16_t *, const int16_t *);

/* Force SUPERcop's dependency resolver to retain both BaseInv implementations. */
int gt32_p_j1_batch_retain_both(int16_t *out, const int16_t *in)
{
	return gt32_p_j1_baseinv_direct_avx2(out, in) |
		gt32_p_j1_c_baseinv_direct_avx2(out, in);
}

#if GT32_P_J1_BATCH_TREE_SELECT
#define gt32_p_baseinv_direct_avx2 gt32_p_j1_baseinv_direct_avx2
#else
#define gt32_p_baseinv_direct_avx2 gt32_p_j1_c_baseinv_direct_avx2
#endif

#define gt_basemul_native_asm_avx2 gt_basemul_native_f0_j1_e0_asm_avx2
#define gt32_q24_encode_p_soa_halfscatter_lazy10788_asm \
	gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm
#include "tile4_keygen_candidate.inc"
