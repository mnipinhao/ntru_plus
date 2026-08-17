#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <x86intrin.h>

#include "tile4.h"

#define WORDS GT32_TILE4_POLY_WORDS
#define BYTES GT32_TILE4_SERIALIZED_BYTES
#define SAMPLES 20

typedef struct {
	int16_t scaled_r[WORDS];
	int16_t frontend[WORDS];
	int16_t h[WORDS];
	int16_t r_frequency[WORDS];
	int16_t product[WORDS];
} gate_scratch_t;

typedef void (*gate_fn)(int16_t *, const uint8_t *, const int16_t *,
	const int16_t *, gate_scratch_t *);

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

static void add_aos(int16_t *out, const int16_t *a, const int16_t *b)
{
	for (unsigned i = 0; i < WORDS; i++)
		out[i] = (int16_t)(a[i] + b[i]);
}

static void scale_small_e1(int16_t *out, const int16_t *in)
{
	for (unsigned i = 0; i < WORDS; i++)
		out[i] = (int16_t)(-147 * in[i]);
}

__attribute__((noinline))
static void current_r2(int16_t *out, const uint8_t *encoded_h,
	const int16_t *r, const int16_t *m, gate_scratch_t *scratch)
{
	(void)gt32_tile4_frombytes_aos_asm(scratch->h, encoded_h);
	gt32_tile4_frontend_wide_raw_asm(scratch->frontend, r);
	gt32_tile4_attr_forward_all_bm_soa_asm(scratch->r_frequency,
		scratch->frontend);
	gt32_tile4_basemul_general_soa_aos_to_aos_asm(scratch->product,
		scratch->r_frequency, scratch->h);
	add_aos(out, scratch->product, m);
}

/* The input is already {-R,0,R}; this is the zero-premium producer bound. */
__attribute__((noinline))
static void e1_free(int16_t *out, const uint8_t *encoded_h,
	const int16_t *r_e1, const int16_t *m, gate_scratch_t *scratch)
{
	(void)gt32_tile4_frombytes_aos_asm(scratch->h, encoded_h);
	gt32_tile4_frontend_wide_e1_asm(scratch->frontend, r_e1);
	gt32_tile4_attr_forward_all_bm_soa_asm(scratch->r_frequency,
		scratch->frontend);
	gt32_tile4_basemul_e1_soa_aos_to_aos_asm(scratch->product,
		scratch->r_frequency, scratch->h);
	add_aos(out, scratch->product, m);
}

/* Concrete control: an extra vectorized coefficient pass supplies e=1. */
__attribute__((noinline))
static void e1_scale_pass(int16_t *out, const uint8_t *encoded_h,
	const int16_t *r, const int16_t *m, gate_scratch_t *scratch)
{
	scale_small_e1(scratch->scaled_r, r);
	e1_free(out, encoded_h, scratch->scaled_r, m, scratch);
}

static double measure(gate_fn fn, int16_t *out, const uint8_t *encoded_h,
	const int16_t *r, const int16_t *m, gate_scratch_t *scratch,
	unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		fn(out, encoded_h, r, m, scratch);
	const uint64_t end = stop_tsc();
	sink += (uint16_t)out[iterations & (WORDS - 1U)];
	return (double)(end - begin) / iterations;
}

static uint32_t next_random(uint32_t *state)
{
	*state = *state * 1664525U + 1013904223U;
	return *state;
}

static void fill_small(int16_t *out, uint32_t *state)
{
	for (unsigned i = 0; i < WORDS; i++)
		out[i] = (int16_t)((int)(next_random(state) % 3U) - 1);
}

static void pack_canonical(uint8_t out[BYTES], uint32_t *state)
{
	for (unsigned pair = 0; pair < WORDS / 2U; pair++) {
		const uint16_t a = (uint16_t)(next_random(state) % GT32_TILE4_Q);
		const uint16_t b = (uint16_t)(next_random(state) % GT32_TILE4_Q);
		out[3U * pair] = (uint8_t)a;
		out[3U * pair + 1U] = (uint8_t)((a >> 8) | (uint16_t)(b << 4));
		out[3U * pair + 2U] = (uint8_t)(b >> 4);
	}
}

static int16_t centered(int32_t value)
{
	value %= GT32_TILE4_Q;
	if (value < 0)
		value += GT32_TILE4_Q;
	if (value > GT32_TILE4_Q / 2)
		value -= GT32_TILE4_Q;
	return (int16_t)value;
}

static int equal_mod_q(const int16_t *a, const int16_t *b)
{
	for (unsigned i = 0; i < WORDS; i++) {
		if (centered(a[i]) != centered(b[i]))
			return 0;
	}
	return 1;
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	gate_scratch_t current_scratch __attribute__((aligned(64)));
	gate_scratch_t free_scratch __attribute__((aligned(64)));
	gate_scratch_t pass_scratch __attribute__((aligned(64)));
	int16_t r[WORDS] __attribute__((aligned(64)));
	int16_t r_e1[WORDS] __attribute__((aligned(64)));
	int16_t m[WORDS] __attribute__((aligned(64)));
	int16_t current_out[WORDS] __attribute__((aligned(64)));
	int16_t free_out[WORDS] __attribute__((aligned(64)));
	int16_t pass_out[WORDS] __attribute__((aligned(64)));
	uint8_t encoded_h[BYTES] __attribute__((aligned(64)));
	uint32_t state = 1U;
	cpu_set_t set;

	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof(set), &set) != 0)
		perror("sched_setaffinity");
	for (unsigned trial = 0; trial < 64; trial++) {
		pack_canonical(encoded_h, &state);
		fill_small(r, &state);
		fill_small(m, &state);
		scale_small_e1(r_e1, r);
		current_r2(current_out, encoded_h, r, m, &current_scratch);
		e1_free(free_out, encoded_h, r_e1, m, &free_scratch);
		e1_scale_pass(pass_out, encoded_h, r, m, &pass_scratch);
		if (!equal_mod_q(current_out, free_out)
			|| !equal_mod_q(current_out, pass_out)) {
			fprintf(stderr, "e1 producer differential failed trial=%u\n", trial);
			return 1;
		}
	}
	for (unsigned warm = 0; warm < 2; warm++) {
		(void)measure(current_r2, current_out, encoded_h, r, m,
			&current_scratch, 1000);
		(void)measure(e1_free, free_out, encoded_h, r_e1, m,
			&free_scratch, 1000);
		(void)measure(e1_scale_pass, pass_out, encoded_h, r, m,
			&pass_scratch, 1000);
	}
	printf("META,correctness=modq-pass,scope=encap-r-e1-producer,"
		"iterations=%u,samples=%u\n", iterations, SAMPLES);
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		double current;
		double free_cost;
		double pass_cost;
		if ((sample & 1U) == 0U) {
			current = measure(current_r2, current_out, encoded_h, r, m,
				&current_scratch, iterations);
			free_cost = measure(e1_free, free_out, encoded_h, r_e1, m,
				&free_scratch, iterations);
			pass_cost = measure(e1_scale_pass, pass_out, encoded_h, r, m,
				&pass_scratch, iterations);
		} else {
			pass_cost = measure(e1_scale_pass, pass_out, encoded_h, r, m,
				&pass_scratch, iterations);
			free_cost = measure(e1_free, free_out, encoded_h, r_e1, m,
				&free_scratch, iterations);
			current = measure(current_r2, current_out, encoded_h, r, m,
				&current_scratch, iterations);
		}
		printf("SAMPLE,%u,%.6f,%.6f,%.6f,%.6f,%.6f\n", sample,
			current, free_cost, pass_cost, free_cost - current,
			pass_cost - current);
	}
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}
