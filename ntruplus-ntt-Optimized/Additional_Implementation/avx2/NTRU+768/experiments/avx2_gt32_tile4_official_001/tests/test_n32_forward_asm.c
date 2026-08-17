#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "tile4.h"

#define Q 3457
#define WORDS 768
#define TRIALS 1000
#define GUARD_WORDS 16

static uint64_t rng_state = UINT64_C(0x6a09e667f3bcc909);

static uint32_t rng32(void)
{
	rng_state ^= rng_state << 7;
	rng_state ^= rng_state >> 9;
	return (uint32_t)rng_state;
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

static int32_t floor_shift(int32_t value, unsigned bits)
{
	const int32_t divisor = (int32_t)(UINT32_C(1) << bits);
	if (value >= 0)
		return value / divisor;
	return -((-value + divisor - 1) / divisor);
}

static int16_t center10(int16_t value)
{
	const int32_t quotient = floor_shift((int32_t)value * 10 + 16384, 15);
	return (int16_t)((int32_t)value - quotient * Q);
}

static int physical_k3(int slot, int qword)
{
	if (slot == 0)
		return 0;
	if (slot == 1)
		return qword < 2 ? 1 : 2;
	return qword < 2 ? 2 : 1;
}

static int conjugated_bound(int word)
{
	static const int bounds[2][3] = {
		{5977, 5971, 5899},
		{6126, 5945, 6092},
	};
	const int vector = word / 16;
	const int branch = vector / 24;
	const int slot = vector % 3;
	const int qword = (word % 16) / 4;
	return bounds[branch][physical_k3(slot, qword)];
}

static void standard_to_half(int16_t half[WORDS],
	const int16_t standard[WORDS])
{
	for (int branch = 0; branch < 2; branch++) {
		for (int group = 0; group < 8; group++) {
			for (int slot = 0; slot < 3; slot++) {
				const int half_vector = (branch * 8 + group) * 3 + slot;
				for (int qword = 0; qword < 4; qword++) {
					const int k3 = physical_k3(slot, qword);
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

static int equal_mod_q(const int16_t a[WORDS], const int16_t b[WORDS])
{
	for (int index = 0; index < WORDS; index++) {
		if (centered_mod(a[index]) != centered_mod(b[index]))
			return 0;
	}
	return 1;
}

static int check_guards(const int16_t guarded[WORDS + 2 * GUARD_WORDS])
{
	for (int index = 0; index < GUARD_WORDS; index++) {
		if (guarded[index] != (int16_t)0x5a5a ||
			guarded[GUARD_WORDS + WORDS + index] != (int16_t)0x5a5a)
			return 0;
	}
	return 1;
}

static void fill_input(int16_t input[WORDS], int trial)
{
	for (int index = 0; index < WORDS; index++) {
		if (trial == 0)
			input[index] = -3;
		else if (trial == 1)
			input[index] = 4;
		else if (trial == 2)
			input[index] = (index & 1) != 0 ? 4 : -3;
		else
			input[index] = (int16_t)((int)(rng32() & 7U) - 3);
	}
}

int main(void)
{
	_Alignas(32) int16_t input[WORDS], input_copy[WORDS];
	_Alignas(32) int16_t standard[WORDS], expected_half[WORDS];
	_Alignas(32) int16_t raw_guarded[WORDS + 2 * GUARD_WORDS];
	_Alignas(32) int16_t centered_guarded[WORDS + 2 * GUARD_WORDS];
	_Alignas(32) int16_t conjugated_guarded[WORDS + 2 * GUARD_WORDS];
	_Alignas(32) int16_t branch_at_time_guarded[WORDS + 2 * GUARD_WORDS];
	_Alignas(32) int16_t alias[WORDS];
	int observed_raw = 0;
	int observed_centered = 0;
	int observed_conjugated = 0;

	for (int trial = 0; trial < TRIALS; trial++) {
		int16_t *const raw = raw_guarded + GUARD_WORDS;
		int16_t *const reduced = centered_guarded + GUARD_WORDS;
		int16_t *const conjugated = conjugated_guarded + GUARD_WORDS;
		int16_t *const branch_at_time = branch_at_time_guarded + GUARD_WORDS;
		fill_input(input, trial);
		memcpy(input_copy, input, sizeof(input));
		for (int index = 0; index < WORDS + 2 * GUARD_WORDS; index++) {
			raw_guarded[index] = (int16_t)0x5a5a;
			centered_guarded[index] = (int16_t)0x5a5a;
			conjugated_guarded[index] = (int16_t)0x5a5a;
			branch_at_time_guarded[index] = (int16_t)0x5a5a;
		}

		gt32_tile4_forward_full_wide_raw_pair_align64_asm(standard, input);
		standard_to_half(expected_half, standard);
		gt32_n32_forward_half_raw_asm(raw, input);
		gt32_n32_forward_half_centered_asm(reduced, input);
		gt32_n32_forward_half_conjugated_asm(conjugated, input);
		gt32_n32_forward_half_conjugated_branch_at_time_asm(branch_at_time, input);

		if (memcmp(input, input_copy, sizeof(input)) != 0) {
			fprintf(stderr, "input clobber at trial %d\n", trial);
			return 1;
		}
		if (!check_guards(raw_guarded) || !check_guards(centered_guarded) ||
			!check_guards(conjugated_guarded)) {
			fprintf(stderr, "guard clobber at trial %d\n", trial);
			return 1;
		}
		if (!check_guards(branch_at_time_guarded) ||
			memcmp(conjugated, branch_at_time, sizeof(input)) != 0) {
			fprintf(stderr, "branch-at-time exact mismatch at trial %d\n", trial);
			return 1;
		}
		if (!equal_mod_q(raw, expected_half) ||
			!equal_mod_q(reduced, expected_half) ||
			!equal_mod_q(conjugated, expected_half)) {
			int mismatch = 0;
			int mismatch_count = 0;
			while (mismatch < WORDS &&
				centered_mod(raw[mismatch]) == centered_mod(expected_half[mismatch]) &&
				centered_mod(reduced[mismatch]) == centered_mod(expected_half[mismatch]) &&
				centered_mod(conjugated[mismatch]) == centered_mod(expected_half[mismatch]))
				mismatch++;
			fprintf(stderr, "forward semantic mismatch at trial %d word %d: "
				"raw=%d centered=%d conjugated=%d expected=%d\n", trial, mismatch,
				mismatch < WORDS ? raw[mismatch] : 0,
				mismatch < WORDS ? reduced[mismatch] : 0,
				mismatch < WORDS ? conjugated[mismatch] : 0,
				mismatch < WORDS ? expected_half[mismatch] : 0);
			for (int index = 0; index < WORDS; index++) {
				if (centered_mod(raw[index]) != centered_mod(expected_half[index]) ||
					centered_mod(reduced[index]) != centered_mod(expected_half[index]) ||
					centered_mod(conjugated[index]) != centered_mod(expected_half[index])) {
					if (mismatch_count < 24)
						fprintf(stderr, "  word %d: raw=%d centered=%d "
							"conjugated=%d expected=%d\n", index, raw[index],
							reduced[index], conjugated[index], expected_half[index]);
					mismatch_count++;
				}
			}
			fprintf(stderr, "  mismatch-count=%d\n", mismatch_count);
			return 1;
		}
		for (int index = 0; index < WORDS; index++) {
			const int raw_abs = raw[index] < 0 ? -(int)raw[index] : (int)raw[index];
			const int centered_abs = reduced[index] < 0
				? -(int)reduced[index] : (int)reduced[index];
			const int conjugated_abs = conjugated[index] < 0
				? -(int)conjugated[index] : (int)conjugated[index];
			if (reduced[index] != center10(raw[index])) {
				fprintf(stderr, "center10 mismatch at trial %d word %d\n",
					trial, index);
				return 1;
			}
			if (raw_abs > observed_raw)
				observed_raw = raw_abs;
			if (centered_abs > observed_centered)
				observed_centered = centered_abs;
			if (conjugated_abs > observed_conjugated)
				observed_conjugated = conjugated_abs;
			if (centered_abs > 3080) {
				fprintf(stderr, "centered proof bound exceeded: %d\n",
					centered_abs);
				return 1;
			}
			if (conjugated_abs > conjugated_bound(index)) {
				fprintf(stderr, "conjugated proof bound exceeded at trial %d "
					"word %d: %d > %d\n", trial, index,
					conjugated_abs, conjugated_bound(index));
				return 1;
			}
		}

		memcpy(alias, input, sizeof(alias));
		gt32_n32_forward_half_raw_asm(alias, alias);
		if (memcmp(alias, raw, sizeof(alias)) != 0) {
			fprintf(stderr, "raw out==in mismatch at trial %d\n", trial);
			return 1;
		}
		memcpy(alias, input, sizeof(alias));
		gt32_n32_forward_half_centered_asm(alias, alias);
		if (memcmp(alias, reduced, sizeof(alias)) != 0) {
			fprintf(stderr, "centered out==in mismatch at trial %d\n", trial);
			return 1;
		}
		memcpy(alias, input, sizeof(alias));
		gt32_n32_forward_half_conjugated_asm(alias, alias);
		if (memcmp(alias, conjugated, sizeof(alias)) != 0) {
			fprintf(stderr, "conjugated out==in mismatch at trial %d\n", trial);
			return 1;
		}
		memcpy(alias, input, sizeof(alias));
		gt32_n32_forward_half_conjugated_branch_at_time_asm(alias, alias);
		if (memcmp(alias, conjugated, sizeof(alias)) != 0) {
			fprintf(stderr, "branch-at-time out==in mismatch at trial %d\n", trial);
			return 1;
		}
	}

	printf("n32-forward-asm: semantic=passed center10=passed alias=passed "
		"guards=passed trials=%d observed-raw=%d observed-centered=%d "
		"observed-conjugated=%d\n",
		TRIALS, observed_raw, observed_centered, observed_conjugated);
	return 0;
}
