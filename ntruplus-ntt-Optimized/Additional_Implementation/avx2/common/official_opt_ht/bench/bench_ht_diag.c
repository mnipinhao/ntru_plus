/*
 * Same-ELF SUPERCOP-derived component/caller diagnostic for the NTRU+768 HT
 * Forward and keygen R^2 fold.  Derived from
 * common/official_opt_keccak/bench/bench_keccak_diag.c (same cpucycles source,
 * 16 banks, 32 observations per block, 4 warm-ups per slot; 14 blocks so the
 * 2- and 7-variant rotations are balanced).  Diagnostic only, not Native.
 *
 * Regions and variants:
 *   0 forward   keygen-f-domain input, reset outside the timed call:
 *               0 caller-lazy Forward   1 HT Forward
 *   1 basemul   keygen h = g_hat * finv: 0 Official poly_basemul(g_hat, finv)
 *               1 ntruplus768_officialopt_basemul_nor2(g_hat, R*finv)
 *   2 baseinv   0 Official poly_baseinv(f_hat)  1 fold BaseInv(f_hat)
 *   3 invntt    Decap input basemul_scale(c, f_hat), reset outside the timed call:
 *               0 Official poly_invntt_scale  1 HT inverse
 *   4 keypair   0 Official  1 base (lazy+freeze+keccak)  2 candidate  3 ht_only
 *               4 r2fold_only  5 htinv_only  6 ht_r2fold  (KAT DRBG reseeded per bank: seed-matched)
 *   5 encap     (derandomised, fixed coins)  same seven
 *   6 decap                                  same seven
 * Block b runs the variants in the rotated order (b + slot) mod V.
 */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "cpucycles.h"
#include "kat/rng.h"
#include "params.h"
#include "poly.h"

#define DECL(v)                                                                   \
    int v##_keypair(unsigned char *, unsigned char *);                           \
    int v##_enc(unsigned char *, unsigned char *, const unsigned char *);        \
    int v##_dec(unsigned char *, const unsigned char *, const unsigned char *);  \
    int v##_enc_derand(uint8_t *, uint8_t *, const uint8_t *, const uint8_t *);
DECL(v0)
DECL(v1)
DECL(v2)
DECL(v3)
DECL(v4)
DECL(v5)
DECL(v6)
void ntruplus768_officialopt_invntt_ht(poly *);
void ntruplus768_officialopt_ntt_caller_lazy(poly *);
void ntruplus768_officialopt_ntt_ht(poly *);
void ntruplus768_officialopt_basemul_nor2(poly *, const poly *, const poly *);
int ntruplus768_officialopt_baseinv_r2fold(poly *, const poly *);

enum { BANKS = 16, OBS = 32, BLOCKS = 14, REGIONS = 7, MAXV = 7, KP = 4 };
static poly f_in[BANKS], f_hat[BANKS], g_hat[BANKS], finv[BANKS], finv2[BANKS], out[BANKS], inv_in[BANKS];
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
        if (v0_keypair(pk[b], sk[b])) __builtin_trap();
        for (unsigned i = 0; i < sizeof coins[b]; i++)
            coins[b][i] = (uint8_t)(i * 23U + b);
        uint8_t secret[NTRUPLUS_SSBYTES];
        if (v0_enc_derand(ct[b], secret, pk[b], coins[b])) __builtin_trap();
        for (unsigned tries = 0;; tries++) {
            for (unsigned i = 0; i < sizeof sample; i++) sample[i] = (uint8_t)(i * 31U + b * 7U + tries);
            poly_cbd1(&f_in[b], sample);
            poly_triple(&f_in[b]);
            f_in[b].coeffs[0]++;
            f_hat[b] = f_in[b];
            ntruplus768_officialopt_ntt_caller_lazy(&f_hat[b]);
            for (unsigned i = 0; i < sizeof sample; i++) sample[i] = (uint8_t)(i * 17U + b * 5U + tries);
            poly_cbd1(&g_hat[b], sample);
            poly_triple(&g_hat[b]);
            ntruplus768_officialopt_ntt_caller_lazy(&g_hat[b]);
            if (!poly_baseinv(&finv[b], &f_hat[b]) &&
                !ntruplus768_officialopt_baseinv_r2fold(&finv2[b], &f_hat[b])) break;
            if (tries > 8) __builtin_trap();
        }
        poly cpoly;
        uint8_t wire[NTRUPLUS_POLYBYTES];
        memcpy(wire, ct[b], sizeof wire);
        if (poly_frombytes(&cpoly, wire)) __builtin_trap();
        poly_basemul_scale(&inv_in[b], &cpoly, &f_hat[b]);
    }
}

typedef void (*operation)(unsigned);
static void fw_l(unsigned b) { ntruplus768_officialopt_ntt_caller_lazy(&out[b]); }
static void fw_h(unsigned b) { ntruplus768_officialopt_ntt_ht(&out[b]); }
static void bm_o(unsigned b) { poly_basemul(&out[b], &g_hat[b], &finv[b]); }
static void bm_n(unsigned b) { ntruplus768_officialopt_basemul_nor2(&out[b], &g_hat[b], &finv2[b]); }
static void bi_o(unsigned b) { status_sink = poly_baseinv(&out[b], &f_hat[b]); }
static void bi_f(unsigned b) { status_sink = ntruplus768_officialopt_baseinv_r2fold(&out[b], &f_hat[b]); }
static void iv_o(unsigned b) { poly_invntt_scale(&out[b]); }
static void iv_h(unsigned b) { ntruplus768_officialopt_invntt_ht(&out[b]); }
#define OPS(v)                                                                                   \
    static void kg_##v(unsigned b) { status_sink = v##_keypair(pk_out[b], sk_out[b]); }         \
    static void en_##v(unsigned b) { status_sink = v##_enc_derand(ct_out[b], ss_out[b], pk[b], coins[b]); } \
    static void de_##v(unsigned b) { status_sink = v##_dec(ss_out[b], ct[b], sk[b]); }
OPS(v0)
OPS(v1)
OPS(v2)
OPS(v3)
OPS(v4)
OPS(v5)
OPS(v6)
static const unsigned nvariants[REGIONS] = {2, 2, 2, 2, 7, 7, 7};
static operation ops[REGIONS][MAXV] = {
    {fw_l, fw_h}, {bm_o, bm_n}, {bi_o, bi_f}, {iv_o, iv_h},
    {kg_v0, kg_v1, kg_v2, kg_v3, kg_v4, kg_v5, kg_v6},
    {en_v0, en_v1, en_v2, en_v3, en_v4, en_v5, en_v6},
    {de_v0, de_v1, de_v2, de_v3, de_v4, de_v5, de_v6}};

static void reset(unsigned region, unsigned b) {
    if (region == 0) out[b] = f_in[b];
    if (region == 3) out[b] = inv_in[b];
    if (region == KP) seed_rng(5000U + b);
}

static void preflight(void) {
    for (unsigned b = 0; b < BANKS; b++) {
        poly ref;
        uint8_t w0[NTRUPLUS_POLYBYTES], w1[NTRUPLUS_POLYBYTES];
        reset(0, b); fw_l(b); ref = out[b];
        reset(0, b); fw_h(b);
        if (memcmp(&ref, &out[b], sizeof ref)) __builtin_trap();          /* bit-exact */
        bm_o(b); poly_tobytes(w0, &out[b]);
        bm_n(b); poly_tobytes(w1, &out[b]);
        if (memcmp(w0, w1, sizeof w0)) __builtin_trap();
        reset(3, b); iv_o(b); ref = out[b];
        reset(3, b); iv_h(b);
        if (memcmp(&ref, &out[b], sizeof ref)) __builtin_trap();          /* bit-exact */
        uint8_t rpk[NTRUPLUS_PUBLICKEYBYTES], rsk[NTRUPLUS_SECRETKEYBYTES];
        uint8_t rct[NTRUPLUS_CIPHERTEXTBYTES], rss[NTRUPLUS_SSBYTES], rdss[NTRUPLUS_SSBYTES];
        for (unsigned v = 0; v < MAXV; v++) {
            reset(KP, b); ops[KP][v](b); if (status_sink) __builtin_trap();
            ops[KP + 1][v](b); if (status_sink) __builtin_trap();
            if (v == 0) { memcpy(rpk, pk_out[b], sizeof rpk); memcpy(rsk, sk_out[b], sizeof rsk);
                          memcpy(rct, ct_out[b], sizeof rct); memcpy(rss, ss_out[b], sizeof rss); }
            else if (memcmp(rpk, pk_out[b], sizeof rpk) || memcmp(rsk, sk_out[b], sizeof rsk) ||
                     memcmp(rct, ct_out[b], sizeof rct) || memcmp(rss, ss_out[b], sizeof rss))
                __builtin_trap();
            ops[KP + 2][v](b); if (status_sink) __builtin_trap();
            if (v == 0) memcpy(rdss, ss_out[b], sizeof rdss);
            else if (memcmp(rdss, ss_out[b], sizeof rdss)) __builtin_trap();
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
        unsigned nv = nvariants[region];
        for (unsigned block = 0; block < BLOCKS; block++) {
            for (unsigned slot = 0; slot < nv; slot++) {
                unsigned variant = (block + slot) % nv;
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
