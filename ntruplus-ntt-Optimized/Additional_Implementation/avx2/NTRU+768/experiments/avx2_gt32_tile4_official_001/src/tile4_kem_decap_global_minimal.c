#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "poly.h"
#include "symmetric.h"
#include "util.h"

#include "tile4.h"
#include "tile4_kem_candidate.h"
#include "gt32_native_rcheck_placement.h"

#ifdef SUPERCOP
#include "crypto_declassify.h"
#define gt32_declassify crypto_declassify
#else
#define gt32_declassify(value, length) ((void)(value), (void)(length))
#endif

#define WORDS GT32_TILE4_POLY_WORDS

typedef struct __attribute__((aligned(64))) {
	int16_t c[WORDS];
	int16_t aux[WORDS];
	int16_t hinv[WORDS];
	int16_t m[WORDS];
	int16_t work[WORDS];
} gt32_decap_global_scratch_t;

extern void gt32_global_inverse_core_asm(int16_t *, const int16_t *);
extern void gt32_tile4_basemul_scale_soa_soa_to_m_private_asm(
	int16_t *, const int16_t *, const int16_t *);

static int verify_bytes(const uint8_t *a, const uint8_t *b, size_t length)
{
	uint8_t acc = 0;
	for (size_t i = 0; i < length; i++)
		acc |= (uint8_t)(a[i] ^ b[i]);
	return (int)((-(uint64_t)acc) >> 63);
}

static int recover_message_and_r(uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	gt32_decap_global_scratch_t *scratch,
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	int decode_result = gt32_q24_decode3_soa_asm(scratch->c, scratch->aux,
		scratch->hinv, ct, sk);
	gt32_declassify(&decode_result, sizeof decode_result);
	if (decode_result != 0)
		return 1;

	gt32_tile4_basemul_scale_soa_soa_to_m_private_asm(scratch->m,
		scratch->c, scratch->aux);
	gt32_global_inverse_core_asm(scratch->work, scratch->m);
	gt32_tile4_inverse_tail_t9_isolated_private_asm(scratch->m,
		scratch->work);
	poly_crepmod3((poly *)(void *)scratch->m);

	gt32_tile4_frontend_wide_raw_asm(scratch->aux, scratch->m);
	gt32_tile4_attr_forward_all_bm_soa_asm(scratch->work, scratch->aux);
	poly_sub((poly *)(void *)scratch->c,
		(const poly *)(const void *)scratch->c,
		(const poly *)(const void *)scratch->work);
	gt32_tile4_basemul_general_soa_soa_to_soa_asm(scratch->aux,
		scratch->c, scratch->hinv);
	gt32_q24_encode_soa_asm(recovered_r, scratch->aux);
	return 0;
}

static void encode_check(uint8_t out[NTRUPLUS_POLYBYTES],
	gt32_decap_global_scratch_t *scratch)
{
	gt32_tile4_frontend_wide_raw_asm(scratch->c, scratch->aux);
	gt32_tile4_attr_forward_all_bm_soa_asm(scratch->hinv, scratch->c);
	gt32_q24_encode_soa_lazy10788_asm(out, scratch->hinv);
}

int crypto_kem_dec_gt32_global_inverse_candidate(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	uint8_t msg[NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES];
	uint8_t buf1[NTRUPLUS_POLYBYTES];
	uint8_t buf2[NTRUPLUS_POLYBYTES];
	uint8_t buf3[NTRUPLUS_POLYBYTES + NTRUPLUS_SYMBYTES];
	gt32_decap_global_scratch_t scratch;
	int fail = 1;

	if (recover_message_and_r(buf1, &scratch, ct, sk) != 0) {
		secure_clear(ss, NTRUPLUS_SSBYTES);
		goto cleanup;
	}

	hash_g(buf2, buf1);
	fail = poly_sotp_decode(msg,
		(const poly *)(const void *)scratch.m, buf2);
	memcpy(msg + NTRUPLUS_N / 8,
		sk + 2 * NTRUPLUS_POLYBYTES, NTRUPLUS_SYMBYTES);
	hash_h(buf3, msg);

	poly_cbd1((poly *)(void *)scratch.aux, buf3 + NTRUPLUS_SSBYTES);
	encode_check(buf2, &scratch);
	fail |= verify_bytes(buf1, buf2, NTRUPLUS_POLYBYTES);
	for (size_t i = 0; i < NTRUPLUS_SSBYTES; i++)
		ss[i] = (uint8_t)(buf3[i] & (uint8_t)~(uint8_t)(-fail));

cleanup:
	secure_clear(msg, sizeof msg);
	secure_clear(buf1, sizeof buf1);
	secure_clear(buf2, sizeof buf2);
	secure_clear(buf3, sizeof buf3);
	secure_clear(&scratch, sizeof scratch);
	return fail;
}

/*
 * GT32-DECAP-NATIVE-RCHECK-001.  Keep the recovered r-hat in aux after its
 * mandatory canonical serialization for hash_g, then compare the derived
 * r-hat directly in the common private SoA e=0 domain.  This deliberately
 * remains a separate opt-in body so the qualified production candidate and
 * its code addresses are not changed by a compile-time selector.
 */
__attribute__((aligned(GT32_NATIVE_RCHECK_ALIGN)))
int crypto_kem_dec_gt32_native_rcheck_candidate(
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	uint8_t msg[NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES];
	uint8_t buf1[NTRUPLUS_POLYBYTES];
	uint8_t buf2[NTRUPLUS_N / 4];
	uint8_t buf3[NTRUPLUS_POLYBYTES + NTRUPLUS_SYMBYTES];
	gt32_decap_global_scratch_t scratch;
	int fail = 1;

	if (recover_message_and_r(buf1, &scratch, ct, sk) != 0) {
		secure_clear(ss, NTRUPLUS_SSBYTES);
		goto cleanup;
	}

	hash_g(buf2, buf1);
	fail = poly_sotp_decode(msg,
		(const poly *)(const void *)scratch.m, buf2);
	memcpy(msg + NTRUPLUS_N / 8,
		sk + 2 * NTRUPLUS_POLYBYTES, NTRUPLUS_SYMBYTES);
	hash_h(buf3, msg);

	/* m is dead after SOTP decode; work is frontend scratch; hinv receives
	 * the derived r-hat.  aux remains the recovered r-hat. */
	poly_cbd1((poly *)(void *)scratch.m, buf3 + NTRUPLUS_SSBYTES);
	gt32_tile4_frontend_wide_raw_asm(scratch.work, scratch.m);
	gt32_tile4_attr_forward_all_bm_soa_asm(scratch.hinv, scratch.work);
	fail |= gt32_tile4_soa_equal_modq_12699_asm(scratch.aux,
		scratch.hinv);

	for (size_t i = 0; i < NTRUPLUS_SSBYTES; i++)
		ss[i] = (uint8_t)(buf3[i] & (uint8_t)~(uint8_t)(-fail));

cleanup:
	secure_clear(msg, sizeof msg);
	secure_clear(buf1, sizeof buf1);
	secure_clear(buf2, sizeof buf2);
	secure_clear(buf3, sizeof buf3);
	secure_clear(&scratch, sizeof scratch);
	return fail;
}
