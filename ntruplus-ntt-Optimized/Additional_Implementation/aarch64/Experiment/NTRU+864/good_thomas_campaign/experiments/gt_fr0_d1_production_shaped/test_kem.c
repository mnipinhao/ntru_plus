#include "api.h"
#include "randombytes.h"

#include <stdint.h>
#include <stdio.h>
#include <string.h>

int gt_old_crypto_kem_keypair(uint8_t *, uint8_t *);
int gt_old_crypto_kem_enc(uint8_t *, uint8_t *, const uint8_t *);
int gt_old_crypto_kem_dec(uint8_t *, const uint8_t *, const uint8_t *);
int gt_d1_crypto_kem_keypair(uint8_t *, uint8_t *);
int gt_d1_crypto_kem_enc(uint8_t *, uint8_t *, const uint8_t *);
int gt_d1_crypto_kem_dec(uint8_t *, const uint8_t *, const uint8_t *);

static uint64_t random_state;

static void reset_random(uint64_t seed)
{
    random_state = seed ? seed : 1;
}

void randombytes(uint8_t *out, size_t outlen)
{
    for (size_t i = 0; i < outlen; i++) {
        random_state ^= random_state << 13;
        random_state ^= random_state >> 7;
        random_state ^= random_state << 17;
        out[i] = (uint8_t)random_state;
    }
}

static int different(const void *a, const void *b, size_t length)
{
    return memcmp(a, b, length) != 0;
}

int main(void)
{
    uint8_t pk[3][CRYPTO_PUBLICKEYBYTES], sk[3][CRYPTO_SECRETKEYBYTES];
    uint8_t ct[3][CRYPTO_CIPHERTEXTBYTES], ss_enc[3][CRYPTO_BYTES];
    uint8_t ss_dec[3][CRYPTO_BYTES], bad_ct[CRYPTO_CIPHERTEXTBYTES];
    int mismatches = 0;
    int key_bytes = 0, enc_bytes = 0, dec_success = 0, dec_bytes = 0;
    int fail_codes = 0, fail_bytes = 0;

    for (uint64_t test = 0; test < 8; test++) {
        uint64_t key_seed = 0xd1f10000ULL + 0x9e37ULL * test;
        uint64_t enc_seed = 0xd1f20000ULL + 0x7f4aULL * test;
        reset_random(key_seed); crypto_kem_keypair(pk[0], sk[0]);
        reset_random(key_seed); gt_old_crypto_kem_keypair(pk[1], sk[1]);
        reset_random(key_seed); gt_d1_crypto_kem_keypair(pk[2], sk[2]);
        key_bytes += different(pk[0], pk[1], sizeof pk[0]);
        key_bytes += different(pk[0], pk[2], sizeof pk[0]);
        key_bytes += different(sk[0], sk[1], sizeof sk[0]);
        key_bytes += different(sk[0], sk[2], sizeof sk[0]);

        reset_random(enc_seed); crypto_kem_enc(ct[0], ss_enc[0], pk[0]);
        reset_random(enc_seed); gt_old_crypto_kem_enc(ct[1], ss_enc[1], pk[1]);
        reset_random(enc_seed); gt_d1_crypto_kem_enc(ct[2], ss_enc[2], pk[2]);
        enc_bytes += different(ct[0], ct[1], sizeof ct[0]);
        enc_bytes += different(ct[0], ct[2], sizeof ct[0]);
        enc_bytes += different(ss_enc[0], ss_enc[1], sizeof ss_enc[0]);
        enc_bytes += different(ss_enc[0], ss_enc[2], sizeof ss_enc[0]);

        dec_success += crypto_kem_dec(ss_dec[0], ct[0], sk[0]);
        dec_success += gt_old_crypto_kem_dec(ss_dec[1], ct[1], sk[1]);
        dec_success += gt_d1_crypto_kem_dec(ss_dec[2], ct[2], sk[2]);
        for (int i = 0; i < 3; i++)
            dec_bytes += different(ss_enc[0], ss_dec[i], CRYPTO_BYTES);

        memcpy(bad_ct, ct[0], sizeof bad_ct);
        bad_ct[(37 * test + 11) % sizeof bad_ct] ^= 0x80;
        int fail0 = crypto_kem_dec(ss_dec[0], bad_ct, sk[0]);
        int fail1 = gt_old_crypto_kem_dec(ss_dec[1], bad_ct, sk[1]);
        int fail2 = gt_d1_crypto_kem_dec(ss_dec[2], bad_ct, sk[2]);
        fail_codes += (fail0 != fail1) || (fail0 != fail2) || (fail0 != 1);
        fail_bytes += different(ss_dec[0], ss_dec[1], CRYPTO_BYTES);
        fail_bytes += different(ss_dec[0], ss_dec[2], CRYPTO_BYTES);
    }
    mismatches = key_bytes + enc_bytes + dec_success + dec_bytes
               + fail_codes + fail_bytes;
    printf("detail,key_bytes=%d,enc_bytes=%d,dec_success=%d,dec_bytes=%d,"
           "fail_codes=%d,fail_bytes=%d\n", key_bytes, enc_bytes,
           dec_success, dec_bytes, fail_codes, fail_bytes);
    printf("d1_p1_kem=%.4s cases=8 mismatches=%d\n",
           mismatches == 0 ? "pass" : "fail", mismatches);
    printf("production_linked=0\n");
    return mismatches != 0;
}
