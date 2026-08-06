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
static void core_aos(int16_t *out, const int16_t *in, const int16_t *unused)
{
	(void)unused;
	gt32_tile4_forward_all_pair_asm(out, in);
}

__attribute__((noinline))
static void core_soa(int16_t *out, const int16_t *in, const int16_t *unused)
{
	(void)unused;
	gt32_tile4_attr_forward_all_bm_soa_asm(out, in);
}

__attribute__((noinline))
static void forward_aos(int16_t *out, const int16_t *in, const int16_t *unused)
{
	(void)unused;
	gt32_tile4_frontend_wide_raw_asm(frontend_scratch, in);
	gt32_tile4_forward_all_pair_asm(out, frontend_scratch);
}

__attribute__((noinline))
static void forward_soa(int16_t *out, const int16_t *in, const int16_t *unused)
{
	(void)unused;
	gt32_tile4_frontend_wide_raw_asm(frontend_scratch, in);
	gt32_tile4_attr_forward_all_bm_soa_asm(out, frontend_scratch);
}

__attribute__((noinline))
static void bm_aos(int16_t *out, const int16_t *a, const int16_t *b)
{
	gt32_tile4_basemul_c3center_late_aos_private_asm(out, a, b);
}

__attribute__((noinline))
static void bm_soa(int16_t *out, const int16_t *a, const int16_t *b)
{
	gt32_tile4_attr_basemul_c3_soa_asm(product_soa, a, b);
	gt32_tile4_attr_transpose_one_asm(out, product_soa);
}

__attribute__((noinline))
static void chain_aos(int16_t *out, const int16_t *a, const int16_t *b)
{
	forward_aos(work_a, a, NULL);
	forward_aos(work_b, b, NULL);
	gt32_tile4_basemul_c3center_late_aos_private_asm(product_aos,
		work_a, work_b);
	gt32_tile4_inverse_all_pair_asm(out, product_aos);
}

__attribute__((noinline))
static void chain_soa(int16_t *out, const int16_t *a, const int16_t *b)
{
	forward_soa(work_a, a, NULL);
	forward_soa(work_b, b, NULL);
	gt32_tile4_attr_basemul_c3_soa_asm(product_soa, work_a, work_b);
	gt32_tile4_attr_transpose_one_asm(product_aos, product_soa);
	gt32_tile4_inverse_all_pair_asm(out, product_aos);
}

__attribute__((noinline))
static void chain_aos_t9(int16_t *out, const int16_t *a, const int16_t *b)
{
	forward_aos(work_a, a, NULL);
	forward_aos(work_b, b, NULL);
	gt32_tile4_basemul_c3center_late_aos_private_asm(product_aos,
		work_a, work_b);
	gt32_tile4_inverse_all_pair_asm(inverse_rows, product_aos);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out, inverse_rows);
}

__attribute__((noinline))
static void chain_soa_t9(int16_t *out, const int16_t *a, const int16_t *b)
{
	forward_soa(work_a, a, NULL);
	forward_soa(work_b, b, NULL);
	gt32_tile4_attr_basemul_c3_soa_asm(product_soa, work_a, work_b);
	gt32_tile4_attr_transpose_one_asm(product_aos, product_soa);
	gt32_tile4_inverse_all_pair_asm(inverse_rows, product_aos);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out, inverse_rows);
}

struct gate {
	const char *name;
	kernel_fn baseline;
	kernel_fn candidate;
	const int16_t *baseline_a;
	const int16_t *baseline_b;
	const int16_t *candidate_a;
	const int16_t *candidate_b;
};

static int exact_equal(const int16_t *a, const int16_t *b)
{
	return memcmp(a, b, WORDS * sizeof(*a)) == 0;
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	int16_t coefficients_a[WORDS] __attribute__((aligned(64)));
	int16_t coefficients_b[WORDS] __attribute__((aligned(64)));
	int16_t scratch_aos[WORDS] __attribute__((aligned(64)));
	int16_t ntt_aos_a[WORDS] __attribute__((aligned(64)));
	int16_t ntt_aos_b[WORDS] __attribute__((aligned(64)));
	int16_t ntt_soa_a[WORDS] __attribute__((aligned(64)));
	int16_t ntt_soa_b[WORDS] __attribute__((aligned(64)));
	int16_t out0[WORDS] __attribute__((aligned(64)));
	int16_t out1[WORDS] __attribute__((aligned(64)));
	cpu_set_t set;
	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof(set), &set) != 0)
		perror("sched_setaffinity");
	for (unsigned i = 0; i < WORDS; i++) {
		coefficients_a[i] = (int16_t)((int)(i % 8U) - 3);
		coefficients_b[i] = (int16_t)((int)((5U * i + 1U) % 8U) - 3);
	}
	gt32_tile4_frontend_wide_raw_asm(scratch_aos, coefficients_a);
	gt32_tile4_forward_all_pair_asm(ntt_aos_a, scratch_aos);
	gt32_tile4_attr_forward_all_bm_soa_asm(ntt_soa_a, scratch_aos);
	gt32_tile4_attr_transpose_one_asm(product_soa, ntt_aos_a);
	if (!exact_equal(product_soa, ntt_soa_a)) {
		fprintf(stderr, "direct SoA plane differential failed\n");
		for (unsigned i = 0, shown = 0; i < WORDS && shown < 16; i++) {
			if (product_soa[i] != ntt_soa_a[i]) {
				fprintf(stderr, "  plane word %u: got %d expected %d\n", i,
					ntt_soa_a[i], product_soa[i]);
				shown++;
			}
		}
		return 1;
	}
	gt32_tile4_attr_transpose_one_asm(out0, ntt_soa_a);
	if (!exact_equal(out0, ntt_aos_a)) {
		fprintf(stderr, "forward SoA redeposit differential failed\n");
		for (unsigned i = 0, shown = 0; i < WORDS && shown < 12; i++) {
			if (out0[i] != ntt_aos_a[i]) {
				fprintf(stderr, "  word %u: got %d expected %d\n", i,
					out0[i], ntt_aos_a[i]);
				shown++;
			}
		}
		return 1;
	}
	gt32_tile4_frontend_wide_raw_asm(scratch_aos, coefficients_b);
	gt32_tile4_forward_all_pair_asm(ntt_aos_b, scratch_aos);
	gt32_tile4_attr_forward_all_bm_soa_asm(ntt_soa_b, scratch_aos);
	bm_aos(out0, ntt_aos_a, ntt_aos_b);
	bm_soa(out1, ntt_soa_a, ntt_soa_b);
	if (!exact_equal(out0, out1)) {
		fprintf(stderr, "SoA forward plus BM differential failed\n");
		return 1;
	}
	chain_aos_t9(out0, coefficients_a, coefficients_b);
	chain_soa_t9(out1, coefficients_a, coefficients_b);
	if (!exact_equal(out0, out1)) {
		fprintf(stderr, "full redeposit chain plus T9 differential failed\n");
		return 1;
	}
	chain_aos(out0, coefficients_a, coefficients_b);
	chain_soa(out1, coefficients_a, coefficients_b);
	if (!exact_equal(out0, out1)) {
		fprintf(stderr, "full redeposit chain differential failed\n");
		return 1;
	}

	const struct gate gates[] = {
		{"forward_core", core_aos, core_soa,
			scratch_aos, NULL, scratch_aos, NULL},
		{"full_forward", forward_aos, forward_soa,
			coefficients_a, NULL, coefficients_a, NULL},
		{"basemul", bm_aos, bm_soa,
			ntt_aos_a, ntt_aos_b, ntt_soa_a, ntt_soa_b},
		{"two_forward_bm_i1", chain_aos, chain_soa,
			coefficients_a, coefficients_b, coefficients_a, coefficients_b},
		{"two_forward_bm_i1_t9", chain_aos_t9, chain_soa_t9,
			coefficients_a, coefficients_b, coefficients_a, coefficients_b},
	};
	const size_t gate_count = sizeof(gates) / sizeof(gates[0]);
	for (size_t gate = 0; gate < gate_count; gate++) {
		for (unsigned warm = 0; warm < 2; warm++) {
			(void)measure(gates[gate].baseline, out0,
				gates[gate].baseline_a, gates[gate].baseline_b, 1000);
			(void)measure(gates[gate].candidate, out1,
				gates[gate].candidate_a, gates[gate].candidate_b, 1000);
		}
	}
	printf("META,correctness=pass,iterations=%u,samples=%u\n",
		iterations, SAMPLES);
	for (size_t gate = 0; gate < gate_count; gate++) {
		for (unsigned sample = 0; sample < SAMPLES; sample++) {
			double baseline;
			double candidate;
			if ((sample & 1U) == 0U) {
				baseline = measure(gates[gate].baseline, out0,
					gates[gate].baseline_a, gates[gate].baseline_b,
					iterations);
				candidate = measure(gates[gate].candidate, out1,
					gates[gate].candidate_a, gates[gate].candidate_b,
					iterations);
			} else {
				candidate = measure(gates[gate].candidate, out1,
					gates[gate].candidate_a, gates[gate].candidate_b,
					iterations);
				baseline = measure(gates[gate].baseline, out0,
					gates[gate].baseline_a, gates[gate].baseline_b,
					iterations);
			}
			printf("SAMPLE,%s,%u,%.6f,%.6f,%.6f\n", gates[gate].name,
				sample, baseline, candidate, candidate - baseline);
		}
	}
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}
