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
#define POST_I1_ITERS 3000U
#define CREP_ITERS 1600U
#define DECODE_CREP_ITERS 1000U
#define RECOVER_ITERS 600U
#define TRACE_ITERS 500U
#define FULL_ITERS 350U

enum { VARIANT_CONTROL, VARIANT_CANDIDATE, VARIANT_COUNT };
enum {
	COMPONENT_POST_I1,
	COMPONENT_CREP,
	COMPONENT_DECODE_CREP,
	COMPONENT_RECOVER,
	COMPONENT_TRACE,
	COMPONENT_FULL,
	COMPONENT_COUNT
};

static uint8_t pk[NTRUPLUS_PUBLICKEYBYTES] __attribute__((aligned(64)));
static uint8_t sk[NTRUPLUS_SECRETKEYBYTES] __attribute__((aligned(64)));
static uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES] __attribute__((aligned(64)));
static uint8_t ss[VARIANT_COUNT][NTRUPLUS_SSBYTES] __attribute__((aligned(64)));
static int16_t c[NTRUPLUS_N] __attribute__((aligned(64)));
static int16_t f[NTRUPLUS_N] __attribute__((aligned(64)));
static int16_t hinv[NTRUPLUS_N] __attribute__((aligned(64)));
static int16_t output[VARIANT_COUNT][NTRUPLUS_N] __attribute__((aligned(64)));
static uint8_t recovered[VARIANT_COUNT][NTRUPLUS_POLYBYTES]
	__attribute__((aligned(64)));
static uint8_t message[VARIANT_COUNT][NTRUPLUS_N / 8]
	__attribute__((aligned(64)));
static late066_region_scratch scratch[VARIANT_COUNT];
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

static void run_once(unsigned variant, unsigned component)
{
	if (component == COMPONENT_POST_I1) {
		if (variant == VARIANT_CONTROL)
			late066_post_i1_control(output[variant], c, f,
				&scratch[variant]);
		else
			late066_post_i1_candidate(output[variant], c, f,
				&scratch[variant]);
	} else if (component == COMPONENT_CREP) {
		if (variant == VARIANT_CONTROL)
			late066_crep_control(output[variant], c, f,
				&scratch[variant]);
		else
			late066_crep_candidate(output[variant], c, f,
				&scratch[variant]);
	} else if (component == COMPONENT_DECODE_CREP) {
		if (variant == VARIANT_CONTROL)
			sink += (unsigned)late066_decode_crep_control(output[variant],
				ct, sk);
		else
			sink += (unsigned)late066_decode_crep_candidate(output[variant],
				ct, sk);
	} else if (component == COMPONENT_RECOVER) {
		if (variant == VARIANT_CONTROL)
			sink += (unsigned)late066_recover_only_control(recovered[variant],
				ct, sk);
		else
			sink += (unsigned)late066_recover_only_candidate(recovered[variant],
				ct, sk);
	} else if (component == COMPONENT_TRACE) {
		if (variant == VARIANT_CONTROL)
			sink += (unsigned)late066_recover_trace_control(message[variant],
				recovered[variant], ct, sk);
		else
			sink += (unsigned)late066_recover_trace_candidate(message[variant],
				recovered[variant], ct, sk);
	} else if (variant == VARIANT_CONTROL) {
		sink += (unsigned)late066_dec_control(ss[variant], ct, sk);
	} else {
		sink += (unsigned)late066_dec_candidate(ss[variant], ct, sk);
	}
}

static unsigned iterations_for(unsigned component)
{
	static const unsigned values[COMPONENT_COUNT] = {
		POST_I1_ITERS, CREP_ITERS, DECODE_CREP_ITERS, RECOVER_ITERS,
		TRACE_ITERS, FULL_ITERS
	};
	return values[component];
}

static double run(unsigned variant, unsigned component, unsigned iterations)
{
	const uint64_t begin = ticks();
	for (unsigned i = 0; i < iterations; ++i) {
		run_once(variant, component);
		if (component <= COMPONENT_DECODE_CREP)
			sink += (uint16_t)output[variant][i % NTRUPLUS_N];
		else if (component == COMPONENT_RECOVER)
			sink += recovered[variant][i % NTRUPLUS_POLYBYTES];
		else if (component == COMPONENT_TRACE)
			sink += message[variant][i % (NTRUPLUS_N / 8)];
		else
			sink += ss[variant][i % NTRUPLUS_SSBYTES];
	}
	return (double)(ticks() - begin) / (double)iterations;
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
	uint8_t expected_ss[NTRUPLUS_SSBYTES];
	for (unsigned i = 0; i < sizeof coins; ++i)
		coins[i] = (uint8_t)(31U * i + 7U);
	if (ntruplus768_keypair_impl(pk, sk) != 0
		|| ntruplus768_enc_derand_impl(ct, expected_ss, pk, coins) != 0
		|| ntruplus768_unpack3_m_avx2(c, f, hinv, ct, sk) != 0
		|| late066_dec_control(ss[VARIANT_CONTROL], ct, sk) != 0
		|| late066_dec_candidate(ss[VARIANT_CANDIDATE], ct, sk) != 0
		|| memcmp(expected_ss, ss[VARIANT_CONTROL], sizeof expected_ss) != 0
		|| memcmp(expected_ss, ss[VARIANT_CANDIDATE], sizeof expected_ss) != 0) {
		fprintf(stderr, "benchmark preparation failed\n");
		exit(1);
	}
	late066_post_i1_control(output[VARIANT_CONTROL], c, f,
		&scratch[VARIANT_CONTROL]);
	late066_post_i1_candidate(output[VARIANT_CANDIDATE], c, f,
		&scratch[VARIANT_CANDIDATE]);
	if (memcmp(output[VARIANT_CONTROL], output[VARIANT_CANDIDATE],
		sizeof output[0]) != 0) {
		fprintf(stderr, "post-I1 preparation mismatch\n");
		exit(1);
	}
}

static unsigned parse_variant(const char *name)
{
	if (!strcmp(name, "control")) return VARIANT_CONTROL;
	if (!strcmp(name, "candidate")) return VARIANT_CANDIDATE;
	fprintf(stderr, "unknown variant: %s\n", name);
	exit(2);
}

static unsigned parse_component(const char *name)
{
	if (!strcmp(name, "post_i1")) return COMPONENT_POST_I1;
	if (!strcmp(name, "crep")) return COMPONENT_CREP;
	if (!strcmp(name, "decode_crep")) return COMPONENT_DECODE_CREP;
	if (!strcmp(name, "recover")) return COMPONENT_RECOVER;
	if (!strcmp(name, "trace")) return COMPONENT_TRACE;
	if (!strcmp(name, "full")) return COMPONENT_FULL;
	fprintf(stderr, "unknown component: %s\n", name);
	exit(2);
}

static int pmu(const char *variant_name, const char *component_name)
{
	static const unsigned iterations[COMPONENT_COUNT] = {
		450000U, 240000U, 160000U, 100000U, 90000U, 80000U
	};
	const unsigned variant = parse_variant(variant_name);
	const unsigned component = parse_component(component_name);
	(void)run(variant, component, iterations[component]);
	printf("%llu\n", (unsigned long long)sink);
	return 0;
}

int main(int argc, char **argv)
{
	pin_first_cpu();
	prepare();
	if (argc == 4 && !strcmp(argv[1], "--pmu"))
		return pmu(argv[2], argv[3]);

	double deltas[COMPONENT_COUNT][SAMPLES];
	for (unsigned sample = 0; sample < SAMPLES; ++sample) {
		const int reverse = (int)(sample & 1U);
		for (unsigned component = 0; component < COMPONENT_COUNT; ++component) {
			const unsigned iterations = iterations_for(component);
			double control;
			double candidate;
			if (!reverse) {
				control = run(VARIANT_CONTROL, component, iterations);
				candidate = run(VARIANT_CANDIDATE, component, iterations);
			} else {
				candidate = run(VARIANT_CANDIDATE, component, iterations);
				control = run(VARIANT_CONTROL, component, iterations);
			}
			deltas[component][sample] = candidate - control;
		}
	}

	printf("{\"delta_tsc\":{\"post_i1\":%.3f,\"crep\":%.3f,"
	       "\"decode_crep\":%.3f,\"recover\":%.3f,\"trace\":%.3f,"
	       "\"full\":%.3f},\"sink\":%llu}\n",
		median(deltas[COMPONENT_POST_I1]),
		median(deltas[COMPONENT_CREP]),
		median(deltas[COMPONENT_DECODE_CREP]),
		median(deltas[COMPONENT_RECOVER]),
		median(deltas[COMPONENT_TRACE]),
		median(deltas[COMPONENT_FULL]),
		(unsigned long long)sink);
	return 0;
}
