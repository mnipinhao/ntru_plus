#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <x86intrin.h>

#include "tile4.h"

#define WORDS GT32_TILE4_POLY_WORDS
#define BYTES GT32_TILE4_SERIALIZED_BYTES
#define SAMPLES 20
#define Q GT32_TILE4_Q
#define GUARD_WORDS 4

typedef void (*region_fn)(void);

typedef struct __attribute__((aligned(64))) {
	uint64_t before[GUARD_WORDS];
	int16_t words[WORDS];
	uint64_t after[GUARD_WORDS];
} guarded_poly;

typedef struct {
	guarded_poly c;
	guarded_poly f;
	guarded_poly hinv;
	guarded_poly product;
	guarded_poly rows;
	guarded_poly message;
} prefix_scratch;

void poly_crepmod3(int16_t *value);

static uint8_t encoded_c[BYTES] __attribute__((aligned(64)));
static uint8_t encoded_sk[2 * BYTES] __attribute__((aligned(64)));
static prefix_scratch control_scratch __attribute__((aligned(64)));
static prefix_scratch candidate_scratch __attribute__((aligned(64)));
static volatile uint64_t sink;

static uint64_t start_tsc(void)
{
	_mm_lfence();
	return __rdtsc();
}

static uint64_t stop_tsc(void)
{
	unsigned aux;
	const uint64_t result = __rdtscp(&aux);
	_mm_lfence();
	return result;
}

static void encode_components(uint8_t out[BYTES], unsigned multiplier,
	unsigned addend)
{
	for (unsigned pair = 0; pair < WORDS / 2U; pair++) {
		const uint16_t first = (uint16_t)((multiplier * (2U * pair)
			+ addend) % Q);
		const uint16_t second = (uint16_t)((multiplier * (2U * pair + 1U)
			+ addend) % Q);
		out[3U * pair] = (uint8_t)first;
		out[3U * pair + 1U] = (uint8_t)((first >> 8)
			| (uint16_t)(second << 4));
		out[3U * pair + 2U] = (uint8_t)(second >> 4);
	}
}

static void malformed_slot(uint8_t bytes[BYTES], unsigned slot)
{
	const unsigned pair = slot / 2U;
	const unsigned offset = 3U * pair;
	if ((slot & 1U) == 0U) {
		bytes[offset] = (uint8_t)Q;
		bytes[offset + 1U] = (uint8_t)((bytes[offset + 1U] & 0xf0U)
			| ((unsigned)Q >> 8));
	} else {
		bytes[offset + 1U] = (uint8_t)((bytes[offset + 1U] & 0x0fU)
			| ((unsigned)Q << 4));
		bytes[offset + 2U] = (uint8_t)((unsigned)Q >> 4);
	}
}

static void initialize_guards(prefix_scratch *scratch, uint64_t tag)
{
	guarded_poly *const objects[] = {
		&scratch->c, &scratch->f, &scratch->hinv, &scratch->product,
		&scratch->rows, &scratch->message,
	};
	for (size_t object = 0; object < sizeof objects / sizeof objects[0];
		object++) {
		for (unsigned i = 0; i < GUARD_WORDS; i++) {
			objects[object]->before[i] = tag + 17U * object + i;
			objects[object]->after[i] = tag + 31U * object + i;
		}
	}
}

static int guards_valid(const prefix_scratch *scratch, uint64_t tag)
{
	const guarded_poly *const objects[] = {
		&scratch->c, &scratch->f, &scratch->hinv, &scratch->product,
		&scratch->rows, &scratch->message,
	};
	for (size_t object = 0; object < sizeof objects / sizeof objects[0];
		object++)
		for (unsigned i = 0; i < GUARD_WORDS; i++)
			if (objects[object]->before[i] != tag + 17U * object + i
				|| objects[object]->after[i] != tag + 31U * object + i)
				return 0;
	return 1;
}

static void first_product(prefix_scratch *scratch)
{
	gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm(
		scratch->product.words, scratch->c.words, scratch->f.words);
	gt32_tile4_inverse_all_pair_asm(scratch->rows.words,
		scratch->product.words);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(
		scratch->message.words, scratch->rows.words);
	poly_crepmod3(scratch->message.words);
}

static int decode2_control(prefix_scratch *scratch)
{
	int failure = gt32_tile4_frombytes_bm_soa_semantic_asm(
		scratch->c.words, encoded_c);
	failure |= gt32_tile4_frombytes_bm_soa_semantic_asm(
		scratch->f.words, encoded_sk);
	return failure;
}

static int decode2_candidate(prefix_scratch *scratch)
{
	int failure = gt32_q24_decode_soa_asm(scratch->c.words, encoded_c);
	failure |= gt32_q24_decode_soa_asm(scratch->f.words, encoded_sk);
	return failure;
}

static int decode3_control(prefix_scratch *scratch)
{
	return gt32_tile4_frombytes3_bm_soa_semantic_asm(scratch->c.words,
		scratch->f.words, scratch->hinv.words, encoded_c, encoded_sk);
}

static int decode3_candidate(prefix_scratch *scratch)
{
	return gt32_q24_decode3_soa_asm(scratch->c.words, scratch->f.words,
		scratch->hinv.words, encoded_c, encoded_sk);
}

__attribute__((noinline))
static void region_decode2_control(void)
{
	sink += (unsigned)decode2_control(&control_scratch);
	sink += (uint16_t)control_scratch.f.words[0];
}

__attribute__((noinline))
static void region_decode2_candidate(void)
{
	sink += (unsigned)decode2_candidate(&candidate_scratch);
	sink += (uint16_t)candidate_scratch.f.words[0];
}

__attribute__((noinline))
static void region_decode3_control(void)
{
	sink += (unsigned)decode3_control(&control_scratch);
	sink += (uint16_t)control_scratch.hinv.words[0];
}

__attribute__((noinline))
static void region_decode3_candidate(void)
{
	sink += (unsigned)decode3_candidate(&candidate_scratch);
	sink += (uint16_t)candidate_scratch.hinv.words[0];
}

__attribute__((noinline))
static void region_prefix2_control(void)
{
	sink += (unsigned)decode2_control(&control_scratch);
	first_product(&control_scratch);
	sink += (uint16_t)control_scratch.message.words[0];
}

__attribute__((noinline))
static void region_prefix2_candidate(void)
{
	sink += (unsigned)decode2_candidate(&candidate_scratch);
	first_product(&candidate_scratch);
	sink += (uint16_t)candidate_scratch.message.words[0];
}

__attribute__((noinline))
static void region_prefix3_control(void)
{
	sink += (unsigned)decode3_control(&control_scratch);
	first_product(&control_scratch);
	sink += (uint16_t)control_scratch.message.words[0];
}

__attribute__((noinline))
static void region_prefix3_candidate(void)
{
	sink += (unsigned)decode3_candidate(&candidate_scratch);
	first_product(&candidate_scratch);
	sink += (uint16_t)candidate_scratch.message.words[0];
}

static double measure(region_fn fn, unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		fn();
	const uint64_t end = stop_tsc();
	return (double)(end - begin) / iterations;
}

static void require_equal(const char *label, const void *left,
	const void *right, size_t size)
{
	if (memcmp(left, right, size) != 0) {
		fprintf(stderr, "%s mismatch\n", label);
		exit(1);
	}
}

static void compare_prefix_case(unsigned case_number)
{
	const int control_failure = decode3_control(&control_scratch);
	const int candidate_failure = decode3_candidate(&candidate_scratch);
	if (control_failure != candidate_failure) {
		fprintf(stderr, "failure aggregation mismatch case=%u\n", case_number);
		exit(1);
	}
	require_equal("c private SoA", candidate_scratch.c.words,
		control_scratch.c.words, sizeof control_scratch.c.words);
	require_equal("f private SoA", candidate_scratch.f.words,
		control_scratch.f.words, sizeof control_scratch.f.words);
	require_equal("hinv private SoA", candidate_scratch.hinv.words,
		control_scratch.hinv.words, sizeof control_scratch.hinv.words);
	first_product(&control_scratch);
	first_product(&candidate_scratch);
	require_equal("first-product message", candidate_scratch.message.words,
		control_scratch.message.words, sizeof control_scratch.message.words);
	if (!guards_valid(&control_scratch, UINT64_C(0x1111000000000000))
		|| !guards_valid(&candidate_scratch,
			UINT64_C(0x2222000000000000))) {
		fprintf(stderr, "scratch canary failure case=%u\n", case_number);
		exit(1);
	}
}

static unsigned correctness(void)
{
	uint8_t saved_c[BYTES] __attribute__((aligned(64)));
	uint8_t saved_sk[2 * BYTES] __attribute__((aligned(64)));
	unsigned cases = 0;

	initialize_guards(&control_scratch, UINT64_C(0x1111000000000000));
	initialize_guards(&candidate_scratch, UINT64_C(0x2222000000000000));
	compare_prefix_case(cases);
	memcpy(saved_c, encoded_c, sizeof saved_c);
	memcpy(saved_sk, encoded_sk, sizeof saved_sk);

	for (unsigned source = 0; source < 3; source++) {
		for (unsigned slot = 0; slot < WORDS; slot++) {
			memcpy(encoded_c, saved_c, sizeof saved_c);
			memcpy(encoded_sk, saved_sk, sizeof saved_sk);
			uint8_t *const target = source == 0 ? encoded_c
				: encoded_sk + (source - 1U) * BYTES;
			malformed_slot(target, slot);
			compare_prefix_case(++cases);
		}
	}

	for (unsigned slot_case = 0; slot_case < 3; slot_case++) {
		const unsigned slots[] = {0, 383, 767};
		memcpy(encoded_c, saved_c, sizeof saved_c);
		memcpy(encoded_sk, saved_sk, sizeof saved_sk);
		malformed_slot(encoded_c, slots[slot_case]);
		malformed_slot(encoded_sk, slots[(slot_case + 1U) % 3U]);
		compare_prefix_case(++cases);

		memcpy(encoded_c, saved_c, sizeof saved_c);
		memcpy(encoded_sk, saved_sk, sizeof saved_sk);
		malformed_slot(encoded_c, slots[slot_case]);
		malformed_slot(encoded_sk, slots[(slot_case + 1U) % 3U]);
		malformed_slot(encoded_sk + BYTES, slots[(slot_case + 2U) % 3U]);
		compare_prefix_case(++cases);
	}
	memcpy(encoded_c, saved_c, sizeof saved_c);
	memcpy(encoded_sk, saved_sk, sizeof saved_sk);
	return cases;
}

static void sample_region(const char *name, region_fn control,
	region_fn candidate, unsigned iterations)
{
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		double old_cycles;
		double q24_cycles;
		if ((sample & 1U) == 0U) {
			old_cycles = measure(control, iterations);
			q24_cycles = measure(candidate, iterations);
		} else {
			q24_cycles = measure(candidate, iterations);
			old_cycles = measure(control, iterations);
		}
		printf("SAMPLE,%s,%u,%.6f,%.6f,%.6f\n", name, sample,
			old_cycles, q24_cycles, q24_cycles - old_cycles);
	}
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	cpu_set_t set;
	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof(set), &set) != 0)
		perror("sched_setaffinity");

	encode_components(encoded_c, 23U, 17U);
	encode_components(encoded_sk, 37U, 29U);
	encode_components(encoded_sk + BYTES, 41U, 31U);
	const unsigned malformed_cases = correctness();
	for (unsigned warm = 0; warm < 2; warm++) {
		(void)measure(region_decode2_control, 500);
		(void)measure(region_decode2_candidate, 500);
		(void)measure(region_decode3_control, 500);
		(void)measure(region_decode3_candidate, 500);
		(void)measure(region_prefix2_control, 500);
		(void)measure(region_prefix2_candidate, 500);
		(void)measure(region_prefix3_control, 500);
		(void)measure(region_prefix3_candidate, 500);
	}
	printf("META,correctness=word-exact-prefix-pass,malformed_cases=%u,"
		"iterations=%u,samples=%u,order=AB-BA,crepmod3=included\n",
		malformed_cases, iterations, SAMPLES);
	sample_region("R0_decode2", region_decode2_control,
		region_decode2_candidate, iterations);
	sample_region("R0_decode3", region_decode3_control,
		region_decode3_candidate, iterations);
	sample_region("R1_prefix2", region_prefix2_control,
		region_prefix2_candidate, iterations);
	sample_region("R2_prefix3", region_prefix3_control,
		region_prefix3_candidate, iterations);
	if (!guards_valid(&control_scratch, UINT64_C(0x1111000000000000))
		|| !guards_valid(&candidate_scratch,
			UINT64_C(0x2222000000000000))) {
		fprintf(stderr, "post-benchmark scratch canary failure\n");
		return 1;
	}
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}
