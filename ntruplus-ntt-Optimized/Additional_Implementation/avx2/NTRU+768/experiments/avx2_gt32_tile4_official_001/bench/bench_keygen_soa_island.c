#define _GNU_SOURCE
#include <sched.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <x86intrin.h>

#include "poly.h"
#include "symmetric.h"
#include "fips202/fips202.h"
#include "tile4.h"
#include "../generated/tile4_baseinv_p_mapping.h"

#define WORDS 768
#define POLYBYTES 1152
#define TRIALS 1000

extern void gt32_tile4_attr_forward_all_baseinv_p_l3_asm(int16_t *, const int16_t *);
extern int gt32_p_baseinv_direct_avx2(int16_t *, const int16_t *);
extern int gt32_p_baseinv_direct_asm_avx2(int16_t *, const int16_t *);
extern void gt_basemul_native_asm_avx2(int16_t *, const int16_t *, const int16_t *);
extern void gt32_q24_encode_p_soa_halfscatter_rr_lazy10788_asm(uint8_t *,
	const int16_t *);
extern void gt32_q24_encode_p_soa_halfscatter_tf1_lazy10788_asm(uint8_t *,
	const int16_t *);
extern void gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm(uint8_t *,
	const int16_t *);
extern void gt32_q24_encode_p_soa_pack3_tf1_compact_asm(
	uint8_t *, const int16_t *, uint8_t *, const int16_t *,
	uint8_t *, const int16_t *);

static poly seed_f __attribute__((aligned(64)));
static poly seed_g __attribute__((aligned(64)));
static poly of, og, ofin, ogin, oh, ohinv __attribute__((aligned(64)));
static int16_t frontend[WORDS] __attribute__((aligned(64)));
static int16_t gf[WORDS] __attribute__((aligned(64)));
static int16_t gg[WORDS] __attribute__((aligned(64)));
static int16_t gfin[WORDS] __attribute__((aligned(64)));
static int16_t ggin[WORDS] __attribute__((aligned(64)));
static int16_t gh[WORDS] __attribute__((aligned(64)));
static int16_t ghinv[WORDS] __attribute__((aligned(64)));
static uint8_t official_bytes[3][POLYBYTES] __attribute__((aligned(64)));
static uint8_t gt_bytes[3][POLYBYTES] __attribute__((aligned(64)));
static uint8_t coins_f[32], coins_g[32];
static uint8_t sample_buf[192] __attribute__((aligned(64)));
static uint8_t key_hash[32] __attribute__((aligned(64)));
static volatile uint64_t sink;
static uint32_t rng = 0x6c3305a1U;

static uint32_t random32(void) { rng ^= rng << 13; rng ^= rng >> 17; rng ^= rng << 5; return rng; }
static int center(int x) { x %= 3457; if (x < 0) x += 3457; if (x > 1728) x -= 3457; return x; }

static void gt_forward(int16_t out[WORDS], const int16_t in[WORDS])
{
	gt32_tile4_frontend_wide_raw_asm(frontend, in);
	gt32_tile4_attr_forward_all_baseinv_p_l3_asm(out, frontend);
}

static int same_output(const poly *official, const int16_t p[WORDS])
{
	for (unsigned i = 0; i < WORDS; i++)
		if (center(official->coeffs[gt32_official_word_from_serialized[i]]) !=
		    center(p[gt32_p_word_from_serialized[i]])) return 0;
	return 1;
}

__attribute__((noinline)) static void official_fbi(void)
{
	of = seed_f; og = seed_g; poly_ntt(&of); poly_ntt(&og);
	(void)poly_baseinv(&ofin, &of); (void)poly_baseinv(&ogin, &og);
}

__attribute__((noinline)) static void gt_fbi(void)
{
	gt_forward(gf, seed_f.coeffs); gt_forward(gg, seed_g.coeffs);
	(void)gt32_p_baseinv_direct_avx2(gfin, gf);
	(void)gt32_p_baseinv_direct_avx2(ggin, gg);
}

__attribute__((noinline)) static void gt_fbi_asm(void)
{
	gt_forward(gf, seed_f.coeffs); gt_forward(gg, seed_g.coeffs);
	(void)gt32_p_baseinv_direct_asm_avx2(gfin, gf);
	(void)gt32_p_baseinv_direct_asm_avx2(ggin, gg);
}

__attribute__((noinline)) static void official_consumer(void)
{
	poly_basemul(&oh, &og, &ofin); poly_basemul(&ohinv, &of, &ogin);
}

__attribute__((noinline)) static void gt_consumer(void)
{
	gt_basemul_native_asm_avx2(gh, gg, gfin);
	gt_basemul_native_asm_avx2(ghinv, gf, ggin);
}

__attribute__((noinline)) static void official_island(void)
{
	official_fbi(); official_consumer();
}

__attribute__((noinline)) static void gt_island(void)
{
	gt_fbi(); gt_consumer();
}

__attribute__((noinline)) static void gt_island_asm(void)
{
	gt_fbi_asm(); gt_consumer();
}

__attribute__((noinline)) static void official_pack3(void)
{
	poly_tobytes(official_bytes[0], &of);
	poly_tobytes(official_bytes[1], &oh);
	poly_tobytes(official_bytes[2], &ohinv);
}

__attribute__((noinline)) static void gt_pack3(void)
{
	gt32_q24_encode_p_soa_lazy10788_asm(gt_bytes[0], gf);
	gt32_q24_encode_p_soa_lazy10788_asm(gt_bytes[1], gh);
	gt32_q24_encode_p_soa_lazy10788_asm(gt_bytes[2], ghinv);
}

__attribute__((noinline)) static void gt_pack3_half(void)
{
	gt32_q24_encode_p_soa_halfscatter_lazy10788_asm(gt_bytes[0], gf);
	gt32_q24_encode_p_soa_halfscatter_lazy10788_asm(gt_bytes[1], gh);
	gt32_q24_encode_p_soa_halfscatter_lazy10788_asm(gt_bytes[2], ghinv);
}

__attribute__((noinline)) static void gt_pack3_half_rr(void)
{
	gt32_q24_encode_p_soa_halfscatter_rr_lazy10788_asm(gt_bytes[0], gf);
	gt32_q24_encode_p_soa_halfscatter_rr_lazy10788_asm(gt_bytes[1], gh);
	gt32_q24_encode_p_soa_halfscatter_rr_lazy10788_asm(gt_bytes[2], ghinv);
}

__attribute__((noinline)) static void gt_pack3_half_tf1(void)
{
	gt32_q24_encode_p_soa_halfscatter_tf1_lazy10788_asm(gt_bytes[0], gf);
	gt32_q24_encode_p_soa_halfscatter_tf1_lazy10788_asm(gt_bytes[1], gh);
	gt32_q24_encode_p_soa_halfscatter_tf1_lazy10788_asm(gt_bytes[2], ghinv);
}

__attribute__((noinline)) static void gt_pack3_half_sp1(void)
{
	gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm(gt_bytes[0], gf);
	gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm(gt_bytes[1], gh);
	gt32_q24_encode_p_soa_halfscatter_sp1_lazy10788_asm(gt_bytes[2], ghinv);
}

__attribute__((noinline)) static void gt_pack3_joint(void)
{
	gt32_q24_encode_p_soa_pack3_tf1_compact_asm(
		gt_bytes[0], gf, gt_bytes[1], gh, gt_bytes[2], ghinv);
}

__attribute__((noinline)) static void official_island_pack(void)
{
	official_island(); official_pack3();
}

__attribute__((noinline)) static void gt_island_pack(void)
{
	gt_island(); gt_pack3();
}

__attribute__((noinline)) static void gt_island_pack_half(void)
{
	gt_island(); gt_pack3_half();
}

__attribute__((noinline)) static void gt_island_pack_half_asm(void)
{
	gt_island_asm(); gt_pack3_half();
}

static void sample_inputs(void)
{
	shake256(sample_buf, sizeof sample_buf, coins_f, sizeof coins_f);
	poly_cbd1(&seed_f, sample_buf); poly_triple(&seed_f); seed_f.coeffs[0]++;
	shake256(sample_buf, sizeof sample_buf, coins_g, sizeof coins_g);
	poly_cbd1(&seed_g, sample_buf); poly_triple(&seed_g);
}

__attribute__((noinline)) static void official_full(void)
{
	sample_inputs(); official_island_pack(); hash_f(key_hash, official_bytes[1]);
}

__attribute__((noinline)) static void gt_full(void)
{
	sample_inputs(); gt_island_pack_half(); hash_f(key_hash, gt_bytes[1]);
}

__attribute__((noinline)) static void gt_full_asm(void)
{
	sample_inputs(); gt_island_pack_half_asm(); hash_f(key_hash, gt_bytes[1]);
}

typedef void (*region_fn)(void);
static void run(region_fn fn, unsigned iterations)
{
	for (unsigned i = 0; i < iterations; i++) fn();
	sink += (uint16_t)oh.coeffs[iterations % WORDS] + (uint16_t)gh[iterations % WORDS];
}

static uint64_t timed(region_fn fn, unsigned iterations)
{
	unsigned aux; _mm_lfence(); uint64_t begin = __rdtsc(); run(fn, iterations);
	uint64_t end = __rdtscp(&aux); _mm_lfence(); return end - begin;
}

static int differential(void)
{
	unsigned accepted = 0;
	poly good_f = {{0}}, good_g = {{0}};
	for (unsigned trial = 0; trial < TRIALS; trial++) {
		for (unsigned i = 0; i < WORDS; i++) {
			seed_f.coeffs[i] = (int16_t)((int)(random32() & 7U) - 3);
			seed_g.coeffs[i] = (int16_t)((int)(random32() & 7U) - 3);
		}
		of = seed_f; og = seed_g; poly_ntt(&of); poly_ntt(&og);
		int os0 = poly_baseinv(&ofin, &of), os1 = poly_baseinv(&ogin, &og);
		gt_forward(gf, seed_f.coeffs); gt_forward(gg, seed_g.coeffs);
		int gs0 = gt32_p_baseinv_direct_avx2(gfin, gf);
		int gs1 = gt32_p_baseinv_direct_avx2(ggin, gg);
		if (os0 != gs0 || os1 != gs1) return fprintf(stderr, "status mismatch %u\n", trial), 0;
		if (os0 == 0 && os1 == 0) {
			accepted++;
			good_f = seed_f; good_g = seed_g;
			poly_basemul(&oh, &og, &ofin); poly_basemul(&ohinv, &of, &ogin);
			gt_basemul_native_asm_avx2(gh, gg, gfin);
			gt_basemul_native_asm_avx2(ghinv, gf, ggin);
			if (!same_output(&oh, gh) || !same_output(&ohinv, ghinv))
				return fprintf(stderr, "BM mismatch %u\n", trial), 0;
			official_pack3(); gt_pack3();
			if (memcmp(official_bytes, gt_bytes, sizeof official_bytes) != 0)
				return fprintf(stderr, "pack mismatch %u\n", trial), 0;
			gt_pack3_half();
			if (memcmp(official_bytes, gt_bytes, sizeof official_bytes) != 0)
				return fprintf(stderr, "half-pack mismatch %u\n", trial), 0;
			gt_pack3_half_rr();
			if (memcmp(official_bytes, gt_bytes, sizeof official_bytes) != 0)
				return fprintf(stderr, "RR half-pack mismatch %u\n", trial), 0;
			gt_pack3_half_tf1();
			if (memcmp(official_bytes, gt_bytes, sizeof official_bytes) != 0)
				return fprintf(stderr, "TF1 half-pack mismatch %u\n", trial), 0;
			gt_pack3_half_sp1();
			if (memcmp(official_bytes, gt_bytes, sizeof official_bytes) != 0)
				return fprintf(stderr, "SP1 half-pack mismatch %u\n", trial), 0;
			gt_pack3_joint();
			if (memcmp(official_bytes, gt_bytes, sizeof official_bytes) != 0)
				return fprintf(stderr, "joint pack3 mismatch %u\n", trial), 0;
			gs0 = gt32_p_baseinv_direct_asm_avx2(gfin, gf);
			gs1 = gt32_p_baseinv_direct_asm_avx2(ggin, gg);
			if (os0 != gs0 || os1 != gs1)
				return fprintf(stderr, "asm status mismatch %u\n", trial), 0;
			gt_consumer();
			if (!same_output(&oh, gh) || !same_output(&ohinv, ghinv))
				return fprintf(stderr, "asm BM mismatch %u\n", trial), 0;
		}
	}
	printf("correctness trials=%u accepted=%u\n", TRIALS, accepted);
	if (accepted == 0) return 0;
	seed_f = good_f; seed_g = good_g;
	official_fbi(); gt_fbi();
	sample_inputs(); official_island_pack(); gt_island_pack_half();
	if (memcmp(official_bytes, gt_bytes, sizeof official_bytes) != 0)
		return fprintf(stderr, "full keygen bytes mismatch\n"), 0;
	return 1;
}

int main(int argc, char **argv)
{
	unsigned iterations = argc > 1 ? (unsigned)strtoul(argv[1], 0, 0) : 10000;
	const char *gate = argc > 2 ? argv[2] : "island";
	const char *backend = argc > 3 ? argv[3] : "official";
	int half = !strcmp(backend, "gt32-half");
	int rr = !strcmp(backend, "gt32-rr");
	int tf1 = !strcmp(backend, "gt32-tf1");
	int sp1 = !strcmp(backend, "gt32-sp1");
	int pack3 = !strcmp(backend, "gt32-pack3");
	int asm_backend = !strcmp(backend, "gt32-asm");
	int skip_check = argc > 4 && !strcmp(argv[4], "nocheck");
	cpu_set_t set; CPU_ZERO(&set); CPU_SET(1, &set); (void)sched_setaffinity(0, sizeof set, &set);
	for (unsigned i = 0; i < sizeof coins_f; i++) {
		coins_f[i] = (uint8_t)(0x31U + 7U * i);
		coins_g[i] = (uint8_t)(0xa7U - 3U * i);
	}
	if (!skip_check) {
		if (!differential()) return 1;
	} else {
		/* Deterministic, known-small inputs; prepare both consumer states. */
		for (unsigned i = 0; i < WORDS; i++) {
			seed_f.coeffs[i] = (int16_t)((int)((i * 5U + 1U) & 7U) - 3);
			seed_g.coeffs[i] = (int16_t)((int)((i * 3U + 2U) & 7U) - 3);
		}
		official_island();
		if (asm_backend) gt_island_asm(); else gt_island();
	}
	/* differential leaves an invertible pair in the seed and prepared states */
	region_fn fn = 0;
	if (!strcmp(gate, "fbi")) fn = !strcmp(backend, "official") ? official_fbi : (asm_backend ? gt_fbi_asm : gt_fbi);
	else if (!strcmp(gate, "consumer")) fn = !strcmp(backend, "official") ? official_consumer : gt_consumer;
	else if (!strcmp(gate, "island")) fn = !strcmp(backend, "official") ? official_island : (asm_backend ? gt_island_asm : gt_island);
	else if (!strcmp(gate, "pack")) fn = !strcmp(backend, "official") ? official_pack3 : (pack3 ? gt_pack3_joint : sp1 ? gt_pack3_half_sp1 : tf1 ? gt_pack3_half_tf1 : rr ? gt_pack3_half_rr : half ? gt_pack3_half : gt_pack3);
	else if (!strcmp(gate, "island-pack")) fn = !strcmp(backend, "official") ? official_island_pack : (asm_backend ? gt_island_pack_half_asm : (half ? gt_island_pack_half : gt_island_pack));
	else if (!strcmp(gate, "full")) fn = !strcmp(backend, "official") ? official_full : (asm_backend ? gt_full_asm : gt_full);
	if (!fn || (strcmp(backend, "official") && strcmp(backend, "gt32-soa") && !half && !rr && !tf1 && !sp1 && !pack3 && !asm_backend)) return 2;
	run(fn, 1000); uint64_t ticks = timed(fn, iterations);
	printf("KSOA_PMU,gate=%s,backend=%s,iterations=%u,correctness=pass,tsc_per_call=%.6f,sink=%llu\n",
		gate, backend, iterations, (double)ticks / iterations, (unsigned long long)sink);
	return 0;
}
