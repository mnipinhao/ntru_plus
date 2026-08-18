#include <stddef.h>
#include <stdint.h>

#include "poly.h"
#include "symmetric.h"
#include "util.h"

#include "tile4.h"
#include "tile4_kem_encap_candidate.h"

#define WORDS GT32_TILE4_POLY_WORDS

#ifndef GT32_ENCAP_FRONTEND
#define GT32_ENCAP_FRONTEND gt32_tile4_frontend_wide_raw_asm
#endif

#ifndef GT32_ENCAP_R_PACK
#define GT32_ENCAP_R_PACK gt32_q24_encode_soa_lazy10788_asm
#endif

#ifndef GT32_ENCAP_C_PACK
#define GT32_ENCAP_C_PACK gt32_q24_encode_soa_encap_hr_h1_asm
#endif

typedef struct {
	int16_t h[WORDS];
	int16_t r[WORDS];
	int16_t m[WORDS];
#if (!defined(GT32_ENCAP_FOUR_POLY_ADD_M) || !GT32_ENCAP_FOUR_POLY_ADD_M) && \
	(!defined(GT32_ENCAP_Q24_SUM_M) || !GT32_ENCAP_Q24_SUM_M)
	int16_t c[WORDS];
#endif
	int16_t work[WORDS];
} gt32_encap_scratch_t __attribute__((aligned(64)));

static void forward_coeff_to_private_soa(int16_t out[WORDS],
	int16_t work[WORDS], const int16_t in[WORDS])
{
	GT32_ENCAP_FRONTEND(work, in);
	gt32_tile4_attr_forward_all_bm_soa_asm(out, work);
}

#ifndef GT32_ENCAP_CANDIDATE_SYMBOL
#define GT32_ENCAP_CANDIDATE_SYMBOL crypto_kem_enc_derand_gt32_candidate
#endif

int GT32_ENCAP_CANDIDATE_SYMBOL(
	uint8_t ct[CRYPTO_CIPHERTEXTBYTES], uint8_t ss[CRYPTO_BYTES],
	const uint8_t pk[CRYPTO_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8])
{
	uint8_t msg[HASH_H_INBYTES];
	uint8_t buf[HASH_H_OUTBYTES];
	gt32_encap_scratch_t scratch;

	if (gt32_q24_decode_soa_asm(scratch.h, pk) != 0) {
		for (size_t i = 0; i < NTRUPLUS_CIPHERTEXTBYTES; i++)
			ct[i] = 0;
		secure_clear(ss, NTRUPLUS_SSBYTES);
		return 1;
	}

	for (size_t i = 0; i < NTRUPLUS_N / 8; i++)
		msg[i] = coins[i];
	hash_f(msg + NTRUPLUS_N / 8, pk);
	hash_h(buf, msg);

	poly_cbd1((poly *)(void *)scratch.work, buf + NTRUPLUS_SYMBYTES);
#if (defined(GT32_ENCAP_FOUR_POLY_ADD_M) && GT32_ENCAP_FOUR_POLY_ADD_M) || \
	(defined(GT32_ENCAP_Q24_SUM_M) && GT32_ENCAP_Q24_SUM_M)
	/* The N5 core has an exact in-place contract after the frontend deposit. */
	forward_coeff_to_private_soa(scratch.r, scratch.r, scratch.work);
#else
	forward_coeff_to_private_soa(scratch.r, scratch.c, scratch.work);
#endif
	/* Forward private-SoA has the proven e=0, |word| <= 10788 contract. */
	GT32_ENCAP_R_PACK(ct, scratch.r);
	hash_g(ct, ct);

	poly_sotp_encode((poly *)(void *)scratch.work, msg, ct);
#if defined(GT32_ENCAP_Q24_SUM_M) && GT32_ENCAP_Q24_SUM_M
	forward_coeff_to_private_soa(scratch.m, scratch.m, scratch.work);
	gt32_tile4_basemul_general_soa_soa_to_soa_asm(scratch.work,
		scratch.h, scratch.r);

	/* Add the M-domain message at the serializer load seam. */
	gt32_q24_encode_soa_encap_hr_sum_asm(ct, scratch.work, scratch.m);
#elif defined(GT32_ENCAP_FOUR_POLY_ADD_M) && GT32_ENCAP_FOUR_POLY_ADD_M
	forward_coeff_to_private_soa(scratch.m, scratch.m, scratch.work);
	gt32_tile4_basemul_general_soa_soa_add_m_asm(scratch.work,
		scratch.h, scratch.r, scratch.m);

	/* B3-general e=0 plus N5 m is proven within |word| <= 12699. */
	GT32_ENCAP_C_PACK(ct, scratch.work);
#else
	forward_coeff_to_private_soa(scratch.m, scratch.c, scratch.work);
	gt32_tile4_basemul_general_soa_soa_to_soa_asm(scratch.c,
		scratch.h, scratch.r);
	poly_add((poly *)(void *)scratch.c, (const poly *)(const void *)scratch.c,
		(const poly *)(const void *)scratch.m);

	/* B3-general e=0 plus N5 m is proven within |word| <= 12699. */
	GT32_ENCAP_C_PACK(ct, scratch.c);
#endif

	for (size_t i = 0; i < NTRUPLUS_SSBYTES; i++)
		ss[i] = buf[i];

	secure_clear(msg, sizeof msg);
	secure_clear(buf, sizeof buf);
	/* Clear every secret representation which survives the producer calls. */
	secure_clear(scratch.r, sizeof scratch.r);
	secure_clear(scratch.m, sizeof scratch.m);
	return 0;
}
