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

typedef void (*bench_fn)(void);

__attribute__((noinline))
static void serial_suffix(void)
{
	gt32_n32_suffix_serial_asm(output, input);
}

__attribute__((noinline))
static void three_way_suffix(void)
{
	gt32_n32_suffix_3way_asm(output, input);
}

__attribute__((noinline))
static void dual_dft_suffix(void)
{
	gt32_n32_suffix_dft_dual_asm(output, input);
}

__attribute__((noinline))
static void mlkstyle_suffix(void)
{
	gt32_n32_suffix_mlkstyle_asm(output, input);
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
	bench_fn candidate, unsigned iterations)
{
	double control;
	double test;
	if ((sample & 1U) == 0U) {
		control = measure(serial_suffix, iterations);
		test = measure(candidate, iterations);
	} else {
		test = measure(candidate, iterations);
		control = measure(serial_suffix, iterations);
	}
	printf("SAMPLE,%s,%u,%.6f,%.6f,%.6f\n",
		region, sample, control, test, test - control);
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
		input[index] = (int16_t)(((index * 197 + 31) % 14001) - 7000);
	for (unsigned warmup = 0; warmup < 2U; warmup++) {
		(void)measure(serial_suffix, 200U);
		(void)measure(three_way_suffix, 200U);
		(void)measure(dual_dft_suffix, 200U);
		(void)measure(mlkstyle_suffix, 200U);
	}
	printf("META,experiment=GT-N32-SUFFIX-RESCHEDULE-015,iterations=%u,samples=%u\n",
		iterations, SAMPLES);
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		print_pair("s45_3way", sample, three_way_suffix, iterations);
		print_pair("dft_dual", sample, dual_dft_suffix, iterations);
		print_pair("mlkstyle", sample, mlkstyle_suffix, iterations);
	}
	return sink == UINT64_MAX ? 1 : 0;
}
