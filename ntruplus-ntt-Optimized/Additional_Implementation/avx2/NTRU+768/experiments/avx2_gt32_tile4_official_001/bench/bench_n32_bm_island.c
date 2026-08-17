#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <x86intrin.h>

#include "tile4.h"

#define WORDS 768
#define SAMPLES 20U

static int16_t standard_a[WORDS] __attribute__((aligned(64)));
static int16_t standard_b[WORDS] __attribute__((aligned(64)));
static int16_t half_a[WORDS] __attribute__((aligned(64)));
static int16_t half_b[WORDS] __attribute__((aligned(64)));
static int16_t output[WORDS] __attribute__((aligned(64)));
static volatile uint64_t sink;

typedef void (*bench_fn)(void);

static int physical_k3(int slot, int qword)
{
	if (slot == 0)
		return 0;
	if (slot == 1)
		return qword < 2 ? 1 : 2;
	return qword < 2 ? 2 : 1;
}

static void standard_to_half(int16_t half[WORDS], const int16_t standard[WORDS])
{
	for (int branch = 0; branch < 2; branch++) {
		for (int group = 0; group < 8; group++) {
			for (int slot = 0; slot < 3; slot++) {
				const int hv = (branch * 8 + group) * 3 + slot;
				for (int qword = 0; qword < 4; qword++) {
					const int k3 = physical_k3(slot, qword);
					const int sv = (k3 * 2 + branch) * 8 + group;
					for (int degree = 0; degree < 4; degree++)
						half[16 * hv + 4 * qword + degree] =
							standard[16 * sv + 4 * qword + degree];
				}
			}
		}
	}
}

__attribute__((noinline))
static void control(void)
{
	gt32_tile4_basemul_scale_ff_aos_r1u_asm(output, standard_a, standard_b);
}

__attribute__((noinline))
static void candidate(void)
{
	gt32_n32_basemul_half_r1u_asm(output, half_a, half_b);
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
	for (unsigned index = 0; index < WORDS; index++) {
		standard_a[index] = (int16_t)((int)(index % 2001U) - 1000);
		standard_b[index] = (int16_t)((int)((index * 37U + 11U) % 2001U) - 1000);
	}
	standard_to_half(half_a, standard_a);
	standard_to_half(half_b, standard_b);
	for (unsigned warmup = 0; warmup < 2U; warmup++) {
		(void)measure(control, 200U);
		(void)measure(candidate, 200U);
	}
	printf("META,experiment=GT-N32-BM-ISLAND-004,iterations=%u,samples=%u\n",
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
		printf("SAMPLE,bm_landing,%u,%.6f,%.6f,%.6f\n",
			sample, baseline, test, test - baseline);
	}
	return sink == UINT64_MAX ? 1 : 0;
}
