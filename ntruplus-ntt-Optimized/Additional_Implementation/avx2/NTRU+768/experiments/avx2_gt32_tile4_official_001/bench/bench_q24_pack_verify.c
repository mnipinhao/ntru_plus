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

typedef void (*region_fn)(void);

static int16_t coefficients[WORDS] __attribute__((aligned(64)));
static int16_t frontend[WORDS] __attribute__((aligned(64)));
static int16_t native_soa[WORDS] __attribute__((aligned(64)));
static int16_t native_control[WORDS] __attribute__((aligned(64)));
static uint8_t expected[BYTES] __attribute__((aligned(64)));
static uint8_t materialized[BYTES + 16] __attribute__((aligned(64)));
static volatile uint64_t sink;

static uint32_t next_random(uint32_t *state)
{
	*state = *state * UINT32_C(1664525) + UINT32_C(1013904223);
	return *state;
}

static __attribute__((noinline)) int verify_local(const uint8_t *a,
	const uint8_t *b, size_t length)
{
	uint8_t accumulator = 0;
	for (size_t i = 0; i < length; i++)
		accumulator |= (uint8_t)(a[i] ^ b[i]);
	return (int)((-(uint64_t)accumulator) >> 63);
}

static void produce_native(int16_t out[WORDS], const int16_t in[WORDS])
{
	gt32_tile4_frontend_wide_raw_asm(frontend, in);
	gt32_tile4_attr_forward_all_bm_soa_asm(out, frontend);
}

static void prepare_n5_input(uint32_t *state)
{
	for (unsigned i = 0; i < WORDS; i++)
		coefficients[i] = (int16_t)((int32_t)(next_random(state) % 3U) - 1);
	produce_native(native_soa, coefficients);
	gt32_q24_encode_soa_lazy10788_asm(expected, native_soa);
}

static int control_verify_native(const int16_t input[WORDS])
{
	memset(materialized + BYTES, 0xa5, sizeof materialized - BYTES);
	gt32_q24_encode_soa_lazy10788_asm(materialized, input);
	return verify_local(expected, materialized, BYTES);
}

static int candidate_verify_native(const int16_t input[WORDS])
{
	return gt32_q24_encode_soa_lazy10788_verify_asm(expected, input);
}

static void control_pack_verify_region(void)
{
	sink += (unsigned)control_verify_native(native_soa);
}

static void candidate_pack_verify_region(void)
{
	sink += (unsigned)candidate_verify_native(native_soa);
}

static void control_n5_pack_verify_region(void)
{
	produce_native(native_control, coefficients);
	sink += (unsigned)control_verify_native(native_control);
}

static void candidate_n5_pack_verify_region(void)
{
	produce_native(native_control, coefficients);
	sink += (unsigned)candidate_verify_native(native_control);
}

static void guard_test(void)
{
	const long page = sysconf(_SC_PAGESIZE);
	uint8_t *mapping = mmap(NULL, (size_t)(2 * page),
		PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
	int16_t zero[WORDS] __attribute__((aligned(64))) = {0};
	if (mapping == MAP_FAILED) {
		perror("mmap");
		exit(1);
	}
	uint8_t *const edge = mapping + page - BYTES;
	memset(edge, 0, BYTES);
	if (mprotect(mapping + page, (size_t)page, PROT_NONE) != 0
		|| mprotect(mapping, (size_t)page, PROT_READ) != 0) {
		perror("mprotect");
		exit(1);
	}
	if (gt32_q24_encode_soa_lazy10788_verify_asm(edge, zero) != 0)
		exit(1);
	if (mprotect(mapping, (size_t)page, PROT_READ | PROT_WRITE) != 0)
		exit(1);
	edge[BYTES - 1U] = UINT8_C(1);
	if (mprotect(mapping, (size_t)page, PROT_READ) != 0)
		exit(1);
	if (gt32_q24_encode_soa_lazy10788_verify_asm(edge, zero) != 1)
		exit(1);
	if (munmap(mapping, (size_t)(2 * page)) != 0)
		exit(1);
}

static void correctness(void)
{
	uint32_t state = UINT32_C(0x24f1c001);
	int16_t saved[WORDS] __attribute__((aligned(64)));
	guard_test();
	for (unsigned trial = 0; trial < 1000; trial++) {
		prepare_n5_input(&state);
		memcpy(saved, native_soa, sizeof saved);
		if (control_verify_native(native_soa) != 0
			|| candidate_verify_native(native_soa) != 0)
			exit(1);
		if (memcmp(saved, native_soa, sizeof saved) != 0)
			exit(1);
		if (memcmp(materialized, expected, BYTES) != 0)
			exit(1);
		for (unsigned i = BYTES; i < sizeof materialized; i++)
			if (materialized[i] != UINT8_C(0xa5))
				exit(1);

		const unsigned byte = trial % BYTES;
		expected[byte] ^= (uint8_t)(UINT8_C(1) << (trial & 7U));
		if (control_verify_native(native_soa) != 1
			|| candidate_verify_native(native_soa) != 1)
			exit(1);
		expected[byte] ^= (uint8_t)(UINT8_C(1) << (trial & 7U));
	}

	/* Every serialized byte participates in the constant-time mismatch mask. */
	memset(native_soa, 0, sizeof native_soa);
	memset(expected, 0, sizeof expected);
	for (unsigned byte = 0; byte < BYTES; byte++) {
		expected[byte] = UINT8_C(1);
		if (candidate_verify_native(native_soa) != 1)
			exit(1);
		expected[byte] = 0;
	}
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

static void print_gate(const char *name, region_fn control,
	region_fn candidate, unsigned iterations)
{
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		double control_tsc;
		double candidate_tsc;
		if ((sample & 1U) == 0U) {
			control_tsc = measure(control, iterations);
			candidate_tsc = measure(candidate, iterations);
		} else {
			candidate_tsc = measure(candidate, iterations);
			control_tsc = measure(control, iterations);
		}
		printf("SAMPLE,%s,%u,%.6f,%.6f,%.6f\n", name, sample,
			control_tsc, candidate_tsc, candidate_tsc - control_tsc);
	}
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
	uint32_t state = UINT32_C(0x24f1beef);
	prepare_n5_input(&state);
	for (unsigned warm = 0; warm < 2; warm++) {
		(void)measure(control_n5_pack_verify_region, 1000);
		(void)measure(candidate_n5_pack_verify_region, 1000);
	}
	printf("META,scope=lazy10788-q24-pack-and-verify,correctness=byte-exact,iterations=%u,samples=%u,materialized-candidate=0,n5=unchanged\n",
		iterations, SAMPLES);
	print_gate("pack_verify", control_pack_verify_region,
		candidate_pack_verify_region, iterations);
	print_gate("n5_pack_verify", control_n5_pack_verify_region,
		candidate_n5_pack_verify_region, iterations);
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}
