#ifndef GT32_LATE_SOA_064_H
#define GT32_LATE_SOA_064_H

#include <stdint.h>

#define LATE064_WORDS 768

void late_full_inverse_i2_asm(int16_t out[LATE064_WORDS],
	const int16_t in[LATE064_WORDS]);
void late_soa_full_basemul_i2_fused_asm(int16_t out[LATE064_WORDS],
	const int16_t a[LATE064_WORDS], const int16_t b[LATE064_WORDS]);

void gt32_tile4_frontend_wide_raw_asm(int16_t *, const int16_t *);
void gt32_tile4_forward_all_pair_asm(int16_t *, const int16_t *);
void gt32_tile4_attr_forward_all_bm_soa_asm(int16_t *, const int16_t *);
void gt32_tile4_basemul_c3center_late_aos_private_asm(
	int16_t *, const int16_t *, const int16_t *);
void gt32_tile4_attr_basemul_i1_stage01_fused_asm(
	int16_t *, const int16_t *, const int16_t *);
void gt32_tile4_attr_inverse_i1_cross3_asm(int16_t *, const int16_t *);
void gt32_tile4_inverse_all_pair_asm(int16_t *, const int16_t *);
void gt32_tile4_attr_transpose_one_asm(int16_t *, const int16_t *);

#endif
