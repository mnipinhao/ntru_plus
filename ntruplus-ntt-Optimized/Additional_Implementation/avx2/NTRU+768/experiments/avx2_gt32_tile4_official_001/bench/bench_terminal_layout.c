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

extern void gt32_tile4_attr_forward_all_bm_soa_p_asm(int16_t *,
	const int16_t *);

static int16_t aos_a[WORDS] __attribute__((aligned(64)));
static int16_t aos_b[WORDS] __attribute__((aligned(64)));
static int16_t soa_a[WORDS] __attribute__((aligned(64)));
static int16_t soa_b[WORDS] __attribute__((aligned(64)));
static int16_t qpair_a[WORDS] __attribute__((aligned(64)));
static int16_t qpair_b[WORDS] __attribute__((aligned(64)));
static int16_t p_a[WORDS] __attribute__((aligned(64)));
static int16_t p_b[WORDS] __attribute__((aligned(64)));
static int16_t l1_a[WORDS] __attribute__((aligned(64)));
static int16_t l1_b[WORDS] __attribute__((aligned(64)));
static int16_t l2_a[WORDS] __attribute__((aligned(64)));
static int16_t l2_b[WORDS] __attribute__((aligned(64)));
static int16_t product_soa[WORDS] __attribute__((aligned(64)));
static volatile uint64_t sink;
static uint32_t rng_state = 1;

static const unsigned qpair02_lane[16] = {
	0, 8, 1, 9, 4, 12, 5, 13, 2, 10, 3, 11, 6, 14, 7, 15
};
static const unsigned p_lane[16] = {
	0, 8, 2, 10, 4, 12, 6, 14, 1, 9, 3, 11, 5, 13, 7, 15
};

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
static void terminal_bm_aos(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	gt32_tile4_forward_all_pair_asm(aos_a, a);
	gt32_tile4_forward_all_pair_asm(aos_b, b);
	gt32_tile4_basemul_c3center_late_aos_private_asm(out, aos_a, aos_b);
}

__attribute__((noinline))
static void terminal_bm_standard_soa(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	gt32_tile4_attr_forward_all_bm_soa_asm(soa_a, a);
	gt32_tile4_attr_forward_all_bm_soa_asm(soa_b, b);
	gt32_tile4_attr_basemul_c3_soa_asm(product_soa, soa_a, soa_b);
	gt32_tile4_attr_transpose_one_asm(out, product_soa);
}

__attribute__((noinline))
static void terminal_bm_standard_soa_aos(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	gt32_tile4_attr_forward_all_bm_soa_asm(soa_a, a);
	gt32_tile4_forward_all_pair_asm(aos_b, b);
	gt32_tile4_basemul_scale_soa_aos_to_aos_private_asm(out, soa_a,
		aos_b);
}

__attribute__((noinline))
static void terminal_bm_l1_aos(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	gt32_tile4_attr_forward_all_bm_l1_asm(l1_a, a);
	gt32_tile4_forward_all_pair_asm(aos_b, b);
	gt32_tile4_attr_basemul_c3_l1_aos_asm(out, l1_a, aos_b);
}

__attribute__((noinline))
static void terminal_bm_l1_l1(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	gt32_tile4_attr_forward_all_bm_l1_asm(l1_a, a);
	gt32_tile4_attr_forward_all_bm_l1_asm(l1_b, b);
	gt32_tile4_attr_basemul_c3_l1_l1_asm(out, l1_a, l1_b);
}

__attribute__((noinline))
static void terminal_bm_l2_aos(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	gt32_tile4_attr_forward_all_bm_l2_asm(l2_a, a);
	gt32_tile4_forward_all_pair_asm(aos_b, b);
	gt32_tile4_attr_basemul_c3_l2_aos_asm(out, l2_a, aos_b);
}

__attribute__((noinline))
static void terminal_bm_l2_l2(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	gt32_tile4_attr_forward_all_bm_l2_asm(l2_a, a);
	gt32_tile4_attr_forward_all_bm_l2_asm(l2_b, b);
	gt32_tile4_attr_basemul_c3_l2_l2_asm(out, l2_a, l2_b);
}

__attribute__((noinline))
static void terminal_bm_soa_l2(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	gt32_tile4_attr_forward_all_bm_soa_asm(soa_a, a);
	gt32_tile4_attr_forward_all_bm_l2_asm(l2_b, b);
	gt32_tile4_attr_basemul_c3_soa_l2_asm(out, soa_a, l2_b);
}

__attribute__((noinline))
static void terminal_bm_l2_soa(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	gt32_tile4_attr_forward_all_bm_l2_asm(l2_a, a);
	gt32_tile4_attr_forward_all_bm_soa_asm(soa_b, b);
	gt32_tile4_attr_basemul_c3_l2_soa_asm(out, l2_a, soa_b);
}

__attribute__((noinline))
static void terminal_bm_qpair02(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	gt32_tile4_attr_forward_all_bm_soa_qpair02_asm(qpair_a, a);
	gt32_tile4_attr_forward_all_bm_soa_qpair02_asm(qpair_b, b);
	gt32_tile4_attr_basemul_c3_qpair02_to_aos_asm(out, qpair_a, qpair_b);
}

__attribute__((noinline))
static void terminal_bm_p(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	gt32_tile4_attr_forward_all_bm_soa_p_asm(p_a, a);
	gt32_tile4_attr_forward_all_bm_soa_p_asm(p_b, b);
	gt32_tile4_attr_basemul_c3_p_to_aos_asm(out, p_a, p_b);
}

static int check_qpair_mapping(const int16_t *standard,
	const int16_t *qpair)
{
	for (unsigned block = 0; block < 12; block++)
		for (unsigned coefficient = 0; coefficient < 4; coefficient++)
			for (unsigned lane = 0; lane < 16; lane++) {
				const unsigned base = 64U * block + 16U * coefficient;
				if (qpair[base + lane]
						!= standard[base + qpair02_lane[lane]]) {
					fprintf(stderr,
						"mapping block=%u c=%u lane=%u expected-lane=%u expected=%d got=%d\n",
						block, coefficient, lane, qpair02_lane[lane],
						standard[base + qpair02_lane[lane]],
						qpair[base + lane]);
					return 0;
				}
			}
	return 1;
}

static int check_p_mapping(const int16_t *standard, const int16_t *p)
{
	for (unsigned block = 0; block < 12; block++)
		for (unsigned coefficient = 0; coefficient < 4; coefficient++)
			for (unsigned lane = 0; lane < 16; lane++) {
				const unsigned base = 64U * block + 16U * coefficient;
				if (p[base + lane] != standard[base + p_lane[lane]])
					return 0;
			}
	return 1;
}

static int check_case(const int16_t *frontend_a, const int16_t *frontend_b)
{
	int16_t out_aos[WORDS] __attribute__((aligned(64)));
	int16_t out_soa[WORDS] __attribute__((aligned(64)));
	int16_t out_qpair[WORDS] __attribute__((aligned(64)));
	int16_t out_p[WORDS] __attribute__((aligned(64)));
	int16_t out_standard_mixed[WORDS] __attribute__((aligned(64)));
	int16_t out_l1_aos[WORDS] __attribute__((aligned(64)));
	int16_t out_l1_l1[WORDS] __attribute__((aligned(64)));
	int16_t out_l2_aos[WORDS] __attribute__((aligned(64)));
	int16_t out_l2_l2[WORDS] __attribute__((aligned(64)));
	int16_t out_soa_l2[WORDS] __attribute__((aligned(64)));
	int16_t out_l2_soa[WORDS] __attribute__((aligned(64)));

	gt32_tile4_attr_forward_all_bm_soa_asm(soa_a, frontend_a);
	gt32_tile4_attr_forward_all_bm_soa_qpair02_asm(qpair_a, frontend_a);
	if (!check_qpair_mapping(soa_a, qpair_a)) {
		fprintf(stderr, "qpair02 forward mapping failed\n");
		return 0;
	}
	gt32_tile4_attr_forward_all_bm_soa_p_asm(p_a, frontend_a);
	if (!check_p_mapping(soa_a, p_a)) {
		fprintf(stderr, "P forward mapping failed\n");
		return 0;
	}
	terminal_bm_aos(out_aos, frontend_a, frontend_b);
	terminal_bm_standard_soa(out_soa, frontend_a, frontend_b);
	terminal_bm_qpair02(out_qpair, frontend_a, frontend_b);
	terminal_bm_p(out_p, frontend_a, frontend_b);
	terminal_bm_standard_soa_aos(out_standard_mixed, frontend_a, frontend_b);
	terminal_bm_l1_aos(out_l1_aos, frontend_a, frontend_b);
	terminal_bm_l1_l1(out_l1_l1, frontend_a, frontend_b);
	terminal_bm_l2_aos(out_l2_aos, frontend_a, frontend_b);
	terminal_bm_l2_l2(out_l2_l2, frontend_a, frontend_b);
	terminal_bm_soa_l2(out_soa_l2, frontend_a, frontend_b);
	terminal_bm_l2_soa(out_l2_soa, frontend_a, frontend_b);
	if (memcmp(out_aos, out_soa, sizeof(out_aos)) != 0) {
		fprintf(stderr, "standard SoA BM control failed\n");
		return 0;
	}
	if (memcmp(out_aos, out_qpair, sizeof(out_aos)) != 0) {
		for (unsigned i = 0, shown = 0; i < WORDS && shown < 8; i++)
			if (out_aos[i] != out_qpair[i]) {
				fprintf(stderr, "qpair02 BM word %u: expected %d got %d\n",
					i, out_aos[i], out_qpair[i]);
				shown++;
			}
		return 0;
	}
	if (memcmp(out_aos, out_p, sizeof(out_aos)) != 0) {
		fprintf(stderr, "P BM output-to-AoS differential failed\n");
		return 0;
	}
	if (memcmp(out_aos, out_standard_mixed, sizeof(out_aos)) != 0) {
		fprintf(stderr, "standard mixed SoA/AoS BM differential failed\n");
		return 0;
	}
	if (memcmp(out_aos, out_l1_aos, sizeof(out_aos)) != 0) {
		fprintf(stderr, "L1/AoS BM differential failed\n");
		return 0;
	}
	if (memcmp(out_aos, out_l1_l1, sizeof(out_aos)) != 0) {
		fprintf(stderr, "L1/L1 BM differential failed\n");
		return 0;
	}
	if (memcmp(out_aos, out_l2_aos, sizeof(out_aos)) != 0) {
		fprintf(stderr, "L2/AoS BM differential failed\n");
		return 0;
	}
	if (memcmp(out_aos, out_l2_l2, sizeof(out_aos)) != 0) {
		fprintf(stderr, "L2/L2 BM differential failed\n");
		return 0;
	}
	if (memcmp(out_aos, out_soa_l2, sizeof(out_aos)) != 0) {
		fprintf(stderr, "SoA/L2 BM differential failed\n");
		return 0;
	}
	if (memcmp(out_aos, out_l2_soa, sizeof(out_aos)) != 0) {
		fprintf(stderr, "L2/SoA BM differential failed\n");
		return 0;
	}
	return 1;
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
	int16_t frontend_b[WORDS] __attribute__((aligned(64)));
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
	if (!check_case(frontend_a, frontend_b)) {
		fprintf(stderr, "terminal qpair02 deterministic differential failed\n");
		return 1;
	}
	for (unsigned trial = 0; trial < 64; trial++) {
		for (unsigned i = 0; i < WORDS; i++) {
			input_a[i] = (int16_t)((int)(next_random() & 7U) - 3);
			input_b[i] = (int16_t)((int)(next_random() & 7U) - 3);
		}
		gt32_tile4_frontend_wide_raw_asm(frontend_a, input_a);
		gt32_tile4_frontend_wide_raw_asm(frontend_b, input_b);
		if (!check_case(frontend_a, frontend_b)) {
			fprintf(stderr,
				"terminal qpair02 random differential failed at %u\n",
				trial);
			return 1;
		}
	}

	const struct gate gates[] = {
		{"aos_vs_standard_soa", terminal_bm_aos,
			terminal_bm_standard_soa},
		{"aos_vs_p", terminal_bm_aos, terminal_bm_p},
		{"standard_soa_vs_p", terminal_bm_standard_soa,
			terminal_bm_p},
		{"aa_vs_l1a", terminal_bm_aos, terminal_bm_l1_aos},
		{"aa_vs_l1l1", terminal_bm_aos, terminal_bm_l1_l1},
		{"aa_vs_l2a", terminal_bm_aos, terminal_bm_l2_aos},
		{"aa_vs_l2l2", terminal_bm_aos, terminal_bm_l2_l2},
		{"sa_vs_l1a", terminal_bm_standard_soa_aos,
			terminal_bm_l1_aos},
		{"sa_vs_l2a", terminal_bm_standard_soa_aos,
			terminal_bm_l2_aos},
		{"sa_vs_l1l1", terminal_bm_standard_soa_aos,
			terminal_bm_l1_l1},
		{"sa_vs_l2l2", terminal_bm_standard_soa_aos,
			terminal_bm_l2_l2},
		{"ss_vs_l1l1", terminal_bm_standard_soa,
			terminal_bm_l1_l1},
		{"ss_vs_l2l2", terminal_bm_standard_soa,
			terminal_bm_l2_l2},
		{"l1a_vs_l1l1", terminal_bm_l1_aos,
			terminal_bm_l1_l1},
		{"l2a_vs_l2l2", terminal_bm_l2_aos,
			terminal_bm_l2_l2},
		{"sa_vs_soa_l2", terminal_bm_standard_soa_aos,
			terminal_bm_soa_l2},
		{"sa_vs_l2_soa", terminal_bm_standard_soa_aos,
			terminal_bm_l2_soa},
		{"l2l2_vs_soa_l2", terminal_bm_l2_l2,
			terminal_bm_soa_l2},
		{"l2l2_vs_l2_soa", terminal_bm_l2_l2,
			terminal_bm_l2_soa},
		{"soa_l2_vs_l2_soa", terminal_bm_soa_l2,
			terminal_bm_l2_soa},
	};
	for (unsigned gate = 0; gate < sizeof(gates) / sizeof(gates[0]); gate++)
		for (unsigned warm = 0; warm < 2; warm++) {
			(void)measure(gates[gate].baseline, out0, frontend_a,
				frontend_b, 500);
			(void)measure(gates[gate].candidate, out1, frontend_a,
				frontend_b, 500);
		}

	printf("META,correctness=pass,iterations=%u,samples=%u\n",
		iterations, SAMPLES);
	for (unsigned gate = 0; gate < sizeof(gates) / sizeof(gates[0]); gate++)
		for (unsigned sample = 0; sample < SAMPLES; sample++) {
			double baseline;
			double candidate;
			if ((sample & 1U) == 0U) {
				baseline = measure(gates[gate].baseline, out0,
					frontend_a, frontend_b, iterations);
				candidate = measure(gates[gate].candidate, out1,
					frontend_a, frontend_b, iterations);
			} else {
				candidate = measure(gates[gate].candidate, out1,
					frontend_a, frontend_b, iterations);
				baseline = measure(gates[gate].baseline, out0,
					frontend_a, frontend_b, iterations);
			}
			printf("SAMPLE,%s,%u,%.6f,%.6f,%.6f\n",
				gates[gate].name, sample, baseline, candidate,
				candidate - baseline);
		}
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}
