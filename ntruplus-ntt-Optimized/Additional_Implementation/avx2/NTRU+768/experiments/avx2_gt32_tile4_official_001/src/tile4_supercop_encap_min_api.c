#include <stdint.h>

#include "crypto_kem.h"
#include "api.h"
#include "params.h"
#include "randombytes.h"
#include "util.h"

extern int crypto_kem_keypair_official_control(unsigned char *, unsigned char *);
extern int crypto_kem_dec_official_unused(unsigned char *, const unsigned char *,
	const unsigned char *);
extern int crypto_kem_enc_derand_gt32_candidate(uint8_t *, uint8_t *,
	const uint8_t *, const uint8_t *);

int crypto_kem_keypair(unsigned char *pk, unsigned char *sk)
{
	return crypto_kem_keypair_official_control(pk, sk);
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
	return crypto_kem_dec_official_unused(ss, ct, sk);
}
