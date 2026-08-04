#define _DEFAULT_SOURCE
#include <stdint.h>

#include "api.h"
#include "fips202/fips202.h"
#include "gt_baseinv_native.h"
#include "gt_basemul_soa.h"
#include "gt_native_pack.h"
#include "gt_ntt_avx2.h"
#include "poly.h"
#include "prototype_keypair_adapter.h"
#include "randombytes.h"
#include "symmetric.h"
#include "util.h"

/*
 * Revision-locked adapter for the committed avx2-gt-ntt-prototype keypair
 * pipeline.  The original prototype was written against the KPQC two-operand
 * poly_triple API.  This adapter deliberately uses Official Main's in-place
 * API while leaving the native transform, baseinv, basemul, and pack kernels
 * unchanged.
 */
static void prototype_ntt_lazy(poly *out, const poly *in)
{
    gt_ntt_avx2_forward_wide_fused_delayed_row2q2_native_lazy_pipelined_asm(
        out->coeffs, in->coeffs);
}

static int prototype_baseinv_l3(poly *out, const poly *in)
{
    return gt_baseinv_native_l3_asm_avx2(out->coeffs, in->coeffs);
}

static void prototype_basemul(poly *out, const poly *a, const poly *b)
{
    gt_basemul_native_asm_avx2(out->coeffs, a->coeffs, b->coeffs);
}

static int prototype_genf(poly *f, poly *finv, uint8_t buffer[NTRUPLUS_N / 4],
                          const uint8_t coins[NTRUPLUS_SYMBYTES])
{
    shake256(buffer, NTRUPLUS_N / 4, coins, NTRUPLUS_SYMBYTES);
    poly_cbd1(f, buffer);
    poly_triple(f);
    f->coeffs[0] += 1;
    prototype_ntt_lazy(f, f);
    return prototype_baseinv_l3(finv, f);
}

static int prototype_geng(poly *g, poly *ginv, uint8_t buffer[NTRUPLUS_N / 4],
                          const uint8_t coins[NTRUPLUS_SYMBYTES])
{
    shake256(buffer, NTRUPLUS_N / 4, coins, NTRUPLUS_SYMBYTES);
    poly_cbd1(g, buffer);
    poly_triple(g);
    prototype_ntt_lazy(g, g);
    return prototype_baseinv_l3(ginv, g);
}

static void prototype_derive(uint8_t *pk, uint8_t *sk, const poly *f,
                             const poly *finv, const poly *g,
                             const poly *ginv)
{
    poly h;

    prototype_basemul(&h, g, finv);
    gt_poly_tobytes_native_centered_asm_avx2(pk, &h);
    prototype_basemul(&h, f, ginv);
    gt_poly_tobytes_native_l3_asm_avx2(sk, f);
    gt_poly_tobytes_native_centered_asm_avx2(
        sk + NTRUPLUS_POLYBYTES, &h);
    hash_f(sk + 2 * NTRUPLUS_POLYBYTES, pk);
    secure_clear(&h, sizeof h);
}

static int prototype_keypair_impl(unsigned char *pk, unsigned char *sk,
                                  int clear_secrets)
{
    uint8_t coins[NTRUPLUS_SYMBYTES];
    uint8_t buffer[NTRUPLUS_N / 4];
    poly f;
    poly finv;
    poly g;
    poly ginv;

    do {
        randombytes(coins, sizeof coins);
    } while (prototype_genf(&f, &finv, buffer, coins) != 0);
    do {
        randombytes(coins, sizeof coins);
    } while (prototype_geng(&g, &ginv, buffer, coins) != 0);
    prototype_derive(pk, sk, &f, &finv, &g, &ginv);

    if (clear_secrets != 0) {
        secure_clear(coins, sizeof coins);
        secure_clear(buffer, sizeof buffer);
        secure_clear(&f, sizeof f);
        secure_clear(&finv, sizeof finv);
        secure_clear(&g, sizeof g);
        secure_clear(&ginv, sizeof ginv);
    }
    return 0;
}

int prototype_crypto_kem_keypair(unsigned char *pk, unsigned char *sk)
{
    return prototype_keypair_impl(pk, sk, 1);
}

int prototype_crypto_kem_keypair_no_clear(unsigned char *pk, unsigned char *sk)
{
    return prototype_keypair_impl(pk, sk, 0);
}
