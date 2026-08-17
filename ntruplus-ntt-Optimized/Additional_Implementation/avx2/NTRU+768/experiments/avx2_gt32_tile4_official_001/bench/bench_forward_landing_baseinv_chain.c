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
#define TRIALS 1000

extern void gt32_tile4_attr_forward_all_bm_soa_p_asm(int16_t *, const int16_t *);
extern void gt32_tile4_attr_forward_all_baseinv_p_l3_asm(int16_t *, const int16_t *);
extern int gt32_p_baseinv_direct_avx2(int16_t *, const int16_t *);
extern int gt32_p_baseinv_center_on_load_avx2(int16_t *, const int16_t *);

static int16_t input[WORDS] __attribute__((aligned(64)));
static int16_t frontend[WORDS] __attribute__((aligned(64)));
static int16_t landed_control[WORDS] __attribute__((aligned(64)));
static int16_t landed_candidate[WORDS] __attribute__((aligned(64)));
static int16_t result[WORDS] __attribute__((aligned(64)));
static int16_t control[WORDS] __attribute__((aligned(64)));
static volatile uint64_t sink;
static uint32_t state = 0x6c3300c1U;

static uint32_t random32(void) { state ^= state << 13; state ^= state >> 17; state ^= state << 5; return state; }
static int16_t mod_center(int32_t x) { x %= 3457; if (x > 1728) x -= 3457; if (x < -1728) x += 3457; return (int16_t)x; }
static uint64_t begin_tsc(void) { _mm_lfence(); return __rdtsc(); }
static uint64_t end_tsc(void) { unsigned aux; uint64_t x = __rdtscp(&aux); _mm_lfence(); return x; }

static void control_fn(void)
{
	gt32_tile4_frontend_wide_raw_asm(frontend, input);
	gt32_tile4_attr_forward_all_bm_soa_p_asm(landed_control, frontend);
	(void)gt32_p_baseinv_center_on_load_avx2(result, landed_control);
	sink += (uint16_t)result[0];
}

static void candidate_fn(void)
{
	gt32_tile4_frontend_wide_raw_asm(frontend, input);
	gt32_tile4_attr_forward_all_baseinv_p_l3_asm(landed_candidate, frontend);
	(void)gt32_p_baseinv_direct_avx2(result, landed_candidate);
	sink += (uint16_t)result[0];
}

static void baseinv_control_fn(void)
{
	(void)gt32_p_baseinv_center_on_load_avx2(result, landed_control);
	sink += (uint16_t)result[0];
}

static void baseinv_candidate_fn(void)
{
	(void)gt32_p_baseinv_direct_avx2(result, landed_candidate);
	sink += (uint16_t)result[0];
}

static double measure(void (*fn)(void), unsigned iterations)
{
	uint64_t start = begin_tsc();
	for (unsigned i = 0; i < iterations; i++) fn();
	return (double)(end_tsc() - start) / iterations;
}

static int correctness(void)
{
	unsigned accepted = 0;
	for (unsigned trial = 0; trial < TRIALS; trial++) {
		for (unsigned i = 0; i < WORDS; i++) input[i] = (int16_t)((int)(random32() & 7U) - 3);
		gt32_tile4_frontend_wide_raw_asm(frontend, input);
		gt32_tile4_attr_forward_all_bm_soa_p_asm(landed_control, frontend);
		int cs = gt32_p_baseinv_center_on_load_avx2(control, landed_control);
		gt32_tile4_attr_forward_all_baseinv_p_l3_asm(landed_candidate, frontend);
		int ns = gt32_p_baseinv_direct_avx2(result, landed_candidate);
		if (cs != ns) return fprintf(stderr, "status mismatch trial=%u\n", trial), 0;
		if (cs == 0) {
			accepted++;
			for (unsigned i = 0; i < WORDS; i++) if (mod_center(control[i]) != mod_center(result[i]))
				return fprintf(stderr, "output mismatch trial=%u word=%u\n", trial, i), 0;
		}
	}
	printf("correctness trials=%u accepted=%u\n", TRIALS, accepted);
	return accepted != 0;
}

int main(int argc, char **argv)
{
	unsigned iterations = argc > 1 ? (unsigned)strtoul(argv[1], 0, 0) : 2000;
	unsigned cpu = argc > 2 ? (unsigned)strtoul(argv[2], 0, 0) : 2;
	cpu_set_t set; CPU_ZERO(&set); CPU_SET(cpu, &set); (void)sched_setaffinity(0, sizeof(set), &set);
	if (!correctness()) return 1;
	for (unsigned i = 0; i < WORDS; i++) input[i] = (int16_t)((int)(i & 7U) - 3);
	gt32_tile4_frontend_wide_raw_asm(frontend, input);
	gt32_tile4_attr_forward_all_bm_soa_p_asm(landed_control, frontend);
	gt32_tile4_attr_forward_all_baseinv_p_l3_asm(landed_candidate, frontend);
	for (unsigned region = 0; region < 2; region++) for (unsigned sample = 0; sample < SAMPLES; sample++) {
		double c, n;
		void (*cf)(void) = region == 0 ? baseinv_control_fn : control_fn;
		void (*nf)(void) = region == 0 ? baseinv_candidate_fn : candidate_fn;
		if ((sample & 1U) == 0) { c = measure(cf, iterations); n = measure(nf, iterations); }
		else { n = measure(nf, iterations); c = measure(cf, iterations); }
		printf("sample region=%s index=%u control=%.6f candidate=%.6f delta=%.6f\n",
			region == 0 ? "baseinv" : "forward_baseinv", sample, c, n, n-c);
	}
	printf("sink=%llu\n", (unsigned long long)sink);
	return 0;
}
