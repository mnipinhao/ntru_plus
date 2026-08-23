#include "late066.h"

#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "internal.h"
#include "poly.h"
#include "symmetric.h"
#include "util.h"

#ifdef SUPERCOP
#include "crypto_declassify.h"
#define declassify crypto_declassify
#else
#define declassify(value, length) ((void)(value), (void)(length))
#endif

typedef struct __attribute__((aligned(64))) {
	int16_t c[NTRUPLUS_N];
	int16_t aux[NTRUPLUS_N];
	int16_t hinv[NTRUPLUS_N];
	int16_t m[NTRUPLUS_N];
	int16_t work[NTRUPLUS_N];
} late066_decap_scratch;

typedef void (*late066_first_product_fn)(late066_decap_scratch *scratch);

void late066_post_i1_control(int16_t out[NTRUPLUS_N],
	const int16_t c[NTRUPLUS_N], const int16_t f[NTRUPLUS_N],
	late066_region_scratch *scratch)
{
	ntruplus768_basemul_scale_m_avx2(scratch->product, c, f);
	late066_inverse_prefix_m_to_post_i1_asm(out, scratch->product);
}

void late066_post_i1_candidate(int16_t out[NTRUPLUS_N],
	const int16_t c[NTRUPLUS_N], const int16_t f[NTRUPLUS_N],
	late066_region_scratch *scratch)
{
	(void)scratch;
	late_soa_full_basemul_i2_fused_asm(out, c, f);
}

void late066_crep_control(int16_t out[NTRUPLUS_N],
	const int16_t c[NTRUPLUS_N], const int16_t f[NTRUPLUS_N],
	late066_region_scratch *scratch)
{
	ntruplus768_basemul_scale_m_avx2(scratch->product, c, f);
	ntruplus768_invntt_m_avx2(scratch->inverse_rows, scratch->product);
	ntruplus768_invntt_tail_avx2(out, scratch->inverse_rows);
	poly_crepmod3((poly *)(void *)out);
}

void late066_crep_candidate(int16_t out[NTRUPLUS_N],
	const int16_t c[NTRUPLUS_N], const int16_t f[NTRUPLUS_N],
	late066_region_scratch *scratch)
{
	late_soa_full_basemul_i2_fused_asm(scratch->post_i1, c, f);
	gt32_tile4_attr_inverse_i1_cross3_asm(scratch->inverse_rows,
		scratch->post_i1);
	ntruplus768_invntt_tail_avx2(out, scratch->inverse_rows);
	poly_crepmod3((poly *)(void *)out);
}

static void first_product_control(late066_decap_scratch *scratch)
{
	ntruplus768_basemul_scale_m_avx2(scratch->m,
		scratch->c, scratch->aux);
	ntruplus768_invntt_m_avx2(scratch->work, scratch->m);
	ntruplus768_invntt_tail_avx2(scratch->m, scratch->work);
	poly_crepmod3((poly *)(void *)scratch->m);
}

static void first_product_candidate(late066_decap_scratch *scratch)
{
	late_soa_full_basemul_i2_fused_asm(scratch->m,
		scratch->c, scratch->aux);
	gt32_tile4_attr_inverse_i1_cross3_asm(scratch->work, scratch->m);
	ntruplus768_invntt_tail_avx2(scratch->m, scratch->work);
	poly_crepmod3((poly *)(void *)scratch->m);
}

static int recover_message_and_r_variant(
	uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	late066_decap_scratch *scratch,
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES],
	late066_first_product_fn first_product)
{
	int decode_result = ntruplus768_unpack3_m_avx2(scratch->c,
		scratch->aux, scratch->hinv, ct, sk);
	declassify(&decode_result, sizeof decode_result);
	if (decode_result != 0)
		return 1;

	first_product(scratch);
	ntruplus768_ntt_frontend_avx2(scratch->aux, scratch->m);
	ntruplus768_ntt_m_avx2(scratch->work, scratch->aux);
	poly_sub((poly *)(void *)scratch->c,
		(const poly *)(const void *)scratch->c,
		(const poly *)(const void *)scratch->work);
	ntruplus768_basemul_general_m_avx2(scratch->aux,
		scratch->c, scratch->hinv);
	ntruplus768_pack_m_centered_avx2(recovered_r, scratch->aux);
	return 0;
}

static int decode_crep_variant(int16_t out[NTRUPLUS_N],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES],
	late066_first_product_fn first_product)
{
	late066_decap_scratch scratch;
	int fail = ntruplus768_unpack3_m_avx2(scratch.c, scratch.aux,
		scratch.hinv, ct, sk);
	declassify(&fail, sizeof fail);
	if (fail == 0) {
		first_product(&scratch);
		memcpy(out, scratch.m, sizeof scratch.m);
	} else {
		memset(out, 0, NTRUPLUS_N * sizeof(*out));
	}
	secure_clear(&scratch, sizeof scratch);
	return fail;
}

int late066_decode_crep_control(int16_t out[NTRUPLUS_N],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	return decode_crep_variant(out, ct, sk, first_product_control);
}

int late066_decode_crep_candidate(int16_t out[NTRUPLUS_N],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	return decode_crep_variant(out, ct, sk, first_product_candidate);
}

static int recover_only_variant(uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES],
	late066_first_product_fn first_product)
{
	late066_decap_scratch scratch;
	const int fail = recover_message_and_r_variant(recovered_r, &scratch,
		ct, sk, first_product);
	secure_clear(&scratch, sizeof scratch);
	return fail;
}

int late066_recover_only_control(uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	return recover_only_variant(recovered_r, ct, sk, first_product_control);
}

int late066_recover_only_candidate(uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	return recover_only_variant(recovered_r, ct, sk, first_product_candidate);
}

static int recover_trace_variant(uint8_t msg[NTRUPLUS_N / 8],
	uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES],
	late066_first_product_fn first_product)
{
	uint8_t hash_g_out[NTRUPLUS_N / 4];
	late066_decap_scratch scratch;
	int fail = recover_message_and_r_variant(recovered_r, &scratch, ct, sk,
		first_product);
	if (fail == 0) {
		hash_g(hash_g_out, recovered_r);
		fail = poly_sotp_decode(msg,
			(const poly *)(const void *)scratch.m, hash_g_out);
	} else {
		memset(msg, 0, NTRUPLUS_N / 8);
		memset(recovered_r, 0, NTRUPLUS_POLYBYTES);
	}
	secure_clear(hash_g_out, sizeof hash_g_out);
	secure_clear(&scratch, sizeof scratch);
	return fail;
}

int late066_recover_trace_control(uint8_t msg[NTRUPLUS_N / 8],
	uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	return recover_trace_variant(msg, recovered_r, ct, sk,
		first_product_control);
}

int late066_recover_trace_candidate(uint8_t msg[NTRUPLUS_N / 8],
	uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	return recover_trace_variant(msg, recovered_r, ct, sk,
		first_product_candidate);
}

__attribute__((noinline))
static int dec_variant(uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES],
	late066_first_product_fn first_product)
{
	uint8_t msg[NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES];
	uint8_t recovered_r[NTRUPLUS_POLYBYTES];
	uint8_t hash_g_out[NTRUPLUS_N / 4];
	uint8_t hash_h_out[NTRUPLUS_POLYBYTES + NTRUPLUS_SYMBYTES];
	late066_decap_scratch scratch;
	int fail = 1;

	if (recover_message_and_r_variant(recovered_r, &scratch, ct, sk,
		first_product) != 0) {
		secure_clear(ss, NTRUPLUS_SSBYTES);
		goto cleanup;
	}

	hash_g(hash_g_out, recovered_r);
	fail = poly_sotp_decode(msg,
		(const poly *)(const void *)scratch.m, hash_g_out);
	memcpy(msg + NTRUPLUS_N / 8,
		sk + 2 * NTRUPLUS_POLYBYTES, NTRUPLUS_SYMBYTES);
	hash_h(hash_h_out, msg);

	poly_cbd1((poly *)(void *)scratch.m,
		hash_h_out + NTRUPLUS_SSBYTES);
	ntruplus768_ntt_frontend_avx2(scratch.work, scratch.m);
	ntruplus768_ntt_m_avx2(scratch.hinv, scratch.work);
	fail |= ntruplus768_equal_m_modq12699_avx2(scratch.aux,
		scratch.hinv);

	for (size_t i = 0; i < NTRUPLUS_SSBYTES; ++i)
		ss[i] = (uint8_t)(hash_h_out[i]
			& (uint8_t)~(uint8_t)(-fail));

cleanup:
	secure_clear(msg, sizeof msg);
	secure_clear(recovered_r, sizeof recovered_r);
	secure_clear(hash_g_out, sizeof hash_g_out);
	secure_clear(hash_h_out, sizeof hash_h_out);
	secure_clear(&scratch, sizeof scratch);
	return fail;
}

int late066_dec_control(uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	return dec_variant(ss, ct, sk, first_product_control);
}

int late066_dec_candidate(uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	return dec_variant(ss, ct, sk, first_product_candidate);
}
