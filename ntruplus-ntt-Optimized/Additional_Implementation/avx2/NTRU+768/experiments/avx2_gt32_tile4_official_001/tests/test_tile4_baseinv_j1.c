#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "poly.h"
#include "tile4.h"
#include "../generated/tile4_serialized_mapping.h"

#define Q GT32_TILE4_Q
#define R 3310

static uint32_t next_u32(uint32_t *state)
{
	*state = *state * 1664525U + 1013904223U;
	return *state;
}

static int16_t centered(int32_t value)
{
	value %= Q;
	if (value < 0)
		value += Q;
	if (value > Q / 2)
		value -= Q;
	return (int16_t)value;
}

static unsigned official_word(unsigned serialized)
{
	return 128U * (serialized / 128U) + (serialized % 128U) / 8U
		+ 16U * (serialized % 8U);
}

static void official_to_aos(int16_t *aos, const poly *official)
{
	for (unsigned serialized = 0; serialized < GT32_TILE4_POLY_WORDS;
		serialized++)
		aos[gt32_tile4_serialized_to_aos[serialized]] =
			official->coeffs[official_word(serialized)];
}

static int check_case(const poly *ntt_input, unsigned trial)
{
	poly official_inverse;
	gt32_f0_aos_e0_t f0;
	gt32_baseinv_j1_aos_e1_t j1;
	gt32_baseinv_j1_aos_e1_t native;
	gt32_baseinv_j1_aos_e1_t alias;
	int16_t official_aos[GT32_TILE4_POLY_WORDS];
	const int official_failure = poly_baseinv(&official_inverse, ntt_input);

	official_to_aos(f0.words, ntt_input);
	const int candidate_failure = gt32_tile4_baseinv_j1_aos_ref(&j1, &f0);
	const int native_failure = gt32_tile4_baseinv_j1_aos_avx2(&native, &f0);
	if (candidate_failure != official_failure) {
		fprintf(stderr, "failure mismatch at trial %u\n", trial);
		return 0;
	}
	if (native_failure != candidate_failure
		|| memcmp(native.words, j1.words, sizeof native.words) != 0) {
		unsigned lane = 0;
		while (lane < GT32_TILE4_POLY_WORDS
			&& native.words[lane] == j1.words[lane])
			lane++;
		fprintf(stderr,
			"native mismatch trial=%u failure=%d/%d lane=%u got=%d expected=%d\n",
			trial, native_failure, candidate_failure, lane,
			lane < GT32_TILE4_POLY_WORDS ? native.words[lane] : 0,
			lane < GT32_TILE4_POLY_WORDS ? j1.words[lane] : 0);
		return 0;
	}
	if (official_failure == 0) {
		official_to_aos(official_aos, &official_inverse);
		for (unsigned lane = 0; lane < GT32_TILE4_POLY_WORDS; lane++) {
			const int16_t expected = centered((int32_t)official_aos[lane] * R);
			if (j1.words[lane] != expected) {
				fprintf(stderr,
					"J1 mismatch trial=%u lane=%u got=%d expected=%d\n",
					trial, lane, j1.words[lane], expected);
				return 0;
			}
		}
	} else {
		for (unsigned lane = 0; lane < GT32_TILE4_POLY_WORDS; lane++)
			if (j1.words[lane] != 0)
				return 0;
	}

	memcpy(alias.words, f0.words, sizeof alias.words);
	if (gt32_tile4_baseinv_j1_aos_ref(&alias,
		(const gt32_f0_aos_e0_t *)(const void *)&alias) != official_failure
		|| memcmp(alias.words, j1.words, sizeof alias.words) != 0) {
		fprintf(stderr, "alias mismatch at trial %u\n", trial);
		return 0;
	}
	memcpy(alias.words, f0.words, sizeof alias.words);
	if (gt32_tile4_baseinv_j1_aos_avx2(&alias,
		(const gt32_f0_aos_e0_t *)(const void *)&alias) != official_failure
		|| memcmp(alias.words, j1.words, sizeof alias.words) != 0) {
		fprintf(stderr, "native alias mismatch at trial %u\n", trial);
		return 0;
	}
	return 1;
}

int main(void)
{
	uint32_t state = 0x4a314b33U;
	poly input;

	memset(&input, 0, sizeof input);
	poly_ntt(&input);
	if (!check_case(&input, 0))
		return 1;

	for (unsigned trial = 1; trial <= 1000; trial++) {
		for (unsigned lane = 0; lane < GT32_TILE4_POLY_WORDS; lane++)
			input.coeffs[lane] = (int16_t)((int32_t)(next_u32(&state) % 7U)
				- 3);
		input.coeffs[0]++;
		poly_ntt(&input);
		if (!check_case(&input, trial))
			return 1;
	}
	puts("K3-A BaseInv J1 typed differential: pass (1000 trials + zero + alias)");
	return 0;
}
