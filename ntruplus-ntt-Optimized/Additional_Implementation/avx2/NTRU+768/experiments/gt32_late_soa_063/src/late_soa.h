#ifndef GT32_LATE_SOA_063_H
#define GT32_LATE_SOA_063_H

#include <stdint.h>

#define LATE_SOA_WORDS 128

/* Shared input: one fixed (branch,k3) island after Forward stage 3. */
void late_suffix_aos_asm(int16_t out[LATE_SOA_WORDS],
	const int16_t post_s3[LATE_SOA_WORDS]);
void late_suffix_soa_asm(int16_t out[LATE_SOA_WORDS],
	const int16_t post_s3[LATE_SOA_WORDS]);
void late_aos_to_soa_asm(int16_t out[LATE_SOA_WORDS],
	const int16_t in[LATE_SOA_WORDS]);

/* Shared output: TILE4/AoS state after inverse stages 0 and 1. */
void late_inverse_i2_asm(int16_t out[LATE_SOA_WORDS],
	const int16_t in[LATE_SOA_WORDS]);
void late_aos_basemul_i2_fused_asm(int16_t out[LATE_SOA_WORDS],
	const int16_t a[LATE_SOA_WORDS], const int16_t b[LATE_SOA_WORDS]);
void late_soa_basemul_i2_fused_asm(int16_t out[LATE_SOA_WORDS],
	const int16_t a[LATE_SOA_WORDS], const int16_t b[LATE_SOA_WORDS]);

/* Reused fixed TILE4 arithmetic control from experiment 061. */
void ctl_tile4_basemul_asm(int16_t out[LATE_SOA_WORDS],
	const int16_t a[LATE_SOA_WORDS], const int16_t b[LATE_SOA_WORDS]);

#endif
