#include "hwa16.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint64_t state = UINT64_C(0x61c0ffee12345678);
static unsigned max_fwd, max_bm, max_inv;

static uint32_t rng32(void)
{
	state ^= state << 7;
	state ^= state >> 9;
	state ^= state << 8;
	return (uint32_t)state;
}

static int16_t mod_center(int32_t x)
{
	x %= HWA16_Q;
	if (x < 0) x += HWA16_Q;
	if (x > HWA16_Q / 2) x -= HWA16_Q;
	return (int16_t)x;
}

static void observe(const int16_t *x, unsigned *bound)
{
	for (unsigned i = 0; i < HWA16_WORDS; ++i) {
		const unsigned a = (unsigned)(x[i] < 0 ? -(int)x[i] : x[i]);
		if (a > *bound) *bound = a;
	}
}

static void fail(const char *label, unsigned trial, unsigned at,
	int16_t expected, int16_t actual)
{
	fprintf(stderr, "%s trial=%u word=%u expected=%d actual=%d\n",
		label, trial, at, expected, actual);
	exit(1);
}

static void exact(const char *label, unsigned trial, const int16_t *a,
	const int16_t *b)
{
	for (unsigned i = 0; i < HWA16_WORDS; ++i)
		if (a[i] != b[i]) fail(label, trial, i, a[i], b[i]);
}

static void modulo(const char *label, unsigned trial, const int16_t *a,
	const int16_t *b)
{
	for (unsigned i = 0; i < HWA16_WORDS; ++i)
		if (mod_center(a[i]) != mod_center(b[i]))
			fail(label, trial, i, mod_center(a[i]), mod_center(b[i]));
}

static void one_case(const int16_t tile_a[HWA16_WORDS],
	const int16_t tile_b[HWA16_WORDS], unsigned trial)
{
	int16_t ha[HWA16_WORDS] __attribute__((aligned(32)));
	int16_t hb[HWA16_WORDS] __attribute__((aligned(32)));
	int16_t ctla[HWA16_WORDS] __attribute__((aligned(32)));
	int16_t ctlb[HWA16_WORDS] __attribute__((aligned(32)));
	int16_t ctlp[HWA16_WORDS] __attribute__((aligned(32)));
	int16_t ctli[HWA16_WORDS] __attribute__((aligned(32)));
	int16_t h1[HWA16_WORDS] __attribute__((aligned(32)));
	int16_t h2[HWA16_WORDS] __attribute__((aligned(32)));
	int16_t hp[HWA16_WORDS] __attribute__((aligned(32)));
	int16_t hi[HWA16_WORDS] __attribute__((aligned(32)));
	int16_t ref[HWA16_WORDS] __attribute__((aligned(32)));
	int16_t mapped[HWA16_WORDS] __attribute__((aligned(32)));
	int16_t alias[HWA16_WORDS] __attribute__((aligned(32)));

	hwa16_from_tile4(ha, tile_a);
	hwa16_from_tile4(hb, tile_b);
	hwa16_to_tile4(mapped, ha);
	exact("mapping-roundtrip", trial, tile_a, mapped);

	ctl_tile4_forward_asm(ctla, tile_a);
	ctl_tile4_forward_asm(ctlb, tile_b);
	hwa16_from_tile4(mapped, ctla);
	hwa16_forward_ref(ref, ha);
	exact("forward-reference", trial, ref, mapped);
	hwa16_forward_v1_asm(h1, ha);
	hwa16_forward_v2_asm(h2, ha);
	exact("forward-v1", trial, mapped, h1);
	exact("forward-v2", trial, mapped, h2);
	observe(h2, &max_fwd);
	memcpy(alias, ha, sizeof(alias));
	hwa16_forward_v2_asm(alias, alias);
	exact("forward-v2-alias", trial, h2, alias);

	ctl_tile4_basemul_asm(ctlp, ctla, ctlb);
	/* Recompute b in HWA: h2 currently contains Forward(a). */
	hwa16_forward_v2_asm(h2, hb);
	hwa16_basemul_asm(hp, h1, h2);
	hwa16_from_tile4(mapped, ctlp);
	hwa16_basemul_ref(ref, h1, h2);
	modulo("basemul-reference", trial, ref, hp);
	exact("basemul-control", trial, mapped, hp);
	observe(hp, &max_bm);

	ctl_tile4_inverse_asm(ctli, ctlp);
	hwa16_inverse_ref(ref, hp);
	hwa16_inverse_v1_asm(h1, hp);
	hwa16_inverse_v2_asm(hi, hp);
	hwa16_from_tile4(mapped, ctli);
	exact("inverse-reference", trial, ref, hi);
	exact("inverse-v1", trial, mapped, h1);
	exact("inverse-v2", trial, mapped, hi);
	modulo("complete-2fbi", trial, mapped, hi);
	observe(hi, &max_inv);
	memcpy(alias, hp, sizeof(alias));
	hwa16_inverse_v2_asm(alias, alias);
	exact("inverse-v2-alias", trial, hi, alias);
}

static void fill_structured(int16_t *a, int16_t *b, unsigned kind)
{
	static const int16_t values[] = {0, 1, -1, 1728, -1728, 3456, 1730, -1730};
	for (unsigned i = 0; i < HWA16_WORDS; ++i) {
		a[i] = values[(i + kind) % (sizeof(values) / sizeof(values[0]))];
		b[i] = values[(3U * i + 2U * kind) % (sizeof(values) / sizeof(values[0]))];
	}
}

int main(void)
{
	int16_t a[HWA16_WORDS] __attribute__((aligned(32)));
	int16_t b[HWA16_WORDS] __attribute__((aligned(32)));
	unsigned trial = 0;

	/* Complete scalar mapping oracle. */
	for (unsigned i = 0; i < HWA16_WORDS; ++i) a[i] = (int16_t)i;
	hwa16_from_tile4(b, a);
	for (unsigned c = 0; c < 4; ++c)
		for (unsigned q = 0; q < 32; ++q) {
			const int16_t want = (int16_t)(16U * (q / 4U) + 4U * (q % 4U) + c);
			if (b[32U * c + q] != want)
				fail("mapping-oracle", 0, 32U * c + q, want, b[32U * c + q]);
		}

	/* Every logical impulse. */
	for (unsigned i = 0; i < HWA16_WORDS; ++i) {
		memset(a, 0, sizeof(a));
		memset(b, 0, sizeof(b));
		a[i] = 1;
		b[(37U * i + 11U) & 127U] = -1;
		one_case(a, b, trial++);
	}
	for (unsigned kind = 0; kind < 8; ++kind) {
		fill_structured(a, b, kind);
		one_case(a, b, trial++);
	}
	/* Centered frontend-shaped range. */
	for (unsigned n = 0; n < 1000; ++n) {
		for (unsigned i = 0; i < HWA16_WORDS; ++i) {
			a[i] = (int16_t)((int)(rng32() % 3457U) - 1728);
			b[i] = (int16_t)((int)(rng32() % 3457U) - 1728);
		}
		one_case(a, b, trial++);
	}
	/* Canonical modulo-q values, supported by the control's int16 range. */
	for (unsigned n = 0; n < 200; ++n) {
		for (unsigned i = 0; i < HWA16_WORDS; ++i) {
			a[i] = (int16_t)(rng32() % HWA16_Q);
			b[i] = (int16_t)(rng32() % HWA16_Q);
		}
		one_case(a, b, trial++);
	}
	printf("HWA16 correctness passed: trials=%u impulses=128 aliases=F/I "
	       "B3_alias=disallowed observed_abs={F:%u,B:%u,I:%u}\n",
	       trial, max_fwd, max_bm, max_inv);
	return 0;
}
