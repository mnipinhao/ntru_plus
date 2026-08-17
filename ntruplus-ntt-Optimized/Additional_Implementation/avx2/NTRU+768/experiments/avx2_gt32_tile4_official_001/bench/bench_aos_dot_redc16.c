#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <x86intrin.h>

#include "tile4.h"

#define WORDS GT32_TILE4_POLY_WORDS
#define SAMPLES 20U
#define Q 3457

typedef void (*kernel_fn)(int16_t *, const int16_t *, const int16_t *);

void poly_crepmod3(int16_t *);

static int16_t input_a[WORDS] __attribute__((aligned(64)));
static int16_t input_b[WORDS] __attribute__((aligned(64)));
static int16_t product[WORDS] __attribute__((aligned(64)));
static int16_t rows[WORDS] __attribute__((aligned(64)));
static int16_t tail[WORDS] __attribute__((aligned(64)));
static volatile uint64_t sink;

static uint32_t rng_state = 0x6d5a56e9U;

static uint32_t random_u32(void)
{
	rng_state ^= rng_state << 13;
	rng_state ^= rng_state >> 17;
	rng_state ^= rng_state << 5;
	return rng_state;
}

static int mod_q(int value)
{
	int result = value % Q;
	if (result < 0)
		result += Q;
	return result;
}

static int crepmod3_contract(int value)
{
	int result = mod_q(value) % 3;
	if (result == 2)
		result = -1;
	return result;
}

static void fail_at(const char *label, unsigned trial, unsigned word,
	int actual, int expected)
{
	fprintf(stderr, "%s failed at trial=%u word=%u: got=%d want=%d\n",
		label, trial, word, actual, expected);
	exit(1);
}

static void compare_exact(const char *label, unsigned trial,
	const int16_t *actual, const int16_t *expected)
{
	for (unsigned i = 0; i < WORDS; i++)
		if (actual[i] != expected[i])
			fail_at(label, trial, i, actual[i], expected[i]);
}

static void compare_mod_q(const char *label, unsigned trial,
	const int16_t *actual, const int16_t *expected)
{
	for (unsigned i = 0; i < WORDS; i++)
		if (mod_q(actual[i]) != mod_q(expected[i]))
			fail_at(label, trial, i, mod_q(actual[i]), mod_q(expected[i]));
}

static void compare_crepmod3(const char *label, unsigned trial,
	const int16_t *actual, const int16_t *expected)
{
	for (unsigned i = 0; i < WORDS; i++) {
		const int got = crepmod3_contract(actual[i]);
		const int want = crepmod3_contract(expected[i]);
		if (got != want)
			fail_at(label, trial, i, got, want);
	}
}

static void fill_coefficients(int16_t *a, int16_t *b, unsigned trial)
{
	for (unsigned i = 0; i < WORDS; i++) {
		if (trial == 0U) {
			a[i] = 0;
			b[i] = 0;
		} else if (trial == 1U) {
			a[i] = (int16_t)((i & 1U) == 0U ? -3 : 4);
			b[i] = (int16_t)((i & 2U) == 0U ? 4 : -3);
		} else if (trial == 2U) {
			a[i] = 4;
			b[i] = -3;
		} else {
			a[i] = (int16_t)((int)(random_u32() & 7U) - 3);
			b[i] = (int16_t)((int)(random_u32() & 7U) - 3);
		}
	}
}

static void check_alias(const char *label, unsigned trial, kernel_fn fn,
	const int16_t *a, const int16_t *b, const int16_t *expected)
{
	int16_t alias[WORDS] __attribute__((aligned(64)));

	memcpy(alias, a, sizeof(alias));
	fn(alias, alias, b);
	compare_exact(label, trial, alias, expected);
	memcpy(alias, b, sizeof(alias));
	fn(alias, a, alias);
	compare_exact(label, trial, alias, expected);
}

static void correctness(void)
{
	int16_t coefficients_a[WORDS] __attribute__((aligned(64)));
	int16_t coefficients_b[WORDS] __attribute__((aligned(64)));
	int16_t a[WORDS] __attribute__((aligned(64)));
	int16_t b[WORDS] __attribute__((aligned(64)));
	int16_t a1[WORDS] __attribute__((aligned(64)));
	int16_t u_intrinsic[WORDS] __attribute__((aligned(64)));
	int16_t u_asm[WORDS] __attribute__((aligned(64)));
	int16_t s_intrinsic[WORDS] __attribute__((aligned(64)));
	int16_t s_asm[WORDS] __attribute__((aligned(64)));
	int16_t a1_rows[WORDS] __attribute__((aligned(64)));
	int16_t u_rows[WORDS] __attribute__((aligned(64)));
	int16_t s_rows[WORDS] __attribute__((aligned(64)));
	int16_t a1_tail[WORDS] __attribute__((aligned(64)));
	int16_t u_tail[WORDS] __attribute__((aligned(64)));
	int16_t s_tail[WORDS] __attribute__((aligned(64)));
	int16_t a1_crep[WORDS] __attribute__((aligned(64)));
	int16_t u_crep[WORDS] __attribute__((aligned(64)));
	int16_t s_crep[WORDS] __attribute__((aligned(64)));

	for (unsigned trial = 0; trial < 1000U; trial++) {
		fill_coefficients(coefficients_a, coefficients_b, trial);
		gt32_tile4_forward_full_wide_raw_pair_align64_asm(a, coefficients_a);
		gt32_tile4_forward_full_wide_raw_pair_align64_asm(b, coefficients_b);
		gt32_tile4_basemul_wide_a1_intrinsic(a1, a, b);
		gt32_tile4_basemul_wide_r1u_intrinsic(u_intrinsic, a, b);
		gt32_tile4_basemul_aos_dot_r1u_asm(u_asm, a, b);
		gt32_tile4_basemul_wide_r1s_intrinsic(s_intrinsic, a, b);
		gt32_tile4_basemul_aos_dot_r1s_asm(s_asm, a, b);

		compare_exact("R1-U-intrinsic-vs-R0", trial, u_intrinsic, a1);
		compare_exact("R1-U-asm-vs-R0", trial, u_asm, a1);
		compare_exact("R1-S-asm-vs-intrinsic", trial, s_asm, s_intrinsic);
		compare_mod_q("R1-S-vs-R0", trial, s_asm, a1);
		for (unsigned i = 0; i < WORDS; i++) {
			const int delta = (int)s_asm[i] - (int)a1[i];
			if (delta != 0 && delta != Q)
				fail_at("R1-S-representative", trial, i, delta, 0);
		}

		/* Canonical Encodeq-equivalence at the e=-1 representation boundary. */
		compare_mod_q("R1-U-canonical", trial, u_asm, a1);
		compare_mod_q("R1-S-canonical", trial, s_asm, a1);

		if (trial < 16U) {
			check_alias("R1-U-alias", trial,
				gt32_tile4_basemul_aos_dot_r1u_asm, a, b, a1);
			check_alias("R1-S-alias", trial,
				gt32_tile4_basemul_aos_dot_r1s_asm, a, b, s_asm);
		}

		gt32_tile4_inverse_all_pair_asm(a1_rows, a1);
		gt32_tile4_inverse_all_pair_asm(u_rows, u_asm);
		gt32_tile4_inverse_all_pair_asm(s_rows, s_asm);
		compare_exact("R1-U-I1", trial, u_rows, a1_rows);
		compare_mod_q("R1-S-I1", trial, s_rows, a1_rows);
		gt32_tile4_inverse_tail_t9_isolated_private_asm(a1_tail, a1_rows);
		gt32_tile4_inverse_tail_t9_isolated_private_asm(u_tail, u_rows);
		gt32_tile4_inverse_tail_t9_isolated_private_asm(s_tail, s_rows);
		compare_exact("R1-U-T9", trial, u_tail, a1_tail);
		compare_mod_q("R1-S-T9", trial, s_tail, a1_tail);
		compare_crepmod3("R1-S-crepmod3", trial, s_tail, a1_tail);
		memcpy(a1_crep, a1_tail, sizeof(a1_crep));
		memcpy(u_crep, u_tail, sizeof(u_crep));
		memcpy(s_crep, s_tail, sizeof(s_crep));
		poly_crepmod3(a1_crep);
		poly_crepmod3(u_crep);
		poly_crepmod3(s_crep);
		compare_exact("R1-U-poly-crepmod3", trial, u_crep, a1_crep);
		compare_exact("R1-S-poly-crepmod3", trial, s_crep, a1_crep);
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
static void a1_i1(int16_t *out, const int16_t *a, const int16_t *b)
{
	gt32_tile4_basemul_wide_a1_intrinsic(product, a, b);
	gt32_tile4_inverse_all_pair_asm(out, product);
}

__attribute__((noinline))
static void r1u_i1(int16_t *out, const int16_t *a, const int16_t *b)
{
	gt32_tile4_basemul_aos_dot_r1u_asm(product, a, b);
	gt32_tile4_inverse_all_pair_asm(out, product);
}

__attribute__((noinline))
static void r1s_i1(int16_t *out, const int16_t *a, const int16_t *b)
{
	gt32_tile4_basemul_aos_dot_r1s_asm(product, a, b);
	gt32_tile4_inverse_all_pair_asm(out, product);
}

__attribute__((noinline))
static void b3_i1(int16_t *out, const int16_t *a, const int16_t *b)
{
	gt32_tile4_basemul_b3_late_asm(product, a, b);
	gt32_tile4_inverse_all_pair_asm(out, product);
}

__attribute__((noinline))
static void a1_full(int16_t *out, const int16_t *a, const int16_t *b)
{
	a1_i1(rows, a, b);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out, rows);
	poly_crepmod3(out);
}

__attribute__((noinline))
static void r1u_full(int16_t *out, const int16_t *a, const int16_t *b)
{
	r1u_i1(rows, a, b);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out, rows);
	poly_crepmod3(out);
}

__attribute__((noinline))
static void r1s_full(int16_t *out, const int16_t *a, const int16_t *b)
{
	r1s_i1(rows, a, b);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out, rows);
	poly_crepmod3(out);
}

__attribute__((noinline))
static void b3_full(int16_t *out, const int16_t *a, const int16_t *b)
{
	b3_i1(rows, a, b);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out, rows);
	poly_crepmod3(out);
}

struct gate {
	const char *name;
	kernel_fn baseline;
	kernel_fn candidate;
};

static void run_gate(const struct gate *gate, unsigned iterations)
{
	for (unsigned warmup = 0; warmup < 2U; warmup++) {
		(void)measure(gate->baseline, tail, input_a, input_b, 100U);
		(void)measure(gate->candidate, tail, input_a, input_b, 100U);
	}
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		double baseline;
		double candidate;
		if ((sample & 1U) == 0U) {
			baseline = measure(gate->baseline, tail, input_a, input_b,
				iterations);
			candidate = measure(gate->candidate, tail, input_a, input_b,
				iterations);
		} else {
			candidate = measure(gate->candidate, tail, input_a, input_b,
				iterations);
			baseline = measure(gate->baseline, tail, input_a, input_b,
				iterations);
		}
		printf("SAMPLE,%s,%u,%.6f,%.6f,%.6f\n", gate->name, sample,
			baseline, candidate, candidate - baseline);
	}
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc >= 2
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	int16_t coefficients_a[WORDS] __attribute__((aligned(64)));
	int16_t coefficients_b[WORDS] __attribute__((aligned(64)));
	cpu_set_t cpuset;
	const struct gate gates[] = {
		{"a1_vs_r1u_bm", gt32_tile4_basemul_wide_a1_intrinsic,
			gt32_tile4_basemul_aos_dot_r1u_asm},
		{"a1_vs_r1s_bm", gt32_tile4_basemul_wide_a1_intrinsic,
			gt32_tile4_basemul_aos_dot_r1s_asm},
		{"b3_vs_r1u_bm", gt32_tile4_basemul_b3_late_asm,
			gt32_tile4_basemul_aos_dot_r1u_asm},
		{"b3_vs_r1s_bm", gt32_tile4_basemul_b3_late_asm,
			gt32_tile4_basemul_aos_dot_r1s_asm},
		{"a1_vs_r1u_i1", a1_i1, r1u_i1},
		{"a1_vs_r1s_i1", a1_i1, r1s_i1},
		{"b3_vs_r1u_i1", b3_i1, r1u_i1},
		{"b3_vs_r1s_i1", b3_i1, r1s_i1},
		{"a1_vs_r1u_full", a1_full, r1u_full},
		{"a1_vs_r1s_full", a1_full, r1s_full},
		{"b3_vs_r1u_full", b3_full, r1u_full},
		{"b3_vs_r1s_full", b3_full, r1s_full},
	};

	CPU_ZERO(&cpuset);
	CPU_SET(1, &cpuset);
	if (sched_setaffinity(0, sizeof(cpuset), &cpuset) != 0)
		perror("sched_setaffinity");
	correctness();
	fill_coefficients(coefficients_a, coefficients_b, 99U);
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(input_a,
		coefficients_a);
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(input_b,
		coefficients_b);
	printf("META,experiment=GT32-AOS-DOT-REDC16-001,correctness=pass,"
		"trials=1000,iterations=%u,samples=%u,sink=%llu\n",
		iterations, SAMPLES, (unsigned long long)sink);
	for (unsigned i = 0; i < sizeof(gates) / sizeof(gates[0]); i++)
		run_gate(&gates[i], iterations);
	return 0;
}
