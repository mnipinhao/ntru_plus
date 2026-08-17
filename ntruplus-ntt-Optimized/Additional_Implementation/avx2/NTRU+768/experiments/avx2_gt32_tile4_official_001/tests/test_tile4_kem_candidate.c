#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "api.h"
#include "kat/rng.h"
#include "poly.h"

#include "tile4.h"
#include "tile4_kem_candidate.h"

#define ROUNDS 8

static int16_t centered_mod_q(int16_t value)
{
	int32_t reduced = (int32_t)value % NTRUPLUS_Q;
	if (reduced > NTRUPLUS_Q / 2)
		reduced -= NTRUPLUS_Q;
	if (reduced < -NTRUPLUS_Q / 2)
		reduced += NTRUPLUS_Q;
	return (int16_t)reduced;
}

static int check_serialized_ntt_boundary(void)
{
	for (unsigned test_case = 0; test_case < 4; test_case++) {
		poly official;
		uint8_t encoded[NTRUPLUS_POLYBYTES];
		int16_t tile4[GT32_TILE4_POLY_WORDS] __attribute__((aligned(64)));
		int16_t decoded[GT32_TILE4_POLY_WORDS] __attribute__((aligned(64)));

		for (size_t i = 0; i < NTRUPLUS_N; i++) {
			if (test_case == 0U)
				official.coeffs[i] = (i == 0U) ? 1 : 0;
			else if (test_case == 1U)
				official.coeffs[i] = (i & 1U) ? 4 : -3;
			else
				official.coeffs[i] = (int16_t)((int)((17U * i
					+ 29U * test_case) & 7U) - 3);
		}
		gt32_tile4_forward_full_wide_raw_pair_align64_asm(tile4,
			official.coeffs);
		poly_ntt(&official);
		poly_tobytes(encoded, &official);
		if (gt32_tile4_frombytes_aos_asm(decoded, encoded) != 0)
			return 0;
		for (size_t i = 0; i < GT32_TILE4_POLY_WORDS; i++) {
			if (centered_mod_q(tile4[i]) != centered_mod_q(decoded[i])) {
				fprintf(stderr, "serialized NTT boundary mismatch case=%u "
					"word=%zu n5=%d decoded=%d\n", test_case, i,
					centered_mod_q(tile4[i]), centered_mod_q(decoded[i]));
				return 0;
			}
		}
	}
	return 1;
}

static void make_first_slot_noncanonical(uint8_t *encoded)
{
	encoded[0] = (uint8_t)(NTRUPLUS_Q & 0xff);
	encoded[1] = (uint8_t)((encoded[1] & 0xf0U) | (NTRUPLUS_Q >> 8));
}

static void reset_rng(unsigned domain, unsigned round)
{
	uint8_t entropy[48];
	for (size_t i = 0; i < sizeof entropy; i++)
		entropy[i] = (uint8_t)(i + 37U * domain + 101U * round);
	randombytes_init(entropy, NULL, 256);
}

static int compare_decap(const char *name, const uint8_t *ct,
	const uint8_t *sk)
{
	uint8_t official_ss[CRYPTO_BYTES];
	uint8_t gt32_ss[CRYPTO_BYTES];
	uint8_t soa_domain_ss[CRYPTO_BYTES];
	uint8_t q24_decode_ss[CRYPTO_BYTES];
	uint8_t q24_pack_ss[CRYPTO_BYTES];
	uint8_t q24_lazy_pack_ss[CRYPTO_BYTES];
#ifdef GT32_GLOBAL_PHYSICAL_KEM
	uint8_t global_inverse_ss[CRYPTO_BYTES];
	uint8_t native_rcheck_ss[CRYPTO_BYTES];
#endif
	memset(official_ss, 0xa5, sizeof official_ss);
	memset(gt32_ss, 0xa5, sizeof gt32_ss);
	memset(soa_domain_ss, 0xa5, sizeof soa_domain_ss);
	memset(q24_decode_ss, 0xa5, sizeof q24_decode_ss);
	memset(q24_pack_ss, 0xa5, sizeof q24_pack_ss);
	memset(q24_lazy_pack_ss, 0xa5, sizeof q24_lazy_pack_ss);
#ifdef GT32_GLOBAL_PHYSICAL_KEM
	memset(global_inverse_ss, 0xa5, sizeof global_inverse_ss);
	memset(native_rcheck_ss, 0xa5, sizeof native_rcheck_ss);
#endif
	const int official_rc = crypto_kem_dec(official_ss, ct, sk);
	const int gt32_rc = crypto_kem_dec_gt32_candidate(gt32_ss, ct, sk);
	const int soa_domain_rc = crypto_kem_dec_gt32_soa_domain_candidate(
		soa_domain_ss, ct, sk);
	const int q24_decode_rc = crypto_kem_dec_gt32_q24_decode_candidate(
		q24_decode_ss, ct, sk);
	const int q24_pack_rc = crypto_kem_dec_gt32_q24_pack_candidate(
		q24_pack_ss, ct, sk);
	const int q24_lazy_pack_rc = crypto_kem_dec_gt32_q24_lazy_pack_candidate(
		q24_lazy_pack_ss, ct, sk);
#ifdef GT32_GLOBAL_PHYSICAL_KEM
	const int global_inverse_rc = crypto_kem_dec_gt32_global_inverse_candidate(
		global_inverse_ss, ct, sk);
	const int native_rcheck_rc = crypto_kem_dec_gt32_native_rcheck_candidate(
		native_rcheck_ss, ct, sk);
#endif
	if (official_rc != gt32_rc
		|| official_rc != soa_domain_rc
		|| official_rc != q24_decode_rc
		|| official_rc != q24_pack_rc
		|| official_rc != q24_lazy_pack_rc
		|| memcmp(official_ss, gt32_ss, sizeof official_ss) != 0
		|| memcmp(official_ss, soa_domain_ss, sizeof official_ss) != 0
		|| memcmp(official_ss, q24_decode_ss, sizeof official_ss) != 0
		|| memcmp(official_ss, q24_pack_ss, sizeof official_ss) != 0
		|| memcmp(official_ss, q24_lazy_pack_ss, sizeof official_ss) != 0
#ifdef GT32_GLOBAL_PHYSICAL_KEM
		|| official_rc != global_inverse_rc
		|| memcmp(official_ss, global_inverse_ss, sizeof official_ss) != 0
		|| official_rc != native_rcheck_rc
		|| memcmp(official_ss, native_rcheck_ss, sizeof official_ss) != 0
#endif
		) {
		fprintf(stderr, "%s: decap differential failed official=%d gt32=%d "
			"soa-domain=%d q24=%d q24-pack=%d lazy-pack=%d\n", name,
			official_rc, gt32_rc, soa_domain_rc, q24_decode_rc,
			q24_pack_rc, q24_lazy_pack_rc);
		return 0;
	}
	return 1;
}

static int compare_trace(const uint8_t *ct, const uint8_t *sk, unsigned round)
{
	poly c;
	poly f;
	poly hinv;
	poly m;
	int16_t sa_control_m[NTRUPLUS_N] __attribute__((aligned(64)));
	int16_t gt32_m[NTRUPLUS_N] __attribute__((aligned(64)));
	int16_t soa_domain_m[NTRUPLUS_N] __attribute__((aligned(64)));
	int16_t q24_decode_m[NTRUPLUS_N] __attribute__((aligned(64)));
	int16_t q24_pack_m[NTRUPLUS_N] __attribute__((aligned(64)));
	uint8_t official_r[NTRUPLUS_POLYBYTES];
	uint8_t sa_control_r[NTRUPLUS_POLYBYTES];
	uint8_t gt32_r[NTRUPLUS_POLYBYTES];
	uint8_t soa_domain_r[NTRUPLUS_POLYBYTES];
	uint8_t q24_decode_r[NTRUPLUS_POLYBYTES];
	uint8_t q24_pack_r[NTRUPLUS_POLYBYTES];

	if (poly_frombytes(&c, ct) != 0 || poly_frombytes(&f, sk) != 0
		|| poly_frombytes(&hinv, sk + NTRUPLUS_POLYBYTES) != 0)
		return 0;
	poly_basemul_scale(&m, &c, &f);
	poly_invntt_scale(&m);
	poly_crepmod3(&m);
	f = m;
	poly_ntt(&f);
	poly_sub(&c, &c, &f);
	poly_basemul(&f, &c, &hinv);
	poly_tobytes(official_r, &f);

	if (gt32_tile4_decap_trace_sa_control(sa_control_m, sa_control_r, ct,
		sk) != 0) {
		fprintf(stderr, "SA control trace decode rejected round=%u\n", round);
		return 0;
	}
	if (gt32_tile4_decap_trace_candidate(gt32_m, gt32_r, ct, sk) != 0) {
		fprintf(stderr, "trace decode rejected round=%u\n", round);
		return 0;
	}
	if (memcmp(m.coeffs, sa_control_m, sizeof sa_control_m) != 0
		|| memcmp(official_r, sa_control_r, sizeof official_r) != 0) {
		fprintf(stderr, "SA control trace mismatch round=%u\n", round);
		return 0;
	}
	if (gt32_tile4_decap_trace_soa_domain_candidate(soa_domain_m,
		soa_domain_r, ct, sk) != 0) {
		fprintf(stderr, "SoA-domain trace decode rejected round=%u\n", round);
		return 0;
	}
	if (gt32_tile4_decap_trace_q24_decode_candidate(q24_decode_m,
		q24_decode_r, ct, sk) != 0) {
		fprintf(stderr, "Q24 decode trace rejected round=%u\n", round);
		return 0;
	}
	if (gt32_tile4_decap_trace_q24_pack_candidate(q24_pack_m,
		q24_pack_r, ct, sk) != 0) {
		fprintf(stderr, "Q24 pack trace rejected round=%u\n", round);
		return 0;
	}
	if (memcmp(m.coeffs, gt32_m, sizeof gt32_m) != 0) {
		for (size_t i = 0; i < NTRUPLUS_N; i++) {
			if (m.coeffs[i] != gt32_m[i]) {
				fprintf(stderr, "message stage mismatch round=%u word=%zu "
					"official=%d gt32=%d\n", round, i, m.coeffs[i],
					gt32_m[i]);
				break;
			}
		}
		return 0;
	}
	if (memcmp(m.coeffs, soa_domain_m, sizeof soa_domain_m) != 0) {
		fprintf(stderr, "SoA-domain message stage mismatch round=%u\n", round);
		return 0;
	}
	if (memcmp(m.coeffs, q24_decode_m, sizeof q24_decode_m) != 0) {
		fprintf(stderr, "Q24 decode message stage mismatch round=%u\n", round);
		return 0;
	}
	if (memcmp(m.coeffs, q24_pack_m, sizeof q24_pack_m) != 0) {
		fprintf(stderr, "Q24 pack message stage mismatch round=%u\n", round);
		return 0;
	}
	if (memcmp(official_r, gt32_r, sizeof official_r) != 0) {
		for (size_t i = 0; i < sizeof official_r; i++) {
			if (official_r[i] != gt32_r[i]) {
				fprintf(stderr, "recovered-r stage mismatch round=%u byte=%zu "
					"official=%u gt32=%u\n", round, i,
					(unsigned)official_r[i], (unsigned)gt32_r[i]);
				break;
			}
		}
		return 0;
	}
	if (memcmp(official_r, soa_domain_r, sizeof official_r) != 0) {
		fprintf(stderr, "SoA-domain recovered-r mismatch round=%u\n", round);
		return 0;
	}
	if (memcmp(official_r, q24_decode_r, sizeof official_r) != 0) {
		fprintf(stderr, "Q24 decode recovered-r mismatch round=%u\n", round);
		return 0;
	}
	if (memcmp(official_r, q24_pack_r, sizeof official_r) != 0) {
		fprintf(stderr, "Q24 pack recovered-r mismatch round=%u\n", round);
		return 0;
	}
	return 1;
}

static int check_round(unsigned round)
{
	uint8_t pk[CRYPTO_PUBLICKEYBYTES];
	uint8_t sk[CRYPTO_SECRETKEYBYTES];
	uint8_t ct[CRYPTO_CIPHERTEXTBYTES];
	uint8_t ss[CRYPTO_BYTES];
	uint8_t modified[CRYPTO_CIPHERTEXTBYTES];
	uint8_t modified_sk[CRYPTO_SECRETKEYBYTES];
	char name[64];

	reset_rng(1, round);
	if (crypto_kem_keypair(pk, sk) != 0)
		return 0;
	reset_rng(2, round);
	if (crypto_kem_enc(ct, ss, pk) != 0)
		return 0;
	if (!compare_trace(ct, sk, round))
		return 0;

	(void)snprintf(name, sizeof name, "valid-%u", round);
	if (!compare_decap(name, ct, sk))
		return 0;

	memcpy(modified, ct, sizeof modified);
	make_first_slot_noncanonical(modified);
	(void)snprintf(name, sizeof name, "noncanonical-%u", round);
	if (!compare_decap(name, modified, sk))
		return 0;

	memcpy(modified_sk, sk, sizeof modified_sk);
	make_first_slot_noncanonical(modified_sk);
	(void)snprintf(name, sizeof name, "noncanonical-f-%u", round);
	if (!compare_decap(name, ct, modified_sk))
		return 0;

	memcpy(modified_sk, sk, sizeof modified_sk);
	make_first_slot_noncanonical(modified_sk + NTRUPLUS_POLYBYTES);
	(void)snprintf(name, sizeof name, "noncanonical-hinv-%u", round);
	if (!compare_decap(name, ct, modified_sk))
		return 0;

	for (unsigned bit_case = 0; bit_case < 4; bit_case++) {
		memcpy(modified, ct, sizeof modified);
		const size_t byte = (size_t)((97U * bit_case + 53U * round)
			% CRYPTO_CIPHERTEXTBYTES);
		modified[byte] ^= (uint8_t)(1U << ((bit_case + round) & 7U));
		(void)snprintf(name, sizeof name, "bitflip-%u-%u", round, bit_case);
		if (!compare_decap(name, modified, sk))
			return 0;
	}

	return 1;
}

int main(void)
{
	unsigned failures = 0;
	if (!check_serialized_ntt_boundary())
		failures++;
	for (unsigned round = 0; round < ROUNDS; round++)
		failures += (unsigned)!check_round(round);
	printf("gt32-tile4-kem-candidate: decap-byte-exact-rounds=%u "
		"malformed-per-round=7 failures=%u\n", ROUNDS, failures);
	return failures == 0U ? 0 : 1;
}
