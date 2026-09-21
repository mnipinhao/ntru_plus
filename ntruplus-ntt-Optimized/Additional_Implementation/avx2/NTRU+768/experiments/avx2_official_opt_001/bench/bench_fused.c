#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "cpucycles.h"
#include "kat/rng.h"
#include "params.h"
#include "poly.h"

int official_ref_keypair(unsigned char *, unsigned char *);
int officialopt_ref_enc_derand(uint8_t *, uint8_t *, const uint8_t *, const uint8_t *);
int officialopt_fused_enc_derand(uint8_t *, uint8_t *, const uint8_t *, const uint8_t *);
void ntruplus768_officialopt_basemul_add(poly *, const poly *, const poly *, const poly *);

enum { BANKS = 16, OBS = 32, BLOCKS = 8 };
static poly h[BANKS], r[BANKS], m[BANKS], output[BANKS];
static uint8_t pk[BANKS][NTRUPLUS_PUBLICKEYBYTES];
static uint8_t sk[NTRUPLUS_SECRETKEYBYTES];
static uint8_t coins[BANKS][NTRUPLUS_N / 8];
static uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES], ss[NTRUPLUS_SSBYTES];

static void setup(void) {
    uint8_t entropy[48], sample[NTRUPLUS_N / 4];
    for (unsigned i = 0; i < sizeof entropy; i++) entropy[i] = (uint8_t)(17U + 13U*i);
    randombytes_init(entropy, NULL, 256);
    if (official_ref_keypair(pk[0], sk)) __builtin_trap();
    for (unsigned b = 0; b < BANKS; b++) {
        memcpy(pk[b], pk[0], sizeof pk[0]);
        if (poly_frombytes(&h[b], pk[b])) __builtin_trap();
        for (unsigned i = 0; i < sizeof sample; i++) sample[i] = (uint8_t)(i*31U + b*7U);
        poly_cbd1(&r[b], sample);
        poly_ntt(&r[b]);
        for (unsigned i = 0; i < sizeof sample; i++) sample[i] = (uint8_t)(i*19U + b*11U);
        poly_cbd1(&m[b], sample);
        poly_ntt(&m[b]);
        for (unsigned i = 0; i < sizeof coins[b]; i++) coins[b][i] = (uint8_t)(i*23U + b);
    }
    poly a, c;
    poly_basemul(&a, &h[0], &r[0]);
    poly_add(&a, &a, &m[0]);
    ntruplus768_officialopt_basemul_add(&c, &h[0], &r[0], &m[0]);
    if (memcmp(&a, &c, sizeof a)) __builtin_trap();
    uint8_t ct_ref[NTRUPLUS_CIPHERTEXTBYTES], ss_ref[NTRUPLUS_SSBYTES];
    officialopt_ref_enc_derand(ct_ref, ss_ref, pk[0], coins[0]);
    officialopt_fused_enc_derand(ct, ss, pk[0], coins[0]);
    if (memcmp(ct_ref, ct, sizeof ct) || memcmp(ss_ref, ss, sizeof ss)) __builtin_trap();
    fputs("preflight=pass\n", stderr);
}

static void one(int region, int variant, unsigned bank) {
    if (region == 0) {
        if (variant == 0) {
            poly_basemul(&output[bank], &h[bank], &r[bank]);
            poly_add(&output[bank], &output[bank], &m[bank]);
        } else {
            ntruplus768_officialopt_basemul_add(&output[bank],
                &h[bank], &r[bank], &m[bank]);
        }
    } else {
        if (variant == 0) officialopt_ref_enc_derand(ct, ss, pk[bank], coins[bank]);
        else officialopt_fused_enc_derand(ct, ss, pk[bank], coins[bank]);
    }
}

int main(void) {
    setup();
    cpucycles_tracesetup();
    fprintf(stderr, "cpucycles=%s persecond=%lld\n",
            cpucycles_implementation(), cpucycles_persecond());
    puts("region,variant,block,observation,cycles");
    for (int region = 0; region < 2; region++) {
        for (int block = 0; block < BLOCKS; block++) {
            const int order[4] = {block & 1, (block & 1) ^ 1,
                                  (block & 1) ^ 1, block & 1};
            for (int slot = 0; slot < 4; slot++) {
                int variant = order[slot];
                for (int j = 0; j < 4; j++) one(region,variant,(unsigned)j);
                for (int obs = 0; obs < OBS; obs++) {
                    unsigned bank = (unsigned)(obs & (BANKS - 1));
                    long long before = cpucycles();
                    one(region,variant,bank);
                    long long cycles = cpucycles() - before;
                    printf("%d,%d,%d,%d,%lld\n",region,variant,block,obs,cycles);
                }
            }
        }
    }
    return 0;
}
