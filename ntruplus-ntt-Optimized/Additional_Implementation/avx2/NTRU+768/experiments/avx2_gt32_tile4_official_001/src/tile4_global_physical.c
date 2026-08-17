#include "tile4_global_physical.h"

#include "tile4.h"

void gt32_global_forward_core_asm(int16_t *, const int16_t *);
void gt32_global_inverse_core_asm(int16_t *, const int16_t *);
void gt32_tile4_basemul_scale_soa_soa_to_m_private_asm(
	int16_t *, const int16_t *, const int16_t *);

void gt32_global_physical_polymul_private(
	int16_t out[GT32_GLOBAL_PHYSICAL_WORDS],
	const int16_t a[GT32_GLOBAL_PHYSICAL_WORDS],
	const int16_t b[GT32_GLOBAL_PHYSICAL_WORDS],
	gt32_global_physical_scratch_t *scratch)
{
	gt32_tile4_frontend_wide_raw_asm(scratch->frontend, a);
	gt32_global_forward_core_asm(scratch->forward_a, scratch->frontend);
	gt32_tile4_frontend_wide_raw_asm(scratch->frontend, b);
	gt32_global_forward_core_asm(scratch->forward_b, scratch->frontend);
	gt32_tile4_basemul_scale_soa_soa_to_m_private_asm(scratch->product,
		scratch->forward_a, scratch->forward_b);
	gt32_global_inverse_core_asm(scratch->inverse_rows, scratch->product);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out,
		scratch->inverse_rows);
}
