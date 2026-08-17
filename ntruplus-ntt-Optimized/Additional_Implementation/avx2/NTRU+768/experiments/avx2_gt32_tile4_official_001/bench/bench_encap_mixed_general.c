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

typedef struct {
	int16_t frontend[WORDS];
	int16_t h[WORDS];
	int16_t r_frequency[WORDS];
	int16_t product[WORDS];
} encap_scratch_t;

typedef void (*encap_subchain_fn)(int16_t *, const uint8_t *,
	const int16_t *, const int16_t *, encap_scratch_t *);

static volatile uint64_t sink;

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

static void add_aos(int16_t *out, const int16_t *a, const int16_t *b)
{
	for (unsigned i = 0; i < WORDS; i++)
		out[i] = (int16_t)(a[i] + b[i]);
}

__attribute__((noinline))
static void encap_subchain_aa(int16_t *out, const uint8_t *encoded_h,
	const int16_t *r, const int16_t *m_frequency, encap_scratch_t *scratch)
{
	(void)gt32_tile4_frombytes_aos_asm(scratch->h, encoded_h);
	gt32_tile4_frontend_wide_raw_asm(scratch->frontend, r);
	gt32_tile4_forward_all_pair_asm(scratch->r_frequency,
		scratch->frontend);
	gt32_tile4_basemul_general_b2_asm(scratch->product, scratch->h,
		scratch->r_frequency);
	add_aos(out, scratch->product, m_frequency);
}

__attribute__((noinline))
static void encap_subchain_sa(int16_t *out, const uint8_t *encoded_h,
	const int16_t *r, const int16_t *m_frequency, encap_scratch_t *scratch)
{
	(void)gt32_tile4_frombytes_aos_asm(scratch->h, encoded_h);
	gt32_tile4_frontend_wide_raw_asm(scratch->frontend, r);
	gt32_tile4_attr_forward_all_bm_soa_asm(scratch->r_frequency,
		scratch->frontend);
	gt32_tile4_basemul_general_soa_aos_to_aos_asm(scratch->product,
		scratch->r_frequency, scratch->h);
	add_aos(out, scratch->product, m_frequency);
}

static double measure(encap_subchain_fn fn, int16_t *out,
	const uint8_t *encoded_h, const int16_t *r, const int16_t *m_frequency,
	encap_scratch_t *scratch, unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		fn(out, encoded_h, r, m_frequency, scratch);
	const uint64_t end = stop_tsc();
	sink += (uint16_t)out[iterations & (WORDS - 1U)];
	return (double)(end - begin) / iterations;
}

static uint32_t next_random(uint32_t *state)
{
	*state = *state * 1664525U + 1013904223U;
	return *state;
}

static void fill_small(int16_t *out, uint32_t *state)
{
	for (unsigned i = 0; i < WORDS; i++)
		out[i] = (int16_t)((int)(next_random(state) >> 29) - 3);
}

static void pack_canonical(uint8_t out[BYTES], uint32_t *state)
{
	for (unsigned pair = 0; pair < WORDS / 2U; pair++) {
		const uint16_t a = (uint16_t)(next_random(state) % GT32_TILE4_Q);
		const uint16_t b = (uint16_t)(next_random(state) % GT32_TILE4_Q);
		out[3U * pair] = (uint8_t)a;
		out[3U * pair + 1U] = (uint8_t)((a >> 8) | (uint16_t)(b << 4));
		out[3U * pair + 2U] = (uint8_t)(b >> 4);
	}
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	encap_scratch_t aa_scratch __attribute__((aligned(64)));
	encap_scratch_t sa_scratch __attribute__((aligned(64)));
	int16_t r[WORDS] __attribute__((aligned(64)));
	int16_t m[WORDS] __attribute__((aligned(64)));
	int16_t m_frontend[WORDS] __attribute__((aligned(64)));
	int16_t aa_out[WORDS] __attribute__((aligned(64)));
	int16_t sa_out[WORDS] __attribute__((aligned(64)));
	uint8_t encoded_h[BYTES] __attribute__((aligned(64)));
	uint32_t random_state = 1U;
	cpu_set_t set;

	CPU_ZERO(&set);
	CPU_SET(1, &set);
	if (sched_setaffinity(0, sizeof(set), &set) != 0)
		perror("sched_setaffinity");

	for (unsigned trial = 0; trial < 64; trial++) {
		pack_canonical(encoded_h, &random_state);
		fill_small(r, &random_state);
		fill_small(m, &random_state);
		gt32_tile4_frontend_wide_raw_asm(m_frontend, m);
		gt32_tile4_forward_all_pair_asm(m, m_frontend);
		encap_subchain_aa(aa_out, encoded_h, r, m, &aa_scratch);
		encap_subchain_sa(sa_out, encoded_h, r, m, &sa_scratch);
		if (memcmp(aa_out, sa_out, sizeof(aa_out)) != 0) {
			fprintf(stderr, "encap mixed general differential failed trial=%u\n",
				trial);
			return 1;
		}
	}

	for (unsigned warm = 0; warm < 2; warm++) {
		(void)measure(encap_subchain_aa, aa_out, encoded_h, r, m,
			&aa_scratch, 1000);
		(void)measure(encap_subchain_sa, sa_out, encoded_h, r, m,
			&sa_scratch, 1000);
	}
	printf("META,correctness=pass,scope=frombytes-h+ntt-r+general-bm+add-m,"
		"output=tile4-aos-e0,iterations=%u,samples=%u\n", iterations,
		SAMPLES);
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		double aa;
		double sa;
		if ((sample & 1U) == 0U) {
			aa = measure(encap_subchain_aa, aa_out, encoded_h, r, m,
				&aa_scratch, iterations);
			sa = measure(encap_subchain_sa, sa_out, encoded_h, r, m,
				&sa_scratch, iterations);
		} else {
			sa = measure(encap_subchain_sa, sa_out, encoded_h, r, m,
				&sa_scratch, iterations);
			aa = measure(encap_subchain_aa, aa_out, encoded_h, r, m,
				&aa_scratch, iterations);
		}
		printf("SAMPLE,%u,%.6f,%.6f,%.6f\n", sample, aa, sa, sa - aa);
	}
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}
