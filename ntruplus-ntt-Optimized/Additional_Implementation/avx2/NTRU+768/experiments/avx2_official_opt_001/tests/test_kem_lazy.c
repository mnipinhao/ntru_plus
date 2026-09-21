#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"
#include "kat/rng.h"

int official_ref_keypair(unsigned char *, unsigned char *);
int official_ref_enc(unsigned char *, unsigned char *, const unsigned char *);
int official_ref_dec(unsigned char *, const unsigned char *, const unsigned char *);
int official_lazy_keypair(unsigned char *, unsigned char *);
int official_lazy_enc(unsigned char *, unsigned char *, const unsigned char *);
int official_lazy_dec(unsigned char *, const unsigned char *, const unsigned char *);

static unsigned long long random_calls;
void __real_randombytes(unsigned char *, unsigned long long);
void __wrap_randombytes(unsigned char *out, unsigned long long length) {
    random_calls++;
    __real_randombytes(out, length);
}

static void seed_rng(unsigned trial) {
    unsigned char entropy[48];
    for (size_t i = 0; i < sizeof entropy; i++)
        entropy[i] = (unsigned char)(i * 31U + trial * 13U);
    randombytes_init(entropy, NULL, 256);
}

int main(void) {
    unsigned char pk_o[NTRUPLUS_PUBLICKEYBYTES], pk_l[NTRUPLUS_PUBLICKEYBYTES];
    unsigned char sk_o[NTRUPLUS_SECRETKEYBYTES], sk_l[NTRUPLUS_SECRETKEYBYTES];
    unsigned char ct_o[NTRUPLUS_CIPHERTEXTBYTES], ct_l[NTRUPLUS_CIPHERTEXTBYTES];
    unsigned char ss_o[NTRUPLUS_SSBYTES], ss_l[NTRUPLUS_SSBYTES];
    unsigned char dec_o[NTRUPLUS_SSBYTES], dec_l[NTRUPLUS_SSBYTES];
    unsigned long long retries = 0;

    for (unsigned trial = 0; trial < 100; trial++) {
        seed_rng(trial);
        random_calls = 0;
        int status_o = official_ref_keypair(pk_o, sk_o);
        unsigned long long calls_o = random_calls;
        seed_rng(trial);
        random_calls = 0;
        int status_l = official_lazy_keypair(pk_l, sk_l);
        unsigned long long calls_l = random_calls;
        if (status_o || status_l || calls_o != calls_l || calls_o < 2 ||
            memcmp(pk_o, pk_l, sizeof pk_o) || memcmp(sk_o, sk_l, sizeof sk_o)) {
            fprintf(stderr, "lazy Keygen mismatch trial=%u\n", trial);
            return 1;
        }
        retries += calls_o - 2;

        seed_rng(trial + 1000U);
        status_o = official_ref_enc(ct_o, ss_o, pk_o);
        seed_rng(trial + 1000U);
        status_l = official_lazy_enc(ct_l, ss_l, pk_l);
        if (status_o || status_l || memcmp(ct_o, ct_l, sizeof ct_o) ||
            memcmp(ss_o, ss_l, sizeof ss_o)) {
            fprintf(stderr, "lazy Encap mismatch trial=%u\n", trial);
            return 1;
        }

        status_o = official_ref_dec(dec_o, ct_o, sk_o);
        status_l = official_lazy_dec(dec_l, ct_l, sk_l);
        if (status_o || status_l || memcmp(dec_o, dec_l, sizeof dec_o) ||
            memcmp(dec_o, ss_o, sizeof dec_o)) {
            fprintf(stderr, "lazy Decap mismatch trial=%u\n", trial);
            return 1;
        }

        ct_o[(trial * 17U) % sizeof ct_o] ^= (unsigned char)(1U << (trial & 7U));
        ct_l[(trial * 17U) % sizeof ct_l] ^= (unsigned char)(1U << (trial & 7U));
        status_o = official_ref_dec(dec_o, ct_o, sk_o);
        status_l = official_lazy_dec(dec_l, ct_l, sk_l);
        if (status_o != status_l || memcmp(dec_o, dec_l, sizeof dec_o)) {
            fprintf(stderr, "lazy invalid-CT mismatch trial=%u\n", trial);
            return 1;
        }
    }

    pk_o[0] = (unsigned char)NTRUPLUS_Q;
    pk_o[1] = (unsigned char)((pk_o[1] & 0xf0U) | (NTRUPLUS_Q >> 8));
    memset(ct_o, 0xa5, sizeof ct_o);
    memset(ct_l, 0xa5, sizeof ct_l);
    memset(ss_o, 0xa5, sizeof ss_o);
    memset(ss_l, 0xa5, sizeof ss_l);
    seed_rng(9001);
    int status_o = official_ref_enc(ct_o, ss_o, pk_o);
    seed_rng(9001);
    int status_l = official_lazy_enc(ct_l, ss_l, pk_o);
    unsigned char zero_ct[NTRUPLUS_CIPHERTEXTBYTES] = {0};
    unsigned char zero_ss[NTRUPLUS_SSBYTES] = {0};
    if (status_o != 1 || status_l != 1 ||
        memcmp(ct_o, zero_ct, sizeof ct_o) || memcmp(ct_l, zero_ct, sizeof ct_l) ||
        memcmp(ss_o, zero_ss, sizeof ss_o) || memcmp(ss_l, zero_ss, sizeof ss_l)) {
        fputs("lazy invalid-PK behavior mismatch\n", stderr);
        return 1;
    }
    printf("Official caller-lazy KEM byte differential: pass (100 vectors, %llu matched Keygen retries)\n", retries);
    return 0;
}
