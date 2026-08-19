#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "encap_b3_addm_032.h"
#include "internal.h"
#include "poly.h"
#include "symmetric.h"
#include "util.h"

typedef struct __attribute__((aligned(64))) {
	int16_t h[NTRUPLUS_N];
	int16_t r[NTRUPLUS_N];
	int16_t m[NTRUPLUS_N];
	int16_t work[NTRUPLUS_N];
} scratch_032;

void gt32_032_b3_control_normal(int16_t *, const int16_t *, const int16_t *);
void gt32_032_b3_addm_normal(int16_t *, const int16_t *, const int16_t *,
	const int16_t *);
void gt32_032_b3_control_reversed(int16_t *, const int16_t *, const int16_t *);
void gt32_032_b3_addm_reversed(int16_t *, const int16_t *, const int16_t *,
	const int16_t *);

static void forward_in_place(int16_t out[NTRUPLUS_N],
	const int16_t in[NTRUPLUS_N])
{
	ntruplus768_ntt_frontend_avx2(out, in);
	ntruplus768_ntt_m_avx2(out, out);
}

__attribute__((noinline))
void gt32_032_local_control_normal(int16_t out[NTRUPLUS_N],
	const int16_t h[NTRUPLUS_N], const int16_t r[NTRUPLUS_N],
	const int16_t m[NTRUPLUS_N])
{
	gt32_032_b3_control_normal(out, h, r);
	poly_add((poly *)(void *)out, (const poly *)(const void *)out,
		(const poly *)(const void *)m);
}

__attribute__((noinline))
void gt32_032_local_candidate_normal(int16_t out[NTRUPLUS_N],
	const int16_t h[NTRUPLUS_N], const int16_t r[NTRUPLUS_N],
	const int16_t m[NTRUPLUS_N])
{
	gt32_032_b3_addm_normal(out, h, r, m);
}

__attribute__((noinline))
void gt32_032_local_control_reversed(int16_t out[NTRUPLUS_N],
	const int16_t h[NTRUPLUS_N], const int16_t r[NTRUPLUS_N],
	const int16_t m[NTRUPLUS_N])
{
	gt32_032_b3_control_reversed(out, h, r);
	poly_add((poly *)(void *)out, (const poly *)(const void *)out,
		(const poly *)(const void *)m);
}

__attribute__((noinline))
void gt32_032_local_candidate_reversed(int16_t out[NTRUPLUS_N],
	const int16_t h[NTRUPLUS_N], const int16_t r[NTRUPLUS_N],
	const int16_t m[NTRUPLUS_N])
{
	gt32_032_b3_addm_reversed(out, h, r, m);
}

#define DEFINE_ENCAP(name, local_b3) \
__attribute__((noinline)) \
int name(uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES], \
	uint8_t ss[NTRUPLUS_SSBYTES], \
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES], \
	const uint8_t coins[NTRUPLUS_N / 8]) \
{ \
	uint8_t msg[HASH_H_INBYTES]; \
	uint8_t buf[HASH_H_OUTBYTES]; \
	scratch_032 scratch; \
	if (ntruplus768_unpack_m_avx2(scratch.h, pk) != 0) { \
		memset(ct, 0, NTRUPLUS_CIPHERTEXTBYTES); \
		secure_clear(ss, NTRUPLUS_SSBYTES); \
		return 1; \
	} \
	memcpy(msg, coins, NTRUPLUS_N / 8); \
	hash_f(msg + NTRUPLUS_N / 8, pk); \
	hash_h(buf, msg); \
	poly_cbd1((poly *)(void *)scratch.work, \
		buf + NTRUPLUS_SYMBYTES); \
	forward_in_place(scratch.r, scratch.work); \
	ntruplus768_pack_m_lazy10788_avx2(ct, scratch.r); \
	hash_g(ct, ct); \
	poly_sotp_encode((poly *)(void *)scratch.work, msg, ct); \
	forward_in_place(scratch.m, scratch.work); \
	local_b3(scratch.work, scratch.h, scratch.r, scratch.m); \
	ntruplus768_pack_m_highrange12699_avx2(ct, scratch.work); \
	memcpy(ss, buf, NTRUPLUS_SSBYTES); \
	secure_clear(msg, sizeof msg); \
	secure_clear(buf, sizeof buf); \
	secure_clear(scratch.r, sizeof scratch.r); \
	secure_clear(scratch.m, sizeof scratch.m); \
	return 0; \
}

DEFINE_ENCAP(gt32_032_encap_control_normal, gt32_032_local_control_normal)
DEFINE_ENCAP(gt32_032_encap_candidate_normal, gt32_032_local_candidate_normal)
DEFINE_ENCAP(gt32_032_encap_candidate_reversed, gt32_032_local_candidate_reversed)
DEFINE_ENCAP(gt32_032_encap_control_reversed, gt32_032_local_control_reversed)
