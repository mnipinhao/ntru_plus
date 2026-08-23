#define _GNU_SOURCE
#include "late067.h"

#include <immintrin.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "api.h"

#define SAMPLES 61
#define PAIRED_ITERATIONS 350U
#define PMU_ITERATIONS 80000U

enum { CONTROL, CANDIDATE, VARIANTS };

static uint8_t pk[NTRUPLUS_PUBLICKEYBYTES] __attribute__((aligned(64)));
static uint8_t sk[NTRUPLUS_SECRETKEYBYTES] __attribute__((aligned(64)));
static uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES] __attribute__((aligned(64)));
static uint8_t expected[NTRUPLUS_SSBYTES] __attribute__((aligned(64)));
static uint8_t ss[VARIANTS][NTRUPLUS_SSBYTES] __attribute__((aligned(64)));
static volatile uint64_t sink;

static uint64_t ticks(void)
{
	unsigned aux;
	_mm_lfence();
	const uint64_t value = __rdtscp(&aux);
	_mm_lfence();
	return value;
}

static int cmp_double(const void *left, const void *right)
{
	const double a = *(const double *)left;
	const double b = *(const double *)right;
	return (a > b) - (a < b);
}

static double median(double values[SAMPLES])
{
	qsort(values, SAMPLES, sizeof(*values), cmp_double);
	return values[SAMPLES / 2];
}

static int decap(unsigned variant)
{
	if (variant == CONTROL)
		return crypto_kem_dec_control(ss[variant], ct, sk);
	return crypto_kem_dec_latesoa(ss[variant], ct, sk);
}

static void prepare(void)
{
	if (crypto_kem_keypair(pk, sk) != 0
		|| crypto_kem_enc(ct, expected, pk) != 0
		|| decap(CONTROL) != 0 || decap(CANDIDATE) != 0
		|| memcmp(expected, ss[CONTROL], sizeof expected) != 0
		|| memcmp(expected, ss[CANDIDATE], sizeof expected) != 0) {
		fprintf(stderr, "production benchmark preparation failed\n");
		exit(1);
	}
}

static double run(unsigned variant, unsigned iterations)
{
	const uint64_t begin = ticks();
	for (unsigned i = 0; i < iterations; ++i) {
		sink += (unsigned)decap(variant);
		sink += ss[variant][i % NTRUPLUS_SSBYTES];
	}
	return (double)(ticks() - begin) / iterations;
}

static int paired_main(void)
{
	double delta[SAMPLES];
	prepare();
	for (unsigned sample = 0; sample < SAMPLES; ++sample) {
		double control;
		double candidate;
		if ((sample & 1U) == 0) {
			control = run(CONTROL, PAIRED_ITERATIONS);
			candidate = run(CANDIDATE, PAIRED_ITERATIONS);
		} else {
			candidate = run(CANDIDATE, PAIRED_ITERATIONS);
			control = run(CONTROL, PAIRED_ITERATIONS);
		}
		delta[sample] = candidate - control;
	}
	printf("{\"delta_tsc\":%.3f,\"sink\":%llu}\n", median(delta),
		(unsigned long long)sink);
	return 0;
}

static int pmu_main(const char *profile)
{
	unsigned variant;
	prepare();
	if (strcmp(profile, "control") == 0)
		variant = CONTROL;
	else if (strcmp(profile, "candidate") == 0)
		variant = CANDIDATE;
	else
		return 64;
	(void)run(variant, PMU_ITERATIONS);
	printf("{\"profile\":\"%s\",\"iterations\":%u,\"sink\":%llu}\n",
		profile, PMU_ITERATIONS, (unsigned long long)sink);
	return 0;
}

int main(int argc, char **argv)
{
	if (argc == 1)
		return paired_main();
	if (argc == 3 && strcmp(argv[1], "--pmu") == 0)
		return pmu_main(argv[2]);
	fprintf(stderr, "usage: %s [--pmu control|candidate]\n", argv[0]);
	return 64;
}
