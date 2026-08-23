#include "producer.h"

#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static uint64_t state = UINT64_C(0x0620d1f3a5c79e11);
static unsigned max_post_s1;

static uint32_t rng32(void)
{
	state ^= state << 7;
	state ^= state >> 9;
	state ^= state << 8;
	return (uint32_t)state;
}

static void exact(const char *label, unsigned trial, const int16_t *want,
	const int16_t *got)
{
	for (unsigned i = 0; i < PRODUCER062_TILE_WORDS; ++i)
		if (want[i] != got[i]) {
			fprintf(stderr, "%s trial=%u word=%u want=%d got=%d\n",
				label, trial, i, want[i], got[i]);
			exit(1);
		}
}

static void tile4_s1(int16_t out[PRODUCER062_TILE_WORDS],
	const int16_t in[PRODUCER062_TILE_WORDS])
{
	for (unsigned vector = 0; vector < 4; ++vector)
		for (unsigned lane = 0; lane < 16; ++lane) {
			const unsigned lo = 16U * vector + lane;
			const unsigned hi = lo + 64U;
			out[lo] = (int16_t)(in[lo] + in[hi]);
			out[hi] = (int16_t)(in[lo] - in[hi]);
		}
}

static void one_case(const int16_t input[PRODUCER062_N], unsigned trial)
{
	int16_t full[PRODUCER062_N] __attribute__((aligned(32)));
	int16_t want_tile[PRODUCER062_TILE_WORDS] __attribute__((aligned(32)));
	int16_t want_hwa[PRODUCER062_TILE_WORDS] __attribute__((aligned(32)));
	int16_t p0[PRODUCER062_TILE_WORDS] __attribute__((aligned(32)));
	int16_t p1[PRODUCER062_TILE_WORDS] __attribute__((aligned(32)));
	int16_t p2[PRODUCER062_TILE_WORDS] __attribute__((aligned(32)));
	int16_t roundtrip[PRODUCER062_TILE_WORDS] __attribute__((aligned(32)));

	gt32_tile4_frontend_wide_raw_f14_asm(full, input);
	tile4_s1(want_tile, full); /* Tile 0 starts at word zero. */
	hwa16_from_tile4(want_hwa, want_tile);
	hwa16_to_tile4(roundtrip, want_hwa);
	exact("mapping-roundtrip", trial, want_tile, roundtrip);
	producer062_p0_tile4_post_s1_asm(p0, input);
	producer062_p1_hwa_explicit_post_s1_asm(p1, input);
	producer062_p2_hwa_fused_post_s1_asm(p2, input);
	exact("P0", trial, want_tile, p0);
	exact("P1", trial, want_hwa, p1);
	exact("P2", trial, want_hwa, p2);
	for (unsigned i = 0; i < PRODUCER062_TILE_WORDS; ++i) {
		const unsigned a = (unsigned)(p0[i] < 0 ? -(int)p0[i] : p0[i]);
		if (a > max_post_s1) max_post_s1 = a;
	}
}

static void structured(int16_t input[PRODUCER062_N], unsigned kind)
{
	static const int16_t values[] = {0, 1, -1, 1728, -1728, 17, -31, 511};
	for (unsigned i = 0; i < PRODUCER062_N; ++i)
		input[i] = values[(5U * i + kind) %
			(sizeof(values) / sizeof(values[0]))];
}

int main(void)
{
	int16_t input[PRODUCER062_N] __attribute__((aligned(32)));
	unsigned trial = 0;
	for (unsigned i = 0; i < PRODUCER062_N; ++i) {
		memset(input, 0, sizeof(input));
		input[i] = 1;
		one_case(input, trial++);
	}
	for (unsigned kind = 0; kind < 8; ++kind) {
		structured(input, kind);
		one_case(input, trial++);
	}
	for (unsigned n = 0; n < 1000; ++n) {
		for (unsigned i = 0; i < PRODUCER062_N; ++i)
			input[i] = (int16_t)((int)(rng32() % 3457U) - 1728);
		one_case(input, trial++);
	}
	printf("producer062 correctness passed: trials=%u impulses=768 "
	       "observed_post_s1_abs=%u aliases=disallowed\n", trial, max_post_s1);
	return 0;
}
