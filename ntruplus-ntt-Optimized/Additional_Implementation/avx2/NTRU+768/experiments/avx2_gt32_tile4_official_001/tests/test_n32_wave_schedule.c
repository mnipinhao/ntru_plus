#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "tile4.h"

#define WORDS 256
#define TRIALS 1000

static uint64_t rng_state = UINT64_C(0x6a09e667f3bcc909);

static uint32_t rng32(void)
{
	rng_state ^= rng_state << 7;
	rng_state ^= rng_state >> 9;
	return (uint32_t)rng_state;
}

static void fill_input(int16_t out[WORDS])
{
	for (int index = 0; index < WORDS; index++)
		out[index] = (int16_t)((int32_t)(rng32() % 3599U) - 1799);
}

static int check_equal(const int16_t expected[WORDS],
	const int16_t actual[WORDS], int trial, const char *kind)
{
	for (int index = 0; index < WORDS; index++) {
		if (expected[index] != actual[index]) {
			fprintf(stderr,
				"%s mismatch at trial %d word %d: %d != %d\n",
				kind, trial, index, actual[index], expected[index]);
			return 0;
		}
	}
	return 1;
}

int main(void)
{
	_Alignas(32) int16_t input[WORDS];
	_Alignas(32) int16_t expected[WORDS];
	_Alignas(32) int16_t candidate[WORDS];
	_Alignas(32) int16_t alias[WORDS];
	_Alignas(32) int16_t route_input[GT32_TILE4_POLY_WORDS];
	_Alignas(32) int16_t route_control[GT32_TILE4_POLY_WORDS];
	_Alignas(32) int16_t route_half[GT32_TILE4_POLY_WORDS];

	for (int trial = 0; trial < TRIALS; trial++) {
		fill_input(input);
		gt32_n32_wave_s1s3_control_asm(expected, input);
		gt32_n32_wave_s1s3_c2_asm(candidate, input);
		if (!check_equal(expected, candidate, trial, "separate"))
			return 1;

		memcpy(alias, input, sizeof(alias));
		gt32_n32_wave_s1s3_control_asm(alias, alias);
		if (!check_equal(expected, alias, trial, "control-alias"))
			return 1;

		memcpy(alias, input, sizeof(alias));
		gt32_n32_wave_s1s3_c2_asm(alias, alias);
		if (!check_equal(expected, alias, trial, "candidate-alias"))
			return 1;
	}
	for (int trial = 0; trial < TRIALS; trial++) {
		for (int index = 0; index < GT32_TILE4_POLY_WORDS; index++)
			route_input[index] = (int16_t)rng32();
		gt32_n32_suffix_route6_control_asm(route_control, route_input);
		gt32_n32_suffix_route5_half_asm(route_half, route_input);
		for (int component = 0; component < 16; component++) {
			const int base = 48 * component;
			for (int lane = 0; lane < 16; lane++) {
				const int control_vector = lane < 8 ? 1 : 2;
				const int opposite_vector = lane < 8 ? 2 : 1;
				if (route_half[base + lane] != route_control[base + lane] ||
					route_half[base + 16 + lane] !=
						route_control[base + 16 * control_vector + lane] ||
					route_half[base + 32 + lane] !=
						route_control[base + 16 * opposite_vector + lane]) {
					fprintf(stderr,
						"suffix route mismatch trial=%d component=%d lane=%d\n",
						trial, component, lane);
					return 1;
				}
			}
		}
	}
	puts("n32-wave-s1s3: exact=passed alias=passed trials=1000 "
		"suffix-route=passed");
	return 0;
}
