#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <x86intrin.h>

#include "tile4.h"
#include "../generated/tile4_n32_inverse_test_ranges.h"

#define WORDS 768
#define SAMPLES 20U

static int16_t input[WORDS] __attribute__((aligned(64)));
static int16_t midpoint[WORDS] __attribute__((aligned(64)));
static int16_t output[WORDS] __attribute__((aligned(64)));
static int16_t expected[WORDS] __attribute__((aligned(64)));
static volatile uint64_t sink;

typedef void (*bench_fn)(void);

__attribute__((noinline))
static void split_inverse(void)
{
	gt32_n32_idft_l2_l4_half_asm(midpoint, input);
	gt32_n32_inv_l8_l32_half_asm(output, midpoint);
}

__attribute__((noinline))
static void combined_inverse(void)
{
	gt32_n32_inverse_half_r1u_asm(output, input);
}

__attribute__((noinline))
static void idft_l2_l4_only(void)
{
	gt32_n32_idft_l2_l4_half_asm(output, input);
}

__attribute__((noinline))
static void l8_l32_only(void)
{
	gt32_n32_inv_l8_l32_half_asm(output, midpoint);
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

static double measure(bench_fn function, unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned iteration = 0; iteration < iterations; iteration++)
		function();
	const uint64_t end = stop_tsc();
	sink += (uint16_t)output[iterations % WORDS];
	return (double)(end - begin) / (double)iterations;
}

static void print_pair(const char *region, unsigned sample,
	bench_fn control, bench_fn candidate, unsigned iterations)
{
	double baseline;
	double test;
	if ((sample & 1U) == 0U) {
		baseline = measure(control, iterations);
		test = measure(candidate, iterations);
	} else {
		test = measure(candidate, iterations);
		baseline = measure(control, iterations);
	}
	printf("SAMPLE,%s,%u,%.6f,%.6f,%.6f\n",
		region, sample, baseline, test, test - baseline);
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
	for (int index = 0; index < WORDS; index++) {
		const int low = gt32_n32_r1u_min[index];
		const int high = gt32_n32_r1u_max[index];
		input[index] = (int16_t)(low +
			(int)((uint32_t)(index * 977 + 131) %
			(uint32_t)(high - low + 1)));
	}
	gt32_n32_inverse_half_r1u_asm(expected, input);
	split_inverse();
	if (memcmp(expected, output, sizeof(output)) != 0) {
		fputs("split/combined mismatch\n", stderr);
		return 1;
	}
	gt32_n32_idft_l2_l4_half_asm(midpoint, input);
	for (unsigned warmup = 0; warmup < 3U; warmup++) {
		(void)measure(split_inverse, 200U);
		(void)measure(combined_inverse, 200U);
		(void)measure(idft_l2_l4_only, 200U);
		(void)measure(l8_l32_only, 200U);
	}
	printf("META,experiment=GT-N32-INVERSE-ASM-012,iterations=%u,samples=%u\n",
		iterations, SAMPLES);
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		print_pair("split_vs_combined", sample,
			split_inverse, combined_inverse, iterations);
		const double idft = measure(idft_l2_l4_only, iterations);
		const double suffix = measure(l8_l32_only, iterations);
		printf("ABSOLUTE,components,%u,%.6f,%.6f,%.6f\n",
			sample, idft, suffix, idft + suffix);
	}
	return sink == UINT64_MAX ? 1 : 0;
}
