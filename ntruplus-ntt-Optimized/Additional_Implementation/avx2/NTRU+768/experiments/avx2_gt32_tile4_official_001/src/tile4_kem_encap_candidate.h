#ifndef TILE4_KEM_ENCAP_CANDIDATE_H
#define TILE4_KEM_ENCAP_CANDIDATE_H

#include <stdint.h>

#include "api.h"

/* Benchmark-only, deterministic full encapsulation candidate. */
int crypto_kem_enc_derand_gt32_candidate(
	uint8_t ct[CRYPTO_CIPHERTEXTBYTES],
	uint8_t ss[CRYPTO_BYTES],
	const uint8_t pk[CRYPTO_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8]);
int crypto_kem_enc_derand_gt32_q24_sum_candidate(
	uint8_t ct[CRYPTO_CIPHERTEXTBYTES], uint8_t ss[CRYPTO_BYTES],
	const uint8_t pk[CRYPTO_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8]);
int crypto_kem_enc_derand_gt32_f14_candidate(
	uint8_t ct[CRYPTO_CIPHERTEXTBYTES], uint8_t ss[CRYPTO_BYTES],
	const uint8_t pk[CRYPTO_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8]);
int crypto_kem_enc_derand_gt32_tf1_candidate(
	uint8_t ct[CRYPTO_CIPHERTEXTBYTES], uint8_t ss[CRYPTO_BYTES],
	const uint8_t pk[CRYPTO_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8]);
int crypto_kem_enc_derand_gt32_f14_tf1_candidate(
	uint8_t ct[CRYPTO_CIPHERTEXTBYTES], uint8_t ss[CRYPTO_BYTES],
	const uint8_t pk[CRYPTO_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8]);

#endif
