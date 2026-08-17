#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "tile4.h"

#define IN_WORDS GT32_TILE4_POLY_WORDS
#define OUT_WORDS 256

static uint32_t state = UINT32_C(0x8c19a57d);

static uint32_t random32(void)
{
	state = state * UINT32_C(1664525) + UINT32_C(1013904223);
	return state;
}

int main(void)
{
	_Alignas(64) int16_t input[IN_WORDS];
	_Alignas(64) int16_t saved[IN_WORDS];
	_Alignas(64) int16_t control[OUT_WORDS];
	_Alignas(64) int16_t candidate[OUT_WORDS];

	for (int trial = 0; trial < 1000; trial++) {
		for (int index = 0; index < IN_WORDS; index++)
			input[index] = (int16_t)((int32_t)(random32() % 8U) - 3);
		memcpy(saved, input, sizeof(input));
		gt32_n32_conj_wave_control_asm(control, input);
		gt32_n32_conj_wave_branch_at_time_asm(candidate, input);
		if (memcmp(control, candidate, sizeof(control)) != 0) {
			for (int index = 0; index < OUT_WORDS; index++) {
				if (control[index] != candidate[index]) {
					fprintf(stderr,
						"trial=%d word=%d control=%d candidate=%d\n",
						trial, index, control[index], candidate[index]);
					return 1;
				}
			}
		}
		if (memcmp(input, saved, sizeof(input)) != 0) {
			fputs("input modified\n", stderr);
			return 1;
		}
	}
	puts("n32 branch-at-a-time: 1000 one-wave exact-word trials passed");
	return 0;
}
