#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <x86intrin.h>

#include "tile4.h"

#define WORDS GT32_TILE4_POLY_WORDS
#define SAMPLES 20

typedef void (*kernel_fn)(int16_t *, const int16_t *, const int16_t *);

static int16_t a_soa[WORDS] __attribute__((aligned(64)));
static int16_t b_soa[WORDS] __attribute__((aligned(64)));
static int16_t b_frontend[WORDS] __attribute__((aligned(64)));
static int16_t product[WORDS] __attribute__((aligned(64)));
static int16_t product_aos[WORDS] __attribute__((aligned(64)));
static int16_t inverse_rows[WORDS] __attribute__((aligned(64)));
static int16_t inactive_half[64] __attribute__((aligned(64)));
static volatile uint64_t sink;
static uint32_t rng_state = 1;

static uint32_t next_random(void)
{
	rng_state = 1664525U * rng_state + 1013904223U;
	return rng_state;
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

static double measure(kernel_fn fn, int16_t *out, const int16_t *a,
	const int16_t *b, unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		fn(out, a, b);
	const uint64_t end = stop_tsc();
	sink += (uint16_t)out[iterations & 767U];
	return (double)(end - begin) / iterations;
}

__attribute__((noinline))
static void baseline_bm(int16_t *out, const int16_t *a,
	const int16_t *frontend_b)
{
	gt32_tile4_attr_forward_all_bm_soa_asm(b_soa, frontend_b);
	gt32_tile4_attr_basemul_c3_soa_asm(out, a, b_soa);
}

__attribute__((noinline))
static void streaming_bm(int16_t *out, const int16_t *a,
	const int16_t *frontend_b)
{
	gt32_tile4_attr_forward_b_stream_bm_soa_asm(out, a, frontend_b,
		inactive_half);
}

__attribute__((noinline))
static void baseline_chain(int16_t *out, const int16_t *a,
	const int16_t *frontend_b)
{
	baseline_bm(product, a, frontend_b);
	gt32_tile4_attr_transpose_one_asm(product_aos, product);
	gt32_tile4_inverse_all_pair_asm(inverse_rows, product_aos);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out, inverse_rows);
}

__attribute__((noinline))
static void streaming_chain(int16_t *out, const int16_t *a,
	const int16_t *frontend_b)
{
	streaming_bm(product, a, frontend_b);
	gt32_tile4_attr_transpose_one_asm(product_aos, product);
	gt32_tile4_inverse_all_pair_asm(inverse_rows, product_aos);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out, inverse_rows);
}

struct gate {
	const char *name;
	kernel_fn baseline;
	kernel_fn candidate;
};

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	int16_t input_a[WORDS] __attribute__((aligned(64)));
	int16_t input_b[WORDS] __attribute__((aligned(64)));
	int16_t frontend_a[WORDS] __attribute__((aligned(64)));
	int16_t out0[WORDS] __attribute__((aligned(64)));
	int16_t out1[WORDS] __attribute__((aligned(64)));
	cpu_set_t set;
	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof(set), &set) != 0)
		perror("sched_setaffinity");
	for (unsigned i = 0; i < WORDS; i++) {
		input_a[i] = (int16_t)((int)(i % 8U) - 3);
		input_b[i] = (int16_t)((int)((5U * i + 1U) % 8U) - 3);
	}
	gt32_tile4_frontend_wide_raw_asm(frontend_a, input_a);
	gt32_tile4_frontend_wide_raw_asm(b_frontend, input_b);
	gt32_tile4_attr_forward_all_bm_soa_asm(a_soa, frontend_a);

	baseline_bm(out0, a_soa, b_frontend);
	streaming_bm(out1, a_soa, b_frontend);
	if (memcmp(out0, out1, sizeof(out0)) != 0) {
		fprintf(stderr, "streaming-B BM differential failed\n");
		return 1;
	}
	for (unsigned trial = 0; trial < 64; trial++) {
		for (unsigned i = 0; i < WORDS; i++) {
			input_a[i] = (int16_t)((int)(next_random() & 7U) - 3);
			input_b[i] = (int16_t)((int)(next_random() & 7U) - 3);
		}
		gt32_tile4_frontend_wide_raw_asm(frontend_a, input_a);
		gt32_tile4_frontend_wide_raw_asm(b_frontend, input_b);
		gt32_tile4_attr_forward_all_bm_soa_asm(a_soa, frontend_a);
		baseline_bm(out0, a_soa, b_frontend);
		streaming_bm(out1, a_soa, b_frontend);
		if (memcmp(out0, out1, sizeof(out0)) != 0) {
			fprintf(stderr, "random streaming-B differential failed\n");
			return 1;
		}
	}
	baseline_chain(out0, a_soa, b_frontend);
	streaming_chain(out1, a_soa, b_frontend);
	if (memcmp(out0, out1, sizeof(out0)) != 0) {
		fprintf(stderr, "streaming-B chain differential failed\n");
		return 1;
	}

	const struct gate gates[] = {
		{"forward_b_plus_bm", baseline_bm, streaming_bm},
		{"forward_b_bm_i1_t9", baseline_chain, streaming_chain},
	};
	for (unsigned gate = 0; gate < sizeof(gates) / sizeof(gates[0]); gate++) {
		for (unsigned warm = 0; warm < 2; warm++) {
			(void)measure(gates[gate].baseline, out0, a_soa,
				b_frontend, 1000);
			(void)measure(gates[gate].candidate, out1, a_soa,
				b_frontend, 1000);
		}
	}
	printf("META,correctness=pass,iterations=%u,samples=%u\n",
		iterations, SAMPLES);
	for (unsigned gate = 0; gate < sizeof(gates) / sizeof(gates[0]); gate++) {
		for (unsigned sample = 0; sample < SAMPLES; sample++) {
			double baseline;
			double candidate;
			if ((sample & 1U) == 0U) {
				baseline = measure(gates[gate].baseline, out0, a_soa,
					b_frontend, iterations);
				candidate = measure(gates[gate].candidate, out1, a_soa,
					b_frontend, iterations);
			} else {
				candidate = measure(gates[gate].candidate, out1, a_soa,
					b_frontend, iterations);
				baseline = measure(gates[gate].baseline, out0, a_soa,
					b_frontend, iterations);
			}
			printf("SAMPLE,%s,%u,%.6f,%.6f,%.6f\n",
				gates[gate].name, sample, baseline, candidate,
				candidate - baseline);
		}
	}
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}
