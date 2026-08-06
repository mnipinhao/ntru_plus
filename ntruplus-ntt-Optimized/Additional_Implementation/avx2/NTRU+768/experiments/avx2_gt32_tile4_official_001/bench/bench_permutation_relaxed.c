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

extern void gt32_tile4_attr_forward_all_bm_soa_p_asm(int16_t *,
	const int16_t *);
extern void gt32_tile4_attr_repair_p_rows_asm(int16_t *, const int16_t *);

typedef void (*kernel_fn)(int16_t *, const int16_t *, const int16_t *);

static int16_t frontend_a[WORDS] __attribute__((aligned(64)));
static int16_t frontend_b[WORDS] __attribute__((aligned(64)));
static int16_t forward_a[WORDS] __attribute__((aligned(64)));
static int16_t forward_b[WORDS] __attribute__((aligned(64)));
static int16_t product_soa[WORDS] __attribute__((aligned(64)));
static int16_t product_aos[WORDS] __attribute__((aligned(64)));
static int16_t standard_rows[WORDS] __attribute__((aligned(64)));
static int16_t p_rows[WORDS] __attribute__((aligned(64)));
static int16_t repaired_rows[WORDS] __attribute__((aligned(64)));
static volatile uint64_t sink;
static uint32_t rng_state = 1;

static const unsigned plane_p[16] = {
	0, 8, 2, 10, 4, 12, 6, 14, 1, 9, 3, 11, 5, 13, 7, 15
};

static unsigned permute_q(unsigned q)
{
	return (q & ~6U) | ((q & 2U) << 1) | ((q & 4U) >> 1);
}

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
static void forward_standard(int16_t *out, const int16_t *in,
	const int16_t *unused)
{
	(void)unused;
	gt32_tile4_attr_forward_all_bm_soa_asm(out, in);
}

__attribute__((noinline))
static void forward_p(int16_t *out, const int16_t *in,
	const int16_t *unused)
{
	(void)unused;
	gt32_tile4_attr_forward_all_bm_soa_p_asm(out, in);
}

__attribute__((noinline))
static void two_forward_standard(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	gt32_tile4_attr_forward_all_bm_soa_asm(out, a);
	gt32_tile4_attr_forward_all_bm_soa_asm(forward_b, b);
}

__attribute__((noinline))
static void two_forward_p(int16_t *out, const int16_t *a, const int16_t *b)
{
	gt32_tile4_attr_forward_all_bm_soa_p_asm(out, a);
	gt32_tile4_attr_forward_all_bm_soa_p_asm(forward_b, b);
}

__attribute__((noinline))
static void t9_standard(int16_t *out, const int16_t *rows,
	const int16_t *unused)
{
	(void)unused;
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out, rows);
}

__attribute__((noinline))
static void repair_then_t9(int16_t *out, const int16_t *rows,
	const int16_t *unused)
{
	const int16_t *const p_domain_rows = unused != NULL ? unused : rows;
	gt32_tile4_attr_repair_p_rows_asm(repaired_rows, p_domain_rows);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out, repaired_rows);
}

static void check_forward_p(const int16_t *standard, const int16_t *p)
{
	for (unsigned group = 0; group < 12; group++)
		for (unsigned coefficient = 0; coefficient < 4; coefficient++)
			for (unsigned lane = 0; lane < 16; lane++) {
				const unsigned base = 64U * group + 16U * coefficient;
				if (p[base + lane] != standard[base + plane_p[lane]]) {
					fprintf(stderr,
						"Forward-P mismatch group=%u c=%u lane=%u\n",
						group, coefficient, lane);
					exit(1);
				}
			}
}

static void make_p_rows(int16_t *p, const int16_t *standard)
{
	for (unsigned tile = 0; tile < 6; tile++)
		for (unsigned physical_q = 0; physical_q < 32; physical_q++) {
			const unsigned logical_q = permute_q(physical_q);
			for (unsigned coefficient = 0; coefficient < 4; coefficient++) {
				const unsigned destination = 128U * tile
					+ 16U * (physical_q / 4U)
					+ 4U * (physical_q % 4U) + coefficient;
				const unsigned source = 128U * tile
					+ 16U * (logical_q / 4U)
					+ 4U * (logical_q % 4U) + coefficient;
				p[destination] = standard[source];
			}
		}
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
	int16_t input_a[WORDS] __attribute__((aligned(64)));
	int16_t input_b[WORDS] __attribute__((aligned(64)));
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
	gt32_tile4_frontend_wide_raw_asm(frontend_b, input_b);
	forward_standard(out0, frontend_a, NULL);
	forward_p(out1, frontend_a, NULL);
	check_forward_p(out0, out1);

	memcpy(forward_a, out0, sizeof(forward_a));
	gt32_tile4_attr_forward_all_bm_soa_asm(forward_b, frontend_b);
	gt32_tile4_attr_basemul_c3_soa_asm(product_soa, forward_a, forward_b);
	gt32_tile4_attr_transpose_one_asm(product_aos, product_soa);
	gt32_tile4_inverse_all_pair_asm(standard_rows, product_aos);
	make_p_rows(p_rows, standard_rows);
	gt32_tile4_attr_repair_p_rows_asm(repaired_rows, p_rows);
	if (memcmp(repaired_rows, standard_rows, sizeof(standard_rows)) != 0) {
		fprintf(stderr, "P-row repair differential failed\n");
		return 1;
	}
	t9_standard(out0, standard_rows, NULL);
	repair_then_t9(out1, p_rows, NULL);
	if (memcmp(out0, out1, sizeof(out0)) != 0) {
		fprintf(stderr, "repair+T9 differential failed\n");
		return 1;
	}
	for (unsigned trial = 0; trial < 64; trial++) {
		for (unsigned i = 0; i < WORDS; i++)
			input_a[i] = (int16_t)((int)(next_random() & 7U) - 3);
		gt32_tile4_frontend_wide_raw_asm(frontend_a, input_a);
		forward_standard(out0, frontend_a, NULL);
		forward_p(out1, frontend_a, NULL);
		check_forward_p(out0, out1);
		for (unsigned i = 0; i < WORDS; i++)
			standard_rows[i] = (int16_t)((int)(next_random() % 4001U) - 2000);
		make_p_rows(p_rows, standard_rows);
		gt32_tile4_attr_repair_p_rows_asm(repaired_rows, p_rows);
		if (memcmp(repaired_rows, standard_rows, sizeof(standard_rows)) != 0) {
			fprintf(stderr, "random P-row repair differential failed\n");
			return 1;
		}
		t9_standard(out0, standard_rows, NULL);
		repair_then_t9(out1, p_rows, NULL);
		if (memcmp(out0, out1, sizeof(out0)) != 0) {
			fprintf(stderr, "random repair+T9 differential failed\n");
			return 1;
		}
	}
	/* Restore the caller-shaped rows used by the timing gate. */
	gt32_tile4_frontend_wide_raw_asm(frontend_a, input_a);
	gt32_tile4_frontend_wide_raw_asm(frontend_b, input_b);
	gt32_tile4_attr_forward_all_bm_soa_asm(forward_a, frontend_a);
	gt32_tile4_attr_forward_all_bm_soa_asm(forward_b, frontend_b);
	gt32_tile4_attr_basemul_c3_soa_asm(product_soa, forward_a, forward_b);
	gt32_tile4_attr_transpose_one_asm(product_aos, product_soa);
	gt32_tile4_inverse_all_pair_asm(standard_rows, product_aos);
	make_p_rows(p_rows, standard_rows);

	const struct gate gates[] = {
		{"forward_core", forward_standard, forward_p, frontend_a, NULL},
		{"two_forward_cores", two_forward_standard, two_forward_p,
			frontend_a, frontend_b},
		{"materialized_repair_plus_t9", t9_standard, repair_then_t9,
			standard_rows, p_rows},
	};
	for (unsigned gate = 0; gate < sizeof(gates) / sizeof(gates[0]); gate++)
		for (unsigned warm = 0; warm < 2; warm++) {
			(void)measure(gates[gate].baseline, out0, gates[gate].a,
				gates[gate].b, 1000);
			(void)measure(gates[gate].candidate, out1, gates[gate].a,
				gates[gate].b, 1000);
		}
	printf("META,correctness=pass,iterations=%u,samples=%u\n",
		iterations, SAMPLES);
	for (unsigned gate = 0; gate < sizeof(gates) / sizeof(gates[0]); gate++)
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
			printf("SAMPLE,%s,%u,%.6f,%.6f,%.6f\n",
				gates[gate].name, sample, baseline, candidate,
				candidate - baseline);
		}
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}
