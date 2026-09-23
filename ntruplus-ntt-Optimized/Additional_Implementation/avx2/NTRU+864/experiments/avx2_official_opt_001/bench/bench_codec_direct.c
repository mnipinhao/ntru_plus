/*
 * Same-ELF SUPERCOP-derived component/caller diagnostic for the NTRU+864
 * exp002 direct codec.  Derived from bench/bench_codec_fused.c (same
 * cpucycles source, 16 banks, 32 observations per block, 4 warm-ups per
 * slot); 12 blocks so that 3- and 4-variant rotations are balanced.
 * Diagnostic only, not Native SUPERCOP.
 *
 * Regions and variants (variant 0 is always Official):
 *   0 tobytes    0 Official poly_tobytes  1 exp001 fused  2 fused_min (exp001 + 2-op freeze)  3 exp002 direct
 *   1 frombytes  0 Official poly_frombytes  1 exp001 fused  2 exp002 direct
 *   2 keypair    0 Official  1 lazy  2 exp001 (lazy+fused)  3 exp002 (lazy+direct)
 *   3 encap      (derandomised, fixed coins)    same four
 *   4 decap                                     same four
 * Block b runs the variants in the rotated order (b + slot) mod V, so every
 * variant occupies every slot position equally often.
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
DECL(v3)
DECL(v4)
void ntruplus864_officialopt_tobytes_fused(uint8_t *, const poly *);
int ntruplus864_officialopt_frombytes_fused(poly *, const uint8_t *);
void ntruplus864_officialopt_tobytes_fused_min(uint8_t *, const poly *);
void ntruplus864_officialopt_tobytes_direct(uint8_t *, const poly *);
int ntruplus864_officialopt_frombytes_direct(poly *, const uint8_t *);
void ntruplus864_officialopt_ntt_caller_lazy(poly *);

enum { BANKS = 16, OBS = 32, BLOCKS = 12, REGIONS = 5, MAXV = 4 };
static poly src_poly[BANKS], out_poly[BANKS];
static uint8_t pk[BANKS][NTRUPLUS_PUBLICKEYBYTES];
static uint8_t sk[BANKS][NTRUPLUS_SECRETKEYBYTES];
static uint8_t ct[BANKS][NTRUPLUS_CIPHERTEXTBYTES];
static uint8_t coins[BANKS][NTRUPLUS_N / 8];
static uint8_t pk_out[BANKS][NTRUPLUS_PUBLICKEYBYTES];
static uint8_t sk_out[BANKS][NTRUPLUS_SECRETKEYBYTES];
static uint8_t ct_out[BANKS][NTRUPLUS_CIPHERTEXTBYTES];
static uint8_t ss_out[BANKS][NTRUPLUS_SSBYTES];
static uint8_t bytes_out[BANKS][NTRUPLUS_POLYBYTES];
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
        for (unsigned i = 0; i < sizeof sample; i++)
            sample[i] = (uint8_t)(i * 31U + b * 7U);
        poly_cbd1(&src_poly[b], sample);   /* lazy-Forward output: KEM-like tobytes input */
        ntruplus864_officialopt_ntt_caller_lazy(&src_poly[b]);
        for (unsigned i = 0; i < sizeof coins[b]; i++)
            coins[b][i] = (uint8_t)(i * 23U + b);
        uint8_t secret[NTRUPLUS_SSBYTES];
        if (v0_enc_derand(ct[b], secret, pk[b], coins[b])) __builtin_trap();
    }
}

typedef void (*operation)(unsigned);
static void tb_o(unsigned b) { poly_tobytes(bytes_out[b], &src_poly[b]); }
static void tb_f(unsigned b) { ntruplus864_officialopt_tobytes_fused(bytes_out[b], &src_poly[b]); }
static void tb_m(unsigned b) { ntruplus864_officialopt_tobytes_fused_min(bytes_out[b], &src_poly[b]); }
static void tb_d(unsigned b) { ntruplus864_officialopt_tobytes_direct(bytes_out[b], &src_poly[b]); }
static void fb_o(unsigned b) { status_sink = poly_frombytes(&out_poly[b], pk[b]); }
static void fb_f(unsigned b) { status_sink = ntruplus864_officialopt_frombytes_fused(&out_poly[b], pk[b]); }
static void fb_d(unsigned b) { status_sink = ntruplus864_officialopt_frombytes_direct(&out_poly[b], pk[b]); }
#define OPS(v)                                                                                   \
    static void kg_##v(unsigned b) { status_sink = v##_keypair(pk_out[b], sk_out[b]); }         \
    static void en_##v(unsigned b) { status_sink = v##_enc_derand(ct_out[b], ss_out[b], pk[b], coins[b]); } \
    static void de_##v(unsigned b) { status_sink = v##_dec(ss_out[b], ct[b], sk[b]); }
OPS(v0)
OPS(v1)
OPS(v3)
OPS(v4)
static const unsigned nvariants[REGIONS] = {4, 3, 4, 4, 4};
static operation ops[REGIONS][MAXV] = {
    {tb_o, tb_f, tb_m, tb_d}, {fb_o, fb_f, fb_d},
    {kg_v0, kg_v1, kg_v3, kg_v4}, {en_v0, en_v1, en_v3, en_v4}, {de_v0, de_v1, de_v3, de_v4}};

static void preflight(void) {
    for (unsigned b = 0; b < BANKS; b++) {
        uint8_t ref[NTRUPLUS_POLYBYTES];
        poly p;
        tb_o(b); memcpy(ref, bytes_out[b], sizeof ref);
        for (unsigned v = 1; v < nvariants[0]; v++) {
            memset(bytes_out[b], 0, sizeof bytes_out[b]);
            ops[0][v](b); if (memcmp(ref, bytes_out[b], sizeof ref)) __builtin_trap();
        }
        fb_o(b); p = out_poly[b]; int s0 = status_sink;
        for (unsigned v = 1; v < nvariants[1]; v++) {
            memset(&out_poly[b], 0, sizeof out_poly[b]);
            ops[1][v](b); if (s0 != status_sink || memcmp(&p, &out_poly[b], sizeof p)) __builtin_trap();
        }
        uint8_t rpk[NTRUPLUS_PUBLICKEYBYTES], rsk[NTRUPLUS_SECRETKEYBYTES];
        uint8_t rct[NTRUPLUS_CIPHERTEXTBYTES], rss[NTRUPLUS_SSBYTES], rdss[NTRUPLUS_SSBYTES];
        for (unsigned v = 0; v < MAXV; v++) {
            seed_rng(5000U + b); ops[2][v](b);
            if (status_sink) __builtin_trap();
            ops[3][v](b); if (status_sink) __builtin_trap();
            if (v == 0) { memcpy(rpk, pk_out[b], sizeof rpk); memcpy(rsk, sk_out[b], sizeof rsk);
                          memcpy(rct, ct_out[b], sizeof rct); memcpy(rss, ss_out[b], sizeof rss); }
            else if (memcmp(rpk, pk_out[b], sizeof rpk) || memcmp(rsk, sk_out[b], sizeof rsk) ||
                     memcmp(rct, ct_out[b], sizeof rct) || memcmp(rss, ss_out[b], sizeof rss))
                __builtin_trap();
            ops[4][v](b); if (status_sink) __builtin_trap();
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
                    if (region == 2) seed_rng(5000U + warm);
                    run(warm);
                }
                for (unsigned obs = 0; obs < OBS; obs++) {
                    unsigned bank = obs & (BANKS - 1);
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
