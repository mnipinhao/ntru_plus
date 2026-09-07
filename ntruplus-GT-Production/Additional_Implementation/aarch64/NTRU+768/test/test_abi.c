#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "api.h"
#include "decap_verify.h"
#include "keygen.h"
#include "poly.h"

typedef uint64_t (*abi_sentinel_fn)(void *, void *, void *, void *);

uint64_t abi_internal_poly_ntt_loose(void *, void *, void *, void *);
uint64_t abi_internal_poly_ntt_encap_small(void *, void *, void *, void *);
uint64_t abi_poly_invntt(void *, void *, void *, void *);
uint64_t abi_poly_basemul(void *, void *, void *, void *);
uint64_t abi_poly_basemul_add(void *, void *, void *, void *);
uint64_t abi_poly_tobytes(void *, void *, void *, void *);
uint64_t abi_poly_frombytes(void *, void *, void *, void *);
uint64_t abi_poly_cbd1(void *, void *, void *, void *);
uint64_t abi_poly_sotp_encode(void *, void *, void *, void *);
uint64_t abi_poly_sotp_decode(void *, void *, void *, void *);
uint64_t abi_poly_sub(void *, void *, void *, void *);
uint64_t abi_poly_triple(void *, void *, void *, void *);
uint64_t abi_poly_crepmod3(void *, void *, void *, void *);
uint64_t abi_keygen_ntt(void *, void *, void *, void *);
uint64_t abi_keygen_baseinv(void *, void *, void *, void *);
uint64_t abi_keygen_basemul(void *, void *, void *, void *);
uint64_t abi_keygen_tobytes(void *, void *, void *, void *);
uint64_t abi_decap_verify(void *, void *, void *, void *);
uint64_t abi_qsoa_frombytes(void *, void *, void *, void *);
uint64_t abi_decap_pointwise(void *, void *, void *, void *);
uint64_t abi_qsoa_tobytes(void *, void *, void *, void *);
uint64_t abi_decap_packed64(void *, void *, void *, void *);
uint64_t abi_decap_frombytes(void *, void *, void *, void *);
uint64_t abi_decap_tobytes(void *, void *, void *, void *);
uint64_t abi_decap_basemul(void *, void *, void *, void *);
uint64_t abi_decap_invntt(void *, void *, void *, void *);
uint64_t abi_decap_sub(void *, void *, void *, void *);
uint64_t abi_decap_ntt(void *, void *, void *, void *);
uint64_t abi_crypto_kem_keypair(void *, void *, void *, void *);
uint64_t abi_crypto_kem_enc(void *, void *, void *, void *);
uint64_t abi_crypto_kem_dec(void *, void *, void *, void *);

struct abi_case {
    const char *name;
    abi_sentinel_fn sentinel;
    void *arg0;
    void *arg1;
    void *arg2;
    void *arg3;
    int aapcs_required;
};

int main(void)
{
    poly a;
    poly b;
    poly c;
    poly d;
    gt_cq_poly cq_a;
    gt_cq_poly cq_b;
    gt_cq_poly cq_c;
    uint8_t bytes_a[NTRUPLUS_POLYBYTES];
    uint8_t bytes_b[NTRUPLUS_POLYBYTES];
    uint8_t pk[CRYPTO_PUBLICKEYBYTES];
    uint8_t sk[CRYPTO_SECRETKEYBYTES];
    uint8_t ct[CRYPTO_CIPHERTEXTBYTES];
    uint8_t ss_enc[CRYPTO_BYTES];
    uint8_t ss_dec[CRYPTO_BYTES];
    uint64_t required_mask = 0;
    uint64_t internal_mask = 0;
    size_t i;

    memset(&a, 0, sizeof(a));
    memset(&b, 0, sizeof(b));
    memset(&c, 0, sizeof(c));
    memset(&d, 0, sizeof(d));
    memset(&cq_a, 0, sizeof(cq_a));
    memset(&cq_b, 0, sizeof(cq_b));
    memset(&cq_c, 0, sizeof(cq_c));
    memset(bytes_a, 0, sizeof(bytes_a));
    memset(bytes_b, 0, sizeof(bytes_b));

    const struct abi_case cases[] = {
        {"crypto_kem_keypair", abi_crypto_kem_keypair,
         pk, sk, NULL, NULL, 1},
        {"crypto_kem_enc", abi_crypto_kem_enc,
         ct, ss_enc, pk, NULL, 1},
        {"crypto_kem_dec", abi_crypto_kem_dec,
         ss_dec, ct, sk, NULL, 1},
        {"internal_ntt_loose", abi_internal_poly_ntt_loose,
         &a, &b, NULL, NULL, 1},
        {"ntt_encap_small", abi_internal_poly_ntt_encap_small,
         &a, &b, NULL, NULL, 1},
        {"poly_invntt", abi_poly_invntt, &a, &b, NULL, NULL, 1},
        {"poly_basemul", abi_poly_basemul, &a, &b, &c, NULL, 1},
        {"poly_basemul_add_encap", abi_poly_basemul_add, &a, &b, &c, &d, 1},
        {"poly_tobytes_encap", abi_poly_tobytes, bytes_a, &a, NULL, NULL, 1},
        {"poly_frombytes_encap", abi_poly_frombytes, &a, bytes_a, NULL, NULL, 1},
        {"poly_cbd1", abi_poly_cbd1, &a, bytes_a, NULL, NULL, 0},
        {"poly_sotp_encode", abi_poly_sotp_encode,
         &a, bytes_a, bytes_b, NULL, 0},
        {"poly_sotp_decode", abi_poly_sotp_decode,
         bytes_a, &a, bytes_b, NULL, 0},
        {"poly_sub", abi_poly_sub, &a, &b, &c, NULL, 0},
        {"poly_triple", abi_poly_triple, &a, &b, NULL, NULL, 0},
        {"poly_crepmod3", abi_poly_crepmod3, &a, &b, NULL, NULL, 0},
        {"keygen_ntt", abi_keygen_ntt, &cq_a, &a, NULL, NULL, 1},
        {"keygen_baseinv", abi_keygen_baseinv,
         &cq_b, &cq_a, NULL, NULL, 1},
        {"keygen_basemul", abi_keygen_basemul,
         &cq_c, &cq_a, &cq_b, NULL, 1},
        {"keygen_tobytes", abi_keygen_tobytes,
         bytes_a, &cq_c, NULL, NULL, 1},
        {"decap_verify_predecoded", abi_decap_verify,
         bytes_b, &a, &b, NULL, 0},
        {"qsoa_frombytes", abi_qsoa_frombytes,
         &b, bytes_a, NULL, NULL, 0},
        {"decap_pointwise", abi_decap_pointwise,
         &c, &a, &b, NULL, 1},
        {"qsoa_tobytes", abi_qsoa_tobytes,
         bytes_b, &c, NULL, NULL, 0},
        {"decap_packed64", abi_decap_packed64,
         &a, &b, bytes_a, bytes_b, 1},
        {"decap_frombytes", abi_decap_frombytes,
         &a, bytes_a, NULL, NULL, 1},
        {"decap_tobytes", abi_decap_tobytes,
         bytes_b, &a, NULL, NULL, 1},
        {"decap_basemul", abi_decap_basemul,
         &a, &b, &c, NULL, 1},
        {"decap_invntt", abi_decap_invntt,
         &a, NULL, NULL, NULL, 1},
        {"decap_sub", abi_decap_sub,
         &a, &b, &c, NULL, 1},
        {"decap_ntt", abi_decap_ntt,
         &a, &b, NULL, NULL, 1},
    };

    for (i = 0; i < sizeof(cases) / sizeof(cases[0]); i++) {
        uint64_t mask = cases[i].sentinel(
            cases[i].arg0, cases[i].arg1, cases[i].arg2, cases[i].arg3);

        printf("%-20s mask=0x%05llx\n", cases[i].name,
               (unsigned long long)mask);
        if (cases[i].aapcs_required)
            required_mask |= mask;
        else
            internal_mask |= mask;
    }

    printf("required_abi_mask=0x%05llx internal_custom_mask=0x%05llx\n",
           (unsigned long long)required_mask,
           (unsigned long long)internal_mask);
    return required_mask != 0;
}
