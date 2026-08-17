#include <stdint.h>

#include "crypto_kem.h"

extern int crypto_kem_keypair_gt32_production_candidate(uint8_t *, uint8_t *);
extern int crypto_kem_enc_official_unused(unsigned char *, unsigned char *,
	const unsigned char *);
extern int crypto_kem_dec_official_unused(unsigned char *, const unsigned char *,
	const unsigned char *);

int crypto_kem_keypair(unsigned char *pk, unsigned char *sk)
{
	return crypto_kem_keypair_gt32_production_candidate(pk, sk);
}

int crypto_kem_enc(unsigned char *ct, unsigned char *ss,
	const unsigned char *pk)
{
	return crypto_kem_enc_official_unused(ct, ss, pk);
}

int crypto_kem_dec(unsigned char *ss, const unsigned char *ct,
	const unsigned char *sk)
{
	return crypto_kem_dec_official_unused(ss, ct, sk);
}
