#define _GNU_SOURCE
#include "producer.h"

#include <immintrin.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define SAMPLES 41
#define ITERS 12000U

typedef void (*producer_fn)(int16_t *, const int16_t *);
static int16_t input[PRODUCER062_N] __attribute__((aligned(32)));
static int16_t output[PRODUCER062_TILE_WORDS] __attribute__((aligned(32)));
static volatile uint64_t sink;

static uint64_t ticks(void)
{
	unsigned aux;
	_mm_lfence();
	const uint64_t t = __rdtscp(&aux);
	_mm_lfence();
	return t;
}

static double run(producer_fn fn, unsigned iters)
{
	const uint64_t begin = ticks();
	for (unsigned i = 0; i < iters; ++i) {
		fn(output, input);
		sink += (uint16_t)output[i & 127U];
	}
	return (double)(ticks() - begin) / (double)iters;
}

static int cmp_double(const void *a, const void *b)
{
	const double x = *(const double *)a, y = *(const double *)b;
	return (x > y) - (x < y);
}

static double median(double *x, size_t count)
{
	qsort(x, count, sizeof(*x), cmp_double);
	return x[count / 2];
}

static void pin(void)
{
	cpu_set_t available, one;
	CPU_ZERO(&available);
	if (sched_getaffinity(0, sizeof(available), &available)) return;
	for (int c = 0; c < CPU_SETSIZE; ++c)
		if (CPU_ISSET(c, &available)) {
			CPU_ZERO(&one); CPU_SET(c, &one);
			(void)sched_setaffinity(0, sizeof(one), &one);
			return;
		}
}

static producer_fn parse_variant(const char *name)
{
	if (!strcmp(name, "p0")) return producer062_p0_tile4_post_s1_asm;
	if (!strcmp(name, "p1")) return producer062_p1_hwa_explicit_post_s1_asm;
	if (!strcmp(name, "p2")) return producer062_p2_hwa_fused_post_s1_asm;
	return NULL;
}

int main(int argc, char **argv)
{
	pin();
	uint64_t s = UINT64_C(0x062abcdef987654);
	for (unsigned i = 0; i < PRODUCER062_N; ++i) {
		s ^= s << 7; s ^= s >> 9;
		input[i] = (int16_t)((int)(s % 3457U) - 1728);
	}
	if (argc == 3 && !strcmp(argv[1], "--pmu")) {
		producer_fn fn = parse_variant(argv[2]);
		if (!fn) return 2;
		(void)run(fn, 1000000U);
		printf("%llu\n", (unsigned long long)sink);
		return 0;
	}
	double d1[SAMPLES], d2[SAMPLES];
	double d1_normal[(SAMPLES + 1) / 2], d1_reversed[SAMPLES / 2];
	double d2_normal[(SAMPLES + 1) / 2], d2_reversed[SAMPLES / 2];
	unsigned normal_count = 0, reversed_count = 0;
	for (unsigned i = 0; i < SAMPLES; ++i) {
		double base, candidate;
		const int reverse = (int)(i & 1U);
		if (!reverse) {
			base = run(producer062_p0_tile4_post_s1_asm, ITERS);
			candidate = run(producer062_p1_hwa_explicit_post_s1_asm, ITERS);
		} else {
			candidate = run(producer062_p1_hwa_explicit_post_s1_asm, ITERS);
			base = run(producer062_p0_tile4_post_s1_asm, ITERS);
		}
		d1[i] = candidate - base;
		if (!reverse) {
			base = run(producer062_p0_tile4_post_s1_asm, ITERS);
			candidate = run(producer062_p2_hwa_fused_post_s1_asm, ITERS);
		} else {
			candidate = run(producer062_p2_hwa_fused_post_s1_asm, ITERS);
			base = run(producer062_p0_tile4_post_s1_asm, ITERS);
		}
		d2[i] = candidate - base;
		if (!reverse) {
			d1_normal[normal_count] = d1[i];
			d2_normal[normal_count++] = d2[i];
		} else {
			d1_reversed[reversed_count] = d1[i];
			d2_reversed[reversed_count++] = d2[i];
		}
	}
	printf("{\"delta_tsc\":{\"p1\":%.6f,\"p2\":%.6f},"
	       "\"normal_delta_tsc\":{\"p1\":%.6f,\"p2\":%.6f},"
	       "\"reversed_delta_tsc\":{\"p1\":%.6f,\"p2\":%.6f},"
	       "\"sink\":%llu}\n",
		median(d1, SAMPLES), median(d2, SAMPLES),
		median(d1_normal, normal_count), median(d2_normal, normal_count),
		median(d1_reversed, reversed_count),
		median(d2_reversed, reversed_count),
		(unsigned long long)sink);
	return 0;
}
