#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpucycles.h"
#include "gate_068.h"
#include "internal.h"

#define LOOPS 4
#define TIMINGS 48
#define OBSERVATIONS (LOOPS * TIMINGS)

static volatile uint64_t sink;
static uint64_t rng_state = UINT64_C(0x068be3c8e2d13371);

static uint32_t random32(void)
{
	rng_state ^= rng_state << 13;
	rng_state ^= rng_state >> 7;
	rng_state ^= rng_state << 17;
	return (uint32_t)rng_state;
}

static uint64_t digest(const uint8_t *input, size_t bytes)
{
	uint64_t value = UINT64_C(1469598103934665603);
	for (size_t i = 0; i < bytes; i++) {
		value ^= input[i];
		value *= UINT64_C(1099511628211);
	}
	return value;
}

static void measure(const char *name, gt32_068_fn function,
	uint8_t out[NTRUPLUS_POLYBYTES], const int16_t *a, const int16_t *b,
	const int16_t *m, int16_t *scratch)
{
	long long stamps[TIMINGS + 1];
	long long observations[OBSERVATIONS];
	size_t used = 0;
	for (size_t i = 0; i < 64; i++)
		function(out, a, b, m, scratch);
	for (size_t loop = 0; loop < LOOPS; loop++) {
		for (size_t i = 0; i <= TIMINGS; i++) {
			stamps[i] = cpucycles();
			function(out, a, b, m, scratch);
		}
		for (size_t i = 0; i < TIMINGS; i++)
			observations[used++] = stamps[i + 1] - stamps[i];
	}
	printf("%s_cycles", name);
	for (size_t i = 0; i < OBSERVATIONS; i++)
		printf(" %lld", observations[i]);
	putchar('\n');
	sink ^= digest(out, NTRUPLUS_POLYBYTES);
}

int main(int argc, char **argv)
{
	static int16_t a[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t b[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t m[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t scratch[NTRUPLUS_N] __attribute__((aligned(64)));
	static uint8_t out[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
	const char *placement = argc > 1 ? argv[1] : "normal";
	const char *order = argc > 2 ? argv[2] : "0123";
	gt32_068_fn functions[4];
	const char *names[4] = {"control", "reference", "shared", "inline"};

	for (size_t i = 0; i < NTRUPLUS_N; i++) {
		a[i] = (int16_t)(random32() % 3457);
		b[i] = (int16_t)((int32_t)(random32() % 20001) - 10000);
		m[i] = (int16_t)((int32_t)(random32() % 20001) - 10000);
	}
	if (strcmp(placement, "normal") == 0) {
		functions[0] = gt32_068_control_normal;
		functions[1] = gt32_068_reference_normal;
		functions[2] = gt32_068_candidate_normal;
		functions[3] = gt32_068_inline_normal;
	} else if (strcmp(placement, "reversed") == 0) {
		functions[0] = gt32_068_control_reversed;
		functions[1] = gt32_068_reference_reversed;
		functions[2] = gt32_068_candidate_reversed;
		functions[3] = gt32_068_inline_reversed;
	} else {
		return 2;
	}
	printf("cpucycles_implementation %s\n", cpucycles_implementation());
	printf("placement %s\n", placement);
	for (size_t index = 0; index < 4; index++)
		printf("%s_address %p\n", names[index],
			(void *)(uintptr_t)functions[index]);
	if (strlen(order) != 4)
		return 2;
	for (size_t index = 0; index < 4; index++) {
		unsigned selected = (unsigned)(order[index] - '0');
		if (selected >= 4)
			return 2;
		measure(names[selected], functions[selected], out, a, b, m, scratch);
	}
	printf("sink %" PRIu64 "\n", sink);
	return 0;
}
