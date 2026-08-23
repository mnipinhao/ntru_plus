#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gate_069.h"
#include "internal.h"

static volatile uint8_t sink;

int main(int argc, char **argv)
{
	static int16_t a[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t b[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t m[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t scratch[NTRUPLUS_N] __attribute__((aligned(64)));
	static uint8_t out[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
	gt32_068_fn old_function = NULL;
	void (*new_function)(uint8_t *, const int16_t *, const int16_t *,
		const int16_t *) = NULL;
	size_t iterations = argc > 2 ? (size_t)strtoull(argv[2], NULL, 10) : 100000;

	if (argc < 2)
		return 2;
	if (strcmp(argv[1], "control") == 0)
		old_function = gt32_068_control_normal;
	else if (strcmp(argv[1], "reference") == 0)
		old_function = gt32_068_reference_normal;
	else if (strcmp(argv[1], "shared") == 0)
		old_function = gt32_068_candidate_normal;
	else if (strcmp(argv[1], "inline") == 0)
		old_function = gt32_068_inline_normal;
	else if (strcmp(argv[1], "cluster3") == 0)
		new_function = gt32_069_cluster3_normal;
	else if (strcmp(argv[1], "cluster4") == 0)
		new_function = gt32_069_cluster4_normal;
	else
		return 2;
	for (size_t i = 0; i < NTRUPLUS_N; i++) {
		a[i] = (int16_t)((17 * i + 31) % 3457);
		b[i] = (int16_t)((29 * i + 7) % 12001 - 6000);
		m[i] = (int16_t)((43 * i + 11) % 12001 - 6000);
	}
	for (size_t i = 0; i < 1000; i++) {
		if (old_function != NULL)
			old_function(out, a, b, m, scratch);
		else
			new_function(out, a, b, m);
	}
	for (size_t i = 0; i < iterations; i++) {
		if (old_function != NULL)
			old_function(out, a, b, m, scratch);
		else
			new_function(out, a, b, m);
	}
	sink ^= out[iterations % NTRUPLUS_POLYBYTES];
	printf("%u\n", sink);
	return 0;
}
