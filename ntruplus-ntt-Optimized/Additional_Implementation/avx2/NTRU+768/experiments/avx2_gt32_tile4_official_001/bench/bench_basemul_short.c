#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <x86intrin.h>

#include "tile4.h"

void poly_basemul(int16_t *out, const int16_t *a, const int16_t *b);
void gt_basemul_native_rminus1_asm_avx2(int16_t *out,
	const int16_t *a, const int16_t *b);

typedef void (*basemul_fn)(int16_t *, const int16_t *, const int16_t *);
static volatile uint64_t sink;
static int16_t private_product[GT32_TILE4_POLY_WORDS]
	__attribute__((aligned(32)));

static void centered_soa_inverse(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	gt32_tile4_basemul_scale_soa_private_asm(private_product, a, b);
	gt32_tile4_inverse_soa_private_parallel_asm(out, private_product);
}

static void raw_soa_inverse(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	gt32_tile4_basemul_raw_soa_private_asm(private_product, a, b);
	gt32_tile4_inverse_soa_private_parallel_asm(out, private_product);
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

static double measure(basemul_fn function, int16_t *out, const int16_t *a,
	const int16_t *b, unsigned iterations)
{
	const uint64_t start = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		function(out, a, b);
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
	int16_t coefficients_a[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t coefficients_b[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t a[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t b[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	int16_t out[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	double official[20], frozen[20], b0[20], b1[20], k1[20], k2[20], k2_asm[20];
	double b2[20], b3[20], b4b[20];
	double general[20], private_soa[20], raw_soa[20], raw_aos[20], c3center[20];
	double c3center_late[20];
	double centered_pipeline[20], raw_pipeline[20];
	cpu_set_t cpuset;

	CPU_ZERO(&cpuset);
	CPU_SET(1, &cpuset);
	if (sched_setaffinity(0, sizeof(cpuset), &cpuset) != 0)
		perror("sched_setaffinity");
	for (unsigned i = 0; i < GT32_TILE4_POLY_WORDS; i++) {
		coefficients_a[i] = (int16_t)((int)(i % 8U) - 3);
		coefficients_b[i] = (int16_t)((int)((3U * i + 1U) % 8U) - 3);
	}
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(a, coefficients_a);
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(b, coefficients_b);
	(void)measure(poly_basemul, out, a, b, 100);
	(void)measure(gt_basemul_native_rminus1_asm_avx2, out, a, b, 100);
	(void)measure(gt32_tile4_basemul_b0, out, a, b, 10);
	(void)measure(gt32_tile4_basemul_b1, out, a, b, 100);
	(void)measure(gt32_tile4_basemul_k1_intrinsic, out, a, b, 100);
	(void)measure(gt32_tile4_basemul_k2_intrinsic, out, a, b, 100);
	(void)measure(gt32_tile4_basemul_k2_asm, out, a, b, 100);
	(void)measure(gt32_tile4_basemul_b2_asm, out, a, b, 100);
	(void)measure(gt32_tile4_basemul_b3_late_asm, out, a, b, 100);
	(void)measure(gt32_tile4_basemul_b4b_partial_asm, out, a, b, 100);
	(void)measure(gt32_tile4_basemul_general_b2_asm, out, a, b, 100);
	(void)measure(gt32_tile4_basemul_scale_soa_private_asm, out, a, b, 100);
	(void)measure(gt32_tile4_basemul_raw_soa_private_asm, out, a, b, 100);
	(void)measure(gt32_tile4_basemul_raw_aos_private_asm, out, a, b, 100);
	(void)measure(gt32_tile4_basemul_c3center_aos_private_asm,
		out, a, b, 100);
	(void)measure(gt32_tile4_basemul_c3center_late_aos_private_asm,
		out, a, b, 100);
	(void)measure(centered_soa_inverse, out, a, b, 100);
	(void)measure(raw_soa_inverse, out, a, b, 100);

	for (unsigned sample = 0; sample < 20; sample++) {
		if ((sample & 1U) == 0U) {
			official[sample] = measure(poly_basemul, out, a, b, iterations);
			frozen[sample] = measure(gt_basemul_native_rminus1_asm_avx2,
				out, a, b, iterations);
			b0[sample] = measure(gt32_tile4_basemul_b0, out, a, b, iterations);
			b1[sample] = measure(gt32_tile4_basemul_b1, out, a, b, iterations);
			k1[sample] = measure(gt32_tile4_basemul_k1_intrinsic,
				out, a, b, iterations);
			k2[sample] = measure(gt32_tile4_basemul_k2_intrinsic,
				out, a, b, iterations);
			k2_asm[sample] = measure(gt32_tile4_basemul_k2_asm,
				out, a, b, iterations);
			b2[sample] = measure(gt32_tile4_basemul_b2_asm, out, a, b, iterations);
			b3[sample] = measure(gt32_tile4_basemul_b3_late_asm,
				out, a, b, iterations);
			b4b[sample] = measure(gt32_tile4_basemul_b4b_partial_asm,
				out, a, b, iterations);
			general[sample] = measure(gt32_tile4_basemul_general_b2_asm,
				out, a, b, iterations);
			private_soa[sample] = measure(
				gt32_tile4_basemul_scale_soa_private_asm,
				out, a, b, iterations);
			raw_soa[sample] = measure(gt32_tile4_basemul_raw_soa_private_asm,
				out, a, b, iterations);
			raw_aos[sample] = measure(gt32_tile4_basemul_raw_aos_private_asm,
				out, a, b, iterations);
			c3center[sample] = measure(
				gt32_tile4_basemul_c3center_aos_private_asm,
				out, a, b, iterations);
			c3center_late[sample] = measure(
				gt32_tile4_basemul_c3center_late_aos_private_asm,
				out, a, b, iterations);
			centered_pipeline[sample] = measure(centered_soa_inverse,
				out, a, b, iterations);
			raw_pipeline[sample] = measure(raw_soa_inverse,
				out, a, b, iterations);
		} else {
			c3center_late[sample] = measure(
				gt32_tile4_basemul_c3center_late_aos_private_asm,
				out, a, b, iterations);
			c3center[sample] = measure(
				gt32_tile4_basemul_c3center_aos_private_asm,
				out, a, b, iterations);
			raw_aos[sample] = measure(gt32_tile4_basemul_raw_aos_private_asm,
				out, a, b, iterations);
			raw_pipeline[sample] = measure(raw_soa_inverse,
				out, a, b, iterations);
			centered_pipeline[sample] = measure(centered_soa_inverse,
				out, a, b, iterations);
			raw_soa[sample] = measure(gt32_tile4_basemul_raw_soa_private_asm,
				out, a, b, iterations);
			private_soa[sample] = measure(
				gt32_tile4_basemul_scale_soa_private_asm,
				out, a, b, iterations);
			general[sample] = measure(gt32_tile4_basemul_general_b2_asm,
				out, a, b, iterations);
			b4b[sample] = measure(gt32_tile4_basemul_b4b_partial_asm,
				out, a, b, iterations);
			b3[sample] = measure(gt32_tile4_basemul_b3_late_asm,
				out, a, b, iterations);
			b2[sample] = measure(gt32_tile4_basemul_b2_asm, out, a, b, iterations);
			k2_asm[sample] = measure(gt32_tile4_basemul_k2_asm,
				out, a, b, iterations);
			k2[sample] = measure(gt32_tile4_basemul_k2_intrinsic,
				out, a, b, iterations);
			k1[sample] = measure(gt32_tile4_basemul_k1_intrinsic,
				out, a, b, iterations);
			b1[sample] = measure(gt32_tile4_basemul_b1, out, a, b, iterations);
			b0[sample] = measure(gt32_tile4_basemul_b0, out, a, b, iterations);
			frozen[sample] = measure(gt_basemul_native_rminus1_asm_avx2,
				out, a, b, iterations);
			official[sample] = measure(poly_basemul, out, a, b, iterations);
		}
	}

	const double official_median = median(official);
	const double frozen_median = median(frozen);
	const double b0_median = median(b0);
	const double b1_median = median(b1);
	const double k1_median = median(k1);
	const double k2_median = median(k2);
	const double k2_asm_median = median(k2_asm);
	const double b2_median = median(b2);
	const double b3_median = median(b3);
	const double b4b_median = median(b4b);
	const double general_median = median(general);
	const double private_median = median(private_soa);
	const double raw_median = median(raw_soa);
	const double raw_aos_median = median(raw_aos);
	const double c3center_median = median(c3center);
	const double c3center_late_median = median(c3center_late);
	const double centered_pipeline_median = median(centered_pipeline);
	const double raw_pipeline_median = median(raw_pipeline);
	printf("iterations=%u samples=20 official=%.3f frozen_rminus1=%.3f "
		"tile4_b0=%.3f tile4_b1=%.3f tile4_k1=%.3f tile4_k2=%.3f "
		"tile4_k2_asm=%.3f "
		"tile4_b2_asm=%.3f tile4_b3_late=%.3f "
		"tile4_b4b_partial=%.3f "
		"general_e0=%.3f private_soa_e_minus1=%.3f raw_soa_e_minus1=%.3f "
		"raw_aos_e_minus1=%.3f c3center_aos_e_minus1=%.3f "
		"c3center_late_aos_e_minus1=%.3f "
		"b2_vs_official=%.3f b2_vs_official_pct=%.3f sink=%llu\n",
		iterations, official_median, frozen_median, b0_median, b1_median,
		k1_median, k2_median, k2_asm_median, b2_median, b3_median, b4b_median,
		general_median, private_median, raw_median, raw_aos_median,
		c3center_median, c3center_late_median,
		b2_median - official_median,
		100.0 * (b2_median / official_median - 1.0),
		(unsigned long long)sink);
	printf("private_bm_i32 centered=%.3f raw=%.3f saving=%+.3f\n",
		centered_pipeline_median, raw_pipeline_median,
		centered_pipeline_median - raw_pipeline_median);
	return 0;
}
