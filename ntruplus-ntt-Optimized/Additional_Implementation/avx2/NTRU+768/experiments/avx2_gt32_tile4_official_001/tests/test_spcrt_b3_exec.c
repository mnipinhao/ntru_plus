#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "tile4.h"

#define Q 3457
#define WORDS 768
#define TRIALS 1000

void gt32_spcrt_forward_raw_asm(int16_t *, const int16_t *);
void gt32_spcrt_forward_a_repaired_asm(int16_t *, const int16_t *);
void gt32_spcrt_forward_a_repaired_r1_asm(int16_t *, const int16_t *);
void gt32_spcrt_forward_raw_r2_shared_asm(int16_t *, const int16_t *);
void gt32_spcrt_forward_a_repaired_r2_shared_asm(int16_t *, const int16_t *);
void gt32_spcrt_basemul_b3_asm(int16_t *, const int16_t *, const int16_t *);

static uint64_t rng_state = UINT64_C(0x243f6a8885a308d3);

static uint32_t rng32(void)
{
	rng_state ^= rng_state << 7;
	rng_state ^= rng_state >> 9;
	return (uint32_t)rng_state;
}

static int bitreverse5(int value)
{
	int result = 0;
	for (int bit = 0; bit < 5; bit++) {
		result = 2 * result + (value & 1);
		value >>= 1;
	}
	return result;
}

static int16_t centered_mod(int32_t value)
{
	value %= Q;
	if (value < 0)
		value += Q;
	if (value > Q / 2)
		value -= Q;
	return (int16_t)value;
}

static void standard_to_sp(int16_t sp[WORDS], const int16_t standard[WORDS])
{
	for (int branch = 0; branch < 2; branch++) {
		for (int row = 0; row < 3; row++) {
			const int current_k3 = 2 * row % 3;
			for (int p = 0; p < 32; p++) {
				const int j = bitreverse5(p);
				const int current_k32 = 11 * j % 32;
				const int current_q = bitreverse5(current_k32);
				const int source_vector =
					(current_k3 * 2 + branch) * 8 + current_q / 4;
				const int destination_vector =
					(branch * 3 + row) * 8 + p / 4;
				for (int degree = 0; degree < 4; degree++)
					sp[16 * destination_vector + 4 * (p % 4) + degree] =
						standard[16 * source_vector +
						4 * (current_q % 4) + degree];
			}
		}
	}
}

static int equal_mod_q(const int16_t a[WORDS], const int16_t b[WORDS])
{
	for (int i = 0; i < WORDS; i++)
		if (centered_mod(a[i]) != centered_mod(b[i]))
			return 0;
	return 1;
}

static void fill(int16_t output[WORDS], int trial)
{
	for (int i = 0; i < WORDS; i++) {
		if (trial == 0)
			output[i] = -3;
		else if (trial == 1)
			output[i] = 4;
		else if (trial == 2)
			output[i] = (i & 1) != 0 ? 4 : -3;
		else
			output[i] = (int16_t)((int)(rng32() & 7U) - 3);
	}
}

int main(void)
{
	_Alignas(64) int16_t input_a[WORDS], input_b[WORDS];
	_Alignas(64) int16_t standard_a[WORDS], standard_b[WORDS];
	_Alignas(64) int16_t expected_a[WORDS], expected_b[WORDS];
	_Alignas(64) int16_t sp_a[WORDS], sp_b[WORDS], sp_raw[WORDS];
	_Alignas(64) int16_t sp_r1[WORDS], sp_r2[WORDS];
	_Alignas(64) int16_t standard_product[WORDS], expected_product[WORDS];
	_Alignas(64) int16_t sp_product[WORDS], alias[WORDS];

	for (int trial = 0; trial < TRIALS; trial++) {
		fill(input_a, trial);
		fill(input_b, trial + 17);
		gt32_tile4_forward_full_wide_raw_pair_align64_asm(standard_a, input_a);
		gt32_tile4_forward_full_wide_raw_pair_align64_asm(standard_b, input_b);
		standard_to_sp(expected_a, standard_a);
		standard_to_sp(expected_b, standard_b);
		gt32_spcrt_forward_raw_asm(sp_raw, input_a);
		gt32_spcrt_forward_a_repaired_asm(sp_a, input_a);
		gt32_spcrt_forward_a_repaired_r1_asm(sp_r1, input_a);
		gt32_spcrt_forward_a_repaired_r2_shared_asm(sp_r2, input_a);
		gt32_spcrt_forward_raw_asm(sp_b, input_b);
		if (!equal_mod_q(sp_raw, expected_a) ||
			!equal_mod_q(sp_a, expected_a) ||
			memcmp(sp_a, sp_r1, sizeof sp_a) != 0 ||
			memcmp(sp_a, sp_r2, sizeof sp_a) != 0 ||
			!equal_mod_q(sp_b, expected_b)) {
			fprintf(stderr, "SP Forward mismatch at trial %d\n", trial);
			return 1;
		}
		gt32_tile4_basemul_b3_late_asm(
			standard_product, standard_a, standard_b);
		standard_to_sp(expected_product, standard_product);
		gt32_spcrt_basemul_b3_asm(sp_product, sp_a, sp_b);
		if (!equal_mod_q(sp_product, expected_product)) {
			fprintf(stderr, "SP B3 mismatch at trial %d\n", trial);
			return 1;
		}
		memcpy(alias, input_a, sizeof alias);
		gt32_spcrt_forward_a_repaired_asm(alias, alias);
		if (!equal_mod_q(alias, expected_a)) {
			fprintf(stderr, "SP Forward alias mismatch at trial %d\n", trial);
			return 1;
		}
	}
	puts("SPCRT/AUTO11 Forward + selective B3: 1000 trials passed");
	return 0;
}
