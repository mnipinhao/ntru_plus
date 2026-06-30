#include <stdint.h>
#include <stdio.h>
#include <string.h>

#ifndef TEST_LOOP_COUNT
#define TEST_LOOP_COUNT 20000
#endif

#include "api.h"
#include "params.h"
#include "poly.h"
#include "symmetric.h"
#include "test/counter.h"

#ifdef GT_PRODUCTION_USE_RMINUS1_DECAP
void poly_basemul_rminus1(poly *r, const poly *a, const poly *b);
void poly_invntt_from_rminus1(poly *r, const poly *a);
#endif

#ifdef GT_PRODUCTION_USE_RMINUS1_CREP3_DECAP
void poly_basemul_rminus1(poly *r, const poly *a, const poly *b);
void poly_invntt_from_rminus1_crepmod3(poly *r, const poly *a);
#endif

#ifdef GT_PRODUCTION_USE_RMINUS1_STAGE123SCRATCH_CREP3_DECAP
void poly_basemul_rminus1_to_stage123scratch(int16_t *scratch,
                                             const poly *a,
                                             const poly *b);
void poly_invntt_from_rminus1_crepmod3_stage45scratch(
    poly *r, const int16_t *scratch);
#endif

#ifdef GT_PRODUCTION_USE_RMINUS1_STAGE123SCRATCH_DECAP
void poly_basemul_rminus1_to_stage123scratch(int16_t *scratch,
                                             const poly *a,
                                             const poly *b);
void poly_invntt_from_rminus1_stage45scratch(poly *r,
                                             const int16_t *scratch);
#endif

#ifdef GT_PRODUCTION_USE_TUPLE_DECAP
void poly_basemul_to_tuple(poly *r, const poly *a, const poly *b);
void gt_tuple_poly_invntt(poly *r, const poly *a);
#endif

#ifdef GT_PRODUCTION_USE_PACK_TUPLE_DECAP
void gt_tuple_poly_invntt(poly *r, const poly *a);

static int gt_pack_block_major_index(int branch, int physical_j, int lane)
{
	return branch * 384 + 4 * physical_j + lane;
}

static int gt_pack_tuple_index(int branch, int row, int k32, int lane)
{
	return branch * 384 + row * 128 + 4 * k32 + lane;
}

static int gt_pack_tuple_physical_j(int row, int k32)
{
	return (32 * row + 3 * k32) % 96;
}

static void gt_block_major_to_tuple_c(poly *tuple,
                                      const poly *block_major)
{
	for (int branch = 0; branch < 2; branch++)
		for (int row = 0; row < 3; row++)
			for (int k32 = 0; k32 < 32; k32++) {
				const int physical_j = gt_pack_tuple_physical_j(row, k32);

				for (int lane = 0; lane < 4; lane++) {
					const int tuple_idx =
					    gt_pack_tuple_index(branch, row, k32, lane);
					const int block_idx =
					    gt_pack_block_major_index(branch, physical_j,
					                              lane);

					tuple->coeffs[tuple_idx] =
					    block_major->coeffs[block_idx];
				}
			}
}
#endif

#ifdef GT_PRODUCTION_USE_SCALED_KEYPAIR
int poly_baseinv_scaled_r(poly *r, const poly *a);
void poly_basemul_scaled_r_input(poly *r, const poly *a,
                                 const poly *b_scaled_r);
#define KEYPAIR_BASEINV poly_baseinv_scaled_r
#define KEYPAIR_BASEMUL poly_basemul_scaled_r_input
#else
#define KEYPAIR_BASEINV poly_baseinv
#define KEYPAIR_BASEMUL poly_basemul
#endif

#ifdef SUPPORTS_SHAKE256_ASM
#include "CE/fips202.h"
#else
#include "NO_CE/fips202.h"
#endif

#ifndef KEM_COMPONENT_PROFILE_TARGET
#define KEM_COMPONENT_PROFILE_TARGET "unknown"
#endif

#if defined(__aarch64__)
#define COUNTER_UNIT_STR "ticks"
#elif defined(__x86_64__) || defined(__i386__)
#define COUNTER_UNIT_STR "cycles"
#else
#error "counter unsupported on this architecture"
#endif

static volatile uint32_t profile_sink;

static unsigned long long adjusted_ticks(unsigned long long start,
                                         unsigned long long end)
{
	unsigned long long elapsed = end - start;

	if (elapsed <= countergap)
		return 0;
	return elapsed - countergap;
}

static void fill_bytes(uint8_t *out, size_t len, uint32_t seed)
{
	uint32_t x = seed ? seed : 1;

	for (size_t i = 0; i < len; i++)
	{
		x = x * 1664525u + 1013904223u;
		out[i] = (uint8_t)(x >> 24);
	}
}

static uint8_t ct_verify(const uint8_t *a, const uint8_t *b, size_t len)
{
	uint8_t acc = 0;

	for (size_t i = 0; i < len; i++)
		acc |= (uint8_t)(a[i] ^ b[i]);

	return (uint8_t)((-(uint64_t)acc) >> 63);
}

static int genf_derand_profile(poly *f, poly *finv, const uint8_t *coins)
{
	uint8_t buf[NTRUPLUS_N / 4];

	shake256(buf, sizeof buf, coins, NTRUPLUS_SYMBYTES);

	poly_cbd1(f, buf);
	poly_triple(f, f);
	f->coeffs[0] += 1;

	poly_ntt(f, f);
	return KEYPAIR_BASEINV(finv, f);
}

static int geng_derand_profile(poly *g, poly *ginv, const uint8_t *coins)
{
	uint8_t buf[NTRUPLUS_N / 4];

	shake256(buf, sizeof buf, coins, NTRUPLUS_SYMBYTES);

	poly_cbd1(g, buf);
	poly_triple(g, g);

	poly_ntt(g, g);
	return KEYPAIR_BASEINV(ginv, g);
}

static void keypair_derand_profile(uint8_t *pk, uint8_t *sk,
                                   const uint8_t *fcoins,
                                   const uint8_t *gcoins)
{
	poly f, finv;
	poly g, ginv;
	poly h, hinv;

	if (genf_derand_profile(&f, &finv, fcoins) != 0)
	{
		printf("profiler setup error: fcoins not invertible\n");
		return;
	}
	if (geng_derand_profile(&g, &ginv, gcoins) != 0)
	{
		printf("profiler setup error: gcoins not invertible\n");
		return;
	}

	KEYPAIR_BASEMUL(&h, &g, &finv);
	KEYPAIR_BASEMUL(&hinv, &f, &ginv);

	poly_tobytes(pk, &h);
	poly_tobytes(sk, &f);
	poly_tobytes(sk + NTRUPLUS_POLYBYTES, &hinv);
	hash_f(sk + 2 * NTRUPLUS_POLYBYTES, pk);
}

static void enc_derand_profile(uint8_t *ct, uint8_t *ss, const uint8_t *pk,
                               const uint8_t *coins)
{
	uint8_t msg[NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES];
	uint8_t buf1[NTRUPLUS_SYMBYTES + NTRUPLUS_N / 4];
	uint8_t buf2[NTRUPLUS_POLYBYTES];
	poly c, h, r, m;

	for (size_t i = 0; i < NTRUPLUS_N / 8; i++)
		msg[i] = coins[i];

	hash_f(msg + NTRUPLUS_N / 8, pk);
	hash_h(buf1, msg);

	poly_cbd1(&r, buf1 + NTRUPLUS_SYMBYTES);
	poly_ntt(&r, &r);

	poly_tobytes(buf2, &r);
	hash_g(buf2, buf2);
	poly_sotp_encode(&m, msg, buf2);
	poly_ntt(&m, &m);

	poly_frombytes(&h, pk);
	poly_basemul_add(&c, &h, &r, &m);
	poly_tobytes(ct, &c);

	for (size_t i = 0; i < NTRUPLUS_SSBYTES; i++)
		ss[i] = buf1[i];
}

static int dec_profile(uint8_t *ss, const uint8_t *ct, const uint8_t *sk)
{
	uint8_t msg[NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES];
	uint8_t buf1[NTRUPLUS_POLYBYTES];
	uint8_t buf2[NTRUPLUS_POLYBYTES];
	uint8_t buf3[NTRUPLUS_POLYBYTES + NTRUPLUS_SYMBYTES];
	uint8_t fail;
	poly c, f, hinv;
	poly r1, r2;
	poly m1, m2;

	poly_frombytes(&c, ct);
	poly_frombytes(&f, sk);
	poly_frombytes(&hinv, sk + NTRUPLUS_POLYBYTES);

#ifdef GT_PRODUCTION_USE_RMINUS1_STAGE123SCRATCH_CREP3_DECAP
	poly_basemul_rminus1_to_stage123scratch(m1.coeffs, &c, &f);
	poly_invntt_from_rminus1_crepmod3_stage45scratch(&m1, m1.coeffs);
#elif defined(GT_PRODUCTION_USE_RMINUS1_CREP3_DECAP)
	poly_basemul_rminus1(&m1, &c, &f);
	poly_invntt_from_rminus1_crepmod3(&m1, &m1);
#elif defined(GT_PRODUCTION_USE_RMINUS1_STAGE123SCRATCH_DECAP)
	poly_basemul_rminus1_to_stage123scratch(m1.coeffs, &c, &f);
	poly_invntt_from_rminus1_stage45scratch(&m1, m1.coeffs);
#elif defined(GT_PRODUCTION_USE_RMINUS1_DECAP)
	poly_basemul_rminus1(&m1, &c, &f);
	poly_invntt_from_rminus1(&m1, &m1);
#elif defined(GT_PRODUCTION_USE_TUPLE_DECAP)
	poly_basemul_to_tuple(&m1, &c, &f);
	gt_tuple_poly_invntt(&m1, &m1);
#elif defined(GT_PRODUCTION_USE_PACK_TUPLE_DECAP)
	poly_basemul(&m1, &c, &f);
	gt_block_major_to_tuple_c(&m2, &m1);
	gt_tuple_poly_invntt(&m1, &m2);
#else
	poly_basemul(&m1, &c, &f);
	poly_invntt(&m1, &m1);
#endif
#if !defined(GT_PRODUCTION_USE_RMINUS1_CREP3_DECAP) && \
	!defined(GT_PRODUCTION_USE_RMINUS1_STAGE123SCRATCH_CREP3_DECAP)
	poly_crepmod3(&m1, &m1);
#endif

	poly_ntt(&m2, &m1);
	poly_sub(&c, &c, &m2);
	poly_basemul(&r2, &c, &hinv);

	poly_tobytes(buf1, &r2);
	hash_g(buf2, buf1);
	fail = poly_sotp_decode(msg, &m1, buf2);

	for (size_t i = 0; i < NTRUPLUS_SYMBYTES; i++)
		msg[i + NTRUPLUS_N / 8] = sk[i + 2 * NTRUPLUS_POLYBYTES];

	hash_h(buf3, msg);

	poly_cbd1(&r1, buf3 + NTRUPLUS_SSBYTES);
	poly_ntt(&r1, &r1);
	poly_tobytes(buf2, &r1);

	fail |= ct_verify(buf1, buf2, NTRUPLUS_POLYBYTES);

	for (size_t i = 0; i < NTRUPLUS_SSBYTES; i++)
		ss[i] = buf3[i] & (uint8_t)~(uint8_t)(-fail);

	return fail;
}

static void find_invertible_coins(uint8_t coins[NTRUPLUS_SYMBYTES],
                                  int is_f, uint32_t start_seed)
{
	poly a, ainv;

	for (uint32_t seed = start_seed; ; seed++)
	{
		fill_bytes(coins, NTRUPLUS_SYMBYTES, seed);
		if (is_f)
		{
			if (genf_derand_profile(&a, &ainv, coins) == 0)
				return;
		}
		else if (geng_derand_profile(&a, &ainv, coins) == 0)
		{
			return;
		}
	}
}

static unsigned long long bench_keygen(const uint8_t *fcoins,
                                       const uint8_t *gcoins,
                                       uint8_t *pk, uint8_t *sk)
{
	unsigned long long total = 0;

	for (int i = 0; i < TEST_LOOP_COUNT; i++)
	{
		unsigned long long start = counter();
		keypair_derand_profile(pk, sk, fcoins, gcoins);
		unsigned long long end = counter();

			total += adjusted_ticks(start, end);
		profile_sink += pk[(unsigned)i & (NTRUPLUS_PUBLICKEYBYTES - 1)];
	}

	return total / TEST_LOOP_COUNT;
}

static unsigned long long bench_enc(const uint8_t *pk, const uint8_t *coins,
                                    uint8_t *ct, uint8_t *ss)
{
	unsigned long long total = 0;

	for (int i = 0; i < TEST_LOOP_COUNT; i++)
	{
		unsigned long long start = counter();
		enc_derand_profile(ct, ss, pk, coins);
		unsigned long long end = counter();

			total += adjusted_ticks(start, end);
		profile_sink += ct[(unsigned)i & (NTRUPLUS_CIPHERTEXTBYTES - 1)];
	}

	return total / TEST_LOOP_COUNT;
}

static unsigned long long bench_dec(const uint8_t *ct, const uint8_t *sk,
                                    uint8_t *ss)
{
	unsigned long long total = 0;

	for (int i = 0; i < TEST_LOOP_COUNT; i++)
	{
		unsigned long long start = counter();
		int fail = dec_profile(ss, ct, sk);
		unsigned long long end = counter();

			total += adjusted_ticks(start, end);
		profile_sink += ss[(unsigned)i & (NTRUPLUS_SSBYTES - 1)];
		profile_sink += (uint32_t)fail;
	}

	return total / TEST_LOOP_COUNT;
}

#define BENCH_COMPONENT_ACC(section_total, label, count, code, sink_expr) do { \
	unsigned long long total__ = 0;                                             \
	unsigned long long one__;                                                   \
	unsigned long long scaled__;                                                \
	for (int i__ = 0; i__ < TEST_LOOP_COUNT; i__++)                             \
	{                                                                           \
		unsigned long long start__ = counter();                                 \
		do { code; } while (0);                                                 \
		unsigned long long end__ = counter();                                   \
		total__ += adjusted_ticks(start__, end__);                              \
		profile_sink += (uint32_t)(sink_expr);                                  \
	}                                                                           \
	one__ = total__ / TEST_LOOP_COUNT;                                          \
	scaled__ = one__ * (unsigned long long)(count);                             \
	(section_total) += scaled__;                                                \
	printf("%-28s %5u %10llu %10llu %s\n", label, (unsigned)(count), one__,     \
	       scaled__, COUNTER_UNIT_STR);                                         \
} while (0)

static void print_component_header(const char *title)
{
	printf("\n[%s components]\n", title);
	printf("%-28s %5s %10s %10s %s\n", "component", "count", "one",
	       "est_total", COUNTER_UNIT_STR);
}

static void print_component_subtotal(unsigned long long total)
{
	printf("%-28s %5s %10s %10llu %s\n", "estimated_subtotal", "", "",
	       total, COUNTER_UNIT_STR);
}

int main(void)
{
	uint8_t fcoins[NTRUPLUS_SYMBYTES];
	uint8_t gcoins[NTRUPLUS_SYMBYTES];
	uint8_t ecoins[NTRUPLUS_N / 8];
	uint8_t sample_buf[NTRUPLUS_N / 4];
	uint8_t msg[NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES];
	uint8_t pk[NTRUPLUS_PUBLICKEYBYTES];
	uint8_t sk[NTRUPLUS_SECRETKEYBYTES];
	uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES];
	uint8_t ss[NTRUPLUS_SSBYTES];
	uint8_t dss[NTRUPLUS_SSBYTES];
	uint8_t polybytes[NTRUPLUS_POLYBYTES];
	poly small;
	poly small_triple;
	poly ntt_poly;
	poly inv_poly;
	poly base_inv;
#ifdef GT_PRODUCTION_USE_SCALED_KEYPAIR
	poly base_inv_keypair;
#endif
	poly product;
	poly decoded;

	setup_counter();

	find_invertible_coins(fcoins, 1, 1);
	find_invertible_coins(gcoins, 0, 1001);
	fill_bytes(ecoins, sizeof ecoins, 2001);
	fill_bytes(msg, sizeof msg, 3001);

	shake256(sample_buf, sizeof sample_buf, fcoins, sizeof fcoins);
	poly_cbd1(&small, sample_buf);
	poly_triple(&small_triple, &small);
	small_triple.coeffs[0] += 1;
	poly_ntt(&ntt_poly, &small_triple);
	if (poly_baseinv(&base_inv, &ntt_poly) != 0)
	{
		printf("profiler setup error: prepared NTT input not invertible\n");
		return 1;
	}
#ifdef GT_PRODUCTION_USE_SCALED_KEYPAIR
	if (poly_baseinv_scaled_r(&base_inv_keypair, &ntt_poly) != 0)
	{
		printf("profiler setup error: prepared scaled NTT input not invertible\n");
		return 1;
	}
#endif
	poly_basemul(&product, &ntt_poly, &base_inv);
	poly_invntt(&inv_poly, &product);
	poly_crepmod3(&decoded, &inv_poly);
	poly_tobytes(polybytes, &ntt_poly);

	keypair_derand_profile(pk, sk, fcoins, gcoins);
	enc_derand_profile(ct, ss, pk, ecoins);
	if (dec_profile(dss, ct, sk) != 0 || memcmp(ss, dss, NTRUPLUS_SSBYTES) != 0)
	{
		printf("kem_component_profiler_correctness: fail\n");
		return 1;
	}

	printf("kem_component_profiler_target: %s\n", KEM_COMPONENT_PROFILE_TARGET);
	printf("kem_component_profiler_correctness: ok\n");
	printf("kem_component_profiler_loops: %d\n", TEST_LOOP_COUNT);
	printf("countergap: %llu %s\n", countergap, COUNTER_UNIT_STR);
	printf("\n[KEM path totals, deterministic no-reject]\n");
	printf("%-28s %8llu %s\n", "keygen_derand", bench_keygen(fcoins, gcoins, pk, sk),
	       COUNTER_UNIT_STR);
	printf("%-28s %8llu %s\n", "enc_derand", bench_enc(pk, ecoins, ct, ss),
	       COUNTER_UNIT_STR);
	printf("%-28s %8llu %s\n", "dec_valid", bench_dec(ct, sk, dss),
	       COUNTER_UNIT_STR);

	unsigned long long keygen_components = 0;
	unsigned long long enc_components = 0;
	unsigned long long dec_components = 0;

	print_component_header("KEYGEN");
	BENCH_COMPONENT_ACC(keygen_components, "shake256_sample", 2, {
		shake256(sample_buf, sizeof sample_buf, fcoins, sizeof fcoins);
	}, sample_buf[(unsigned)i__ & (sizeof sample_buf - 1)]);
	BENCH_COMPONENT_ACC(keygen_components, "poly_cbd1_secret", 2, {
		poly_cbd1(&small, sample_buf);
	}, small.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(keygen_components, "poly_triple_secret", 2, {
		poly_triple(&small_triple, &small);
	}, small_triple.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(keygen_components, "poly_ntt_secret", 2, {
		poly_ntt(&ntt_poly, &small_triple);
	}, ntt_poly.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
#ifdef GT_PRODUCTION_USE_SCALED_KEYPAIR
	BENCH_COMPONENT_ACC(keygen_components, "poly_baseinv_scaled_r_secret", 2, {
		(void)poly_baseinv_scaled_r(&base_inv_keypair, &ntt_poly);
	}, base_inv_keypair.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(keygen_components, "poly_basemul_scaled_keypair", 2, {
		poly_basemul_scaled_r_input(&product, &ntt_poly, &base_inv_keypair);
	}, product.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
#else
	BENCH_COMPONENT_ACC(keygen_components, "poly_baseinv_secret", 2, {
		(void)poly_baseinv(&base_inv, &ntt_poly);
	}, base_inv.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(keygen_components, "poly_basemul_keypair", 2, {
		poly_basemul(&product, &ntt_poly, &base_inv);
	}, product.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
#endif
	BENCH_COMPONENT_ACC(keygen_components, "poly_tobytes_key", 3, {
		poly_tobytes(polybytes, &ntt_poly);
	}, polybytes[(unsigned)i__ & (NTRUPLUS_POLYBYTES - 1)]);
	BENCH_COMPONENT_ACC(keygen_components, "hash_f_pk", 1, {
		hash_f(sample_buf, pk);
	}, sample_buf[(unsigned)i__ & 31]);
	print_component_subtotal(keygen_components);

	print_component_header("ENCAP");
	BENCH_COMPONENT_ACC(enc_components, "hash_f_pk", 1, {
		hash_f(sample_buf, pk);
	}, sample_buf[(unsigned)i__ & 31]);
	BENCH_COMPONENT_ACC(enc_components, "hash_h_msg", 1, {
		hash_h(sample_buf, msg);
	}, sample_buf[(unsigned)i__ & (sizeof sample_buf - 1)]);
	BENCH_COMPONENT_ACC(enc_components, "poly_cbd1_r", 1, {
		poly_cbd1(&small, sample_buf);
	}, small.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(enc_components, "poly_ntt_r", 1, {
		poly_ntt(&ntt_poly, &small);
	}, ntt_poly.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(enc_components, "poly_tobytes_r", 1, {
		poly_tobytes(polybytes, &ntt_poly);
	}, polybytes[(unsigned)i__ & (NTRUPLUS_POLYBYTES - 1)]);
	BENCH_COMPONENT_ACC(enc_components, "hash_g_polybytes", 1, {
		hash_g(sample_buf, polybytes);
	}, sample_buf[(unsigned)i__ & (sizeof sample_buf - 1)]);
	BENCH_COMPONENT_ACC(enc_components, "poly_sotp_encode", 1, {
		poly_sotp_encode(&decoded, msg, sample_buf);
	}, decoded.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(enc_components, "poly_ntt_m", 1, {
		poly_ntt(&ntt_poly, &decoded);
	}, ntt_poly.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(enc_components, "poly_frombytes_pk", 1, {
		poly_frombytes(&decoded, polybytes);
	}, decoded.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(enc_components, "poly_basemul_add", 1, {
		poly_basemul_add(&product, &ntt_poly, &base_inv, &ntt_poly);
	}, product.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(enc_components, "poly_tobytes_ct", 1, {
		poly_tobytes(polybytes, &product);
	}, polybytes[(unsigned)i__ & (NTRUPLUS_POLYBYTES - 1)]);
	print_component_subtotal(enc_components);

	print_component_header("DECAP");
	BENCH_COMPONENT_ACC(dec_components, "poly_frombytes", 3, {
		poly_frombytes(&decoded, polybytes);
	}, decoded.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
#ifdef GT_PRODUCTION_USE_RMINUS1_STAGE123SCRATCH_CREP3_DECAP
	BENCH_COMPONENT_ACC(dec_components,
	                    "poly_basemul_rminus1_to_stage123scratch", 1, {
		poly_basemul_rminus1_to_stage123scratch(product.coeffs,
		                                        &ntt_poly,
		                                        &base_inv);
	}, product.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(dec_components,
	                    "poly_invntt_from_rminus1_crep3_stage45scratch", 1, {
		poly_invntt_from_rminus1_crepmod3_stage45scratch(&decoded,
		                                                 product.coeffs);
	}, decoded.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(dec_components, "poly_basemul", 1, {
		poly_basemul(&product, &ntt_poly, &base_inv);
	}, product.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
#elif defined(GT_PRODUCTION_USE_RMINUS1_CREP3_DECAP)
	BENCH_COMPONENT_ACC(dec_components, "poly_basemul_rminus1", 1, {
		poly_basemul_rminus1(&product, &ntt_poly, &base_inv);
	}, product.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(dec_components,
	                    "poly_invntt_from_rminus1_crepmod3", 1, {
		poly_invntt_from_rminus1_crepmod3(&decoded, &product);
	}, decoded.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(dec_components, "poly_basemul", 1, {
		poly_basemul(&product, &ntt_poly, &base_inv);
	}, product.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
#elif defined(GT_PRODUCTION_USE_RMINUS1_STAGE123SCRATCH_DECAP)
	BENCH_COMPONENT_ACC(dec_components,
	                    "poly_basemul_rminus1_to_stage123scratch", 1, {
		poly_basemul_rminus1_to_stage123scratch(product.coeffs,
		                                        &ntt_poly,
		                                        &base_inv);
	}, product.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(dec_components,
	                    "poly_invntt_from_rminus1_stage45scratch", 1, {
		poly_invntt_from_rminus1_stage45scratch(&inv_poly,
		                                        product.coeffs);
	}, inv_poly.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(dec_components, "poly_basemul", 1, {
		poly_basemul(&product, &ntt_poly, &base_inv);
	}, product.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
#elif defined(GT_PRODUCTION_USE_RMINUS1_DECAP)
	BENCH_COMPONENT_ACC(dec_components, "poly_basemul_rminus1", 1, {
		poly_basemul_rminus1(&product, &ntt_poly, &base_inv);
	}, product.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(dec_components, "poly_invntt_from_rminus1", 1, {
		poly_invntt_from_rminus1(&inv_poly, &product);
	}, inv_poly.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(dec_components, "poly_basemul", 1, {
		poly_basemul(&product, &ntt_poly, &base_inv);
	}, product.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
#elif defined(GT_PRODUCTION_USE_TUPLE_DECAP)
	BENCH_COMPONENT_ACC(dec_components, "poly_basemul_to_tuple", 1, {
		poly_basemul_to_tuple(&product, &ntt_poly, &base_inv);
	}, product.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(dec_components, "gt_tuple_poly_invntt", 1, {
		gt_tuple_poly_invntt(&inv_poly, &product);
	}, inv_poly.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(dec_components, "poly_basemul", 1, {
		poly_basemul(&product, &ntt_poly, &base_inv);
	}, product.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
#elif defined(GT_PRODUCTION_USE_PACK_TUPLE_DECAP)
	BENCH_COMPONENT_ACC(dec_components, "poly_basemul", 1, {
		poly_basemul(&product, &ntt_poly, &base_inv);
	}, product.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(dec_components, "gt_block_major_to_tuple_c", 1, {
		gt_block_major_to_tuple_c(&decoded, &product);
	}, decoded.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(dec_components, "gt_tuple_poly_invntt", 1, {
		gt_tuple_poly_invntt(&inv_poly, &decoded);
	}, inv_poly.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(dec_components, "poly_basemul", 1, {
		poly_basemul(&product, &ntt_poly, &base_inv);
	}, product.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
#else
	BENCH_COMPONENT_ACC(dec_components, "poly_basemul", 2, {
		poly_basemul(&product, &ntt_poly, &base_inv);
	}, product.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(dec_components, "poly_invntt", 1, {
		poly_invntt(&inv_poly, &product);
	}, inv_poly.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
#endif
#if !defined(GT_PRODUCTION_USE_RMINUS1_CREP3_DECAP) && \
	!defined(GT_PRODUCTION_USE_RMINUS1_STAGE123SCRATCH_CREP3_DECAP)
	BENCH_COMPONENT_ACC(dec_components, "poly_crepmod3", 1, {
		poly_crepmod3(&decoded, &inv_poly);
	}, decoded.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
#endif
	BENCH_COMPONENT_ACC(dec_components, "poly_ntt_m1", 1, {
		poly_ntt(&ntt_poly, &decoded);
	}, ntt_poly.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(dec_components, "poly_sub", 1, {
		poly_sub(&product, &ntt_poly, &base_inv);
	}, product.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(dec_components, "poly_tobytes", 2, {
		poly_tobytes(polybytes, &ntt_poly);
	}, polybytes[(unsigned)i__ & (NTRUPLUS_POLYBYTES - 1)]);
	BENCH_COMPONENT_ACC(dec_components, "hash_g_polybytes", 1, {
		hash_g(sample_buf, polybytes);
	}, sample_buf[(unsigned)i__ & (sizeof sample_buf - 1)]);
	BENCH_COMPONENT_ACC(dec_components, "poly_sotp_decode", 1, {
		(void)poly_sotp_decode(msg, &decoded, sample_buf);
	}, msg[(unsigned)i__ & (NTRUPLUS_N / 8 - 1)]);
	BENCH_COMPONENT_ACC(dec_components, "hash_h_msg", 1, {
		hash_h(sample_buf, msg);
	}, sample_buf[(unsigned)i__ & (sizeof sample_buf - 1)]);
	BENCH_COMPONENT_ACC(dec_components, "poly_cbd1_r1", 1, {
		poly_cbd1(&small, sample_buf);
	}, small.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(dec_components, "poly_ntt_r1", 1, {
		poly_ntt(&ntt_poly, &small);
	}, ntt_poly.coeffs[(unsigned)i__ & (NTRUPLUS_N - 1)]);
	BENCH_COMPONENT_ACC(dec_components, "verify_polybytes", 1, {
		(void)ct_verify(polybytes, polybytes, NTRUPLUS_POLYBYTES);
	}, polybytes[(unsigned)i__ & (NTRUPLUS_POLYBYTES - 1)]);
	print_component_subtotal(dec_components);

	printf("\nkem_component_profiler_sink: %u\n", profile_sink);
	return 0;
}
