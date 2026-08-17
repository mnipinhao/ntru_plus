#include <stdint.h>
#include "crypto_kem.h"
#include "api.h"
#include "params.h"

extern int crypto_kem_keypair_official_control(unsigned char *, unsigned char *);
extern int crypto_kem_enc_official_hybrid(unsigned char *, unsigned char *,
	const unsigned char *);
extern int crypto_kem_dec_gt32_native_rcheck_candidate(uint8_t *,
	const uint8_t *, const uint8_t *);

int crypto_kem_keypair(unsigned char *pk, unsigned char *sk)
{
	return crypto_kem_keypair_official_control(pk, sk);
}

int crypto_kem_enc(unsigned char *ct, unsigned char *ss,
	const unsigned char *pk)
{
	return crypto_kem_enc_official_hybrid(ct, ss, pk);
}

int crypto_kem_dec(unsigned char *ss, const unsigned char *ct,
	const unsigned char *sk)
{
	return crypto_kem_dec_gt32_native_rcheck_candidate(ss, ct, sk);
}
