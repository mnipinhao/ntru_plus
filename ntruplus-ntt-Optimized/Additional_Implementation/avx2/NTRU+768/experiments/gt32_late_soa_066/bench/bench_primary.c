#define _GNU_SOURCE
#include "late066.h"

#include <immintrin.h>
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "internal.h"

#define SAMPLES 41

enum { CONTROL, CANDIDATE, VARIANTS };
enum { POST_I1, CREP, FULL, COMPONENTS };

static const unsigned iterations[COMPONENTS] = {3000U, 1600U, 350U};
static uint8_t pk[NTRUPLUS_PUBLICKEYBYTES] __attribute__((aligned(64)));
static uint8_t sk[NTRUPLUS_SECRETKEYBYTES] __attribute__((aligned(64)));
static uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES] __attribute__((aligned(64)));
static uint8_t ss[VARIANTS][NTRUPLUS_SSBYTES] __attribute__((aligned(64)));
static int16_t c[NTRUPLUS_N] __attribute__((aligned(64)));
static int16_t f[NTRUPLUS_N] __attribute__((aligned(64)));
static int16_t hinv[NTRUPLUS_N] __attribute__((aligned(64)));
static int16_t output[VARIANTS][NTRUPLUS_N] __attribute__((aligned(64)));
static late066_region_scratch scratch[VARIANTS];
static volatile uint64_t sink;

static uint64_t ticks(void)
{
	unsigned aux;
	_mm_lfence();
	const uint64_t value = __rdtscp(&aux);
	_mm_lfence();
	return value;
}
static int cmp_double(const void *a, const void *b)
{
	const double x = *(const double *)a;
	const double y = *(const double *)b;
	return (x > y) - (x < y);
}

static double median(double values[SAMPLES])
{
	qsort(values, SAMPLES, sizeof(*values), cmp_double);
	return values[SAMPLES / 2];
}

static void once(unsigned variant, unsigned component)
{
	if (component == POST_I1) {
		if (variant == CONTROL)
			late066_post_i1_control(output[variant], c, f,
				&scratch[variant]);
		else
			late066_post_i1_candidate(output[variant], c, f,
				&scratch[variant]);
	} else if (component == CREP) {
		if (variant == CONTROL)
			late066_crep_control(output[variant], c, f,
				&scratch[variant]);
		else
			late066_crep_candidate(output[variant], c, f,
				&scratch[variant]);
	} else if (variant == CONTROL) {
		sink += (unsigned)late066_dec_control(ss[variant], ct, sk);
	} else {
		sink += (unsigned)late066_dec_candidate(ss[variant], ct, sk);
	}
}

static double run(unsigned variant, unsigned component)
{
	const uint64_t begin = ticks();
	for (unsigned i = 0; i < iterations[component]; ++i) {
		once(variant, component);
		if (component == FULL)
			sink += ss[variant][i % NTRUPLUS_SSBYTES];
		else
			sink += (uint16_t)output[variant][i % NTRUPLUS_N];
	}
	return (double)(ticks() - begin) / iterations[component];
}

static void pin_first_cpu(void)
{
	cpu_set_t available;
	cpu_set_t selected;
	CPU_ZERO(&available);
	if (sched_getaffinity(0, sizeof available, &available) != 0)
		return;
	for (int cpu = 0; cpu < CPU_SETSIZE; ++cpu) {
		if (!CPU_ISSET(cpu, &available))
			continue;
		CPU_ZERO(&selected);
		CPU_SET(cpu, &selected);
		(void)sched_setaffinity(0, sizeof selected, &selected);
		return;
	}
}

static void prepare(void)
{
	uint8_t coins[NTRUPLUS_N / 8];
	uint8_t expected[NTRUPLUS_SSBYTES];
	for (unsigned i = 0; i < sizeof coins; ++i)
		coins[i] = (uint8_t)(31U * i + 7U);
	if (ntruplus768_keypair_impl(pk, sk) != 0
		|| ntruplus768_enc_derand_impl(ct, expected, pk, coins) != 0
		|| ntruplus768_unpack3_m_avx2(c, f, hinv, ct, sk) != 0
		|| late066_dec_control(ss[CONTROL], ct, sk) != 0
		|| late066_dec_candidate(ss[CANDIDATE], ct, sk) != 0
		|| memcmp(expected, ss[CONTROL], sizeof expected) != 0
		|| memcmp(expected, ss[CANDIDATE], sizeof expected) != 0) {
		fprintf(stderr, "primary benchmark preparation failed\n");
		exit(1);
	}
}

int main(void)
{
	pin_first_cpu();
	prepare();
	double delta[COMPONENTS][SAMPLES];
	for (unsigned sample = 0; sample < SAMPLES; ++sample) {
		for (unsigned component = 0; component < COMPONENTS; ++component) {
			double control;
			double candidate;
			if ((sample & 1U) == 0) {
				control = run(CONTROL, component);
				candidate = run(CANDIDATE, component);
			} else {
				candidate = run(CANDIDATE, component);
				control = run(CONTROL, component);
			}
			delta[component][sample] = candidate - control;
		}
	}
	printf("{\"delta_tsc\":{\"post_i1\":%.3f,\"crep\":%.3f,"
	       "\"full\":%.3f},\"sink\":%llu}\n",
		median(delta[POST_I1]), median(delta[CREP]), median(delta[FULL]),
		(unsigned long long)sink);
	return 0;
}
