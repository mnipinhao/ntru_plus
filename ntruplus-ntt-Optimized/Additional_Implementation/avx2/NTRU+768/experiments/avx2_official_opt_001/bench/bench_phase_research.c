#include <immintrin.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "cpucycles.h"
#include "kat/rng.h"
#include "params.h"
#include "poly.h"

int official_ref_keypair(unsigned char *, unsigned char *);
int officialopt_ref_enc_derand(uint8_t *, uint8_t *, const uint8_t *, const uint8_t *);
void officialopt_diag_baseinv_den(poly *, __m256i [12], const poly *);
int officialopt_diag_baseinv_batch(__m256i [12]);
void officialopt_diag_baseinv_apply(poly *, const __m256i [12]);

enum { BANKS = 16, OBS = 32, BLOCKS = 8, REGIONS = 13 };
static poly base_input[BANKS], base_den_out[BANKS], base_expected[BANKS];
static poly c_dec[BANKS], f_dec[BANKS], hinv_dec[BANKS];
static poly m_core[BANKS], m_inverse[BANKS], m_expected[BANKS];
static poly work[BANKS], c_work[BANKS], f_work[BANKS], hinv_work[BANKS];
static __m256i den_raw[BANKS][12], den_inv[BANKS][12], den_work[BANKS][12];
static uint8_t ct[BANKS][NTRUPLUS_CIPHERTEXTBYTES];
static uint8_t sk[BANKS][NTRUPLUS_SECRETKEYBYTES];
static volatile int status_sink;

static void seed_rng(unsigned tag) {
    uint8_t entropy[48];
    for (unsigned i = 0; i < sizeof entropy; i++)
        entropy[i] = (uint8_t)(i * 31U + tag * 13U);
    randombytes_init(entropy, NULL, 256);
}

static void fixture(void) {
    for (unsigned b = 0; b < BANKS; b++) {
        uint8_t pk[NTRUPLUS_PUBLICKEYBYTES], ss[NTRUPLUS_SSBYTES];
        uint8_t coins[NTRUPLUS_N / 8], sample[NTRUPLUS_N / 4];
        seed_rng(500U + b);
        if (official_ref_keypair(pk, sk[b])) __builtin_trap();
        for (unsigned i = 0; i < sizeof coins; i++)
            coins[i] = (uint8_t)(i * 23U + b);
        if (officialopt_ref_enc_derand(ct[b], ss, pk, coins)) __builtin_trap();
        if (poly_frombytes(&c_dec[b], ct[b]) ||
            poly_frombytes(&f_dec[b], sk[b]) ||
            poly_frombytes(&hinv_dec[b], sk[b] + NTRUPLUS_POLYBYTES))
            __builtin_trap();
        poly_basemul_scale(&m_core[b], &c_dec[b], &f_dec[b]);
        m_inverse[b] = m_core[b];
        poly_invntt_scale(&m_inverse[b]);
        m_expected[b] = m_inverse[b];
        poly_crepmod3(&m_expected[b]);

        int valid = 0;
        for (unsigned attempt = 0; attempt < 1000 && !valid; attempt++) {
            for (unsigned i = 0; i < sizeof sample; i++)
                sample[i] = (uint8_t)(i * 19U + b * 11U + attempt * 7U);
            poly_cbd1(&base_input[b], sample);
            poly_triple(&base_input[b]);
            base_input[b].coeffs[0] += 1;
            poly_ntt(&base_input[b]);
            valid = !poly_baseinv(&base_expected[b], &base_input[b]);
        }
        if (!valid) __builtin_trap();
        officialopt_diag_baseinv_den(&base_den_out[b], den_raw[b], &base_input[b]);
        memcpy(den_inv[b], den_raw[b], sizeof den_inv[b]);
        if (officialopt_diag_baseinv_batch(den_inv[b])) __builtin_trap();
        work[b] = base_den_out[b];
        officialopt_diag_baseinv_apply(&work[b], den_inv[b]);
        if (memcmp(&work[b], &base_expected[b], sizeof(poly))) __builtin_trap();
    }
    fputs("preflight=pass; all BaseInv phase compositions raw-exact\n", stderr);
}

typedef void (*operation)(unsigned);
typedef void (*reset_fn)(unsigned);
static void no_reset(unsigned b) { (void)b; }
static void reset_den(unsigned b) { memcpy(den_work[b], den_raw[b], sizeof den_raw[b]); }
static void reset_apply(unsigned b) { work[b] = base_den_out[b]; }
static void reset_inverse(unsigned b) { work[b] = m_core[b]; }
static void reset_crep(unsigned b) { work[b] = m_inverse[b]; }

static void run_den(unsigned b) {
    officialopt_diag_baseinv_den(&work[b], den_work[b], &base_input[b]);
}
static void run_batch(unsigned b) { status_sink = officialopt_diag_baseinv_batch(den_work[b]); }
static void run_apply(unsigned b) { officialopt_diag_baseinv_apply(&work[b], den_inv[b]); }
static void run_base_full(unsigned b) { status_sink = poly_baseinv(&work[b], &base_input[b]); }
static void run_decode(unsigned b) {
    status_sink = poly_frombytes(&c_work[b], ct[b]);
    status_sink |= poly_frombytes(&f_work[b], sk[b]);
    status_sink |= poly_frombytes(&hinv_work[b], sk[b] + NTRUPLUS_POLYBYTES);
}
static void run_decode_cf(unsigned b) {
    status_sink = poly_frombytes(&c_work[b], ct[b]);
    status_sink |= poly_frombytes(&f_work[b], sk[b]);
}
static void run_decode_hinv(unsigned b) {
    status_sink = poly_frombytes(&hinv_work[b], sk[b] + NTRUPLUS_POLYBYTES);
}
static void run_scale(unsigned b) { poly_basemul_scale(&work[b], &c_dec[b], &f_dec[b]); }
static void run_inverse(unsigned b) { poly_invntt_scale(&work[b]); }
static void run_crep(unsigned b) { poly_crepmod3(&work[b]); }
static void run_scale_inverse(unsigned b) {
    run_scale(b);
    run_inverse(b);
}
static void run_scale_inverse_crep(unsigned b) {
    run_scale_inverse(b);
    run_crep(b);
}
static void run_ingress_full(unsigned b) {
    run_decode(b);
    poly_basemul_scale(&work[b], &c_work[b], &f_work[b]);
    run_inverse(b);
    run_crep(b);
}

static operation operations[REGIONS] = {
    run_den, run_batch, run_apply, run_base_full, run_decode,
    run_scale, run_inverse, run_crep, run_scale_inverse,
    run_scale_inverse_crep, run_ingress_full, run_decode_cf,
    run_decode_hinv
};
static reset_fn resets[REGIONS] = {
    no_reset, reset_den, reset_apply, no_reset, no_reset,
    no_reset, reset_inverse, reset_crep, no_reset, no_reset, no_reset,
    no_reset, no_reset
};

int main(void) {
    fixture();
    for (unsigned b = 0; b < BANKS; b++) {
        run_scale_inverse_crep(b);
        if (memcmp(&work[b], &m_expected[b], sizeof(poly))) __builtin_trap();
        run_ingress_full(b);
        if (status_sink || memcmp(&work[b], &m_expected[b], sizeof(poly)))
            __builtin_trap();
    }
    cpucycles_tracesetup();
    fprintf(stderr, "cpucycles=%s persecond=%lld\n",
            cpucycles_implementation(), cpucycles_persecond());
    puts("region,block,observation,cycles");
    for (unsigned block = 0; block < BLOCKS; block++) {
        for (unsigned slot = 0; slot < REGIONS; slot++) {
            unsigned region = (block & 1U) ? REGIONS - 1U - slot : slot;
            operation run = operations[region];
            reset_fn reset = resets[region];
            for (unsigned warm = 0; warm < 4; warm++) {
                reset(warm);
                run(warm);
            }
            for (unsigned obs = 0; obs < OBS; obs++) {
                unsigned bank = obs & (BANKS - 1);
                reset(bank); /* destructive phase reset is outside timing */
                long long start = cpucycles();
                run(bank);
                long long cycles = cpucycles() - start;
                printf("%u,%u,%u,%lld\n", region, block, obs, cycles);
            }
        }
    }
    return 0;
}
