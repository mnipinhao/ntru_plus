#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <x86intrin.h>

#include "tile4.h"

#define WORDS GT32_TILE4_POLY_WORDS
#define PAD_WORDS 16
#define SAMPLES 20
#define CORRECTNESS_TRIALS 1000

typedef void (*kernel_fn)(int16_t *, const int16_t *, const int16_t *);

void poly_crepmod3(int16_t *);

static int16_t frontend[WORDS] __attribute__((aligned(64)));
static int16_t work_a_raw[WORDS + PAD_WORDS] __attribute__((aligned(64)));
static int16_t work_b_raw[WORDS + PAD_WORDS] __attribute__((aligned(64)));
static int16_t fixed_b[WORDS] __attribute__((aligned(64)));
static int16_t fixed_aos_a[WORDS] __attribute__((aligned(64)));
static int16_t fixed_aos_b[WORDS] __attribute__((aligned(64)));
static int16_t product_soa[WORDS] __attribute__((aligned(64)));
static int16_t product_aos[WORDS] __attribute__((aligned(64)));
static int16_t inverse_rows[WORDS] __attribute__((aligned(64)));
static unsigned alignment_words;
static volatile uint64_t sink;

static int16_t *work_a(void)
{
	return work_a_raw + alignment_words;
}

static int16_t *work_b(void)
{
	return work_b_raw + alignment_words;
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
	sink += (uint16_t)out[iterations & (WORDS - 1U)];
	return (double)(end - begin) / iterations;
}

__attribute__((noinline))
static void terminal_t0(int16_t *out, const int16_t *in,
	const int16_t *unused)
{
	(void)unused;
	gt32_tile4_attr_forward_all_bm_soa_asm(out, in);
}

__attribute__((noinline))
static void terminal_t1(int16_t *out, const int16_t *in,
	const int16_t *unused)
{
	(void)unused;
	gt32_tile4_attr_forward_all_bm_soa_shufps_asm(out, in);
}

__attribute__((noinline))
static void aos_transpose_t0(int16_t *out, const int16_t *in,
	const int16_t *unused)
{
	(void)unused;
	gt32_tile4_attr_transpose_one_asm(out, in);
}

__attribute__((noinline))
static void aos_transpose_t1(int16_t *out, const int16_t *in,
	const int16_t *unused)
{
	(void)unused;
	gt32_tile4_attr_transpose_one_shufps_asm(out, in);
}

__attribute__((noinline))
static void aos_transpose_bm_t0(int16_t *out, const int16_t *in,
	const int16_t *b)
{
	gt32_tile4_attr_transpose_one_asm(work_a(), in);
	gt32_tile4_attr_basemul_c3_soa_asm(out, work_a(), b);
}

__attribute__((noinline))
static void aos_transpose_bm_t1(int16_t *out, const int16_t *in,
	const int16_t *b)
{
	gt32_tile4_attr_transpose_one_shufps_asm(work_a(), in);
	gt32_tile4_attr_basemul_c3_soa_asm(out, work_a(), b);
}

__attribute__((noinline))
static void aos_two_transpose_bm_t0(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	gt32_tile4_attr_transpose_one_asm(work_a(), a);
	gt32_tile4_attr_transpose_one_asm(work_b(), b);
	gt32_tile4_attr_basemul_c3_soa_asm(out, work_a(), work_b());
}

__attribute__((noinline))
static void aos_two_transpose_bm_t1(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	gt32_tile4_attr_transpose_one_shufps_asm(work_a(), a);
	gt32_tile4_attr_transpose_one_shufps_asm(work_b(), b);
	gt32_tile4_attr_basemul_c3_soa_asm(out, work_a(), work_b());
}

__attribute__((noinline))
static void terminal_bm_t0(int16_t *out, const int16_t *in,
	const int16_t *b)
{
	gt32_tile4_attr_forward_all_bm_soa_asm(work_a(), in);
	gt32_tile4_attr_basemul_c3_soa_asm(out, work_a(), b);
}

__attribute__((noinline))
static void terminal_bm_t1(int16_t *out, const int16_t *in,
	const int16_t *b)
{
	gt32_tile4_attr_forward_all_bm_soa_shufps_asm(work_a(), in);
	gt32_tile4_attr_basemul_c3_soa_asm(out, work_a(), b);
}

static void forward_t0(int16_t *out, const int16_t *in)
{
	gt32_tile4_frontend_wide_raw_asm(frontend, in);
	gt32_tile4_attr_forward_all_bm_soa_asm(out, frontend);
}

static void forward_t1(int16_t *out, const int16_t *in)
{
	gt32_tile4_frontend_wide_raw_asm(frontend, in);
	gt32_tile4_attr_forward_all_bm_soa_shufps_asm(out, frontend);
}

__attribute__((noinline))
static void forward_bm_t0(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	forward_t0(work_a(), a);
	gt32_tile4_attr_basemul_c3_soa_asm(out, work_a(), b);
}

__attribute__((noinline))
static void forward_bm_t1(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	forward_t1(work_a(), a);
	gt32_tile4_attr_basemul_c3_soa_asm(out, work_a(), b);
}

static void two_forward_bm_body(int16_t *out, const int16_t *a,
	const int16_t *b, int use_t1)
{
	if (use_t1) {
		forward_t1(work_a(), a);
		forward_t1(work_b(), b);
	} else {
		forward_t0(work_a(), a);
		forward_t0(work_b(), b);
	}
	gt32_tile4_attr_basemul_c3_soa_asm(out, work_a(), work_b());
}

__attribute__((noinline))
static void two_forward_bm_t0(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	two_forward_bm_body(out, a, b, 0);
}

__attribute__((noinline))
static void two_forward_bm_t1(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	two_forward_bm_body(out, a, b, 1);
}

static void inverse_body(int16_t *out, const int16_t *a, const int16_t *b,
	int use_t1, int include_t9, int include_crepmod3)
{
	two_forward_bm_body(product_soa, a, b, use_t1);
	gt32_tile4_attr_transpose_one_asm(product_aos, product_soa);
	gt32_tile4_inverse_all_pair_asm(inverse_rows, product_aos);
	if (include_t9) {
		gt32_tile4_inverse_tail_t9_isolated_private_asm(out, inverse_rows);
		if (include_crepmod3)
			poly_crepmod3(out);
	} else {
		memcpy(out, inverse_rows, WORDS * sizeof(*out));
	}
}

#define DEFINE_INVERSE_WRAPPER(name, t1, t9, crep) \
	__attribute__((noinline)) \
	static void name(int16_t *out, const int16_t *a, const int16_t *b) \
	{ \
		inverse_body(out, a, b, t1, t9, crep); \
	}

DEFINE_INVERSE_WRAPPER(two_forward_bm_i1_t0, 0, 0, 0)
DEFINE_INVERSE_WRAPPER(two_forward_bm_i1_t1, 1, 0, 0)
DEFINE_INVERSE_WRAPPER(two_forward_bm_i1_t9_t0, 0, 1, 0)
DEFINE_INVERSE_WRAPPER(two_forward_bm_i1_t9_t1, 1, 1, 0)
DEFINE_INVERSE_WRAPPER(decap_slice_t0, 0, 1, 1)
DEFINE_INVERSE_WRAPPER(decap_slice_t1, 1, 1, 1)

static uint32_t next_random(uint32_t *state)
{
	*state = *state * 1664525U + 1013904223U;
	return *state;
}

static void fill_small(int16_t *out, uint32_t *state)
{
	for (unsigned i = 0; i < WORDS; i++)
		out[i] = (int16_t)((int)(next_random(state) >> 29) - 3);
}

static int check_exact(const int16_t *a, const int16_t *b)
{
	return memcmp(a, b, WORDS * sizeof(*a)) == 0;
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
	const unsigned alignment = argc > 2
		? (unsigned)strtoul(argv[2], NULL, 10) : 64U;
	int16_t a[WORDS] __attribute__((aligned(64)));
	int16_t b[WORDS] __attribute__((aligned(64)));
	int16_t out0_raw[WORDS + PAD_WORDS] __attribute__((aligned(64)));
	int16_t out1_raw[WORDS + PAD_WORDS] __attribute__((aligned(64)));
	uint32_t random_state = 1;
	cpu_set_t set;

	if (alignment != 32U && alignment != 64U) {
		fprintf(stderr, "alignment must be 32 or 64\n");
		return 2;
	}
	alignment_words = alignment == 64U ? 0U : PAD_WORDS;
	int16_t *const out0 = out0_raw + alignment_words;
	int16_t *const out1 = out1_raw + alignment_words;
	if (((uintptr_t)work_a() & 31U) != 0U
			|| ((uintptr_t)work_a() & 63U) != (alignment == 64U ? 0U : 32U)) {
		fprintf(stderr, "unexpected scratch alignment\n");
		return 2;
	}

	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof(set), &set) != 0)
		perror("sched_setaffinity");
	fill_small(a, &random_state);
	fill_small(b, &random_state);
	gt32_tile4_frontend_wide_raw_asm(frontend, b);
	gt32_tile4_attr_forward_all_bm_soa_asm(fixed_b, frontend);

	for (unsigned trial = 0; trial < CORRECTNESS_TRIALS; trial++) {
		fill_small(a, &random_state);
		fill_small(b, &random_state);
		gt32_tile4_frontend_wide_raw_asm(frontend, a);
		terminal_t0(out0, frontend, NULL);
		terminal_t1(out1, frontend, NULL);
		if (!check_exact(out0, out1)) {
			fprintf(stderr, "T1 terminal differential failed at trial %u\n",
				trial);
			return 1;
		}
		gt32_tile4_forward_all_pair_asm(fixed_aos_a, frontend);
		gt32_tile4_frontend_wide_raw_asm(frontend, b);
		gt32_tile4_forward_all_pair_asm(fixed_aos_b, frontend);
		aos_transpose_t0(out0, fixed_aos_a, NULL);
		aos_transpose_t1(out1, fixed_aos_a, NULL);
		if (!check_exact(out0, out1)) {
			fprintf(stderr, "T1 AoS transpose differential failed at trial %u\n",
				trial);
			return 1;
		}
		aos_two_transpose_bm_t0(out0, fixed_aos_a, fixed_aos_b);
		aos_two_transpose_bm_t1(out1, fixed_aos_a, fixed_aos_b);
		if (!check_exact(out0, out1)) {
			fprintf(stderr, "T1 AoS transpose/BM differential failed at trial %u\n",
				trial);
			return 1;
		}
		decap_slice_t0(out0, a, b);
		decap_slice_t1(out1, a, b);
		if (!check_exact(out0, out1)) {
			fprintf(stderr, "T1 decap-slice differential failed at trial %u\n",
				trial);
			return 1;
		}
	}

	const struct gate gates[] = {
		{"aos_transpose", aos_transpose_t0, aos_transpose_t1,
			fixed_aos_a, NULL},
		{"aos_transpose_plus_bm", aos_transpose_bm_t0,
			aos_transpose_bm_t1, fixed_aos_a, fixed_b},
		{"aos_two_transpose_bm", aos_two_transpose_bm_t0,
			aos_two_transpose_bm_t1, fixed_aos_a, fixed_aos_b},
		{"terminal_store", terminal_t0, terminal_t1, frontend, NULL},
		{"terminal_plus_bm_load", terminal_bm_t0, terminal_bm_t1,
			frontend, fixed_b},
		{"forward_bm", forward_bm_t0, forward_bm_t1, a, fixed_b},
		{"two_forward_bm", two_forward_bm_t0, two_forward_bm_t1, a, b},
		{"two_forward_bm_i1", two_forward_bm_i1_t0,
			two_forward_bm_i1_t1, a, b},
		{"two_forward_bm_i1_t9", two_forward_bm_i1_t9_t0,
			two_forward_bm_i1_t9_t1, a, b},
		{"decap_polynomial_slice", decap_slice_t0, decap_slice_t1, a, b},
	};
	const size_t gate_count = sizeof(gates) / sizeof(gates[0]);
	for (size_t gate = 0; gate < gate_count; gate++) {
		for (unsigned warm = 0; warm < 2; warm++) {
			(void)measure(gates[gate].baseline, out0, gates[gate].a,
				gates[gate].b, 500);
			(void)measure(gates[gate].candidate, out1, gates[gate].a,
				gates[gate].b, 500);
		}
	}
	printf("META,correctness=pass,iterations=%u,samples=%u,alignment=%u\n",
		iterations, SAMPLES, alignment);
	for (size_t gate = 0; gate < gate_count; gate++) {
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
