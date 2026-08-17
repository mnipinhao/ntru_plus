#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "tile4.h"
#include "../generated/tile4_frontend_constants.h"

#define Q 3457
#define OMEGA32 1784

static uint64_t rng_state = UINT64_C(0x8a5cd789635d2dff);

static int physical_k3(int slot, int qword);

static uint32_t rng32(void)
{
	rng_state ^= rng_state << 7;
	rng_state ^= rng_state >> 9;
	return (uint32_t)rng_state;
}

static int16_t centered_mod(int64_t value)
{
	value %= Q;
	if (value < 0)
		value += Q;
	if (value > Q / 2)
		value -= Q;
	return (int16_t)value;
}

static int normal_from_mont(int16_t value)
{
	return (int)centered_mod((int64_t)value * 2775);
}

static unsigned bitreverse(unsigned value, unsigned bits)
{
	unsigned result = 0;
	for (unsigned bit = 0; bit < bits; bit++) {
		result = (result << 1) | (value & 1U);
		value >>= 1;
	}
	return result;
}

static unsigned forward_power(unsigned stage, unsigned group)
{
	if (stage == 1U)
		return 0;
	return bitreverse(group >> (6U - stage), stage - 1U)
		<< (5U - stage);
}

static int pow_mod(int base, unsigned exponent)
{
	int result = 1;
	while (exponent != 0U) {
		if ((exponent & 1U) != 0U)
			result = (int)centered_mod((int64_t)result * base);
		base = (int)centered_mod((int64_t)base * base);
		exponent >>= 1;
	}
	return result;
}

static void ntt32_mod(int16_t values[32])
{
	for (unsigned stage = 1; stage <= 5; stage++) {
		const unsigned distance = 32U >> stage;
		for (unsigned group = 0; group < 32; group += 2U * distance) {
			const int factor = pow_mod(OMEGA32, forward_power(stage, group));
			for (unsigned lane = 0; lane < distance; lane++) {
				const unsigned low_index = group + lane;
				const unsigned high_index = low_index + distance;
				const int low = values[low_index];
				const int high = values[high_index];
				const int product = (int)centered_mod((int64_t)factor * high);
				values[low_index] = centered_mod((int64_t)low + product);
				values[high_index] = centered_mod((int64_t)low - product);
			}
		}
	}
}

static void n32_forward_half_ref(int16_t out[768], const int16_t in[768])
{
	int16_t rows[2][3][4][32];
	const int omega3 = normal_from_mont(-886);

	for (unsigned branch = 0; branch < 2; branch++) {
		for (unsigned n3 = 0; n3 < 3; n3++) {
			for (unsigned degree = 0; degree < 4; degree++) {
				for (unsigned q = 0; q < 32; q++) {
					const unsigned n = (64U * n3 + 33U * q) % 96U;
					const int low = in[4U * n + degree];
					const int high = in[384U + 4U * n + degree];
					const int split = branch == 0
						? low - 722 * high : low + 723 * high;
					const int twist = normal_from_mont(
						gt32_tile4_twist[branch][n]);
					rows[branch][n3][degree][q] = centered_mod(
						(int64_t)split * twist);
				}
				ntt32_mod(rows[branch][n3][degree]);
			}
		}
	}
	for (unsigned branch = 0; branch < 2; branch++) {
		for (unsigned group = 0; group < 8; group++) {
			for (unsigned qword = 0; qword < 4; qword++) {
				const unsigned q = 4U * group + qword;
				for (unsigned degree = 0; degree < 4; degree++) {
					const int x0 = rows[branch][0][degree][q];
					const int x1 = rows[branch][1][degree][q];
					const int x2 = rows[branch][2][degree][q];
					const int t = (int)centered_mod(
						(int64_t)omega3 * (x1 - x2));
					const int16_t logical[3] = {
						centered_mod((int64_t)x0 + x1 + x2),
						centered_mod((int64_t)x0 - x2 + t),
						centered_mod((int64_t)x0 - x1 - t),
					};
					for (int slot = 0; slot < 3; slot++) {
						const int k3 = physical_k3(slot, (int)qword);
						const int vector = ((int)branch * 8 + (int)group) * 3 + slot;
						out[16 * vector + 4 * (int)qword + (int)degree] =
							logical[k3];
					}
				}
			}
		}
	}
}

static int physical_k3(int slot, int qword)
{
	if (slot == 0) {
		return 0;
	}
	if (slot == 1) {
		return qword < 2 ? 1 : 2;
	}
	return qword < 2 ? 2 : 1;
}

static void standard_to_half(int16_t half[768], const int16_t standard[768])
{
	for (int branch = 0; branch < 2; branch++) {
		for (int group = 0; group < 8; group++) {
			for (int slot = 0; slot < 3; slot++) {
				const int half_vector = (branch * 8 + group) * 3 + slot;
				for (int qword = 0; qword < 4; qword++) {
					const int k3 = physical_k3(slot, qword);
					/* generate_tile4.py emits tiles in (k3, branch) order. */
					const int standard_vector = (k3 * 2 + branch) * 8 + group;
					for (int degree = 0; degree < 4; degree++) {
						half[16 * half_vector + 4 * qword + degree] =
							standard[16 * standard_vector + 4 * qword + degree];
					}
				}
			}
		}
	}
}

static void half_to_standard(int16_t standard[768], const int16_t half[768])
{
	for (int branch = 0; branch < 2; branch++) {
		for (int group = 0; group < 8; group++) {
			for (int slot = 0; slot < 3; slot++) {
				const int half_vector = (branch * 8 + group) * 3 + slot;
				for (int qword = 0; qword < 4; qword++) {
					const int k3 = physical_k3(slot, qword);
					/* generate_tile4.py emits tiles in (k3, branch) order. */
					const int standard_vector = (k3 * 2 + branch) * 8 + group;
					for (int degree = 0; degree < 4; degree++) {
						standard[16 * standard_vector + 4 * qword + degree] =
							half[16 * half_vector + 4 * qword + degree];
					}
				}
			}
		}
	}
}

static int equal_words(const int16_t a[768], const int16_t b[768])
{
	return memcmp(a, b, 768 * sizeof(int16_t)) == 0;
}

static int equal_mod_q(const int16_t a[768], const int16_t b[768])
{
	for (int index = 0; index < 768; index++)
		if (centered_mod(a[index]) != centered_mod(b[index]))
			return 0;
	return 1;
}

static int check_forward_semantics(void)
{
	_Alignas(32) int16_t input[768], standard[768], standard_h[768], n32[768];
	for (int trial = 0; trial < 64; trial++) {
		for (int index = 0; index < 768; index++)
			input[index] = (int16_t)((int)(rng32() & 7U) - 3);
		gt32_tile4_forward_full_wide_raw_pair_align64_asm(standard, input);
		standard_to_half(standard_h, standard);
		n32_forward_half_ref(n32, input);
		if (!equal_mod_q(standard_h, n32)) {
			fprintf(stderr, "N32-forward semantic mismatch at trial %d\n", trial);
			return 0;
		}
	}
	return 1;
}

int main(void)
{
	_Alignas(32) int16_t a[768], b[768], ah[768], bh[768];
	_Alignas(32) int16_t expected[768], candidate_h[768], candidate[768];
	_Alignas(32) int16_t alias[768];

	if (!check_forward_semantics())
		return 1;
	for (int trial = 0; trial < 1000; trial++) {
		for (int index = 0; index < 768; index++) {
			a[index] = (int16_t)((int32_t)(rng32() % 2001U) - 1000);
			b[index] = (int16_t)((int32_t)(rng32() % 2001U) - 1000);
		}
		standard_to_half(ah, a);
		standard_to_half(bh, b);
		gt32_tile4_basemul_scale_ff_aos_r1u_asm(expected, a, b);
		gt32_n32_basemul_half_r1u_asm(candidate_h, ah, bh);
		half_to_standard(candidate, candidate_h);
		if (!equal_words(expected, candidate)) {
			fprintf(stderr, "half-native BM mismatch at trial %d\n", trial);
			return 1;
		}

		memcpy(alias, ah, sizeof(alias));
		gt32_n32_basemul_half_r1u_asm(alias, alias, bh);
		if (!equal_words(alias, candidate_h)) {
			fprintf(stderr, "out==a alias mismatch at trial %d\n", trial);
			return 1;
		}
		memcpy(alias, bh, sizeof(alias));
		gt32_n32_basemul_half_r1u_asm(alias, ah, alias);
		if (!equal_words(alias, candidate_h)) {
			fprintf(stderr, "out==b alias mismatch at trial %d\n", trial);
			return 1;
		}
	}
	puts("n32-half-native-bm: forward-semantic=passed mapping=passed "
		"r1u=passed alias=passed forward-trials=64 bm-trials=1000");
	return 0;
}
