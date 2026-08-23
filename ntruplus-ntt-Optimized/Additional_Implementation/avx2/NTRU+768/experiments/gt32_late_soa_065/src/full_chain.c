#include "full_chain.h"

#if defined(__GNUC__)
#define LATE065_ENTRY __attribute__((noinline, used, noipa))
#else
#define LATE065_ENTRY
#endif

LATE065_ENTRY
void late065_chain_c0(int16_t out[LATE065_WORDS],
	const int16_t a[LATE065_WORDS], const int16_t b[LATE065_WORDS],
	late065_scratch *scratch)
{
	gt32_tile4_frontend_wide_raw_asm(scratch->frontend, a);
	gt32_tile4_forward_all_pair_asm(scratch->operand_a, scratch->frontend);
	gt32_tile4_frontend_wide_raw_asm(scratch->frontend, b);
	gt32_tile4_forward_all_pair_asm(scratch->operand_b, scratch->frontend);
	gt32_tile4_basemul_c3center_late_aos_private_asm(scratch->product,
		scratch->operand_a, scratch->operand_b);
	gt32_tile4_inverse_all_pair_asm(scratch->inverse_rows,
		scratch->product);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out,
		scratch->inverse_rows);
}

LATE065_ENTRY
void late065_chain_c1(int16_t out[LATE065_WORDS],
	const int16_t a[LATE065_WORDS], const int16_t b[LATE065_WORDS],
	late065_scratch *scratch)
{
	gt32_tile4_frontend_wide_raw_asm(scratch->frontend, a);
	gt32_tile4_forward_all_pair_asm(scratch->operand_a, scratch->frontend);
	gt32_tile4_frontend_wide_raw_asm(scratch->frontend, b);
	gt32_tile4_forward_all_pair_asm(scratch->operand_b, scratch->frontend);
	gt32_tile4_attr_basemul_i1_stage01_fused_asm(scratch->product,
		scratch->operand_a, scratch->operand_b);
	gt32_tile4_attr_inverse_i1_cross3_asm(scratch->inverse_rows,
		scratch->product);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out,
		scratch->inverse_rows);
}

LATE065_ENTRY
void late065_chain_l0(int16_t out[LATE065_WORDS],
	const int16_t a[LATE065_WORDS], const int16_t b[LATE065_WORDS],
	late065_scratch *scratch)
{
	gt32_tile4_frontend_wide_raw_asm(scratch->frontend, a);
	gt32_tile4_attr_forward_all_bm_soa_asm(scratch->operand_a,
		scratch->frontend);
	gt32_tile4_frontend_wide_raw_asm(scratch->frontend, b);
	gt32_tile4_attr_forward_all_bm_soa_asm(scratch->operand_b,
		scratch->frontend);
	late_soa_full_basemul_i2_fused_asm(scratch->product,
		scratch->operand_a, scratch->operand_b);
	gt32_tile4_attr_inverse_i1_cross3_asm(scratch->inverse_rows,
		scratch->product);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out,
		scratch->inverse_rows);
}
