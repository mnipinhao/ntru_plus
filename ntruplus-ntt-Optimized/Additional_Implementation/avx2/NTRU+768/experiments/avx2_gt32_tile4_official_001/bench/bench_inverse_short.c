#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <x86intrin.h>

#include "tile4.h"

typedef void (*inverse_fn)(int16_t *, const int16_t *);
typedef void (*basemul_fn)(int16_t *, const int16_t *, const int16_t *);
static volatile uint64_t sink;
void poly_crepmod3(int16_t *value);

static void tail_t8_then_crepmod3(int16_t *out, const int16_t *in)
{
	gt32_tile4_inverse_tail_t8_renamed_private_asm(out, in);
	poly_crepmod3(out);
}

static void full_inverse_candidate(int16_t *out, const int16_t *in)
{
	int16_t scratch[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	gt32_tile4_inverse_all_pair_asm(scratch, in);
	gt32_tile4_inverse_tail_intrinsic_rminus1(out, scratch);
}

static void full_inverse_asm_candidate(int16_t *out, const int16_t *in)
{
	int16_t scratch[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	gt32_tile4_inverse_all_pair_asm(scratch, in);
	gt32_tile4_inverse_tail_asm_rminus1(out, scratch);
}

static void full_inverse_champion(int16_t *out, const int16_t *in)
{
	int16_t scratch[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	gt32_tile4_inverse_all_pair_asm(scratch, in);
	gt32_tile4_inverse_tail_champion_private_asm(out, scratch);
}

static void full_inverse_t10(int16_t *out, const int16_t *in)
{
	int16_t scratch[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	gt32_tile4_inverse_all_pair_asm(scratch, in);
	gt32_tile4_inverse_tail_t10_crepmod3_asm(out, scratch);
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

static double measure_pipeline(basemul_fn basemul, inverse_fn inverse,
	int16_t *out, int16_t *scratch, const int16_t *a, const int16_t *b,
	unsigned iterations)
{
	const uint64_t start = start_tsc();
	for (unsigned i = 0; i < iterations; i++) {
		basemul(scratch, a, b);
		inverse(out, scratch);
	}
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
	int16_t frequency_b[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t private_frequency[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t scratch[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t output[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	double i0[20];
	double i1[20];
	double i2[20];
	double i2_parallel[20];
	double d0[20];
	double d2[20];
	double d2_parallel[20];
	double tail[20];
	double tail_asm[20];
	double tail_t1[20], tail_t2[20], tail_t3[20], tail_t3_relaxed[20];
	double tail_t4[20], tail_champion[20];
	double tail_t5[20], tail_t6[20], tail_t7[20], tail_t8[20];
	double tail_t8_crep[20], tail_t10[20], d0_full_t10[20];
	double tail_t9[20];
	double full_inverse[20];
	double full_inverse_asm[20];
	double d0_full[20];
	double d0_full_asm[20];
	double d0_full_champion[20];
	cpu_set_t cpuset;

	CPU_ZERO(&cpuset);
	CPU_SET(1, &cpuset);
	if (sched_setaffinity(0, sizeof(cpuset), &cpuset) != 0)
		perror("sched_setaffinity");
	for (unsigned i = 0; i < GT32_TILE4_POLY_WORDS; i++)
		coefficients[i] = (int16_t)((int)(i % 8U) - 3);
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(frequency, coefficients);
	for (unsigned i = 0; i < GT32_TILE4_POLY_WORDS; i++)
		coefficients[i] = (int16_t)((int)((3U * i + 1U) % 8U) - 3);
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(frequency_b, coefficients);
	gt32_tile4_basemul_scale_soa_private_asm(private_frequency,
		frequency, frequency_b);
	gt32_tile4_basemul_b2_asm(scratch, frequency, frequency_b);
	gt32_tile4_inverse_all_pair_asm(coefficients, scratch);
	(void)measure(gt32_tile4_inverse_all_asm, output, frequency, 100);
	(void)measure(gt32_tile4_inverse_all_pair_asm, output, frequency, 100);
	(void)measure(gt32_tile4_inverse_soa_private_asm, output,
		private_frequency, 100);
	(void)measure(gt32_tile4_inverse_soa_private_parallel_asm, output,
		private_frequency, 100);
	(void)measure(gt32_tile4_inverse_tail_intrinsic_rminus1, output,
		coefficients, 100);
	(void)measure(gt32_tile4_inverse_tail_asm_rminus1, output,
		coefficients, 100);
	(void)measure(gt32_tile4_inverse_tail_champion_private_asm, output,
		coefficients, 100);
	(void)measure(full_inverse_candidate, output, scratch, 100);
	(void)measure(full_inverse_asm_candidate, output, scratch, 100);

	for (unsigned sample = 0; sample < 20; sample++) {
		if ((sample & 1U) == 0U) {
			i0[sample] = measure(gt32_tile4_inverse_all_asm,
				output, frequency, iterations);
			i1[sample] = measure(gt32_tile4_inverse_all_pair_asm,
				output, frequency, iterations);
			i2[sample] = measure(gt32_tile4_inverse_soa_private_asm,
				output, private_frequency, iterations);
			i2_parallel[sample] = measure(
				gt32_tile4_inverse_soa_private_parallel_asm,
				output, private_frequency, iterations);
			d0[sample] = measure_pipeline(gt32_tile4_basemul_b2_asm,
				gt32_tile4_inverse_all_pair_asm, output, scratch,
				frequency, frequency_b, iterations);
			d2[sample] = measure_pipeline(
				gt32_tile4_basemul_scale_soa_private_asm,
				gt32_tile4_inverse_soa_private_asm, output, scratch,
				frequency, frequency_b, iterations);
			d2_parallel[sample] = measure_pipeline(
				gt32_tile4_basemul_scale_soa_private_asm,
				gt32_tile4_inverse_soa_private_parallel_asm,
				output, scratch, frequency, frequency_b, iterations);
			tail[sample] = measure(gt32_tile4_inverse_tail_intrinsic_rminus1,
				output, coefficients, iterations);
			tail_asm[sample] = measure(gt32_tile4_inverse_tail_asm_rminus1,
				output, coefficients, iterations);
			tail_t1[sample] = measure(gt32_tile4_inverse_tail_t1_relaxed_asm,
				output, coefficients, iterations);
			tail_t2[sample] = measure(gt32_tile4_inverse_tail_t2_one_mont_asm,
				output, coefficients, iterations);
			tail_t3[sample] = measure(gt32_tile4_inverse_tail_t3_reduced_center_asm,
				output, coefficients, iterations);
			tail_t4[sample] = measure(gt32_tile4_inverse_tail_t4_matrix3_asm,
				output, coefficients, iterations);
			tail_t3_relaxed[sample] = measure(
				gt32_tile4_inverse_tail_t3_relaxed_control_asm,
				output, coefficients, iterations);
			tail_champion[sample] = measure(
				gt32_tile4_inverse_tail_champion_private_asm,
				output, coefficients, iterations);
			tail_t5[sample] = measure(gt32_tile4_inverse_tail_t5_private_asm,
				output, coefficients, iterations);
			tail_t6[sample] = measure(gt32_tile4_inverse_tail_t6_dual_private_asm,
				output, coefficients, iterations);
			tail_t7[sample] = measure(gt32_tile4_inverse_tail_t7_triple_private_asm,
				output, coefficients, iterations);
			tail_t8[sample] = measure(gt32_tile4_inverse_tail_t8_renamed_private_asm,
				output, coefficients, iterations);
			tail_t8_crep[sample] = measure(tail_t8_then_crepmod3,
				output, coefficients, iterations);
			tail_t10[sample] = measure(gt32_tile4_inverse_tail_t10_crepmod3_asm,
				output, coefficients, iterations);
			tail_t9[sample] = measure(gt32_tile4_inverse_tail_t9_isolated_private_asm,
				output, coefficients, iterations);
			full_inverse[sample] = measure(full_inverse_candidate,
				output, scratch, iterations);
			full_inverse_asm[sample] = measure(full_inverse_asm_candidate,
				output, scratch, iterations);
			d0_full[sample] = measure_pipeline(gt32_tile4_basemul_b2_asm,
				full_inverse_candidate, output, scratch,
				frequency, frequency_b, iterations);
			d0_full_asm[sample] = measure_pipeline(gt32_tile4_basemul_b2_asm,
				full_inverse_asm_candidate, output, scratch,
				frequency, frequency_b, iterations);
			d0_full_champion[sample] = measure_pipeline(gt32_tile4_basemul_b2_asm,
				full_inverse_champion, output, scratch,
				frequency, frequency_b, iterations);
			d0_full_t10[sample] = measure_pipeline(gt32_tile4_basemul_b2_asm,
				full_inverse_t10, output, scratch,
				frequency, frequency_b, iterations);
		} else {
			d0_full_t10[sample] = measure_pipeline(gt32_tile4_basemul_b2_asm,
				full_inverse_t10, output, scratch,
				frequency, frequency_b, iterations);
			d0_full_champion[sample] = measure_pipeline(gt32_tile4_basemul_b2_asm,
				full_inverse_champion, output, scratch,
				frequency, frequency_b, iterations);
			d0_full_asm[sample] = measure_pipeline(gt32_tile4_basemul_b2_asm,
				full_inverse_asm_candidate, output, scratch,
				frequency, frequency_b, iterations);
			d0_full[sample] = measure_pipeline(gt32_tile4_basemul_b2_asm,
				full_inverse_candidate, output, scratch,
				frequency, frequency_b, iterations);
			full_inverse[sample] = measure(full_inverse_candidate,
				output, scratch, iterations);
			full_inverse_asm[sample] = measure(full_inverse_asm_candidate,
				output, scratch, iterations);
			tail[sample] = measure(gt32_tile4_inverse_tail_intrinsic_rminus1,
				output, coefficients, iterations);
			tail_asm[sample] = measure(gt32_tile4_inverse_tail_asm_rminus1,
				output, coefficients, iterations);
			tail_champion[sample] = measure(
				gt32_tile4_inverse_tail_champion_private_asm,
				output, coefficients, iterations);
			tail_t6[sample] = measure(gt32_tile4_inverse_tail_t6_dual_private_asm,
				output, coefficients, iterations);
			tail_t7[sample] = measure(gt32_tile4_inverse_tail_t7_triple_private_asm,
				output, coefficients, iterations);
			tail_t8[sample] = measure(gt32_tile4_inverse_tail_t8_renamed_private_asm,
				output, coefficients, iterations);
			tail_t10[sample] = measure(gt32_tile4_inverse_tail_t10_crepmod3_asm,
				output, coefficients, iterations);
			tail_t9[sample] = measure(gt32_tile4_inverse_tail_t9_isolated_private_asm,
				output, coefficients, iterations);
			tail_t8_crep[sample] = measure(tail_t8_then_crepmod3,
				output, coefficients, iterations);
			tail_t5[sample] = measure(gt32_tile4_inverse_tail_t5_private_asm,
				output, coefficients, iterations);
			tail_t3_relaxed[sample] = measure(
				gt32_tile4_inverse_tail_t3_relaxed_control_asm,
				output, coefficients, iterations);
			tail_t4[sample] = measure(gt32_tile4_inverse_tail_t4_matrix3_asm,
				output, coefficients, iterations);
			tail_t3[sample] = measure(gt32_tile4_inverse_tail_t3_reduced_center_asm,
				output, coefficients, iterations);
			tail_t2[sample] = measure(gt32_tile4_inverse_tail_t2_one_mont_asm,
				output, coefficients, iterations);
			tail_t1[sample] = measure(gt32_tile4_inverse_tail_t1_relaxed_asm,
				output, coefficients, iterations);
			d2_parallel[sample] = measure_pipeline(
				gt32_tile4_basemul_scale_soa_private_asm,
				gt32_tile4_inverse_soa_private_parallel_asm,
				output, scratch, frequency, frequency_b, iterations);
			d2[sample] = measure_pipeline(
				gt32_tile4_basemul_scale_soa_private_asm,
				gt32_tile4_inverse_soa_private_asm, output, scratch,
				frequency, frequency_b, iterations);
			d0[sample] = measure_pipeline(gt32_tile4_basemul_b2_asm,
				gt32_tile4_inverse_all_pair_asm, output, scratch,
				frequency, frequency_b, iterations);
			i2[sample] = measure(gt32_tile4_inverse_soa_private_asm,
				output, private_frequency, iterations);
			i2_parallel[sample] = measure(
				gt32_tile4_inverse_soa_private_parallel_asm,
				output, private_frequency, iterations);
			i1[sample] = measure(gt32_tile4_inverse_all_pair_asm,
				output, frequency, iterations);
			i0[sample] = measure(gt32_tile4_inverse_all_asm,
				output, frequency, iterations);
		}
	}

	const double i0_median = median(i0);
	const double i1_median = median(i1);
	const double i2_median = median(i2);
	const double i2_parallel_median = median(i2_parallel);
	const double d0_median = median(d0);
	const double d2_median = median(d2);
	const double d2_parallel_median = median(d2_parallel);
	const double tail_median = median(tail);
	const double tail_asm_median = median(tail_asm);
	const double tail_t1_median = median(tail_t1);
	const double tail_t2_median = median(tail_t2);
	const double tail_t3_median = median(tail_t3);
	const double tail_t3_relaxed_median = median(tail_t3_relaxed);
	const double tail_t4_median = median(tail_t4);
	const double tail_champion_median = median(tail_champion);
	const double tail_t5_median = median(tail_t5);
	const double tail_t6_median = median(tail_t6);
	const double tail_t7_median = median(tail_t7);
	const double tail_t8_median = median(tail_t8);
	const double tail_t8_crep_median = median(tail_t8_crep);
	const double tail_t10_median = median(tail_t10);
	const double tail_t9_median = median(tail_t9);
	const double full_inverse_median = median(full_inverse);
	const double full_inverse_asm_median = median(full_inverse_asm);
	const double d0_full_median = median(d0_full);
	const double d0_full_asm_median = median(d0_full_asm);
	const double d0_full_champion_median = median(d0_full_champion);
	const double d0_full_t10_median = median(d0_full_t10);
	printf("iterations=%u samples=20 inverse_i0=%.3f inverse_i1_pair=%.3f "
		"inverse_i2_private=%.3f inverse_i2_parallel=%.3f "
		"d0_b2_i1=%.3f d2_b2s_i2=%.3f d2_parallel=%.3f "
		"tail=%.3f tail_asm=%.3f full_inverse=%.3f full_inverse_asm=%.3f "
		"t1=%.3f t2=%.3f t3=%.3f t3_relaxed=%.3f t4=%.3f champion=%.3f "
		"t5=%.3f t6=%.3f t7=%.3f t8=%.3f t9=%.3f t8_crep=%.3f t10=%.3f "
		"d0_full=%.3f d0_full_asm=%.3f "
		"d0_full_champion=%.3f d0_full_t10=%.3f "
		"d2_parallel_saving=%.3f saving=%.3f saving_pct=%.3f sink=%llu\n",
		iterations, i0_median, i1_median, i2_median, i2_parallel_median,
		d0_median, d2_median, d2_parallel_median, tail_median,
		tail_asm_median, full_inverse_median, full_inverse_asm_median,
		tail_t1_median, tail_t2_median, tail_t3_median,
		tail_t3_relaxed_median, tail_t4_median,
		tail_champion_median, tail_t5_median, tail_t6_median, tail_t7_median,
		tail_t8_median, tail_t9_median, tail_t8_crep_median, tail_t10_median,
		d0_full_median, d0_full_asm_median,
		d0_full_champion_median, d0_full_t10_median,
		d0_median - d2_parallel_median, i0_median - i1_median,
		100.0 * (1.0 - i1_median / i0_median),
		(unsigned long long)sink);
	return 0;
}
