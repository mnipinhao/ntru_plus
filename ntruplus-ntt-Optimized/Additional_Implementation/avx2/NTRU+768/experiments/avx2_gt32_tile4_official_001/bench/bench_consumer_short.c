#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <x86intrin.h>

#include "tile4.h"

#define WORDS 768
#define SAMPLES 20

typedef void (*consumer_fn)(int16_t *, const int16_t *, const int16_t *);
static int16_t product[WORDS] __attribute__((aligned(32)));
static int16_t rows[WORDS] __attribute__((aligned(32)));
static volatile uint64_t sink;

void poly_basemul_scale(int16_t *, const int16_t *, const int16_t *);
void poly_invntt_scale(int16_t *);
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

int main(int argc, char **argv)
{
	const unsigned iterations = argc >= 2
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	int16_t a[WORDS] __attribute__((aligned(32)));
	int16_t b[WORDS] __attribute__((aligned(32)));
	int16_t out[WORDS] __attribute__((aligned(32)));
	double official[SAMPLES], frozen[SAMPLES], tile4[SAMPLES];
	cpu_set_t set;
	CPU_ZERO(&set);
	CPU_SET(1, &set);
	(void)sched_setaffinity(0, sizeof(set), &set);
	for (unsigned i = 0; i < WORDS; i++) {
		a[i] = (int16_t)((int)((17U * i + 3U) % 3457U) - 1728);
		b[i] = (int16_t)((int)((29U * i + 5U) % 3457U) - 1728);
	}
	for (unsigned warm = 0; warm < 2; warm++) {
		for (unsigned i = 0; i < 32; i++) {
			official_consumer(out, a, b);
			frozen_consumer(out, a, b);
			tile4_consumer(out, a, b);
		}
	}
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		if ((sample & 1U) == 0U) {
			official[sample] = run(official_consumer, out, a, b, iterations);
			frozen[sample] = run(frozen_consumer, out, a, b, iterations);
			tile4[sample] = run(tile4_consumer, out, a, b, iterations);
		} else {
			tile4[sample] = run(tile4_consumer, out, a, b, iterations);
			frozen[sample] = run(frozen_consumer, out, a, b, iterations);
			official[sample] = run(official_consumer, out, a, b, iterations);
		}
	}
	const double official_median = median(official);
	const double frozen_median = median(frozen);
	const double tile4_median = median(tile4);
	printf("iterations=%u samples=%d official_bm_inv=%.3f frozen_bm_inv=%.3f "
		"tile4_bm_inv=%.3f tile4_vs_official=%+.3f tile4_vs_frozen=%+.3f "
		"sink=%llu\n", iterations, SAMPLES, official_median, frozen_median,
		tile4_median, tile4_median - official_median,
		tile4_median - frozen_median, (unsigned long long)sink);
	return 0;
}
