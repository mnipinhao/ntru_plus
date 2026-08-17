#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <x86intrin.h>

#include "tile4.h"

#define WORDS 768
#define SAMPLES 20U

void gt32_tile4_n5_to_n32_half_asm(int16_t *, const int16_t *);

static int16_t coeff_a[WORDS] __attribute__((aligned(64)));
static int16_t coeff_b[WORDS] __attribute__((aligned(64)));
static int16_t standard_a[WORDS] __attribute__((aligned(64)));
static int16_t standard_b[WORDS] __attribute__((aligned(64)));
static int16_t half_a[WORDS] __attribute__((aligned(64)));
static int16_t half_b[WORDS] __attribute__((aligned(64)));
static int16_t product[WORDS] __attribute__((aligned(64)));
static int16_t midpoint[WORDS] __attribute__((aligned(64)));
static int16_t output[WORDS] __attribute__((aligned(64)));
static volatile uint64_t sink;

typedef void (*bench_fn)(void);

__attribute__((noinline))
static void control(void)
{
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(standard_a, coeff_a);
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(standard_b, coeff_b);
	gt32_tile4_basemul_scale_ff_aos_r1u_asm(product, standard_a, standard_b);
	gt32_tile4_inverse_all_pair_asm(midpoint, product);
	gt32_current_idft3_branch_row_asm(output, midpoint);
}

__attribute__((noinline))
static void candidate(void)
{
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(standard_a, coeff_a);
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(standard_b, coeff_b);
	gt32_tile4_n5_to_n32_half_asm(half_a, standard_a);
	gt32_tile4_n5_to_n32_half_asm(half_b, standard_b);
	gt32_n32_basemul_half_r1u_asm(product, half_a, half_b);
	gt32_n32_inverse_half_r1u_asm(output, product);
}

static uint64_t begin_tsc(void)
{
	_mm_lfence();
	return __rdtsc();
}

static uint64_t end_tsc(void)
{
	unsigned aux;
	uint64_t result = __rdtscp(&aux);
	_mm_lfence();
	return result;
}

static double measure(bench_fn fn, unsigned iterations)
{
	uint64_t begin = begin_tsc();
	for (unsigned i = 0; i < iterations; i++)
		fn();
	uint64_t end = end_tsc();
	sink += (uint16_t)output[iterations % WORDS];
	return (double)(end - begin) / iterations;
}

static int16_t centered(int32_t x)
{
	x %= 3457;
	if (x < 0)
		x += 3457;
	if (x > 1728)
		x -= 3457;
	return (int16_t)x;
}

int main(int argc, char **argv)
{
	unsigned iterations = argc > 1 ? (unsigned)strtoul(argv[1], 0, 10) : 5000U;
	_Alignas(64) int16_t expected[WORDS];
	cpu_set_t set;
	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof(set), &set) != 0)
		perror("sched_setaffinity");
	for (int i = 0; i < WORDS; i++) {
		coeff_a[i] = (int16_t)((i * 5 + 1) % 8 - 3);
		coeff_b[i] = (int16_t)((i * 7 + 3) % 8 - 3);
	}
	control();
	for (int i = 0; i < WORDS; i++)
		expected[i] = output[i];
	candidate();
	for (int i = 0; i < WORDS; i++)
		if (centered(expected[i]) != centered(output[i])) {
			fprintf(stderr, "whole endpoint mismatch at word %d\n", i);
			return 1;
		}
	for (unsigned i = 0; i < 2; i++) {
		(void)measure(control, 200);
		(void)measure(candidate, 200);
	}
	printf("META,experiment=GT-N5-HALF-TERMINAL-001,iterations=%u,samples=%u\n",
		iterations, SAMPLES);
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		double a, b;
		if ((sample & 1U) == 0) {
			a = measure(control, iterations);
			b = measure(candidate, iterations);
		} else {
			b = measure(candidate, iterations);
			a = measure(control, iterations);
		}
		printf("SAMPLE,whole,%u,%.6f,%.6f,%.6f\n", sample, a, b, b - a);
	}
	return sink == UINT64_MAX;
}
