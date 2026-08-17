#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define WORDS 768
#define TRIALS 1000

void gt32_global_forward_core_asm(int16_t *, const int16_t *);
void gt32_global_inverse_core_asm(int16_t *, const int16_t *);
void gt32_tile4_forward_all_pair_asm(int16_t *, const int16_t *);
void gt32_tile4_attr_forward_all_bm_soa_asm(int16_t *, const int16_t *);
void gt32_tile4_inverse_soa_private_parallel_asm(int16_t *, const int16_t *);
void gt32_tile4_inverse_all_pair_asm(int16_t *, const int16_t *);
void gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm(
	int16_t *, const int16_t *, const int16_t *);
void gt32_tile4_basemul_scale_soa_soa_to_m_private_asm(
	int16_t *, const int16_t *, const int16_t *);

static uint32_t rng_state = 1;

static uint32_t rng32(void)
{
	rng_state = 1664525U * rng_state + 1013904223U;
	return rng_state;
}

static void private_soa_to_tile4(int16_t *out, const int16_t *in)
{
	static const uint8_t q_order[16] = {
		0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15
	};
	uint8_t position[16];

	for (unsigned lane = 0; lane < 16; lane++)
		position[q_order[lane]] = (uint8_t)lane;
	for (unsigned group = 0; group < 12; group++)
		for (unsigned q = 0; q < 16; q++)
			for (unsigned c = 0; c < 4; c++)
				out[64U * group + 4U * q + c] =
					in[64U * group + 16U * c + position[q]];
}

static void tile4_to_private_soa(int16_t *out, const int16_t *in)
{
	static const uint8_t q_order[16] = {
		0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15
	};
	uint8_t position[16];

	for (unsigned lane = 0; lane < 16; lane++)
		position[q_order[lane]] = (uint8_t)lane;
	for (unsigned group = 0; group < 12; group++)
		for (unsigned q = 0; q < 16; q++)
			for (unsigned c = 0; c < 4; c++)
				out[64U * group + 16U * c + position[q]] =
					in[64U * group + 4U * q + c];
}

static void compare(const char *name, unsigned trial, const int16_t *want,
	const int16_t *got)
{
	for (unsigned i = 0; i < WORDS; i++) {
		if (want[i] != got[i]) {
			fprintf(stderr,
				"%s trial=%u word=%u want=%d got=%d\n",
				name, trial, i, want[i], got[i]);
			exit(1);
		}
	}
}

int main(void)
{
	int16_t in[WORDS] __attribute__((aligned(32)));
	int16_t want[WORDS] __attribute__((aligned(32)));
	int16_t got[WORDS] __attribute__((aligned(32)));
	int16_t tmp[WORDS] __attribute__((aligned(32)));
	int16_t alias[WORDS] __attribute__((aligned(32)));
	int16_t in_b[WORDS] __attribute__((aligned(32)));
	int16_t f_a[WORDS] __attribute__((aligned(32)));
	int16_t f_b[WORDS] __attribute__((aligned(32)));
	int16_t product[WORDS] __attribute__((aligned(32)));

	for (unsigned trial = 0; trial < TRIALS; trial++) {
		for (unsigned i = 0; i < WORDS; i++)
			in[i] = (int16_t)((int)(rng32() % 3457U) - 1728);

		gt32_tile4_forward_all_pair_asm(tmp, in);
		tile4_to_private_soa(want, tmp);
		gt32_global_forward_core_asm(got, in);
		compare("forward", trial, want, got);
		gt32_tile4_attr_forward_all_bm_soa_asm(tmp, in);
		compare("forward-production-m", trial, tmp, got);

		memcpy(alias, in, sizeof(alias));
		gt32_global_forward_core_asm(alias, alias);
		compare("forward-alias", trial, want, alias);

		for (unsigned i = 0; i < WORDS; i++)
			in[i] = (int16_t)((int)(rng32() % 4719U) - 2359);

		gt32_tile4_inverse_soa_private_parallel_asm(tmp, in);
		private_soa_to_tile4(want, tmp);
		gt32_global_inverse_core_asm(got, in);
		compare("inverse", trial, want, got);

		memcpy(alias, in, sizeof(alias));
		gt32_global_inverse_core_asm(alias, alias);
		compare("inverse-alias", trial, want, alias);

		for (unsigned i = 0; i < WORDS; i++) {
			in[i] = (int16_t)((int)(rng32() % 3457U) - 1728);
			in_b[i] = (int16_t)((int)(rng32() % 3457U) - 1728);
		}
		gt32_tile4_attr_forward_all_bm_soa_asm(f_a, in);
		gt32_tile4_attr_forward_all_bm_soa_asm(f_b, in_b);
		gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm(
			product, f_a, f_b);
		gt32_tile4_inverse_all_pair_asm(want, product);

		gt32_global_forward_core_asm(f_a, in);
		gt32_global_forward_core_asm(f_b, in_b);
		gt32_tile4_basemul_scale_soa_soa_to_m_private_asm(
			product, f_a, f_b);
		gt32_global_inverse_core_asm(got, product);
		compare("whole-2F-B-I", trial, want, got);
	}

	puts("global physical core: 1000 trials + alias ok");
	return 0;
}
