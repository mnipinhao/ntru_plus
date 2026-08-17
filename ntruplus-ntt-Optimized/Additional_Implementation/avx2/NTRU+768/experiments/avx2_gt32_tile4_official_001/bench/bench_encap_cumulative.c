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
#include "symmetric.h"
#include "util.h"

#include "tile4.h"
#include "tile4_kem_encap_candidate.h"

#define WORDS GT32_TILE4_POLY_WORDS
#define SAMPLES 20

typedef struct {
	/* Coefficient checkpoints need 1536 bytes; wire checkpoints use 1152. */
	uint8_t primary[sizeof(int16_t) * WORDS];
	uint8_t secondary[NTRUPLUS_POLYBYTES];
	uint8_t ss[NTRUPLUS_SSBYTES];
} snapshot_t;

typedef int (*prefix_fn)(unsigned, snapshot_t *);

static uint8_t pk[CRYPTO_PUBLICKEYBYTES] __attribute__((aligned(64)));
static uint8_t sk[CRYPTO_SECRETKEYBYTES] __attribute__((aligned(64)));
static uint8_t coins[NTRUPLUS_N / 8] __attribute__((aligned(64)));
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

static void forward_gt(int16_t *out, int16_t *work, const int16_t *in)
{
	gt32_tile4_frontend_wide_raw_asm(work, in);
	gt32_tile4_attr_forward_all_bm_soa_asm(out, work);
}

static void snapshot_coeff(snapshot_t *snapshot, const int16_t *coeffs)
{
	memcpy(snapshot->primary, coeffs, sizeof(int16_t) * WORDS);
}

__attribute__((noinline))
static int official_prefix(unsigned stop, snapshot_t *snapshot)
{
	uint8_t msg[HASH_H_INBYTES];
	uint8_t buf[HASH_H_OUTBYTES];
	uint8_t rhat[NTRUPLUS_POLYBYTES];
	poly c, h, r, m;

	if (poly_frombytes(&h, pk) != 0)
		return 1;
	memcpy(msg, coins, NTRUPLUS_N / 8);
	hash_f(msg + NTRUPLUS_N / 8, pk);
	hash_h(buf, msg);
	poly_cbd1(&r, buf + NTRUPLUS_SYMBYTES);
	if (stop == 1) {
		if (snapshot != NULL)
			snapshot_coeff(snapshot, r.coeffs);
		sink += (uint16_t)r.coeffs[0];
		return 0;
	}

	poly_ntt(&r);
	if (stop == 2) {
		if (snapshot != NULL)
			poly_tobytes(snapshot->primary, &r);
		sink += (uint16_t)r.coeffs[0];
		return 0;
	}

	poly_tobytes(rhat, &r);
	hash_g(rhat, rhat);
	poly_sotp_encode(&m, msg, rhat);
	if (stop == 3) {
		if (snapshot != NULL)
			snapshot_coeff(snapshot, m.coeffs);
		sink += (uint16_t)m.coeffs[0];
		return 0;
	}

	poly_ntt(&m);
	if (stop == 4) {
		if (snapshot != NULL)
			poly_tobytes(snapshot->primary, &m);
		sink += (uint16_t)m.coeffs[0];
		return 0;
	}

	poly_basemul(&c, &h, &r);
	if (stop == 5) {
		if (snapshot != NULL)
			poly_tobytes(snapshot->primary, &c);
		sink += (uint16_t)c.coeffs[0];
		return 0;
	}

	poly_add(&c, &c, &m);
	if (stop == 6) {
		if (snapshot != NULL)
			poly_tobytes(snapshot->primary, &c);
		sink += (uint16_t)c.coeffs[0];
		return 0;
	}

	poly_tobytes(rhat, &c);
	if (snapshot != NULL) {
		memcpy(snapshot->primary, rhat, sizeof rhat);
		memcpy(snapshot->ss, buf, NTRUPLUS_SSBYTES);
	}
	secure_clear(msg, sizeof msg);
	secure_clear(buf, sizeof buf);
	secure_clear(&r, sizeof r);
	secure_clear(&m, sizeof m);
	sink += rhat[0];
	return 0;
}

__attribute__((noinline))
static int gt_prefix(unsigned stop, snapshot_t *snapshot)
{
	uint8_t msg[HASH_H_INBYTES];
	uint8_t buf[HASH_H_OUTBYTES];
	uint8_t rhat[NTRUPLUS_POLYBYTES];
	int16_t h[WORDS] __attribute__((aligned(64)));
	int16_t r[WORDS] __attribute__((aligned(64)));
	int16_t m[WORDS] __attribute__((aligned(64)));
	int16_t c[WORDS] __attribute__((aligned(64)));
	int16_t work[WORDS] __attribute__((aligned(64)));

	if (gt32_q24_decode_soa_asm(h, pk) != 0)
		return 1;
	memcpy(msg, coins, NTRUPLUS_N / 8);
	hash_f(msg + NTRUPLUS_N / 8, pk);
	hash_h(buf, msg);
	poly_cbd1((poly *)(void *)work, buf + NTRUPLUS_SYMBYTES);
	if (stop == 1) {
		if (snapshot != NULL)
			snapshot_coeff(snapshot, work);
		sink += (uint16_t)work[0];
		return 0;
	}

	forward_gt(r, c, work);
	if (stop == 2) {
		if (snapshot != NULL)
			gt32_q24_encode_soa_lazy10788_asm(snapshot->primary, r);
		sink += (uint16_t)r[0];
		return 0;
	}

	gt32_q24_encode_soa_lazy10788_asm(rhat, r);
	hash_g(rhat, rhat);
	poly_sotp_encode((poly *)(void *)work, msg, rhat);
	if (stop == 3) {
		if (snapshot != NULL)
			snapshot_coeff(snapshot, work);
		sink += (uint16_t)work[0];
		return 0;
	}

	forward_gt(m, c, work);
	if (stop == 4) {
		if (snapshot != NULL)
			gt32_q24_encode_soa_lazy10788_asm(snapshot->primary, m);
		sink += (uint16_t)m[0];
		return 0;
	}

	gt32_tile4_basemul_general_soa_soa_to_soa_asm(c, h, r);
	if (stop == 5) {
		if (snapshot != NULL)
			gt32_q24_encode_soa_encap_hr_h1_asm(snapshot->primary, c);
		sink += (uint16_t)c[0];
		return 0;
	}

	poly_add((poly *)(void *)c, (const poly *)(const void *)c,
		(const poly *)(const void *)m);
	if (stop == 6) {
		if (snapshot != NULL)
			gt32_q24_encode_soa_encap_hr_h1_asm(snapshot->primary, c);
		sink += (uint16_t)c[0];
		return 0;
	}

	gt32_q24_encode_soa_encap_hr_h1_asm(rhat, c);
	if (snapshot != NULL) {
		memcpy(snapshot->primary, rhat, sizeof rhat);
		memcpy(snapshot->ss, buf, NTRUPLUS_SSBYTES);
	}
	secure_clear(msg, sizeof msg);
	secure_clear(buf, sizeof buf);
	secure_clear(r, sizeof r);
	secure_clear(m, sizeof m);
	sink += rhat[0];
	return 0;
}

static double measure(prefix_fn fn, unsigned stop, unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		sink += (unsigned)fn(stop, NULL);
	const uint64_t end = stop_tsc();
	return (double)(end - begin) / iterations;
}

static int check_prefixes(void)
{
	for (unsigned stop = 1; stop <= 7; stop++) {
		snapshot_t official = {0};
		snapshot_t gt = {0};
		if (official_prefix(stop, &official) != 0
			|| gt_prefix(stop, &gt) != 0
			|| memcmp(&official, &gt, sizeof official) != 0) {
			fprintf(stderr, "prefix %u differential failed\n", stop);
			return 0;
		}
	}
	return 1;
}

int main(int argc, char **argv)
{
	static const char *const names[] = {
		"", "P1_decode_hash_cbd", "P2_forward_r", "P3_rpack_hashg_sotp",
		"P4_forward_m", "P5_basemul", "P6_add", "P7_pack_copy_clear"
	};
	const int perf_mode = argc > 1 && strcmp(argv[1], "--perf") == 0;
	const unsigned iterations = perf_mode && argc > 4
		? (unsigned)strtoul(argv[4], NULL, 10) : argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 500U;
	uint8_t entropy[48];
	cpu_set_t set;

	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof set, &set) != 0)
		perror("sched_setaffinity");
	for (size_t i = 0; i < sizeof entropy; i++)
		entropy[i] = (uint8_t)(31U + 7U * i);
	randombytes_init(entropy, NULL, 256);
	if (crypto_kem_keypair(pk, sk) != 0)
		return 1;
	for (size_t i = 0; i < sizeof coins; i++)
		coins[i] = (uint8_t)(11U + 37U * i);
	if (!check_prefixes())
		return 1;
	if (perf_mode) {
		if (argc <= 4) {
			fprintf(stderr, "usage: --perf prefix impl iterations\n");
			return 2;
		}
		if (strcmp(argv[2], "noop") == 0) {
			printf("PERF,noop,%s,0.000000\n", argv[3]);
			return 0;
		}
		for (unsigned stop = 1; stop <= 7; stop++) {
			if (strcmp(argv[2], names[stop]) == 0) {
				prefix_fn fn = strcmp(argv[3], "gt") == 0
					? gt_prefix : official_prefix;
				printf("PERF,%s,%s,%.6f\n", names[stop], argv[3],
					measure(fn, stop, iterations));
				return 0;
			}
		}
		fprintf(stderr, "unknown prefix: %s\n", argv[2]);
		return 2;
	}

	printf("META,correctness=byte-exact-prefix-pass,iterations=%u,samples=%u\n",
		iterations, SAMPLES);
	for (unsigned warm = 0; warm < 2; warm++)
		for (unsigned stop = 1; stop <= 7; stop++) {
			(void)measure(official_prefix, stop, 20);
			(void)measure(gt_prefix, stop, 20);
		}
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		for (unsigned stop = 1; stop <= 7; stop++) {
			double official;
			double gt;
			if ((sample & 1U) == 0) {
				official = measure(official_prefix, stop, iterations);
				gt = measure(gt_prefix, stop, iterations);
			} else {
				gt = measure(gt_prefix, stop, iterations);
				official = measure(official_prefix, stop, iterations);
			}
			printf("PREFIX,%s,%u,%.6f,%.6f,%.6f\n", names[stop], sample,
				official, gt, gt - official);
		}
	}
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}
