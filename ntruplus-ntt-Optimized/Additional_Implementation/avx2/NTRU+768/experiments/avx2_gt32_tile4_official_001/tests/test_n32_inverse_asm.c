#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "tile4.h"
#include "../generated/tile4_n32_inverse_test_ranges.h"

#define Q 3457
#define QINV 12929
#define OMEGA32 1784
#define WORDS 768
#define TRIALS 1000
#define GUARD_WORDS 16

static uint64_t rng_state = UINT64_C(0xd1b54a32d192ed03);

static uint32_t rng32(void)
{
	rng_state ^= rng_state << 7;
	rng_state ^= rng_state >> 9;
	return (uint32_t)rng_state;
}

static int32_t floor_shift(int32_t value, unsigned bits)
{
	const int32_t divisor = (int32_t)(UINT32_C(1) << bits);
	if (value >= 0)
		return value / divisor;
	return -((-value + divisor - 1) / divisor);
}

static int16_t signed16(uint32_t value)
{
	value &= UINT32_C(0xffff);
	return value >= UINT32_C(0x8000)
		? (int16_t)((int32_t)value - 65536) : (int16_t)value;
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

static int pow_mod(int base, unsigned exponent)
{
	int result = 1;
	while (exponent != 0U) {
		if ((exponent & 1U) != 0U)
			result = (int)centered(result * base);
		base = (int)centered(base * base);
		exponent >>= 1;
	}
	return result;
}

static int16_t mont_factor(unsigned length, unsigned offset)
{
	const unsigned power = (32U -
		(offset * (32U / length)) % 32U) % 32U;
	const int root = pow_mod(OMEGA32, power);
	const int r = (int)((UINT32_C(1) << 16) % Q);
	return centered(root * r);
}

static int16_t montgomery_fixed(int16_t value, int16_t factor)
{
	const int16_t qinv = signed16(
		(uint32_t)(uint16_t)factor * (uint32_t)QINV);
	const int16_t low = signed16(
		(uint32_t)(uint16_t)value * (uint32_t)(uint16_t)qinv);
	const int32_t high_factor = floor_shift((int32_t)value * factor, 16);
	const int32_t high_q = floor_shift((int32_t)low * Q, 16);
	return (int16_t)(high_factor - high_q);
}

static int16_t center10(int16_t value)
{
	const int32_t quotient = floor_shift((int32_t)value * 10 + 16384, 15);
	return (int16_t)((int32_t)value - quotient * Q);
}

static int physical_row(unsigned slot, unsigned q)
{
	if (slot == 0U)
		return 0;
	if (q % 4U < 2U)
		return (int)slot;
	return slot == 1U ? 2 : 1;
}

static int input_index(unsigned branch, unsigned group, unsigned slot,
	unsigned qword, unsigned degree)
{
	const unsigned vector = (branch * 8U + group) * 3U + slot;
	return (int)(16U * vector + 4U * qword + degree);
}

static int output_index(unsigned branch, unsigned group, unsigned slot,
	unsigned qword, unsigned degree)
{
	const unsigned vector = (branch * 3U + slot) * 8U + group;
	return (int)(16U * vector + 4U * qword + degree);
}

static int abs_i16(int16_t value)
{
	return value < 0 ? -(int)value : (int)value;
}

struct observed_bounds {
	int idft_internal;
	int idft_output;
	int stage[5];
};

static void reference_inverse(int16_t out[WORDS], const int16_t in[WORDS],
	struct observed_bounds *observed)
{
	int16_t rows[2][3][4][32];
	static const unsigned lengths[5] = {2, 4, 8, 16, 32};

	memset(rows, 0, sizeof(rows));
	for (unsigned branch = 0; branch < 2; branch++) {
		for (unsigned group = 0; group < 8; group++) {
			for (unsigned qword = 0; qword < 4; qword++) {
				const unsigned q = 4U * group + qword;
				for (unsigned slot = 0; slot < 3; slot++) {
					const int row = physical_row(slot, q);
					for (unsigned degree = 0; degree < 4; degree++)
						rows[branch][row][degree][q] = in[input_index(
							branch, group, slot, qword, degree)];
				}
			}
		}
	}

	for (unsigned branch = 0; branch < 2; branch++) {
		for (unsigned degree = 0; degree < 4; degree++) {
			for (unsigned q = 0; q < 32; q++) {
				const int16_t r0 = rows[branch][0][degree][q];
				const int16_t r1 = rows[branch][1][degree][q];
				const int16_t r2 = rows[branch][2][degree][q];
				const int16_t sum = (int16_t)((int32_t)r1 + r2);
				const int16_t difference = (int16_t)((int32_t)r1 - r2);
				const int16_t product = montgomery_fixed(difference, -886);
				const int internal[] = {
					abs_i16(sum), abs_i16(difference),
					abs_i16((int16_t)((int32_t)r0 - r1)),
					abs_i16((int16_t)((int32_t)r0 - r2)),
				};
				for (unsigned item = 0; item < 4; item++)
					if (internal[item] > observed->idft_internal)
						observed->idft_internal = internal[item];
				rows[branch][0][degree][q] = (int16_t)(
					(int32_t)r0 + center10(sum));
				rows[branch][1][degree][q] = (int16_t)(
					(int32_t)r0 - r1 - product);
				rows[branch][2][degree][q] = (int16_t)(
					(int32_t)r0 - r2 + product);
				for (unsigned row = 0; row < 3; row++) {
					const int value = abs_i16(rows[branch][row][degree][q]);
					if (value > observed->idft_output)
						observed->idft_output = value;
				}
			}
		}
	}

	for (unsigned stage = 0; stage < 5; stage++) {
		const unsigned length = lengths[stage];
		for (unsigned branch = 0; branch < 2; branch++) {
			for (unsigned row = 0; row < 3; row++) {
				for (unsigned degree = 0; degree < 4; degree++) {
					for (unsigned base = 0; base < 32; base += length) {
						for (unsigned offset = 0; offset < length / 2U; offset++) {
							const unsigned low_q = base + offset;
							const unsigned high_q = low_q + length / 2U;
							const int16_t low = rows[branch][row][degree][low_q];
							const int16_t high = rows[branch][row][degree][high_q];
							const int16_t product = length == 2U ? high
								: montgomery_fixed(high, mont_factor(length, offset));
							rows[branch][row][degree][low_q] = (int16_t)(
								(int32_t)low + product);
							rows[branch][row][degree][high_q] = (int16_t)(
								(int32_t)low - product);
							const int a = abs_i16(rows[branch][row][degree][low_q]);
							const int b = abs_i16(rows[branch][row][degree][high_q]);
							if (a > observed->stage[stage])
								observed->stage[stage] = a;
							if (b > observed->stage[stage])
								observed->stage[stage] = b;
						}
					}
				}
			}
		}
	}

	for (unsigned branch = 0; branch < 2; branch++) {
		for (unsigned group = 0; group < 8; group++) {
			for (unsigned qword = 0; qword < 4; qword++) {
				const unsigned q = 4U * group + qword;
				for (unsigned slot = 0; slot < 3; slot++) {
					const int row = physical_row(slot, q);
					for (unsigned degree = 0; degree < 4; degree++)
						out[output_index(branch, group, slot,
							qword, degree)] = rows[branch][row][degree][q];
				}
			}
		}
	}
}

static void fill_input(int16_t out[WORDS], int trial)
{
	for (int index = 0; index < WORDS; index++) {
		const int low = gt32_n32_r1u_min[index];
		const int high = gt32_n32_r1u_max[index];
		if (trial == 0)
			out[index] = (int16_t)low;
		else if (trial == 1)
			out[index] = (int16_t)high;
		else if (trial == 2)
			out[index] = (index & 1) != 0 ? (int16_t)high : (int16_t)low;
		else if (trial == 3)
			out[index] = 0;
		else
			out[index] = (int16_t)(low + (int)(rng32() %
				(uint32_t)(high - low + 1)));
	}
}

static int equal_words(const int16_t expected[WORDS],
	const int16_t actual[WORDS], int trial, const char *name)
{
	for (int index = 0; index < WORDS; index++) {
		if (expected[index] != actual[index]) {
			fprintf(stderr, "%s mismatch trial=%d word=%d actual=%d expected=%d\n",
				name, trial, index, actual[index], expected[index]);
			return 0;
		}
	}
	return 1;
}

static int guards_ok(const int16_t words[WORDS + 2 * GUARD_WORDS])
{
	for (int index = 0; index < GUARD_WORDS; index++) {
		if (words[index] != (int16_t)0x55aa ||
			words[GUARD_WORDS + WORDS + index] != (int16_t)0x55aa)
			return 0;
	}
	return 1;
}

int main(void)
{
	_Alignas(32) int16_t input[WORDS];
	_Alignas(32) int16_t original[WORDS];
	_Alignas(32) int16_t expected[WORDS];
	_Alignas(32) int16_t split_mid[WORDS];
	_Alignas(32) int16_t split_out[WORDS];
	_Alignas(32) int16_t suffix_alias[WORDS];
	_Alignas(32) int16_t guarded[WORDS + 2 * GUARD_WORDS];
	int16_t *const candidate = guarded + GUARD_WORDS;
	struct observed_bounds observed = {0};
	static const int stage_limits[5] = {17760, 19581, 21637, 23752, 26043};

	for (int trial = 0; trial < TRIALS; trial++) {
		fill_input(input, trial);
		memcpy(original, input, sizeof(input));
		for (int index = 0; index < WORDS + 2 * GUARD_WORDS; index++)
			guarded[index] = (int16_t)0x55aa;

		reference_inverse(expected, input, &observed);
		gt32_n32_inverse_half_r1u_asm(candidate, input);
		if (!equal_words(expected, candidate, trial, "combined") ||
			!guards_ok(guarded) || memcmp(input, original, sizeof(input)) != 0)
			return 1;

		gt32_n32_idft_l2_l4_half_asm(split_mid, input);
		gt32_n32_inv_l8_l32_half_asm(split_out, split_mid);
		if (!equal_words(expected, split_out, trial, "split"))
			return 1;
		memcpy(suffix_alias, split_mid, sizeof(suffix_alias));
		gt32_n32_inv_l8_l32_half_asm(suffix_alias, suffix_alias);
		if (!equal_words(expected, suffix_alias, trial, "suffix-alias"))
			return 1;
	}

	if (observed.idft_internal > 10493 || observed.idft_output > 8880)
		return 1;
	for (unsigned stage = 0; stage < 5; stage++)
		if (observed.stage[stage] > stage_limits[stage])
			return 1;
	printf("n32-native-inverse: exact=passed trials=%d disjoint=passed "
		"suffix-alias=passed canary=passed observed=%d/%d/%d/%d/%d/%d/%d\n",
		TRIALS, observed.idft_internal, observed.idft_output,
		observed.stage[0], observed.stage[1], observed.stage[2],
		observed.stage[3], observed.stage[4]);
	return 0;
}
