/*
 * Same-ELF SUPERCOP-derived component/caller diagnostic for the
 * mlkem-native x1 Keccak backend of Official NTRU+ AVX2 (768/864/1152).
 * Derived from common/official_opt_lazy/bench/bench_freeze2op.c (same
 * cpucycles source, 16 banks, 32 observations per block, 4 warm-ups per
 * slot, 12 blocks so that 3- and 4-variant rotations are balanced).
 * Diagnostic only, not Native.
 *
 * Regions and variants (variant 0 is always Official):
 *   0 permute  x1 Keccak-f[1600] on an evolving per-bank state:
 *              0 Official KeccakP1600_Permute_24rounds (AVX2 asm)
 *              1 mlkem-native C, -O3 copy   2 mlkem-native C, -O2 copy
 *   1 hash_f   (0x00 || POLYBYTES) -> 32         same three variants
 *   2 hash_g   (0x01 || POLYBYTES) -> N/4        (Official symmetric.c wrapper
 *   3 hash_h   (0x02 || N/8+32)    -> 32+N/4      on each backend)
 *   4 keypair  0 Official  1 base candidate  2 base + keccak (candidate)  3 keccak only
 *   5 encap    (derandomised, fixed coins)                same four
 *   6 decap                                               same four
 * Keypair observations reseed the KAT DRBG per bank, so every variant sees
 * the same coins and the same f/g retry composition (seed-matched).
 * Block b runs the variants in the rotated order (b + slot) mod V.
 */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "cpucycles.h"
#include "kat/rng.h"
#include "params.h"

#define DECL(v)                                                                   \
    int v##_keypair(unsigned char *, unsigned char *);                           \
    int v##_enc(unsigned char *, unsigned char *, const unsigned char *);        \
    int v##_dec(unsigned char *, const unsigned char *, const unsigned char *);  \
    int v##_enc_derand(uint8_t *, uint8_t *, const uint8_t *, const uint8_t *);
DECL(v0)
DECL(v1)
DECL(v2)
DECL(v3)

void KeccakP1600_Initialize(void *);
void KeccakP1600_AddBytes(void *, const unsigned char *, unsigned, unsigned);
void KeccakP1600_ExtractBytes(const void *, unsigned char *, unsigned, unsigned);
void KeccakP1600_Permute_24rounds(void *);
void ntruplus_mlkfips202_keccakf1600_permute(uint64_t *);
void ntruplus_mlkfips202_keccakf1600_xor_bytes(uint64_t *, const unsigned char *, unsigned, unsigned);
void ntruplus_mlkfips202_keccakf1600_extract_bytes(uint64_t *, unsigned char *, unsigned, unsigned);
void ntruplus_mlkfips202o2_keccakf1600_permute(uint64_t *);
void hash_f(uint8_t *, const uint8_t *);
void hash_g(uint8_t *, const uint8_t *);
void hash_h(uint8_t *, const uint8_t *);
#define CAT3_(a, b, c) a##b##c
#define CAT3(a, b, c) CAT3_(a, b, c)
#define CAND(s) CAT3(ntruplus, NTRUPLUS_N, _keccak_##s)
#define CANDO2(s) CAT3(ntruplus, NTRUPLUS_N, _keccako2_##s)
void CAND(hash_f)(uint8_t *, const uint8_t *);
void CAND(hash_g)(uint8_t *, const uint8_t *);
void CAND(hash_h)(uint8_t *, const uint8_t *);
void CANDO2(hash_f)(uint8_t *, const uint8_t *);
void CANDO2(hash_g)(uint8_t *, const uint8_t *);
void CANDO2(hash_h)(uint8_t *, const uint8_t *);

#define HH_OUT (NTRUPLUS_SSBYTES + NTRUPLUS_N / 4)
enum { BANKS = 16, OBS = 32, BLOCKS = 12, REGIONS = 7, MAXV = 4 };
static uint8_t pk[BANKS][NTRUPLUS_PUBLICKEYBYTES];
static uint8_t sk[BANKS][NTRUPLUS_SECRETKEYBYTES];
static uint8_t ct[BANKS][NTRUPLUS_CIPHERTEXTBYTES];
static uint8_t coins[BANKS][NTRUPLUS_N / 8];
static uint8_t pk_out[BANKS][NTRUPLUS_PUBLICKEYBYTES];
static uint8_t sk_out[BANKS][NTRUPLUS_SECRETKEYBYTES];
static uint8_t ct_out[BANKS][NTRUPLUS_CIPHERTEXTBYTES];
static uint8_t ss_out[BANKS][NTRUPLUS_SSBYTES];
static uint8_t msg[BANKS][NTRUPLUS_POLYBYTES];
static uint8_t hout[BANKS][HH_OUT];
static _Alignas(32) uint64_t st_off[BANKS][26];
static _Alignas(32) uint64_t st_o3[BANKS][25];
static _Alignas(32) uint64_t st_o2[BANKS][25];
static volatile int status_sink;

static void seed_rng(unsigned tag) {
    uint8_t entropy[48];
    for (unsigned i = 0; i < sizeof entropy; i++)
        entropy[i] = (uint8_t)(i * 31U + tag * 13U);
    randombytes_init(entropy, NULL, 256);
}

static void fixture(void) {
    uint32_t x = UINT32_C(0x76820269);
    for (unsigned b = 0; b < BANKS; b++) {
        seed_rng(1000U + b);
        if (v0_keypair(pk[b], sk[b])) __builtin_trap();
        for (unsigned i = 0; i < sizeof coins[b]; i++)
            coins[b][i] = (uint8_t)(i * 23U + b);
        uint8_t secret[NTRUPLUS_SSBYTES];
        if (v0_enc_derand(ct[b], secret, pk[b], coins[b])) __builtin_trap();
        uint8_t sem[200];
        for (unsigned i = 0; i < sizeof msg[b]; i++) {
            x = x * UINT32_C(1664525) + UINT32_C(1013904223);
            msg[b][i] = (uint8_t)(x >> 24);
        }
        for (unsigned i = 0; i < sizeof sem; i++) {
            x = x * UINT32_C(1664525) + UINT32_C(1013904223);
            sem[i] = (uint8_t)(x >> 24);
        }
        KeccakP1600_Initialize(st_off[b]);
        KeccakP1600_AddBytes(st_off[b], sem, 0, 200);
        memset(st_o3[b], 0, sizeof st_o3[b]);
        ntruplus_mlkfips202_keccakf1600_xor_bytes(st_o3[b], sem, 0, 200);
        memcpy(st_o2[b], st_o3[b], sizeof st_o2[b]);
    }
}

typedef void (*operation)(unsigned);
static void pm_o(unsigned b) { KeccakP1600_Permute_24rounds(st_off[b]); }
static void pm_3(unsigned b) { ntruplus_mlkfips202_keccakf1600_permute(st_o3[b]); }
static void pm_2(unsigned b) { ntruplus_mlkfips202o2_keccakf1600_permute(st_o2[b]); }
#define HASH_OPS(x)                                                              \
    static void x##_o(unsigned b) { hash_##x(hout[b], msg[b]); }                \
    static void x##_3(unsigned b) { CAND(hash_##x)(hout[b], msg[b]); }          \
    static void x##_2(unsigned b) { CANDO2(hash_##x)(hout[b], msg[b]); }
HASH_OPS(f)
HASH_OPS(g)
HASH_OPS(h)
#define OPS(v)                                                                                   \
    static void kg_##v(unsigned b) { status_sink = v##_keypair(pk_out[b], sk_out[b]); }         \
    static void en_##v(unsigned b) { status_sink = v##_enc_derand(ct_out[b], ss_out[b], pk[b], coins[b]); } \
    static void de_##v(unsigned b) { status_sink = v##_dec(ss_out[b], ct[b], sk[b]); }
OPS(v0)
OPS(v1)
OPS(v2)
OPS(v3)
static const unsigned nvariants[REGIONS] = {3, 3, 3, 3, 4, 4, 4};
static operation ops[REGIONS][MAXV] = {
    {pm_o, pm_3, pm_2}, {f_o, f_3, f_2}, {g_o, g_3, g_2}, {h_o, h_3, h_2},
    {kg_v0, kg_v1, kg_v2, kg_v3}, {en_v0, en_v1, en_v2, en_v3}, {de_v0, de_v1, de_v2, de_v3}};

static void preflight(void) {
    for (unsigned b = 0; b < BANKS; b++) {
        uint8_t a[200], c[200], d[200];
        pm_o(b); pm_3(b); pm_2(b);
        KeccakP1600_ExtractBytes(st_off[b], a, 0, 200);
        ntruplus_mlkfips202_keccakf1600_extract_bytes(st_o3[b], c, 0, 200);
        ntruplus_mlkfips202_keccakf1600_extract_bytes(st_o2[b], d, 0, 200);
        if (memcmp(a, c, 200) || memcmp(a, d, 200)) __builtin_trap();
        for (unsigned r = 1; r < 4; r++) {
            uint8_t ref[HH_OUT];
            memset(hout[b], 0, sizeof hout[b]);
            ops[r][0](b); memcpy(ref, hout[b], sizeof ref);
            for (unsigned v = 1; v < 3; v++) {
                memset(hout[b], 0, sizeof hout[b]);
                ops[r][v](b);
                if (memcmp(ref, hout[b], sizeof ref)) __builtin_trap();
            }
        }
        uint8_t rpk[NTRUPLUS_PUBLICKEYBYTES], rsk[NTRUPLUS_SECRETKEYBYTES];
        uint8_t rct[NTRUPLUS_CIPHERTEXTBYTES], rss[NTRUPLUS_SSBYTES], rdss[NTRUPLUS_SSBYTES];
        for (unsigned v = 0; v < MAXV; v++) {
            seed_rng(5000U + b); ops[4][v](b);
            if (status_sink) __builtin_trap();
            ops[5][v](b); if (status_sink) __builtin_trap();
            if (v == 0) { memcpy(rpk, pk_out[b], sizeof rpk); memcpy(rsk, sk_out[b], sizeof rsk);
                          memcpy(rct, ct_out[b], sizeof rct); memcpy(rss, ss_out[b], sizeof rss); }
            else if (memcmp(rpk, pk_out[b], sizeof rpk) || memcmp(rsk, sk_out[b], sizeof rsk) ||
                     memcmp(rct, ct_out[b], sizeof rct) || memcmp(rss, ss_out[b], sizeof rss))
                __builtin_trap();
            ops[6][v](b); if (status_sink) __builtin_trap();
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
                    if (region == 4) seed_rng(5000U + warm);
                    run(warm);
                }
                for (unsigned obs = 0; obs < OBS; obs++) {
                    unsigned bank = obs & (BANKS - 1);
                    if (region == 4) seed_rng(5000U + bank);
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
