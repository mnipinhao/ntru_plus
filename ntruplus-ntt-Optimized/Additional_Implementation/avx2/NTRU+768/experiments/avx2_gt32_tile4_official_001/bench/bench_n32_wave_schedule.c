#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <x86intrin.h>

#include "tile4.h"

#define WORDS 768
#define SAMPLES 20U

static int16_t input[WORDS] __attribute__((aligned(64)));
static int16_t output[WORDS] __attribute__((aligned(64)));
static volatile uint64_t sink;

typedef void (*bench_fn)(void);

__attribute__((noinline))
static void control(void)
{
	gt32_n32_wave_s1s3_control_asm(output, input);
}

__attribute__((noinline))
static void candidate(void)
{
	gt32_n32_wave_s1s3_c2_asm(output, input);
}

__attribute__((noinline))
static void route_control(void)
{
	gt32_n32_suffix_route6_control_asm(output, input);
}

__attribute__((noinline))
static void route_candidate(void)
{
	gt32_n32_suffix_route5_half_asm(output, input);
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

static double measure(bench_fn fn, unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned iteration = 0; iteration < iterations; iteration++)
		fn();
	const uint64_t end = stop_tsc();
	sink += (uint16_t)output[iterations % WORDS];
	return (double)(end - begin) / (double)iterations;
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 5000U;
	cpu_set_t cpuset;

	CPU_ZERO(&cpuset);
	CPU_SET(1, &cpuset);
	if (sched_setaffinity(0, sizeof(cpuset), &cpuset) != 0)
		perror("sched_setaffinity");
	for (unsigned index = 0; index < WORDS; index++)
		input[index] = (int16_t)((int)((index * 97U + 31U) % 3599U) - 1799);
	for (unsigned warmup = 0; warmup < 2U; warmup++) {
		(void)measure(control, 200U);
		(void)measure(candidate, 200U);
		(void)measure(route_control, 200U);
		(void)measure(route_candidate, 200U);
	}
	printf("META,experiment=GT-N32-PHYSICAL-SCHEDULE-005,iterations=%u,samples=%u\n",
		iterations, SAMPLES);
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		double baseline;
		double test;
		if ((sample & 1U) == 0U) {
			baseline = measure(control, iterations);
			test = measure(candidate, iterations);
		} else {
			test = measure(candidate, iterations);
			baseline = measure(control, iterations);
		}
		printf("SAMPLE,wave_s1s3,%u,%.6f,%.6f,%.6f\n",
			sample, baseline, test, test - baseline);
		if ((sample & 1U) == 0U) {
			baseline = measure(route_control, iterations);
			test = measure(route_candidate, iterations);
		} else {
			test = measure(route_candidate, iterations);
			baseline = measure(route_control, iterations);
		}
		printf("SAMPLE,suffix_route,%u,%.6f,%.6f,%.6f\n",
			sample, baseline, test, test - baseline);
	}
	return sink == UINT64_MAX ? 1 : 0;
}
