#include <stdint.h>

#include "api.h"
#include "internal.h"
#include "late066.h"
#include "randombytes.h"
#include "util.h"

int crypto_kem_keypair(unsigned char *pk, unsigned char *sk)
{
	return ntruplus768_keypair_impl(pk, sk);
}
int crypto_kem_enc(unsigned char *ct, unsigned char *ss,
	const unsigned char *pk)
{
	uint8_t coins[NTRUPLUS_N / 8];
	int result;
	randombytes(coins, sizeof coins);
	result = ntruplus768_enc_derand_impl(ct, ss, pk, coins);
	secure_clear(coins, sizeof coins);
	return result;
}

int crypto_kem_dec(unsigned char *ss, const unsigned char *ct,
	const unsigned char *sk)
{
	return late066_dec_candidate(ss, ct, sk);
}
