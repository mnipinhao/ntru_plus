#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "tile4.h"

void ntt_gt_rowbitrevlayout(int16_t r[GT32_TILE4_POLY_WORDS],
	const int16_t a[GT32_TILE4_POLY_WORDS]);

static uint64_t rng_state = UINT64_C(0x6a09e667f3bcc909);

static uint32_t random32(void)
{
	rng_state ^= rng_state << 13;
	rng_state ^= rng_state >> 7;
	rng_state ^= rng_state << 17;
	return (uint32_t)rng_state;
}

static int16_t centered(int32_t value)
{
	value %= GT32_TILE4_Q;
	if (value < 0)
		value += GT32_TILE4_Q;
	if (value > GT32_TILE4_Q / 2)
		value -= GT32_TILE4_Q;
	return (int16_t)value;
}

static void fail_at(const char *name, unsigned trial, size_t index,
	int16_t expected, int16_t actual)
{
	fprintf(stderr, "%s trial=%u index=%zu expected=%d actual=%d\n",
		name, trial, index, expected, actual);
	exit(1);
}

static void compare_exact(const char *name, unsigned trial,
	const int16_t *expected, const int16_t *actual, size_t words)
{
	for (size_t i = 0; i < words; i++) {
		if (expected[i] != actual[i])
			fail_at(name, trial, i, expected[i], actual[i]);
	}
}

static void compare_mod_q(const char *name, unsigned trial,
	const int16_t *expected, const int16_t *actual, size_t words)
{
	for (size_t i = 0; i < words; i++) {
		if (centered(expected[i]) != centered(actual[i]))
			fail_at(name, trial, i, centered(expected[i]), centered(actual[i]));
	}
}

static void compare_roundtrip(const int16_t *input, const int16_t *actual,
	size_t words, unsigned trial)
{
	for (size_t i = 0; i < words; i++) {
		const int16_t expected = centered(32 * (int32_t)input[i]);
		if (centered(actual[i]) != expected)
			fail_at("roundtrip-mod-q", trial, i, expected, centered(actual[i]));
	}
}

static void compare_parent_rowbitrev(const int16_t *input,
	const int16_t *tile4, unsigned trial)
{
	int16_t parent[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));

	ntt_gt_rowbitrevlayout(parent, input);
	for (unsigned k3 = 0; k3 < 3; k3++) {
		for (unsigned branch = 0; branch < 2; branch++) {
			const unsigned tile = 2U * k3 + branch;
			for (unsigned q = 0; q < 32; q++) {
				const unsigned block = (32U * k3 + 3U * q) % 96U;
				for (unsigned coefficient = 0; coefficient < 4; coefficient++) {
					const size_t tile_word = 128U * tile + 16U * (q / 4U)
						+ 4U * (q % 4U) + coefficient;
					const size_t parent_word = 384U * branch + 4U * block
						+ coefficient;
					const int16_t expected = centered(parent[parent_word]);
					const int16_t actual = centered(tile4[tile_word]);
					if (expected != actual)
						fail_at("frozen-parent", trial, tile_word,
							expected, actual);
				}
			}
		}
	}
}

static void fill_case(int16_t *value, size_t words, unsigned trial)
{
	for (size_t i = 0; i < words; i++) {
		switch (trial) {
		case 0: value[i] = 0; break;
		case 1: value[i] = (i == 0U) ? 1 : 0; break;
		case 2: value[i] = (i & 1U) ? -1728 : 1728; break;
		case 3: value[i] = (int16_t)((int)(i % 8U) - 3); break;
		default: value[i] = (int16_t)((int)(random32() % 3457U) - 1728); break;
		}
	}
}

int main(void)
{
	int16_t input[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t ref[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t got[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t inverse_ref[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t inverse_got[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t alias[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t frontend_ref[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t frontend_got[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t frontend_asm[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t full_ref[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t full_got[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t serial_got[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));

	for (unsigned trial = 0; trial < 1000; trial++) {
		fill_case(input, GT32_TILE4_POLY_WORDS, trial);
		gt32_tile4_frontend_ref(frontend_ref, input);
		gt32_tile4_frontend_intrinsic(frontend_got, input);
		compare_exact("frontend", trial, frontend_ref, frontend_got,
			GT32_TILE4_POLY_WORDS);
		gt32_tile4_frontend_asm(frontend_asm, input);
		compare_exact("frontend-asm", trial, frontend_ref, frontend_asm,
			GT32_TILE4_POLY_WORDS);
		if (trial == 3U) {
			gt32_tile4_frontend_raw_asm(frontend_asm, input);
			compare_mod_q("frontend-raw", trial, frontend_ref, frontend_asm,
				GT32_TILE4_POLY_WORDS);
			gt32_tile4_frontend_fixed_raw_asm(frontend_got, input);
			compare_exact("frontend-fixed-vs-raw", trial, frontend_asm,
				frontend_got, GT32_TILE4_POLY_WORDS);
			gt32_tile4_frontend_wide_raw_asm(got, input);
			compare_exact("frontend-wide-vs-fixed", trial, frontend_got, got,
				GT32_TILE4_POLY_WORDS);
			gt32_tile4_forward_all_pair_asm(serial_got, frontend_got);
			gt32_tile4_forward_full_fixed_pair_asm(full_got, input);
			compare_exact("full-fixed-pair", trial, serial_got, full_got,
				GT32_TILE4_POLY_WORDS);
			gt32_tile4_forward_full_fixed_pair_wide_load_asm(full_got, input);
			compare_exact("full-fixed-pair-wide", trial, serial_got, full_got,
				GT32_TILE4_POLY_WORDS);
			gt32_tile4_forward_full_wide_raw_pair_asm(full_got, input);
			compare_exact("full-wide-raw-pair", trial, serial_got, full_got,
				GT32_TILE4_POLY_WORDS);
			gt32_tile4_forward_full_wide_raw_pair_align32_asm(full_got, input);
			compare_exact("full-wide-raw-pair-align32", trial, serial_got,
				full_got, GT32_TILE4_POLY_WORDS);
			gt32_tile4_forward_full_wide_raw_pair_align64_asm(full_got, input);
			compare_exact("full-wide-raw-pair-align64", trial, serial_got,
				full_got, GT32_TILE4_POLY_WORDS);
			memcpy(alias, input, sizeof(alias));
			gt32_tile4_forward_full_fixed_pair_asm(alias, alias);
			compare_exact("full-fixed-pair-alias", trial, serial_got, alias,
				GT32_TILE4_POLY_WORDS);
		}

		gt32_tile4_forward_full_ref(full_ref, input);
		gt32_tile4_forward_full_candidate(full_got, input);
		compare_exact("full-forward", trial, full_ref, full_got,
			GT32_TILE4_POLY_WORDS);
		compare_parent_rowbitrev(input, full_got, trial);
		memcpy(alias, input, sizeof(alias));
		gt32_tile4_forward_full_candidate(alias, alias);
		compare_exact("full-forward-alias", trial, full_ref, alias,
			GT32_TILE4_POLY_WORDS);

		gt32_tile4_forward_all_ref(ref, input);
		gt32_tile4_forward_all_asm(got, input);
		compare_exact("forward", trial, ref, got, GT32_TILE4_POLY_WORDS);
		gt32_tile4_forward_all_parallel_asm(serial_got, input);
		compare_exact("forward-parallel", trial, ref, serial_got,
			GT32_TILE4_POLY_WORDS);
		gt32_tile4_forward_all_pair_asm(serial_got, input);
		compare_exact("forward-pair", trial, ref, serial_got,
			GT32_TILE4_POLY_WORDS);

		gt32_tile4_inverse_all_ref(inverse_ref, ref);
		gt32_tile4_inverse_all_asm(inverse_got, got);
		compare_exact("inverse", trial, inverse_ref, inverse_got,
			GT32_TILE4_POLY_WORDS);
		compare_roundtrip(input, inverse_got, GT32_TILE4_POLY_WORDS, trial);

		memcpy(alias, input, sizeof(alias));
		gt32_tile4_forward_all_asm(alias, alias);
		compare_exact("forward-alias", trial, ref, alias,
			GT32_TILE4_POLY_WORDS);
		gt32_tile4_inverse_all_asm(alias, alias);
		compare_exact("inverse-alias", trial, inverse_ref, alias,
			GT32_TILE4_POLY_WORDS);
	}

	puts("gt32-tile4: mapping=passed frontend=passed frozen-parent=passed full-forward=passed forward=passed inverse=passed alias=passed roundtrip=passed trials=1000");
	return 0;
}
