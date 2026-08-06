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

typedef void (*consumer_fn)(int16_t *, const int16_t *, const int16_t *);
static int16_t product[WORDS] __attribute__((aligned(32)));
static int16_t rows[WORDS] __attribute__((aligned(32)));
static int16_t work_a[WORDS] __attribute__((aligned(64)));
static int16_t work_b[WORDS] __attribute__((aligned(64)));
static volatile uint64_t sink;

void poly_basemul_scale(int16_t *, const int16_t *, const int16_t *);
void poly_invntt_scale(int16_t *);
void poly_ntt(int16_t *);
void poly_crepmod3(int16_t *);
void gt_basemul_native_rminus1_c0lazy_asm_avx2(
	int16_t *, const int16_t *, const int16_t *);
void gt_invntt_soa_avx2_fused_asm(int16_t *, const int16_t *);

static void official_consumer(int16_t *out, const int16_t *a, const int16_t *b)
{
	poly_basemul_scale(out, a, b);
	poly_invntt_scale(out);
}

static void frozen_consumer(int16_t *out, const int16_t *a, const int16_t *b)
{
	gt_basemul_native_rminus1_c0lazy_asm_avx2(product, a, b);
	gt_invntt_soa_avx2_fused_asm(out, product);
}

static void tile4_consumer(int16_t *out, const int16_t *a, const int16_t *b)
{
	gt32_tile4_basemul_b2_asm(product, a, b);
	gt32_tile4_inverse_all_pair_asm(rows, product);
	gt32_tile4_inverse_tail_asm_rminus1(out, rows);
}

static void tile4_private_consumer(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	gt32_tile4_basemul_b2_asm(product, a, b);
	gt32_tile4_inverse_all_pair_asm(rows, product);
	gt32_tile4_inverse_tail_champion_private_asm(out, rows);
}

static void official_full_chain(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	memcpy(work_a, a, sizeof(work_a));
	memcpy(work_b, b, sizeof(work_b));
	poly_ntt(work_a);
	poly_ntt(work_b);
	poly_basemul_scale(out, work_a, work_b);
	poly_invntt_scale(out);
}

static void tile4_full_chain(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	memcpy(work_a, a, sizeof(work_a));
	memcpy(work_b, b, sizeof(work_b));
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(work_a, work_a);
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(work_b, work_b);
	gt32_tile4_basemul_b2_asm(product, work_a, work_b);
	gt32_tile4_inverse_all_pair_asm(rows, product);
	gt32_tile4_inverse_tail_champion_private_asm(out, rows);
}

static void official_full_chain_crep(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	official_full_chain(out, a, b);
	poly_crepmod3(out);
}

static void tile4_full_chain_crep(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	memcpy(work_a, a, sizeof(work_a));
	memcpy(work_b, b, sizeof(work_b));
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(work_a, work_a);
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(work_b, work_b);
	gt32_tile4_basemul_b2_asm(product, work_a, work_b);
	gt32_tile4_inverse_all_pair_asm(rows, product);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out, rows);
	poly_crepmod3(out);
}

static void tile4_full_chain_t10(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	memcpy(work_a, a, sizeof(work_a));
	memcpy(work_b, b, sizeof(work_b));
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(work_a, work_a);
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(work_b, work_b);
	gt32_tile4_basemul_b2_asm(product, work_a, work_b);
	gt32_tile4_inverse_all_pair_asm(rows, product);
	gt32_tile4_inverse_tail_t10_crepmod3_asm(out, rows);
}

static uint64_t ticks(void)
{
	unsigned aux;
	_mm_lfence();
	const uint64_t value = __rdtscp(&aux);
	_mm_lfence();
	return value;
}

static double run(consumer_fn fn, int16_t *out, const int16_t *a,
	const int16_t *b, unsigned iterations)
{
	const uint64_t begin = ticks();
	for (unsigned i = 0; i < iterations; i++)
		fn(out, a, b);
	const uint64_t elapsed = ticks() - begin;
	sink += (uint16_t)out[37];
	return (double)elapsed / iterations;
}

static int compare_double(const void *left, const void *right)
{
	const double a = *(const double *)left;
	const double b = *(const double *)right;
	return (a > b) - (a < b);
}

static double median(double values[SAMPLES])
{
	qsort(values, SAMPLES, sizeof(values[0]), compare_double);
	return 0.5 * (values[9] + values[10]);
}

static int16_t centered_mod_q(int16_t value)
{
	int result = value % 3457;
	if (result < 0)
		result += 3457;
	if (result > 1728)
		result -= 3457;
	return (int16_t)result;
}

static int16_t crepmod3_contract(int16_t value)
{
	value = (int16_t)(value + ((value >> 15) & 3457));
	value = (int16_t)(value - 1729);
	value = (int16_t)(value + ((value >> 15) & 3457));
	value = (int16_t)(value - 1728);
	const int16_t quotient = (int16_t)(((int32_t)10923 * value + 16384) >> 15);
	return (int16_t)(value - 3 * quotient);
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc >= 2
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	int16_t a[WORDS] __attribute__((aligned(32)));
	int16_t b[WORDS] __attribute__((aligned(32)));
	int16_t out[WORDS] __attribute__((aligned(32)));
	int16_t official_result[WORDS] __attribute__((aligned(32)));
	int16_t tile4_result[WORDS] __attribute__((aligned(32)));
	double official[SAMPLES], frozen[SAMPLES], tile4[SAMPLES], private[SAMPLES];
	double official_full[SAMPLES], tile4_full[SAMPLES];
	double official_crep[SAMPLES], tile4_crep[SAMPLES], tile4_t10[SAMPLES];
	cpu_set_t set;
	CPU_ZERO(&set);
	CPU_SET(1, &set);
	(void)sched_setaffinity(0, sizeof(set), &set);
	for (unsigned i = 0; i < WORDS; i++) {
		a[i] = (int16_t)((int)(i % 8U) - 3);
		b[i] = (int16_t)((int)((3U * i + 1U) % 8U) - 3);
	}
	official_full_chain(official_result, a, b);
	tile4_full_chain(tile4_result, a, b);
	for (unsigned i = 0; i < WORDS; i++) {
		if (centered_mod_q(official_result[i]) != centered_mod_q(tile4_result[i])
			|| crepmod3_contract(official_result[i])
				!= crepmod3_contract(tile4_result[i])) {
			fprintf(stderr, "full-chain differential failed at %u: %d != %d\n",
				i, official_result[i], tile4_result[i]);
			return 1;
		}
	}
	official_full_chain_crep(official_result, a, b);
	tile4_full_chain_t10(tile4_result, a, b);
	for (unsigned i = 0; i < WORDS; i++) {
		if (official_result[i] != tile4_result[i]) {
			fprintf(stderr, "full-chain crep differential failed at %u\n", i);
			return 1;
		}
	}
	for (unsigned warm = 0; warm < 2; warm++) {
		for (unsigned i = 0; i < 32; i++) {
			official_consumer(out, a, b);
			frozen_consumer(out, a, b);
			tile4_consumer(out, a, b);
			tile4_private_consumer(out, a, b);
			official_full_chain(out, a, b);
			tile4_full_chain(out, a, b);
			official_full_chain_crep(out, a, b);
			tile4_full_chain_crep(out, a, b);
			tile4_full_chain_t10(out, a, b);
		}
	}
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		if ((sample & 1U) == 0U) {
			official[sample] = run(official_consumer, out, a, b, iterations);
			frozen[sample] = run(frozen_consumer, out, a, b, iterations);
			tile4[sample] = run(tile4_consumer, out, a, b, iterations);
			private[sample] = run(tile4_private_consumer, out, a, b, iterations);
			official_full[sample] = run(official_full_chain, out, a, b, iterations);
			tile4_full[sample] = run(tile4_full_chain, out, a, b, iterations);
			official_crep[sample] = run(official_full_chain_crep, out, a, b,
				iterations);
			tile4_crep[sample] = run(tile4_full_chain_crep, out, a, b, iterations);
			tile4_t10[sample] = run(tile4_full_chain_t10, out, a, b, iterations);
		} else {
			tile4_t10[sample] = run(tile4_full_chain_t10, out, a, b, iterations);
			tile4_crep[sample] = run(tile4_full_chain_crep, out, a, b, iterations);
			official_crep[sample] = run(official_full_chain_crep, out, a, b,
				iterations);
			tile4_full[sample] = run(tile4_full_chain, out, a, b, iterations);
			official_full[sample] = run(official_full_chain, out, a, b, iterations);
			private[sample] = run(tile4_private_consumer, out, a, b, iterations);
			tile4[sample] = run(tile4_consumer, out, a, b, iterations);
			frozen[sample] = run(frozen_consumer, out, a, b, iterations);
			official[sample] = run(official_consumer, out, a, b, iterations);
		}
	}
	const double official_median = median(official);
	const double frozen_median = median(frozen);
	const double tile4_median = median(tile4);
	const double private_median = median(private);
	const double official_full_median = median(official_full);
	const double tile4_full_median = median(tile4_full);
	const double official_crep_median = median(official_crep);
	const double tile4_crep_median = median(tile4_crep);
	const double tile4_t10_median = median(tile4_t10);
	printf("iterations=%u samples=%d official_bm_inv=%.3f frozen_bm_inv=%.3f "
		"tile4_bm_inv=%.3f private_bm_inv=%.3f "
		"private_vs_official=%+.3f private_vs_frozen=%+.3f "
		"sink=%llu\n", iterations, SAMPLES, official_median, frozen_median,
		tile4_median, private_median, private_median - official_median,
		private_median - frozen_median, (unsigned long long)sink);
	printf("full_2f_b_i official=%.3f tile4_private=%.3f delta=%+.3f "
		"delta_pct=%+.3f\n", official_full_median, tile4_full_median,
		tile4_full_median - official_full_median,
		100.0 * (tile4_full_median / official_full_median - 1.0));
	printf("full_2f_b_i_crep official=%.3f tile4_t9=%.3f tile4_t10=%.3f "
		"t9_delta=%+.3f t10_vs_t9=%+.3f\n", official_crep_median,
		tile4_crep_median, tile4_t10_median,
		tile4_crep_median - official_crep_median,
		tile4_t10_median - tile4_crep_median);
	printf("addresses official=%p frozen=%p tile4=%p private=%p\n",
		(void *)(uintptr_t)official_consumer, (void *)(uintptr_t)frozen_consumer,
		(void *)(uintptr_t)tile4_consumer,
		(void *)(uintptr_t)tile4_private_consumer);
	return 0;
}
