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
int official_ct_dec(unsigned char *, const unsigned char *, const unsigned char *);
void ntruplus768_officialopt_invntt_ct(poly *);

enum { BANKS = 16, OBS = 64, BLOCKS = 8, REGIONS = 3 };
static poly inverse_input[BANKS], inverse_output[BANKS];
static unsigned char pk[BANKS][NTRUPLUS_PUBLICKEYBYTES];
static unsigned char sk[BANKS][NTRUPLUS_SECRETKEYBYTES];
static unsigned char ct[BANKS][NTRUPLUS_CIPHERTEXTBYTES];
static unsigned char ss_out[BANKS][NTRUPLUS_SSBYTES];
static volatile int status_sink;
static uint64_t state = UINT64_C(0x768c720260921);

static uint32_t random_word(void) {
    state ^= state << 13;
    state ^= state >> 7;
    state ^= state << 17;
    return (uint32_t)state;
}

static void seed_rng(unsigned tag) {
    unsigned char entropy[48];
    for (unsigned i = 0; i < sizeof entropy; i++)
        entropy[i] = (unsigned char)(i * 31U + tag * 13U);
    randombytes_init(entropy, NULL, 256);
}

static void fixture(void) {
    for (unsigned b = 0; b < BANKS; b++) {
        poly a, c;
        for (unsigned i = 0; i < NTRUPLUS_N; i++) {
            a.coeffs[i] = (int16_t)(random_word() % NTRUPLUS_Q);
            c.coeffs[i] = (int16_t)(random_word() % NTRUPLUS_Q);
        }
        poly_basemul_scale(&inverse_input[b], &a, &c);
        for (unsigned i = 0; i < NTRUPLUS_N; i++)
            if (inverse_input[b].coeffs[i] < -7644 ||
                inverse_input[b].coeffs[i] > 7644) __builtin_trap();
        seed_rng(2000U + b);
        if (official_ref_keypair(pk[b], sk[b])) __builtin_trap();
        seed_rng(3000U + b);
        unsigned char secret[NTRUPLUS_SSBYTES];
        if (official_ref_enc(ct[b], secret, pk[b])) __builtin_trap();
    }
}

typedef void (*operation)(unsigned);
static void inverse_official(unsigned b) { poly_invntt_scale(&inverse_output[b]); }
static void inverse_ct(unsigned b) { ntruplus768_officialopt_invntt_ct(&inverse_output[b]); }
static void inverse_crep_official(unsigned b) {
    poly_invntt_scale(&inverse_output[b]);
    poly_crepmod3(&inverse_output[b]);
}
static void inverse_crep_ct(unsigned b) {
    ntruplus768_officialopt_invntt_ct(&inverse_output[b]);
    poly_crepmod3(&inverse_output[b]);
}
static void decap_official(unsigned b) {
    status_sink = official_ref_dec(ss_out[b], ct[b], sk[b]);
}
static void decap_ct(unsigned b) {
    status_sink = official_ct_dec(ss_out[b], ct[b], sk[b]);
}
static operation ops[REGIONS][2] = {
    {inverse_official, inverse_ct},
    {inverse_crep_official, inverse_crep_ct},
    {decap_official, decap_ct},
};

static void reset(unsigned region, unsigned b) {
    if (region < 2) inverse_output[b] = inverse_input[b];
    else memset(ss_out[b], 0, sizeof ss_out[b]);
}

static void preflight(void) {
    for (unsigned b = 0; b < BANKS; b++) {
        for (unsigned region = 0; region < REGIONS; region++) {
            poly expected_poly;
            unsigned char expected_ss[NTRUPLUS_SSBYTES];
            int expected_status;
            reset(region, b);
            ops[region][0](b);
            expected_status = status_sink;
            if (region < 2) expected_poly = inverse_output[b];
            else memcpy(expected_ss, ss_out[b], sizeof expected_ss);
            reset(region, b);
            ops[region][1](b);
            if (region == 0) {
                for (unsigned i = 0; i < NTRUPLUS_N; i++)
                    if (((int)expected_poly.coeffs[i] -
                         (int)inverse_output[b].coeffs[i]) % NTRUPLUS_Q)
                        __builtin_trap();
            } else if (region == 1) {
                if (memcmp(&expected_poly, &inverse_output[b], sizeof expected_poly))
                    __builtin_trap();
            } else if (expected_status != status_sink ||
                       memcmp(expected_ss, ss_out[b], sizeof expected_ss)) {
                __builtin_trap();
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
            for (unsigned slot = 0; slot < 2; slot++) {
                unsigned variant = (block & 1U) ? 1U - slot : slot;
                operation run = ops[region][variant];
                for (unsigned warm = 0; warm < 4; warm++) {
                    reset(region, warm);
                    run(warm);
                }
                for (unsigned obs = 0; obs < OBS; obs++) {
                    unsigned bank = obs & (BANKS - 1);
                    reset(region, bank);
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
