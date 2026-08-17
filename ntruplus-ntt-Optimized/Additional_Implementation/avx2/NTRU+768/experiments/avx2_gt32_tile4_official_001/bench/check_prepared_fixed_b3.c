#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "../src/tile4.h"
#include "../src/tile4_prepared_fixed_b3.h"

static uint32_t state = 1;

static uint32_t random32(void)
{
	state = state * 1664525u + 1013904223u;
	return state;
}

static int modq(int value)
{
	value %= 3457;
	if (value < 0)
		value += 3457;
	return value;
}

int main(void)
{
	static int16_t fixed[GT32_TILE4_POLY_WORDS] __attribute__((aligned(64)));
	static int16_t dynamic[GT32_TILE4_POLY_WORDS] __attribute__((aligned(64)));
	static int16_t control[GT32_TILE4_POLY_WORDS] __attribute__((aligned(64)));
	static int16_t candidate[GT32_TILE4_POLY_WORDS] __attribute__((aligned(64)));
	static gt32_prepared_fixed_b3_general_e1 matrix;

	for (int trial = 0; trial < 1000; ++trial) {
		for (int i = 0; i < GT32_TILE4_POLY_WORDS; ++i) {
			fixed[i] = (int16_t)(random32() % 3457u);
			dynamic[i] = (int16_t)((int)(random32() % 21577u) - 10788);
		}
		gt32_prepare_fixed_b3_general_e1(&matrix, fixed);
		gt32_tile4_basemul_general_soa_soa_to_soa_asm(control,
			fixed, dynamic);
		gt32_tile4_basemul_general_fixed_soa_e1_asm(candidate,
			dynamic, &matrix);
		for (int i = 0; i < GT32_TILE4_POLY_WORDS; ++i) {
			if (modq(control[i]) != modq(candidate[i])) {
				fprintf(stderr, "trial=%d word=%d control=%d candidate=%d\n",
					trial, i, control[i], candidate[i]);
				return 1;
			}
		}
	}
	puts("prepared fixed B3 correctness: pass (1000 trials)");
	return 0;
}
