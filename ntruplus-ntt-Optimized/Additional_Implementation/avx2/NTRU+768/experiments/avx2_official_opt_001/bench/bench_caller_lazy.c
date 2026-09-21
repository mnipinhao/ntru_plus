#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "cpucycles.h"
#include "kat/rng.h"
#include "params.h"
#include "poly.h"

int official_ref_keypair(unsigned char *, unsigned char *);
int official_ref_enc(unsigned char *, unsigned char *, const unsigned char *);
int official_ref_dec(unsigned char *, const unsigned char *, const unsigned char *);
int official_lazy_keypair(unsigned char *, unsigned char *);
int official_lazy_enc(unsigned char *, unsigned char *, const unsigned char *);
int official_lazy_dec(unsigned char *, const unsigned char *, const unsigned char *);
int officialopt_ref_enc_derand(uint8_t *, uint8_t *, const uint8_t *, const uint8_t *);
int officialopt_lazy_enc_derand(uint8_t *, uint8_t *, const uint8_t *, const uint8_t *);
void ntruplus768_officialopt_ntt_caller_lazy(poly *);

enum { BANKS = 16, OBS = 32, BLOCKS = 8, REGIONS = 5 };
static poly r_coeff[BANKS], f_coeff[BANKS], out[BANKS];
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
    for (unsigned i = 0; i < sizeof entropy; i++)
        entropy[i] = (uint8_t)(i * 31U + tag * 13U);
    randombytes_init(entropy, NULL, 256);
}

static void fixture(void) {
    uint8_t sample[NTRUPLUS_N / 4];
    for (unsigned b = 0; b < BANKS; b++) {
        seed_rng(1000U + b);
        if (official_ref_keypair(pk[b], sk[b])) __builtin_trap();
        for (unsigned i = 0; i < sizeof sample; i++)
            sample[i] = (uint8_t)(i * 31U + b * 7U);
        poly_cbd1(&r_coeff[b], sample);
        f_coeff[b] = r_coeff[b];
        poly_triple(&f_coeff[b]);
        f_coeff[b].coeffs[0]++;
        for (unsigned i = 0; i < sizeof coins[b]; i++)
            coins[b][i] = (uint8_t)(i * 23U + b);
        uint8_t secret[NTRUPLUS_SSBYTES];
        if (officialopt_ref_enc_derand(ct[b], secret, pk[b], coins[b])) __builtin_trap();
    }
}

typedef void (*operation)(unsigned);
static void fw_r_o(unsigned b) { poly_ntt(&out[b]); }
static void fw_r_l(unsigned b) { ntruplus768_officialopt_ntt_caller_lazy(&out[b]); }
static void fw_f_o(unsigned b) { poly_ntt(&out[b]); }
static void fw_f_l(unsigned b) { ntruplus768_officialopt_ntt_caller_lazy(&out[b]); }
static void kg_o(unsigned b) { status_sink = official_ref_keypair(pk_out[b], sk_out[b]); }
static void kg_l(unsigned b) { status_sink = official_lazy_keypair(pk_out[b], sk_out[b]); }
static void en_o(unsigned b) { status_sink = officialopt_ref_enc_derand(ct_out[b], ss_out[b], pk[b], coins[b]); }
static void en_l(unsigned b) { status_sink = officialopt_lazy_enc_derand(ct_out[b], ss_out[b], pk[b], coins[b]); }
static void de_o(unsigned b) { status_sink = official_ref_dec(ss_out[b], ct[b], sk[b]); }
static void de_l(unsigned b) { status_sink = official_lazy_dec(ss_out[b], ct[b], sk[b]); }
static operation ops[REGIONS][2] = {
    {fw_r_o, fw_r_l}, {fw_f_o, fw_f_l}, {kg_o, kg_l},
    {en_o, en_l}, {de_o, de_l}
};

static void reset_forward(unsigned region, unsigned b) {
    if (region == 0) out[b] = r_coeff[b];
    if (region == 1) out[b] = f_coeff[b];
}

static void preflight(void) {
    poly official;
    for (unsigned b = 0; b < BANKS; b++) {
        for (unsigned region = 0; region < 2; region++) {
            reset_forward(region, b);
            ops[region][0](b);
            official = out[b];
            reset_forward(region, b);
            ops[region][1](b);
            for (unsigned i = 0; i < NTRUPLUS_N; i++)
                if (((int)official.coeffs[i] - (int)out[b].coeffs[i]) % NTRUPLUS_Q)
                    __builtin_trap();
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
            for (unsigned slot = 0; slot < 2; slot++) {
                unsigned variant = (block & 1U) ? 1U - slot : slot;
                operation run = ops[region][variant];
                for (unsigned warm = 0; warm < 4; warm++) {
                    reset_forward(region, warm);
                    if (region == 2) seed_rng(5000U + warm);
                    run(warm);
                }
                for (unsigned obs = 0; obs < OBS; obs++) {
                    unsigned bank = obs & (BANKS - 1);
                    reset_forward(region, bank);
                    if (region == 2) seed_rng(5000U + bank);
                    long long start = cpucycles();
                    run(bank);
                    long long cycles = cpucycles() - start;
                    printf("%u,%u,%u,%u,%lld\n", region, variant, block, obs, cycles);
                }
            }
        }
    }
    return 0;
}
