#ifndef GT32_HWA16_PRODUCER_062_H
#define GT32_HWA16_PRODUCER_062_H

#include <stdint.h>

#define PRODUCER062_N 768
#define PRODUCER062_TILE_WORDS 128

void gt32_tile4_frontend_wide_raw_f14_asm(int16_t out[PRODUCER062_N],
	const int16_t in[PRODUCER062_N]);

void producer062_p0_tile4_post_s1_asm(int16_t out[PRODUCER062_TILE_WORDS],
	const int16_t in[PRODUCER062_N]);
void producer062_p1_hwa_explicit_post_s1_asm(
	int16_t out[PRODUCER062_TILE_WORDS], const int16_t in[PRODUCER062_N]);
void producer062_p2_hwa_fused_post_s1_asm(
	int16_t out[PRODUCER062_TILE_WORDS], const int16_t in[PRODUCER062_N]);

void hwa16_from_tile4(int16_t hwa[PRODUCER062_TILE_WORDS],
	const int16_t tile[PRODUCER062_TILE_WORDS]);
void hwa16_to_tile4(int16_t tile[PRODUCER062_TILE_WORDS],
	const int16_t hwa[PRODUCER062_TILE_WORDS]);

#endif
