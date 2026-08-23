#include "hwa16.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

typedef void (*unary_fn)(int16_t *, const int16_t *);
typedef void (*binary_fn)(int16_t *, const int16_t *, const int16_t *);

static const unary_fn forwards[HWA16_V3_MAPPINGS] = {
	hwa16_v3_forward_m40a_asm, hwa16_v3_forward_m40b_asm,
	hwa16_v3_forward_m40c_asm
};
static const unary_fn inverses[HWA16_V3_MAPPINGS] = {
	hwa16_v3_inverse_m40a_asm, hwa16_v3_inverse_m40b_asm,
	hwa16_v3_inverse_m40c_asm
};
static const binary_fn basemuls[HWA16_V3_MAPPINGS] = {
	hwa16_v3_basemul_m40a_asm, hwa16_v3_basemul_m40b_asm,
	hwa16_v3_basemul_m40c_asm
};
static uint64_t rng_state = UINT64_C(0x06130000deadbeef);

static uint32_t rng32(void)
{
	rng_state ^= rng_state << 7;
	rng_state ^= rng_state >> 9;
	return (uint32_t)rng_state;
}

static void fill_structured(int16_t *a, int16_t *b, unsigned kind)
{
	static const int16_t values[] = {0, 1, -1, 1728, -1728, 3456, 1730, -1730};
	for (unsigned i = 0; i < HWA16_WORDS; ++i) {
		a[i] = values[(i + kind) % (sizeof(values) / sizeof(values[0]))];
		b[i] = values[(3U * i + 2U * kind) %
			(sizeof(values) / sizeof(values[0]))];
	}
}

static void compare(const char *what, unsigned trial, unsigned mapping,
	const int16_t *expected, const int16_t *actual)
{
	for (unsigned i = 0; i < HWA16_WORDS; ++i)
		if (expected[i] != actual[i]) {
			fprintf(stderr, "%s mapping=%u trial=%u word=%u expected=%d actual=%d\n",
				what, mapping, trial, i, expected[i], actual[i]);
			exit(1);
		}
}

static void one_case(const int16_t *a, const int16_t *b, unsigned trial)
{
	int16_t cfa[128] __attribute__((aligned(32)));
	int16_t cfb[128] __attribute__((aligned(32)));
	int16_t cp[128] __attribute__((aligned(32)));
	int16_t ci[128] __attribute__((aligned(32)));
	int16_t ha[128] __attribute__((aligned(32)));
	int16_t hb[128] __attribute__((aligned(32)));
	int16_t hfa[128] __attribute__((aligned(32)));
	int16_t hfb[128] __attribute__((aligned(32)));
	int16_t hp[128] __attribute__((aligned(32)));
	int16_t hi[128] __attribute__((aligned(32)));
	int16_t mapped[128] __attribute__((aligned(32)));
	int16_t alias[128] __attribute__((aligned(32)));

	ctl_tile4_forward_asm(cfa, a);
	ctl_tile4_forward_asm(cfb, b);
	ctl_tile4_basemul_asm(cp, cfa, cfb);
	ctl_tile4_inverse_asm(ci, cp);
	for (unsigned m = 0; m < HWA16_V3_MAPPINGS; ++m) {
		hwa16_v3_from_tile4(ha, a, (enum hwa16_v3_mapping)m);
		hwa16_v3_from_tile4(hb, b, (enum hwa16_v3_mapping)m);
		hwa16_v3_to_tile4(mapped, ha, (enum hwa16_v3_mapping)m);
		compare("mapping", trial, m, a, mapped);
		forwards[m](hfa, ha);
		forwards[m](hfb, hb);
		hwa16_v3_to_tile4(mapped, hfa, (enum hwa16_v3_mapping)m);
		compare("forward", trial, m, cfa, mapped);
		basemuls[m](hp, hfa, hfb);
		hwa16_v3_to_tile4(mapped, hp, (enum hwa16_v3_mapping)m);
		compare("basemul", trial, m, cp, mapped);
		inverses[m](hi, hp);
		hwa16_v3_to_tile4(mapped, hi, (enum hwa16_v3_mapping)m);
		compare("complete", trial, m, ci, mapped);
		memcpy(alias, ha, sizeof(alias));
		forwards[m](alias, alias);
		compare("forward-alias", trial, m, hfa, alias);
		memcpy(alias, hp, sizeof(alias));
		inverses[m](alias, alias);
		compare("inverse-alias", trial, m, hi, alias);
	}
}

int main(void)
{
	int16_t a[128] __attribute__((aligned(32)));
	int16_t b[128] __attribute__((aligned(32)));
	unsigned trial = 0;
	for (unsigned impulse = 0; impulse < 128; ++impulse) {
		memset(a, 0, sizeof(a)); memset(b, 0, sizeof(b));
		a[impulse] = 1; b[(impulse * 29U + 7U) & 127U] = -1;
		one_case(a, b, trial++);
	}
	for (unsigned kind = 0; kind < 8; ++kind) {
		fill_structured(a, b, kind);
		one_case(a, b, trial++);
	}
	for (unsigned n = 0; n < 1000; ++n) {
		for (unsigned i = 0; i < 128; ++i) {
			a[i] = (int16_t)((int)(rng32() % 3457U) - 1728);
			b[i] = (int16_t)((int)(rng32() % 3457U) - 1728);
		}
		one_case(a, b, trial++);
	}
	for (unsigned n = 0; n < 200; ++n) {
		for (unsigned i = 0; i < 128; ++i) {
			a[i] = (int16_t)(rng32() % HWA16_Q);
			b[i] = (int16_t)(rng32() % HWA16_Q);
		}
		one_case(a, b, trial++);
	}
	printf("HWA16 V3 correctness passed: mappings=3 trials=%u aliases=F/I\n", trial);
	return 0;
}
