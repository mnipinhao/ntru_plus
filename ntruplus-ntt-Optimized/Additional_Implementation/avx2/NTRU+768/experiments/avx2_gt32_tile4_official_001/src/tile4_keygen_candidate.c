#include <stdint.h>

#if __has_include("fips202/fips202.h")
#include "fips202/fips202.h"
#else
#include "fips202.h"
#endif
#include "poly.h"
#include "randombytes.h"
#include "symmetric.h"
#include "util.h"

#include "tile4.h"
#include "tile4_keygen_candidate.h"

#define WORDS NTRUPLUS_N
#define SAMPLE_BYTES (NTRUPLUS_N / 4)

extern void gt32_tile4_attr_forward_all_baseinv_p_l3_asm(int16_t *,
	const int16_t *);
#ifdef GT32_KEYGEN_P_SUFFIX
extern void gt32_progressive_suffix_forward_p_safe_core_asm(int16_t *,
	const int16_t *);
#endif
extern int gt32_p_baseinv_direct_avx2(int16_t *, const int16_t *);
extern void gt_basemul_native_asm_avx2(int16_t *, const int16_t *,
	const int16_t *);

typedef struct __attribute__((aligned(64))) {
	uint8_t sample[SAMPLE_BYTES];
	poly coeff;
	int16_t frontend[WORDS];
	int16_t f[WORDS];
	int16_t finv[WORDS];
	int16_t g[WORDS];
	int16_t ginv[WORDS];
	int16_t h[WORDS];
} gt32_keygen_scratch_t;

static void gt32_keygen_forward(int16_t out[WORDS], int16_t frontend[WORDS],
	const int16_t in[WORDS])
{
	gt32_tile4_frontend_wide_raw_asm(frontend, in);
#ifdef GT32_KEYGEN_P_SUFFIX
	gt32_progressive_suffix_forward_p_safe_core_asm(out, frontend);
#else
	gt32_tile4_attr_forward_all_baseinv_p_l3_asm(out, frontend);
#endif
}

static int gt32_keygen_attempt(gt32_keygen_scratch_t *scratch, int is_f,
	const uint8_t coins[NTRUPLUS_SYMBYTES])
{
	int16_t *value = is_f != 0 ? scratch->f : scratch->g;
	int16_t *inverse = is_f != 0 ? scratch->finv : scratch->ginv;

	shake256(scratch->sample, sizeof scratch->sample, coins,
		NTRUPLUS_SYMBYTES);
	poly_cbd1(&scratch->coeff, scratch->sample);
	poly_triple(&scratch->coeff);
	if (is_f != 0)
		scratch->coeff.coeffs[0]++;
	gt32_keygen_forward(value, scratch->frontend, scratch->coeff.coeffs);
	return gt32_p_baseinv_direct_avx2(inverse, value);
}

static void gt32_keygen_finish(gt32_keygen_scratch_t *scratch,
	uint8_t pk[CRYPTO_PUBLICKEYBYTES], uint8_t sk[CRYPTO_SECRETKEYBYTES])
{
	gt_basemul_native_asm_avx2(scratch->h, scratch->g, scratch->finv);
	gt32_q24_encode_p_soa_halfscatter_lazy10788_asm(pk, scratch->h);

	gt32_q24_encode_p_soa_halfscatter_lazy10788_asm(sk, scratch->f);
	gt_basemul_native_asm_avx2(scratch->h, scratch->f, scratch->ginv);
	gt32_q24_encode_p_soa_halfscatter_lazy10788_asm(
		sk + NTRUPLUS_POLYBYTES, scratch->h);
	hash_f(sk + 2 * NTRUPLUS_POLYBYTES, pk);
}

int crypto_kem_keypair_gt32_production_candidate(
	uint8_t pk[CRYPTO_PUBLICKEYBYTES], uint8_t sk[CRYPTO_SECRETKEYBYTES])
{
	uint8_t coins[NTRUPLUS_SYMBYTES];
	gt32_keygen_scratch_t scratch;

	do {
		randombytes(coins, sizeof coins);
	} while (gt32_keygen_attempt(&scratch, 1, coins) != 0);
	do {
		randombytes(coins, sizeof coins);
	} while (gt32_keygen_attempt(&scratch, 0, coins) != 0);

	gt32_keygen_finish(&scratch, pk, sk);
	secure_clear(coins, sizeof coins);
	secure_clear(&scratch, sizeof scratch);
	return 0;
}
