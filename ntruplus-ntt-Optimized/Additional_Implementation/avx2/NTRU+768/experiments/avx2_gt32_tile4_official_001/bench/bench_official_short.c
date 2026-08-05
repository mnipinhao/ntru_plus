#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <x86intrin.h>

#include "tile4.h"

void poly_ntt(int16_t inout[GT32_TILE4_POLY_WORDS]);
void gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS]);

typedef void (*unary_fn)(int16_t *);
typedef void (*binary_fn)(int16_t *, const int16_t *);

static volatile uint64_t sink;
static volatile uint8_t eviction[64U * 1024U] __attribute__((aligned(64)));
static int cold_mode;

static void evict_l1(void)
{
	for (size_t i = 0; i < sizeof(eviction); i += 64U)
		eviction[i]++;
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

static double measure_unary(unary_fn function, int16_t *inout,
	unsigned iterations)
{
	if (cold_mode) {
		uint64_t elapsed = 0;
		for (unsigned i = 0; i < iterations; i++) {
			evict_l1();
			const uint64_t start = start_tsc();
			function(inout);
			elapsed += stop_tsc() - start;
		}
		sink += (uint16_t)inout[iterations & 767U];
		return (double)elapsed / iterations;
	}
	const uint64_t start = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		function(inout);
	const uint64_t stop = stop_tsc();
	sink += (uint16_t)inout[iterations & 767U];
	return (double)(stop - start) / iterations;
}

static double measure_binary(binary_fn function, int16_t *out,
	const int16_t *in, unsigned iterations)
{
	if (cold_mode) {
		uint64_t elapsed = 0;
		for (unsigned i = 0; i < iterations; i++) {
			evict_l1();
			const uint64_t start = start_tsc();
			function(out, in);
			elapsed += stop_tsc() - start;
		}
		sink += (uint16_t)out[iterations & 767U];
		return (double)elapsed / iterations;
	}
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

static double median(const double input[20])
{
	double values[20];
	memcpy(values, input, sizeof(values));
	qsort(values, 20, sizeof(values[0]), compare_double);
	return 0.5 * (values[9] + values[10]);
}

static void summarize(const double input[20], double *med, double *p25,
	double *p75, double *mad)
{
	double values[20];
	double deviations[20];
	memcpy(values, input, sizeof(values));
	qsort(values, 20, sizeof(values[0]), compare_double);
	*med = 0.5 * (values[9] + values[10]);
	*p25 = 0.5 * (values[4] + values[5]);
	*p75 = 0.5 * (values[14] + values[15]);
	for (unsigned i = 0; i < 20; i++)
		deviations[i] = values[i] > *med ? values[i] - *med : *med - values[i];
	*mad = median(deviations);
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc >= 2
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	cold_mode = argc >= 3 && strcmp(argv[2], "cold") == 0;
	int16_t input[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t official_work[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t alias_work[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t output[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	double official[20];
	double frozen[20];
	double tile4[20];
	double tile4_align32[20];
	double tile4_align64[20];
	double tile4_alias[20];
	cpu_set_t cpuset;

	CPU_ZERO(&cpuset);
	CPU_SET(1, &cpuset);
	if (sched_setaffinity(0, sizeof(cpuset), &cpuset) != 0)
		perror("sched_setaffinity");
	for (unsigned i = 0; i < GT32_TILE4_POLY_WORDS; i++)
		input[i] = (int16_t)((int)(i % 8U) - 3);
	memcpy(official_work, input, sizeof(input));
	(void)measure_unary(poly_ntt, official_work, 100);
	(void)measure_binary(
		gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm,
		output, input, 100);
	(void)measure_binary(gt32_tile4_forward_full_wide_raw_pair_asm,
		output, input, 100);

	for (unsigned sample = 0; sample < 20; sample++) {
		memcpy(official_work, input, sizeof(input));
		memcpy(alias_work, input, sizeof(input));
		if ((sample & 1U) == 0U) {
			official[sample] = measure_unary(poly_ntt, official_work, iterations);
			frozen[sample] = measure_binary(
				gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm,
				output, input, iterations);
			tile4[sample] = measure_binary(
				gt32_tile4_forward_full_wide_raw_pair_asm,
				output, input, iterations);
			tile4_align32[sample] = measure_binary(
				gt32_tile4_forward_full_wide_raw_pair_align32_asm,
				output, input, iterations);
			tile4_align64[sample] = measure_binary(
				gt32_tile4_forward_full_wide_raw_pair_align64_asm,
				output, input, iterations);
			tile4_alias[sample] = measure_binary(
				gt32_tile4_forward_full_wide_raw_pair_asm,
				alias_work, alias_work, iterations);
		} else {
			tile4_alias[sample] = measure_binary(
				gt32_tile4_forward_full_wide_raw_pair_asm,
				alias_work, alias_work, iterations);
			tile4_align64[sample] = measure_binary(
				gt32_tile4_forward_full_wide_raw_pair_align64_asm,
				output, input, iterations);
			tile4_align32[sample] = measure_binary(
				gt32_tile4_forward_full_wide_raw_pair_align32_asm,
				output, input, iterations);
			tile4[sample] = measure_binary(
				gt32_tile4_forward_full_wide_raw_pair_asm,
				output, input, iterations);
			frozen[sample] = measure_binary(
				gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm,
				output, input, iterations);
			official[sample] = measure_unary(poly_ntt, official_work, iterations);
		}
	}

	double official_median, official_p25, official_p75, official_mad;
	double frozen_median, frozen_p25, frozen_p75, frozen_mad;
	double tile4_median, tile4_p25, tile4_p75, tile4_mad;
	double align32_median, align32_p25, align32_p75, align32_mad;
	double align64_median, align64_p25, align64_p75, align64_mad;
	double alias_median, alias_p25, alias_p75, alias_mad;
	summarize(official, &official_median, &official_p25, &official_p75,
		&official_mad);
	summarize(frozen, &frozen_median, &frozen_p25, &frozen_p75, &frozen_mad);
	summarize(tile4, &tile4_median, &tile4_p25, &tile4_p75, &tile4_mad);
	summarize(tile4_align32, &align32_median, &align32_p25, &align32_p75,
		&align32_mad);
	summarize(tile4_align64, &align64_median, &align64_p25, &align64_p75,
		&align64_mad);
	summarize(tile4_alias, &alias_median, &alias_p25, &alias_p75, &alias_mad);
	printf("mode=%s iterations=%u samples=20 official=%.3f frozen_gt32=%.3f "
		"tile4_n5=%.3f tile4_vs_official=%.3f tile4_vs_official_pct=%.3f "
		"tile4_vs_frozen_pct=%.3f align32=%.3f align64=%.3f alias=%.3f "
		"official_p25=%.3f official_p75=%.3f official_mad=%.3f "
		"frozen_p25=%.3f frozen_p75=%.3f frozen_mad=%.3f "
		"tile4_p25=%.3f tile4_p75=%.3f tile4_mad=%.3f "
		"align32_p25=%.3f align32_p75=%.3f align32_mad=%.3f "
		"align64_p25=%.3f align64_p75=%.3f align64_mad=%.3f "
		"alias_p25=%.3f alias_p75=%.3f alias_mad=%.3f sink=%llu\n",
		cold_mode ? "cold-l1-evicted" : "warm", iterations,
		official_median, frozen_median, tile4_median,
		tile4_median - official_median,
		100.0 * (tile4_median / official_median - 1.0),
		100.0 * (tile4_median / frozen_median - 1.0),
		align32_median, align64_median, alias_median,
		official_p25, official_p75, official_mad,
		frozen_p25, frozen_p75, frozen_mad,
		tile4_p25, tile4_p75, tile4_mad,
		align32_p25, align32_p75, align32_mad,
		align64_p25, align64_p75, align64_mad,
		alias_p25, alias_p75, alias_mad,
		(unsigned long long)sink);
	return 0;
}
