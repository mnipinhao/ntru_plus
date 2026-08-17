#include <stdint.h>

#include "crypto_kem.h"
#include "api.h"
#include "params.h"
#include "randombytes.h"
#include "util.h"

extern int crypto_kem_keypair_gt32_production_candidate(
	uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);
extern int crypto_kem_enc_derand_gt32_candidate(
	uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8]);
extern int crypto_kem_dec_gt32_native_rcheck_candidate(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);

int crypto_kem_keypair(unsigned char *pk, unsigned char *sk)
{
	return crypto_kem_keypair_gt32_production_candidate(pk, sk);
}

int crypto_kem_enc(unsigned char *ct, unsigned char *ss,
	const unsigned char *pk)
{
	uint8_t coins[NTRUPLUS_N / 8];
	int result;

	randombytes(coins, sizeof coins);
	result = crypto_kem_enc_derand_gt32_candidate(ct, ss, pk, coins);
	secure_clear(coins, sizeof coins);
	return result;
}

int crypto_kem_dec(unsigned char *ss, const unsigned char *ct,
	const unsigned char *sk)
{
	return crypto_kem_dec_gt32_native_rcheck_candidate(ss, ct, sk);
}
