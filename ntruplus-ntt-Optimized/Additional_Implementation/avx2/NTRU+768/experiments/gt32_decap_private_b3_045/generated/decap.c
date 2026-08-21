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
} decap_scratch;

static int recover_message_and_r(uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	decap_scratch *scratch,
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	int decode_result = ntruplus768_unpack3_m_avx2(scratch->c,
		scratch->aux, scratch->hinv, ct, sk);
	declassify(&decode_result, sizeof decode_result);
	if (decode_result != 0)
		return 1;

	ntruplus768_basemul_scale_m_avx2(scratch->m,
		scratch->c, scratch->aux);
	ntruplus768_invntt_m_avx2(scratch->work, scratch->m);
	ntruplus768_invntt_tail_avx2(scratch->m, scratch->work);
	poly_crepmod3((poly *)(void *)scratch->m);

	ntruplus768_ntt_frontend_avx2(scratch->aux, scratch->m);
	ntruplus768_ntt_m_avx2(scratch->work, scratch->aux);
	poly_sub((poly *)(void *)scratch->c,
		(const poly *)(const void *)scratch->c,
		(const poly *)(const void *)scratch->work);
	ntruplus768_basemul_general_m_decap_avx2(scratch->aux,
		scratch->c, scratch->hinv);
	ntruplus768_pack_m_centered_avx2(recovered_r, scratch->aux);
	return 0;
}

__attribute__((aligned(32)))
int ntruplus768_dec_impl(uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	uint8_t msg[NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES];
	uint8_t recovered_r[NTRUPLUS_POLYBYTES];
	uint8_t hash_g_out[NTRUPLUS_N / 4];
	uint8_t hash_h_out[NTRUPLUS_POLYBYTES + NTRUPLUS_SYMBYTES];
	decap_scratch scratch;
	int fail = 1;

	if (recover_message_and_r(recovered_r, &scratch, ct, sk) != 0) {
		secure_clear(ss, NTRUPLUS_SSBYTES);
		goto cleanup;
	}

	hash_g(hash_g_out, recovered_r);
	fail = poly_sotp_decode(msg,
		(const poly *)(const void *)scratch.m, hash_g_out);
	memcpy(msg + NTRUPLUS_N / 8,
		sk + 2 * NTRUPLUS_POLYBYTES, NTRUPLUS_SYMBYTES);
	hash_h(hash_h_out, msg);

	/* Keep recovered r-hat in aux and compare the derived transform directly
	 * in the common M/e=0 domain; no second serialization is required. */
	poly_cbd1((poly *)(void *)scratch.m,
		hash_h_out + NTRUPLUS_SSBYTES);
	ntruplus768_ntt_frontend_avx2(scratch.work, scratch.m);
	ntruplus768_ntt_m_avx2(scratch.hinv, scratch.work);
	fail |= ntruplus768_equal_m_modq12699_avx2(scratch.aux,
		scratch.hinv);

	for (size_t i = 0; i < NTRUPLUS_SSBYTES; i++)
		ss[i] = (uint8_t)(hash_h_out[i] & (uint8_t)~(uint8_t)(-fail));

cleanup:
	secure_clear(msg, sizeof msg);
	secure_clear(recovered_r, sizeof recovered_r);
	secure_clear(hash_g_out, sizeof hash_g_out);
	secure_clear(hash_h_out, sizeof hash_h_out);
	secure_clear(&scratch, sizeof scratch);
	return fail;
}
