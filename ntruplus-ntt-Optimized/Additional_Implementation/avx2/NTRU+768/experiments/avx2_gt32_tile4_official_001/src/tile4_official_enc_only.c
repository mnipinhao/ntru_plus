/* Official-main encapsulation extracted as an operation-specific hybrid edge. */
#include <stddef.h>
#include <stdint.h>

#include "api.h"
#include "params.h"
#include "poly.h"
#include "randombytes.h"
#include "symmetric.h"
#include "util.h"

static int official_enc_derand(uint8_t *ct, uint8_t *ss, const uint8_t *pk,
	const uint8_t *coins)
{
	uint8_t msg[HASH_H_INBYTES];
	uint8_t buf[HASH_H_OUTBYTES];
	poly c, h, r, m;

	if (poly_frombytes(&h, pk)) {
		for (size_t i = 0; i < NTRUPLUS_CIPHERTEXTBYTES; i++)
			ct[i] = 0;
		secure_clear(ss, NTRUPLUS_SSBYTES);
		return 1;
	}
	for (size_t i = 0; i < NTRUPLUS_N / 8; i++)
		msg[i] = coins[i];
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
	for (size_t i = 0; i < NTRUPLUS_SSBYTES; i++)
		ss[i] = buf[i];
	secure_clear(msg, sizeof msg);
	secure_clear(buf, sizeof buf);
	secure_clear(&r, sizeof r);
	secure_clear(&m, sizeof m);
	return 0;
}

int crypto_kem_enc_official_hybrid(unsigned char *ct, unsigned char *ss,
	const unsigned char *pk)
{
	uint8_t coins[NTRUPLUS_N / 8];
	int result;

	randombytes(coins, sizeof coins);
	result = official_enc_derand(ct, ss, pk, coins);
	secure_clear(coins, sizeof coins);
	return result;
}
