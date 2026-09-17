#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "cpucycles.h"
#include "internal.h"

#define LOOPS 3
#define TIMINGS 32
#define OBSERVATIONS (LOOPS * TIMINGS)

typedef void (*forward_fn)(int16_t *, const int16_t *);
void gt32_130_control_normal(int16_t *, const int16_t *);
void gt32_130_candidate_normal(int16_t *, const int16_t *);
void gt32_130_control_reversed(int16_t *, const int16_t *);
void gt32_130_candidate_reversed(int16_t *, const int16_t *);

static volatile uint64_t sink;

static void print_observations(const char *name, const long long *values)
{
	printf("%s_cycles", name);
	for (size_t i = 0; i < OBSERVATIONS; i++)
		printf(" %lld", values[i]);
	putchar('\n');
}

static void measure(const char *name, forward_fn fn, int16_t *out,
	const int16_t *in)
{
	long long stamps[TIMINGS + 1];
	long long values[OBSERVATIONS];
	size_t used = 0;
	for (size_t i = 0; i < 128; i++)
		fn(out, in);
	for (size_t loop = 0; loop < LOOPS; loop++) {
		for (size_t i = 0; i <= TIMINGS; i++) {
			stamps[i] = cpucycles();
			fn(out, in);
		}
		for (size_t i = 0; i < TIMINGS; i++)
			values[used++] = stamps[i + 1] - stamps[i];
	}
	for (size_t i = 0; i < NTRUPLUS_N; i++)
		sink = sink * 131 + (uint16_t)out[i];
	print_observations(name, values);
}

int main(int argc, char **argv)
{
	static int16_t in[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t out[NTRUPLUS_N] __attribute__((aligned(64)));
	forward_fn control, candidate;
	const char *placement = argc > 1 ? argv[1] : "normal";
	const char *order = argc > 2 ? argv[2] : "AB";
	for (size_t i = 0; i < NTRUPLUS_N; i++)
		in[i] = (int16_t)((int)(i * 73 % 3457) - 1728);
	if (strcmp(placement, "normal") == 0) {
		control = gt32_130_control_normal;
		candidate = gt32_130_candidate_normal;
	} else {
		control = gt32_130_control_reversed;
		candidate = gt32_130_candidate_reversed;
	}
	printf("cpucycles_implementation %s\n", cpucycles_implementation());
	printf("placement %s\n", placement);
	printf("control_address %p\n", (void *)(uintptr_t)control);
	printf("candidate_address %p\n", (void *)(uintptr_t)candidate);
	if (strcmp(order, "AB") == 0) {
		measure("control", control, out, in);
		measure("candidate", candidate, out, in);
	} else {
		measure("candidate", candidate, out, in);
		measure("control", control, out, in);
	}
	printf("sink %" PRIu64 "\n", sink);
	return 0;
}
