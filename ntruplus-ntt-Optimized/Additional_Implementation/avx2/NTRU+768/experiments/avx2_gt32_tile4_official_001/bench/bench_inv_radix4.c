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

typedef void (*kernel_fn)(int16_t *, const int16_t *);

static int16_t inverse_rows[WORDS] __attribute__((aligned(64)));
static volatile uint64_t sink;

static uint32_t next_random(uint32_t *state)
{
	*state = *state * 1664525U + 1013904223U;
	return *state;
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

static void fill_input(int16_t *a, uint32_t *state, unsigned trial)
{
	for (unsigned i = 0; i < WORDS; i++) {
		if (trial == 0)
			a[i] = 0;
		else if (trial == 1)
			a[i] = (int16_t)((i & 1U) ? 1728 : -1728);
		else
			a[i] = (int16_t)((int32_t)(next_random(state) % 3457U) - 1728);
	}
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
	int16_t input[WORDS] __attribute__((aligned(64)));
	int16_t control[WORDS] __attribute__((aligned(64)));
	int16_t candidate[WORDS] __attribute__((aligned(64)));
	int16_t control_tail[WORDS] __attribute__((aligned(64)));
	int16_t candidate_tail[WORDS] __attribute__((aligned(64)));
	int16_t control_alias[WORDS] __attribute__((aligned(64)));
	int16_t candidate_alias[WORDS] __attribute__((aligned(64)));
	uint32_t state = UINT32_C(0x1a4d4c01);

	for (unsigned trial = 0; trial < 1000; trial++) {
		fill_input(input, &state, trial);
		gt32_tile4_inverse_all_pair_asm(control, input);
		gt32_tile4_inverse_radix4_identity_asm(candidate, input);
		compare_mod_q("inverse-core", trial, candidate, control);
		for (unsigned i = 0; i < WORDS; i++) {
			control_alias[i] = input[i];
			candidate_alias[i] = input[i];
		}
		gt32_tile4_inverse_all_pair_asm(control_alias, control_alias);
		gt32_tile4_inverse_radix4_identity_asm(candidate_alias,
			candidate_alias);
		compare_mod_q("inverse-alias", trial, candidate_alias,
			control_alias);
		gt32_tile4_inverse_tail_t9_isolated_private_asm(control_tail, control);
		gt32_tile4_inverse_tail_t9_isolated_private_asm(candidate_tail,
			candidate);
		compare_mod_q("inverse-tail", trial, candidate_tail, control_tail);
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
static void control_core(int16_t *out, const int16_t *in)
{
	gt32_tile4_inverse_all_pair_asm(out, in);
}

__attribute__((noinline))
static void candidate_core(int16_t *out, const int16_t *in)
{
	gt32_tile4_inverse_radix4_identity_asm(out, in);
}

__attribute__((noinline))
static void control_full(int16_t *out, const int16_t *in)
{
	gt32_tile4_inverse_all_pair_asm(inverse_rows, in);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out, inverse_rows);
}

__attribute__((noinline))
static void candidate_full(int16_t *out, const int16_t *in)
{
	gt32_tile4_inverse_radix4_identity_asm(inverse_rows, in);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out, inverse_rows);
}

static double measure(kernel_fn fn, int16_t *out, const int16_t *in,
	unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		fn(out, in);
	const uint64_t end = stop_tsc();
	sink += (uint16_t)out[iterations % WORDS];
	return (double)(end - begin) / iterations;
}

static void print_gate(const char *name, kernel_fn control,
	kernel_fn candidate, int16_t *out0, int16_t *out1,
	const int16_t *in, unsigned iterations)
{
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		double c, n;
		if ((sample & 1U) == 0U) {
			c = measure(control, out0, in, iterations);
			n = measure(candidate, out1, in, iterations);
		} else {
			n = measure(candidate, out1, in, iterations);
			c = measure(control, out0, in, iterations);
		}
		printf("SAMPLE,%s,%u,%.6f,%.6f,%.6f\n", name, sample,
			c, n, n - c);
	}
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	int16_t input[WORDS] __attribute__((aligned(64)));
	int16_t out0[WORDS] __attribute__((aligned(64)));
	int16_t out1[WORDS] __attribute__((aligned(64)));
	uint32_t state = 1;
	cpu_set_t set;

	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof(set), &set) != 0)
		perror("sched_setaffinity");
	correctness();
	fill_input(input, &state, 2);
	for (unsigned warm = 0; warm < 2; warm++) {
		(void)measure(control_core, out0, input, 1000);
		(void)measure(candidate_core, out1, input, 1000);
		(void)measure(control_full, out0, input, 1000);
		(void)measure(candidate_full, out1, input, 1000);
	}
	printf("META,correctness=modq-pass,trials=1000,iterations=%u,samples=%u\n",
		iterations, SAMPLES);
	print_gate("core", control_core, candidate_core, out0, out1,
		input, iterations);
	print_gate("full", control_full, candidate_full, out0, out1,
		input, iterations);
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}
