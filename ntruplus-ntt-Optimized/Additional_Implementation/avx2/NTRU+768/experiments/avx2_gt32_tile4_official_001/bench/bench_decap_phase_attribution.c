#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <x86intrin.h>

#include "api.h"
#include "kat/rng.h"
#include "poly.h"

#include "tile4.h"
#include "tile4_kem_candidate.h"

#define WORDS GT32_TILE4_POLY_WORDS
#define SAMPLES 20

typedef void (*phase_fn)(void);

static uint8_t pk[CRYPTO_PUBLICKEYBYTES] __attribute__((aligned(64)));
static uint8_t sk[CRYPTO_SECRETKEYBYTES] __attribute__((aligned(64)));
static uint8_t ct[CRYPTO_CIPHERTEXTBYTES] __attribute__((aligned(64)));
static uint8_t expected_ss[CRYPTO_BYTES] __attribute__((aligned(64)));

static poly off_c;
static poly off_f;
static poly off_hinv;
static poly off_m;
static poly off_mhat;
static poly off_cminus;
static poly off_rhat;
static poly off_check_input;
static poly off_work0;
static poly off_work1;

static int16_t gt_c[WORDS] __attribute__((aligned(64)));
static int16_t gt_f[WORDS] __attribute__((aligned(64)));
static int16_t gt_hinv[WORDS] __attribute__((aligned(64)));
static int16_t gt_m[WORDS] __attribute__((aligned(64)));
static int16_t gt_mhat[WORDS] __attribute__((aligned(64)));
static int16_t gt_cminus[WORDS] __attribute__((aligned(64)));
static int16_t gt_rhat[WORDS] __attribute__((aligned(64)));
static int16_t gt_check_input[WORDS] __attribute__((aligned(64)));
static int16_t gt_work0[WORDS] __attribute__((aligned(64)));
static int16_t gt_work1[WORDS] __attribute__((aligned(64)));
static int16_t gt_rows[WORDS] __attribute__((aligned(64)));
static int16_t gt_official_words[WORDS] __attribute__((aligned(64)));
static uint8_t off_bytes[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
static uint8_t gt_bytes[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
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

static void reset_rng(void)
{
	uint8_t entropy[48];
	for (size_t i = 0; i < sizeof entropy; i++)
		entropy[i] = (uint8_t)(41U + 13U * i);
	randombytes_init(entropy, NULL, 256);
}

__attribute__((noinline))
static void phase_off_decode_all(void)
{
	sink += (unsigned)poly_frombytes(&off_work0, ct);
	sink += (unsigned)poly_frombytes(&off_work1, sk);
	sink += (unsigned)poly_frombytes(&off_work0,
		sk + NTRUPLUS_POLYBYTES);
}

__attribute__((noinline))
static void phase_gt_decode_all(void)
{
	sink += (unsigned)gt32_tile4_frombytes3_bm_soa_semantic_asm(gt_c,
		gt_f, gt_hinv, ct, sk);
}

__attribute__((noinline))
static void phase_off_m1(void)
{
	poly_basemul_scale(&off_work0, &off_c, &off_f);
	poly_invntt_scale(&off_work0);
	poly_crepmod3(&off_work0);
}

__attribute__((noinline))
static void phase_gt_m1(void)
{
	gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm(gt_work0,
		gt_c, gt_f);
	gt32_tile4_inverse_all_pair_asm(gt_rows, gt_work0);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(gt_work1, gt_rows);
	poly_crepmod3((poly *)(void *)gt_work1);
}

__attribute__((noinline))
static void phase_off_forward_m(void)
{
	off_work0 = off_m;
	poly_ntt(&off_work0);
}

__attribute__((noinline))
static void phase_gt_forward_m(void)
{
	gt32_tile4_frontend_wide_raw_asm(gt_work0, gt_m);
	gt32_tile4_attr_forward_all_bm_soa_asm(gt_work1, gt_work0);
}

__attribute__((noinline))
static void phase_off_sub(void)
{
	poly_sub(&off_work0, &off_c, &off_mhat);
}

__attribute__((noinline))
static void phase_gt_sub(void)
{
	poly_sub((poly *)(void *)gt_work0, (const poly *)(const void *)gt_c,
		(const poly *)(const void *)gt_mhat);
}

__attribute__((noinline))
static void phase_off_general_bm(void)
{
	poly_basemul(&off_work0, &off_cminus, &off_hinv);
}

__attribute__((noinline))
static void phase_gt_general_bm(void)
{
	gt32_tile4_basemul_general_soa_soa_to_soa_asm(gt_work0, gt_cminus,
		gt_hinv);
}

__attribute__((noinline))
static void phase_off_tobytes(void)
{
	poly_tobytes(off_bytes, &off_rhat);
	sink += off_bytes[0];
}

__attribute__((noinline))
static void phase_gt_tobytes(void)
{
	gt32_tile4_soa_to_official_words_grouped_asm(gt_work0, gt_rhat);
	poly_tobytes(gt_bytes, (const poly *)(const void *)gt_work0);
	sink += gt_bytes[0];
}

__attribute__((noinline))
static void phase_encodeq_materialized(void)
{
	gt32_tile4_soa_to_official_words_grouped_asm(gt_work0, gt_rhat);
	poly_tobytes(off_bytes, (const poly *)(const void *)gt_work0);
	sink += off_bytes[0];
}

__attribute__((noinline))
static void phase_encodeq_direct(void)
{
	gt32_tile4_soa_tobytes_direct_asm(gt_bytes, gt_rhat);
	sink += gt_bytes[0];
}

__attribute__((noinline))
static void phase_bridge_old(void)
{
	gt32_tile4_soa_to_official_words_asm(gt_work0, gt_rhat);
	sink += (uint16_t)gt_work0[0];
}

__attribute__((noinline))
static void phase_bridge_grouped(void)
{
	gt32_tile4_soa_to_official_words_grouped_asm(gt_work1, gt_rhat);
	sink += (uint16_t)gt_work1[0];
}

__attribute__((noinline))
static void phase_off_check_encode(void)
{
	off_work0 = off_check_input;
	poly_ntt(&off_work0);
	poly_tobytes(off_bytes, &off_work0);
	sink += off_bytes[0];
}

__attribute__((noinline))
static void phase_gt_check_encode(void)
{
	gt32_tile4_frontend_wide_raw_asm(gt_work0, gt_check_input);
	gt32_tile4_attr_forward_all_bm_soa_asm(gt_work1, gt_work0);
	gt32_tile4_soa_to_official_words_grouped_asm(gt_official_words,
		gt_work1);
	poly_tobytes(gt_bytes, (const poly *)(const void *)gt_official_words);
	sink += gt_bytes[0];
}

static double measure(phase_fn fn, unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		fn();
	const uint64_t end = stop_tsc();
	return (double)(end - begin) / iterations;
}

typedef struct {
	const char *name;
	phase_fn official;
	phase_fn gt32;
} phase_pair;

static int prepare_states(void)
{
	reset_rng();
	if (crypto_kem_keypair(pk, sk) != 0
		|| crypto_kem_enc(ct, expected_ss, pk) != 0
		|| poly_frombytes(&off_c, ct) != 0
		|| poly_frombytes(&off_f, sk) != 0
		|| poly_frombytes(&off_hinv, sk + NTRUPLUS_POLYBYTES) != 0
		|| gt32_tile4_frombytes_bm_soa_semantic_asm(gt_c, ct) != 0
		|| gt32_tile4_frombytes_bm_soa_semantic_asm(gt_f, sk) != 0
		|| gt32_tile4_frombytes_bm_soa_semantic_asm(gt_hinv,
			sk + NTRUPLUS_POLYBYTES) != 0)
		return 0;

	poly_basemul_scale(&off_m, &off_c, &off_f);
	poly_invntt_scale(&off_m);
	poly_crepmod3(&off_m);
	gt32_tile4_basemul_scale_soa_soa_to_aos_private_asm(gt_work0,
		gt_c, gt_f);
	gt32_tile4_inverse_all_pair_asm(gt_rows, gt_work0);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(gt_m, gt_rows);
	poly_crepmod3((poly *)(void *)gt_m);
	if (memcmp(off_m.coeffs, gt_m, sizeof gt_m) != 0)
		return 0;

	off_mhat = off_m;
	poly_ntt(&off_mhat);
	gt32_tile4_frontend_wide_raw_asm(gt_work0, gt_m);
	gt32_tile4_attr_forward_all_bm_soa_asm(gt_mhat, gt_work0);
	poly_sub(&off_cminus, &off_c, &off_mhat);
	poly_sub((poly *)(void *)gt_cminus, (const poly *)(const void *)gt_c,
		(const poly *)(const void *)gt_mhat);
	poly_basemul(&off_rhat, &off_cminus, &off_hinv);
	gt32_tile4_basemul_general_soa_soa_to_soa_asm(gt_rhat, gt_cminus,
		gt_hinv);
	poly_tobytes(off_bytes, &off_rhat);
	gt32_tile4_soa_to_official_words_grouped_asm(gt_work0, gt_rhat);
	poly_tobytes(gt_bytes, (const poly *)(const void *)gt_work0);
	if (memcmp(off_bytes, gt_bytes, sizeof off_bytes) != 0)
		return 0;

	for (size_t i = 0; i < NTRUPLUS_N; i++) {
		const int16_t value = (int16_t)((int)(i % 3U) - 1);
		off_check_input.coeffs[i] = value;
		gt_check_input[i] = value;
	}
	off_work0 = off_check_input;
	poly_ntt(&off_work0);
	poly_tobytes(off_bytes, &off_work0);
	gt32_tile4_frontend_wide_raw_asm(gt_work0, gt_check_input);
	gt32_tile4_attr_forward_all_bm_soa_asm(gt_work1, gt_work0);
	gt32_tile4_soa_to_official_words_grouped_asm(gt_official_words,
		gt_work1);
	poly_tobytes(gt_bytes, (const poly *)(const void *)gt_official_words);
	if (memcmp(off_bytes, gt_bytes, sizeof off_bytes) != 0)
		return 0;
	gt32_tile4_soa_to_official_words_asm(gt_work0, gt_rhat);
	gt32_tile4_soa_to_official_words_grouped_asm(gt_work1, gt_rhat);
	return memcmp(gt_work0, gt_work1, sizeof gt_work0) == 0;
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	const phase_pair phases[] = {
		{"decode_all", phase_off_decode_all, phase_gt_decode_all},
		{"first_bm_inverse_crep", phase_off_m1, phase_gt_m1},
		{"forward_m", phase_off_forward_m, phase_gt_forward_m},
		{"sub_c_mhat", phase_off_sub, phase_gt_sub},
		{"general_basemul", phase_off_general_bm, phase_gt_general_bm},
		{"tobytes_recovered_r", phase_off_tobytes, phase_gt_tobytes},
		{"check_forward_tobytes", phase_off_check_encode,
			phase_gt_check_encode},
		{"control_encodeq_bridge_grouped", phase_bridge_old,
			phase_bridge_grouped},
		{"control_encodeq_direct", phase_encodeq_materialized,
			phase_encodeq_direct},
	};
	cpu_set_t set;
	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof(set), &set) != 0)
		perror("sched_setaffinity");
	if (!prepare_states()) {
		fprintf(stderr, "decap attribution state differential failed\n");
		return 1;
	}
	for (size_t phase = 0; phase < sizeof phases / sizeof phases[0]; phase++) {
		for (unsigned warm = 0; warm < 2; warm++) {
			(void)measure(phases[phase].official, 200);
			(void)measure(phases[phase].gt32, 200);
		}
	}
	printf("META,correctness=pass,scope=soa-domain-direct-encode-phase-costs,"
		"iterations=%u,samples=%u\n", iterations, SAMPLES);
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		for (size_t phase = 0; phase < sizeof phases / sizeof phases[0];
			phase++) {
			double official;
			double gt32;
			if ((sample & 1U) == 0U) {
				official = measure(phases[phase].official, iterations);
				gt32 = measure(phases[phase].gt32, iterations);
			} else {
				gt32 = measure(phases[phase].gt32, iterations);
				official = measure(phases[phase].official, iterations);
			}
			printf("SAMPLE,%s,%u,%.6f,%.6f,%.6f\n",
				phases[phase].name, sample, official, gt32,
				gt32 - official);
		}
	}
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}
