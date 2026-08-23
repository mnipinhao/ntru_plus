#include "late_soa.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint64_t rng_state = UINT64_C(0x0639e3779b97f4a7);
static unsigned max_suffix;
static unsigned max_i2;

static uint32_t rng32(void)
{
	rng_state ^= rng_state << 7;
	rng_state ^= rng_state >> 9;
	return (uint32_t)rng_state;
}

static void exact(const char *label, unsigned trial, const int16_t *a,
	const int16_t *b)
{
	for (unsigned i = 0; i < LATE_SOA_WORDS; ++i) if (a[i] != b[i]) {
		fprintf(stderr, "%s trial=%u word=%u expected=%d actual=%d\n",
			label, trial, i, a[i], b[i]);
		exit(1);
	}
}

static void observe(const int16_t *x, unsigned *bound)
{
	for (unsigned i = 0; i < LATE_SOA_WORDS; ++i) {
		const unsigned v = (unsigned)(x[i] < 0 ? -(int)x[i] : x[i]);
		if (v > *bound) *bound = v;
	}
}

static void one_case(const int16_t *a, const int16_t *b, unsigned trial)
{
	int16_t aa[128] __attribute__((aligned(32)));
	int16_t ab[128] __attribute__((aligned(32)));
	int16_t sa[128] __attribute__((aligned(32)));
	int16_t sb[128] __attribute__((aligned(32)));
	int16_t refsa[128] __attribute__((aligned(32)));
	int16_t refsb[128] __attribute__((aligned(32)));
	int16_t product[128] __attribute__((aligned(32)));
	int16_t c0[128] __attribute__((aligned(32)));
	int16_t c1[128] __attribute__((aligned(32)));
	int16_t late[128] __attribute__((aligned(32)));
	int16_t alias[128] __attribute__((aligned(32)));

	late_suffix_aos_asm(aa, a);
	late_suffix_aos_asm(ab, b);
	late_suffix_soa_asm(sa, a);
	late_suffix_soa_asm(sb, b);
	late_aos_to_soa_asm(refsa, aa);
	late_aos_to_soa_asm(refsb, ab);
	exact("suffix-a", trial, refsa, sa);
	exact("suffix-b", trial, refsb, sb);
	observe(aa, &max_suffix);

	ctl_tile4_basemul_asm(product, aa, ab);
	late_inverse_i2_asm(c0, product);
	late_aos_basemul_i2_fused_asm(c1, aa, ab);
	late_soa_basemul_i2_fused_asm(late, sa, sb);
	exact("aos-fused", trial, c0, c1);
	exact("late-soa", trial, c0, late);
	observe(late, &max_i2);

	memcpy(alias, a, sizeof(alias));
	late_suffix_aos_asm(alias, alias);
	exact("suffix-aos-alias", trial, aa, alias);
	memcpy(alias, a, sizeof(alias));
	late_suffix_soa_asm(alias, alias);
	exact("suffix-soa-alias", trial, sa, alias);
	memcpy(alias, aa, sizeof(alias));
	late_aos_basemul_i2_fused_asm(alias, alias, ab);
	exact("aos-bm-alias", trial, c1, alias);
	memcpy(alias, sa, sizeof(alias));
	late_soa_basemul_i2_fused_asm(alias, alias, sb);
	exact("soa-bm-alias", trial, late, alias);
}

int main(void)
{
	int16_t a[128] __attribute__((aligned(32)));
	int16_t b[128] __attribute__((aligned(32)));
	unsigned trial = 0;

	for (unsigned i = 0; i < 128; ++i) {
		memset(a, 0, sizeof(a));
		memset(b, 0, sizeof(b));
		a[i] = 1;
		b[(i * 37U + 9U) & 127U] = -1;
		one_case(a, b, trial++);
	}
	static const int16_t values[] = {0, 1, -1, 1728, -1728, 3456, 1730, -1730};
	for (unsigned k = 0; k < 8; ++k) {
		for (unsigned i = 0; i < 128; ++i) {
			a[i] = values[(i + k) & 7U];
			b[i] = values[(3U * i + 2U * k) & 7U];
		}
		one_case(a, b, trial++);
	}
	for (unsigned n = 0; n < 1200; ++n) {
		for (unsigned i = 0; i < 128; ++i) {
			a[i] = (int16_t)((int)(rng32() % 3457U) - 1728);
			b[i] = (int16_t)((int)(rng32() % 3457U) - 1728);
		}
		one_case(a, b, trial++);
	}
	printf("Late-SoA correctness passed: trials=%u aliases=suffix/BM "
	       "observed_abs={suffix:%u,postI2:%u}\n", trial, max_suffix, max_i2);
	return 0;
}
