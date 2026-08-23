#include "full_bridge.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint64_t state = UINT64_C(0x0649e3779b97f4a7);
static unsigned max_forward;
static unsigned max_i2;
static unsigned max_inverse;

static uint32_t rng32(void)
{
	state ^= state << 7;
	state ^= state >> 9;
	return (uint32_t)state;
}

static void exact(const char *label, unsigned trial, const int16_t *a,
	const int16_t *b)
{
	for (unsigned i = 0; i < LATE064_WORDS; ++i) if (a[i] != b[i]) {
		fprintf(stderr, "%s trial=%u word=%u expected=%d actual=%d\n",
			label, trial, i, a[i], b[i]);
		exit(1);
	}
}

static void observe(const int16_t *x, unsigned *bound)
{
	for (unsigned i = 0; i < LATE064_WORDS; ++i) {
		const unsigned v = (unsigned)(x[i] < 0 ? -(int)x[i] : x[i]);
		if (v > *bound) *bound = v;
	}
}

static void one_case(const int16_t *a, const int16_t *b, unsigned trial)
{
	int16_t fa[768] __attribute__((aligned(64)));
	int16_t fb[768] __attribute__((aligned(64)));
	int16_t ca[768] __attribute__((aligned(64)));
	int16_t cb[768] __attribute__((aligned(64)));
	int16_t sa[768] __attribute__((aligned(64)));
	int16_t sb[768] __attribute__((aligned(64)));
	int16_t mapped[768] __attribute__((aligned(64)));
	int16_t product[768] __attribute__((aligned(64)));
	int16_t i20[768] __attribute__((aligned(64)));
	int16_t i21[768] __attribute__((aligned(64)));
	int16_t i2l[768] __attribute__((aligned(64)));
	int16_t out0[768] __attribute__((aligned(64)));
	int16_t out1[768] __attribute__((aligned(64)));

	gt32_tile4_frontend_wide_raw_asm(fa, a);
	gt32_tile4_frontend_wide_raw_asm(fb, b);
	gt32_tile4_forward_all_pair_asm(ca, fa);
	gt32_tile4_forward_all_pair_asm(cb, fb);
	gt32_tile4_attr_forward_all_bm_soa_asm(sa, fa);
	gt32_tile4_attr_forward_all_bm_soa_asm(sb, fb);
	gt32_tile4_attr_transpose_one_asm(mapped, ca);
	exact("forward-a", trial, mapped, sa);
	gt32_tile4_attr_transpose_one_asm(mapped, cb);
	exact("forward-b", trial, mapped, sb);
	observe(ca, &max_forward);

	gt32_tile4_basemul_c3center_late_aos_private_asm(product, ca, cb);
	late_full_inverse_i2_asm(i20, product);
	gt32_tile4_attr_basemul_i1_stage01_fused_asm(i21, ca, cb);
	late_soa_full_basemul_i2_fused_asm(i2l, sa, sb);
	exact("aos-fused-i2", trial, i20, i21);
	exact("late-soa-i2", trial, i20, i2l);
	observe(i2l, &max_i2);

	gt32_tile4_inverse_all_pair_asm(out0, product);
	gt32_tile4_attr_inverse_i1_cross3_asm(out1, i2l);
	exact("complete-2FBI", trial, out0, out1);
	observe(out1, &max_inverse);
}

int main(void)
{
	int16_t a[768] __attribute__((aligned(64)));
	int16_t b[768] __attribute__((aligned(64)));
	unsigned trial = 0;
	for (unsigned i = 0; i < 768; ++i) {
		memset(a, 0, sizeof(a));
		memset(b, 0, sizeof(b));
		a[i] = 1;
		b[(i * 181U + 17U) % 768U] = -1;
		one_case(a, b, trial++);
	}
	static const int16_t values[] = {0, 1, -1, 1728, -1728, 3456, 1730, -1730};
	for (unsigned k = 0; k < 8; ++k) {
		for (unsigned i = 0; i < 768; ++i) {
			a[i] = values[(i + k) & 7U];
			b[i] = values[(5U * i + 3U * k) & 7U];
		}
		one_case(a, b, trial++);
	}
	for (unsigned n = 0; n < 1000; ++n) {
		for (unsigned i = 0; i < 768; ++i) {
			a[i] = (int16_t)((int)(rng32() % 3457U) - 1728);
			b[i] = (int16_t)((int)(rng32() % 3457U) - 1728);
		}
		one_case(a, b, trial++);
	}
	printf("Late-SoA six-tile correctness passed: trials=%u "
	       "observed_abs={F:%u,postI2:%u,I:%u}\n",
		trial, max_forward, max_i2, max_inverse);
	return 0;
}
