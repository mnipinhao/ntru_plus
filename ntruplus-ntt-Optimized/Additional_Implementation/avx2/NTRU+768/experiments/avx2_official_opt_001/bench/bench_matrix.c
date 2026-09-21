#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "cpucycles.h"
#include "kat/rng.h"
#include "params.h"
#include "poly.h"

int official_ref_keypair(unsigned char *, unsigned char *);
int official_dup_keypair(unsigned char *, unsigned char *);
int official_fused_keypair(unsigned char *, unsigned char *);
int official_shared_keypair(unsigned char *, unsigned char *);
int official_ref_dec(unsigned char *, const unsigned char *, const unsigned char *);
int official_dup_dec(unsigned char *, const unsigned char *, const unsigned char *);
int official_fused_dec(unsigned char *, const unsigned char *, const unsigned char *);
int official_shared_dec(unsigned char *, const unsigned char *, const unsigned char *);
int official_forward_keypair(unsigned char *, unsigned char *);
int official_forward_dec(unsigned char *, const unsigned char *, const unsigned char *);
int officialopt_forward_enc_derand(uint8_t *, uint8_t *, const uint8_t *, const uint8_t *);
int officialopt_ref_enc_derand(uint8_t *, uint8_t *, const uint8_t *, const uint8_t *);
int officialopt_dup_enc_derand(uint8_t *, uint8_t *, const uint8_t *, const uint8_t *);
int officialopt_fused_enc_derand(uint8_t *, uint8_t *, const uint8_t *, const uint8_t *);
int officialopt_shared_enc_derand(uint8_t *, uint8_t *, const uint8_t *, const uint8_t *);
void ntruplus768_officialopt_dup_basemul(poly *, const poly *, const poly *);
void ntruplus768_officialopt_basemul_add(poly *, const poly *, const poly *, const poly *);
void ntruplus768_officialopt_shared_add(poly *, const poly *, const poly *, const poly *);
void ntruplus768_officialopt_ntt_early_const(poly *);

enum { BANKS = 16, OBS = 32, BLOCKS = 8, VARIANTS = 5, REGIONS = 5 };
static poly h[BANKS], r[BANKS], m[BANKS], out[BANKS], r_coeff[BANKS];
static uint8_t pk[BANKS][NTRUPLUS_PUBLICKEYBYTES];
static uint8_t sk[BANKS][NTRUPLUS_SECRETKEYBYTES];
static uint8_t ct[BANKS][NTRUPLUS_CIPHERTEXTBYTES];
static uint8_t coins[BANKS][NTRUPLUS_N / 8];
static uint8_t pk_out[BANKS][NTRUPLUS_PUBLICKEYBYTES];
static uint8_t sk_out[BANKS][NTRUPLUS_SECRETKEYBYTES];
static uint8_t ct_out[BANKS][NTRUPLUS_CIPHERTEXTBYTES];
static uint8_t ss_out[BANKS][NTRUPLUS_SSBYTES];
static volatile int status_sink;

static void seed_rng(unsigned tag) {
    uint8_t entropy[48];
    for (unsigned i = 0; i < 48; i++) entropy[i] = (uint8_t)(i * 31U + tag * 13U);
    randombytes_init(entropy, NULL, 256);
}

static void fixture(void) {
    uint8_t sample[NTRUPLUS_N / 4];
    for (unsigned b = 0; b < BANKS; b++) {
        seed_rng(1000U + b);
        if (official_ref_keypair(pk[b], sk[b])) __builtin_trap();
        if (poly_frombytes(&h[b], pk[b])) __builtin_trap();
        for (unsigned i = 0; i < sizeof sample; i++) sample[i] = (uint8_t)(i*31U+b*7U);
        poly_cbd1(&r[b], sample);
        r_coeff[b] = r[b];
        poly_ntt(&r[b]);
        for (unsigned i = 0; i < sizeof sample; i++) sample[i] = (uint8_t)(i*19U+b*11U);
        poly_cbd1(&m[b], sample);
        poly_ntt(&m[b]);
        for (unsigned i = 0; i < sizeof coins[b]; i++) coins[b][i] = (uint8_t)(i*23U+b);
        uint8_t secret[NTRUPLUS_SSBYTES];
        if (officialopt_ref_enc_derand(ct[b], secret, pk[b], coins[b])) __builtin_trap();
    }
}

typedef void (*operation)(unsigned);
#define FW_FN(label, fn) static void label(unsigned b) { fn(&out[b]); }
FW_FN(fw_o, poly_ntt)
FW_FN(fw_d, poly_ntt)
FW_FN(fw_f, poly_ntt)
FW_FN(fw_s, poly_ntt)
FW_FN(fw_w, ntruplus768_officialopt_ntt_early_const)
#define BM_FN(label, body) static void label(unsigned b) { body; }
BM_FN(bm_o, poly_basemul(&out[b], &h[b], &r[b]); poly_add(&out[b], &out[b], &m[b]))
BM_FN(bm_d, ntruplus768_officialopt_dup_basemul(&out[b], &h[b], &r[b]); poly_add(&out[b], &out[b], &m[b]))
BM_FN(bm_f, ntruplus768_officialopt_basemul_add(&out[b], &h[b], &r[b], &m[b]))
BM_FN(bm_s, ntruplus768_officialopt_shared_add(&out[b], &h[b], &r[b], &m[b]))
BM_FN(bm_w, poly_basemul(&out[b], &h[b], &r[b]); poly_add(&out[b], &out[b], &m[b]))
#define KG_FN(label, fn) static void label(unsigned b) { status_sink = fn(pk_out[b], sk_out[b]); }
KG_FN(kg_o, official_ref_keypair)
KG_FN(kg_d, official_dup_keypair)
KG_FN(kg_f, official_fused_keypair)
KG_FN(kg_s, official_shared_keypair)
KG_FN(kg_w, official_forward_keypair)
#define EN_FN(label, fn) static void label(unsigned b) { status_sink = fn(ct_out[b], ss_out[b], pk[b], coins[b]); }
EN_FN(en_o, officialopt_ref_enc_derand)
EN_FN(en_d, officialopt_dup_enc_derand)
EN_FN(en_f, officialopt_fused_enc_derand)
EN_FN(en_s, officialopt_shared_enc_derand)
EN_FN(en_w, officialopt_forward_enc_derand)
#define DE_FN(label, fn) static void label(unsigned b) { status_sink = fn(ss_out[b], ct[b], sk[b]); }
DE_FN(de_o, official_ref_dec)
DE_FN(de_d, official_dup_dec)
DE_FN(de_f, official_fused_dec)
DE_FN(de_s, official_shared_dec)
DE_FN(de_w, official_forward_dec)
static operation ops[REGIONS][VARIANTS] = {
    {fw_o,fw_d,fw_f,fw_s,fw_w}, {bm_o,bm_d,bm_f,bm_s,bm_w},
    {kg_o,kg_d,kg_f,kg_s,kg_w}, {en_o,en_d,en_f,en_s,en_w},
    {de_o,de_d,de_f,de_s,de_w}
};

static void preflight(void) {
    poly expected;
    for (unsigned b = 0; b < BANKS; b++) {
        out[b] = r_coeff[b];
        fw_o(b); expected = out[b];
        for (unsigned v = 1; v < VARIANTS; v++) {
            out[b] = r_coeff[b];
            ops[0][v](b);
            if (memcmp(&expected, &out[b], sizeof expected)) __builtin_trap();
        }
        bm_o(b); expected = out[b];
        for (unsigned v = 1; v < VARIANTS; v++) {
            ops[1][v](b);
            if (memcmp(&expected, &out[b], sizeof expected)) __builtin_trap();
        }
        for (unsigned region = 2; region < REGIONS; region++) {
            if (region == 2) seed_rng(2000U + b);
            ops[region][0](b);
            uint8_t expected_pk[NTRUPLUS_PUBLICKEYBYTES];
            uint8_t expected_sk[NTRUPLUS_SECRETKEYBYTES];
            uint8_t expected_ct[NTRUPLUS_CIPHERTEXTBYTES];
            uint8_t expected_ss[NTRUPLUS_SSBYTES];
            memcpy(expected_pk, pk_out[b], sizeof expected_pk);
            memcpy(expected_sk, sk_out[b], sizeof expected_sk);
            memcpy(expected_ct, ct_out[b], sizeof expected_ct);
            memcpy(expected_ss, ss_out[b], sizeof expected_ss);
            int expected_status = status_sink;
            for (unsigned v = 1; v < VARIANTS; v++) {
                if (region == 2) seed_rng(2000U + b);
                ops[region][v](b);
                if (status_sink != expected_status ||
                    (region == 2 && (memcmp(expected_pk, pk_out[b], sizeof expected_pk) ||
                                     memcmp(expected_sk, sk_out[b], sizeof expected_sk))) ||
                    (region == 3 && memcmp(expected_ct, ct_out[b], sizeof expected_ct)) ||
                    memcmp(expected_ss, ss_out[b], sizeof expected_ss)) __builtin_trap();
            }
        }
    }
    fputs("preflight=pass\n", stderr);
}

int main(void) {
    fixture();
    preflight();
    cpucycles_tracesetup();
    fprintf(stderr, "cpucycles=%s persecond=%lld\n",
            cpucycles_implementation(), cpucycles_persecond());
    puts("region,variant,block,observation,cycles");
    for (unsigned region = 0; region < REGIONS; region++) {
        for (unsigned block = 0; block < BLOCKS; block++) {
            for (unsigned slot = 0; slot < VARIANTS; slot++) {
                unsigned variant = (block & 1U) ? VARIANTS - 1U - slot : slot;
                operation run = ops[region][variant];
                for (unsigned warm = 0; warm < 4; warm++) {
                    if (region == 0) out[warm] = r_coeff[warm];
                    if (region == 2) seed_rng(5000U + warm);
                    run(warm);
                }
                for (unsigned obs = 0; obs < OBS; obs++) {
                    unsigned bank = obs & (BANKS-1);
                    if (region == 0) out[bank] = r_coeff[bank];
                    if (region == 2) seed_rng(5000U + bank);
                    long long start = cpucycles();
                    run(bank);
                    long long cycles = cpucycles() - start;
                    printf("%u,%u,%u,%u,%lld\n",region,variant,block,obs,cycles);
                }
            }
        }
    }
    return 0;
}
