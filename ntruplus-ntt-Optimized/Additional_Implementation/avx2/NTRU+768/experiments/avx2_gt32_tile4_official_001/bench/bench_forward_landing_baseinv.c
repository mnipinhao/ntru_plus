#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <x86intrin.h>

#include "tile4.h"

#define WORDS GT32_TILE4_POLY_WORDS
#define SAMPLES 20
#define CORRECTNESS_TRIALS 1000

extern void gt32_tile4_attr_forward_all_bm_soa_p_asm(int16_t *,
	const int16_t *);
extern void gt32_tile4_attr_forward_all_baseinv_p_l3_asm(int16_t *,
	const int16_t *);

typedef void (*bench_fn)(void);

static int16_t input[WORDS] __attribute__((aligned(64)));
static int16_t frontend[WORDS] __attribute__((aligned(64)));
static int16_t output[WORDS] __attribute__((aligned(64)));
static int16_t control[WORDS] __attribute__((aligned(64)));
static int16_t candidate[WORDS] __attribute__((aligned(64)));
static volatile uint64_t sink;

static uint32_t random_state = 0x6c330001U;

static uint32_t random32(void)
{
	random_state ^= random_state << 13;
	random_state ^= random_state >> 17;
	random_state ^= random_state << 5;
	return random_state;
}

static int16_t centered(int32_t value)
{
	value %= GT32_TILE4_Q;
	if (value > GT32_TILE4_Q / 2)
		value -= GT32_TILE4_Q;
	if (value < -GT32_TILE4_Q / 2)
		value += GT32_TILE4_Q;
	return (int16_t)value;
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

static void core_control(void)
{
	gt32_tile4_attr_forward_all_bm_soa_p_asm(output, frontend);
	sink += (uint16_t)output[0];
}

static void core_candidate(void)
{
	gt32_tile4_attr_forward_all_baseinv_p_l3_asm(output, frontend);
	sink += (uint16_t)output[0];
}

static void full_control(void)
{
	gt32_tile4_frontend_wide_raw_asm(frontend, input);
	gt32_tile4_attr_forward_all_bm_soa_p_asm(output, frontend);
	sink += (uint16_t)output[0];
}

static void full_candidate(void)
{
	gt32_tile4_frontend_wide_raw_asm(frontend, input);
	gt32_tile4_attr_forward_all_baseinv_p_l3_asm(output, frontend);
	sink += (uint16_t)output[0];
}

static double measure(bench_fn function, unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		function();
	return (double)(stop_tsc() - begin) / (double)iterations;
}

static int correctness(void)
{
	int maximum_frontend = 0;
	int maximum_control = 0;
	int maximum_candidate = 0;
	for (unsigned trial = 0; trial < CORRECTNESS_TRIALS; trial++) {
		for (unsigned i = 0; i < WORDS; i++)
			input[i] = (int16_t)((int)(random32() & 7U) - 3);
		gt32_tile4_frontend_wide_raw_asm(frontend, input);
		gt32_tile4_attr_forward_all_bm_soa_p_asm(control, frontend);
		gt32_tile4_attr_forward_all_baseinv_p_l3_asm(candidate, frontend);
		for (unsigned i = 0; i < WORDS; i++) {
			const int frontend_value = frontend[i] < 0 ? -frontend[i] : frontend[i];
			const int control_value = control[i] < 0 ? -control[i] : control[i];
			const int candidate_value = candidate[i] < 0 ? -candidate[i] : candidate[i];
			if (frontend_value > maximum_frontend)
				maximum_frontend = frontend_value;
			if (control_value > maximum_control)
				maximum_control = control_value;
			if (candidate_value > maximum_candidate)
				maximum_candidate = candidate_value;
			if (centered(control[i]) != centered(candidate[i])) {
				fprintf(stderr,
					"landing mismatch trial=%u word=%u control=%d candidate=%d\n",
					trial, i, control[i], candidate[i]);
				return 0;
			}
		}
	}
	printf("correctness trials=%u maximum_frontend_abs=%d maximum_control_abs=%d maximum_candidate_abs=%d\n",
		CORRECTNESS_TRIALS, maximum_frontend, maximum_control,
		maximum_candidate);
	return 1;
}

static void pin_cpu(unsigned cpu)
{
	cpu_set_t set;
	CPU_ZERO(&set);
	CPU_SET(cpu, &set);
	if (sched_setaffinity(0, sizeof(set), &set) != 0)
		perror("sched_setaffinity");
}

static void run_region(const char *name, bench_fn a, bench_fn b,
	unsigned iterations)
{
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		double control_tsc;
		double candidate_tsc;
		if ((sample & 1U) == 0) {
			control_tsc = measure(a, iterations);
			candidate_tsc = measure(b, iterations);
		} else {
			candidate_tsc = measure(b, iterations);
			control_tsc = measure(a, iterations);
		}
		printf("sample region=%s index=%u control=%.6f candidate=%.6f delta=%.6f\n",
			name, sample, control_tsc, candidate_tsc,
			candidate_tsc - control_tsc);
	}
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1 ? (unsigned)strtoul(argv[1], NULL, 0)
		: 2000U;
	const unsigned cpu = argc > 2 ? (unsigned)strtoul(argv[2], NULL, 0) : 2U;
	pin_cpu(cpu);
	for (unsigned i = 0; i < WORDS; i++)
		input[i] = (int16_t)((int)(i & 7U) - 3);
	gt32_tile4_frontend_wide_raw_asm(frontend, input);
	if (!correctness())
		return 1;
	/* Restore a fixed benchmark input after the random differential. */
	for (unsigned i = 0; i < WORDS; i++)
		input[i] = (int16_t)((int)(i & 7U) - 3);
	gt32_tile4_frontend_wide_raw_asm(frontend, input);
	run_region("core", core_control, core_candidate, iterations);
	run_region("full", full_control, full_candidate, iterations);
	printf("sink=%llu\n", (unsigned long long)sink);
	return 0;
}
