#include <stdint.h>

#include "fips202.h"
#include "internal.h"
#include "poly.h"
#include "randombytes.h"
#include "symmetric.h"
#include "util.h"

#define SAMPLE_BYTES (NTRUPLUS_N / 4)

typedef struct __attribute__((aligned(64))) {
	uint8_t sample[SAMPLE_BYTES];
	poly coeff;
	int16_t frontend[NTRUPLUS_N];
	int16_t f[NTRUPLUS_N];
	int16_t finv[NTRUPLUS_N];
	int16_t g[NTRUPLUS_N];
	int16_t ginv[NTRUPLUS_N];
	int16_t h[NTRUPLUS_N];
} keygen_scratch;

static void forward_p(int16_t out[NTRUPLUS_N],
	int16_t frontend[NTRUPLUS_N], const int16_t in[NTRUPLUS_N])
{
	ntruplus768_ntt_frontend_avx2(frontend, in);
	ntruplus768_ntt_p_avx2(out, frontend);
}

static int sample_invertible(keygen_scratch *scratch, int sample_f,
	const uint8_t coins[NTRUPLUS_SYMBYTES])
{
	int16_t *value = sample_f != 0 ? scratch->f : scratch->g;
	int16_t *inverse = sample_f != 0 ? scratch->finv : scratch->ginv;

	shake256(scratch->sample, sizeof scratch->sample, coins,
		NTRUPLUS_SYMBYTES);
	poly_cbd1(&scratch->coeff, scratch->sample);
	poly_triple(&scratch->coeff);
	if (sample_f != 0)
		scratch->coeff.coeffs[0]++;
	forward_p(value, scratch->frontend, scratch->coeff.coeffs);
	return ntruplus768_baseinv_j1_avx2(inverse, value);
}

static void finish_keypair(keygen_scratch *scratch,
	uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	ntruplus768_basemul_f0_j1_avx2(scratch->h, scratch->g,
		scratch->finv);
	ntruplus768_pack_p_sp1_lazy10788_avx2(pk, scratch->h);

	ntruplus768_pack_p_sp1_lazy10788_avx2(sk, scratch->f);
	ntruplus768_basemul_f0_j1_avx2(scratch->h, scratch->f,
		scratch->ginv);
	ntruplus768_pack_p_sp1_lazy10788_avx2(
		sk + NTRUPLUS_POLYBYTES, scratch->h);
	hash_f(sk + 2 * NTRUPLUS_POLYBYTES, pk);
}

int ntruplus768_keypair_impl(uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	uint8_t sk[NTRUPLUS_SECRETKEYBYTES])
{
	uint8_t coins[NTRUPLUS_SYMBYTES];
	keygen_scratch scratch;

	do {
		randombytes(coins, sizeof coins);
	} while (sample_invertible(&scratch, 1, coins) != 0);
	do {
		randombytes(coins, sizeof coins);
	} while (sample_invertible(&scratch, 0, coins) != 0);

	finish_keypair(&scratch, pk, sk);
	secure_clear(coins, sizeof coins);
	secure_clear(&scratch, sizeof scratch);
	return 0;
}
