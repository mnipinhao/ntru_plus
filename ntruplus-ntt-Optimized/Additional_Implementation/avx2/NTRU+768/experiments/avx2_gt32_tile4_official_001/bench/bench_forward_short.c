#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <x86intrin.h>

#include "tile4.h"

void gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);

typedef void (*forward_fn)(int16_t *, const int16_t *);

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

static double measure(forward_fn function, int16_t *out, const int16_t *in,
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

static double median(double value[20])
{
	qsort(value, 20, sizeof(value[0]), compare_double);
	return 0.5 * (value[9] + value[10]);
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc == 2 ? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	int16_t input[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t output_a[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t output_b[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	double frozen[20];
	double tile4[20];
	double tile4_fixed_pair[20];
	double tile4_fixed_pair_wide[20];
	double tile4_wide_raw_pair[20];
	double frontend[20];
	double frontend_raw[20];
	double frontend_fixed[20];
	double frontend_wide[20];
	double core[20];
	double core_parallel[20];
	double core_pair[20];
	cpu_set_t cpuset;

	CPU_ZERO(&cpuset);
	CPU_SET(1, &cpuset);
	if (sched_setaffinity(0, sizeof(cpuset), &cpuset) != 0)
		perror("sched_setaffinity");
	for (unsigned i = 0; i < GT32_TILE4_POLY_WORDS; i++)
		input[i] = (int16_t)((int)(i % 8U) - 3);
	for (unsigned warm = 0; warm < 2; warm++) {
		(void)measure(gt32_tile4_forward_full_candidate, output_a, input, 100);
		(void)measure(
			gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm,
			output_b, input, 100);
	}
	for (unsigned sample = 0; sample < 20; sample++) {
		if ((sample & 1U) == 0U) {
			frozen[sample] = measure(
				gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm,
				output_b, input, iterations);
			tile4[sample] = measure(gt32_tile4_forward_full_candidate,
				output_a, input, iterations);
			tile4_fixed_pair[sample] = measure(
				gt32_tile4_forward_full_fixed_pair_asm, output_a, input, iterations);
			tile4_fixed_pair_wide[sample] = measure(
				gt32_tile4_forward_full_fixed_pair_wide_load_asm,
				output_a, input, iterations);
			tile4_wide_raw_pair[sample] = measure(
				gt32_tile4_forward_full_wide_raw_pair_asm,
				output_a, input, iterations);
			frontend[sample] = measure(gt32_tile4_frontend_asm,
				output_a, input, iterations);
			frontend_raw[sample] = measure(gt32_tile4_frontend_raw_asm,
				output_a, input, iterations);
			frontend_fixed[sample] = measure(gt32_tile4_frontend_fixed_raw_asm,
				output_a, input, iterations);
			frontend_wide[sample] = measure(gt32_tile4_frontend_wide_raw_asm,
				output_a, input, iterations);
			core[sample] = measure(gt32_tile4_forward_all_serial_asm,
				output_a, input, iterations);
			core_parallel[sample] = measure(gt32_tile4_forward_all_parallel_asm,
				output_a, input, iterations);
			core_pair[sample] = measure(gt32_tile4_forward_all_pair_asm,
				output_a, input, iterations);
		} else {
			frontend_wide[sample] = measure(gt32_tile4_frontend_wide_raw_asm,
				output_a, input, iterations);
			tile4_fixed_pair_wide[sample] = measure(
				gt32_tile4_forward_full_fixed_pair_wide_load_asm,
				output_a, input, iterations);
			tile4_wide_raw_pair[sample] = measure(
				gt32_tile4_forward_full_wide_raw_pair_asm,
				output_a, input, iterations);
			core_pair[sample] = measure(gt32_tile4_forward_all_pair_asm,
				output_a, input, iterations);
			core_parallel[sample] = measure(gt32_tile4_forward_all_parallel_asm,
				output_a, input, iterations);
			core[sample] = measure(gt32_tile4_forward_all_serial_asm,
				output_a, input, iterations);
			frontend[sample] = measure(gt32_tile4_frontend_asm,
				output_a, input, iterations);
			frontend_raw[sample] = measure(gt32_tile4_frontend_raw_asm,
				output_a, input, iterations);
			frontend_fixed[sample] = measure(gt32_tile4_frontend_fixed_raw_asm,
				output_a, input, iterations);
			tile4[sample] = measure(gt32_tile4_forward_full_candidate,
				output_a, input, iterations);
			tile4_fixed_pair[sample] = measure(
				gt32_tile4_forward_full_fixed_pair_asm, output_a, input, iterations);
			frozen[sample] = measure(
				gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm,
				output_b, input, iterations);
		}
	}
	const double frozen_median = median(frozen);
	const double tile4_median = median(tile4);
	const double tile4_fixed_pair_median = median(tile4_fixed_pair);
	const double tile4_fixed_pair_wide_median = median(tile4_fixed_pair_wide);
	const double tile4_wide_raw_pair_median = median(tile4_wide_raw_pair);
	const double frontend_median = median(frontend);
	const double frontend_raw_median = median(frontend_raw);
	const double frontend_fixed_median = median(frontend_fixed);
	const double frontend_wide_median = median(frontend_wide);
	const double core_median = median(core);
	const double core_parallel_median = median(core_parallel);
	const double core_pair_median = median(core_pair);
	printf("iterations=%u samples=20 frozen_gt32=%.3f tile4_full=%.3f tile4_full_fixed_pair=%.3f tile4_full_fixed_pair_wide=%.3f tile4_full_wide_raw_pair=%.3f tile4_frontend=%.3f tile4_frontend_raw=%.3f tile4_frontend_fixed=%.3f tile4_frontend_wide=%.3f tile4_core_serial=%.3f tile4_core_parallel=%.3f tile4_core_pair=%.3f reconstructed_fixed_pair=%.3f delta_wide=%.3f delta_wide_pct=%.3f sink=%llu\n",
		iterations, frozen_median, tile4_median, tile4_fixed_pair_median,
		tile4_fixed_pair_wide_median, tile4_wide_raw_pair_median,
		frontend_median, frontend_raw_median, frontend_fixed_median,
		frontend_wide_median, core_median,
		core_parallel_median, core_pair_median,
		frontend_fixed_median + core_pair_median,
		tile4_wide_raw_pair_median - frozen_median,
		100.0 * (tile4_wide_raw_pair_median / frozen_median - 1.0),
		(unsigned long long)sink);
	return 0;
}
