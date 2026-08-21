#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "internal.h"
#include "poly.h"
#include "symmetric.h"
#include "util.h"
#include "working_set_057.h"

typedef struct __attribute__((aligned(64))) {
	int16_t h[NTRUPLUS_N];
	int16_t r[NTRUPLUS_N];
	int16_t m[NTRUPLUS_N];
	int16_t c[NTRUPLUS_N];
	int16_t work[NTRUPLUS_N];
} five_poly_scratch;

typedef struct __attribute__((aligned(64))) {
	int16_t h[NTRUPLUS_N];
	int16_t r[NTRUPLUS_N];
	int16_t m[NTRUPLUS_N];
	int16_t work[NTRUPLUS_N];
} four_poly_scratch;

static int reject(uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	uint8_t ss[NTRUPLUS_SSBYTES])
{
	memset(ct, 0, NTRUPLUS_CIPHERTEXTBYTES);
	secure_clear(ss, NTRUPLUS_SSBYTES);
	return 1;
}

static inline void forward(int16_t out[NTRUPLUS_N],
	int16_t landing[NTRUPLUS_N], const int16_t in[NTRUPLUS_N])
{
	ntruplus768_ntt_frontend_avx2(landing, in);
	ntruplus768_ntt_m_avx2(out, landing);
}

static __attribute__((noinline)) int encap_body(
	uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8], int16_t h[NTRUPLUS_N],
	int16_t r[NTRUPLUS_N], int16_t m[NTRUPLUS_N],
	int16_t work[NTRUPLUS_N], int16_t r_landing[NTRUPLUS_N],
	int16_t m_landing[NTRUPLUS_N], int16_t result[NTRUPLUS_N])
{
	uint8_t msg[HASH_H_INBYTES];
	uint8_t hashbuf[HASH_H_OUTBYTES];

	if (ntruplus768_unpack_m_avx2(h, pk) != 0)
		return reject(ct, ss);
	memcpy(msg, coins, NTRUPLUS_N / 8);
	hash_f(msg + NTRUPLUS_N / 8, pk);
	hash_h(hashbuf, msg);
	poly_cbd1((poly *)(void *)work, hashbuf + NTRUPLUS_SYMBYTES);
	forward(r, r_landing, work);
	ntruplus768_pack_m_lazy10788_avx2(ct, r);
	hash_g(ct, ct);
	poly_sotp_encode((poly *)(void *)work, msg, ct);
	forward(m, m_landing, work);
	ntruplus768_basemul_general_m_avx2(result, h, r);
	poly_add((poly *)(void *)result, (const poly *)(const void *)result,
		(const poly *)(const void *)m);
	ntruplus768_pack_m_highrange12699_avx2(ct, result);
	memcpy(ss, hashbuf, NTRUPLUS_SSBYTES);
	secure_clear(msg, sizeof msg);
	secure_clear(hashbuf, sizeof hashbuf);
	secure_clear(r, NTRUPLUS_N * sizeof(int16_t));
	secure_clear(m, NTRUPLUS_N * sizeof(int16_t));
	return 0;
}

__attribute__((noinline))
int working_set_057_reserved(enum working_set_057_profile profile,
	uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES], uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8])
{
	five_poly_scratch scratch;

	if (profile == WORKING_SET_057_A_FIVE_ACTIVE)
		return encap_body(ct, ss, pk, coins, scratch.h, scratch.r,
			scratch.m, scratch.work, scratch.c, scratch.c, scratch.c);
	if (profile == WORKING_SET_057_B_FOUR_ACTIVE_RESERVED)
		return encap_body(ct, ss, pk, coins, scratch.h, scratch.r,
			scratch.m, scratch.work, scratch.r, scratch.m, scratch.work);
	return reject(ct, ss);
}

__attribute__((noinline))
int working_set_057_compact(uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8])
{
	four_poly_scratch scratch;

	return encap_body(ct, ss, pk, coins, scratch.h, scratch.r, scratch.m,
		scratch.work, scratch.r, scratch.m, scratch.work);
}
