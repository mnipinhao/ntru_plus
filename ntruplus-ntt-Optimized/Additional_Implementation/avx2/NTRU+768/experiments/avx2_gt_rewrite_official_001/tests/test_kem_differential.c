#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "api.h"
#include "kat/rng.h"

int gt_crypto_kem_keypair(unsigned char *pk, unsigned char *sk);
int gt_crypto_kem_enc(unsigned char *ct, unsigned char *ss,
                      const unsigned char *pk);
int gt_crypto_kem_dec(unsigned char *ss, const unsigned char *ct,
                      const unsigned char *sk);

static void reset_rng(unsigned domain, unsigned round)
{
    unsigned char entropy[48];
    for (size_t i = 0; i < sizeof entropy; ++i)
        entropy[i] = (unsigned char)(i + 37U * domain + 101U * round);
    randombytes_init(entropy, NULL, 256);
}

static int check_one(unsigned round)
{
    unsigned char official_pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char official_sk[CRYPTO_SECRETKEYBYTES];
    unsigned char official_ct[CRYPTO_CIPHERTEXTBYTES];
    unsigned char official_ss[CRYPTO_BYTES];
    unsigned char official_dec[CRYPTO_BYTES];
    unsigned char gt_pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char gt_sk[CRYPTO_SECRETKEYBYTES];
    unsigned char gt_ct[CRYPTO_CIPHERTEXTBYTES];
    unsigned char gt_ss[CRYPTO_BYTES];
    unsigned char gt_dec[CRYPTO_BYTES];

    reset_rng(1, round);
    const int official_keypair_rc = crypto_kem_keypair(official_pk, official_sk);
    reset_rng(1, round);
    const int gt_keypair_rc = gt_crypto_kem_keypair(gt_pk, gt_sk);
    if (official_keypair_rc != gt_keypair_rc
            || memcmp(official_pk, gt_pk, sizeof gt_pk) != 0
            || memcmp(official_sk, gt_sk, sizeof gt_sk) != 0) {
        fprintf(stderr, "keypair byte differential failed round=%u\n", round);
        return 0;
    }

    reset_rng(2, round);
    const int official_enc_rc = crypto_kem_enc(official_ct, official_ss,
                                                official_pk);
    reset_rng(2, round);
    const int gt_enc_rc = gt_crypto_kem_enc(gt_ct, gt_ss, gt_pk);
    if (official_enc_rc != gt_enc_rc
            || memcmp(official_ct, gt_ct, sizeof gt_ct) != 0
            || memcmp(official_ss, gt_ss, sizeof gt_ss) != 0) {
        fprintf(stderr, "encapsulation byte differential failed round=%u\n", round);
        return 0;
    }

    const int official_dec_rc = crypto_kem_dec(official_dec, official_ct,
                                                official_sk);
    const int gt_dec_rc = gt_crypto_kem_dec(gt_dec, gt_ct, gt_sk);
    if (official_dec_rc != gt_dec_rc
            || memcmp(official_dec, gt_dec, sizeof gt_dec) != 0
            || memcmp(gt_dec, gt_ss, sizeof gt_dec) != 0) {
        fprintf(stderr, "decapsulation byte differential failed round=%u\n", round);
        return 0;
    }

    /* Canonical encoding of q in the first 12-bit slot is malformed. */
    gt_pk[0] = (unsigned char)(NTRUPLUS_Q & 0xff);
    gt_pk[1] = (unsigned char)((gt_pk[1] & 0xf0U) | (NTRUPLUS_Q >> 8));
    memcpy(official_pk, gt_pk, sizeof gt_pk);
    memset(official_ct, 0xa5, sizeof official_ct);
    memset(gt_ct, 0xa5, sizeof gt_ct);
    memset(official_ss, 0xa5, sizeof official_ss);
    memset(gt_ss, 0xa5, sizeof gt_ss);
    reset_rng(3, round);
    const int official_bad_pk_rc = crypto_kem_enc(official_ct, official_ss,
                                                   official_pk);
    reset_rng(3, round);
    const int gt_bad_pk_rc = gt_crypto_kem_enc(gt_ct, gt_ss, gt_pk);
    if (official_bad_pk_rc != gt_bad_pk_rc
            || memcmp(official_ct, gt_ct, sizeof gt_ct) != 0
            || memcmp(official_ss, gt_ss, sizeof gt_ss) != 0) {
        fprintf(stderr, "malformed-pk behavior failed round=%u\n", round);
        return 0;
    }

    /* Restore valid objects, then make the ciphertext non-canonical. */
    reset_rng(1, round);
    (void)crypto_kem_keypair(official_pk, official_sk);
    reset_rng(2, round);
    (void)crypto_kem_enc(official_ct, official_ss, official_pk);
    memcpy(gt_sk, official_sk, sizeof gt_sk);
    memcpy(gt_ct, official_ct, sizeof gt_ct);
    official_ct[0] = (unsigned char)(NTRUPLUS_Q & 0xff);
    official_ct[1] = (unsigned char)((official_ct[1] & 0xf0U)
                                    | (NTRUPLUS_Q >> 8));
    memcpy(gt_ct, official_ct, sizeof gt_ct);
    memset(official_dec, 0xa5, sizeof official_dec);
    memset(gt_dec, 0xa5, sizeof gt_dec);
    const int official_bad_ct_rc = crypto_kem_dec(official_dec, official_ct,
                                                   official_sk);
    const int gt_bad_ct_rc = gt_crypto_kem_dec(gt_dec, gt_ct, gt_sk);
    if (official_bad_ct_rc != gt_bad_ct_rc
            || memcmp(official_dec, gt_dec, sizeof gt_dec) != 0) {
        fprintf(stderr, "malformed-ct behavior failed round=%u\n", round);
        return 0;
    }
    return 1;
}

int main(void)
{
    int failures = 0;
    for (unsigned round = 0; round < 8; ++round)
        failures += !check_one(round);
    printf("canonical-kem-byte-exact-rounds=8 failures=%d\n", failures);
    return failures == 0 ? 0 : 1;
}
