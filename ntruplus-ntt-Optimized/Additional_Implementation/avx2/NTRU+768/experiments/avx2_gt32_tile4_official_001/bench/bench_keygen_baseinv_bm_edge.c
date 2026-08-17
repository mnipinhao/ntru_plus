#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <x86intrin.h>

#include "tile4.h"

#define WORDS 768
#define DET_WORDS 192
#define TRIALS 1000

extern void gt32_tile4_attr_forward_all_baseinv_p_l3_asm(int16_t *,
	const int16_t *);
extern int gt32_p_baseinv_direct_asm_avx2(int16_t *, const int16_t *);
extern int gt32_p_baseinv_prepare_inverse_asm_avx2(int16_t *, int16_t *,
	const int16_t *);
extern void gt32_p_baseinv_apply_inverse_avx2(int16_t *, const int16_t *);
extern void gt32_p_baseinv_apply_inverse_bm_avx2(int16_t *, const int16_t *,
	const int16_t *, const int16_t *);
extern void gt32_p_baseinv_apply_inverse_bm_asm(int16_t *, const int16_t *,
	const int16_t *, const int16_t *);
extern void gt32_p_baseinv_apply_inverse_bm_control_asm(int16_t *,
	const int16_t *, const int16_t *, const int16_t *, int16_t *);
extern void gt_basemul_native_asm_avx2(int16_t *, const int16_t *,
	const int16_t *);

static int16_t coeff[WORDS] __attribute__((aligned(64)));
static int16_t frontend[WORDS] __attribute__((aligned(64)));
static int16_t f[WORDS] __attribute__((aligned(64)));
static int16_t g[WORDS] __attribute__((aligned(64)));
static int16_t pre_f[WORDS] __attribute__((aligned(64)));
static int16_t pre_g[WORDS] __attribute__((aligned(64)));
static int16_t det_f[DET_WORDS] __attribute__((aligned(64)));
static int16_t det_g[DET_WORDS] __attribute__((aligned(64)));
static int16_t direct_inverse[WORDS] __attribute__((aligned(64)));
static int16_t control_h[WORDS] __attribute__((aligned(64)));
static int16_t control_hinv[WORDS] __attribute__((aligned(64)));
static int16_t candidate_h[WORDS] __attribute__((aligned(64)));
static int16_t candidate_hinv[WORDS] __attribute__((aligned(64)));
static int16_t inverse_scratch_f[WORDS] __attribute__((aligned(64)));
static int16_t inverse_scratch_g[WORDS] __attribute__((aligned(64)));
static volatile uint64_t sink;
static uint32_t rng = 0x4b334231U;

static uint32_t random32(void)
{
	rng ^= rng << 13;
	rng ^= rng >> 17;
	rng ^= rng << 5;
	return rng;
}

static int center(int value)
{
	value %= 3457;
	if (value < 0)
		value += 3457;
	if (value > 1728)
		value -= 3457;
	return value;
}

static int same_mod_q(const int16_t a[WORDS], const int16_t b[WORDS])
{
	for (unsigned i = 0; i < WORDS; i++)
		if (center(a[i]) != center(b[i]))
			return 0;
	return 1;
}

static void forward(int16_t out[WORDS])
{
	gt32_tile4_frontend_wide_raw_asm(frontend, coeff);
	gt32_tile4_attr_forward_all_baseinv_p_l3_asm(out, frontend);
}

static void sample_invertible(int16_t out[WORDS], unsigned add_one)
{
	for (;;) {
		for (unsigned i = 0; i < WORDS; i++)
			coeff[i] = (int16_t)((int)(random32() & 7U) - 3);
		if (add_one != 0)
			coeff[0]++;
		forward(out);
		if (gt32_p_baseinv_direct_asm_avx2(direct_inverse, out) == 0)
			return;
	}
}

__attribute__((noinline)) static void control_one(void)
{
	(void)gt32_p_baseinv_prepare_inverse_asm_avx2(pre_f, det_f, f);
	gt32_p_baseinv_apply_inverse_avx2(pre_f, det_f);
	gt_basemul_native_asm_avx2(control_h, g, pre_f);
}

__attribute__((noinline)) static void candidate_one(void)
{
	(void)gt32_p_baseinv_prepare_inverse_asm_avx2(pre_f, det_f, f);
	gt32_p_baseinv_apply_inverse_bm_asm(candidate_h, g, pre_f, det_f);
}

__attribute__((noinline)) static void control_two(void)
{
	control_one();
	(void)gt32_p_baseinv_prepare_inverse_asm_avx2(pre_g, det_g, g);
	gt32_p_baseinv_apply_inverse_avx2(pre_g, det_g);
	gt_basemul_native_asm_avx2(control_hinv, f, pre_g);
}

__attribute__((noinline)) static void candidate_two(void)
{
	candidate_one();
	(void)gt32_p_baseinv_prepare_inverse_asm_avx2(pre_g, det_g, g);
	gt32_p_baseinv_apply_inverse_bm_asm(candidate_hinv, f, pre_g, det_g);
}

__attribute__((noinline)) static void boundary_control_one(void)
{
	gt32_p_baseinv_apply_inverse_bm_control_asm(control_h, g, pre_f,
		det_f, inverse_scratch_f);
}

__attribute__((noinline)) static void boundary_candidate_one(void)
{
	gt32_p_baseinv_apply_inverse_bm_asm(candidate_h, g, pre_f, det_f);
}

__attribute__((noinline)) static void boundary_control_two(void)
{
	boundary_control_one();
	gt32_p_baseinv_apply_inverse_bm_control_asm(control_hinv, f, pre_g,
		det_g, inverse_scratch_g);
}

__attribute__((noinline)) static void boundary_candidate_two(void)
{
	boundary_candidate_one();
	gt32_p_baseinv_apply_inverse_bm_asm(candidate_hinv, f, pre_g, det_g);
}

static int differential(void)
{
	unsigned accepted = 0;
	int16_t split_inverse[WORDS] __attribute__((aligned(64)));
	int16_t split_pre[WORDS] __attribute__((aligned(64)));
	int16_t split_det[DET_WORDS] __attribute__((aligned(64)));

	memset(coeff, 0, sizeof coeff);
	forward(f);
	if (gt32_p_baseinv_prepare_inverse_asm_avx2(split_pre, split_det, f) == 0)
		return fprintf(stderr, "zero polynomial accepted\n"), 0;
	for (unsigned i = 0; i < WORDS; i++)
		if (split_pre[i] != 0)
			return fprintf(stderr, "failure output not zero\n"), 0;

	for (unsigned trial = 0; trial < TRIALS; trial++) {
		for (unsigned i = 0; i < WORDS; i++)
			coeff[i] = (int16_t)((int)(random32() & 7U) - 3);
		coeff[0]++;
		forward(f);
		const int direct_status =
			gt32_p_baseinv_direct_asm_avx2(direct_inverse, f);
		const int split_status =
			gt32_p_baseinv_prepare_inverse_asm_avx2(
				split_pre, split_det, f);
		if (direct_status != split_status)
			return fprintf(stderr, "status mismatch trial=%u\n", trial), 0;
		if (split_status != 0)
			continue;
		accepted++;
		memcpy(split_inverse, split_pre, sizeof split_inverse);
		gt32_p_baseinv_apply_inverse_avx2(split_inverse, split_det);
		if (!same_mod_q(direct_inverse, split_inverse))
			return fprintf(stderr, "inverse mismatch trial=%u\n", trial), 0;

		sample_invertible(g, 0);
		gt_basemul_native_asm_avx2(control_h, g, split_inverse);
		gt32_p_baseinv_apply_inverse_bm_avx2(
			candidate_h, g, split_pre, split_det);
		if (!same_mod_q(control_h, candidate_h))
			return fprintf(stderr, "edge mismatch trial=%u\n", trial), 0;
		gt32_p_baseinv_apply_inverse_bm_asm(
			candidate_h, g, split_pre, split_det);
		if (!same_mod_q(control_h, candidate_h))
			return fprintf(stderr, "asm edge mismatch trial=%u\n", trial), 0;
	}
	printf("correctness trials=%u accepted=%u\n", TRIALS, accepted);
	return accepted != 0;
}

typedef void (*region_fn)(void);

static int compare_i64(const void *left, const void *right)
{
	const int64_t a = *(const int64_t *)left;
	const int64_t b = *(const int64_t *)right;
	return (a > b) - (a < b);
}

static void run(region_fn fn, unsigned iterations)
{
	for (unsigned i = 0; i < iterations; i++)
		fn();
	sink += (uint16_t)control_h[iterations % WORDS] +
		(uint16_t)candidate_h[(iterations + 17U) % WORDS];
}

static uint64_t timed(region_fn fn, unsigned iterations)
{
	unsigned aux;
	_mm_lfence();
	const uint64_t begin = __rdtsc();
	run(fn, iterations);
	const uint64_t end = __rdtscp(&aux);
	_mm_lfence();
	return end - begin;
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1 ?
		(unsigned)strtoul(argv[1], 0, 0) : 10000;
	const char *gate = argc > 2 ? argv[2] : "two";
	const char *backend = argc > 3 ? argv[3] : "control";
	const int skip_check = argc > 4 && !strcmp(argv[4], "nocheck");
	cpu_set_t set;
	CPU_ZERO(&set);
	CPU_SET(1, &set);
	(void)sched_setaffinity(0, sizeof set, &set);

	if (!skip_check && !differential())
		return 1;
	sample_invertible(f, 1);
	sample_invertible(g, 0);
	(void)gt32_p_baseinv_prepare_inverse_asm_avx2(pre_f, det_f, f);
	(void)gt32_p_baseinv_prepare_inverse_asm_avx2(pre_g, det_g, g);
	if (!strcmp(backend, "paired")) {
		region_fn control = !strcmp(gate, "boundary-one") ?
			boundary_control_one : boundary_control_two;
		region_fn candidate = !strcmp(gate, "boundary-one") ?
			boundary_candidate_one : boundary_candidate_two;
		int64_t deltas[40];
		unsigned wins = 0;
		if (strcmp(gate, "boundary-one") && strcmp(gate, "boundary-two"))
			return 2;
		run(control, 1000);
		run(candidate, 1000);
		for (unsigned sample = 0; sample < 40; sample++) {
			uint64_t control_ticks;
			uint64_t candidate_ticks;
			if ((sample & 1U) == 0) {
				control_ticks = timed(control, iterations);
				candidate_ticks = timed(candidate, iterations);
			} else {
				candidate_ticks = timed(candidate, iterations);
				control_ticks = timed(control, iterations);
			}
			deltas[sample] = (int64_t)candidate_ticks -
				(int64_t)control_ticks;
			wins += deltas[sample] < 0;
			printf("KEDGE_PAIR,sample=%u,delta_per_call=%.6f\n",
				sample, (double)deltas[sample] / iterations);
		}
		qsort(deltas, 40, sizeof deltas[0], compare_i64);
		printf("KEDGE_SUMMARY,gate=%s,samples=40,wins=%u,"
			"median_delta_per_call=%.6f\n", gate, wins,
			((double)deltas[19] + (double)deltas[20]) /
				(2.0 * iterations));
		return 0;
	}

	region_fn fn = 0;
	if (!strcmp(gate, "one"))
		fn = !strcmp(backend, "control") ? control_one : candidate_one;
	else if (!strcmp(gate, "two"))
		fn = !strcmp(backend, "control") ? control_two : candidate_two;
	else if (!strcmp(gate, "boundary-one"))
		fn = !strcmp(backend, "control") ?
			boundary_control_one : boundary_candidate_one;
	else if (!strcmp(gate, "boundary-two"))
		fn = !strcmp(backend, "control") ?
			boundary_control_two : boundary_candidate_two;
	if (fn == 0 || (strcmp(backend, "control") &&
		strcmp(backend, "candidate")))
		return 2;
	run(fn, 1000);
	const uint64_t ticks = timed(fn, iterations);
	printf("KEDGE_PMU,gate=%s,backend=%s,iterations=%u,correctness=pass,"
		"tsc_per_call=%.6f,sink=%llu\n", gate, backend, iterations,
		(double)ticks / iterations, (unsigned long long)sink);
	return 0;
}
