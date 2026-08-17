#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "poly.h"
#include "tile4.h"

#define WORDS GT32_TILE4_POLY_WORDS

static uint32_t next_u32(uint32_t *state)
{
	*state = *state * 1664525U + 1013904223U;
	return *state;
}

int main(int argc, char **argv)
{
	const unsigned trials = argc > 1 ? (unsigned)strtoul(argv[1], NULL, 10)
		: 10000U;
	int16_t input[WORDS] __attribute__((aligned(64)));
	int16_t frontend[WORDS] __attribute__((aligned(64)));
	int16_t output[WORDS] __attribute__((aligned(64)));
	uint8_t cbd[WORDS / 4];
	uint32_t state = 1U;
	unsigned maximum = 0;
	unsigned first_over_q_trial = 0;
	unsigned first_over_q_lane = 0;
	int first_over_q_value = 0;

	for (unsigned trial = 1; trial <= trials; trial++) {
		for (unsigned byte = 0; byte < sizeof cbd; byte++)
			cbd[byte] = (uint8_t)(next_u32(&state) >> 24);
		poly_cbd1((poly *)(void *)input, cbd);
		gt32_tile4_frontend_wide_raw_asm(frontend, input);
		gt32_tile4_attr_forward_all_bm_soa_asm(output, frontend);
		for (unsigned lane = 0; lane < WORDS; lane++) {
			const int value = output[lane];
			const unsigned absolute = (unsigned)(value < 0 ? -value : value);
			if (absolute > maximum)
				maximum = absolute;
			if (absolute >= 3457U && first_over_q_trial == 0U) {
				first_over_q_trial = trial;
				first_over_q_lane = lane;
				first_over_q_value = value;
			}
		}
	}
	printf("trials=%u max_abs=%u first_over_q_trial=%u lane=%u value=%d\n",
		trials, maximum, first_over_q_trial, first_over_q_lane,
		first_over_q_value);
	return first_over_q_trial == 0U;
}
