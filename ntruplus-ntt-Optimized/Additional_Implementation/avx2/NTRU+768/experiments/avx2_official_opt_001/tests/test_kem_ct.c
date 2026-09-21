#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"
#include "kat/rng.h"

int official_ref_keypair(unsigned char *, unsigned char *);
int official_ref_enc(unsigned char *, unsigned char *, const unsigned char *);
int official_ref_dec(unsigned char *, const unsigned char *, const unsigned char *);
int official_ct_dec(unsigned char *, const unsigned char *, const unsigned char *);

static void seed_rng(unsigned trial) {
    unsigned char entropy[48];
    for (size_t i = 0; i < sizeof entropy; i++)
        entropy[i] = (unsigned char)(i * 31U + trial * 13U);
    randombytes_init(entropy, NULL, 256);
}

int main(void) {
    unsigned char pk[NTRUPLUS_PUBLICKEYBYTES], sk[NTRUPLUS_SECRETKEYBYTES];
    unsigned char ct[NTRUPLUS_CIPHERTEXTBYTES];
    unsigned char ss[NTRUPLUS_SSBYTES], dec_o[NTRUPLUS_SSBYTES], dec_ct[NTRUPLUS_SSBYTES];
    for (unsigned trial = 0; trial < 100; trial++) {
        seed_rng(trial);
        if (official_ref_keypair(pk, sk)) return 1;
        seed_rng(trial + 1000);
        if (official_ref_enc(ct, ss, pk)) return 1;
        int status_o = official_ref_dec(dec_o, ct, sk);
        int status_ct = official_ct_dec(dec_ct, ct, sk);
        if (status_o || status_ct || memcmp(dec_o, dec_ct, sizeof dec_o) ||
            memcmp(dec_o, ss, sizeof ss)) {
            fprintf(stderr, "CT Decap valid KEM mismatch trial=%u\n", trial);
            return 1;
        }
        ct[(trial * 17U) % sizeof ct] ^= (unsigned char)(1U << (trial & 7U));
        status_o = official_ref_dec(dec_o, ct, sk);
        status_ct = official_ct_dec(dec_ct, ct, sk);
        if (status_o != status_ct || memcmp(dec_o, dec_ct, sizeof dec_o)) {
            fprintf(stderr, "CT Decap invalid ciphertext mismatch trial=%u\n", trial);
            return 1;
        }
        unsigned char saved_sk0 = sk[0], saved_sk1 = sk[1];
        sk[0] = 0xff;
        sk[1] = 0xff;
        status_o = official_ref_dec(dec_o, ct, sk);
        status_ct = official_ct_dec(dec_ct, ct, sk);
        sk[0] = saved_sk0;
        sk[1] = saved_sk1;
        if (status_o != status_ct || memcmp(dec_o, dec_ct, sizeof dec_o)) {
            fprintf(stderr, "CT Decap invalid secret-key mismatch trial=%u\n", trial);
            return 1;
        }
    }
    puts("Official vs CT inverse Decap: 100 valid, 100 tampered ciphertext, and 100 invalid secret-key cases byte-exact");
    return 0;
}
