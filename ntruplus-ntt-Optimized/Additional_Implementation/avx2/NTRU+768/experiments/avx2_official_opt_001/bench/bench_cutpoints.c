#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "cpucycles.h"
#include "kat/rng.h"
#include "params.h"
#include "poly.h"
#include "symmetric.h"
#include "fips202.h"
#include "util.h"

int official_ref_keypair(unsigned char *, unsigned char *);
int official_ref_dec(unsigned char *, const unsigned char *, const unsigned char *);
int officialopt_ref_enc_derand(uint8_t *, uint8_t *, const uint8_t *, const uint8_t *);

enum { BANKS = 16, OBS = 32, BLOCKS = 8 };
static uint8_t pk[BANKS][NTRUPLUS_PUBLICKEYBYTES];
static uint8_t sk[BANKS][NTRUPLUS_SECRETKEYBYTES];
static uint8_t ct[BANKS][NTRUPLUS_CIPHERTEXTBYTES];
static uint8_t coins[BANKS][NTRUPLUS_N/8];
static uint8_t fcoins[BANKS][NTRUPLUS_SYMBYTES];
static uint8_t gcoins[BANKS][NTRUPLUS_SYMBYTES];
static uint8_t out_pk[NTRUPLUS_PUBLICKEYBYTES], out_sk[NTRUPLUS_SECRETKEYBYTES];
static uint8_t out_ct[NTRUPLUS_CIPHERTEXTBYTES], out_ss[NTRUPLUS_SSBYTES];
static volatile uint8_t sink;
static unsigned retries_f[BANKS], retries_g[BANKS];

static void seed_rng(unsigned tag) {
    uint8_t entropy[48];
    for (unsigned i = 0; i < 48; i++) entropy[i] = (uint8_t)(i*31U+tag*13U);
    randombytes_init(entropy, NULL, 256);
}

static int sample_f(poly *f, const uint8_t seed[NTRUPLUS_SYMBYTES]) {
    uint8_t buf[NTRUPLUS_N/4];
    shake256(buf, sizeof buf, seed, NTRUPLUS_SYMBYTES);
    poly_cbd1(f, buf);
    poly_triple(f);
    f->coeffs[0] += 1;
    return 0;
}

static int sample_g(poly *g, const uint8_t seed[NTRUPLUS_SYMBYTES]) {
    uint8_t buf[NTRUPLUS_N/4];
    shake256(buf, sizeof buf, seed, NTRUPLUS_SYMBYTES);
    poly_cbd1(g, buf);
    poly_triple(g);
    return 0;
}

static int keygen_cut(unsigned b, unsigned cut) {
    poly f, g, finv, ginv, h;
    sample_f(&f, fcoins[b]);
    if (cut == 0) { sink ^= (uint8_t)f.coeffs[0]; return 0; }
    poly_ntt(&f);
    if (cut == 1) { sink ^= (uint8_t)f.coeffs[0]; return 0; }
    if (poly_baseinv(&finv, &f)) return 1;
    if (cut == 2) { sink ^= (uint8_t)finv.coeffs[0]; return 0; }
    sample_g(&g, gcoins[b]);
    if (cut == 3) { sink ^= (uint8_t)g.coeffs[0]; return 0; }
    poly_ntt(&g);
    if (cut == 4) { sink ^= (uint8_t)g.coeffs[0]; return 0; }
    if (poly_baseinv(&ginv, &g)) return 1;
    if (cut == 5) { sink ^= (uint8_t)ginv.coeffs[0]; return 0; }
    poly_basemul(&h, &g, &finv);
    poly_tobytes(out_pk, &h);
    if (cut == 6) { sink ^= out_pk[0]; return 0; }
    poly_basemul(&h, &f, &ginv);
    poly_tobytes(out_sk, &f);
    poly_tobytes(out_sk+NTRUPLUS_POLYBYTES, &h);
    if (cut == 7) { sink ^= out_sk[0]; return 0; }
    hash_f(out_sk+2*NTRUPLUS_POLYBYTES, out_pk);
    if (cut == 8) { sink ^= out_sk[2*NTRUPLUS_POLYBYTES]; return 0; }
    secure_clear(&h, sizeof h);
    secure_clear(&f, sizeof f);
    secure_clear(&g, sizeof g);
    secure_clear(&finv, sizeof finv);
    secure_clear(&ginv, sizeof ginv);
    return 0;
}

static int encap_cut(unsigned b, unsigned cut) {
    uint8_t msg[HASH_H_INBYTES], buf[HASH_H_OUTBYTES];
    poly h, r, m, c;
    if (poly_frombytes(&h, pk[b])) return 1;
    if (cut == 0) { sink ^= (uint8_t)h.coeffs[0]; return 0; }
    memcpy(msg, coins[b], NTRUPLUS_N/8);
    hash_f(msg+NTRUPLUS_N/8, pk[b]);
    hash_h(buf, msg);
    poly_cbd1(&r, buf+NTRUPLUS_SYMBYTES);
    if (cut == 1) { sink ^= (uint8_t)r.coeffs[0]; return 0; }
    poly_ntt(&r);
    if (cut == 2) { sink ^= (uint8_t)r.coeffs[0]; return 0; }
    poly_tobytes(out_ct, &r);
    if (cut == 3) { sink ^= out_ct[0]; return 0; }
    hash_g(out_ct, out_ct);
    if (cut == 4) { sink ^= out_ct[0]; return 0; }
    poly_sotp_encode(&m, msg, out_ct);
    if (cut == 5) { sink ^= (uint8_t)m.coeffs[0]; return 0; }
    poly_ntt(&m);
    if (cut == 6) { sink ^= (uint8_t)m.coeffs[0]; return 0; }
    poly_basemul(&c, &h, &r);
    poly_add(&c, &c, &m);
    if (cut == 7) { sink ^= (uint8_t)c.coeffs[0]; return 0; }
    poly_tobytes(out_ct, &c);
    if (cut == 8) { sink ^= out_ct[0]; return 0; }
    memcpy(out_ss, buf, NTRUPLUS_SSBYTES);
    secure_clear(msg, sizeof msg);
    secure_clear(buf, sizeof buf);
    secure_clear(&r, sizeof r);
    secure_clear(&m, sizeof m);
    return 0;
}

static int decap_cut(unsigned b, unsigned cut) {
    uint8_t msg[HASH_H_INBYTES], buf1[HASH_G_INBYTES];
    uint8_t buf2[HASH_G_INBYTES], buf3[HASH_H_OUTBYTES];
    poly c, f, hinv, m;
    if (poly_frombytes(&c, ct[b]) || poly_frombytes(&f, sk[b]) ||
        poly_frombytes(&hinv, sk[b]+NTRUPLUS_POLYBYTES)) return 1;
    if (cut == 0) { sink ^= (uint8_t)c.coeffs[0]; return 0; }
    poly_basemul_scale(&m, &c, &f);
    if (cut == 1) { sink ^= (uint8_t)m.coeffs[0]; return 0; }
    poly_invntt_scale(&m);
    poly_crepmod3(&m);
    if (cut == 2) { sink ^= (uint8_t)m.coeffs[0]; return 0; }
    f = m;
    poly_ntt(&f);
    poly_sub(&c, &c, &f);
    if (cut == 3) { sink ^= (uint8_t)c.coeffs[0]; return 0; }
    poly_basemul(&f, &c, &hinv);
    if (cut == 4) { sink ^= (uint8_t)f.coeffs[0]; return 0; }
    poly_tobytes(buf1, &f);
    if (cut == 5) { sink ^= buf1[0]; return 0; }
    hash_g(buf2, buf1);
    if (cut == 6) { sink ^= buf2[0]; return 0; }
    int fail = poly_sotp_decode(msg, &m, buf2);
    memcpy(msg+NTRUPLUS_N/8, sk[b]+2*NTRUPLUS_POLYBYTES, HASH_F_OUTBYTES);
    if (cut == 7) { sink ^= msg[0]; return 0; }
    hash_h(buf3, msg);
    if (cut == 8) { sink ^= buf3[0]; return 0; }
    poly_cbd1(&f, buf3+NTRUPLUS_SSBYTES);
    poly_ntt(&f);
    if (cut == 9) { sink ^= (uint8_t)f.coeffs[0]; return 0; }
    poly_tobytes(buf2, &f);
    for (unsigned i = 0; i < NTRUPLUS_POLYBYTES; i++) fail |= buf1[i] != buf2[i];
    for (unsigned i = 0; i < NTRUPLUS_SSBYTES; i++)
        out_ss[i] = buf3[i] & (uint8_t)~(-fail);
    secure_clear(msg, sizeof msg);
    secure_clear(buf1, sizeof buf1);
    secure_clear(buf2, sizeof buf2);
    secure_clear(buf3, sizeof buf3);
    secure_clear(&c, sizeof c);
    secure_clear(&f, sizeof f);
    secure_clear(&hinv, sizeof hinv);
    secure_clear(&m, sizeof m);
    return fail;
}

static void fixture(void) {
    for (unsigned b = 0; b < BANKS; b++) {
        seed_rng(2000U+b);
        if (official_ref_keypair(pk[b], sk[b])) __builtin_trap();
        seed_rng(2000U+b);
        poly f, finv, g, ginv;
        do {
            randombytes(fcoins[b], sizeof fcoins[b]);
            sample_f(&f, fcoins[b]);
            poly_ntt(&f);
            if (!poly_baseinv(&finv, &f)) break;
            retries_f[b]++;
        } while (retries_f[b] < 1000);
        do {
            randombytes(gcoins[b], sizeof gcoins[b]);
            sample_g(&g, gcoins[b]);
            poly_ntt(&g);
            if (!poly_baseinv(&ginv, &g)) break;
            retries_g[b]++;
        } while (retries_g[b] < 1000);
        if (retries_f[b] >= 1000 || retries_g[b] >= 1000 ||
            keygen_cut(b, 9) || memcmp(out_pk, pk[b], sizeof out_pk) ||
            memcmp(out_sk, sk[b], sizeof out_sk)) __builtin_trap();
        for (unsigned i = 0; i < sizeof coins[b]; i++) coins[b][i] = (uint8_t)(i*23U+b);
        uint8_t ss[NTRUPLUS_SSBYTES];
        if (officialopt_ref_enc_derand(ct[b], ss, pk[b], coins[b]) ||
            encap_cut(b, 9) || memcmp(out_ct, ct[b], sizeof out_ct) ||
            memcmp(out_ss, ss, sizeof ss) || decap_cut(b, 10) ||
            memcmp(out_ss, ss, sizeof ss)) __builtin_trap();
    }
    unsigned total_f=0, total_g=0;
    for (unsigned b = 0; b < BANKS; b++) total_f += retries_f[b], total_g += retries_g[b];
    fprintf(stderr, "preflight=pass retry_f=%u retry_g=%u\n", total_f, total_g);
}

int main(void) {
    fixture();
    cpucycles_tracesetup();
    puts("family,cut,block,observation,cycles");
    const unsigned cuts[3] = {10,10,11};
    for (unsigned block = 0; block < BLOCKS; block++) {
        for (unsigned family = 0; family < 3; family++) {
            for (unsigned step = 0; step < cuts[family]; step++) {
                unsigned cut = (block & 1U) ? cuts[family]-1U-step : step;
                for (unsigned warm = 0; warm < 4; warm++) {
                    if (family == 0) keygen_cut(warm, cut);
                    if (family == 1) encap_cut(warm, cut);
                    if (family == 2) decap_cut(warm, cut);
                }
                for (unsigned obs = 0; obs < OBS; obs++) {
                    unsigned bank = obs & (BANKS-1);
                    long long start = cpucycles();
                    if (family == 0) keygen_cut(bank, cut);
                    if (family == 1) encap_cut(bank, cut);
                    if (family == 2) decap_cut(bank, cut);
                    long long cycles = cpucycles()-start;
                    printf("%u,%u,%u,%u,%lld\n",family,cut,block,obs,cycles);
                }
            }
        }
    }
    return 0;
}
