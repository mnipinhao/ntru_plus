#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <x86intrin.h>

#include "tile4.h"

#define WORDS GT32_TILE4_POLY_WORDS
#define SAMPLES 20

typedef void (*bench_fn)(int16_t *out);

int poly_frombytes(int16_t *out, const uint8_t *in);
void poly_crepmod3(int16_t *value);

static uint8_t encoded_c[GT32_TILE4_SERIALIZED_BYTES]
	__attribute__((aligned(64)));
static uint8_t encoded_f[GT32_TILE4_SERIALIZED_BYTES]
	__attribute__((aligned(64)));
static uint8_t encoded_hinv[GT32_TILE4_SERIALIZED_BYTES]
	__attribute__((aligned(64)));
static uint8_t encoded_sk[2 * GT32_TILE4_SERIALIZED_BYTES]
	__attribute__((aligned(64)));
static int16_t c_aos[WORDS] __attribute__((aligned(64)));
static int16_t f_aos[WORDS] __attribute__((aligned(64)));
static int16_t c_soa[WORDS] __attribute__((aligned(64)));
static int16_t f_soa[WORDS] __attribute__((aligned(64)));
static int16_t triple_control[3][WORDS] __attribute__((aligned(64)));
static int16_t triple_candidate[3][WORDS] __attribute__((aligned(64)));
static int16_t product[WORDS] __attribute__((aligned(64)));
static int16_t inverse_rows[WORDS] __attribute__((aligned(64)));
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

static void encode_components(uint8_t out[GT32_TILE4_SERIALIZED_BYTES],
	unsigned multiplier, unsigned addend)
{
	for (unsigned pair = 0; pair < 384; pair++) {
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

__attribute__((noinline))
static void decode_official(int16_t *out)
{
	sink += (unsigned)poly_frombytes(out, encoded_f);
}

__attribute__((noinline))
static void decode_aos(int16_t *out)
{
	sink += (unsigned)gt32_tile4_frombytes_aos_asm(out, encoded_f);
}

__attribute__((noinline))
static void decode_soa(int16_t *out)
{
	sink += (unsigned)gt32_tile4_frombytes_bm_soa_semantic_asm(out,
		encoded_f);
}

__attribute__((noinline))
static void decode_three_separate(int16_t *out)
{
	(void)out;
	sink += (unsigned)gt32_tile4_frombytes_bm_soa_semantic_asm(
		triple_control[0], encoded_c);
	sink += (unsigned)gt32_tile4_frombytes_bm_soa_semantic_asm(
		triple_control[1], encoded_f);
	sink += (unsigned)gt32_tile4_frombytes_bm_soa_semantic_asm(
		triple_control[2], encoded_hinv);
}

__attribute__((noinline))
static void decode_three_combined(int16_t *out)
{
	(void)out;
	sink += (unsigned)gt32_tile4_frombytes3_bm_soa_semantic_asm(
		triple_candidate[0], triple_candidate[1], triple_candidate[2],
		encoded_c, encoded_sk);
}

static void finish_private_product(int16_t *out)
{
	gt32_tile4_inverse_all_pair_asm(inverse_rows, product);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(out, inverse_rows);
	poly_crepmod3(out);
}

__attribute__((noinline))
static void island_aa(int16_t *out)
{
	sink += (unsigned)gt32_tile4_frombytes_aos_asm(c_aos, encoded_c);
	sink += (unsigned)gt32_tile4_frombytes_aos_asm(f_aos, encoded_f);
	gt32_tile4_basemul_c3center_late_aos_private_asm(product, c_aos,
		f_aos);
	finish_private_product(out);
}

/* Realistic decap orientation: c remains AoS for the later c-m consumer. */
__attribute__((noinline))
static void island_sa_f(int16_t *out)
{
	sink += (unsigned)gt32_tile4_frombytes_aos_asm(c_aos, encoded_c);
	sink += (unsigned)gt32_tile4_frombytes_bm_soa_semantic_asm(f_soa,
		encoded_f);
	gt32_tile4_basemul_scale_soa_aos_to_aos_private_asm(product, f_soa,
		c_aos);
	finish_private_product(out);
}

/* Orientation control: useful arithmetically, but c would need AoS again. */
__attribute__((noinline))
static void island_sa_c(int16_t *out)
{
	sink += (unsigned)gt32_tile4_frombytes_bm_soa_semantic_asm(c_soa,
		encoded_c);
	sink += (unsigned)gt32_tile4_frombytes_aos_asm(f_aos, encoded_f);
	gt32_tile4_basemul_scale_soa_aos_to_aos_private_asm(product, c_soa,
		f_aos);
	finish_private_product(out);
}

__attribute__((noinline))
static void island_ss(int16_t *out)
{
	sink += (unsigned)gt32_tile4_frombytes_bm_soa_semantic_asm(c_soa,
		encoded_c);
	sink += (unsigned)gt32_tile4_frombytes_bm_soa_semantic_asm(f_soa,
		encoded_f);
	gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm(product, c_soa,
		f_soa);
	finish_private_product(out);
}

/*
 * The honest SS cost in decapsulation also preserves c in AoS for c-m.
 * This intentionally includes a third decode rather than hiding the DAG debt.
 */
__attribute__((noinline))
static void island_ss_preserve_c(int16_t *out)
{
	sink += (unsigned)gt32_tile4_frombytes_aos_asm(c_aos, encoded_c);
	sink += (unsigned)gt32_tile4_frombytes_bm_soa_semantic_asm(c_soa,
		encoded_c);
	sink += (unsigned)gt32_tile4_frombytes_bm_soa_semantic_asm(f_soa,
		encoded_f);
	gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm(product, c_soa,
		f_soa);
	finish_private_product(out);
}

static double measure(bench_fn fn, int16_t *out, unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		fn(out);
	const uint64_t end = stop_tsc();
	sink += (uint16_t)out[iterations % WORDS];
	return (double)(end - begin) / iterations;
}

static int compare_islands(void)
{
	int16_t aa[WORDS] __attribute__((aligned(64)));
	int16_t candidate[WORDS] __attribute__((aligned(64)));
	island_aa(aa);
	island_sa_f(candidate);
	if (memcmp(aa, candidate, sizeof aa) != 0)
		return 0;
	island_sa_c(candidate);
	if (memcmp(aa, candidate, sizeof aa) != 0)
		return 0;
	island_ss(candidate);
	if (memcmp(aa, candidate, sizeof aa) != 0)
		return 0;
	island_ss_preserve_c(candidate);
	return memcmp(aa, candidate, sizeof aa) == 0;
}

static int compare_three_decoder(void)
{
	decode_three_separate(triple_control[0]);
	decode_three_combined(triple_candidate[0]);
	return memcmp(triple_control, triple_candidate,
		sizeof triple_control) == 0;
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	int16_t decode_official_out[WORDS] __attribute__((aligned(64)));
	int16_t decode_aos_out[WORDS] __attribute__((aligned(64)));
	int16_t decode_soa_out[WORDS] __attribute__((aligned(64)));
	int16_t decode_three_out[WORDS] __attribute__((aligned(64)));
	int16_t aa_out[WORDS] __attribute__((aligned(64)));
	int16_t sa_f_out[WORDS] __attribute__((aligned(64)));
	int16_t sa_c_out[WORDS] __attribute__((aligned(64)));
	int16_t ss_out[WORDS] __attribute__((aligned(64)));
	int16_t ss_preserve_out[WORDS] __attribute__((aligned(64)));
	cpu_set_t set;

	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof(set), &set) != 0)
		perror("sched_setaffinity");
	encode_components(encoded_c, 23U, 17U);
	encode_components(encoded_f, 37U, 29U);
	encode_components(encoded_hinv, 41U, 31U);
	/* The combined ABI reads f and hinv from consecutive secret-key slots. */
	memcpy(encoded_sk, encoded_f, GT32_TILE4_SERIALIZED_BYTES);
	memcpy(encoded_sk + GT32_TILE4_SERIALIZED_BYTES, encoded_hinv,
		GT32_TILE4_SERIALIZED_BYTES);
	if (!compare_three_decoder() || !compare_islands()) {
		fprintf(stderr, "correct-semantic AA/SA/SS differential failed\n");
		return 1;
	}
	for (unsigned warm = 0; warm < 2; warm++) {
		(void)measure(decode_official, decode_official_out, 500);
		(void)measure(decode_aos, decode_aos_out, 500);
		(void)measure(decode_soa, decode_soa_out, 500);
		(void)measure(decode_three_separate, decode_three_out, 500);
		(void)measure(decode_three_combined, decode_three_out, 500);
		(void)measure(island_aa, aa_out, 500);
		(void)measure(island_sa_f, sa_f_out, 500);
		(void)measure(island_sa_c, sa_c_out, 500);
		(void)measure(island_ss, ss_out, 500);
		(void)measure(island_ss_preserve_c, ss_preserve_out, 500);
	}
	printf("META,correctness=pass,mapping=official-index-to-gt-brv5,"
		"scope=short-only,iterations=%u,samples=%u,crepmod3=included\n",
		iterations, SAMPLES);
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		double official;
		double aos;
		double soa;
		double decoder3_separate;
		double decoder3_combined;
		double aa;
		double sa_f;
		double sa_c;
		double ss;
		double ss_preserve;
		if ((sample & 1U) == 0U) {
			official = measure(decode_official, decode_official_out,
				iterations);
			aos = measure(decode_aos, decode_aos_out, iterations);
			soa = measure(decode_soa, decode_soa_out, iterations);
			decoder3_separate = measure(decode_three_separate,
				decode_three_out, iterations);
			decoder3_combined = measure(decode_three_combined,
				decode_three_out, iterations);
			aa = measure(island_aa, aa_out, iterations);
			sa_f = measure(island_sa_f, sa_f_out, iterations);
			sa_c = measure(island_sa_c, sa_c_out, iterations);
			ss = measure(island_ss, ss_out, iterations);
			ss_preserve = measure(island_ss_preserve_c, ss_preserve_out,
				iterations);
		} else {
			ss_preserve = measure(island_ss_preserve_c, ss_preserve_out,
				iterations);
			ss = measure(island_ss, ss_out, iterations);
			sa_c = measure(island_sa_c, sa_c_out, iterations);
			sa_f = measure(island_sa_f, sa_f_out, iterations);
			aa = measure(island_aa, aa_out, iterations);
			decoder3_combined = measure(decode_three_combined,
				decode_three_out, iterations);
			decoder3_separate = measure(decode_three_separate,
				decode_three_out, iterations);
			soa = measure(decode_soa, decode_soa_out, iterations);
			aos = measure(decode_aos, decode_aos_out, iterations);
			official = measure(decode_official, decode_official_out,
				iterations);
		}
		printf("SAMPLE,decoder,%u,%.6f,%.6f,%.6f\n", sample,
			official, aos, soa);
		printf("SAMPLE,decoder3,%u,%.6f,%.6f,%.6f\n", sample,
			decoder3_separate, decoder3_combined,
			decoder3_combined - decoder3_separate);
		printf("SAMPLE,island,%u,%.6f,%.6f,%.6f,%.6f,%.6f\n",
			sample, aa, sa_f, sa_c, ss, ss_preserve);
	}
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}
