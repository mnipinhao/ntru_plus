#include <stddef.h>
#include <stdint.h>

#include "internal.h"
#include "poly.h"
#include "symmetric.h"
#include "util.h"

typedef struct __attribute__((aligned(64))) {
	int16_t h[NTRUPLUS_N];
	int16_t r[NTRUPLUS_N];
	int16_t m[NTRUPLUS_N];
	int16_t c[NTRUPLUS_N];
} encap_scratch;

static void forward_m(int16_t out[NTRUPLUS_N],
	int16_t frontend[NTRUPLUS_N], const int16_t in[NTRUPLUS_N])
{
	ntruplus768_ntt_frontend_avx2(frontend, in);
	ntruplus768_ntt_m_avx2(out, frontend);
}

int ntruplus768_enc_derand_impl(
	uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8])
{
	uint8_t msg[HASH_H_INBYTES];
	uint8_t buf[HASH_H_OUTBYTES];
	encap_scratch scratch;

	if (ntruplus768_unpack_m_avx2(scratch.h, pk) != 0) {
		for (size_t i = 0; i < NTRUPLUS_CIPHERTEXTBYTES; i++)
			ct[i] = 0;
		secure_clear(ss, NTRUPLUS_SSBYTES);
		return 1;
	}

	for (size_t i = 0; i < NTRUPLUS_N / 8; i++)
		msg[i] = coins[i];
	hash_f(msg + NTRUPLUS_N / 8, pk);
	hash_h(buf, msg);

	poly_cbd1((poly *)(void *)scratch.m,
		buf + NTRUPLUS_SYMBYTES);
	forward_m(scratch.r, scratch.c, scratch.m);
	ntruplus768_pack_m_lazy10788_avx2(ct, scratch.r);
	hash_g(ct, ct);

	poly_sotp_encode((poly *)(void *)scratch.m, msg, ct);
	/* frontend consumes m before ntt_m overwrites it with message M. */
	forward_m(scratch.m, scratch.c, scratch.m);
	ntruplus768_basemul_general_m_avx2(scratch.c, scratch.h, scratch.r);
	/*
	 * product + message is a semantic M/e=0 value, but is deliberately
	 * not materialized as a polynomial.  Addition occurs before the
	 * existing Q24 transpose and canonicalization under the validated
	 * |product + message| <= 12699 contract.
	 */
	ntruplus768_pack_m_sum_highrange12699_avx2(
		ct, scratch.c, scratch.m);

	for (size_t i = 0; i < NTRUPLUS_SSBYTES; i++)
		ss[i] = buf[i];

	secure_clear(msg, sizeof msg);
	secure_clear(buf, sizeof buf);
	secure_clear(scratch.r, sizeof scratch.r);
	secure_clear(scratch.m, sizeof scratch.m);
	return 0;
}
