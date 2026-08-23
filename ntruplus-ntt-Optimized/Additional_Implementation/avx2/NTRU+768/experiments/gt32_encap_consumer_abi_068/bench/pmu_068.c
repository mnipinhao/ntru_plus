#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "gate_068.h"
#include "internal.h"

static volatile uint8_t sink;

int main(int argc, char **argv)
{
	static int16_t a[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t b[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t m[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t scratch[NTRUPLUS_N] __attribute__((aligned(64)));
	static uint8_t out[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
	gt32_068_fn function;
	size_t iterations = argc > 2 ? (size_t)strtoull(argv[2], NULL, 10) : 100000;

	if (argc < 2)
		return 2;
	if (strcmp(argv[1], "control") == 0)
		function = gt32_068_control_normal;
	else if (strcmp(argv[1], "reference") == 0)
		function = gt32_068_reference_normal;
	else if (strcmp(argv[1], "candidate") == 0)
		function = gt32_068_candidate_normal;
	else if (strcmp(argv[1], "inline") == 0)
		function = gt32_068_inline_normal;
	else
		return 2;
	for (size_t i = 0; i < NTRUPLUS_N; i++) {
		a[i] = (int16_t)((17 * i + 31) % 3457);
		b[i] = (int16_t)((29 * i + 7) % 12001 - 6000);
		m[i] = (int16_t)((43 * i + 11) % 12001 - 6000);
	}
	for (size_t i = 0; i < 1000; i++)
		function(out, a, b, m, scratch);
	for (size_t i = 0; i < iterations; i++)
		function(out, a, b, m, scratch);
	sink ^= out[iterations % NTRUPLUS_POLYBYTES];
	printf("%u\n", sink);
	return 0;
}
