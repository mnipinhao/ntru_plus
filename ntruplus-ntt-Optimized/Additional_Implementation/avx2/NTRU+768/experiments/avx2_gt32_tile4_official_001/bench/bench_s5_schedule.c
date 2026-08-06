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

static int16_t frontend_scratch[WORDS] __attribute__((aligned(64)));
static int16_t work_a[WORDS] __attribute__((aligned(64)));
static int16_t work_b[WORDS] __attribute__((aligned(64)));
static int16_t product_soa[WORDS] __attribute__((aligned(64)));
static int16_t product_aos[WORDS] __attribute__((aligned(64)));
static int16_t inverse_rows[WORDS] __attribute__((aligned(64)));
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
static void core_old(int16_t *out, const int16_t *in, const int16_t *unused)
{
	(void)unused;
	gt32_tile4_attr_forward_all_bm_soa_asm(out, in);
}

__attribute__((noinline))
static void core_s5x4(int16_t *out, const int16_t *in, const int16_t *unused)
{
	(void)unused;
	gt32_tile4_attr_forward_all_bm_soa_s5x4_asm(out, in);
}

static void forward_old(int16_t *out, const int16_t *in)
{
	gt32_tile4_frontend_wide_raw_asm(frontend_scratch, in);
	gt32_tile4_attr_forward_all_bm_soa_asm(out, frontend_scratch);
}

static void forward_s5x4(int16_t *out, const int16_t *in)
{
	gt32_tile4_frontend_wide_raw_asm(frontend_scratch, in);
	gt32_tile4_attr_forward_all_bm_soa_s5x4_asm(out, frontend_scratch);
}

__attribute__((noinline))
static void chain_old(int16_t *out, const int16_t *a, const int16_t *b)
{
	forward_old(work_a, a);
	forward_old(work_b, b);
	gt32_tile4_attr_basemul_c3_soa_asm(product_soa, work_a, work_b);
	gt32_tile4_attr_transpose_one_asm(product_aos, product_soa);
	gt32_tile4_inverse_all_pair_asm(inverse_rows, product_aos);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out, inverse_rows);
}

__attribute__((noinline))
static void chain_s5x4(int16_t *out, const int16_t *a, const int16_t *b)
{
	forward_s5x4(work_a, a);
	forward_s5x4(work_b, b);
	gt32_tile4_attr_basemul_c3_soa_asm(product_soa, work_a, work_b);
	gt32_tile4_attr_transpose_one_asm(product_aos, product_soa);
	gt32_tile4_inverse_all_pair_asm(inverse_rows, product_aos);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out, inverse_rows);
}

struct gate {
	const char *name;
	kernel_fn baseline;
	kernel_fn candidate;
	const int16_t *a;
	const int16_t *b;
};

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	int16_t a[WORDS] __attribute__((aligned(64)));
	int16_t b[WORDS] __attribute__((aligned(64)));
	int16_t out0[WORDS] __attribute__((aligned(64)));
	int16_t out1[WORDS] __attribute__((aligned(64)));
	cpu_set_t set;
	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof(set), &set) != 0)
		perror("sched_setaffinity");
	for (unsigned i = 0; i < WORDS; i++) {
		a[i] = (int16_t)((int)(i % 8U) - 3);
		b[i] = (int16_t)((int)((5U * i + 1U) % 8U) - 3);
	}
	gt32_tile4_frontend_wide_raw_asm(frontend_scratch, a);
	core_old(out0, frontend_scratch, NULL);
	core_s5x4(out1, frontend_scratch, NULL);
	if (memcmp(out0, out1, sizeof(out0)) != 0) {
		fprintf(stderr, "S5x4 forward-core differential failed\n");
		return 1;
	}
	chain_old(out0, a, b);
	chain_s5x4(out1, a, b);
	if (memcmp(out0, out1, sizeof(out0)) != 0) {
		fprintf(stderr, "S5x4 full-chain differential failed\n");
		return 1;
	}
	const struct gate gates[] = {
		{"forward_core", core_old, core_s5x4, frontend_scratch, NULL},
		{"two_forward_bm_i1_t9", chain_old, chain_s5x4, a, b},
	};
	for (unsigned gate = 0; gate < sizeof(gates) / sizeof(gates[0]); gate++) {
		for (unsigned warm = 0; warm < 2; warm++) {
			(void)measure(gates[gate].baseline, out0, gates[gate].a,
				gates[gate].b, 1000);
			(void)measure(gates[gate].candidate, out1, gates[gate].a,
				gates[gate].b, 1000);
		}
	}
	printf("META,correctness=pass,iterations=%u,samples=%u\n",
		iterations, SAMPLES);
	for (unsigned gate = 0; gate < sizeof(gates) / sizeof(gates[0]); gate++) {
		for (unsigned sample = 0; sample < SAMPLES; sample++) {
			double baseline;
			double candidate;
			if ((sample & 1U) == 0U) {
				baseline = measure(gates[gate].baseline, out0,
					gates[gate].a, gates[gate].b, iterations);
				candidate = measure(gates[gate].candidate, out1,
					gates[gate].a, gates[gate].b, iterations);
			} else {
				candidate = measure(gates[gate].candidate, out1,
					gates[gate].a, gates[gate].b, iterations);
				baseline = measure(gates[gate].baseline, out0,
					gates[gate].a, gates[gate].b, iterations);
			}
			printf("SAMPLE,%s,%u,%.6f,%.6f,%.6f\n", gates[gate].name,
				sample, baseline, candidate, candidate - baseline);
		}
	}
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}
