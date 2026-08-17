#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <x86intrin.h>

#include "api.h"
#include "fips202/fips202.h"
#include "poly.h"
#include "symmetric.h"
#include "tile4.h"
#include "util.h"

#define WORDS NTRUPLUS_N
#define SAMPLE_BYTES (NTRUPLUS_N / 4)
#define STREAM_SCENARIOS 1024U
#define STREAM_CANDIDATES 32U

extern void gt32_tile4_attr_forward_all_baseinv_p_l3_asm(int16_t *,
	const int16_t *);
extern int gt32_p_baseinv_direct_avx2(int16_t *, const int16_t *);
extern int gt32_p_j1_baseinv_direct_avx2(int16_t *, const int16_t *);
extern int gt32_p_j1_c_baseinv_direct_avx2(int16_t *, const int16_t *);
extern void gt_basemul_native_asm_avx2(int16_t *, const int16_t *,
	const int16_t *);
extern void gt_basemul_native_f0_j1_e0_asm_avx2(int16_t *, const int16_t *,
	const int16_t *);
extern void gt32_q24_encode_p_soa_halfscatter_tf1_lazy10788_asm(uint8_t *,
	const int16_t *);
extern void gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm(uint8_t *,
	const int16_t *);

typedef void (*gt_pack_fn)(uint8_t *, const int16_t *);
static gt_pack_fn gt_pack_selected =
	gt32_q24_encode_p_soa_halfscatter_lazy10788_asm;
static int gt_use_p_j1;
static int gt_use_p_j1_c;

typedef struct __attribute__((aligned(64))) {
	uint8_t sample[SAMPLE_BYTES];
	poly f;
	poly finv;
	poly g;
	poly ginv;
	poly h;
} official_scratch_t;

typedef struct __attribute__((aligned(64))) {
	uint8_t sample[SAMPLE_BYTES];
	poly coeff;
	int16_t frontend[WORDS];
	int16_t f[WORDS];
	int16_t finv[WORDS];
	int16_t g[WORDS];
	int16_t ginv[WORDS];
	int16_t h[WORDS];
} gt_scratch_t;

typedef struct {
	unsigned f;
	unsigned g;
} retry_count_t;

static uint8_t stream[STREAM_SCENARIOS][STREAM_CANDIDATES][NTRUPLUS_SYMBYTES];
static uint8_t g1_f_coins[NTRUPLUS_SYMBYTES];
static uint8_t g1_g_coins[NTRUPLUS_SYMBYTES];
static uint8_t pk[NTRUPLUS_PUBLICKEYBYTES] __attribute__((aligned(64)));
static uint8_t sk[NTRUPLUS_SECRETKEYBYTES] __attribute__((aligned(64)));
static official_scratch_t official_global_scratch;
static gt_scratch_t gt_global_scratch;
static volatile uint64_t sink;
static uint64_t total_retry_f;
static uint64_t total_retry_g;
static unsigned scenario_cursor;
static volatile unsigned cumulative_limit;

static void gt_forward(int16_t out[WORDS], int16_t frontend[WORDS],
	const int16_t in[WORDS])
{
	gt32_tile4_frontend_wide_raw_asm(frontend, in);
	gt32_tile4_attr_forward_all_baseinv_p_l3_asm(out, frontend);
}

static int official_attempt(official_scratch_t *s, int is_f,
	const uint8_t coins[NTRUPLUS_SYMBYTES])
{
	poly *a = is_f ? &s->f : &s->g;
	poly *ainv = is_f ? &s->finv : &s->ginv;
	shake256(s->sample, sizeof s->sample, coins, NTRUPLUS_SYMBYTES);
	poly_cbd1(a, s->sample);
	poly_triple(a);
	if (is_f)
		a->coeffs[0]++;
	poly_ntt(a);
	return poly_baseinv(ainv, a);
}

static int gt_attempt(gt_scratch_t *s, int is_f,
	const uint8_t coins[NTRUPLUS_SYMBYTES])
{
	int16_t *a = is_f ? s->f : s->g;
	int16_t *ainv = is_f ? s->finv : s->ginv;
	shake256(s->sample, sizeof s->sample, coins, NTRUPLUS_SYMBYTES);
	poly_cbd1(&s->coeff, s->sample);
	poly_triple(&s->coeff);
	if (is_f)
		s->coeff.coeffs[0]++;
	gt_forward(a, s->frontend, s->coeff.coeffs);
	return gt_use_p_j1_c ? gt32_p_j1_c_baseinv_direct_avx2(ainv, a)
		: gt_use_p_j1 ? gt32_p_j1_baseinv_direct_avx2(ainv, a)
		: gt32_p_baseinv_direct_avx2(ainv, a);
}

static void official_edge0(official_scratch_t *s, uint8_t *out_pk)
{
	poly_basemul(&s->h, &s->g, &s->finv);
	poly_tobytes(out_pk, &s->h);
}

static void official_edge1(official_scratch_t *s, uint8_t *out_sk)
{
	poly_basemul(&s->h, &s->f, &s->ginv);
	poly_tobytes(out_sk, &s->f);
	poly_tobytes(out_sk + NTRUPLUS_POLYBYTES, &s->h);
}

static void official_finish(official_scratch_t *s, uint8_t *out_pk,
	uint8_t *out_sk)
{
	official_edge0(s, out_pk);
	official_edge1(s, out_sk);
	hash_f(out_sk + 2 * NTRUPLUS_POLYBYTES, out_pk);
}

static void gt_edge0(gt_scratch_t *s, uint8_t *out_pk)
{
	if (gt_use_p_j1)
		gt_basemul_native_f0_j1_e0_asm_avx2(s->h, s->g, s->finv);
	else
		gt_basemul_native_asm_avx2(s->h, s->g, s->finv);
	gt_pack_selected(out_pk, s->h);
}

static void gt_edge1(gt_scratch_t *s, uint8_t *out_sk)
{
	gt_pack_selected(out_sk, s->f);
	if (gt_use_p_j1)
		gt_basemul_native_f0_j1_e0_asm_avx2(s->h, s->f, s->ginv);
	else
		gt_basemul_native_asm_avx2(s->h, s->f, s->ginv);
	gt_pack_selected(
		out_sk + NTRUPLUS_POLYBYTES, s->h);
}

static void gt_finish(gt_scratch_t *s, uint8_t *out_pk, uint8_t *out_sk)
{
	gt_edge0(s, out_pk);
	gt_edge1(s, out_sk);
	hash_f(out_sk + 2 * NTRUPLUS_POLYBYTES, out_pk);
}

__attribute__((noinline)) static retry_count_t official_g1(uint8_t *out_pk,
	uint8_t *out_sk)
{
	official_scratch_t s;
	retry_count_t count = {1, 1};
	int status = official_attempt(&s, 1, g1_f_coins);
	status |= official_attempt(&s, 0, g1_g_coins);
	if (status == 0)
		official_finish(&s, out_pk, out_sk);
	secure_clear(&s, sizeof s);
	sink += (unsigned)status;
	return count;
}

__attribute__((noinline)) static retry_count_t gt_g1(uint8_t *out_pk,
	uint8_t *out_sk)
{
	gt_scratch_t s;
	retry_count_t count = {1, 1};
	int status = gt_attempt(&s, 1, g1_f_coins);
	status |= gt_attempt(&s, 0, g1_g_coins);
	if (status == 0)
		gt_finish(&s, out_pk, out_sk);
	secure_clear(&s, sizeof s);
	sink += (unsigned)status;
	return count;
}

__attribute__((noinline)) static retry_count_t official_g1_noclear(
	uint8_t *out_pk, uint8_t *out_sk)
{
	official_scratch_t s;
	retry_count_t count = {1, 1};
	int status = official_attempt(&s, 1, g1_f_coins);
	status |= official_attempt(&s, 0, g1_g_coins);
	if (status == 0)
		official_finish(&s, out_pk, out_sk);
	sink += (unsigned)status;
	return count;
}

__attribute__((noinline)) static retry_count_t gt_g1_noclear(uint8_t *out_pk,
	uint8_t *out_sk)
{
	gt_scratch_t s;
	retry_count_t count = {1, 1};
	int status = gt_attempt(&s, 1, g1_f_coins);
	status |= gt_attempt(&s, 0, g1_g_coins);
	if (status == 0)
		gt_finish(&s, out_pk, out_sk);
	sink += (unsigned)status;
	return count;
}

__attribute__((noinline)) static retry_count_t official_g1_global(
	uint8_t *out_pk, uint8_t *out_sk)
{
	retry_count_t count = {1, 1};
	int status = official_attempt(&official_global_scratch, 1, g1_f_coins);
	status |= official_attempt(&official_global_scratch, 0, g1_g_coins);
	if (status == 0)
		official_finish(&official_global_scratch, out_pk, out_sk);
	secure_clear(&official_global_scratch, sizeof official_global_scratch);
	sink += (unsigned)status;
	return count;
}

__attribute__((noinline)) static retry_count_t gt_g1_global(uint8_t *out_pk,
	uint8_t *out_sk)
{
	retry_count_t count = {1, 1};
	int status = gt_attempt(&gt_global_scratch, 1, g1_f_coins);
	status |= gt_attempt(&gt_global_scratch, 0, g1_g_coins);
	if (status == 0)
		gt_finish(&gt_global_scratch, out_pk, out_sk);
	secure_clear(&gt_global_scratch, sizeof gt_global_scratch);
	sink += (unsigned)status;
	return count;
}

__attribute__((noinline)) static retry_count_t official_g1_global_noclear(
	uint8_t *out_pk, uint8_t *out_sk)
{
	retry_count_t count = {1, 1};
	int status = official_attempt(&official_global_scratch, 1, g1_f_coins);
	status |= official_attempt(&official_global_scratch, 0, g1_g_coins);
	if (status == 0)
		official_finish(&official_global_scratch, out_pk, out_sk);
	sink += (unsigned)status;
	return count;
}

__attribute__((noinline)) static retry_count_t gt_g1_global_noclear(
	uint8_t *out_pk, uint8_t *out_sk)
{
	retry_count_t count = {1, 1};
	int status = gt_attempt(&gt_global_scratch, 1, g1_f_coins);
	status |= gt_attempt(&gt_global_scratch, 0, g1_g_coins);
	if (status == 0)
		gt_finish(&gt_global_scratch, out_pk, out_sk);
	sink += (unsigned)status;
	return count;
}

__attribute__((noinline)) static retry_count_t official_cumulative(
	uint8_t *out_pk, uint8_t *out_sk)
{
	official_scratch_t s;
	retry_count_t count = {1, 0};
	int status = official_attempt(&s, 1, g1_f_coins);
	if (cumulative_limit >= 2U) {
		count.g = 1;
		status |= official_attempt(&s, 0, g1_g_coins);
	}
	if (cumulative_limit >= 3U)
		official_edge0(&s, out_pk);
	if (cumulative_limit >= 4U)
		official_edge1(&s, out_sk);
	if (cumulative_limit >= 5U)
		hash_f(out_sk + 2 * NTRUPLUS_POLYBYTES, out_pk);
	if (cumulative_limit >= 6U)
		secure_clear(&s, sizeof s);
	sink += (unsigned)status + out_pk[0];
	return count;
}

__attribute__((noinline)) static retry_count_t gt_cumulative(uint8_t *out_pk,
	uint8_t *out_sk)
{
	gt_scratch_t s;
	retry_count_t count = {1, 0};
	int status = gt_attempt(&s, 1, g1_f_coins);
	if (cumulative_limit >= 2U) {
		count.g = 1;
		status |= gt_attempt(&s, 0, g1_g_coins);
	}
	if (cumulative_limit >= 3U)
		gt_edge0(&s, out_pk);
	if (cumulative_limit >= 4U)
		gt_edge1(&s, out_sk);
	if (cumulative_limit >= 5U)
		hash_f(out_sk + 2 * NTRUPLUS_POLYBYTES, out_pk);
	if (cumulative_limit >= 6U)
		secure_clear(&s, sizeof s);
	sink += (unsigned)status + out_pk[0];
	return count;
}

__attribute__((noinline)) static retry_count_t official_g2(uint8_t *out_pk,
	uint8_t *out_sk, unsigned scenario)
{
	official_scratch_t s;
	retry_count_t count = {0, 0};
	unsigned next = 0;
	int status;
	do {
		if (next == STREAM_CANDIDATES)
			abort();
		count.f++;
		status = official_attempt(&s, 1, stream[scenario][next++]);
	} while (status != 0);
	do {
		if (next == STREAM_CANDIDATES)
			abort();
		count.g++;
		status = official_attempt(&s, 0, stream[scenario][next++]);
	} while (status != 0);
	official_finish(&s, out_pk, out_sk);
	secure_clear(&s, sizeof s);
	return count;
}

__attribute__((noinline)) static retry_count_t gt_g2(uint8_t *out_pk,
	uint8_t *out_sk, unsigned scenario)
{
	gt_scratch_t s;
	retry_count_t count = {0, 0};
	unsigned next = 0;
	int status;
	do {
		if (next == STREAM_CANDIDATES)
			abort();
		count.f++;
		status = gt_attempt(&s, 1, stream[scenario][next++]);
	} while (status != 0);
	do {
		if (next == STREAM_CANDIDATES)
			abort();
		count.g++;
		status = gt_attempt(&s, 0, stream[scenario][next++]);
	} while (status != 0);
	gt_finish(&s, out_pk, out_sk);
	secure_clear(&s, sizeof s);
	return count;
}

typedef retry_count_t (*g1_fn)(uint8_t *, uint8_t *);
typedef retry_count_t (*g2_fn)(uint8_t *, uint8_t *, unsigned);

static void run_g1(g1_fn fn, unsigned iterations)
{
	for (unsigned i = 0; i < iterations; i++) {
		retry_count_t count = fn(pk, sk);
		total_retry_f += count.f;
		total_retry_g += count.g;
		sink += pk[i % sizeof pk] + sk[i % sizeof sk];
	}
}

static void run_g2(g2_fn fn, unsigned iterations)
{
	for (unsigned i = 0; i < iterations; i++) {
		unsigned scenario = scenario_cursor++ % STREAM_SCENARIOS;
		retry_count_t count = fn(pk, sk, scenario);
		total_retry_f += count.f;
		total_retry_g += count.g;
		sink += pk[i % sizeof pk] + sk[i % sizeof sk];
	}
}

static uint64_t timed_g1(g1_fn fn, unsigned iterations)
{
	unsigned aux;
	_mm_lfence();
	uint64_t begin = __rdtsc();
	run_g1(fn, iterations);
	uint64_t end = __rdtscp(&aux);
	_mm_lfence();
	return end - begin;
}

static uint64_t timed_g2(g2_fn fn, unsigned iterations)
{
	unsigned aux;
	_mm_lfence();
	uint64_t begin = __rdtsc();
	run_g2(fn, iterations);
	uint64_t end = __rdtscp(&aux);
	_mm_lfence();
	return end - begin;
}

static uint32_t next32(uint32_t *state)
{
	*state ^= *state << 13;
	*state ^= *state >> 17;
	*state ^= *state << 5;
	return *state;
}

static void initialize_stream(void)
{
	uint32_t state = 0x6f2384b1U;
	for (unsigned s = 0; s < STREAM_SCENARIOS; s++)
		for (unsigned c = 0; c < STREAM_CANDIDATES; c++)
			for (unsigned i = 0; i < NTRUPLUS_SYMBYTES; i++)
				stream[s][c][i] = (uint8_t)next32(&state);
}

static int select_g1_coins(void)
{
	official_scratch_t os;
	gt_scratch_t gs;
	unsigned selected = 0;
	for (unsigned s = 0; s < STREAM_SCENARIOS && selected < 2; s++) {
		for (unsigned c = 0; c < STREAM_CANDIDATES && selected < 2; c++) {
			int is_f = selected == 0;
			int official_status = official_attempt(&os, is_f, stream[s][c]);
			int gt_status = gt_attempt(&gs, is_f, stream[s][c]);
			if (official_status != gt_status)
				return fprintf(stderr, "attempt status mismatch\n"), 0;
			if (official_status == 0) {
				memcpy(selected == 0 ? g1_f_coins : g1_g_coins,
					stream[s][c], NTRUPLUS_SYMBYTES);
				selected++;
			}
		}
	}
	secure_clear(&os, sizeof os);
	secure_clear(&gs, sizeof gs);
	if (selected != 2)
		return fprintf(stderr, "could not select G1 coins\n"), 0;
	return 1;
}

static int differential(void)
{
	uint8_t official_pk[NTRUPLUS_PUBLICKEYBYTES];
	uint8_t official_sk[NTRUPLUS_SECRETKEYBYTES];
	uint8_t gt_pk[NTRUPLUS_PUBLICKEYBYTES];
	uint8_t gt_sk[NTRUPLUS_SECRETKEYBYTES];
	official_scratch_t fail_os;
	gt_scratch_t fail_gs;
	memset(&fail_os, 0, sizeof fail_os);
	memset(&fail_gs, 0, sizeof fail_gs);
	poly_ntt(&fail_os.g);
	gt_forward(fail_gs.g, fail_gs.frontend, fail_gs.coeff.coeffs);
	int official_failure = poly_baseinv(&fail_os.ginv, &fail_os.g);
	int gt_failure = gt32_p_baseinv_direct_avx2(fail_gs.ginv, fail_gs.g);
	if (official_failure == 0 || gt_failure == 0
		|| official_failure != gt_failure)
		return fprintf(stderr, "noninvertible failure mismatch\n"), 0;
	for (unsigned i = 0; i < WORDS; i++)
		if (fail_os.ginv.coeffs[i] != 0 || fail_gs.ginv[i] != 0)
			return fprintf(stderr, "noninvertible zero mismatch\n"), 0;
	secure_clear(&fail_os, sizeof fail_os);
	secure_clear(&fail_gs, sizeof fail_gs);

	retry_count_t oc = official_g1(official_pk, official_sk);
	retry_count_t gc = gt_g1(gt_pk, gt_sk);
	if (oc.f != gc.f || oc.g != gc.g
		|| memcmp(official_pk, gt_pk, sizeof official_pk) != 0
		|| memcmp(official_sk, gt_sk, sizeof official_sk) != 0)
		return fprintf(stderr, "G1 differential failed\n"), 0;

	uint64_t retries_f = 0;
	uint64_t retries_g = 0;
	unsigned multi_retry = 0;
	for (unsigned scenario = 0; scenario < STREAM_SCENARIOS; scenario++) {
		oc = official_g2(official_pk, official_sk, scenario);
		gc = gt_g2(gt_pk, gt_sk, scenario);
		if (oc.f != gc.f || oc.g != gc.g
			|| memcmp(official_pk, gt_pk, sizeof official_pk) != 0
			|| memcmp(official_sk, gt_sk, sizeof official_sk) != 0)
			return fprintf(stderr, "G2 differential failed scenario=%u\n",
				scenario), 0;
		retries_f += oc.f;
		retries_g += oc.g;
		multi_retry += oc.f > 1 || oc.g > 1;
	}
	printf("correctness=pass scenarios=%u multi_retry=%u retry_f=%llu "
		"retry_g=%llu\n", STREAM_SCENARIOS, multi_retry,
		(unsigned long long)retries_f, (unsigned long long)retries_g);
	return 1;
}

int main(int argc, char **argv)
{
	unsigned iterations = argc > 1 ? (unsigned)strtoul(argv[1], NULL, 10)
		: 1000U;
	const char *gate = argc > 2 ? argv[2] : "g1";
	const char *backend = argc > 3 ? argv[3] : "official";
	if (strcmp(backend, "gt32-tf1") == 0)
		gt_pack_selected =
			gt32_q24_encode_p_soa_halfscatter_tf1_lazy10788_asm;
	else if (strcmp(backend, "gt32-sp1") == 0)
		gt_pack_selected =
			gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm;
	gt_use_p_j1 = strcmp(backend, "gt32-p-j1") == 0 ||
		strcmp(backend, "gt32-p-j1-c") == 0;
	gt_use_p_j1_c = strcmp(backend, "gt32-p-j1-c") == 0;
	if (gt_use_p_j1)
		gt_pack_selected =
			gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm;
	int skip_check = argc > 4 && strcmp(argv[4], "nocheck") == 0;
	cpu_set_t set;
	CPU_ZERO(&set);
	CPU_SET(1, &set);
	(void)sched_setaffinity(0, sizeof set, &set);
	initialize_stream();
	if (!select_g1_coins())
		return 1;
	if (!skip_check && !differential())
		return 1;
	total_retry_f = 0;
	total_retry_g = 0;
	scenario_cursor = 0;
	uint64_t ticks;
	if (gate[0] == 'c' && gate[1] >= '1' && gate[1] <= '6'
		&& gate[2] == '\0') {
		cumulative_limit = (unsigned)(gate[1] - '0');
		g1_fn fn = strcmp(backend, "official") == 0
			? official_cumulative : gt_cumulative;
		run_g1(fn, 64);
		total_retry_f = total_retry_g = 0;
		ticks = timed_g1(fn, iterations);
	} else if (strcmp(gate, "g1") == 0 || strcmp(gate, "g1-noclear") == 0
		|| strcmp(gate, "g1-global") == 0
		|| strcmp(gate, "g1-global-noclear") == 0) {
		int no_clear = strcmp(gate, "g1-noclear") == 0;
		int global = strcmp(gate, "g1-global") == 0;
		int global_noclear = strcmp(gate, "g1-global-noclear") == 0;
		g1_fn fn = strcmp(backend, "official") == 0
			? (global_noclear ? official_g1_global_noclear
				: global ? official_g1_global
				: no_clear ? official_g1_noclear : official_g1)
			: (global_noclear ? gt_g1_global_noclear
				: global ? gt_g1_global
				: no_clear ? gt_g1_noclear : gt_g1);
		run_g1(fn, 64);
		total_retry_f = total_retry_g = 0;
		ticks = timed_g1(fn, iterations);
	} else if (strcmp(gate, "g2") == 0) {
		g2_fn fn = strcmp(backend, "official") == 0 ? official_g2 : gt_g2;
		run_g2(fn, 64);
		total_retry_f = total_retry_g = 0;
		scenario_cursor = 0;
		ticks = timed_g2(fn, iterations);
	} else {
		return 2;
	}
	printf("KPROD_PMU,gate=%s,backend=%s,iterations=%u,correctness=pass,"
		"tsc_per_call=%.6f,retry_f=%.6f,retry_g=%.6f,sink=%llu\n",
		gate, backend, iterations, (double)ticks / iterations,
		(double)total_retry_f / iterations,
		(double)total_retry_g / iterations, (unsigned long long)sink);
	return 0;
}
