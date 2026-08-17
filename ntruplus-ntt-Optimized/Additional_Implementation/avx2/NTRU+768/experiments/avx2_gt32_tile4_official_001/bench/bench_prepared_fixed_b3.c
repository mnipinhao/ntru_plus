#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <x86intrin.h>

#include "tile4.h"
#include "tile4_prepared_fixed_b3.h"

#define WORDS GT32_TILE4_POLY_WORDS
#define SAMPLES 20

static gt32_prepared_fixed_b3_general_e1 matrix;
static volatile uint64_t sink;

static uint32_t next_random(uint32_t *state)
{
	*state = *state * 1664525U + 1013904223U;
	return *state;
}

static uint64_t start_tsc(void)
{
	_mm_lfence();
	return __rdtsc();
}

static uint64_t stop_tsc(void)
{
	unsigned aux;
	const uint64_t value = __rdtscp(&aux);
	_mm_lfence();
	return value;
}

__attribute__((noinline))
static void control(int16_t *out, const int16_t *dynamic,
	const int16_t *fixed)
{
	gt32_tile4_basemul_general_soa_soa_to_soa_asm(out, dynamic, fixed);
}

__attribute__((noinline))
static void candidate(int16_t *out, const int16_t *dynamic,
	const int16_t *fixed)
{
	(void)fixed;
	gt32_tile4_basemul_general_fixed_soa_e1_asm(out, dynamic, &matrix);
}

typedef void (*kernel_fn)(int16_t *, const int16_t *, const int16_t *);

static double measure(kernel_fn fn, int16_t *out, const int16_t *dynamic,
	const int16_t *fixed, unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; ++i)
		fn(out, dynamic, fixed);
	const uint64_t end = stop_tsc();
	sink += (uint16_t)out[iterations % WORDS];
	return (double)(end - begin) / iterations;
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 10000U;
	int16_t fixed[WORDS] __attribute__((aligned(64)));
	int16_t dynamic[WORDS] __attribute__((aligned(64)));
	int16_t out0[WORDS] __attribute__((aligned(64)));
	int16_t out1[WORDS] __attribute__((aligned(64)));
	uint32_t state = UINT32_C(0xF13EDB3);
	cpu_set_t set;

	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof(set), &set) != 0)
		perror("sched_setaffinity");
	for (unsigned i = 0; i < WORDS; ++i) {
		fixed[i] = (int16_t)(next_random(&state) % 3457U);
		dynamic[i] = (int16_t)((int32_t)(next_random(&state) % 21577U)
			- 10788);
	}
	gt32_prepare_fixed_b3_general_e1(&matrix, fixed);
	for (unsigned warm = 0; warm < 4; ++warm) {
		(void)measure(control, out0, dynamic, fixed, 2000);
		(void)measure(candidate, out1, dynamic, fixed, 2000);
	}
	for (unsigned sample = 0; sample < SAMPLES; ++sample) {
		double c, n;
		if ((sample & 1U) == 0U) {
			c = measure(control, out0, dynamic, fixed, iterations);
			n = measure(candidate, out1, dynamic, fixed, iterations);
		} else {
			n = measure(candidate, out1, dynamic, fixed, iterations);
			c = measure(control, out0, dynamic, fixed, iterations);
		}
		printf("SAMPLE,general_fixed,%u,%.6f,%.6f,%.6f\n",
			sample, c, n, n - c);
	}
	printf("META,iterations=%u,samples=%u,matrix_bytes=%zu\n",
		iterations, SAMPLES, sizeof matrix);
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}
