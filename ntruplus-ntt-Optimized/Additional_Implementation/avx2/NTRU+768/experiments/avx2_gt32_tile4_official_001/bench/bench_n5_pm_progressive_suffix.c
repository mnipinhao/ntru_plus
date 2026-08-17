#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <x86intrin.h>

#define WORDS 768
#define TRIALS 1000

void gt32_tile4_frontend_wide_raw_asm(int16_t *, const int16_t *);
void gt32_tile4_attr_forward_all_baseinv_p_l3_asm(int16_t *, const int16_t *);
void gt32_global_forward_core_asm(int16_t *, const int16_t *);
void gt32_progressive_suffix_forward_p_safe_core_asm(int16_t *, const int16_t *);
void gt32_progressive_suffix_forward_m_core_asm(int16_t *, const int16_t *);

static int16_t coeff[4][WORDS] __attribute__((aligned(64)));
static int16_t frontend[4][WORDS] __attribute__((aligned(64)));
static int16_t control[4][WORDS] __attribute__((aligned(64)));
static int16_t candidate[4][WORDS] __attribute__((aligned(64)));
static volatile uint64_t sink;
static uint32_t rng = 0x504d5335U;

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
	if (value < 0) value += 3457;
	if (value > 1728) value -= 3457;
	return value;
}

static int equal_mod_q(const int16_t a[WORDS], const int16_t b[WORDS])
{
	for (unsigned i = 0; i < WORDS; i++)
		if (center(a[i]) != center(b[i])) return 0;
	return 1;
}

static int differential(void)
{
	for (unsigned trial = 0; trial < TRIALS; trial++) {
		for (unsigned i = 0; i < WORDS; i++)
			coeff[0][i] = (int16_t)((int)(random32() & 7U) - 3);
		gt32_tile4_frontend_wide_raw_asm(frontend[0], coeff[0]);

		gt32_tile4_attr_forward_all_baseinv_p_l3_asm(
			control[0], frontend[0]);
		gt32_progressive_suffix_forward_p_safe_core_asm(
			candidate[0], frontend[0]);
		if (!equal_mod_q(control[0], candidate[0]))
			return fprintf(stderr, "P suffix mismatch at trial %u\n", trial), 0;

		gt32_global_forward_core_asm(control[0], frontend[0]);
		gt32_progressive_suffix_forward_m_core_asm(
			candidate[0], frontend[0]);
		if (!equal_mod_q(control[0], candidate[0]))
			return fprintf(stderr, "M suffix mismatch at trial %u\n", trial), 0;
	}
	printf("correctness trials=%u P=pass M=pass\n", TRIALS);
	return 1;
}

__attribute__((noinline)) static void p_control(void)
{
	gt32_tile4_attr_forward_all_baseinv_p_l3_asm(control[0], frontend[0]);
	gt32_tile4_attr_forward_all_baseinv_p_l3_asm(control[1], frontend[1]);
}

__attribute__((noinline)) static void p_candidate(void)
{
	gt32_progressive_suffix_forward_p_safe_core_asm(candidate[0], frontend[0]);
	gt32_progressive_suffix_forward_p_safe_core_asm(candidate[1], frontend[1]);
}

__attribute__((noinline)) static void m_control(void)
{
	for (unsigned i = 0; i < 4; i++)
		gt32_global_forward_core_asm(control[i], frontend[i]);
}

__attribute__((noinline)) static void m_candidate(void)
{
	for (unsigned i = 0; i < 4; i++)
		gt32_progressive_suffix_forward_m_core_asm(candidate[i], frontend[i]);
}

__attribute__((noinline)) static void weighted_control(void)
{
	p_control();
	for (unsigned i = 0; i < 4; i++)
		gt32_global_forward_core_asm(control[i], frontend[i]);
}

__attribute__((noinline)) static void weighted_candidate(void)
{
	p_candidate();
	for (unsigned i = 0; i < 4; i++)
		gt32_progressive_suffix_forward_m_core_asm(candidate[i], frontend[i]);
}

typedef void (*region_fn)(void);

static void run(region_fn fn, unsigned iterations)
{
	for (unsigned i = 0; i < iterations; i++) fn();
	sink += (uint64_t)(uint16_t)control[0][iterations % WORDS]
		+ (uint64_t)(uint16_t)candidate[3][(iterations * 5U) % WORDS];
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
		(unsigned)strtoul(argv[1], NULL, 0) : 10000;
	const char *gate = argc > 2 ? argv[2] : "weighted";
	const char *backend = argc > 3 ? argv[3] : "control";
	const int skip_check = argc > 4 && strcmp(argv[4], "nocheck") == 0;
	cpu_set_t set;
	CPU_ZERO(&set);
	CPU_SET(1, &set);
	(void)sched_setaffinity(0, sizeof set, &set);

	for (unsigned p = 0; p < 4; p++) {
		for (unsigned i = 0; i < WORDS; i++)
			coeff[p][i] = (int16_t)((int)(random32() & 7U) - 3);
		gt32_tile4_frontend_wide_raw_asm(frontend[p], coeff[p]);
	}
	if (!skip_check && !differential()) return 1;

	const int use_candidate = strcmp(backend, "candidate") == 0;
	region_fn fn = NULL;
	if (strcmp(gate, "p") == 0) fn = use_candidate ? p_candidate : p_control;
	else if (strcmp(gate, "m") == 0) fn = use_candidate ? m_candidate : m_control;
	else if (strcmp(gate, "weighted") == 0)
		fn = use_candidate ? weighted_candidate : weighted_control;
	if (fn == NULL || (!use_candidate && strcmp(backend, "control") != 0))
		return 2;
	run(fn, 100);
	const uint64_t ticks = timed(fn, iterations);
	printf("PM_SUFFIX_PMU,gate=%s,backend=%s,iterations=%u,correctness=pass,"
		"tsc_per_call=%.6f,sink=%llu\n", gate, backend, iterations,
		(double)ticks / iterations, (unsigned long long)sink);
	return 0;
}
