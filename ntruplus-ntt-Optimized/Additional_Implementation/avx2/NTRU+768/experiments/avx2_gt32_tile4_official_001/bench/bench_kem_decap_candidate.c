#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <x86intrin.h>

#include "api.h"
#include "kat/rng.h"

#include "tile4_kem_candidate.h"

#define SAMPLES 20

typedef int (*decap_fn)(uint8_t *, const uint8_t *, const uint8_t *);

static uint8_t public_key[CRYPTO_PUBLICKEYBYTES] __attribute__((aligned(64)));
static uint8_t secret_key[CRYPTO_SECRETKEYBYTES] __attribute__((aligned(64)));
static uint8_t ciphertext[CRYPTO_CIPHERTEXTBYTES] __attribute__((aligned(64)));
static uint8_t encapsulated_ss[CRYPTO_BYTES] __attribute__((aligned(64)));
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
		entropy[i] = (uint8_t)(17U + 29U * i);
	randombytes_init(entropy, NULL, 256);
}

__attribute__((noinline))
static int decap_official(uint8_t *ss, const uint8_t *ct, const uint8_t *sk)
{
	return crypto_kem_dec(ss, ct, sk);
}

__attribute__((noinline))
static int decap_gt32(uint8_t *ss, const uint8_t *ct, const uint8_t *sk)
{
	return crypto_kem_dec_gt32_candidate(ss, ct, sk);
}

__attribute__((noinline))
static int decap_gt32_soa_domain(uint8_t *ss, const uint8_t *ct,
	const uint8_t *sk)
{
	return crypto_kem_dec_gt32_soa_domain_candidate(ss, ct, sk);
}

__attribute__((noinline))
static int decap_gt32_soa_domain_zeroinit(uint8_t *ss, const uint8_t *ct,
	const uint8_t *sk)
{
	return crypto_kem_dec_gt32_soa_domain_zeroinit_control(ss, ct, sk);
}

__attribute__((noinline))
static int decap_gt32_soa_domain_direct(uint8_t *ss, const uint8_t *ct,
	const uint8_t *sk)
{
	return crypto_kem_dec_gt32_soa_domain_direct_control(ss, ct, sk);
}

static double measure(decap_fn fn, uint8_t *ss, unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		sink += (unsigned)fn(ss, ciphertext, secret_key);
	const uint64_t end = stop_tsc();
	sink += ss[iterations % CRYPTO_BYTES];
	return (double)(end - begin) / iterations;
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	uint8_t official_ss[CRYPTO_BYTES] __attribute__((aligned(64)));
	uint8_t gt32_ss[CRYPTO_BYTES] __attribute__((aligned(64)));
	uint8_t soa_domain_ss[CRYPTO_BYTES] __attribute__((aligned(64)));
	uint8_t zeroinit_ss[CRYPTO_BYTES] __attribute__((aligned(64)));
	uint8_t direct_ss[CRYPTO_BYTES] __attribute__((aligned(64)));
	cpu_set_t set;

	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof(set), &set) != 0)
		perror("sched_setaffinity");
	reset_rng();
	if (crypto_kem_keypair(public_key, secret_key) != 0
		|| crypto_kem_enc(ciphertext, encapsulated_ss, public_key) != 0
		|| decap_official(official_ss, ciphertext, secret_key) != 0
		|| decap_gt32(gt32_ss, ciphertext, secret_key) != 0
		|| decap_gt32_soa_domain(soa_domain_ss, ciphertext, secret_key) != 0
		|| decap_gt32_soa_domain_zeroinit(zeroinit_ss, ciphertext,
			secret_key) != 0
		|| decap_gt32_soa_domain_direct(direct_ss, ciphertext,
			secret_key) != 0
		|| memcmp(official_ss, gt32_ss, sizeof official_ss) != 0
		|| memcmp(official_ss, soa_domain_ss, sizeof official_ss) != 0
		|| memcmp(official_ss, zeroinit_ss, sizeof official_ss) != 0
		|| memcmp(official_ss, direct_ss, sizeof official_ss) != 0
		|| memcmp(official_ss, encapsulated_ss, sizeof official_ss) != 0) {
		fprintf(stderr, "same-binary valid decapsulation check failed\n");
		return 1;
	}
	for (unsigned warm = 0; warm < 2; warm++) {
		(void)measure(decap_official, official_ss, 100);
		(void)measure(decap_gt32, gt32_ss, 100);
		(void)measure(decap_gt32_soa_domain, soa_domain_ss, 100);
		(void)measure(decap_gt32_soa_domain_zeroinit, zeroinit_ss, 100);
		(void)measure(decap_gt32_soa_domain_direct, direct_ss, 100);
	}
	printf("META,correctness=byte-exact,scope=valid-decap-short-only,"
		"iterations=%u,samples=%u,order=AB-BA\n", iterations, SAMPLES);
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		double official;
		double gt32;
		double soa_domain;
		double zeroinit;
		double direct;
		if ((sample & 1U) == 0U) {
			official = measure(decap_official, official_ss, iterations);
			gt32 = measure(decap_gt32, gt32_ss, iterations);
			soa_domain = measure(decap_gt32_soa_domain, soa_domain_ss,
				iterations);
			zeroinit = measure(decap_gt32_soa_domain_zeroinit, zeroinit_ss,
				iterations);
			direct = measure(decap_gt32_soa_domain_direct, direct_ss,
				iterations);
		} else {
			direct = measure(decap_gt32_soa_domain_direct, direct_ss,
				iterations);
			zeroinit = measure(decap_gt32_soa_domain_zeroinit, zeroinit_ss,
				iterations);
			soa_domain = measure(decap_gt32_soa_domain, soa_domain_ss,
				iterations);
			gt32 = measure(decap_gt32, gt32_ss, iterations);
			official = measure(decap_official, official_ss, iterations);
		}
		printf("SAMPLE,%u,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f,%.6f\n",
			sample,
			official, gt32, soa_domain, gt32 - official,
			soa_domain - official, zeroinit, soa_domain - zeroinit,
			direct, direct - soa_domain);
	}
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}
