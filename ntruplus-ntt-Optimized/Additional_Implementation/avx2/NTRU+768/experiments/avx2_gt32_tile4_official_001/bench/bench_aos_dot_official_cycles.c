#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "tile4.h"

#define WORDS GT32_TILE4_POLY_WORDS

typedef void (*kernel_fn)(int16_t *, const int16_t *, const int16_t *);

void poly_ntt(int16_t *);
void poly_basemul_scale(int16_t *, const int16_t *, const int16_t *);
void poly_invntt_scale(int16_t *);
void poly_crepmod3(int16_t *);

static int16_t official_a[WORDS] __attribute__((aligned(64)));
static int16_t official_b[WORDS] __attribute__((aligned(64)));
static int16_t gt_a[WORDS] __attribute__((aligned(64)));
static int16_t gt_b[WORDS] __attribute__((aligned(64)));
static int16_t product[WORDS] __attribute__((aligned(64)));
static int16_t rows[WORDS] __attribute__((aligned(64)));
static int16_t work_a[WORDS] __attribute__((aligned(64)));
static int16_t work_b[WORDS] __attribute__((aligned(64)));
static int16_t output[WORDS] __attribute__((aligned(64)));
static volatile uint64_t sink;

__attribute__((noinline))
static void official_bm(int16_t *out, const int16_t *a, const int16_t *b)
{
	poly_basemul_scale(out, a, b);
}

__attribute__((noinline))
static void gt_r1u_bm(int16_t *out, const int16_t *a, const int16_t *b)
{
	gt32_tile4_basemul_aos_dot_r1u_asm(out, a, b);
}

__attribute__((noinline))
static void official_bm_inverse(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	poly_basemul_scale(out, a, b);
	poly_invntt_scale(out);
}

__attribute__((noinline))
static void gt_r1u_bm_inverse(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	gt32_tile4_basemul_aos_dot_r1u_asm(product, a, b);
	gt32_tile4_inverse_all_pair_asm(rows, product);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out, rows);
}

__attribute__((noinline))
static void official_full(int16_t *out, const int16_t *a, const int16_t *b)
{
	memcpy(work_a, a, sizeof(work_a));
	memcpy(work_b, b, sizeof(work_b));
	poly_ntt(work_a);
	poly_ntt(work_b);
	poly_basemul_scale(out, work_a, work_b);
	poly_invntt_scale(out);
}

__attribute__((noinline))
static void gt_r1u_full(int16_t *out, const int16_t *a, const int16_t *b)
{
	memcpy(work_a, a, sizeof(work_a));
	memcpy(work_b, b, sizeof(work_b));
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(work_a, work_a);
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(work_b, work_b);
	gt32_tile4_basemul_aos_dot_r1u_asm(product, work_a, work_b);
	gt32_tile4_inverse_all_pair_asm(rows, product);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out, rows);
}

__attribute__((noinline))
static void official_full_crep(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	official_full(out, a, b);
	poly_crepmod3(out);
}

__attribute__((noinline))
static void gt_r1u_full_crep(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	gt_r1u_full(out, a, b);
	poly_crepmod3(out);
}

struct gate {
	const char *name;
	kernel_fn official;
	kernel_fn gt;
	const int16_t *official_input_a;
	const int16_t *official_input_b;
	const int16_t *gt_input_a;
	const int16_t *gt_input_b;
};

static int centered_mod_q(int16_t value)
{
	int result = value % GT32_TILE4_Q;
	if (result < 0)
		result += GT32_TILE4_Q;
	if (result > GT32_TILE4_Q / 2)
		result -= GT32_TILE4_Q;
	return result;
}

static void compare_mod_q(const int16_t *official, const int16_t *gt)
{
	for (unsigned i = 0; i < WORDS; i++) {
		if (centered_mod_q(official[i]) != centered_mod_q(gt[i])) {
			fprintf(stderr, "Official/R1-U differential failed at %u\n", i);
			exit(1);
		}
	}
}

static void run(kernel_fn fn, int16_t *out, const int16_t *a,
	const int16_t *b, unsigned iterations)
{
	for (unsigned i = 0; i < iterations; i++)
		fn(out, a, b);
	sink += (uint16_t)out[iterations & 767U];
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 1000000U;
	const char *gate_name = argc > 2 ? argv[2] : "full_crep";
	const char *backend = argc > 3 ? argv[3] : "official";
	int16_t coefficients_a[WORDS] __attribute__((aligned(64)));
	int16_t coefficients_b[WORDS] __attribute__((aligned(64)));
	int16_t official_result[WORDS] __attribute__((aligned(64)));
	int16_t gt_result[WORDS] __attribute__((aligned(64)));
	cpu_set_t set;

	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof(set), &set) != 0)
		perror("sched_setaffinity");
	for (unsigned i = 0; i < WORDS; i++) {
		coefficients_a[i] = (int16_t)((int)(i % 8U) - 3);
		coefficients_b[i] = (int16_t)((int)((3U * i + 1U) % 8U) - 3);
	}
	memcpy(official_a, coefficients_a, sizeof(official_a));
	memcpy(official_b, coefficients_b, sizeof(official_b));
	memcpy(gt_a, coefficients_a, sizeof(gt_a));
	memcpy(gt_b, coefficients_b, sizeof(gt_b));
	poly_ntt(official_a);
	poly_ntt(official_b);
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(gt_a, gt_a);
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(gt_b, gt_b);

	const struct gate gates[] = {
		{"bm", official_bm, gt_r1u_bm,
			official_a, official_b, gt_a, gt_b},
		{"bm_inverse", official_bm_inverse, gt_r1u_bm_inverse,
			official_a, official_b, gt_a, gt_b},
		{"full", official_full, gt_r1u_full,
			coefficients_a, coefficients_b, coefficients_a, coefficients_b},
		{"full_crep", official_full_crep, gt_r1u_full_crep,
			coefficients_a, coefficients_b, coefficients_a, coefficients_b},
	};

	official_bm_inverse(official_result, official_a, official_b);
	gt_r1u_bm_inverse(gt_result, gt_a, gt_b);
	compare_mod_q(official_result, gt_result);
	official_full_crep(official_result, coefficients_a, coefficients_b);
	gt_r1u_full_crep(gt_result, coefficients_a, coefficients_b);
	if (memcmp(official_result, gt_result, sizeof(official_result)) != 0) {
		fprintf(stderr, "Official/R1-U crepmod3 differential failed\n");
		return 1;
	}

	for (unsigned gate = 0; gate < sizeof(gates) / sizeof(gates[0]); gate++) {
		if (strcmp(gates[gate].name, gate_name) != 0)
			continue;
		const int use_gt = strcmp(backend, "gt32-r1u") == 0;
		kernel_fn fn = use_gt ? gates[gate].gt : gates[gate].official;
		const int16_t *a = use_gt ? gates[gate].gt_input_a
			: gates[gate].official_input_a;
		const int16_t *b = use_gt ? gates[gate].gt_input_b
			: gates[gate].official_input_b;
		for (unsigned warmup = 0; warmup < 2U; warmup++)
			run(fn, output, a, b, 1000U);
		run(fn, output, a, b, iterations);
		printf("PMU,gate=%s,backend=%s,iterations=%u,sink=%llu\n",
			gate_name, backend, iterations, (unsigned long long)sink);
		return 0;
	}
	fprintf(stderr, "unknown gate/backend: %s/%s\n", gate_name, backend);
	return 2;
}
