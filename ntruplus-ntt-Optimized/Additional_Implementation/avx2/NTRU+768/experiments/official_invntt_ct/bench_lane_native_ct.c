#define _GNU_SOURCE
#include "poly.h"

#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

enum { CPU = 3, FIXTURES = 32, SAMPLES = 10001, WARMUP = 2048, CASES = 2 };
static poly products[FIXTURES];
static poly work[CASES];
extern void official_invntt_ct_lane_native_asm(poly *value);

static uint64_t begin_tsc(void)
{
	unsigned low, high;
	__asm__ volatile("lfence\n\trdtsc" : "=a"(low), "=d"(high) :: "memory");
	return (uint64_t)high << 32 | low;
}

static uint64_t end_tsc(void)
{
	unsigned low, high, auxiliary;
	__asm__ volatile("rdtscp\n\tlfence" : "=a"(low), "=d"(high), "=c"(auxiliary) :: "memory");
	return (uint64_t)high << 32 | low;
}

static int compare_u64(const void *left, const void *right)
{
	const uint64_t a = *(const uint64_t *)left;
	const uint64_t b = *(const uint64_t *)right;
	return (a > b) - (a < b);
}

int main(void)
{
	static uint64_t samples[CASES][SAMPLES];
	static const char *names[CASES] = {"official-gs", "official-lane-native-ct"};
	cpu_set_t affinity;
	uint32_t random_word = 0x4c4e4354U;
	CPU_ZERO(&affinity);
	CPU_SET(CPU, &affinity);
	if (sched_setaffinity(0, sizeof(affinity), &affinity) != 0) {
		perror("sched_setaffinity");
		return 1;
	}
	for (unsigned fixture = 0; fixture < FIXTURES; ++fixture) {
		poly a, b;
		for (unsigned i = 0; i < 768; ++i) {
			random_word = 1664525U * random_word + 1013904223U;
			a.coeffs[i] = (int16_t)((int)(random_word % 3U) - 1);
			random_word = 1664525U * random_word + 1013904223U;
			b.coeffs[i] = (int16_t)((int)(random_word % 3U) - 1);
		}
		poly_ntt(&a);
		poly_ntt(&b);
		poly_basemul_scale(&products[fixture], &a, &b);
	}
	for (unsigned i = 0; i < WARMUP; ++i) {
		work[0] = products[i & 31U];
		work[1] = products[i & 31U];
		poly_invntt_scale(&work[0]);
		official_invntt_ct_lane_native_asm(&work[1]);
	}
	for (unsigned sample = 0; sample < SAMPLES; ++sample) {
		const unsigned fixture = (17U * sample + 9U) & 31U;
		for (unsigned position = 0; position < CASES; ++position) {
			const unsigned implementation = (sample + position) & 1U;
			work[implementation] = products[fixture];
			const uint64_t start = begin_tsc();
			if (implementation == 0) poly_invntt_scale(&work[0]);
			else official_invntt_ct_lane_native_asm(&work[1]);
			samples[implementation][sample] = end_tsc() - start;
		}
	}
	for (unsigned implementation = 0; implementation < CASES; ++implementation) {
		qsort(samples[implementation], SAMPLES, sizeof(uint64_t), compare_u64);
		printf("%s median=%llu p10=%llu p90=%llu\n", names[implementation],
		       (unsigned long long)samples[implementation][SAMPLES / 2],
		       (unsigned long long)samples[implementation][SAMPLES / 10],
		       (unsigned long long)samples[implementation][9 * SAMPLES / 10]);
	}
	return 0;
}
