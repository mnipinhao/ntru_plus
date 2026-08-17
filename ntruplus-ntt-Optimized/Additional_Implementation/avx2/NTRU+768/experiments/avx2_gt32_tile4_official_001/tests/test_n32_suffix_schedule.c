#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "tile4.h"

#define WORDS GT32_TILE4_POLY_WORDS
#define GUARD_WORDS 32

static uint32_t state = 1U;

static uint32_t random32(void)
{
	state = state * 1664525U + 1013904223U;
	return state;
}

static int guard_ok(const int16_t buffer[WORDS + 2 * GUARD_WORDS])
{
	for (int index = 0; index < GUARD_WORDS; index++) {
		if (buffer[index] != (int16_t)0x5a5a ||
		    buffer[GUARD_WORDS + WORDS + index] != (int16_t)0x5a5a)
			return 0;
	}
	return 1;
}

int main(void)
{
	_Alignas(64) int16_t input[WORDS];
	_Alignas(64) int16_t saved[WORDS];
	_Alignas(64) int16_t control_storage[WORDS + 2 * GUARD_WORDS];
	_Alignas(64) int16_t candidate_storage[WORDS + 2 * GUARD_WORDS];
	_Alignas(64) int16_t dft_dual_storage[WORDS + 2 * GUARD_WORDS];
	_Alignas(64) int16_t mlkstyle_storage[WORDS + 2 * GUARD_WORDS];
	int16_t *const control = control_storage + GUARD_WORDS;
	int16_t *const candidate = candidate_storage + GUARD_WORDS;
	int16_t *const dft_dual = dft_dual_storage + GUARD_WORDS;
	int16_t *const mlkstyle = mlkstyle_storage + GUARD_WORDS;

	for (int trial = 0; trial < 1000; trial++) {
		for (int index = 0; index < WORDS; index++)
			input[index] = (int16_t)((int32_t)(random32() % 14001U) - 7000);
		memcpy(saved, input, sizeof(input));
		for (int index = 0; index < WORDS + 2 * GUARD_WORDS; index++) {
			control_storage[index] = (int16_t)0x5a5a;
			candidate_storage[index] = (int16_t)0x5a5a;
			dft_dual_storage[index] = (int16_t)0x5a5a;
			mlkstyle_storage[index] = (int16_t)0x5a5a;
		}
		gt32_n32_suffix_serial_asm(control, input);
		gt32_n32_suffix_3way_asm(candidate, input);
		gt32_n32_suffix_dft_dual_asm(dft_dual, input);
		gt32_n32_suffix_mlkstyle_asm(mlkstyle, input);
		if (memcmp(control, candidate, sizeof(input)) != 0) {
			for (int index = 0; index < WORDS; index++) {
				if (control[index] != candidate[index]) {
					fprintf(stderr,
						"suffix mismatch trial=%d word=%d control=%d candidate=%d\n",
						trial, index, control[index], candidate[index]);
					return 1;
				}
			}
		}
		if (memcmp(control, dft_dual, sizeof(input)) != 0) {
			for (int index = 0; index < WORDS; index++) {
				if (control[index] != dft_dual[index]) {
					fprintf(stderr,
						"dual DFT mismatch trial=%d word=%d control=%d candidate=%d\n",
						trial, index, control[index], dft_dual[index]);
					return 1;
				}
			}
		}
		if (memcmp(control, mlkstyle, sizeof(input)) != 0) {
			for (int index = 0; index < WORDS; index++) {
				if (control[index] != mlkstyle[index]) {
					fprintf(stderr,
						"MLK-style mismatch trial=%d word=%d control=%d candidate=%d\n",
						trial, index, control[index], mlkstyle[index]);
					return 1;
				}
			}
		}
		if (memcmp(input, saved, sizeof(input)) != 0 ||
		    !guard_ok(control_storage) || !guard_ok(candidate_storage) ||
		    !guard_ok(dft_dual_storage) || !guard_ok(mlkstyle_storage)) {
			fputs("suffix input/guard corruption\n", stderr);
			return 1;
		}
	}
	puts("n32 suffix serial/3way/dual-DFT/MLK-style: 1000 exact-word trials passed");
	return 0;
}
