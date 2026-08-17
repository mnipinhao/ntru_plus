#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <x86intrin.h>

#include "../generated/tile4_baseinv_p_mapping.h"
#include "../generated/tile4_serialized_mapping.h"

#define WORDS 768
#define POLYBYTES 1152
#define TRIALS 1000

void gt32_tile4_frontend_wide_raw_asm(int16_t *, const int16_t *);
void gt32_tile4_attr_forward_all_baseinv_p_l3_asm(int16_t *, const int16_t *);
void gt32_global_forward_core_asm(int16_t *, const int16_t *);
void gt32_global_forward_baseinv_m_safe_core_asm(int16_t *, const int16_t *);
void gt32_progressive_suffix_forward_p_safe_core_asm(int16_t *, const int16_t *);
int gt32_p_baseinv_direct_asm_avx2(int16_t *, const int16_t *);
int gt32_m_baseinv_direct_asm_avx2(int16_t *, const int16_t *);
void gt_basemul_native_asm_avx2(int16_t *, const int16_t *, const int16_t *);
void gt32_tile4_basemul_general_soa_soa_to_soa_asm(
	int16_t *, const int16_t *, const int16_t *);
void gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm(
	uint8_t *, const int16_t *);
void gt32_q24_encode_soa_lazy10788_asm(uint8_t *, const int16_t *);

static int16_t seed_f[WORDS] __attribute__((aligned(64)));
static int16_t seed_g[WORDS] __attribute__((aligned(64)));
static int16_t frontend[WORDS] __attribute__((aligned(64)));
static int16_t pf[WORDS] __attribute__((aligned(64)));
static int16_t pg[WORDS] __attribute__((aligned(64)));
static int16_t mf[WORDS] __attribute__((aligned(64)));
static int16_t mg[WORDS] __attribute__((aligned(64)));
static int16_t pfinv[WORDS] __attribute__((aligned(64)));
static int16_t pginv[WORDS] __attribute__((aligned(64)));
static int16_t mfinv[WORDS] __attribute__((aligned(64)));
static int16_t mginv[WORDS] __attribute__((aligned(64)));
static int16_t ph[WORDS] __attribute__((aligned(64)));
static int16_t phinv[WORDS] __attribute__((aligned(64)));
static int16_t mh[WORDS] __attribute__((aligned(64)));
static int16_t mhinv[WORDS] __attribute__((aligned(64)));
static uint8_t pbytes[3][POLYBYTES] __attribute__((aligned(64)));
static uint8_t mbytes[3][POLYBYTES] __attribute__((aligned(64)));
static volatile uint64_t sink;
static uint32_t rng = 0x4d424931U;

static uint32_t random32(void)
{
	rng ^= rng << 13;
	rng ^= rng >> 17;
	rng ^= rng << 5;
	return rng;
}

static int center(int value)
{
	value %= 3457;
	if (value < 0) value += 3457;
	if (value > 1728) value -= 3457;
	return value;
}

static void p_forward(int16_t out[WORDS], const int16_t in[WORDS])
{
	gt32_tile4_frontend_wide_raw_asm(frontend, in);
	gt32_tile4_attr_forward_all_baseinv_p_l3_asm(out, frontend);
}

static void p_forward_suffix(int16_t out[WORDS], const int16_t in[WORDS])
{
	gt32_tile4_frontend_wide_raw_asm(frontend, in);
	gt32_progressive_suffix_forward_p_safe_core_asm(out, frontend);
}

static int same_layout_mod_q(const int16_t a[WORDS], const int16_t b[WORDS])
{
	for (unsigned i = 0; i < WORDS; i++)
		if (center(a[i]) != center(b[i])) return 0;
	return 1;
}

static void m_forward_control(int16_t out[WORDS], const int16_t in[WORDS])
{
	gt32_tile4_frontend_wide_raw_asm(frontend, in);
	gt32_global_forward_core_asm(out, frontend);
}

static void m_forward_safe(int16_t out[WORDS], const int16_t in[WORDS])
{
	gt32_tile4_frontend_wide_raw_asm(frontend, in);
	gt32_global_forward_baseinv_m_safe_core_asm(out, frontend);
}

static int same_p_m(const int16_t p[WORDS], const int16_t m[WORDS])
{
	for (unsigned serialized = 0; serialized < WORDS; serialized++) {
		const unsigned pw = gt32_p_word_from_serialized[serialized];
		const unsigned mw = gt32_tile4_serialized_to_bm_soa[serialized];
		if (center(p[pw]) != center(m[mw])) return 0;
	}
	return 1;
}

static int all_zero(const int16_t value[WORDS])
{
	for (unsigned i = 0; i < WORDS; i++)
		if (value[i] != 0) return 0;
	return 1;
}

static void p_pack3(void)
{
	gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm(pbytes[0], pf);
	gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm(pbytes[1], ph);
	gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm(pbytes[2], phinv);
}

static void m_pack3(void)
{
	gt32_q24_encode_soa_lazy10788_asm(mbytes[0], mf);
	gt32_q24_encode_soa_lazy10788_asm(mbytes[1], mh);
	gt32_q24_encode_soa_lazy10788_asm(mbytes[2], mhinv);
}

__attribute__((noinline)) static void m1_control(void)
{
	m_forward_control(mf, seed_f);
}

__attribute__((noinline)) static void m1_candidate(void)
{
	m_forward_safe(mf, seed_f);
}

__attribute__((noinline)) static void m2_control(void)
{
	(void)gt32_p_baseinv_direct_asm_avx2(pfinv, pf);
	(void)gt32_p_baseinv_direct_asm_avx2(pginv, pg);
}

__attribute__((noinline)) static void m2_candidate(void)
{
	(void)gt32_m_baseinv_direct_asm_avx2(mfinv, mf);
	(void)gt32_m_baseinv_direct_asm_avx2(mginv, mg);
}

__attribute__((noinline)) static void m3_control(void)
{
	p_forward(pf, seed_f);
	p_forward(pg, seed_g);
	(void)gt32_p_baseinv_direct_asm_avx2(pfinv, pf);
	(void)gt32_p_baseinv_direct_asm_avx2(pginv, pg);
	gt_basemul_native_asm_avx2(ph, pg, pfinv);
	gt_basemul_native_asm_avx2(phinv, pf, pginv);
}

__attribute__((noinline)) static void m3_candidate(void)
{
	m_forward_safe(mf, seed_f);
	m_forward_safe(mg, seed_g);
	(void)gt32_m_baseinv_direct_asm_avx2(mfinv, mf);
	(void)gt32_m_baseinv_direct_asm_avx2(mginv, mg);
	gt32_tile4_basemul_general_soa_soa_to_soa_asm(mh, mg, mfinv);
	gt32_tile4_basemul_general_soa_soa_to_soa_asm(mhinv, mf, mginv);
}

__attribute__((noinline)) static void m4_control(void)
{
	m3_control();
	p_pack3();
}

__attribute__((noinline)) static void m4_candidate(void)
{
	m3_candidate();
	m_pack3();
}

__attribute__((noinline)) static void p_suffix_k3k5_candidate(void)
{
	p_forward_suffix(pf, seed_f);
	p_forward_suffix(pg, seed_g);
	(void)gt32_p_baseinv_direct_asm_avx2(pfinv, pf);
	(void)gt32_p_baseinv_direct_asm_avx2(pginv, pg);
	gt_basemul_native_asm_avx2(ph, pg, pfinv);
	gt_basemul_native_asm_avx2(phinv, pf, pginv);
	p_pack3();
}

__attribute__((noinline)) static void p_suffix_f_control(void)
{
	p_forward(pf, seed_f);
	p_forward(pg, seed_g);
}

__attribute__((noinline)) static void p_suffix_f_candidate(void)
{
	p_forward_suffix(pf, seed_f);
	p_forward_suffix(pg, seed_g);
}

__attribute__((noinline)) static void p_suffix_fbi_control(void)
{
	p_suffix_f_control();
	(void)gt32_p_baseinv_direct_asm_avx2(pfinv, pf);
	(void)gt32_p_baseinv_direct_asm_avx2(pginv, pg);
}

__attribute__((noinline)) static void p_suffix_fbi_candidate(void)
{
	p_suffix_f_candidate();
	(void)gt32_p_baseinv_direct_asm_avx2(pfinv, pf);
	(void)gt32_p_baseinv_direct_asm_avx2(pginv, pg);
}

__attribute__((noinline)) static void p_suffix_bm_control(void)
{
	p_suffix_fbi_control();
	gt_basemul_native_asm_avx2(ph, pg, pfinv);
	gt_basemul_native_asm_avx2(phinv, pf, pginv);
}

__attribute__((noinline)) static void p_suffix_bm_candidate(void)
{
	p_suffix_fbi_candidate();
	gt_basemul_native_asm_avx2(ph, pg, pfinv);
	gt_basemul_native_asm_avx2(phinv, pf, pginv);
}

typedef void (*region_fn)(void);

static void run(region_fn function, unsigned iterations)
{
	for (unsigned i = 0; i < iterations; i++) function();
	sink += (uint64_t)(uint16_t)pf[iterations % WORDS]
		+ (uint64_t)(uint16_t)mf[(iterations * 3U) % WORDS]
		+ (uint64_t)pbytes[0][iterations % POLYBYTES]
		+ (uint64_t)mbytes[0][(iterations * 5U) % POLYBYTES];
}

static uint64_t timed(region_fn function, unsigned iterations)
{
	unsigned aux;
	_mm_lfence();
	const uint64_t begin = __rdtsc();
	run(function, iterations);
	const uint64_t end = __rdtscp(&aux);
	_mm_lfence();
	return end - begin;
}

static int prepare_invertible(void)
{
	for (unsigned attempt = 0; attempt < 10000; attempt++) {
		for (unsigned i = 0; i < WORDS; i++) {
			seed_f[i] = (int16_t)((int)(random32() & 7U) - 3);
			seed_g[i] = (int16_t)((int)(random32() & 7U) - 3);
		}
		p_forward(pf, seed_f);
		p_forward(pg, seed_g);
		m_forward_safe(mf, seed_f);
		m_forward_safe(mg, seed_g);
		if (gt32_p_baseinv_direct_asm_avx2(pfinv, pf) == 0
				&& gt32_p_baseinv_direct_asm_avx2(pginv, pg) == 0
				&& gt32_m_baseinv_direct_asm_avx2(mfinv, mf) == 0
				&& gt32_m_baseinv_direct_asm_avx2(mginv, mg) == 0)
			return 1;
	}
	return 0;
}

static int differential(void)
{
	unsigned accepted = 0;
	int16_t alias[WORDS] __attribute__((aligned(64)));
	int16_t zero[WORDS] __attribute__((aligned(64))) = {0};
	int16_t failed[WORDS] __attribute__((aligned(64)));

	for (unsigned trial = 0; trial < TRIALS; trial++) {
		for (unsigned i = 0; i < WORDS; i++) {
			seed_f[i] = (int16_t)((int)(random32() & 7U) - 3);
			seed_g[i] = (int16_t)((int)(random32() & 7U) - 3);
		}
		p_forward(pf, seed_f);
		p_forward(pg, seed_g);
		p_forward_suffix(mf, seed_f);
		p_forward_suffix(mg, seed_g);
		if (!same_layout_mod_q(pf, mf) || !same_layout_mod_q(pg, mg))
			return fprintf(stderr, "P suffix Forward mismatch %u\n", trial), 0;
		const int pss0 = gt32_p_baseinv_direct_asm_avx2(mfinv, mf);
		const int pss1 = gt32_p_baseinv_direct_asm_avx2(mginv, mg);
		const int pcs0 = gt32_p_baseinv_direct_asm_avx2(pfinv, pf);
		const int pcs1 = gt32_p_baseinv_direct_asm_avx2(pginv, pg);
		if (pss0 != pcs0 || pss1 != pcs1
				|| (pcs0 == 0 && !same_layout_mod_q(pfinv, mfinv))
				|| (pcs1 == 0 && !same_layout_mod_q(pginv, mginv)))
			return fprintf(stderr, "P suffix BaseInv mismatch %u\n", trial), 0;
		if (pcs0 == 0 && pcs1 == 0) {
			gt_basemul_native_asm_avx2(ph, pg, pfinv);
			gt_basemul_native_asm_avx2(mh, mg, mfinv);
			gt_basemul_native_asm_avx2(phinv, pf, pginv);
			gt_basemul_native_asm_avx2(mhinv, mf, mginv);
			if (!same_layout_mod_q(ph, mh) || !same_layout_mod_q(phinv, mhinv))
				return fprintf(stderr, "P suffix BM mismatch %u\n", trial), 0;
			p_pack3();
			gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm(mbytes[0], mf);
			gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm(mbytes[1], mh);
			gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm(mbytes[2], mhinv);
			if (memcmp(pbytes, mbytes, sizeof pbytes) != 0)
				return fprintf(stderr, "P suffix Q24 mismatch %u\n", trial), 0;
		}
		m_forward_control(mh, seed_f);
		m_forward_safe(mf, seed_f);
		m_forward_safe(mg, seed_g);
		if (!same_p_m(pf, mf) || !same_p_m(pg, mg))
			return fprintf(stderr, "Forward semantic mismatch %u\n", trial), 0;
		for (unsigned i = 0; i < WORDS; i++)
			if (center(mh[i]) != center(mf[i]))
				return fprintf(stderr, "M-safe representative mismatch %u\n", trial), 0;

		const int ps0 = gt32_p_baseinv_direct_asm_avx2(pfinv, pf);
		const int ps1 = gt32_p_baseinv_direct_asm_avx2(pginv, pg);
		const int ms0 = gt32_m_baseinv_direct_asm_avx2(mfinv, mf);
		const int ms1 = gt32_m_baseinv_direct_asm_avx2(mginv, mg);
		if (ps0 != ms0 || ps1 != ms1)
			return fprintf(stderr, "BaseInv status mismatch %u\n", trial), 0;
		if (ps0 == 0 && ps1 == 0) {
			accepted++;
			if (!same_p_m(pfinv, mfinv) || !same_p_m(pginv, mginv))
				return fprintf(stderr, "BaseInv value mismatch %u\n", trial), 0;
			memcpy(alias, mf, sizeof alias);
			if (gt32_m_baseinv_direct_asm_avx2(alias, alias) != 0
					|| memcmp(alias, mfinv, sizeof alias) != 0)
				return fprintf(stderr, "M BaseInv alias mismatch %u\n", trial), 0;
			gt_basemul_native_asm_avx2(ph, pg, pfinv);
			gt_basemul_native_asm_avx2(phinv, pf, pginv);
			gt32_tile4_basemul_general_soa_soa_to_soa_asm(mh, mg, mfinv);
			gt32_tile4_basemul_general_soa_soa_to_soa_asm(mhinv, mf, mginv);
			if (!same_p_m(ph, mh) || !same_p_m(phinv, mhinv))
				return fprintf(stderr, "BM value mismatch %u\n", trial), 0;
			p_pack3();
			m_pack3();
			if (memcmp(pbytes, mbytes, sizeof pbytes) != 0)
				return fprintf(stderr, "Q24 byte mismatch %u\n", trial), 0;
		}
	}
	memset(failed, 0x5a, sizeof failed);
	if (gt32_m_baseinv_direct_asm_avx2(failed, zero) != 1 || !all_zero(failed))
		return fprintf(stderr, "M BaseInv noninvertible semantics mismatch\n"), 0;
	printf("correctness trials=%u accepted=%u alias=pass noninvertible=pass\n",
		TRIALS, accepted);
	return accepted != 0 && prepare_invertible();
}

int main(int argc, char **argv)
{
	const unsigned iterations = argc > 1 ?
		(unsigned)strtoul(argv[1], NULL, 0) : 10000;
	const char *gate = argc > 2 ? argv[2] : "m3";
	const char *backend = argc > 3 ? argv[3] : "control";
	const int skip_check = argc > 4 && strcmp(argv[4], "nocheck") == 0;
	cpu_set_t set;
	CPU_ZERO(&set);
	CPU_SET(1, &set);
	(void)sched_setaffinity(0, sizeof set, &set);
	if ((!skip_check && !differential()) || (skip_check && !prepare_invertible()))
		return 1;

	region_fn function = NULL;
	const int candidate = strcmp(backend, "candidate") == 0;
	if (strcmp(gate, "m1") == 0)
		function = candidate ? m1_candidate : m1_control;
	else if (strcmp(gate, "m2") == 0)
		function = candidate ? m2_candidate : m2_control;
	else if (strcmp(gate, "m3") == 0)
		function = candidate ? m3_candidate : m3_control;
	else if (strcmp(gate, "mpack") == 0)
		function = candidate ? m_pack3 : p_pack3;
	else if (strcmp(gate, "m4") == 0)
		function = candidate ? m4_candidate : m4_control;
	else if (strcmp(gate, "p_suffix_k3k5") == 0)
		function = candidate ? p_suffix_k3k5_candidate : m4_control;
	else if (strcmp(gate, "p_suffix_f") == 0)
		function = candidate ? p_suffix_f_candidate : p_suffix_f_control;
	else if (strcmp(gate, "p_suffix_fbi") == 0)
		function = candidate ? p_suffix_fbi_candidate : p_suffix_fbi_control;
	else if (strcmp(gate, "p_suffix_bm") == 0)
		function = candidate ? p_suffix_bm_candidate : p_suffix_bm_control;
	if (function == NULL || (!candidate && strcmp(backend, "control") != 0))
		return 2;
	run(function, 100);
	const uint64_t ticks = timed(function, iterations);
	printf("MBASEINV_PMU,gate=%s,backend=%s,iterations=%u,correctness=pass,"
		"tsc_per_call=%.6f,sink=%llu\n", gate, backend, iterations,
		(double)ticks / iterations, (unsigned long long)sink);
	return 0;
}
