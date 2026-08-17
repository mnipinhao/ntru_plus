/* Fixed-layout SUPERcop A/B wrapper.
 *
 * Both binaries link the current P and P-J1 BaseInv implementations plus both
 * native BaseMul entry points.  The one-byte configuration value changes only
 * which already-linked pair the Keypair body calls.
 */
#include "gt32_fixed_p_j1_select.h"

#include <stdint.h>

extern int gt32_p_baseinv_direct_avx2(int16_t *, const int16_t *);
extern int gt32_p_j1_baseinv_direct_avx2(int16_t *, const int16_t *);

/* SUPERcop resolves source files from undefined symbols.  Keep this externally
 * visible, never-called anchor identical in A and B so both BaseInv objects are
 * selected before the call-target switch is applied below. */
int gt32_fixed_p_j1_retain_both_baseinv(int16_t *out, const int16_t *in)
{
	return gt32_p_baseinv_direct_avx2(out, in) |
		gt32_p_j1_baseinv_direct_avx2(out, in);
}

#if GT32_FIXED_P_J1_SELECT
#define gt32_p_baseinv_direct_avx2 gt32_p_j1_baseinv_direct_avx2
#define gt_basemul_native_asm_avx2 gt_basemul_native_f0_j1_e0_asm_avx2
#endif

#define gt32_q24_encode_p_soa_halfscatter_lazy10788_asm \
	gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm
#include "tile4_keygen_candidate.inc"
