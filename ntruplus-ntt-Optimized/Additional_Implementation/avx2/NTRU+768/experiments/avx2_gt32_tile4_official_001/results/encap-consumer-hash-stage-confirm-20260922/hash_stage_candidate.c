#include <stddef.h>
#include <stdint.h>

#include "internal.h"
#include "poly.h"
#include "symmetric.h"
#include "util.h"


#include "fips202.h"
/* Keep the original hash_g-sized buffer and its clearing, but have the
 * existing M serializer produce directly into its final hash input slot. */
__attribute__((noinline)) void ntruplus768_hash_stage_research(uint8_t *out,
                                                            const int16_t *r)
{
    uint8_t data[1 + HASH_G_INBYTES];
    data[0] = 0x01;
    ntruplus768_pack_m_lazy10788_avx2(data + 1, r);
    shake256(out, HASH_G_OUTBYTES, data, sizeof data);
    secure_clear(data, sizeof data);
}

typedef struct __attribute__((aligned(64))) {
	int16_t h[NTRUPLUS_N];
	int16_t r[NTRUPLUS_N];
	int16_t m[NTRUPLUS_N];
	int16_t c[NTRUPLUS_N];
	int16_t work[NTRUPLUS_N];
} encap_scratch;

static void forward_m(int16_t out[NTRUPLUS_N],
	int16_t frontend[NTRUPLUS_N], const int16_t in[NTRUPLUS_N])
{
	ntruplus768_ntt_frontend_avx2(frontend, in);
	ntruplus768_ntt_m_avx2(out, frontend);
}

int ntruplus768_hash_stage_enc_derand(
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

	poly_cbd1((poly *)(void *)scratch.work,
		buf + NTRUPLUS_SYMBYTES);
	forward_m(scratch.r, scratch.c, scratch.work);
	ntruplus768_hash_stage_research(ct, scratch.r);

	poly_sotp_encode((poly *)(void *)scratch.work, msg, ct);
	forward_m(scratch.m, scratch.c, scratch.work);
	ntruplus768_basemul_general_m_avx2(scratch.c, scratch.h, scratch.r);
	poly_add((poly *)(void *)scratch.c,
		(const poly *)(const void *)scratch.c,
		(const poly *)(const void *)scratch.m);
	ntruplus768_pack_m_highrange12699_avx2(ct, scratch.c);

	for (size_t i = 0; i < NTRUPLUS_SSBYTES; i++)
		ss[i] = buf[i];

	secure_clear(msg, sizeof msg);
	secure_clear(buf, sizeof buf);
	secure_clear(scratch.r, sizeof scratch.r);
	secure_clear(scratch.m, sizeof scratch.m);
	return 0;
}
