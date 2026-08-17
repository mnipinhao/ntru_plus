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
#define CORRECTNESS_TRIALS 64

typedef struct {
	int16_t frontend[WORDS];
	int16_t operand_a[WORDS];
	int16_t operand_b[WORDS];
	int16_t product[WORDS];
	int16_t inverse_rows[WORDS];
} private_scratch_t;

typedef void (*private_polymul_fn)(int16_t *, const int16_t *,
	const int16_t *, private_scratch_t *);

void poly_crepmod3(int16_t *);

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

/* General N5 AoS remains the baseline ABI inside an otherwise identical caller. */
__attribute__((noinline))
static void polymul_private_gt32_aos(int16_t *out, const int16_t *a,
	const int16_t *b, private_scratch_t *scratch)
{
	gt32_tile4_frontend_wide_raw_asm(scratch->frontend, a);
	gt32_tile4_forward_all_pair_asm(scratch->operand_a, scratch->frontend);
	gt32_tile4_frontend_wide_raw_asm(scratch->frontend, b);
	gt32_tile4_forward_all_pair_asm(scratch->operand_b, scratch->frontend);
	gt32_tile4_basemul_c3center_late_aos_private_asm(scratch->product,
		scratch->operand_a, scratch->operand_b);
	gt32_tile4_inverse_all_pair_asm(scratch->inverse_rows, scratch->product);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out,
		scratch->inverse_rows);
	poly_crepmod3(out);
}

/*
 * Asymmetric representation island: only operand A is redeposited into
 * BM-native coefficient planes.  Operand B and every downstream boundary
 * retain the selected TILE4 AoS contract.
 */
__attribute__((noinline))
static void polymul_private_gt32_mixed(int16_t *out, const int16_t *a,
	const int16_t *b, private_scratch_t *scratch)
{
	gt32_tile4_frontend_wide_raw_asm(scratch->frontend, a);
	gt32_tile4_attr_forward_all_bm_soa_asm(scratch->operand_a,
		scratch->frontend);
	gt32_tile4_frontend_wide_raw_asm(scratch->frontend, b);
	gt32_tile4_forward_all_pair_asm(scratch->operand_b, scratch->frontend);
	gt32_tile4_basemul_scale_soa_aos_to_aos_private_asm(scratch->product,
		scratch->operand_a, scratch->operand_b);
	gt32_tile4_inverse_all_pair_asm(scratch->inverse_rows, scratch->product);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out,
		scratch->inverse_rows);
	poly_crepmod3(out);
}

/* Caller-private island: only the two forward results use BM-native planes. */
__attribute__((noinline))
static void polymul_private_gt32_soa(int16_t *out, const int16_t *a,
	const int16_t *b, private_scratch_t *scratch)
{
	gt32_tile4_frontend_wide_raw_asm(scratch->frontend, a);
	gt32_tile4_attr_forward_all_bm_soa_asm(scratch->operand_a,
		scratch->frontend);
	gt32_tile4_frontend_wide_raw_asm(scratch->frontend, b);
	gt32_tile4_attr_forward_all_bm_soa_asm(scratch->operand_b,
		scratch->frontend);
	gt32_tile4_attr_basemul_c3_soa_asm(scratch->product,
		scratch->operand_a, scratch->operand_b);
	/* Reuse dead frontend storage; the transpose leaf requires disjoint buffers. */
	gt32_tile4_attr_transpose_one_asm(scratch->frontend, scratch->product);
	gt32_tile4_inverse_all_pair_asm(scratch->inverse_rows, scratch->frontend);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out,
		scratch->inverse_rows);
	poly_crepmod3(out);
}

/* Transpose-cut island: both private forwards stop at L2; B3 resumes Q. */
__attribute__((noinline))
static void polymul_private_gt32_l2(int16_t *out, const int16_t *a,
	const int16_t *b, private_scratch_t *scratch)
{
	gt32_tile4_frontend_wide_raw_asm(scratch->frontend, a);
	gt32_tile4_attr_forward_all_bm_l2_asm(scratch->operand_a,
		scratch->frontend);
	gt32_tile4_frontend_wide_raw_asm(scratch->frontend, b);
	gt32_tile4_attr_forward_all_bm_l2_asm(scratch->operand_b,
		scratch->frontend);
	gt32_tile4_attr_basemul_c3_l2_l2_asm(scratch->product,
		scratch->operand_a, scratch->operand_b);
	gt32_tile4_inverse_all_pair_asm(scratch->inverse_rows, scratch->product);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out,
		scratch->inverse_rows);
	poly_crepmod3(out);
}

__attribute__((noinline))
static void polymul_private_gt32_soa_l2(int16_t *out, const int16_t *a,
	const int16_t *b, private_scratch_t *scratch)
{
	gt32_tile4_frontend_wide_raw_asm(scratch->frontend, a);
	gt32_tile4_attr_forward_all_bm_soa_asm(scratch->operand_a,
		scratch->frontend);
	gt32_tile4_frontend_wide_raw_asm(scratch->frontend, b);
	gt32_tile4_attr_forward_all_bm_l2_asm(scratch->operand_b,
		scratch->frontend);
	gt32_tile4_attr_basemul_c3_soa_l2_asm(scratch->product,
		scratch->operand_a, scratch->operand_b);
	gt32_tile4_inverse_all_pair_asm(scratch->inverse_rows, scratch->product);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out,
		scratch->inverse_rows);
	poly_crepmod3(out);
}

__attribute__((noinline))
static void polymul_private_gt32_l2_soa(int16_t *out, const int16_t *a,
	const int16_t *b, private_scratch_t *scratch)
{
	gt32_tile4_frontend_wide_raw_asm(scratch->frontend, a);
	gt32_tile4_attr_forward_all_bm_l2_asm(scratch->operand_a,
		scratch->frontend);
	gt32_tile4_frontend_wide_raw_asm(scratch->frontend, b);
	gt32_tile4_attr_forward_all_bm_soa_asm(scratch->operand_b,
		scratch->frontend);
	gt32_tile4_attr_basemul_c3_l2_soa_asm(scratch->product,
		scratch->operand_a, scratch->operand_b);
	gt32_tile4_inverse_all_pair_asm(scratch->inverse_rows, scratch->product);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out,
		scratch->inverse_rows);
	poly_crepmod3(out);
}

static double measure(private_polymul_fn fn, int16_t *out,
	const int16_t *a, const int16_t *b, private_scratch_t *scratch,
	unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		fn(out, a, b, scratch);
	const uint64_t end = stop_tsc();
	sink += (uint16_t)out[iterations & (WORDS - 1U)];
	return (double)(end - begin) / iterations;
}

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

static int compare_case(const char *name, const int16_t *a, const int16_t *b,
	int alias_mode)
{
	private_scratch_t baseline_scratch __attribute__((aligned(64)));
	private_scratch_t mixed_scratch __attribute__((aligned(64)));
	private_scratch_t candidate_scratch __attribute__((aligned(64)));
	private_scratch_t l2_scratch __attribute__((aligned(64)));
	private_scratch_t soa_l2_scratch __attribute__((aligned(64)));
	private_scratch_t l2_soa_scratch __attribute__((aligned(64)));
	int16_t baseline_a[WORDS] __attribute__((aligned(64)));
	int16_t baseline_b[WORDS] __attribute__((aligned(64)));
	int16_t candidate_a[WORDS] __attribute__((aligned(64)));
	int16_t candidate_b[WORDS] __attribute__((aligned(64)));
	int16_t l2_a[WORDS] __attribute__((aligned(64)));
	int16_t l2_b[WORDS] __attribute__((aligned(64)));
	int16_t soa_l2_a[WORDS] __attribute__((aligned(64)));
	int16_t soa_l2_b[WORDS] __attribute__((aligned(64)));
	int16_t l2_soa_a[WORDS] __attribute__((aligned(64)));
	int16_t l2_soa_b[WORDS] __attribute__((aligned(64)));
	int16_t baseline_out[WORDS] __attribute__((aligned(64)));
	int16_t mixed_out[WORDS] __attribute__((aligned(64)));
	int16_t candidate_out[WORDS] __attribute__((aligned(64)));
	int16_t l2_out[WORDS] __attribute__((aligned(64)));
	int16_t soa_l2_out[WORDS] __attribute__((aligned(64)));
	int16_t l2_soa_out[WORDS] __attribute__((aligned(64)));
	memcpy(baseline_a, a, sizeof(baseline_a));
	memcpy(baseline_b, b, sizeof(baseline_b));
	memcpy(candidate_a, a, sizeof(candidate_a));
	memcpy(candidate_b, b, sizeof(candidate_b));
	memcpy(l2_a, a, sizeof(l2_a));
	memcpy(l2_b, b, sizeof(l2_b));
	memcpy(soa_l2_a, a, sizeof(soa_l2_a));
	memcpy(soa_l2_b, b, sizeof(soa_l2_b));
	memcpy(l2_soa_a, a, sizeof(l2_soa_a));
	memcpy(l2_soa_b, b, sizeof(l2_soa_b));
	int16_t *baseline_dst = baseline_out;
	int16_t *mixed_dst = mixed_out;
	int16_t *candidate_dst = candidate_out;
	int16_t *l2_dst = l2_out;
	int16_t *soa_l2_dst = soa_l2_out;
	int16_t *l2_soa_dst = l2_soa_out;
	if (alias_mode == 1) {
		baseline_dst = baseline_a;
		mixed_dst = candidate_a;
		candidate_dst = candidate_a;
		l2_dst = l2_a;
		soa_l2_dst = soa_l2_a;
		l2_soa_dst = l2_soa_a;
	} else if (alias_mode == 2) {
		baseline_dst = baseline_b;
		mixed_dst = candidate_b;
		candidate_dst = candidate_b;
		l2_dst = l2_b;
		soa_l2_dst = soa_l2_b;
		l2_soa_dst = l2_soa_b;
	}
	polymul_private_gt32_aos(baseline_dst, baseline_a, baseline_b,
		&baseline_scratch);
	polymul_private_gt32_mixed(mixed_dst, candidate_a, candidate_b,
		&mixed_scratch);
	if (memcmp(baseline_dst, mixed_dst, sizeof(baseline_out)) != 0) {
		fprintf(stderr, "%s mixed differential failed (alias=%d)\n", name,
			alias_mode);
		return 0;
	}
	/* The mixed alias call may have overwritten one of its inputs. */
	memcpy(candidate_a, a, sizeof(candidate_a));
	memcpy(candidate_b, b, sizeof(candidate_b));
	if (alias_mode == 1)
		candidate_dst = candidate_a;
	else if (alias_mode == 2)
		candidate_dst = candidate_b;
	polymul_private_gt32_soa(candidate_dst, candidate_a, candidate_b,
		&candidate_scratch);
	if (memcmp(baseline_dst, candidate_dst, sizeof(baseline_out)) != 0) {
		fprintf(stderr, "%s differential failed (alias=%d)\n", name,
			alias_mode);
		return 0;
	}
	polymul_private_gt32_l2(l2_dst, l2_a, l2_b, &l2_scratch);
	if (memcmp(baseline_dst, l2_dst, sizeof(baseline_out)) != 0) {
		fprintf(stderr, "%s L2 differential failed (alias=%d)\n", name,
			alias_mode);
		return 0;
	}
	polymul_private_gt32_soa_l2(soa_l2_dst, soa_l2_a, soa_l2_b,
		&soa_l2_scratch);
	if (memcmp(baseline_dst, soa_l2_dst, sizeof(baseline_out)) != 0) {
		fprintf(stderr, "%s SoA/L2 differential failed (alias=%d)\n", name,
			alias_mode);
		return 0;
	}
	polymul_private_gt32_l2_soa(l2_soa_dst, l2_soa_a, l2_soa_b,
		&l2_soa_scratch);
	if (memcmp(baseline_dst, l2_soa_dst, sizeof(baseline_out)) != 0) {
		fprintf(stderr, "%s L2/SoA differential failed (alias=%d)\n", name,
			alias_mode);
		return 0;
	}
	return 1;
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	const unsigned scratch_offset = argc > 2
		? (unsigned)strtoul(argv[2], NULL, 10) : 0U;
	uint8_t baseline_storage[sizeof(private_scratch_t) + 128U]
		__attribute__((aligned(64)));
	uint8_t candidate_storage[sizeof(private_scratch_t) + 128U]
		__attribute__((aligned(64)));
	uint8_t mixed_storage[sizeof(private_scratch_t) + 128U]
		__attribute__((aligned(64)));
	uint8_t l2_storage[sizeof(private_scratch_t) + 128U]
		__attribute__((aligned(64)));
	uint8_t soa_l2_storage[sizeof(private_scratch_t) + 128U]
		__attribute__((aligned(64)));
	uint8_t l2_soa_storage[sizeof(private_scratch_t) + 128U]
		__attribute__((aligned(64)));
	private_scratch_t *baseline_scratch = (private_scratch_t *)(void *)(
		baseline_storage + scratch_offset);
	private_scratch_t *candidate_scratch = (private_scratch_t *)(void *)(
		candidate_storage + scratch_offset);
	private_scratch_t *mixed_scratch = (private_scratch_t *)(void *)(
		mixed_storage + scratch_offset);
	private_scratch_t *l2_scratch = (private_scratch_t *)(void *)(
		l2_storage + scratch_offset);
	private_scratch_t *soa_l2_scratch = (private_scratch_t *)(void *)(
		soa_l2_storage + scratch_offset);
	private_scratch_t *l2_soa_scratch = (private_scratch_t *)(void *)(
		l2_soa_storage + scratch_offset);
	int16_t a[WORDS] __attribute__((aligned(64)));
	int16_t b[WORDS] __attribute__((aligned(64)));
	int16_t baseline_out[WORDS] __attribute__((aligned(64)));
	int16_t mixed_out[WORDS] __attribute__((aligned(64)));
	int16_t candidate_out[WORDS] __attribute__((aligned(64)));
	int16_t l2_out[WORDS] __attribute__((aligned(64)));
	int16_t soa_l2_out[WORDS] __attribute__((aligned(64)));
	int16_t l2_soa_out[WORDS] __attribute__((aligned(64)));
	cpu_set_t set;
	uint32_t random_state = 1U;
	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof(set), &set) != 0)
		perror("sched_setaffinity");
	if ((scratch_offset != 0U && scratch_offset != 32U)
		|| ((uintptr_t)baseline_scratch & 31U) != 0U
		|| ((uintptr_t)mixed_scratch & 31U) != 0U
		|| ((uintptr_t)candidate_scratch & 31U) != 0U
		|| ((uintptr_t)l2_scratch & 31U) != 0U
		|| ((uintptr_t)soa_l2_scratch & 31U) != 0U
		|| ((uintptr_t)l2_soa_scratch & 31U) != 0U) {
		fprintf(stderr, "unsupported private scratch placement\n");
		return 1;
	}
	for (unsigned trial = 0; trial < CORRECTNESS_TRIALS; trial++) {
		fill_small(a, &random_state);
		fill_small(b, &random_state);
		if (!compare_case("distinct", a, b, 0)
			|| !compare_case("out-equals-a", a, b, 1)
			|| !compare_case("out-equals-b", a, b, 2)
			|| !compare_case("squaring", a, a, 0))
			return 1;
	}
	fill_small(a, &random_state);
	fill_small(b, &random_state);
	for (unsigned warm = 0; warm < 2; warm++) {
		(void)measure(polymul_private_gt32_aos, baseline_out, a, b,
			baseline_scratch, 1000);
		(void)measure(polymul_private_gt32_mixed, mixed_out, a, b,
			mixed_scratch, 1000);
		(void)measure(polymul_private_gt32_soa, candidate_out, a, b,
			candidate_scratch, 1000);
		(void)measure(polymul_private_gt32_l2, l2_out, a, b,
			l2_scratch, 1000);
		(void)measure(polymul_private_gt32_soa_l2, soa_l2_out, a, b,
			soa_l2_scratch, 1000);
		(void)measure(polymul_private_gt32_l2_soa, l2_soa_out, a, b,
			l2_soa_scratch, 1000);
	}
	printf("META,correctness=pass,paths=AA-SA-SS-L2L2-SL2-L2S,alias=out-a-out-b,squaring=pass,"
		"scratch_alignment=%u,crepmod3=included,iterations=%u,samples=%u\n",
		scratch_offset == 0U ? 64U : 32U, iterations, SAMPLES);
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		double baseline;
		double mixed;
		double candidate;
		double l2;
		double soa_l2;
		double l2_soa;
		if ((sample & 1U) == 0U) {
			baseline = measure(polymul_private_gt32_aos, baseline_out,
				a, b, baseline_scratch, iterations);
			mixed = measure(polymul_private_gt32_mixed, mixed_out,
				a, b, mixed_scratch, iterations);
			candidate = measure(polymul_private_gt32_soa, candidate_out,
				a, b, candidate_scratch, iterations);
			l2 = measure(polymul_private_gt32_l2, l2_out,
				a, b, l2_scratch, iterations);
			soa_l2 = measure(polymul_private_gt32_soa_l2, soa_l2_out,
				a, b, soa_l2_scratch, iterations);
			l2_soa = measure(polymul_private_gt32_l2_soa, l2_soa_out,
				a, b, l2_soa_scratch, iterations);
		} else {
			l2_soa = measure(polymul_private_gt32_l2_soa, l2_soa_out,
				a, b, l2_soa_scratch, iterations);
			soa_l2 = measure(polymul_private_gt32_soa_l2, soa_l2_out,
				a, b, soa_l2_scratch, iterations);
			l2 = measure(polymul_private_gt32_l2, l2_out,
				a, b, l2_scratch, iterations);
			candidate = measure(polymul_private_gt32_soa, candidate_out,
				a, b, candidate_scratch, iterations);
			mixed = measure(polymul_private_gt32_mixed, mixed_out,
				a, b, mixed_scratch, iterations);
			baseline = measure(polymul_private_gt32_aos, baseline_out,
				a, b, baseline_scratch, iterations);
		}
		printf("SAMPLE,%u,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f\n",
			sample, baseline, mixed, candidate, l2, soa_l2, l2_soa,
			mixed - baseline, candidate - baseline, l2 - baseline,
			soa_l2 - baseline, l2_soa - baseline);
	}
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}
