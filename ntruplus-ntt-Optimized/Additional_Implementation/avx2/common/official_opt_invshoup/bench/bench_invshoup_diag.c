/*
 * Same-ELF SUPERCOP-derived component/caller diagnostic for the NTRU+768 / 864 / 1152 fused
 * inverse (invntt_scale + crepmod3 in one call) and the Shoup BaseMul, stacked on the current
 * best (parameter from params.h).  Derived from common/official_opt_ht/bench/bench_ht_diag.c
 * (same cpucycles source, 16 banks, 32 observations per block, 4 warm-ups per slot, 20 blocks
 * so the 2- and 5-variant rotations are balanced).  Diagnostic only, not Native.
 *
 * Regions and variants:
 *   0 inverse   Decap input basemul_scale(c, f), reset outside the timed call:
 *               0 current best (864/1152: Official poly_invntt_scale + poly_crepmod3;
 *                 768: HT inverse + poly_crepmod3)   1 fused invntt_crep
 *   1 bm_encap  Encap BaseMul, a = HT Forward(r), b = h:  0 Official poly_basemul(c, h, r)  1 Shoup
 *   2 bm_decap  second Decap BaseMul, a = c - f_hat, b = hinv:  0 Official  1 Shoup
 *   3 keypair   (KAT DRBG reseeded per bank: seed-matched)
 *   4 encap     (derandomised, fixed coins)
 *   5 decap
 *   KEM variants 864/1152: 0 Official  1 base (current best)  2 candidate (Inverse D + Shoup)
 *                          3 invd_only  4 shoup_only
 *                768:      0 Official  1 base (current best)  2 shoup (HT inverse kept)
 *                          3 invcrep_only (fused inverse)  4 invcrep + shoup
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
#define CAT_(a, b, c) a##b##c
#define CAT(a, b, c) CAT_(a, b, c)
#define HT_FN CAT(ntruplus, NTRUPLUS_N, _officialopt_ntt_ht)
#define INV_FN CAT(ntruplus, NTRUPLUS_N, _officialopt_invntt_crep)
#define SHOUP_FN CAT(ntruplus, NTRUPLUS_N, _officialopt_basemul_shoup)
DECL(v0)
DECL(v1)
DECL(v2)
DECL(v3)
DECL(v4)
void HT_FN(poly *);
void INV_FN(poly *);
void SHOUP_FN(poly *, const poly *, const poly *);
#if NTRUPLUS_N == 768
void ntruplus768_officialopt_invntt_ht(poly *);
#define BASE_INV ntruplus768_officialopt_invntt_ht
#else
#define BASE_INV poly_invntt_scale
#endif

enum { BANKS = 16, OBS = 32, BLOCKS = 20, REGIONS = 6, MAXV = 5, KP = 3 };
static poly inv_in[BANKS], r_hat[BANKS], h_can[BANKS], sub_in[BANKS], hinv_can[BANKS], out[BANKS];
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

/* The real Decap / Encap operands of bank b, from its Official keypair and ciphertext. */
static void fixture(void) {
    uint8_t sample[NTRUPLUS_N / 4];
    for (unsigned b = 0; b < BANKS; b++) {
        seed_rng(1000U + b);
        if (v0_keypair(pk[b], sk[b])) __builtin_trap();
        for (unsigned i = 0; i < sizeof coins[b]; i++)
            coins[b][i] = (uint8_t)(i * 23U + b);
        uint8_t secret[NTRUPLUS_SSBYTES];
        if (v0_enc_derand(ct[b], secret, pk[b], coins[b])) __builtin_trap();
        poly c, f, m;
        if (poly_frombytes(&c, ct[b]) || poly_frombytes(&f, sk[b]) ||
            poly_frombytes(&hinv_can[b], sk[b] + NTRUPLUS_POLYBYTES) || poly_frombytes(&h_can[b], pk[b]))
            __builtin_trap();
        poly_basemul_scale(&inv_in[b], &c, &f);
        m = inv_in[b];
        poly_invntt_scale(&m);
        poly_crepmod3(&m);
        HT_FN(&m);
        poly_sub(&sub_in[b], &c, &m);
        for (unsigned i = 0; i < sizeof sample; i++) sample[i] = (uint8_t)(i * 31U + b * 7U);
        poly_cbd1(&r_hat[b], sample);
        HT_FN(&r_hat[b]);
    }
}

typedef void (*operation)(unsigned);
static void iv_o(unsigned b) { BASE_INV(&out[b]); poly_crepmod3(&out[b]); }
static void iv_c(unsigned b) { INV_FN(&out[b]); }
static void be_o(unsigned b) { poly_basemul(&out[b], &h_can[b], &r_hat[b]); }
static void be_s(unsigned b) { SHOUP_FN(&out[b], &r_hat[b], &h_can[b]); }
static void bd_o(unsigned b) { poly_basemul(&out[b], &sub_in[b], &hinv_can[b]); }
static void bd_s(unsigned b) { SHOUP_FN(&out[b], &sub_in[b], &hinv_can[b]); }
#define OPS(v)                                                                                   \
    static void kg_##v(unsigned b) { status_sink = v##_keypair(pk_out[b], sk_out[b]); }         \
    static void en_##v(unsigned b) { status_sink = v##_enc_derand(ct_out[b], ss_out[b], pk[b], coins[b]); } \
    static void de_##v(unsigned b) { status_sink = v##_dec(ss_out[b], ct[b], sk[b]); }
OPS(v0)
OPS(v1)
OPS(v2)
OPS(v3)
OPS(v4)
static const unsigned nvariants[REGIONS] = {2, 2, 2, 5, 5, 5};
static operation ops[REGIONS][MAXV] = {
    {iv_o, iv_c}, {be_o, be_s}, {bd_o, bd_s},
    {kg_v0, kg_v1, kg_v2, kg_v3, kg_v4},
    {en_v0, en_v1, en_v2, en_v3, en_v4},
    {de_v0, de_v1, de_v2, de_v3, de_v4}};

static void reset(unsigned region, unsigned b) {
    if (region == 0) out[b] = inv_in[b];
    if (region == KP) seed_rng(5000U + b);
}

static void preflight(void) {
    for (unsigned b = 0; b < BANKS; b++) {
        poly ref;
        uint8_t w0[NTRUPLUS_POLYBYTES], w1[NTRUPLUS_POLYBYTES];
        reset(0, b); iv_o(b); ref = out[b];
        reset(0, b); iv_c(b);
        if (memcmp(&ref, &out[b], sizeof ref)) __builtin_trap();          /* bit-exact */
        be_o(b); poly_tobytes(w0, &out[b]);
        be_s(b); poly_tobytes(w1, &out[b]);
        if (memcmp(w0, w1, sizeof w0)) __builtin_trap();                  /* equal mod q */
        bd_o(b); poly_tobytes(w0, &out[b]);
        bd_s(b); poly_tobytes(w1, &out[b]);
        if (memcmp(w0, w1, sizeof w0)) __builtin_trap();
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
