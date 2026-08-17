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
#define BYTES GT32_TILE4_SERIALIZED_BYTES
#define SAMPLES 20

typedef struct {
	int16_t j_soa[WORDS];
	int16_t product_aos[WORDS];
	int16_t product_soa[WORDS];
	int16_t p0[WORDS];
} control_scratch_t;

typedef struct {
	uint64_t before[8];
	int16_t p0[WORDS];
	uint64_t after[8];
} guarded_p0_t;

typedef void (*edge_fn)(uint8_t *, const int16_t *, const int16_t *, void *);

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

static uint32_t next_random(uint32_t *state)
{
	*state = *state * 1664525U + 1013904223U;
	return *state;
}

static void fill_inputs(int16_t *f0, int16_t *j1, uint32_t *state,
	unsigned trial)
{
	for (unsigned i = 0; i < WORDS; i++) {
		if (trial == 0) {
			f0[i] = 0;
			j1[i] = 0;
		} else if (trial == 1) {
			f0[i] = (int16_t)((i & 1U) ? 10788 : -10788);
			j1[i] = (int16_t)((i & 1U) ? 1728 : -1728);
		} else {
			f0[i] = (int16_t)((int32_t)(next_random(state) % 21577U)
				- 10788);
			j1[i] = (int16_t)((int32_t)(next_random(state) % 3457U)
				- 1728);
		}
	}
}

static void reference_p0(int16_t *p0, const int16_t *f0, const int16_t *j1)
{
	int16_t aos[WORDS] __attribute__((aligned(64)));
	gt32_tile4_basemul_aos_dot_r1u_asm(aos, f0, j1);
	for (unsigned serialized = 0; serialized < WORDS; serialized++) {
		const unsigned official_word = 128U * (serialized / 128U)
			+ (serialized % 128U) / 8U + 16U * (serialized % 8U);
		p0[official_word] = aos[gt32_tile4_serialized_to_aos[serialized]];
	}
}

__attribute__((noinline))
static void control_edge(uint8_t *bytes, const int16_t *f0,
	const int16_t *j1, void *opaque)
{
	control_scratch_t *scratch = opaque;
	gt32_tile4_attr_transpose_one_asm(scratch->j_soa, j1);
	gt32_tile4_basemul_e1_soa_aos_to_aos_asm(scratch->product_aos,
		scratch->j_soa, f0);
	gt32_tile4_attr_transpose_one_asm(scratch->product_soa,
		scratch->product_aos);
	gt32_tile4_soa_to_official_words_grouped_asm(scratch->p0,
		scratch->product_soa);
	poly_tobytes(bytes, (const poly *)scratch->p0);
}

__attribute__((noinline))
static void control_route(uint8_t *unused, const int16_t *f0,
	const int16_t *j1, void *opaque)
{
	control_scratch_t *scratch = opaque;
	(void)unused;
	gt32_tile4_attr_transpose_one_asm(scratch->j_soa, j1);
	gt32_tile4_basemul_e1_soa_aos_to_aos_asm(scratch->product_aos,
		scratch->j_soa, f0);
	gt32_tile4_attr_transpose_one_asm(scratch->product_soa,
		scratch->product_aos);
	gt32_tile4_soa_to_official_words_grouped_asm(scratch->p0,
		scratch->product_soa);
}

__attribute__((noinline))
static void s0_edge(uint8_t *bytes, const int16_t *f0,
	const int16_t *j1, void *opaque)
{
	int16_t *p0 = opaque;
	gt32_tile4_keygen_fj1_p0_s0_asm(p0, f0, j1);
	poly_tobytes(bytes, (const poly *)p0);
}

__attribute__((noinline))
static void s0_route(uint8_t *unused, const int16_t *f0,
	const int16_t *j1, void *opaque)
{
	(void)unused;
	gt32_tile4_keygen_fj1_p0_s0_asm(opaque, f0, j1);
}

__attribute__((noinline))
static void s1_edge(uint8_t *bytes, const int16_t *f0,
	const int16_t *j1, void *opaque)
{
	int16_t *p0 = opaque;
	gt32_tile4_keygen_fj1_p0_s1_asm(p0, f0, j1);
	poly_tobytes(bytes, (const poly *)p0);
}

__attribute__((noinline))
static void s1_route(uint8_t *unused, const int16_t *f0,
	const int16_t *j1, void *opaque)
{
	(void)unused;
	gt32_tile4_keygen_fj1_p0_s1_asm(opaque, f0, j1);
}

static double measure(edge_fn fn, uint8_t *bytes, const int16_t *f0,
	const int16_t *j1, void *scratch, unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		fn(bytes, f0, j1, scratch);
	const uint64_t end = stop_tsc();
	sink += bytes[iterations % BYTES];
	return (double)(end - begin) / iterations;
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	int16_t f0[WORDS] __attribute__((aligned(64)));
	int16_t j1[WORDS] __attribute__((aligned(64)));
	int16_t reference[WORDS] __attribute__((aligned(64)));
	guarded_p0_t s0_guard __attribute__((aligned(64)));
	guarded_p0_t s1_guard __attribute__((aligned(64)));
	uint8_t ref_bytes[BYTES] __attribute__((aligned(64)));
	uint8_t control_bytes[BYTES] __attribute__((aligned(64)));
	uint8_t s0_bytes[BYTES] __attribute__((aligned(64)));
	uint8_t s1_bytes[BYTES] __attribute__((aligned(64)));
	control_scratch_t control __attribute__((aligned(64)));
	uint32_t state = 0xF001B1U;
	cpu_set_t set;
	int16_t *const s0_p0 = s0_guard.p0;
	int16_t *const s1_p0 = s1_guard.p0;

	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof(set), &set) != 0)
		perror("sched_setaffinity");
	memset(s0_guard.before, 0xA5, sizeof(s0_guard.before));
	memset(s0_guard.after, 0x5A, sizeof(s0_guard.after));
	memset(s1_guard.before, 0xA5, sizeof(s1_guard.before));
	memset(s1_guard.after, 0x5A, sizeof(s1_guard.after));

	for (unsigned trial = 0; trial < 1000; trial++) {
		fill_inputs(f0, j1, &state, trial);
		reference_p0(reference, f0, j1);
		gt32_tile4_keygen_fj1_p0_s0_asm(s0_p0, f0, j1);
		gt32_tile4_keygen_fj1_p0_s1_asm(s1_p0, f0, j1);
		if (memcmp(reference, s0_p0, sizeof(reference)) != 0
			|| memcmp(reference, s1_p0, sizeof(reference)) != 0) {
			fprintf(stderr, "P0 differential failed trial=%u\n", trial);
			return 1;
		}
		poly_tobytes(ref_bytes, (const poly *)reference);
		control_edge(control_bytes, f0, j1, &control);
		s0_edge(s0_bytes, f0, j1, s0_p0);
		s1_edge(s1_bytes, f0, j1, s1_p0);
		if (memcmp(ref_bytes, control_bytes, BYTES) != 0
			|| memcmp(ref_bytes, s0_bytes, BYTES) != 0
			|| memcmp(ref_bytes, s1_bytes, BYTES) != 0) {
			fprintf(stderr, "pack differential failed trial=%u\n", trial);
			return 1;
		}
	}
	for (unsigned i = 0; i < 8; i++) {
		if (s0_guard.before[i] != UINT64_C(0xA5A5A5A5A5A5A5A5)
			|| s0_guard.after[i] != UINT64_C(0x5A5A5A5A5A5A5A5A)
			|| s1_guard.before[i] != UINT64_C(0xA5A5A5A5A5A5A5A5)
			|| s1_guard.after[i] != UINT64_C(0x5A5A5A5A5A5A5A5A)) {
			fprintf(stderr, "guard-buffer overwrite\n");
			return 1;
		}
	}

	for (unsigned warm = 0; warm < 2; warm++) {
		(void)measure(control_edge, control_bytes, f0, j1, &control, 1000);
		(void)measure(s0_edge, s0_bytes, f0, j1, s0_p0, 1000);
		(void)measure(s1_edge, s1_bytes, f0, j1, s1_p0, 1000);
	}
	printf("META,correctness=bit-exact-pass,scope=F0xJ1-to-P0-to-pack,"
		"iterations=%u,samples=%u\n", iterations, SAMPLES);
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		double c, s0, s1, rc, rs0, rs1;
		if ((sample & 1U) == 0U) {
			c = measure(control_edge, control_bytes, f0, j1, &control, iterations);
			s0 = measure(s0_edge, s0_bytes, f0, j1, s0_p0, iterations);
			s1 = measure(s1_edge, s1_bytes, f0, j1, s1_p0, iterations);
			rc = measure(control_route, control_bytes, f0, j1, &control, iterations);
			rs0 = measure(s0_route, s0_bytes, f0, j1, s0_p0, iterations);
			rs1 = measure(s1_route, s1_bytes, f0, j1, s1_p0, iterations);
		} else {
			rs1 = measure(s1_route, s1_bytes, f0, j1, s1_p0, iterations);
			rs0 = measure(s0_route, s0_bytes, f0, j1, s0_p0, iterations);
			rc = measure(control_route, control_bytes, f0, j1, &control, iterations);
			s1 = measure(s1_edge, s1_bytes, f0, j1, s1_p0, iterations);
			s0 = measure(s0_edge, s0_bytes, f0, j1, s0_p0, iterations);
			c = measure(control_edge, control_bytes, f0, j1, &control, iterations);
		}
		printf("SAMPLE,%u,%.6f,%.6f,%.6f,%.6f,%.6f\n", sample,
			c, s0, s1, c - s0, c - s1);
		printf("ROUTE_SAMPLE,%u,%.6f,%.6f,%.6f\n", sample,
			rc, rs0, rs1);
	}
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}
