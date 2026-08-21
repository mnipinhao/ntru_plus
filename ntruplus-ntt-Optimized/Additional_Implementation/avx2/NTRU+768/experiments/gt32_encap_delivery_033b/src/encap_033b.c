#include <stdint.h>
#include <string.h>

#include "internal.h"
#include "poly.h"
#include "symmetric.h"
#include "util.h"

typedef struct __attribute__((aligned(64))) {
	int16_t h[NTRUPLUS_N];
	int16_t r[NTRUPLUS_N];
	int16_t m[NTRUPLUS_N];
	int16_t work[NTRUPLUS_N];
} encap_scratch;

static void forward_in_place(int16_t out[NTRUPLUS_N],
	const int16_t in[NTRUPLUS_N])
{
	ntruplus768_ntt_frontend_avx2(out, in);
	ntruplus768_ntt_m_avx2(out, out);
}

__attribute__((noinline))
int gt033b_encap(uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8])
{
	uint8_t msg[HASH_H_INBYTES];
	uint8_t buf[HASH_H_OUTBYTES];
	encap_scratch scratch;

	if (ntruplus768_unpack_m_avx2(scratch.h, pk) != 0) {
		memset(ct, 0, NTRUPLUS_CIPHERTEXTBYTES);
		secure_clear(ss, NTRUPLUS_SSBYTES);
		return 1;
	}
	memcpy(msg, coins, NTRUPLUS_N / 8);
	hash_f(msg + NTRUPLUS_N / 8, pk);
	hash_h(buf, msg);
	poly_cbd1((poly *)(void *)scratch.work, buf + NTRUPLUS_SYMBYTES);
	forward_in_place(scratch.r, scratch.work);
	ntruplus768_pack_m_lazy10788_avx2(ct, scratch.r);
	hash_g(ct, ct);
	poly_sotp_encode((poly *)(void *)scratch.work, msg, ct);
	forward_in_place(scratch.m, scratch.work);
	ntruplus768_basemul_general_m_avx2(scratch.work, scratch.h, scratch.r);
	poly_add((poly *)(void *)scratch.work,
		(const poly *)(const void *)scratch.work,
		(const poly *)(const void *)scratch.m);
	ntruplus768_pack_m_highrange12699_avx2(ct, scratch.work);
	memcpy(ss, buf, NTRUPLUS_SSBYTES);
	secure_clear(msg, sizeof msg);
	secure_clear(buf, sizeof buf);
	secure_clear(scratch.r, sizeof scratch.r);
	secure_clear(scratch.m, sizeof scratch.m);
	return 0;
}

