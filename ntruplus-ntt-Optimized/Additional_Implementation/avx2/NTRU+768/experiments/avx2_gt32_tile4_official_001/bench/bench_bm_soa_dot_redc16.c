#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <x86intrin.h>

#include "tile4.h"

#define WORDS GT32_TILE4_POLY_WORDS
#define SAMPLES 20
#define Q GT32_TILE4_Q

typedef void (*kernel_fn)(int16_t *, const int16_t *, const int16_t *);

static int16_t product_soa[WORDS] __attribute__((aligned(64)));
static int16_t product_aos[WORDS] __attribute__((aligned(64)));
static int16_t inverse_rows[WORDS] __attribute__((aligned(64)));
static volatile uint64_t sink;

static uint32_t next_random(uint32_t *state)
{
	*state = *state * 1664525U + 1013904223U;
	return *state;
}

static void fill_inputs(int16_t *a, int16_t *b, uint32_t *state,
	unsigned trial)
{
	for (unsigned i = 0; i < WORDS; i++) {
		if (trial == 0) {
			a[i] = 0;
			b[i] = 0;
		} else if (trial == 1) {
			a[i] = (int16_t)((i & 1U) ? 1728 : -1728);
			b[i] = (int16_t)((i & 2U) ? 1728 : -1728);
		} else {
			a[i] = (int16_t)((int32_t)(next_random(state) % 3457U) - 1728);
			b[i] = (int16_t)((int32_t)(next_random(state) % 3457U) - 1728);
		}
	}
}

static int16_t centered(int32_t value)
{
	value %= Q;
	if (value < 0)
		value += Q;
	if (value > Q / 2)
		value -= Q;
	return (int16_t)value;
}

static void compare_mod_q(const char *label, unsigned trial,
	const int16_t *a, const int16_t *b)
{
	for (unsigned i = 0; i < WORDS; i++) {
		if (centered(a[i]) != centered(b[i])) {
			fprintf(stderr, "%s failed trial=%u word=%u got=%d want=%d\n",
				label, trial, i, a[i], b[i]);
			exit(1);
		}
	}
}

static void correctness(void)
{
	int16_t a[WORDS] __attribute__((aligned(64)));
	int16_t b[WORDS] __attribute__((aligned(64)));
	int16_t reference_soa[WORDS] __attribute__((aligned(64)));
	int16_t candidate_soa[WORDS] __attribute__((aligned(64)));
	int16_t reference_aos[WORDS] __attribute__((aligned(64)));
	int16_t candidate_aos[WORDS] __attribute__((aligned(64)));
	int16_t reference_rows[WORDS] __attribute__((aligned(64)));
	int16_t candidate_rows[WORDS] __attribute__((aligned(64)));
	int16_t reference_tail[WORDS] __attribute__((aligned(64)));
	int16_t candidate_tail[WORDS] __attribute__((aligned(64)));
	uint32_t state = UINT32_C(0xB5D0716);

	for (unsigned trial = 0; trial < 1000; trial++) {
		fill_inputs(a, b, &state, trial);
		gt32_tile4_attr_basemul_raw_soa_asm(reference_soa, a, b);
		gt32_tile4_bm_soa_dot_redc16_asm(candidate_soa, a, b);
		compare_mod_q("SoA arithmetic", trial, candidate_soa, reference_soa);

		gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm(
			reference_aos, a, b);
		gt32_tile4_attr_transpose_one_asm(candidate_aos, candidate_soa);
		compare_mod_q("I1 input", trial, candidate_aos, reference_aos);
		gt32_tile4_inverse_all_pair_asm(reference_rows, reference_aos);
		gt32_tile4_inverse_all_pair_asm(candidate_rows, candidate_aos);
		compare_mod_q("I1", trial, candidate_rows, reference_rows);
		gt32_tile4_inverse_tail_t9_isolated_private_asm(reference_tail,
			reference_rows);
		gt32_tile4_inverse_tail_t9_isolated_private_asm(candidate_tail,
			candidate_rows);
		compare_mod_q("T9", trial, candidate_tail, reference_tail);
	}
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

__attribute__((noinline))
static void control_arithmetic(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	gt32_tile4_attr_basemul_raw_soa_asm(out, a, b);
}

__attribute__((noinline))
static void candidate_arithmetic(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	gt32_tile4_bm_soa_dot_redc16_asm(out, a, b);
}

__attribute__((noinline))
static void control_i1_input(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm(out, a, b);
}

__attribute__((noinline))
static void candidate_i1_input(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	gt32_tile4_bm_soa_dot_redc16_asm(product_soa, a, b);
	gt32_tile4_attr_transpose_one_asm(out, product_soa);
}

__attribute__((noinline))
static void control_full(int16_t *out, const int16_t *a, const int16_t *b)
{
	gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm(product_aos, a, b);
	gt32_tile4_inverse_all_pair_asm(inverse_rows, product_aos);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out, inverse_rows);
}

__attribute__((noinline))
static void candidate_full(int16_t *out, const int16_t *a, const int16_t *b)
{
	gt32_tile4_bm_soa_dot_redc16_asm(product_soa, a, b);
	gt32_tile4_attr_transpose_one_asm(product_aos, product_soa);
	gt32_tile4_inverse_all_pair_asm(inverse_rows, product_aos);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out, inverse_rows);
}

static double measure(kernel_fn fn, int16_t *out, const int16_t *a,
	const int16_t *b, unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		fn(out, a, b);
	const uint64_t end = stop_tsc();
	sink += (uint16_t)out[iterations % WORDS];
	return (double)(end - begin) / iterations;
}

static void print_gate(const char *name, kernel_fn control,
	kernel_fn candidate, int16_t *out0, int16_t *out1,
	const int16_t *a, const int16_t *b, unsigned iterations)
{
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		double c, n;
		if ((sample & 1U) == 0U) {
			c = measure(control, out0, a, b, iterations);
			n = measure(candidate, out1, a, b, iterations);
		} else {
			n = measure(candidate, out1, a, b, iterations);
			c = measure(control, out0, a, b, iterations);
		}
		printf("SAMPLE,%s,%u,%.6f,%.6f,%.6f\n", name, sample,
			c, n, n - c);
	}
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	int16_t a[WORDS] __attribute__((aligned(64)));
	int16_t b[WORDS] __attribute__((aligned(64)));
	int16_t out0[WORDS] __attribute__((aligned(64)));
	int16_t out1[WORDS] __attribute__((aligned(64)));
	uint32_t state = 1;
	cpu_set_t set;

	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof(set), &set) != 0)
		perror("sched_setaffinity");
	correctness();
	fill_inputs(a, b, &state, 2);
	for (unsigned warm = 0; warm < 2; warm++) {
		(void)measure(control_arithmetic, out0, a, b, 1000);
		(void)measure(candidate_arithmetic, out1, a, b, 1000);
		(void)measure(control_i1_input, out0, a, b, 1000);
		(void)measure(candidate_i1_input, out1, a, b, 1000);
		(void)measure(control_full, out0, a, b, 1000);
		(void)measure(candidate_full, out1, a, b, 1000);
	}
	printf("META,correctness=modq-pass,trials=1000,iterations=%u,samples=%u\n",
		iterations, SAMPLES);
	print_gate("arithmetic", control_arithmetic, candidate_arithmetic,
		out0, out1, a, b, iterations);
	print_gate("i1_input", control_i1_input, candidate_i1_input,
		out0, out1, a, b, iterations);
	print_gate("full", control_full, candidate_full,
		out0, out1, a, b, iterations);
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}
