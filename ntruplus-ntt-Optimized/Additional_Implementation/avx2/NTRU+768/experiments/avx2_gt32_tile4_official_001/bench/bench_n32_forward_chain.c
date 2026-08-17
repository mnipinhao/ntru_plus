#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <x86intrin.h>

#include "tile4.h"

#define Q 3457
#define WORDS 768
#define SAMPLES 20U

static int16_t coefficients_a[WORDS] __attribute__((aligned(64)));
static int16_t coefficients_b[WORDS] __attribute__((aligned(64)));
static int16_t standard_a[WORDS] __attribute__((aligned(64)));
static int16_t standard_b[WORDS] __attribute__((aligned(64)));
static int16_t half_a[WORDS] __attribute__((aligned(64)));
static int16_t half_b[WORDS] __attribute__((aligned(64)));
static int16_t standard_product[WORDS] __attribute__((aligned(64)));
static int16_t half_product[WORDS] __attribute__((aligned(64)));
static int16_t current_midpoint[WORDS] __attribute__((aligned(64)));
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

static void half_to_standard(int16_t standard[WORDS], const int16_t half[WORDS])
{
	for (int branch = 0; branch < 2; branch++) {
		for (int group = 0; group < 8; group++) {
			for (int slot = 0; slot < 3; slot++) {
				const int hv = (branch * 8 + group) * 3 + slot;
				for (int qword = 0; qword < 4; qword++) {
					const int k3 = physical_k3(slot, qword);
					const int sv = (k3 * 2 + branch) * 8 + group;
					for (int degree = 0; degree < 4; degree++) {
						standard[16 * sv + 4 * qword + degree] =
							half[16 * hv + 4 * qword + degree];
					}
				}
			}
		}
	}
}

static int16_t centered_mod(int32_t value)
{
	value %= Q;
	if (value < 0)
		value += Q;
	if (value > Q / 2)
		value -= Q;
	return (int16_t)value;
}

static int equal_mod_q(const int16_t a[WORDS], const int16_t b[WORDS])
{
	for (int index = 0; index < WORDS; index++) {
		if (centered_mod(a[index]) != centered_mod(b[index]))
			return 0;
	}
	return 1;
}

__attribute__((noinline))
static void current_forward_one(void)
{
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(output, coefficients_a);
}

__attribute__((noinline))
static void n32_forward_raw_one(void)
{
	gt32_n32_forward_half_raw_asm(output, coefficients_a);
}

__attribute__((noinline))
static void n32_forward_centered_one(void)
{
	gt32_n32_forward_half_centered_asm(output, coefficients_a);
}

__attribute__((noinline))
static void n32_forward_conjugated_one(void)
{
	gt32_n32_forward_half_conjugated_asm(output, coefficients_a);
}

__attribute__((noinline))
static void current_forward_two(void)
{
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(standard_a, coefficients_a);
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(standard_b, coefficients_b);
}

__attribute__((noinline))
static void n32_forward_centered_two(void)
{
	gt32_n32_forward_half_centered_asm(half_a, coefficients_a);
	gt32_n32_forward_half_centered_asm(half_b, coefficients_b);
}

__attribute__((noinline))
static void n32_forward_conjugated_two(void)
{
	gt32_n32_forward_half_conjugated_asm(half_a, coefficients_a);
	gt32_n32_forward_half_conjugated_asm(half_b, coefficients_b);
}

__attribute__((noinline))
static void current_basemul(void)
{
	gt32_tile4_basemul_scale_ff_aos_r1u_asm(
		output, standard_a, standard_b);
}

__attribute__((noinline))
static void n32_basemul(void)
{
	gt32_n32_basemul_half_r1u_asm(output, half_a, half_b);
}

__attribute__((noinline))
static void current_inverse(void)
{
	gt32_tile4_inverse_all_pair_asm(current_midpoint, standard_product);
	gt32_current_idft3_branch_row_asm(output, current_midpoint);
}

__attribute__((noinline))
static void n32_inverse(void)
{
	gt32_n32_inverse_half_r1u_asm(output, half_product);
}

__attribute__((noinline))
static void current_whole(void)
{
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(standard_a, coefficients_a);
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(standard_b, coefficients_b);
	gt32_tile4_basemul_scale_ff_aos_r1u_asm(
		standard_product, standard_a, standard_b);
	gt32_tile4_inverse_all_pair_asm(current_midpoint, standard_product);
	gt32_current_idft3_branch_row_asm(output, current_midpoint);
}

__attribute__((noinline))
static void n32_whole(void)
{
	gt32_n32_forward_half_conjugated_asm(half_a, coefficients_a);
	gt32_n32_forward_half_conjugated_asm(half_b, coefficients_b);
	gt32_n32_basemul_half_r1u_asm(half_product, half_a, half_b);
	gt32_n32_inverse_half_r1u_asm(output, half_product);
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
	_Alignas(64) int16_t standard_half[WORDS];
	_Alignas(64) int16_t half_product_standard[WORDS];
	cpu_set_t set;

	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof(set), &set) != 0)
		perror("sched_setaffinity");
	for (int index = 0; index < WORDS; index++) {
		coefficients_a[index] = (int16_t)((index * 5 + 1) % 8 - 3);
		coefficients_b[index] = (int16_t)((index * 7 + 3) % 8 - 3);
	}
	current_forward_two();
	n32_forward_conjugated_two();
	/* Reuse the inverse mapping by treating half_a as the destination. */
	half_to_standard(standard_half, half_a);
	if (!equal_mod_q(standard_a, standard_half)) {
		fputs("Forward semantic mismatch\n", stderr);
		return 1;
	}
	gt32_tile4_basemul_scale_ff_aos_r1u_asm(
		standard_product, standard_a, standard_b);
	gt32_n32_basemul_half_r1u_asm(half_product, half_a, half_b);
	half_to_standard(half_product_standard, half_product);
	if (!equal_mod_q(standard_product, half_product_standard)) {
		fputs("BaseMul semantic mismatch\n", stderr);
		return 1;
	}
	current_inverse();
	for (int index = 0; index < WORDS; index++)
		standard_half[index] = output[index];
	n32_inverse();
	if (!equal_mod_q(standard_half, output)) {
		int mismatch = 0;
		while (mismatch < WORDS && centered_mod(standard_half[mismatch]) ==
			centered_mod(output[mismatch]))
			mismatch++;
		fprintf(stderr, "Inverse common-endpoint mismatch word=%d current=%d "
			"n32=%d\n", mismatch,
			mismatch < WORDS ? standard_half[mismatch] : 0,
			mismatch < WORDS ? output[mismatch] : 0);
		return 1;
	}
	for (unsigned warmup = 0; warmup < 2U; warmup++) {
		(void)measure(current_forward_one, 200U);
		(void)measure(n32_forward_raw_one, 200U);
		(void)measure(n32_forward_centered_one, 200U);
		(void)measure(n32_forward_conjugated_one, 200U);
		(void)measure(current_forward_two, 200U);
		(void)measure(n32_forward_centered_two, 200U);
		(void)measure(n32_forward_conjugated_two, 200U);
		(void)measure(current_basemul, 200U);
		(void)measure(n32_basemul, 200U);
		(void)measure(current_inverse, 200U);
		(void)measure(n32_inverse, 200U);
		(void)measure(current_whole, 200U);
		(void)measure(n32_whole, 200U);
	}
	printf("META,experiment=GT-N32-FORWARD-CHAIN-014,iterations=%u,samples=%u\n",
		iterations, SAMPLES);
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		print_pair("forward_raw", sample,
			current_forward_one, n32_forward_raw_one, iterations);
		print_pair("forward_centered", sample,
			current_forward_one, n32_forward_centered_one, iterations);
		print_pair("forward_conjugated", sample,
			current_forward_one, n32_forward_conjugated_one, iterations);
		print_pair("forward2_centered", sample,
			current_forward_two, n32_forward_centered_two, iterations);
		print_pair("forward2_conjugated", sample,
			current_forward_two, n32_forward_conjugated_two, iterations);
		print_pair("basemul", sample,
			current_basemul, n32_basemul, iterations);
		print_pair("inverse_common", sample,
			current_inverse, n32_inverse, iterations);
		print_pair("whole_common", sample,
			current_whole, n32_whole, iterations);
	}
	return sink == UINT64_MAX ? 1 : 0;
}
