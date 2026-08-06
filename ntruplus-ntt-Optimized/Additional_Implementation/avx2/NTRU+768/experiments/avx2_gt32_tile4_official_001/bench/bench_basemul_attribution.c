#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <x86intrin.h>

#include "tile4.h"

#define WORDS 768
#define SAMPLES 20

typedef void (*unary_fn)(int16_t *, const int16_t *);
typedef void (*binary_fn)(int16_t *, const int16_t *, const int16_t *);
typedef void (*two_fn)(int16_t *, int16_t *, const int16_t *, const int16_t *);
typedef void (*three_fn)(int16_t *, int16_t *, int16_t *, const int16_t *,
	const int16_t *, const int16_t *);

void poly_ntt(int16_t *);
void poly_basemul_scale(int16_t *, const int16_t *, const int16_t *);

static int16_t coefficient_a[WORDS] __attribute__((aligned(64)));
static int16_t coefficient_b[WORDS] __attribute__((aligned(64)));
static int16_t official_a[WORDS] __attribute__((aligned(64)));
static int16_t official_b[WORDS] __attribute__((aligned(64)));
static int16_t aos_a[WORDS] __attribute__((aligned(64)));
static int16_t aos_b[WORDS] __attribute__((aligned(64)));
static int16_t soa_a[WORDS] __attribute__((aligned(64)));
static int16_t soa_b[WORDS] __attribute__((aligned(64)));
static int16_t raw_soa[WORDS] __attribute__((aligned(64)));
static int16_t product[WORDS] __attribute__((aligned(64)));
static int16_t post_stage1[WORDS] __attribute__((aligned(64)));
static int16_t out0[WORDS] __attribute__((aligned(64)));
static int16_t out1[WORDS] __attribute__((aligned(64)));
static int16_t out2[WORDS] __attribute__((aligned(64)));
static volatile uint64_t sink;

__attribute__((noinline))
static void champion_bm_i1(int16_t *out, const int16_t *a, const int16_t *b)
{
	gt32_tile4_basemul_c3center_late_aos_private_asm(product, a, b);
	gt32_tile4_inverse_all_pair_asm(out, product);
}

__attribute__((noinline))
static void fused_bm_i1(int16_t *out, const int16_t *a, const int16_t *b)
{
	gt32_tile4_attr_basemul_i1_stage01_fused_asm(post_stage1, a, b);
	gt32_tile4_attr_inverse_i1_cross3_asm(out, post_stage1);
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

static double measure_unary(unary_fn fn, int16_t *out, const int16_t *in,
	unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		fn(out, in);
	const uint64_t end = stop_tsc();
	sink += (uint16_t)out[iterations & 767U];
	return (double)(end - begin) / iterations;
}

static double measure_binary(binary_fn fn, int16_t *out, const int16_t *a,
	const int16_t *b, unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		fn(out, a, b);
	const uint64_t end = stop_tsc();
	sink += (uint16_t)out[iterations & 767U];
	return (double)(end - begin) / iterations;
}

static double measure_two(two_fn fn, int16_t *out_a, int16_t *out_b,
	const int16_t *a, const int16_t *b, unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		fn(out_a, out_b, a, b);
	const uint64_t end = stop_tsc();
	sink += (uint16_t)out_a[iterations & 767U];
	return (double)(end - begin) / iterations;
}

static double measure_three(three_fn fn, int16_t *oa, int16_t *ob,
	int16_t *oc, const int16_t *a, const int16_t *b, const int16_t *c,
	unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		fn(oa, ob, oc, a, b, c);
	const uint64_t end = stop_tsc();
	sink += (uint16_t)oa[iterations & 767U];
	return (double)(end - begin) / iterations;
}

enum gate_kind { G_UNARY, G_BINARY, G_TWO, G_THREE };

struct gate {
	const char *name;
	enum gate_kind kind;
	union {
		unary_fn unary;
		binary_fn binary;
		two_fn two;
		three_fn three;
	} fn;
	int16_t *out_a;
	int16_t *out_b;
	int16_t *out_c;
	const int16_t *in_a;
	const int16_t *in_b;
	const int16_t *in_c;
};

static double run_gate(const struct gate *gate, unsigned iterations)
{
	switch (gate->kind) {
	case G_UNARY:
		return measure_unary(gate->fn.unary, gate->out_a, gate->in_a,
			iterations);
	case G_BINARY:
		return measure_binary(gate->fn.binary, gate->out_a, gate->in_a,
			gate->in_b, iterations);
	case G_TWO:
		return measure_two(gate->fn.two, gate->out_a, gate->out_b,
			gate->in_a, gate->in_b, iterations);
	case G_THREE:
		return measure_three(gate->fn.three, gate->out_a, gate->out_b,
			gate->out_c, gate->in_a, gate->in_b, gate->in_c,
			iterations);
	}
	abort();
}

static int exact_equal(const int16_t *a, const int16_t *b)
{
	return memcmp(a, b, WORDS * sizeof(*a)) == 0;
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	cpu_set_t set;
	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof(set), &set) != 0)
		perror("sched_setaffinity");

	for (unsigned i = 0; i < WORDS; i++) {
		coefficient_a[i] = (int16_t)((int)(i % 8U) - 3);
		coefficient_b[i] = (int16_t)((int)((5U * i + 1U) % 8U) - 3);
	}
	memcpy(official_a, coefficient_a, sizeof(official_a));
	memcpy(official_b, coefficient_b, sizeof(official_b));
	memcpy(aos_a, coefficient_a, sizeof(aos_a));
	memcpy(aos_b, coefficient_b, sizeof(aos_b));
	poly_ntt(official_a);
	poly_ntt(official_b);
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(aos_a, aos_a);
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(aos_b, aos_b);
	gt32_tile4_attr_transpose_one_asm(soa_a, aos_a);
	gt32_tile4_attr_transpose_one_asm(soa_b, aos_b);

	/* Boundary and arithmetic oracles are exact, not merely mod-q. */
	gt32_tile4_attr_transpose_one_asm(out0, soa_a);
	if (!exact_equal(out0, aos_a)) {
		fprintf(stderr, "self-inverse transpose failed\n");
		return 1;
	}
	gt32_tile4_basemul_raw_soa_private_asm(out0, aos_a, aos_b);
	gt32_tile4_attr_basemul_raw_soa_asm(raw_soa, soa_a, soa_b);
	if (!exact_equal(out0, raw_soa)) {
		fprintf(stderr, "raw arithmetic decomposition failed\n");
		return 1;
	}
	gt32_tile4_attr_basemul_c3_soa_asm(out0, soa_a, soa_b);
	gt32_tile4_attr_center_c3_soa_asm(out1, raw_soa);
	if (!exact_equal(out0, out1)) {
		fprintf(stderr, "c3 repair decomposition failed\n");
		return 1;
	}
	gt32_tile4_attr_transpose_one_asm(out2, out0);
	gt32_tile4_basemul_c3center_late_aos_private_asm(out1, aos_a, aos_b);
	if (!exact_equal(out1, out2)) {
		fprintf(stderr, "full B3 decomposition failed\n");
		return 1;

	}
	champion_bm_i1(out0, aos_a, aos_b);
	fused_bm_i1(out1, aos_a, aos_b);
	if (!exact_equal(out0, out1)) {
		fprintf(stderr, "fused BM plus I1 differential failed\n");
		return 1;
	}
	gt32_tile4_attr_basemul_i1_stage01_fused_asm(post_stage1, aos_a, aos_b);

	const struct gate gates[] = {
		{"empty", G_BINARY, {.binary = gt32_tile4_attr_empty_asm},
			out0, NULL, NULL, soa_a, soa_b, NULL},
		{"TA", G_UNARY, {.unary = gt32_tile4_attr_transpose_one_asm},
			out0, NULL, NULL, aos_a, NULL, NULL},
		{"TAB", G_TWO, {.two = gt32_tile4_attr_transpose_two_asm},
			out0, out1, NULL, aos_a, aos_b, NULL},
		{"TO", G_UNARY, {.unary = gt32_tile4_attr_transpose_one_asm},
			out0, NULL, NULL, raw_soa, NULL, NULL},
		{"TABO", G_THREE, {.three = gt32_tile4_attr_transpose_three_asm},
			out0, out1, out2, aos_a, aos_b, raw_soa},
		{"tile4_arith_raw", G_BINARY,
			{.binary = gt32_tile4_attr_basemul_raw_soa_asm},
			out0, NULL, NULL, soa_a, soa_b, NULL},
		{"tile4_arith_c3", G_BINARY,
			{.binary = gt32_tile4_attr_basemul_c3_soa_asm},
			out0, NULL, NULL, soa_a, soa_b, NULL},
		{"c3_repair_boundary", G_UNARY,
			{.unary = gt32_tile4_attr_center_c3_soa_asm},
			out0, NULL, NULL, raw_soa, NULL, NULL},
		{"tile4_full_b3", G_BINARY,
			{.binary = gt32_tile4_basemul_c3center_late_aos_private_asm},
			out0, NULL, NULL, aos_a, aos_b, NULL},
		{"official_arith_scale", G_BINARY, {.binary = poly_basemul_scale},
			out0, NULL, NULL, official_a, official_b, NULL},
		{"fused_stage01_producer", G_BINARY,
			{.binary = gt32_tile4_attr_basemul_i1_stage01_fused_asm},
			out0, NULL, NULL, aos_a, aos_b, NULL},
		{"i1_cross3_remainder", G_UNARY,
			{.unary = gt32_tile4_attr_inverse_i1_cross3_asm},
			out0, NULL, NULL, post_stage1, NULL, NULL},
		{"champion_bm_i1", G_BINARY, {.binary = champion_bm_i1},
			out0, NULL, NULL, aos_a, aos_b, NULL},
		{"fused_bm_i1", G_BINARY, {.binary = fused_bm_i1},
			out0, NULL, NULL, aos_a, aos_b, NULL},
	};
	const size_t gate_count = sizeof(gates) / sizeof(gates[0]);
	for (size_t gate = 0; gate < gate_count; gate++)
		for (unsigned warm = 0; warm < 2; warm++)
			(void)run_gate(&gates[gate], 1000);

	printf("META,correctness=pass,iterations=%u,samples=%u\n",
		iterations, SAMPLES);
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		for (size_t step = 0; step < gate_count; step++) {
			const size_t gate = (sample & 1U) ? gate_count - 1U - step : step;
			const double ticks = run_gate(&gates[gate], iterations);
			printf("SAMPLE,%s,%u,%.6f\n", gates[gate].name, sample,
				ticks);
		}
	}
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}
