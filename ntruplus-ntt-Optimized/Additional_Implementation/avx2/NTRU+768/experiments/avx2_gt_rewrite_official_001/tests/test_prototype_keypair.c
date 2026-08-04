#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "api.h"
#include "kat/rng.h"
#include "prototype_keypair_adapter.h"

static void reset_rng(unsigned domain, unsigned round)
{
    unsigned char entropy[48];
    for (size_t i = 0; i < sizeof entropy; ++i)
        entropy[i] = (unsigned char)(i + 53U * domain + 97U * round);
    randombytes_init(entropy, NULL, 256);
}

static int check_keypair(unsigned round)
{
    unsigned char official_pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char official_sk[CRYPTO_SECRETKEYBYTES];
    unsigned char prototype_pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char prototype_sk[CRYPTO_SECRETKEYBYTES];
    unsigned char no_clear_pk[CRYPTO_PUBLICKEYBYTES];
    unsigned char no_clear_sk[CRYPTO_SECRETKEYBYTES];
    unsigned char official_ct[CRYPTO_CIPHERTEXTBYTES];
    unsigned char prototype_ct[CRYPTO_CIPHERTEXTBYTES];
    unsigned char official_ss[CRYPTO_BYTES];
    unsigned char prototype_ss[CRYPTO_BYTES];
    unsigned char official_dec[CRYPTO_BYTES];
    unsigned char prototype_dec[CRYPTO_BYTES];

    reset_rng(1, round);
    const int official_rc = crypto_kem_keypair(official_pk, official_sk);
    reset_rng(1, round);
    const int prototype_rc = prototype_crypto_kem_keypair(
        prototype_pk, prototype_sk);
    reset_rng(1, round);
    const int no_clear_rc = prototype_crypto_kem_keypair_no_clear(
        no_clear_pk, no_clear_sk);

    if (official_rc != prototype_rc || official_rc != no_clear_rc
            || memcmp(official_pk, prototype_pk, sizeof official_pk) != 0
            || memcmp(official_sk, prototype_sk, sizeof official_sk) != 0
            || memcmp(official_pk, no_clear_pk, sizeof official_pk) != 0
            || memcmp(official_sk, no_clear_sk, sizeof official_sk) != 0) {
        fprintf(stderr, "prototype keypair differential failed round=%u\n",
                round);
        return 0;
    }

    reset_rng(2, round);
    const int official_enc_rc = crypto_kem_enc(
        official_ct, official_ss, official_pk);
    reset_rng(2, round);
    const int prototype_enc_rc = crypto_kem_enc(
        prototype_ct, prototype_ss, prototype_pk);
    const int official_dec_rc = crypto_kem_dec(
        official_dec, official_ct, official_sk);
    const int prototype_dec_rc = crypto_kem_dec(
        prototype_dec, prototype_ct, prototype_sk);
    if (official_enc_rc != prototype_enc_rc
            || official_dec_rc != prototype_dec_rc
            || memcmp(official_ct, prototype_ct, sizeof official_ct) != 0
            || memcmp(official_ss, prototype_ss, sizeof official_ss) != 0
            || memcmp(official_dec, prototype_dec, sizeof official_dec) != 0
            || memcmp(prototype_ss, prototype_dec, sizeof prototype_ss) != 0) {
        fprintf(stderr, "prototype hybrid triplet failed round=%u\n", round);
        return 0;
    }
    return 1;
}

int main(void)
{
    int failures = 0;
    for (unsigned round = 0; round < 100; ++round)
        failures += !check_keypair(round);
    printf("prototype-native-keypair-and-hybrid-triplet-byte-exact-rounds=100 failures=%d\n",
           failures);
    return failures == 0 ? 0 : 1;
}
