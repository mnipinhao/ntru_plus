#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <x86intrin.h>

#include "tile4.h"

#define WORDS GT32_TILE4_POLY_WORDS
#define SAMPLES 20U

static int16_t input[WORDS] __attribute__((aligned(64)));
static int16_t output[WORDS] __attribute__((aligned(64)));
static volatile uint64_t sink;

typedef void (*bench_fn)(int16_t *, const int16_t *);

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

static double measure(bench_fn function, unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned iteration = 0; iteration < iterations; iteration++)
		function(output, input);
	const uint64_t end = stop_tsc();
	sink += (uint16_t)output[iterations % WORDS];
	return (double)(end - begin) / (double)iterations;
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 5000U;
	cpu_set_t set;

	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof(set), &set) != 0)
		perror("sched_setaffinity");
	for (int index = 0; index < WORDS; index++)
		input[index] = (int16_t)((index * 29 + 5) % 8 - 3);
	(void)measure(gt32_n32_forward_half_conjugated_asm, 200U);
	(void)measure(gt32_n32_forward_half_conjugated_branch_at_time_asm, 200U);
	printf("META,experiment=GT-N32-CONJ-BRANCH-AT-A-TIME-FULL-020,iterations=%u,samples=%u\n",
		iterations, SAMPLES);
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		double control;
		double candidate;
		if ((sample & 1U) == 0U) {
			control = measure(gt32_n32_forward_half_conjugated_asm, iterations);
			candidate = measure(
				gt32_n32_forward_half_conjugated_branch_at_time_asm, iterations);
		} else {
			candidate = measure(
				gt32_n32_forward_half_conjugated_branch_at_time_asm, iterations);
			control = measure(gt32_n32_forward_half_conjugated_asm, iterations);
		}
		printf("SAMPLE,%u,%.6f,%.6f,%.6f\n", sample, control,
			candidate, candidate - control);
	}
	return sink == UINT64_MAX ? 1 : 0;
}
