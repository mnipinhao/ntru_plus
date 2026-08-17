#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "poly.h"
#include "symmetric.h"
#include "util.h"

#include "tile4_kem_prepared_p0.h"

#ifdef SUPERCOP
#include "crypto_declassify.h"
#define gt32_declassify crypto_declassify
#else
#define gt32_declassify(value, length) ((void)(value), (void)(length))
#endif

#define WORDS GT32_TILE4_POLY_WORDS

typedef struct __attribute__((aligned(64))) {
	int16_t r[WORDS];
	int16_t m[WORDS];
	int16_t c[WORDS];
	int16_t work[WORDS];
} prepared_enc_scratch;

typedef struct __attribute__((aligned(64))) {
	int16_t c[WORDS];
	int16_t aux[WORDS];
	int16_t m[WORDS];
	int16_t work[WORDS];
	int16_t derived[WORDS];
} prepared_dec_scratch;

extern void gt32_global_inverse_core_asm(int16_t *, const int16_t *);
extern void gt32_tile4_basemul_scale_soa_soa_to_m_private_asm(
	int16_t *, const int16_t *, const int16_t *);

static void forward_private(int16_t out[WORDS], int16_t work[WORDS],
	const int16_t in[WORDS])
{
	gt32_tile4_frontend_wide_raw_asm(work, in);
	gt32_tile4_attr_forward_all_bm_soa_asm(out, work);
}

int gt32_prepare_pk_p0(gt32_prepared_pk_p0 *ctx,
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES])
{
	int16_t h[WORDS] __attribute__((aligned(64)));
	int result = gt32_q24_decode_soa_asm(h, pk);
	gt32_prepare_fixed_b3_general_e1(&ctx->h_matrix, h);
	memcpy(ctx->pk, pk, sizeof ctx->pk);
	gt32_declassify(&result, sizeof result);
	return result;
}

int gt32_prepare_sk_p0(gt32_prepared_sk_p0 *ctx,
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	int16_t hinv[WORDS] __attribute__((aligned(64)));
	int result_f = gt32_q24_decode_soa_asm(ctx->f, sk);
	int result_hinv = gt32_q24_decode_soa_asm(hinv,
		sk + NTRUPLUS_POLYBYTES);
	int result = result_f | result_hinv;
	gt32_prepare_fixed_b3_general_e1(&ctx->hinv_matrix, hinv);
	memcpy(ctx->hash_key, sk + 2 * NTRUPLUS_POLYBYTES,
		sizeof ctx->hash_key);
	secure_clear(hinv, sizeof hinv);
	gt32_declassify(&result, sizeof result);
	return result;
}

int gt32_enc_derand_prepared_p0(
	uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	uint8_t ss[NTRUPLUS_SSBYTES],
	const gt32_prepared_pk_p0 *ctx,
	const uint8_t coins[NTRUPLUS_N / 8])
{
	uint8_t msg[HASH_H_INBYTES];
	uint8_t buf[HASH_H_OUTBYTES];
	prepared_enc_scratch scratch;

	memcpy(msg, coins, NTRUPLUS_N / 8);
	hash_f(msg + NTRUPLUS_N / 8, ctx->pk);
	hash_h(buf, msg);

	poly_cbd1((poly *)(void *)scratch.work, buf + NTRUPLUS_SYMBYTES);
	forward_private(scratch.r, scratch.c, scratch.work);
	gt32_q24_encode_soa_lazy10788_asm(ct, scratch.r);
	hash_g(ct, ct);

	poly_sotp_encode((poly *)(void *)scratch.work, msg, ct);
	forward_private(scratch.m, scratch.c, scratch.work);
	gt32_tile4_basemul_general_fixed_soa_e1_asm(scratch.c,
		scratch.r, &ctx->h_matrix);
	poly_add((poly *)(void *)scratch.c, (const poly *)(const void *)scratch.c,
		(const poly *)(const void *)scratch.m);
	gt32_q24_encode_soa_encap_hr_h1_asm(ct, scratch.c);

	memcpy(ss, buf, NTRUPLUS_SSBYTES);
	secure_clear(msg, sizeof msg);
	secure_clear(buf, sizeof buf);
	secure_clear(scratch.r, sizeof scratch.r);
	secure_clear(scratch.m, sizeof scratch.m);
	return 0;
}

static int recover_prepared(uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	prepared_dec_scratch *scratch,
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const gt32_prepared_sk_p0 *ctx)
{
	int decode_result = gt32_q24_decode_soa_asm(scratch->c, ct);
	gt32_declassify(&decode_result, sizeof decode_result);
	if (decode_result != 0)
		return 1;

	gt32_tile4_basemul_scale_soa_soa_to_m_private_asm(scratch->m,
		scratch->c, ctx->f);
	gt32_global_inverse_core_asm(scratch->work, scratch->m);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(scratch->m,
		scratch->work);
	poly_crepmod3((poly *)(void *)scratch->m);

	forward_private(scratch->work, scratch->aux, scratch->m);
	poly_sub((poly *)(void *)scratch->c,
		(const poly *)(const void *)scratch->c,
		(const poly *)(const void *)scratch->work);
	gt32_tile4_basemul_general_fixed_soa_e1_asm(scratch->aux,
		scratch->c, &ctx->hinv_matrix);
	/* Fixed REDC16 is e=0 but deliberately not centered; H1's qualified
	 * full-int16 reducer canonicalizes the representative before hashing. */
	gt32_q24_encode_soa_encap_hr_h1_asm(recovered_r, scratch->aux);
	return 0;
}

int gt32_dec_prepared_p0(uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const gt32_prepared_sk_p0 *ctx)
{
	uint8_t msg[NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES];
	uint8_t buf1[NTRUPLUS_POLYBYTES];
	uint8_t buf2[NTRUPLUS_N / 4];
	uint8_t buf3[NTRUPLUS_POLYBYTES + NTRUPLUS_SYMBYTES];
	prepared_dec_scratch scratch;
	int fail = 1;

	if (recover_prepared(buf1, &scratch, ct, ctx) != 0) {
		secure_clear(ss, NTRUPLUS_SSBYTES);
		goto cleanup;
	}

	hash_g(buf2, buf1);
	fail = poly_sotp_decode(msg, (const poly *)(const void *)scratch.m, buf2);
	memcpy(msg + NTRUPLUS_N / 8, ctx->hash_key, NTRUPLUS_SYMBYTES);
	hash_h(buf3, msg);

	poly_cbd1((poly *)(void *)scratch.m, buf3 + NTRUPLUS_SSBYTES);
	forward_private(scratch.derived, scratch.work, scratch.m);
	fail |= gt32_tile4_soa_equal_modq_12699_asm(scratch.aux,
		scratch.derived);
	for (size_t i = 0; i < NTRUPLUS_SSBYTES; ++i)
		ss[i] = (uint8_t)(buf3[i] & (uint8_t)~(uint8_t)(-fail));

cleanup:
	secure_clear(msg, sizeof msg);
	secure_clear(buf1, sizeof buf1);
	secure_clear(buf2, sizeof buf2);
	secure_clear(buf3, sizeof buf3);
	secure_clear(&scratch, sizeof scratch);
	return fail;
}
