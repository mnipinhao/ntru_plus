#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <x86intrin.h>

#include "poly.h"
#include "tile4.h"
#include "../generated/tile4_serialized_mapping.h"

#define WORDS GT32_TILE4_POLY_WORDS

static poly official_f __attribute__((aligned(64)));
static poly official_g __attribute__((aligned(64)));
static poly official_inverse0 __attribute__((aligned(64)));
static poly official_inverse1 __attribute__((aligned(64)));
static poly official_output0 __attribute__((aligned(64)));
static poly official_output1 __attribute__((aligned(64)));
static gt32_f0_aos_e0_t gt_f;
static gt32_f0_aos_e0_t gt_g;
static gt32_baseinv_j1_aos_e1_t gt_inverse0;
static gt32_baseinv_j1_aos_e1_t gt_inverse1;
static int16_t gt_output0[WORDS] __attribute__((aligned(64)));
static int16_t gt_output1[WORDS] __attribute__((aligned(64)));
static volatile uint64_t sink;

static unsigned official_word(unsigned serialized)
{
	return 128U * (serialized / 128U) + (serialized % 128U) / 8U
		+ 16U * (serialized % 8U);
}

static void official_to_aos(int16_t *aos, const poly *official)
{
	for (unsigned serialized = 0; serialized < WORDS; serialized++)
		aos[gt32_tile4_serialized_to_aos[serialized]] =
			official->coeffs[official_word(serialized)];
}

static int centered_mod_q(int16_t value)
{
	int result = value % GT32_TILE4_Q;
	if (result < 0)
		result += GT32_TILE4_Q;
	if (result > GT32_TILE4_Q / 2)
		result -= GT32_TILE4_Q;
	return result;
}

__attribute__((noinline))
static void official_a0(void)
{
	(void)poly_baseinv(&official_inverse0, &official_f);
	(void)poly_baseinv(&official_inverse1, &official_g);
}

__attribute__((noinline))
static void gt_a0(void)
{
	(void)gt32_tile4_baseinv_j1_aos_avx2(&gt_inverse0, &gt_f);
	(void)gt32_tile4_baseinv_j1_aos_avx2(&gt_inverse1, &gt_g);
}

__attribute__((noinline))
static void official_a1(void)
{
	(void)poly_baseinv(&official_inverse0, &official_f);
	(void)poly_baseinv(&official_inverse1, &official_g);
	poly_basemul(&official_output0, &official_g, &official_inverse0);
	poly_basemul(&official_output1, &official_f, &official_inverse1);
}

__attribute__((noinline))
static void gt_a1(void)
{
	(void)gt32_tile4_baseinv_j1_aos_avx2(&gt_inverse0, &gt_f);
	(void)gt32_tile4_baseinv_j1_aos_avx2(&gt_inverse1, &gt_g);
	gt32_tile4_basemul_aos_dot_r1u_asm(gt_output0, gt_g.words,
		gt_inverse0.words);
	gt32_tile4_basemul_aos_dot_r1u_asm(gt_output1, gt_f.words,
		gt_inverse1.words);
}

__attribute__((noinline))
static void official_consumer(void)
{
	poly_basemul(&official_output0, &official_g, &official_inverse0);
	poly_basemul(&official_output1, &official_f, &official_inverse1);
}

__attribute__((noinline))
static void gt_consumer(void)
{
	gt32_tile4_basemul_aos_dot_r1u_asm(gt_output0, gt_g.words,
		gt_inverse0.words);
	gt32_tile4_basemul_aos_dot_r1u_asm(gt_output1, gt_f.words,
		gt_inverse1.words);
}

typedef void (*region_fn)(void);

static void run(region_fn function, unsigned iterations)
{
	for (unsigned i = 0; i < iterations; i++)
		function();
	sink += (uint16_t)gt_output0[iterations % WORDS]
		+ (uint16_t)official_output0.coeffs[iterations % WORDS];
}

static uint64_t timed_run(region_fn function, unsigned iterations)
{
	unsigned aux;
	_mm_lfence();
	const uint64_t begin = __rdtsc();
	run(function, iterations);
	const uint64_t end = __rdtscp(&aux);
	_mm_lfence();
	return end - begin;
}

static int prepare(void)
{
	for (unsigned i = 0; i < WORDS; i++) {
		official_f.coeffs[i] = (int16_t)((int)(i % 7U) - 3);
		official_g.coeffs[i] = (int16_t)((int)((5U * i + 3U) % 7U) - 3);
	}
	official_f.coeffs[0]++;
	official_g.coeffs[0]++;
	poly_ntt(&official_f);
	poly_ntt(&official_g);
	if (poly_baseinv(&official_inverse0, &official_f) != 0
		|| poly_baseinv(&official_inverse1, &official_g) != 0)
		return 0;
	official_to_aos(gt_f.words, &official_f);
	official_to_aos(gt_g.words, &official_g);
	if (gt32_tile4_baseinv_j1_aos_avx2(&gt_inverse0, &gt_f) != 0
		|| gt32_tile4_baseinv_j1_aos_avx2(&gt_inverse1, &gt_g) != 0)
		return 0;
	poly_basemul(&official_output0, &official_g, &official_inverse0);
	poly_basemul(&official_output1, &official_f, &official_inverse1);
	gt32_tile4_basemul_aos_dot_r1u_asm(gt_output0, gt_g.words,
		gt_inverse0.words);
	gt32_tile4_basemul_aos_dot_r1u_asm(gt_output1, gt_f.words,
		gt_inverse1.words);
	int16_t mapped[WORDS] __attribute__((aligned(64)));
	official_to_aos(mapped, &official_output0);
	for (unsigned i = 0; i < WORDS; i++)
		if (centered_mod_q(mapped[i]) != centered_mod_q(gt_output0[i]))
			return 0;
	official_to_aos(mapped, &official_output1);
	for (unsigned i = 0; i < WORDS; i++)
		if (centered_mod_q(mapped[i]) != centered_mod_q(gt_output1[i]))
			return 0;
	return 1;
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 10000U;
	const char *gate = argc > 2 ? argv[2] : "a1";
	const char *backend = argc > 3 ? argv[3] : "official";
	cpu_set_t set;
	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof set, &set) != 0)
		perror("sched_setaffinity");
	if (!prepare()) {
		fputs("K3-B correctness/input preparation failed\n", stderr);
		return 1;
	}
	region_fn function = NULL;
	if (strcmp(gate, "a0") == 0)
		function = strcmp(backend, "official") == 0 ? official_a0 : gt_a0;
	else if (strcmp(gate, "a1") == 0)
		function = strcmp(backend, "official") == 0 ? official_a1 : gt_a1;
	else if (strcmp(gate, "consumer") == 0)
		function = strcmp(backend, "official") == 0
			? official_consumer : gt_consumer;
	if (function == NULL || (strcmp(backend, "official") != 0
		&& strcmp(backend, "gt32-j1-r1u") != 0)) {
		fprintf(stderr, "unknown gate/backend: %s/%s\n", gate, backend);
		return 2;
	}
	run(function, 1000U);
	const uint64_t ticks = timed_run(function, iterations);
	printf("K3B_PMU,gate=%s,backend=%s,iterations=%u,correctness=pass,tsc_per_call=%.6f,sink=%llu\n",
		gate, backend, iterations, (double)ticks / iterations,
		(unsigned long long)sink);
	return 0;
}
