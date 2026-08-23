#include "full_chain.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint64_t rng_state = UINT64_C(0x0659e3779b97f4a7);
static unsigned max_output;

static uint32_t rng32(void)
{
	rng_state ^= rng_state << 7;
	rng_state ^= rng_state >> 9;
	return (uint32_t)rng_state;
}

static void exact(const char *profile, const char *mode, unsigned trial,
	const int16_t *expected, const int16_t *actual)
{
	for (unsigned i = 0; i < LATE065_WORDS; ++i) {
		if (expected[i] == actual[i])
			continue;
		fprintf(stderr,
			"%s/%s trial=%u word=%u expected=%d actual=%d\n",
			profile, mode, trial, i, expected[i], actual[i]);
		exit(1);
	}
}

static void observe(const int16_t *x)
{
	for (unsigned i = 0; i < LATE065_WORDS; ++i) {
		const unsigned value = (unsigned)(x[i] < 0 ? -(int)x[i] : x[i]);
		if (value > max_output)
			max_output = value;
	}
}

static void run_distinct(const int16_t *a, const int16_t *b, unsigned trial)
{
	late065_scratch s0 __attribute__((aligned(64)));
	late065_scratch s1 __attribute__((aligned(64)));
	late065_scratch sl __attribute__((aligned(64)));
	int16_t out0[LATE065_WORDS] __attribute__((aligned(64)));
	int16_t out1[LATE065_WORDS] __attribute__((aligned(64)));
	int16_t outl[LATE065_WORDS] __attribute__((aligned(64)));

	late065_chain_c0(out0, a, b, &s0);
	late065_chain_c1(out1, a, b, &s1);
	late065_chain_l0(outl, a, b, &sl);
	exact("C1", "distinct", trial, out0, out1);
	exact("L0", "distinct", trial, out0, outl);
	observe(out0);
}

static void run_alias(const int16_t *a, const int16_t *b, unsigned trial,
	int alias_b)
{
	late065_scratch s0 __attribute__((aligned(64)));
	late065_scratch s1 __attribute__((aligned(64)));
	late065_scratch sl __attribute__((aligned(64)));
	int16_t a0[LATE065_WORDS] __attribute__((aligned(64)));
	int16_t b0[LATE065_WORDS] __attribute__((aligned(64)));
	int16_t a1[LATE065_WORDS] __attribute__((aligned(64)));
	int16_t b1[LATE065_WORDS] __attribute__((aligned(64)));
	int16_t al[LATE065_WORDS] __attribute__((aligned(64)));
	int16_t bl[LATE065_WORDS] __attribute__((aligned(64)));
	memcpy(a0, a, sizeof(a0)); memcpy(b0, b, sizeof(b0));
	memcpy(a1, a, sizeof(a1)); memcpy(b1, b, sizeof(b1));
	memcpy(al, a, sizeof(al)); memcpy(bl, b, sizeof(bl));
	int16_t *out0 = alias_b ? b0 : a0;
	int16_t *out1 = alias_b ? b1 : a1;
	int16_t *outl = alias_b ? bl : al;
	late065_chain_c0(out0, a0, b0, &s0);
	late065_chain_c1(out1, a1, b1, &s1);
	late065_chain_l0(outl, al, bl, &sl);
	exact("C1", alias_b ? "out_eq_b" : "out_eq_a", trial, out0, out1);
	exact("L0", alias_b ? "out_eq_b" : "out_eq_a", trial, out0, outl);
}

static void one_case(const int16_t *a, const int16_t *b, unsigned trial,
	int alias_check)
{
	run_distinct(a, b, trial);
	if (alias_check) {
		run_alias(a, b, trial, 0);
		run_alias(a, b, trial, 1);
	}
}

int main(void)
{
	int16_t a[LATE065_WORDS] __attribute__((aligned(64)));
	int16_t b[LATE065_WORDS] __attribute__((aligned(64)));
	unsigned trial = 0;
	unsigned alias_trials = 0;

	for (unsigned i = 0; i < LATE065_WORDS; ++i) {
		memset(a, 0, sizeof(a));
		memset(b, 0, sizeof(b));
		a[i] = 1;
		b[(i * 181U + 17U) % LATE065_WORDS] = -1;
		const int alias_check = i < 64U;
		one_case(a, b, trial++, alias_check);
		alias_trials += (unsigned)alias_check;
	}

	static const int16_t values[] = {-3, -2, -1, 0, 1, 2, 3, 4};
	for (unsigned k = 0; k < 8; ++k) {
		for (unsigned i = 0; i < LATE065_WORDS; ++i) {
			a[i] = values[(i + k) & 7U];
			b[i] = values[(5U * i + 3U * k) & 7U];
		}
		one_case(a, b, trial++, 1);
		++alias_trials;
	}

	for (unsigned n = 0; n < 1000; ++n) {
		for (unsigned i = 0; i < LATE065_WORDS; ++i) {
			a[i] = (int16_t)((int)(rng32() & 7U) - 3);
			b[i] = (int16_t)((int)(rng32() & 7U) - 3);
		}
		const int alias_check = n < 64U;
		one_case(a, b, trial++, alias_check);
		alias_trials += (unsigned)alias_check;
	}

	printf("Late-SoA full-chain correctness passed: trials=%u "
	       "alias_trials_per_mode=%u observed_abs_output=%u\n",
		trial, alias_trials, max_output);
	return 0;
}
