#include <stdint.h>

#include "gt_keygen_native.h"

#include "api.h"
#include "gt_baseinv_native.h"
#include "gt_basemul_soa.h"
#include "gt_native_pack.h"
#include "gt_ntt_avx2.h"
#include "randombytes.h"
#include "symmetric.h"
#include "fips202/fips202.h"

#ifndef NTRUPLUS_GT_KEYPAIR_API
#define NTRUPLUS_GT_KEYPAIR_API crypto_kem_keypair_gt
#endif

void gt_poly_ntt_lazy(poly *out, const poly *in)
{
	gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm(
		out->coeffs, in->coeffs);
}

int gt_poly_baseinv_l3(poly *out, const poly *in)
{
	return gt_baseinv_native_l3_asm_avx2(out->coeffs, in->coeffs);
}

void gt_poly_basemul_native(poly *out, const poly *a, const poly *b)
{
	gt_basemul_native_asm_avx2(
		out->coeffs, a->coeffs, b->coeffs);
}

static int genf_derand(poly *f, poly *finv, const uint8_t *coins)
{
	uint8_t buffer[NTRUPLUS_N / 4];

	shake256(buffer, sizeof(buffer), coins, NTRUPLUS_SYMBYTES);
	poly_cbd1(f, buffer);
	poly_triple(f, f);
	f->coeffs[0] += 1;
	gt_poly_ntt_lazy(f, f);
	return gt_poly_baseinv_l3(finv, f);
}

static int geng_derand(poly *g, poly *ginv, const uint8_t *coins)
{
	uint8_t buffer[NTRUPLUS_N / 4];

	shake256(buffer, sizeof(buffer), coins, NTRUPLUS_SYMBYTES);
	poly_cbd1(g, buffer);
	poly_triple(g, g);
	gt_poly_ntt_lazy(g, g);
	return gt_poly_baseinv_l3(ginv, g);
}

static void derive_keypair(uint8_t *pk, uint8_t *sk,
	const poly *f, const poly *finv, const poly *g, const poly *ginv)
{
	poly h;
	poly hinv;

	gt_poly_basemul_native(&h, g, finv);
	gt_poly_basemul_native(&hinv, f, ginv);
#if defined(GT_HAVE_AVX2_ASM) && GT_HAVE_AVX2_ASM
	gt_poly_tobytes_native_centered_asm_avx2(pk, &h);
	gt_poly_tobytes_native_centered_asm_avx2(
		sk + NTRUPLUS_POLYBYTES, &hinv);
	gt_poly_tobytes_native_l3_asm_avx2(sk, f);
#else
	gt_poly_tobytes_native(pk, &h);
	gt_poly_tobytes_native(sk, f);
	gt_poly_tobytes_native(sk + NTRUPLUS_POLYBYTES, &hinv);
#endif
	hash_f(sk + 2 * NTRUPLUS_POLYBYTES, pk);
}

int ntruplus_gt_keypair_derand(
	uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	uint8_t sk[NTRUPLUS_SECRETKEYBYTES],
	const uint8_t f_coins[NTRUPLUS_SYMBYTES],
	const uint8_t g_coins[NTRUPLUS_SYMBYTES])
{
	poly f;
	poly finv;
	poly g;
	poly ginv;

	if (genf_derand(&f, &finv, f_coins) != 0 ||
	    geng_derand(&g, &ginv, g_coins) != 0) {
		return 1;
	}
	derive_keypair(pk, sk, &f, &finv, &g, &ginv);
	return 0;
}

int NTRUPLUS_GT_KEYPAIR_API(unsigned char *pk, unsigned char *sk)
{
	uint8_t coins[NTRUPLUS_SYMBYTES];
	poly f;
	poly finv;
	poly g;
	poly ginv;

	do {
		randombytes(coins, sizeof(coins));
	} while (genf_derand(&f, &finv, coins) != 0);
	do {
		randombytes(coins, sizeof(coins));
	} while (geng_derand(&g, &ginv, coins) != 0);
	derive_keypair(pk, sk, &f, &finv, &g, &ginv);
	return 0;
}
