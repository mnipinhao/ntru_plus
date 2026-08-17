#include <stdint.h>

#include "crypto_kem.h"
#include "api.h"
#include "params.h"
#include "randombytes.h"
#include "util.h"

#include "gt32_native_rcheck_select.h"

extern int crypto_kem_keypair_gt32_production_candidate(uint8_t *, uint8_t *);
extern int crypto_kem_enc_derand_gt32_candidate(uint8_t *, uint8_t *,
	const uint8_t *, const uint8_t *);
extern int crypto_kem_dec_gt32_global_inverse_candidate(uint8_t *,
	const uint8_t *, const uint8_t *);
extern int crypto_kem_dec_gt32_native_rcheck_candidate(uint8_t *,
	const uint8_t *, const uint8_t *);

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
#if GT32_NATIVE_RCHECK_SELECT
	return crypto_kem_dec_gt32_native_rcheck_candidate(ss, ct, sk);
#else
	return crypto_kem_dec_gt32_global_inverse_candidate(ss, ct, sk);
#endif
}
