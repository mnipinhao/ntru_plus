#include "api.h"
#include "gt864_fr0_basemul.h"
#include "gt864_fr0_basemul_d1.h"
#include "gt864_fr0_to_official_map.h"
#include "params.h"
#include "poly.h"
#include "symmetric.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

/* Exact, test-only extraction of the stock crypto_kem_enc_derand intermediates. */
static void capture_stock_encap(poly *h, poly *r, poly *m,
                                uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
                                const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
                                const uint8_t coins[NTRUPLUS_N / 8])
{
    uint8_t msg[NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES];
    uint8_t buf1[NTRUPLUS_SYMBYTES + NTRUPLUS_N / 4];
    uint8_t buf2[NTRUPLUS_POLYBYTES];
    poly c;

    memcpy(msg, coins, NTRUPLUS_N / 8);
    hash_f(msg + NTRUPLUS_N / 8, pk);
    hash_h(buf1, msg);
    poly_cbd1(r, buf1 + NTRUPLUS_SYMBYTES);
    poly_ntt(r, r);
    poly_tobytes(buf2, r);
    hash_g(buf2, buf2);
    poly_sotp_encode(m, msg, buf2);
    poly_ntt(m, m);
    poly_frombytes(h, pk);
    poly_basemul_add(&c, h, r, m);
    poly_tobytes(ct, &c);
}

static void official_to_fr0(poly *fr0, const poly *official)
{
    for (int i = 0; i < NTRUPLUS_N; i++)
        fr0->coeffs[gt864_fr0_for_official[i]] = official->coeffs[i];
}

static void fr0_to_official(poly *official, const poly *fr0)
{
    for (int i = 0; i < NTRUPLUS_N; i++)
        official->coeffs[i] = fr0->coeffs[gt864_fr0_for_official[i]];
}

int main(void)
{
    uint8_t pk[NTRUPLUS_PUBLICKEYBYTES];
    uint8_t sk[NTRUPLUS_SECRETKEYBYTES];
    uint8_t coins[NTRUPLUS_N / 8];
    uint8_t stock_ct[NTRUPLUS_CIPHERTEXTBYTES];
    uint8_t old_gt_ct[NTRUPLUS_CIPHERTEXTBYTES];
    uint8_t d1_gt_ct[NTRUPLUS_CIPHERTEXTBYTES];
    int mismatches = 0;
    int cases = 0;

    for (int key = 0; key < 3; key++) {
        poly h, r, m, h_fr0, r_fr0, m_fr0, old_fr0, d1_fr0;
        poly old_official, d1_official;
        if (crypto_kem_keypair(pk, sk) != 0) return 2;
        for (int trial = 0; trial < 8; trial++) {
            for (size_t i = 0; i < sizeof(coins); i++)
                coins[i] = (uint8_t)(17 * key + 29 * trial + 13 * i);
            capture_stock_encap(&h, &r, &m, stock_ct, pk, coins);
            official_to_fr0(&h_fr0, &h);
            official_to_fr0(&r_fr0, &r);
            official_to_fr0(&m_fr0, &m);
            gt864_fr0_basemul_add_neon(old_fr0.coeffs, h_fr0.coeffs,
                                       r_fr0.coeffs, m_fr0.coeffs);
            gt864_fr0_basemul_add_d1_neon(d1_fr0.coeffs, h_fr0.coeffs,
                                          r_fr0.coeffs, m_fr0.coeffs);
            fr0_to_official(&old_official, &old_fr0);
            fr0_to_official(&d1_official, &d1_fr0);
            poly_tobytes(old_gt_ct, &old_official);
            poly_tobytes(d1_gt_ct, &d1_official);
            for (int i = 0; i < NTRUPLUS_CIPHERTEXTBYTES; i++) {
                if (stock_ct[i] != old_gt_ct[i] ||
                    stock_ct[i] != d1_gt_ct[i]) {
                    if (mismatches < 8)
                        fprintf(stderr,
                                "encap byte key=%d trial=%d i=%d stock=%u old=%u d1=%u\n",
                                key, trial, i, (unsigned)stock_ct[i],
                                (unsigned)old_gt_ct[i], (unsigned)d1_gt_ct[i]);
                    mismatches++;
                }
            }
            cases++;
        }
    }
    printf("d1_c2b_real_encap=%s cases=%d byte_mismatches=%d\n",
           mismatches == 0 ? "pass" : "fail", cases, mismatches);
    printf("production_linked=0\n");
    return mismatches != 0;
}
