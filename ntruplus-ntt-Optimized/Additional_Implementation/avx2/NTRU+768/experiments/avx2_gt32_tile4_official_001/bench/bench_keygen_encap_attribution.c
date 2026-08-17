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

typedef void (*phase_fn)(void);

static uint8_t pk[CRYPTO_PUBLICKEYBYTES] __attribute__((aligned(64)));
static uint8_t sk[CRYPTO_SECRETKEYBYTES] __attribute__((aligned(64)));
static uint8_t coins[NTRUPLUS_N / 8] __attribute__((aligned(64)));
static uint8_t enc_msg[HASH_H_INBYTES] __attribute__((aligned(64)));
static uint8_t enc_buf[HASH_H_OUTBYTES] __attribute__((aligned(64)));
static uint8_t r_bytes[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
static uint8_t out_bytes[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
static uint8_t out_ss[NTRUPLUS_SSBYTES] __attribute__((aligned(64)));

static poly off_h, off_r_coeff, off_m_coeff, off_r, off_m, off_product;
static poly off_sum, off_work0, off_work1;
static int16_t gt_h[WORDS] __attribute__((aligned(64)));
static int16_t gt_r_coeff[WORDS] __attribute__((aligned(64)));
static int16_t gt_m_coeff[WORDS] __attribute__((aligned(64)));
static int16_t gt_r[WORDS] __attribute__((aligned(64)));
static int16_t gt_m[WORDS] __attribute__((aligned(64)));
static int16_t gt_product[WORDS] __attribute__((aligned(64)));
static int16_t gt_sum[WORDS] __attribute__((aligned(64)));
static int16_t gt_work0[WORDS] __attribute__((aligned(64)));
static int16_t gt_work1[WORDS] __attribute__((aligned(64)));

static poly kg_f_coeff, kg_g_coeff, kg_f, kg_g, kg_finv, kg_ginv;
static poly kg_h0, kg_h1, kg_work0, kg_work1;
static int16_t kg_gt_f[WORDS] __attribute__((aligned(64)));
static int16_t kg_gt_g[WORDS] __attribute__((aligned(64)));
static int16_t kg_gt_work0[WORDS] __attribute__((aligned(64)));
static int16_t kg_gt_work1[WORDS] __attribute__((aligned(64)));
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

static int official_enc_derand(uint8_t *ct, uint8_t *ss_out,
	const uint8_t *public_key, const uint8_t *enc_coins)
{
	uint8_t msg[HASH_H_INBYTES];
	uint8_t buf[HASH_H_OUTBYTES];
	poly c, h, r, m;
	if (poly_frombytes(&h, public_key) != 0) {
		memset(ct, 0, NTRUPLUS_CIPHERTEXTBYTES);
		secure_clear(ss_out, NTRUPLUS_SSBYTES);
		return 1;
	}
	memcpy(msg, enc_coins, NTRUPLUS_N / 8);
	hash_f(msg + NTRUPLUS_N / 8, public_key);
	hash_h(buf, msg);
	poly_cbd1(&r, buf + NTRUPLUS_SYMBYTES);
	poly_ntt(&r);
	poly_tobytes(ct, &r);
	hash_g(ct, ct);
	poly_sotp_encode(&m, msg, ct);
	poly_ntt(&m);
	poly_basemul(&c, &h, &r);
	poly_add(&c, &c, &m);
	poly_tobytes(ct, &c);
	memcpy(ss_out, buf, NTRUPLUS_SSBYTES);
	return 0;
}

static void enc_e1_official(void)
{
	sink += (unsigned)poly_frombytes(&off_work0, pk);
	poly_cbd1(&off_work0, enc_buf + NTRUPLUS_SYMBYTES);
	poly_sotp_encode(&off_work1, enc_msg, r_bytes);
}

static void enc_e1_gt(void)
{
	sink += (unsigned)gt32_q24_decode_soa_asm(gt_work0, pk);
	poly_cbd1((poly *)(void *)gt_work0, enc_buf + NTRUPLUS_SYMBYTES);
	poly_sotp_encode((poly *)(void *)gt_work1, enc_msg, r_bytes);
}

static void enc_e2_official(void)
{
	off_work0 = off_r_coeff;
	off_work1 = off_m_coeff;
	poly_ntt(&off_work0);
	poly_ntt(&off_work1);
}

static void enc_e2_gt(void)
{
	forward_gt(gt_work0, gt_product, gt_r_coeff);
	forward_gt(gt_work1, gt_product, gt_m_coeff);
}

static void enc_e3_official(void)
{
	poly_basemul(&off_work0, &off_h, &off_r);
}

static void enc_e3_gt(void)
{
	gt32_tile4_basemul_general_soa_soa_to_soa_asm(gt_work0, gt_h, gt_r);
}

static void enc_e4_official(void)
{
	poly_tobytes(r_bytes, &off_r);
	poly_add(&off_work0, &off_product, &off_m);
	poly_tobytes(out_bytes, &off_work0);
	sink += out_bytes[0];
}

static void enc_e4_gt(void)
{
	gt32_q24_encode_soa_lazy10788_asm(r_bytes, gt_r);
	poly_add((poly *)(void *)gt_work0,
		(const poly *)(const void *)gt_product,
		(const poly *)(const void *)gt_m);
	gt32_q24_encode_soa_encap_hr_h1_asm(out_bytes, gt_work0);
	sink += out_bytes[0];
}

static void enc_e4a_add_official(void)
{
	poly_add(&off_work0, &off_product, &off_m);
	sink += (uint16_t)off_work0.coeffs[0];
}

static void enc_e4a_add_gt(void)
{
	poly_add((poly *)(void *)gt_work0,
		(const poly *)(const void *)gt_product,
		(const poly *)(const void *)gt_m);
	sink += (uint16_t)gt_work0[0];
}

static void enc_e4b_serialize_r_official(void)
{
	poly_tobytes(r_bytes, &off_r);
	sink += r_bytes[0];
}

static void enc_e4b_serialize_r_gt(void)
{
	gt32_q24_encode_soa_lazy10788_asm(r_bytes, gt_r);
	sink += r_bytes[0];
}

static void enc_e4c_serialize_c_official(void)
{
	poly_tobytes(out_bytes, &off_sum);
	sink += out_bytes[0];
}

static void enc_e4c_serialize_c_gt(void)
{
	gt32_q24_encode_soa_encap_hr_h1_asm(out_bytes, gt_sum);
	sink += out_bytes[0];
}

static void enc_e4c_serialize_c_bridge_control(void)
{
	gt32_tile4_soa_to_official_words_grouped_asm(gt_work1, gt_sum);
	poly_tobytes(out_bytes, (const poly *)(const void *)gt_work1);
	sink += out_bytes[0];
}

static void enc_e4c_serialize_c_hr_h1(void)
{
	gt32_q24_encode_soa_encap_hr_h1_asm(out_bytes, gt_sum);
	sink += out_bytes[0];
}

static void enc_e4c_serialize_c_hr_h2(void)
{
	gt32_q24_encode_soa_encap_hr_h2_asm(out_bytes, gt_sum);
	sink += out_bytes[0];
}

static void enc_e5_common(void)
{
	hash_f(enc_msg + NTRUPLUS_N / 8, pk);
	hash_h(enc_buf, enc_msg);
	hash_g(enc_buf, r_bytes);
	sink += enc_buf[0];
}

static void kg_k1_official(void)
{
	kg_work0 = kg_f_coeff;
	kg_work1 = kg_g_coeff;
	poly_triple(&kg_work0);
	poly_triple(&kg_work1);
	kg_work0.coeffs[0]++;
}

static void kg_k1_gt(void)
{
	/* No direct CBD/triple producer exists yet; this is the shared control. */
	kg_k1_official();
}

static void kg_k2_official(void)
{
	kg_work0 = kg_f_coeff;
	kg_work1 = kg_g_coeff;
	poly_triple(&kg_work0);
	poly_triple(&kg_work1);
	kg_work0.coeffs[0]++;
	poly_ntt(&kg_work0);
	poly_ntt(&kg_work1);
}

static void kg_k2_gt(void)
{
	kg_work0 = kg_f_coeff;
	kg_work1 = kg_g_coeff;
	poly_triple(&kg_work0);
	poly_triple(&kg_work1);
	kg_work0.coeffs[0]++;
	forward_gt(kg_gt_f, kg_gt_work0, kg_work0.coeffs);
	forward_gt(kg_gt_g, kg_gt_work1, kg_work1.coeffs);
}

static void kg_k3_official(void)
{
	sink += (unsigned)poly_baseinv(&kg_work0, &kg_f);
	sink += (unsigned)poly_baseinv(&kg_work1, &kg_g);
}

static void kg_k4_official(void)
{
	poly_basemul(&kg_work0, &kg_g, &kg_finv);
	poly_basemul(&kg_work1, &kg_f, &kg_ginv);
}

static void kg_k5_official(void)
{
	poly_tobytes(out_bytes, &kg_f);
	poly_tobytes(r_bytes, &kg_h0);
	poly_tobytes(out_bytes, &kg_h1);
	sink += out_bytes[0];
}

static void kg_k6_common(void)
{
	hash_f(out_ss, pk);
	sink += out_ss[0];
}

static double measure(phase_fn fn, unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++)
		fn();
	const uint64_t end = stop_tsc();
	return (double)(end - begin) / iterations;
}

static double measure_full(int gt, unsigned iterations)
{
	const uint64_t begin = start_tsc();
	for (unsigned i = 0; i < iterations; i++) {
		if (gt)
			sink += (unsigned)crypto_kem_enc_derand_gt32_candidate(
				out_bytes, out_ss, pk, coins);
		else
			sink += (unsigned)official_enc_derand(out_bytes, out_ss, pk,
				coins);
	}
	const uint64_t end = stop_tsc();
	return (double)(end - begin) / iterations;
}

static int prepare_encap(void)
{
	memcpy(enc_msg, coins, NTRUPLUS_N / 8);
	hash_f(enc_msg + NTRUPLUS_N / 8, pk);
	hash_h(enc_buf, enc_msg);
	if (poly_frombytes(&off_h, pk) != 0
		|| gt32_q24_decode_soa_asm(gt_h, pk) != 0)
		return 0;
	poly_cbd1(&off_r_coeff, enc_buf + NTRUPLUS_SYMBYTES);
	memcpy(gt_r_coeff, off_r_coeff.coeffs, sizeof gt_r_coeff);
	off_r = off_r_coeff;
	poly_ntt(&off_r);
	forward_gt(gt_r, gt_work0, gt_r_coeff);
	poly_tobytes(r_bytes, &off_r);
	hash_g(r_bytes, r_bytes);
	poly_sotp_encode(&off_m_coeff, enc_msg, r_bytes);
	memcpy(gt_m_coeff, off_m_coeff.coeffs, sizeof gt_m_coeff);
	off_m = off_m_coeff;
	poly_ntt(&off_m);
	forward_gt(gt_m, gt_work0, gt_m_coeff);
	poly_basemul(&off_product, &off_h, &off_r);
	gt32_tile4_basemul_general_soa_soa_to_soa_asm(gt_product, gt_h, gt_r);
	poly_add(&off_sum, &off_product, &off_m);
	poly_add((poly *)(void *)gt_sum,
		(const poly *)(const void *)gt_product,
		(const poly *)(const void *)gt_m);
	return 1;
}

static int prepare_keygen(void)
{
	uint32_t state = 1U;
	uint8_t cbd[NTRUPLUS_N / 4];
	for (;;) {
		for (size_t i = 0; i < sizeof cbd; i++) {
			state = state * 1664525U + 1013904223U;
			cbd[i] = (uint8_t)(state >> 24);
		}
		poly_cbd1(&kg_f_coeff, cbd);
		kg_f = kg_f_coeff;
		poly_triple(&kg_f);
		kg_f.coeffs[0]++;
		poly_ntt(&kg_f);
		if (poly_baseinv(&kg_finv, &kg_f) == 0)
			break;
	}
	for (;;) {
		for (size_t i = 0; i < sizeof cbd; i++) {
			state = state * 1664525U + 1013904223U;
			cbd[i] = (uint8_t)(state >> 24);
		}
		poly_cbd1(&kg_g_coeff, cbd);
		kg_g = kg_g_coeff;
		poly_triple(&kg_g);
		poly_ntt(&kg_g);
		if (poly_baseinv(&kg_ginv, &kg_g) == 0)
			break;
	}
	poly_basemul(&kg_h0, &kg_g, &kg_finv);
	poly_basemul(&kg_h1, &kg_f, &kg_ginv);
	return 1;
}

typedef struct {
	const char *name;
	phase_fn official;
	phase_fn gt;
} pair_t;

int main(int argc, char **argv)
{
	const int perf_mode = argc > 1 && strcmp(argv[1], "--perf") == 0;
	const unsigned iterations = perf_mode && argc > 4
		? (unsigned)strtoul(argv[4], NULL, 10) : argc > 1
		? (unsigned)strtoul(argv[1], NULL, 10) : 2000U;
	const pair_t encap[] = {
		{"E1_input_decode_cbd_sotp", enc_e1_official, enc_e1_gt},
		{"E2_two_forwards", enc_e2_official, enc_e2_gt},
		{"E3_general_basemul", enc_e3_official, enc_e3_gt},
		{"E4_add_two_serializations", enc_e4_official, enc_e4_gt},
		{"E4a_add_m", enc_e4a_add_official, enc_e4a_add_gt},
		{"E4b_serialize_rhat", enc_e4b_serialize_r_official,
			enc_e4b_serialize_r_gt},
		{"E4c_serialize_chat", enc_e4c_serialize_c_official,
			enc_e4c_serialize_c_gt},
		{"E4c_bridge_control", enc_e4c_serialize_c_official,
			enc_e4c_serialize_c_bridge_control},
		{"E4c_hr_h1_vs_bridge", enc_e4c_serialize_c_bridge_control,
			enc_e4c_serialize_c_hr_h1},
		{"E4c_hr_h2_vs_bridge", enc_e4c_serialize_c_bridge_control,
			enc_e4c_serialize_c_hr_h2},
		{"E5_hash_glue", enc_e5_common, enc_e5_common},
	};
	const pair_t keygen[] = {
		{"K1_cbd_triple", kg_k1_official, kg_k1_gt},
		{"K2_two_forwards", kg_k2_official, kg_k2_gt},
		{"K6_hash_glue", kg_k6_common, kg_k6_common},
	};
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
	if (!prepare_encap() || !prepare_keygen())
		return 1;
	if (official_enc_derand(r_bytes, enc_buf, pk, coins) != 0
		|| crypto_kem_enc_derand_gt32_candidate(out_bytes, out_ss, pk, coins)
			!= 0 || memcmp(r_bytes, out_bytes, NTRUPLUS_CIPHERTEXTBYTES) != 0
		|| memcmp(enc_buf, out_ss, NTRUPLUS_SSBYTES) != 0) {
		fprintf(stderr, "full encap differential failed\n");
		return 1;
	}
	if (perf_mode) {
		if (argc <= 4) {
			fprintf(stderr, "usage: --perf domain.phase impl iterations\n");
			return 2;
		}
		const char *const requested = argv[2];
		const char *const impl = argv[3];
		if (strcmp(requested, "noop") == 0) {
			printf("PERF,noop,%s,0.000000\n", impl);
			return 0;
		}
		for (size_t i = 0; i < sizeof encap / sizeof encap[0]; i++) {
			char name[96];
			(void)snprintf(name, sizeof name, "encap.%s", encap[i].name);
			if (strcmp(name, requested) == 0) {
				phase_fn fn = strcmp(impl, "gt32") == 0
					? encap[i].gt : encap[i].official;
				printf("PERF,%s,%s,%.6f\n", requested, impl,
					measure(fn, iterations));
				return 0;
			}
		}
		for (size_t i = 0; i < sizeof keygen / sizeof keygen[0]; i++) {
			char name[96];
			(void)snprintf(name, sizeof name, "keygen.%s", keygen[i].name);
			if (strcmp(name, requested) == 0) {
				phase_fn fn = strcmp(impl, "gt32") == 0
					? keygen[i].gt : keygen[i].official;
				printf("PERF,%s,%s,%.6f\n", requested, impl,
					measure(fn, iterations));
				return 0;
			}
		}
		if (strcmp(requested, "encap.full") == 0) {
			printf("PERF,%s,%s,%.6f\n", requested, impl,
				measure_full(strcmp(impl, "gt32") == 0, iterations));
			return 0;
		}
		if (strcmp(requested, "keygen.K3_baseinv") == 0) {
			printf("PERF,%s,official,%.6f\n", requested,
				measure(kg_k3_official, iterations));
			return 0;
		}
		if (strcmp(requested, "keygen.K4_two_general_basemuls") == 0) {
			printf("PERF,%s,official,%.6f\n", requested,
				measure(kg_k4_official, iterations));
			return 0;
		}
		if (strcmp(requested, "keygen.K5_three_serializations") == 0) {
			printf("PERF,%s,official,%.6f\n", requested,
				measure(kg_k5_official, iterations));
			return 0;
		}
		fprintf(stderr, "unknown perf region: %s\n", requested);
		return 2;
	}
	printf("META,correctness=byte-exact-pass,iterations=%u,samples=%u\n",
		iterations, SAMPLES);
	printf("COVERAGE,keygen,K3_baseinv,official-only,GT-BaseInv-J1-missing\n");
	printf("COVERAGE,keygen,K4_two_general_basemuls,official-only,depends-on-K3\n");
	printf("COVERAGE,keygen,K5_three_serializations,official-only,depends-on-K4\n");
	for (unsigned warm = 0; warm < 2; warm++) {
		for (size_t i = 0; i < sizeof encap / sizeof encap[0]; i++) {
			(void)measure(encap[i].official, 200);
			(void)measure(encap[i].gt, 200);
		}
	}
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		for (size_t i = 0; i < sizeof encap / sizeof encap[0]; i++) {
			double off, gt;
			if ((sample & 1U) == 0U) {
				off = measure(encap[i].official, iterations);
				gt = measure(encap[i].gt, iterations);
			} else {
				gt = measure(encap[i].gt, iterations);
				off = measure(encap[i].official, iterations);
			}
			printf("PHASE,encap,%s,%u,%.6f,%.6f,%.6f\n",
				encap[i].name, sample, off, gt, gt - off);
		}
		double off, gt;
		if ((sample & 1U) == 0U) {
			off = measure_full(0, iterations);
			gt = measure_full(1, iterations);
		} else {
			gt = measure_full(1, iterations);
			off = measure_full(0, iterations);
		}
		printf("FULL,encap,%u,%.6f,%.6f,%.6f\n", sample, off, gt,
			gt - off);
		for (size_t i = 0; i < sizeof keygen / sizeof keygen[0]; i++) {
			if ((sample & 1U) == 0U) {
				off = measure(keygen[i].official, iterations);
				gt = measure(keygen[i].gt, iterations);
			} else {
				gt = measure(keygen[i].gt, iterations);
				off = measure(keygen[i].official, iterations);
			}
			printf("PHASE,keygen,%s,%u,%.6f,%.6f,%.6f\n",
				keygen[i].name, sample, off, gt, gt - off);
		}
		printf("OFFICIAL_ONLY,keygen,K3_baseinv,%u,%.6f\n", sample,
			measure(kg_k3_official, iterations));
		printf("OFFICIAL_ONLY,keygen,K4_two_general_basemuls,%u,%.6f\n",
			sample, measure(kg_k4_official, iterations));
		printf("OFFICIAL_ONLY,keygen,K5_three_serializations,%u,%.6f\n",
			sample, measure(kg_k5_official, iterations));
	}
	printf("SINK,%llu\n", (unsigned long long)sink);
	return 0;
}
