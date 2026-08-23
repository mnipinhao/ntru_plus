#include "late067.h"

int crypto_kem_dec(unsigned char *ss, const unsigned char *ct,
	const unsigned char *sk)
{
	return crypto_kem_dec_latesoa(ss, ct, sk);
}
