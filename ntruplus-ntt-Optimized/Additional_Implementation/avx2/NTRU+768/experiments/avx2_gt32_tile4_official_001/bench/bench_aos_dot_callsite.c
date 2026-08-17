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
#define SAMPLES 20U

typedef void (*bench_fn)(void);

void poly_crepmod3(int16_t *value);

static uint8_t encoded_c[BYTES] __attribute__((aligned(64)));
static uint8_t encoded_sk[2 * BYTES] __attribute__((aligned(64)));

static int16_t control_c[WORDS] __attribute__((aligned(64)));
static int16_t control_f[WORDS] __attribute__((aligned(64)));
static int16_t control_hinv[WORDS] __attribute__((aligned(64)));
static int16_t candidate_c[WORDS] __attribute__((aligned(64)));
static int16_t candidate_f[WORDS] __attribute__((aligned(64)));
static int16_t candidate_hinv[WORDS] __attribute__((aligned(64)));
static int16_t control_product[WORDS] __attribute__((aligned(64)));
static int16_t candidate_product[WORDS] __attribute__((aligned(64)));
static int16_t control_rows[WORDS] __attribute__((aligned(64)));
static int16_t candidate_rows[WORDS] __attribute__((aligned(64)));
static int16_t control_out[WORDS] __attribute__((aligned(64)));
static int16_t candidate_out[WORDS] __attribute__((aligned(64)));
static int16_t forward_coeff_a[WORDS] __attribute__((aligned(64)));
static int16_t forward_coeff_b[WORDS] __attribute__((aligned(64)));
static int16_t forward_a[WORDS] __attribute__((aligned(64)));
static int16_t forward_b[WORDS] __attribute__((aligned(64)));
static int16_t forward_product[WORDS] __attribute__((aligned(64)));
static int16_t forward_rows[WORDS] __attribute__((aligned(64)));
static int16_t forward_out[WORDS] __attribute__((aligned(64)));
static volatile uint64_t sink;

static void encode_components(uint8_t out[BYTES], unsigned multiplier,
	unsigned addend)
{
	for (unsigned pair = 0; pair < 384U; pair++) {
		const uint16_t first = (uint16_t)((multiplier * (2U * pair)
			+ addend) % GT32_TILE4_Q);
		const uint16_t second = (uint16_t)((multiplier * (2U * pair + 1U)
			+ addend) % GT32_TILE4_Q);
		out[3U * pair] = (uint8_t)first;
		out[3U * pair + 1U] = (uint8_t)((first >> 8)
			| (uint16_t)(second << 4));
		out[3U * pair + 2U] = (uint8_t)(second >> 4);
	}
}

static void set_component(uint8_t out[BYTES], unsigned slot, uint16_t value)
{
	const unsigned pair = slot >> 1;
	if ((slot & 1U) == 0U) {
		out[3U * pair] = (uint8_t)value;
		out[3U * pair + 1U] = (uint8_t)((out[3U * pair + 1U] & 0xf0U)
			| (uint8_t)(value >> 8));
	} else {
		out[3U * pair + 1U] = (uint8_t)((out[3U * pair + 1U] & 0x0fU)
			| (uint8_t)(value << 4));
		out[3U * pair + 2U] = (uint8_t)(value >> 4);
	}
}

static int decode_control(void)
{
	return gt32_tile4_frombytes3_bm_soa_semantic_asm(control_c,
		control_f, control_hinv, encoded_c, encoded_sk);
}

static int decode_candidate(void)
{
	return gt32_tile4_frombytes2_aos_1soa_semantic_asm(candidate_c,
		candidate_f, candidate_hinv, encoded_c, encoded_sk);
}

static void finish_control(void)
{
	gt32_tile4_inverse_all_pair_asm(control_rows, control_product);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(control_out,
		control_rows);
	poly_crepmod3(control_out);
}

static void finish_candidate(void)
{
	gt32_tile4_inverse_all_pair_asm(candidate_rows, candidate_product);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(candidate_out,
		candidate_rows);
	poly_crepmod3(candidate_out);
}

__attribute__((noinline))
static void decoder_control(void)
{
	sink += (unsigned)decode_control();
}

__attribute__((noinline))
static void decoder_candidate(void)
{
	sink += (unsigned)decode_candidate();
}

__attribute__((noinline))
static void arithmetic_control(void)
{
	gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm(control_product,
		control_c, control_f);
	finish_control();
}

__attribute__((noinline))
static void arithmetic_candidate(void)
{
	gt32_tile4_basemul_aos_dot_r1u_asm(candidate_product, candidate_c,
		candidate_f);
	finish_candidate();
}

__attribute__((noinline))
static void first_product_control(void)
{
	sink += (unsigned)gt32_tile4_frombytes_bm_soa_semantic_asm(control_c,
		encoded_c);
	sink += (unsigned)gt32_tile4_frombytes_bm_soa_semantic_asm(control_f,
		encoded_sk);
	arithmetic_control();
}

__attribute__((noinline))
static void first_product_candidate(void)
{
	sink += (unsigned)gt32_tile4_frombytes_aos_asm(candidate_c, encoded_c);
	sink += (unsigned)gt32_tile4_frombytes_aos_asm(candidate_f, encoded_sk);
	arithmetic_candidate();
}

__attribute__((noinline))
static void decap_state_control(void)
{
	decoder_control();
	arithmetic_control();
}

__attribute__((noinline))
static void decap_state_candidate(void)
{
	decoder_candidate();
	arithmetic_candidate();
}

static void finish_forward_product(void)
{
	gt32_tile4_inverse_all_pair_asm(forward_rows, forward_product);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(forward_out,
		forward_rows);
	poly_crepmod3(forward_out);
}

__attribute__((noinline))
static void forward_native_control(void)
{
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(forward_a,
		forward_coeff_a);
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(forward_b,
		forward_coeff_b);
	gt32_tile4_basemul_b3_late_asm(forward_product, forward_a, forward_b);
	finish_forward_product();
}

__attribute__((noinline))
static void forward_native_candidate(void)
{
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(forward_a,
		forward_coeff_a);
	gt32_tile4_forward_full_wide_raw_pair_align64_asm(forward_b,
		forward_coeff_b);
	gt32_tile4_basemul_scale_ff_aos_r1u_asm(forward_product, forward_a,
		forward_b);
	finish_forward_product();
}

static void fail(const char *label, unsigned trial)
{
	fprintf(stderr, "%s failed at trial %u\n", label, trial);
	exit(1);
}

static void correctness(void)
{
	uint8_t saved[BYTES];
	int16_t reference_c_aos[WORDS] __attribute__((aligned(64)));
	int16_t reference_f_aos[WORDS] __attribute__((aligned(64)));
	int16_t reference_forward[WORDS] __attribute__((aligned(64)));

	for (unsigned trial = 0; trial < 1000U; trial++) {
		encode_components(encoded_c, 2U * trial + 3U, trial + 17U);
		encode_components(encoded_sk, 4U * trial + 5U, trial + 29U);
		encode_components(encoded_sk + BYTES, 6U * trial + 7U,
			trial + 31U);
		if (decode_control() != 0 || decode_candidate() != 0)
			fail("valid decode", trial);
		if (gt32_tile4_frombytes_aos_asm(reference_c_aos, encoded_c) != 0
			|| gt32_tile4_frombytes_aos_asm(reference_f_aos,
				encoded_sk) != 0
			|| memcmp(reference_c_aos, candidate_c,
				sizeof(reference_c_aos)) != 0
			|| memcmp(reference_f_aos, candidate_f,
				sizeof(reference_f_aos)) != 0)
			fail("mixed decoder AoS deposit", trial);
		arithmetic_control();
		arithmetic_candidate();
		if (memcmp(control_out, candidate_out, sizeof(control_out)) != 0)
			fail("decap first product", trial);
		/* The candidate keeps hinv in exactly the control's private SoA ABI. */
		if (memcmp(control_hinv, candidate_hinv,
			sizeof(control_hinv)) != 0)
			fail("persistent hinv", trial);

		for (unsigned i = 0; i < WORDS; i++) {
			forward_coeff_a[i] = (int16_t)((int)((trial + i) & 7U) - 3);
			forward_coeff_b[i] = (int16_t)((int)((3U * trial + 5U * i)
				& 7U) - 3);
		}
		forward_native_control();
		memcpy(reference_forward, forward_out, sizeof(reference_forward));
		forward_native_candidate();
		if (memcmp(reference_forward, forward_out,
			sizeof(reference_forward)) != 0)
			fail("Forward-native R1-U chain", trial);
	}

	/* The combined mixed decoder must preserve the aggregate rejection bit. */
	for (unsigned input = 0; input < 3U; input++) {
		uint8_t *target = input == 0U ? encoded_c
			: encoded_sk + (input - 1U) * BYTES;
		for (unsigned slot_index = 0; slot_index < 3U; slot_index++) {
			const unsigned slots[] = {0U, 383U, 767U};
			encode_components(encoded_c, 23U, 17U);
			encode_components(encoded_sk, 37U, 29U);
			encode_components(encoded_sk + BYTES, 41U, 31U);
			memcpy(saved, target, sizeof(saved));
			set_component(target, slots[slot_index], GT32_TILE4_Q);
			if (decode_control() != 1 || decode_candidate() != 1)
				fail("malformed rejection", input * 3U + slot_index);
			memcpy(target, saved, sizeof(saved));
		}
	}

	encode_components(encoded_c, 23U, 17U);
	encode_components(encoded_sk, 37U, 29U);
	encode_components(encoded_sk + BYTES, 41U, 31U);
	(void)decode_control();
	(void)decode_candidate();
	for (unsigned i = 0; i < WORDS; i++) {
		forward_coeff_a[i] = (int16_t)((int)((17U * i + 3U) & 7U) - 3);
		forward_coeff_b[i] = (int16_t)((int)((29U * i + 5U) & 7U) - 3);
	}
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

static double measure(bench_fn fn, unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		fn();
	const uint64_t end = stop_tsc();
	sink += (uint16_t)control_out[iterations & 767U];
	sink += (uint16_t)candidate_out[(iterations + 1U) & 767U];
	return (double)(end - begin) / iterations;
}

struct gate {
	const char *name;
	bench_fn baseline;
	bench_fn candidate;
};

static void run_gate(const struct gate *gate, unsigned iterations)
{
	for (unsigned warmup = 0; warmup < 2U; warmup++) {
		(void)measure(gate->baseline, 100U);
		(void)measure(gate->candidate, 100U);
	}
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		double baseline;
		double candidate;
		const unsigned order = sample & 3U;
		if (order == 0U || order == 3U) {
			baseline = measure(gate->baseline, iterations);
			candidate = measure(gate->candidate, iterations);
		} else {
			candidate = measure(gate->candidate, iterations);
			baseline = measure(gate->baseline, iterations);
		}
		printf("SAMPLE,%s,%u,%.6f,%.6f,%.6f\n", gate->name, sample,
			baseline, candidate, candidate - baseline);
	}
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc >= 2
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	const int forward_only = argc >= 3
		&& strcmp(argv[2], "forward-only") == 0;
	cpu_set_t cpuset;
	const struct gate gates[] = {
		{"decoder3_mixed_vs_ss", decoder_control, decoder_candidate},
		{"arithmetic_r1u_vs_ss", arithmetic_control,
			arithmetic_candidate},
		{"first_product_r1u_vs_ss", first_product_control,
			first_product_candidate},
		{"decap_state_r1u_vs_ss", decap_state_control,
			decap_state_candidate},
		{"forward_native_r1u_vs_b3", forward_native_control,
			forward_native_candidate},
	};

	CPU_ZERO(&cpuset);
	CPU_SET(1, &cpuset);
	if (sched_setaffinity(0, sizeof(cpuset), &cpuset) != 0)
		perror("sched_setaffinity");
	correctness();
	printf("META,experiment=GT32-AOS-DOT-REDC16-CALLSITE-001,"
		"correctness=pass,trials=1000,iterations=%u,samples=%u,"
		"ordering=ABBA-BAAB,primary=decap_state_r1u_vs_ss,"
		"secondary=forward_native_r1u_vs_b3,forward_only=%d,sink=%llu\n",
		iterations, SAMPLES, forward_only, (unsigned long long)sink);
	if (forward_only) {
		run_gate(&gates[4], iterations);
	} else {
		for (unsigned i = 0; i < sizeof(gates) / sizeof(gates[0]); i++)
			run_gate(&gates[i], iterations);
	}
	return 0;
}
