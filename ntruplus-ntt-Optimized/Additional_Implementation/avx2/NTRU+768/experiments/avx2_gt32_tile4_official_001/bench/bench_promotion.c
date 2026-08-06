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

typedef void (*kernel_fn)(int16_t *, const int16_t *, const int16_t *);

void poly_ntt(int16_t *);
void poly_basemul_scale(int16_t *, const int16_t *, const int16_t *);
void poly_invntt_scale(int16_t *);
void poly_crepmod3(int16_t *);

static int16_t official_a[WORDS] __attribute__((aligned(64)));
static int16_t official_b[WORDS] __attribute__((aligned(64)));
static int16_t tile4_a[WORDS] __attribute__((aligned(64)));
static int16_t tile4_b[WORDS] __attribute__((aligned(64)));
static int16_t product[WORDS] __attribute__((aligned(64)));
static int16_t rows[WORDS] __attribute__((aligned(64)));
static int16_t work_a[WORDS] __attribute__((aligned(64)));
static int16_t work_b[WORDS] __attribute__((aligned(64)));
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

static double measure(kernel_fn fn, int16_t *out, const int16_t *a,
	const int16_t *b, unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		fn(out, a, b);
	const uint64_t end = stop_tsc();
	sink += (uint16_t)out[iterations & 767U];
	return (double)(end - begin) / iterations;
}

__attribute__((noinline))
static void official_bm(int16_t *out, const int16_t *a, const int16_t *b)
{
	poly_basemul_scale(out, a, b);
}

__attribute__((noinline))
static void tile4_bm(int16_t *out, const int16_t *a, const int16_t *b)
{
	gt32_tile4_basemul_c3center_late_aos_private_asm(out, a, b);
}

__attribute__((noinline))
static void official_bm_inverse(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	poly_basemul_scale(out, a, b);
	poly_invntt_scale(out);
}

__attribute__((noinline))
static void tile4_bm_inverse(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	gt32_tile4_basemul_c3center_late_aos_private_asm(product, a, b);
	gt32_tile4_inverse_all_pair_asm(rows, product);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out, rows);
}

__attribute__((noinline))
static void official_full(int16_t *out, const int16_t *a, const int16_t *b)
{
	memcpy(work_a, a, sizeof(work_a));
	memcpy(work_b, b, sizeof(work_b));
	poly_ntt(work_a);
	poly_ntt(work_b);
	poly_basemul_scale(out, work_a, work_b);
	poly_invntt_scale(out);
}

__attribute__((noinline))
static void tile4_full(int16_t *out, const int16_t *a, const int16_t *b)
{
	memcpy(work_a, a, sizeof(work_a));
	memcpy(work_b, b, sizeof(work_b));
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(work_a, work_a);
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(work_b, work_b);
	gt32_tile4_basemul_c3center_late_aos_private_asm(product, work_a, work_b);
	gt32_tile4_inverse_all_pair_asm(rows, product);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out, rows);
}

__attribute__((noinline))
static void official_full_crep(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	official_full(out, a, b);
	poly_crepmod3(out);
}

__attribute__((noinline))
static void tile4_full_crep(int16_t *out, const int16_t *a,
	const int16_t *b)
{
	tile4_full(out, a, b);
	poly_crepmod3(out);
}

struct gate {
	const char *name;
	kernel_fn official;
	kernel_fn tile4;
	const int16_t *official_input_a;
	const int16_t *official_input_b;
	const int16_t *tile4_input_a;
	const int16_t *tile4_input_b;
};

static int16_t centered_mod_q(int16_t value)
{
	int result = value % 3457;
	if (result < 0)
		result += 3457;
	if (result > 1728)
		result -= 3457;
	return (int16_t)result;
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 100000U;
	const unsigned reverse_pattern = argc > 2
		? (unsigned)strtoul(argv[2], NULL, 10) & 1U : 0U;
	int16_t coefficients_a[WORDS] __attribute__((aligned(64)));
	int16_t coefficients_b[WORDS] __attribute__((aligned(64)));
	int16_t out[WORDS] __attribute__((aligned(64)));
	cpu_set_t set;
	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof(set), &set) != 0)
		perror("sched_setaffinity");
	for (unsigned i = 0; i < WORDS; i++) {
		coefficients_a[i] = (int16_t)((int)(i % 8U) - 3);
		coefficients_b[i] = (int16_t)((int)((3U * i + 1U) % 8U) - 3);
	}
	memcpy(official_a, coefficients_a, sizeof(official_a));
	memcpy(official_b, coefficients_b, sizeof(official_b));
	memcpy(tile4_a, coefficients_a, sizeof(tile4_a));
	memcpy(tile4_b, coefficients_b, sizeof(tile4_b));
	poly_ntt(official_a);
	poly_ntt(official_b);
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(tile4_a, tile4_a);
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(tile4_b, tile4_b);

	const struct gate gates[] = {
		{"bm", official_bm, tile4_bm,
			official_a, official_b, tile4_a, tile4_b},
		{"bm_i1_t9", official_bm_inverse, tile4_bm_inverse,
			official_a, official_b, tile4_a, tile4_b},
		{"full", official_full, tile4_full,
			coefficients_a, coefficients_b, coefficients_a, coefficients_b},
		{"full_crep", official_full_crep, tile4_full_crep,
			coefficients_a, coefficients_b, coefficients_a, coefficients_b},
	};
	int16_t official_result[WORDS] __attribute__((aligned(64)));
	int16_t tile4_result[WORDS] __attribute__((aligned(64)));
	official_full(official_result, coefficients_a, coefficients_b);
	tile4_full(tile4_result, coefficients_a, coefficients_b);
	for (unsigned i = 0; i < WORDS; i++) {
		if (centered_mod_q(official_result[i]) != centered_mod_q(tile4_result[i])) {
			fprintf(stderr, "promotion full differential failed at %u\n", i);
			return 1;
		}
	}
	if (argc > 5 && strcmp(argv[3], "pmu") == 0) {
		const char *gate_name = argv[4];
		const char *backend = argv[5];
		for (unsigned gate = 0; gate < sizeof(gates) / sizeof(gates[0]); gate++) {
			if (strcmp(gates[gate].name, gate_name) != 0)
				continue;
			const int tile = strcmp(backend, "tile4") == 0;
			kernel_fn fn = tile ? gates[gate].tile4 : gates[gate].official;
			const int16_t *input_a = tile ? gates[gate].tile4_input_a
				: gates[gate].official_input_a;
			const int16_t *input_b = tile ? gates[gate].tile4_input_b
				: gates[gate].official_input_b;
			for (unsigned warm = 0; warm < 2; warm++)
				(void)measure(fn, out, input_a, input_b, 1000);
			(void)measure(fn, out, input_a, input_b, iterations);
			printf("PMU,gate=%s,backend=%s,iterations=%u,sink=%llu\n",
				gate_name, backend, iterations, (unsigned long long)sink);
			return 0;
		}
		fprintf(stderr, "unknown PMU gate: %s\n", gate_name);
		return 2;
	}
	official_full_crep(official_result, coefficients_a, coefficients_b);
	tile4_full_crep(tile4_result, coefficients_a, coefficients_b);
	for (unsigned i = 0; i < WORDS; i++) {
		if (official_result[i] != tile4_result[i]) {
			fprintf(stderr, "promotion crep differential failed at %u\n", i);
			return 1;
		}
	}

	printf("META,correctness=pass,iterations=%u,pattern=%s,out=%p,official_a=%p,tile4_a=%p,"
		"official_bm=%p,tile4_bm=%p,official_full=%p,tile4_full=%p\n",
		iterations, reverse_pattern ? "BAAB" : "ABBA", (void *)out,
		(void *)official_a, (void *)tile4_a,
		(void *)(uintptr_t)official_bm, (void *)(uintptr_t)tile4_bm,
		(void *)(uintptr_t)official_full, (void *)(uintptr_t)tile4_full);
	for (unsigned gate = 0; gate < sizeof(gates) / sizeof(gates[0]); gate++) {
		for (unsigned warm = 0; warm < 2; warm++) {
			(void)measure(gates[gate].official, out,
				gates[gate].official_input_a, gates[gate].official_input_b, 1000);
			(void)measure(gates[gate].tile4, out,
				gates[gate].tile4_input_a, gates[gate].tile4_input_b, 1000);
		}
		for (unsigned sample = 0; sample < SAMPLES; sample++) {
			const unsigned phase = (sample + (reverse_pattern ? 2U : 0U)) & 3U;
			double official_ticks;
			double tile4_ticks;
			if (phase == 0U || phase == 3U) {
				official_ticks = measure(gates[gate].official, out,
					gates[gate].official_input_a,
					gates[gate].official_input_b, iterations);
				tile4_ticks = measure(gates[gate].tile4, out,
					gates[gate].tile4_input_a,
					gates[gate].tile4_input_b, iterations);
			} else {
				tile4_ticks = measure(gates[gate].tile4, out,
					gates[gate].tile4_input_a,
					gates[gate].tile4_input_b, iterations);
				official_ticks = measure(gates[gate].official, out,
					gates[gate].official_input_a,
					gates[gate].official_input_b, iterations);
			}
			printf("SAMPLE,%s,%u,%.6f,%.6f,%.9f\n", gates[gate].name,
				sample, official_ticks, tile4_ticks,
				tile4_ticks / official_ticks);
		}
	}
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}
