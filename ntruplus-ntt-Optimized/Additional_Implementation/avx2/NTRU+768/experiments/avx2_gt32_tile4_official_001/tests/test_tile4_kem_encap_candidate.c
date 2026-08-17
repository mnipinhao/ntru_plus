#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "api.h"
#include "kat/rng.h"
#include "poly.h"
#include "symmetric.h"
#include "util.h"

#include "tile4_kem_encap_candidate.h"

static int official_enc_derand(uint8_t *ct, uint8_t *ss,
	const uint8_t *pk, const uint8_t *coins)
{
	uint8_t msg[HASH_H_INBYTES];
	uint8_t buf[HASH_H_OUTBYTES];
	poly c, h, r, m;

	if (poly_frombytes(&h, pk) != 0) {
		memset(ct, 0, NTRUPLUS_CIPHERTEXTBYTES);
		secure_clear(ss, NTRUPLUS_SSBYTES);
		return 1;
	}
	memcpy(msg, coins, NTRUPLUS_N / 8);
	hash_f(msg + NTRUPLUS_N / 8, pk);
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
	memcpy(ss, buf, NTRUPLUS_SSBYTES);
	secure_clear(msg, sizeof msg);
	secure_clear(buf, sizeof buf);
	secure_clear(&r, sizeof r);
	secure_clear(&m, sizeof m);
	return 0;
}

static void set_serialized_word(uint8_t *bytes, unsigned index,
	uint16_t value)
{
	const unsigned pair = index / 2U;
	if ((index & 1U) == 0U) {
		bytes[3U * pair] = (uint8_t)value;
		bytes[3U * pair + 1U] = (uint8_t)((bytes[3U * pair + 1U] & 0xf0U)
			| (uint8_t)(value >> 8));
	} else {
		bytes[3U * pair + 1U] = (uint8_t)((bytes[3U * pair + 1U] & 0x0fU)
			| (uint8_t)(value << 4));
		bytes[3U * pair + 2U] = (uint8_t)(value >> 4);
	}
}

int main(void)
{
	uint8_t entropy[48];
	uint8_t pk[CRYPTO_PUBLICKEYBYTES];
	uint8_t sk[CRYPTO_SECRETKEYBYTES];
	uint8_t bad_pk[CRYPTO_PUBLICKEYBYTES];
	uint8_t coins[NTRUPLUS_N / 8];
	uint8_t off_ct[CRYPTO_CIPHERTEXTBYTES];
	uint8_t gt_ct[CRYPTO_CIPHERTEXTBYTES];
	uint8_t off_ss[CRYPTO_BYTES];
	uint8_t gt_ss[CRYPTO_BYTES];

	for (size_t i = 0; i < sizeof entropy; i++)
		entropy[i] = (uint8_t)(17U + 29U * i);
	randombytes_init(entropy, NULL, 256);
	if (crypto_kem_keypair(pk, sk) != 0) {
		fprintf(stderr, "keypair setup failed\n");
		return 1;
	}
	for (unsigned trial = 0; trial < 100; trial++) {
		for (size_t i = 0; i < sizeof coins; i++)
			coins[i] = (uint8_t)(trial * 73U + i * 19U);
		const int off = official_enc_derand(off_ct, off_ss, pk, coins);
		const int gt = crypto_kem_enc_derand_gt32_candidate(gt_ct, gt_ss,
			pk, coins);
		if (off != gt || memcmp(off_ct, gt_ct, sizeof off_ct) != 0
			|| memcmp(off_ss, gt_ss, sizeof off_ss) != 0) {
			fprintf(stderr, "valid differential failed trial=%u off=%d gt=%d\n",
				trial, off, gt);
			return 1;
		}
	}
	for (unsigned slot = 0; slot < NTRUPLUS_N; slot++) {
		memcpy(bad_pk, pk, sizeof bad_pk);
		set_serialized_word(bad_pk, slot, NTRUPLUS_Q);
		memset(off_ct, 0xa5, sizeof off_ct);
		memset(gt_ct, 0x5a, sizeof gt_ct);
		memset(off_ss, 0xa5, sizeof off_ss);
		memset(gt_ss, 0x5a, sizeof gt_ss);
		const int off = official_enc_derand(off_ct, off_ss, bad_pk, coins);
		const int gt = crypto_kem_enc_derand_gt32_candidate(gt_ct, gt_ss,
			bad_pk, coins);
		if (off != 1 || gt != 1 || memcmp(off_ct, gt_ct, sizeof off_ct) != 0
			|| memcmp(off_ss, gt_ss, sizeof off_ss) != 0) {
			fprintf(stderr, "noncanonical differential failed slot=%u\n", slot);
			return 1;
		}
	}
	puts("GT32 encap candidate differential: pass");
	return 0;
}
