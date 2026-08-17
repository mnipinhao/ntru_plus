#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

#include <x86intrin.h>

#include "tile4.h"

#define WORDS GT32_TILE4_POLY_WORDS
#define BYTES GT32_TILE4_SERIALIZED_BYTES
#define SAMPLES 20U
#define Q 3457U

typedef void (*region_fn)(void);

typedef struct {
	uint8_t before[64];
	int16_t words[WORDS] __attribute__((aligned(64)));
	uint8_t after[64];
} guarded_poly;

static uint8_t encoded_c[BYTES] __attribute__((aligned(64)));
static uint8_t encoded_f[BYTES] __attribute__((aligned(64)));
static int16_t control_c[WORDS] __attribute__((aligned(64)));
static int16_t control_f[WORDS] __attribute__((aligned(64)));
static guarded_poly control_out;
static guarded_poly candidate_out;
static volatile uint64_t sink;

static uint32_t next_random(uint32_t *state)
{
	*state = *state * UINT32_C(1664525) + UINT32_C(1013904223);
	return *state;
}

static void pack12(uint8_t out[BYTES], const uint16_t in[WORDS])
{
	for (unsigned pair = 0; pair < WORDS / 2U; pair++) {
		const uint16_t a = in[2U * pair];
		const uint16_t b = in[2U * pair + 1U];
		out[3U * pair] = (uint8_t)a;
		out[3U * pair + 1U] = (uint8_t)((a >> 8)
			| (uint16_t)(b << 4));
		out[3U * pair + 2U] = (uint8_t)(b >> 4);
	}
}

static void fill_encoded(uint8_t out[BYTES], uint32_t *state)
{
	uint16_t values[WORDS];
	for (unsigned i = 0; i < WORDS; i++)
		values[i] = (uint16_t)(next_random(state) % Q);
	pack12(out, values);
}

static void set_canaries(guarded_poly *poly, uint8_t tag)
{
	memset(poly->before, tag, sizeof poly->before);
	memset(poly->after, (uint8_t)(tag ^ UINT8_C(0xff)),
		sizeof poly->after);
}

static int canaries_ok(const guarded_poly *poly, uint8_t tag)
{
	for (unsigned i = 0; i < sizeof poly->before; i++)
		if (poly->before[i] != tag
			|| poly->after[i] != (uint8_t)(tag ^ UINT8_C(0xff)))
			return 0;
	return 1;
}

static int control(void)
{
	int failure = gt32_q24_decode_soa_asm(control_c, encoded_c);
	failure |= gt32_q24_decode_soa_asm(control_f, encoded_f);
	gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm(
		control_out.words, control_c, control_f);
	return failure;
}

static int candidate(void)
{
	return gt32_q24_decode2_b3_scale_stream_asm(candidate_out.words,
		encoded_c, encoded_f);
}

static void control_region(void)
{
	sink += (unsigned)control();
	sink += (uint16_t)control_out.words[0];
}

static void candidate_region(void)
{
	sink += (unsigned)candidate();
	sink += (uint16_t)candidate_out.words[0];
}

static void require_equal(void)
{
	if (memcmp(control_out.words, candidate_out.words,
			sizeof control_out.words) != 0) {
		fputs("streaming B3 output mismatch\n", stderr);
		exit(1);
	}
}

static void guard_page_test(void)
{
	const long page = sysconf(_SC_PAGESIZE);
	uint8_t *left = mmap(NULL, (size_t)(2 * page), PROT_READ | PROT_WRITE,
		MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
	uint8_t *right = mmap(NULL, (size_t)(2 * page), PROT_READ | PROT_WRITE,
		MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
	if (left == MAP_FAILED || right == MAP_FAILED)
		exit(1);
	uint8_t *const c = left + page - BYTES;
	uint8_t *const f = right + page - BYTES;
	memset(c, 0, BYTES);
	memset(f, 0, BYTES);
	if (mprotect(left + page, (size_t)page, PROT_NONE) != 0
		|| mprotect(right + page, (size_t)page, PROT_NONE) != 0
		|| mprotect(left, (size_t)page, PROT_READ) != 0
		|| mprotect(right, (size_t)page, PROT_READ) != 0)
		exit(1);
	set_canaries(&candidate_out, UINT8_C(0x61));
	if (gt32_q24_decode2_b3_scale_stream_asm(candidate_out.words, c, f)
		!= 0 || !canaries_ok(&candidate_out, UINT8_C(0x61)))
		exit(1);
	if (munmap(left, (size_t)(2 * page)) != 0
		|| munmap(right, (size_t)(2 * page)) != 0)
		exit(1);
}

static void correctness(void)
{
	uint32_t state = UINT32_C(0xc1f10a01);
	uint16_t malformed[WORDS] = {0};
	guard_page_test();
	for (unsigned trial = 0; trial < 1000; trial++) {
		fill_encoded(encoded_c, &state);
		fill_encoded(encoded_f, &state);
		set_canaries(&control_out, UINT8_C(0x42));
		set_canaries(&candidate_out, UINT8_C(0x61));
		if (control() != 0 || candidate() != 0)
			exit(1);
		require_equal();
		if (!canaries_ok(&control_out, UINT8_C(0x42))
			|| !canaries_ok(&candidate_out, UINT8_C(0x61)))
			exit(1);
	}

	/* Every serialized coefficient position independently rejects q. */
	for (unsigned slot = 0; slot < WORDS; slot++) {
		memset(malformed, 0, sizeof malformed);
		malformed[slot] = Q;
		pack12(encoded_c, malformed);
		memset(encoded_f, 0, sizeof encoded_f);
		if (control() != 1 || candidate() != 1)
			exit(1);
		require_equal();
		memset(encoded_c, 0, sizeof encoded_c);
		pack12(encoded_f, malformed);
		if (control() != 1 || candidate() != 1)
			exit(1);
		require_equal();
	}
	memset(malformed, 0, sizeof malformed);
	malformed[0] = Q;
	pack12(encoded_c, malformed);
	malformed[0] = 0;
	malformed[WORDS - 1U] = Q;
	pack12(encoded_f, malformed);
	if (control() != 1 || candidate() != 1)
		exit(1);
	require_equal();
}

static uint64_t start_tsc(void)
{
	_mm_lfence();
	return __rdtsc();
}

static uint64_t stop_tsc(void)
{
	unsigned auxiliary;
	const uint64_t result = __rdtscp(&auxiliary);
	_mm_lfence();
	return result;
}

static double measure(region_fn function, unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned iteration = 0; iteration < iterations; iteration++)
		function();
	return (double)(stop_tsc() - begin) / iterations;
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	cpu_set_t set;
	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof set, &set) != 0)
		perror("sched_setaffinity");

	correctness();
	uint32_t state = UINT32_C(0xc1f1beef);
	fill_encoded(encoded_c, &state);
	fill_encoded(encoded_f, &state);
	for (unsigned warm = 0; warm < 2; warm++) {
		(void)measure(control_region, 1000);
		(void)measure(candidate_region, 1000);
	}
	printf("META,scope=q24-decode2-b3-frontier,correctness=word-exact,iterations=%u,samples=%u,materialized-inputs-candidate=0,b3-arithmetic=unchanged\n",
		iterations, SAMPLES);
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		double control_tsc;
		double candidate_tsc;
		if ((sample & 1U) == 0U) {
			control_tsc = measure(control_region, iterations);
			candidate_tsc = measure(candidate_region, iterations);
		} else {
			candidate_tsc = measure(candidate_region, iterations);
			control_tsc = measure(control_region, iterations);
		}
		printf("SAMPLE,decode2_b3,%u,%.6f,%.6f,%.6f\n", sample,
			control_tsc, candidate_tsc, candidate_tsc - control_tsc);
	}
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}
