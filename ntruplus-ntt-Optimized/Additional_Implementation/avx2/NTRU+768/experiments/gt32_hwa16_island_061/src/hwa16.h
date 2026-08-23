#ifndef GT32_HWA16_ISLAND_061_H
#define GT32_HWA16_ISLAND_061_H

#include <stdint.h>

#define HWA16_Q 3457
#define HWA16_WORDS 128

/* TILE4 word = 16*(Q/4) + 4*(Q%4) + c. */
/* HWA16 word = 32*c + 16*g + lane, Q=16*g+lane. */
void hwa16_from_tile4(int16_t out[HWA16_WORDS],
	const int16_t in[HWA16_WORDS]);
void hwa16_to_tile4(int16_t out[HWA16_WORDS],
	const int16_t in[HWA16_WORDS]);

void hwa16_forward_ref(int16_t out[HWA16_WORDS],
	const int16_t in[HWA16_WORDS]);
void hwa16_inverse_ref(int16_t out[HWA16_WORDS],
	const int16_t in[HWA16_WORDS]);
void hwa16_basemul_ref(int16_t out[HWA16_WORDS],
	const int16_t a[HWA16_WORDS], const int16_t b[HWA16_WORDS]);

void ctl_tile4_forward_asm(int16_t out[HWA16_WORDS],
	const int16_t in[HWA16_WORDS]);
void ctl_tile4_basemul_asm(int16_t out[HWA16_WORDS],
	const int16_t a[HWA16_WORDS], const int16_t b[HWA16_WORDS]);
void ctl_tile4_inverse_asm(int16_t out[HWA16_WORDS],
	const int16_t in[HWA16_WORDS]);

/* V1: direct per-vector HWA16 routing. */
void hwa16_forward_v1_asm(int16_t out[HWA16_WORDS],
	const int16_t in[HWA16_WORDS]);
void hwa16_inverse_v1_asm(int16_t out[HWA16_WORDS],
	const int16_t in[HWA16_WORDS]);
/* V2: semantic-equivalent two-vector packed routing mutation. */
void hwa16_forward_v2_asm(int16_t out[HWA16_WORDS],
	const int16_t in[HWA16_WORDS]);
void hwa16_inverse_v2_asm(int16_t out[HWA16_WORDS],
	const int16_t in[HWA16_WORDS]);
void hwa16_basemul_asm(int16_t out[HWA16_WORDS],
	const int16_t a[HWA16_WORDS], const int16_t b[HWA16_WORDS]);

enum hwa16_v3_mapping {
	HWA16_V3_M40A = 0,
	HWA16_V3_M40B = 1,
	HWA16_V3_M40C = 2,
	HWA16_V3_MAPPINGS = 3
};
void hwa16_v3_from_tile4(int16_t out[HWA16_WORDS],
	const int16_t in[HWA16_WORDS], enum hwa16_v3_mapping mapping);
void hwa16_v3_to_tile4(int16_t out[HWA16_WORDS],
	const int16_t in[HWA16_WORDS], enum hwa16_v3_mapping mapping);

#define HWA16_DECLARE_V3(name) \
	void hwa16_v3_forward_##name##_asm(int16_t *, const int16_t *); \
	void hwa16_v3_inverse_##name##_asm(int16_t *, const int16_t *); \
	void hwa16_v3_basemul_##name##_asm(int16_t *, const int16_t *, const int16_t *)
HWA16_DECLARE_V3(m40a);
HWA16_DECLARE_V3(m40b);
HWA16_DECLARE_V3(m40c);
#undef HWA16_DECLARE_V3

#endif
