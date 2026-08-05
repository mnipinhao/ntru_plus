#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <x86intrin.h>

#include "tile4.h"

typedef void (*inverse_fn)(int16_t *, const int16_t *);
static volatile uint64_t sink;

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

static double measure(inverse_fn function, int16_t *out, const int16_t *in,
	unsigned iterations)
{
	const uint64_t start = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		function(out, in);
	const uint64_t stop = stop_tsc();
	sink += (uint16_t)out[iterations & 767U];
	return (double)(stop - start) / iterations;
}

static int compare_double(const void *left, const void *right)
{
	const double a = *(const double *)left;
	const double b = *(const double *)right;
	return (a > b) - (a < b);
}

static double median(double values[20])
{
	qsort(values, 20, sizeof(values[0]), compare_double);
	return 0.5 * (values[9] + values[10]);
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc >= 2
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	int16_t coefficients[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t frequency[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t output[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	double i0[20];
	double i1[20];
	cpu_set_t cpuset;

	CPU_ZERO(&cpuset);
	CPU_SET(1, &cpuset);
	if (sched_setaffinity(0, sizeof(cpuset), &cpuset) != 0)
		perror("sched_setaffinity");
	for (unsigned i = 0; i < GT32_TILE4_POLY_WORDS; i++)
		coefficients[i] = (int16_t)((int)(i % 8U) - 3);
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(frequency, coefficients);
	(void)measure(gt32_tile4_inverse_all_asm, output, frequency, 100);
	(void)measure(gt32_tile4_inverse_all_pair_asm, output, frequency, 100);

	for (unsigned sample = 0; sample < 20; sample++) {
		if ((sample & 1U) == 0U) {
			i0[sample] = measure(gt32_tile4_inverse_all_asm,
				output, frequency, iterations);
			i1[sample] = measure(gt32_tile4_inverse_all_pair_asm,
				output, frequency, iterations);
		} else {
			i1[sample] = measure(gt32_tile4_inverse_all_pair_asm,
				output, frequency, iterations);
			i0[sample] = measure(gt32_tile4_inverse_all_asm,
				output, frequency, iterations);
		}
	}

	const double i0_median = median(i0);
	const double i1_median = median(i1);
	printf("iterations=%u samples=20 inverse_i0=%.3f inverse_i1_pair=%.3f "
		"saving=%.3f saving_pct=%.3f sink=%llu\n",
		iterations, i0_median, i1_median, i0_median - i1_median,
		100.0 * (1.0 - i1_median / i0_median),
		(unsigned long long)sink);
	return 0;
}
