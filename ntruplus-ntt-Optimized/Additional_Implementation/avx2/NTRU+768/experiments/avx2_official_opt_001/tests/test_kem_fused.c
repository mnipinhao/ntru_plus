#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"
#include "kat/rng.h"

int official_ref_keypair(unsigned char *, unsigned char *);
int official_ref_enc(unsigned char *, unsigned char *, const unsigned char *);
int official_ref_dec(unsigned char *, const unsigned char *, const unsigned char *);
int official_fused_keypair(unsigned char *, unsigned char *);
int official_fused_enc(unsigned char *, unsigned char *, const unsigned char *);
int official_fused_dec(unsigned char *, const unsigned char *, const unsigned char *);

static unsigned long long random_calls;
void __real_randombytes(unsigned char *, unsigned long long);
void __wrap_randombytes(unsigned char *out, unsigned long long length) {
    random_calls++;
    __real_randombytes(out, length);
}

static void init_rng(unsigned trial) {
    unsigned char entropy[48];
    for (size_t i = 0; i < sizeof entropy; i++)
        entropy[i] = (unsigned char)(i * 31U + trial * 13U);
    randombytes_init(entropy, NULL, 256);
}

int main(void) {
    unsigned char pk0[NTRUPLUS_PUBLICKEYBYTES], pk1[NTRUPLUS_PUBLICKEYBYTES];
    unsigned char sk0[NTRUPLUS_SECRETKEYBYTES], sk1[NTRUPLUS_SECRETKEYBYTES];
    unsigned char ct0[NTRUPLUS_CIPHERTEXTBYTES], ct1[NTRUPLUS_CIPHERTEXTBYTES];
    unsigned char ss0[NTRUPLUS_SSBYTES], ss1[NTRUPLUS_SSBYTES];
    unsigned char dec0[NTRUPLUS_SSBYTES], dec1[NTRUPLUS_SSBYTES];
    unsigned long long retries = 0;

    for (unsigned trial = 0; trial < 100; trial++) {
        init_rng(trial);
        random_calls = 0;
        int key0 = official_ref_keypair(pk0, sk0);
        unsigned long long calls0 = random_calls;
        init_rng(trial);
        random_calls = 0;
        int key1 = official_fused_keypair(pk1, sk1);
        unsigned long long calls1 = random_calls;
        if (key0 || key1 || memcmp(pk0, pk1, sizeof pk0) ||
            memcmp(sk0, sk1, sizeof sk0) || calls0 != calls1 || calls0 < 2) {
            fprintf(stderr, "keypair mismatch trial=%u\n", trial);
            return 1;
        }
        retries += calls0 - 2;
        init_rng(trial + 1000U);
        int enc0 = official_ref_enc(ct0, ss0, pk0);
        init_rng(trial + 1000U);
        int enc1 = official_fused_enc(ct1, ss1, pk1);
        if (enc0 || enc1 || memcmp(ct0, ct1, sizeof ct0) ||
            memcmp(ss0, ss1, sizeof ss0)) {
            fprintf(stderr, "encap mismatch trial=%u\n", trial);
            return 1;
        }
        int dec_status0 = official_ref_dec(dec0, ct0, sk0);
        int dec_status1 = official_fused_dec(dec1, ct1, sk1);
        if (dec_status0 || dec_status1 || memcmp(dec0, ss0, sizeof dec0) ||
            memcmp(dec1, ss1, sizeof dec1)) {
            fprintf(stderr, "decap mismatch trial=%u\n", trial);
            return 1;
        }
        ct0[(trial * 17U) % sizeof ct0] ^= (unsigned char)(1U << (trial & 7U));
        ct1[(trial * 17U) % sizeof ct1] ^= (unsigned char)(1U << (trial & 7U));
        dec_status0 = official_ref_dec(dec0, ct0, sk0);
        dec_status1 = official_fused_dec(dec1, ct1, sk1);
        if (dec_status0 != dec_status1 || memcmp(dec0, dec1, sizeof dec0)) {
            fprintf(stderr, "invalid CT mismatch trial=%u\n", trial);
            return 1;
        }
    }
    pk0[0] = (unsigned char)NTRUPLUS_Q;
    pk0[1] = (unsigned char)((pk0[1] & 0xf0U) | (NTRUPLUS_Q >> 8));
    memset(ct0, 0xa5, sizeof ct0);
    memset(ct1, 0xa5, sizeof ct1);
    memset(ss0, 0xa5, sizeof ss0);
    memset(ss1, 0xa5, sizeof ss1);
    init_rng(9001);
    int invalid0 = official_ref_enc(ct0, ss0, pk0);
    init_rng(9001);
    int invalid1 = official_fused_enc(ct1, ss1, pk0);
    unsigned char zero_ct[NTRUPLUS_CIPHERTEXTBYTES] = {0};
    unsigned char zero_ss[NTRUPLUS_SSBYTES] = {0};
    if (invalid0 != 1 || invalid1 != 1 ||
        memcmp(ct0, zero_ct, sizeof ct0) || memcmp(ct1, zero_ct, sizeof ct1) ||
        memcmp(ss0, zero_ss, sizeof ss0) || memcmp(ss1, zero_ss, sizeof ss1)) {
        fputs("invalid PK behavior mismatch\n", stderr);
        return 1;
    }
    printf("Official/fused KEM byte differential: pass (100 vectors, %llu matched keygen retries)\n",
           retries);
    return 0;
}
