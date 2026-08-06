#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include <x86intrin.h>

#include "tile4.h"

#define SAMPLES 20

typedef void (*bench_fn)(int16_t *out);

int poly_frombytes(int16_t *r, const uint8_t *a);

static uint8_t encoded_f[GT32_TILE4_SERIALIZED_BYTES] __attribute__((aligned(64)));
static uint8_t encoded_c[GT32_TILE4_SERIALIZED_BYTES] __attribute__((aligned(64)));
static int16_t f_aos[GT32_TILE4_POLY_WORDS] __attribute__((aligned(64)));
static int16_t f_soa[GT32_TILE4_POLY_WORDS] __attribute__((aligned(64)));
static int16_t c_aos[GT32_TILE4_POLY_WORDS] __attribute__((aligned(64)));
static int16_t product[GT32_TILE4_POLY_WORDS] __attribute__((aligned(64)));
static int16_t rows[GT32_TILE4_POLY_WORDS] __attribute__((aligned(64)));
static volatile uint64_t sink;

static void encode_components(uint8_t out[GT32_TILE4_SERIALIZED_BYTES],
	unsigned multiplier, unsigned addend)
{
	for (unsigned pair = 0; pair < 384; pair++) {
		const uint16_t first = (uint16_t)((multiplier * (2U * pair) + addend)
			% GT32_TILE4_Q);
		const uint16_t second = (uint16_t)((multiplier * (2U * pair + 1U)
			+ addend) % GT32_TILE4_Q);
		out[3U * pair] = (uint8_t)first;
		out[3U * pair + 1U] = (uint8_t)((first >> 8)
			| (uint16_t)(second << 4));
		out[3U * pair + 2U] = (uint8_t)(second >> 4);
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

__attribute__((noinline))
static void official_decode(int16_t *out)
{
	sink += (unsigned)poly_frombytes(out, encoded_f);
}

__attribute__((noinline))
static void baseline_decode(int16_t *out)
{
	sink += (unsigned)gt32_tile4_frombytes_aos_ref(out, encoded_f);
}

__attribute__((noinline))
static void mixed_decode(int16_t *out)
{
	sink += (unsigned)gt32_tile4_frombytes_bm_soa_ref(out, encoded_f);
}

__attribute__((noinline))
static void bridge_aos_decode(int16_t *out)
{
	sink += (unsigned)gt32_tile4_frombytes_aos_official_bridge(out, encoded_f);
}

__attribute__((noinline))
static void bridge_soa_decode(int16_t *out)
{
	sink += (unsigned)gt32_tile4_frombytes_bm_soa_official_bridge(out, encoded_f);
}

__attribute__((noinline))
static void baseline_bm(int16_t *out)
{
	gt32_tile4_basemul_c3center_late_aos_private_asm(out, f_aos, c_aos);
}

__attribute__((noinline))
static void mixed_bm(int16_t *out)
{
	gt32_tile4_basemul_scale_soa_aos_to_aos_private_asm(out, f_soa, c_aos);
}

__attribute__((noinline))
static void baseline_pipeline(int16_t *out)
{
	sink += (unsigned)gt32_tile4_frombytes_aos_official_bridge(f_aos, encoded_f);
	baseline_bm(product);
	gt32_tile4_inverse_all_pair_asm(rows, product);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out, rows);
}

__attribute__((noinline))
static void mixed_pipeline(int16_t *out)
{
	sink += (unsigned)gt32_tile4_frombytes_bm_soa_official_bridge(f_soa,
		encoded_f);
	mixed_bm(product);
	gt32_tile4_inverse_all_pair_asm(rows, product);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out, rows);
}

static double measure(bench_fn fn, int16_t *out, unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		fn(out);
	const uint64_t end = stop_tsc();
	sink += (uint16_t)out[iterations % GT32_TILE4_POLY_WORDS];
	return (double)(end - begin) / iterations;
}

static int16_t centered(int16_t value)
{
	int result = value % GT32_TILE4_Q;
	if (result < 0)
		result += GT32_TILE4_Q;
	if (result > GT32_TILE4_Q / 2)
		result -= GT32_TILE4_Q;
	return (int16_t)result;
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	const unsigned reverse = argc > 2
		? (unsigned)strtoul(argv[2], NULL, 10) & 1U : 0U;
	int16_t out_a[GT32_TILE4_POLY_WORDS] __attribute__((aligned(64)));
	int16_t out_b[GT32_TILE4_POLY_WORDS] __attribute__((aligned(64)));
	cpu_set_t set;
	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof(set), &set) != 0)
		perror("sched_setaffinity");
	encode_components(encoded_f, 17U, 3U);
	encode_components(encoded_c, 29U, 11U);
	if (gt32_tile4_frombytes_aos_ref(f_aos, encoded_f) != 0
		|| gt32_tile4_frombytes_bm_soa_ref(f_soa, encoded_f) != 0
		|| gt32_tile4_frombytes_aos_ref(c_aos, encoded_c) != 0)
		return 1;
	baseline_pipeline(out_a);
	mixed_pipeline(out_b);
	for (unsigned i = 0; i < GT32_TILE4_POLY_WORDS; i++) {
		if (centered(out_a[i]) != centered(out_b[i])) {
			fprintf(stderr, "mixed pipeline mismatch at %u\n", i);
			return 1;
		}
	}
	struct gate { const char *name; bench_fn baseline; bench_fn mixed; };
	const struct gate gates[] = {
		{"official_vs_aos_bridge", official_decode, bridge_aos_decode},
		{"reference_frombytes", baseline_decode, mixed_decode},
		{"bridge_frombytes", bridge_aos_decode, bridge_soa_decode},
		{"basemul", baseline_bm, mixed_bm},
		{"frombytes_bm_i1_t9", baseline_pipeline, mixed_pipeline},
	};
	printf("META,iterations=%u,pattern=%s,correctness=pass\n", iterations,
		reverse ? "BAAB" : "ABBA");
	for (unsigned gate = 0; gate < sizeof(gates) / sizeof(gates[0]); gate++) {
		for (unsigned warm = 0; warm < 2; warm++) {
			(void)measure(gates[gate].baseline, out_a, 1000U);
			(void)measure(gates[gate].mixed, out_b, 1000U);
		}
		for (unsigned sample = 0; sample < SAMPLES; sample++) {
			double baseline;
			double mixed;
			if (((sample ^ reverse) & 1U) == 0U) {
				baseline = measure(gates[gate].baseline, out_a, iterations);
				mixed = measure(gates[gate].mixed, out_b, iterations);
			} else {
				mixed = measure(gates[gate].mixed, out_b, iterations);
				baseline = measure(gates[gate].baseline, out_a, iterations);
			}
			printf("SAMPLE,%s,%u,%.6f,%.6f,%.9f\n", gates[gate].name,
				sample, baseline, mixed, mixed / baseline);
		}
	}
	return sink == UINT64_MAX ? 1 : 0;
}
