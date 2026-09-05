#include "api.h"
#include "randombytes.h"
#include <stdint.h>
#include <stdio.h>
#include <string.h>

int gt_base_crypto_kem_keypair(uint8_t *, uint8_t *);
int gt_base_crypto_kem_enc(uint8_t *, uint8_t *, const uint8_t *);
int gt_base_crypto_kem_dec(uint8_t *, const uint8_t *, const uint8_t *);
int gt_bytes_crypto_kem_keypair(uint8_t *, uint8_t *);
int gt_bytes_crypto_kem_enc(uint8_t *, uint8_t *, const uint8_t *);
int gt_bytes_crypto_kem_dec(uint8_t *, const uint8_t *, const uint8_t *);

static uint64_t random_state;
static void reset_random(uint64_t seed) { random_state = seed ? seed : 1; }
void randombytes(uint8_t *out, size_t n)
{
    for (size_t i = 0; i < n; i++) {
        random_state ^= random_state << 13;
        random_state ^= random_state >> 7;
        random_state ^= random_state << 17;
        out[i] = (uint8_t)random_state;
    }
}
static int different(const void *a, const void *b, size_t n)
{ return memcmp(a, b, n) != 0; }

int main(void)
{
    uint8_t pk[3][CRYPTO_PUBLICKEYBYTES], sk[3][CRYPTO_SECRETKEYBYTES];
    uint8_t ct[3][CRYPTO_CIPHERTEXTBYTES], se[3][CRYPTO_BYTES];
    uint8_t sd[3][CRYPTO_BYTES], bad[CRYPTO_CIPHERTEXTBYTES];
    int mismatch = 0;
    for (uint64_t t = 0; t < 8; t++) {
        uint64_t ks = 0xb4000000ULL + 0x9e37ULL * t;
        uint64_t es = 0xb5000000ULL + 0x7f4aULL * t;
        reset_random(ks); crypto_kem_keypair(pk[0], sk[0]);
        reset_random(ks); gt_base_crypto_kem_keypair(pk[1], sk[1]);
        reset_random(ks); gt_bytes_crypto_kem_keypair(pk[2], sk[2]);
        for (int i = 1; i < 3; i++) {
            mismatch += different(pk[0], pk[i], sizeof pk[0]);
            mismatch += different(sk[0], sk[i], sizeof sk[0]);
        }
        reset_random(es); crypto_kem_enc(ct[0], se[0], pk[0]);
        reset_random(es); gt_base_crypto_kem_enc(ct[1], se[1], pk[1]);
        reset_random(es); gt_bytes_crypto_kem_enc(ct[2], se[2], pk[2]);
        for (int i = 1; i < 3; i++) {
            mismatch += different(ct[0], ct[i], sizeof ct[0]);
            mismatch += different(se[0], se[i], sizeof se[0]);
        }
        mismatch += crypto_kem_dec(sd[0], ct[0], sk[0]);
        mismatch += gt_base_crypto_kem_dec(sd[1], ct[1], sk[1]);
        mismatch += gt_bytes_crypto_kem_dec(sd[2], ct[2], sk[2]);
        for (int i = 0; i < 3; i++) mismatch += different(se[0], sd[i], sizeof sd[0]);
        memcpy(bad, ct[0], sizeof bad);
        bad[(37 * t + 11) % sizeof bad] ^= 0x80;
        int f0 = crypto_kem_dec(sd[0], bad, sk[0]);
        int f1 = gt_base_crypto_kem_dec(sd[1], bad, sk[1]);
        int f2 = gt_bytes_crypto_kem_dec(sd[2], bad, sk[2]);
        mismatch += f0 != 1 || f1 != f0 || f2 != f0;
        mismatch += different(sd[0], sd[1], sizeof sd[0]);
        mismatch += different(sd[0], sd[2], sizeof sd[0]);
    }
    printf("p3b4_kem=%s cases=8 mismatches=%d\n", mismatch ? "fail" : "pass", mismatch);
    printf("production_linked=0\n");
    return mismatch != 0;
}
