#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "encap_lifetime_031.h"
#include "internal.h"
#include "poly.h"
#include "symmetric.h"
#include "util.h"

typedef struct __attribute__((aligned(64))) {
	int16_t h[NTRUPLUS_N];
	int16_t r[NTRUPLUS_N];
	int16_t m[NTRUPLUS_N];
	int16_t c[NTRUPLUS_N];
	int16_t work[NTRUPLUS_N];
} control_scratch;

typedef struct __attribute__((aligned(64))) {
	int16_t h[NTRUPLUS_N];
	int16_t r[NTRUPLUS_N];
	int16_t m[NTRUPLUS_N];
	int16_t work[NTRUPLUS_N];
} candidate_scratch;

static void forward_out_of_place(int16_t out[NTRUPLUS_N],
	int16_t frontend[NTRUPLUS_N], const int16_t in[NTRUPLUS_N])
{
	ntruplus768_ntt_frontend_avx2(frontend, in);
	ntruplus768_ntt_m_avx2(out, frontend);
}

static void forward_in_place(int16_t out[NTRUPLUS_N],
	const int16_t in[NTRUPLUS_N])
{
	ntruplus768_ntt_frontend_avx2(out, in);
	ntruplus768_ntt_m_avx2(out, out);
}

static int reject_trace(gt32_encap_031_trace *trace)
{
	memset(trace, 0, sizeof *trace);
	return 1;
}

int gt32_encap_031_control_trace(gt32_encap_031_trace *trace,
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8])
{
	uint8_t msg[HASH_H_INBYTES];
	uint8_t buf[HASH_H_OUTBYTES];
	uint8_t r_serialized[NTRUPLUS_POLYBYTES];
	control_scratch scratch;

	if (ntruplus768_unpack_m_avx2(scratch.h, pk) != 0)
		return reject_trace(trace);
	memcpy(msg, coins, NTRUPLUS_N / 8);
	hash_f(msg + NTRUPLUS_N / 8, pk);
	hash_h(buf, msg);
	poly_cbd1((poly *)(void *)scratch.work, buf + NTRUPLUS_SYMBYTES);
	forward_out_of_place(scratch.r, scratch.c, scratch.work);
	memcpy(trace->r_hat, scratch.r, sizeof trace->r_hat);
	ntruplus768_pack_m_lazy10788_avx2(r_serialized, scratch.r);
	memcpy(trace->r_encoded, r_serialized, sizeof trace->r_encoded);
	hash_g(r_serialized, r_serialized);
	poly_sotp_encode((poly *)(void *)scratch.work, msg, r_serialized);
	forward_out_of_place(scratch.m, scratch.c, scratch.work);
	memcpy(trace->m_hat, scratch.m, sizeof trace->m_hat);
	ntruplus768_basemul_general_m_avx2(scratch.c, scratch.h, scratch.r);
	poly_add((poly *)(void *)scratch.c, (const poly *)(const void *)scratch.c,
		(const poly *)(const void *)scratch.m);
	ntruplus768_pack_m_highrange12699_avx2(trace->ciphertext, scratch.c);
	memcpy(trace->shared_secret, buf, NTRUPLUS_SSBYTES);
	secure_clear(msg, sizeof msg);
	secure_clear(buf, sizeof buf);
	secure_clear(scratch.r, sizeof scratch.r);
	secure_clear(scratch.m, sizeof scratch.m);
	return 0;
}

int gt32_encap_031_candidate_trace(gt32_encap_031_trace *trace,
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8])
{
	uint8_t msg[HASH_H_INBYTES];
	uint8_t buf[HASH_H_OUTBYTES];
	uint8_t r_serialized[NTRUPLUS_POLYBYTES];
	candidate_scratch scratch;

	if (ntruplus768_unpack_m_avx2(scratch.h, pk) != 0)
		return reject_trace(trace);
	memcpy(msg, coins, NTRUPLUS_N / 8);
	hash_f(msg + NTRUPLUS_N / 8, pk);
	hash_h(buf, msg);
	poly_cbd1((poly *)(void *)scratch.work, buf + NTRUPLUS_SYMBYTES);
	forward_in_place(scratch.r, scratch.work);
	memcpy(trace->r_hat, scratch.r, sizeof trace->r_hat);
	ntruplus768_pack_m_lazy10788_avx2(r_serialized, scratch.r);
	memcpy(trace->r_encoded, r_serialized, sizeof trace->r_encoded);
	hash_g(r_serialized, r_serialized);
	poly_sotp_encode((poly *)(void *)scratch.work, msg, r_serialized);
	forward_in_place(scratch.m, scratch.work);
	memcpy(trace->m_hat, scratch.m, sizeof trace->m_hat);
	ntruplus768_basemul_general_m_avx2(scratch.work, scratch.h, scratch.r);
	poly_add((poly *)(void *)scratch.work,
		(const poly *)(const void *)scratch.work,
		(const poly *)(const void *)scratch.m);
	ntruplus768_pack_m_highrange12699_avx2(trace->ciphertext, scratch.work);
	memcpy(trace->shared_secret, buf, NTRUPLUS_SSBYTES);
	secure_clear(msg, sizeof msg);
	secure_clear(buf, sizeof buf);
	secure_clear(scratch.r, sizeof scratch.r);
	secure_clear(scratch.m, sizeof scratch.m);
	return 0;
}

__attribute__((noinline))
int gt32_encap_lifetime_031(uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8])
{
	uint8_t msg[HASH_H_INBYTES];
	uint8_t buf[HASH_H_OUTBYTES];
	candidate_scratch scratch;

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
