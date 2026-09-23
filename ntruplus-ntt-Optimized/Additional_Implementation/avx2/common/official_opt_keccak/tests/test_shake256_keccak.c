/*
 * SHAKE256 / Keccak-f[1600] differential: Official NTRU+ AVX2 (XKCP /
 * CRYPTOGAMS KeccakP-1600-AVX2.s + fips202.c) versus the vendored
 * mlkem-native x1 C Keccak (third_party/mlkem-native-fips202-b3ba7b32) and
 * the namespaced hash wrappers of src/symmetric_keccak.c, in one ELF.
 * Parameterised only through the linked params.h (NTRUPLUS_N etc.).
 *
 *   1. x1 permutation: semantic 200-byte states, 3 chained permutations,
 *      random + all-zero (known first lane) states.
 *   2. SHAKE256 grid: every inlen 0..700 x a rate-boundary outlen set; every
 *      outlen 0..600 for boundary inlens; inlen k*136 + {-2..+2} up to 1770;
 *      random in/out misalignment 0..31, output canaries both sides, input
 *      immutability.
 *   3. NTRU+ call shapes: 32 -> N/4 (keypair genf/geng), 1+POLYBYTES -> 32
 *      (hash_f), 1+POLYBYTES -> N/4 (hash_g), 1+N/8+32 -> 32+N/4 (hash_h) at
 *      the SHAKE level, and Official hash_f/g/h vs the candidate wrappers
 *      (including kem.c's in-place hash_g(ct, ct)).
 *   4. NIST CAVP SHAKE256 subset (tests/vectors/shake256_cavp_subset.txt,
 *      path in argv[1]) through both implementations.
 * The candidate adapter uses only the one-shot mlk_shake256 (no incremental
 * absorb/squeeze path exists in it), so no incremental API is exercised.
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "params.h"

/* Official (SUPERCOP 20260831 fips202.c / KeccakP-1600-AVX2.s / symmetric.c) */
void fips202avx_shake256(uint8_t *, size_t, const uint8_t *, size_t);
void KeccakP1600_Initialize(void *);
void KeccakP1600_AddBytes(void *, const unsigned char *, unsigned, unsigned);
void KeccakP1600_ExtractBytes(const void *, unsigned char *, unsigned, unsigned);
void KeccakP1600_Permute_24rounds(void *);
void hash_f(uint8_t *, const uint8_t *);
void hash_g(uint8_t *, const uint8_t *);
void hash_h(uint8_t *, const uint8_t *);

/* Candidate (mlkem-native, MLK_CONFIG_NAMESPACE_PREFIX ntruplus_mlkfips202) */
void ntruplus_mlkfips202_shake256(uint8_t *, size_t, const uint8_t *, size_t);
void ntruplus_mlkfips202_keccakf1600_permute(uint64_t *);
void ntruplus_mlkfips202_keccakf1600_xor_bytes(uint64_t *, const unsigned char *, unsigned, unsigned);
void ntruplus_mlkfips202_keccakf1600_extract_bytes(uint64_t *, unsigned char *, unsigned, unsigned);
#define CAT3_(a, b, c) a##b##c
#define CAT3(a, b, c) CAT3_(a, b, c)
#define CAND(s) CAT3(ntruplus, NTRUPLUS_N, _keccak_##s)
void CAND(hash_f)(uint8_t *, const uint8_t *);
void CAND(hash_g)(uint8_t *, const uint8_t *);
void CAND(hash_h)(uint8_t *, const uint8_t *);

#define RATE 136
#define POLY NTRUPLUS_POLYBYTES
#define HF_IN (POLY)
#define HF_OUT 32
#define HG_IN (POLY)
#define HG_OUT (NTRUPLUS_N / 4)
#define HH_IN (NTRUPLUS_N / 8 + NTRUPLUS_SYMBYTES)
#define HH_OUT (NTRUPLUS_SSBYTES + NTRUPLUS_N / 4)
#define MAX_IN 6000
#define MAX_OUT 1200
#define PAD 64

static uint64_t rng = 0x9e3779b97f4a7c15ULL;
static uint64_t next64(void) {
    rng ^= rng >> 12; rng ^= rng << 25; rng ^= rng >> 27;
    return rng * 0x2545f4914f6cdd1dULL;
}
static void fill(uint8_t *p, size_t n) { for (size_t i = 0; i < n; i++) p[i] = (uint8_t)(next64() >> 56); }

static unsigned long long cases, bytes_compared;

static _Alignas(64) uint8_t inbuf[MAX_IN + PAD], inref[MAX_IN + PAD];
static _Alignas(64) uint8_t out_o[MAX_OUT + 2 * PAD], out_c[MAX_OUT + 2 * PAD];

static int check(size_t inlen, size_t outlen) {
    unsigned ioff = (unsigned)(next64() & 31), ooff = (unsigned)(next64() & 31);
    uint8_t *in = inbuf + ioff;
    fill(in, inlen);
    memcpy(inref, in, inlen);
    memset(out_o, 0xa5, sizeof out_o);
    memset(out_c, 0x5a, sizeof out_c);
    fips202avx_shake256(out_o + PAD / 2 + ooff, outlen, in, inlen);
    ntruplus_mlkfips202_shake256(out_c + PAD / 2 + ooff, outlen, in, inlen);
    if (memcmp(out_o + PAD / 2 + ooff, out_c + PAD / 2 + ooff, outlen)) {
        fprintf(stderr, "SHAKE256 mismatch inlen=%zu outlen=%zu\n", inlen, outlen);
        return 1;
    }
    for (size_t i = 0; i < sizeof out_c; i++) {
        int inside = i >= PAD / 2 + ooff && i < PAD / 2 + ooff + outlen;
        if (!inside && (out_c[i] != 0x5a || out_o[i] != 0xa5)) {
            fprintf(stderr, "SHAKE256 wrote outside output inlen=%zu outlen=%zu at %zu\n", inlen, outlen, i);
            return 1;
        }
    }
    if (memcmp(in, inref, inlen)) {
        fprintf(stderr, "SHAKE256 modified input inlen=%zu\n", inlen);
        return 1;
    }
    cases++;
    bytes_compared += outlen;
    return 0;
}

static int test_permutation(void) {
    _Alignas(32) uint64_t so[26], sc[25];
    uint8_t a[200], b[200];
    /* Keccak-f[1600] of the all-zero state: first lane F1258F7940E1DDE7. */
    memset(sc, 0, sizeof sc);
    ntruplus_mlkfips202_keccakf1600_permute(sc);
    KeccakP1600_Initialize(so);
    KeccakP1600_Permute_24rounds(so);
    KeccakP1600_ExtractBytes(so, a, 0, 200);
    ntruplus_mlkfips202_keccakf1600_extract_bytes(sc, b, 0, 200);
    if (sc[0] != 0xF1258F7940E1DDE7ULL || memcmp(a, b, 200)) {
        fputs("zero-state permutation mismatch\n", stderr);
        return 1;
    }
    for (unsigned t = 0; t < 4000; t++) {
        uint8_t st[200];
        fill(st, sizeof st);
        KeccakP1600_Initialize(so);
        KeccakP1600_AddBytes(so, st, 0, 200);
        memset(sc, 0, sizeof sc);
        ntruplus_mlkfips202_keccakf1600_xor_bytes(sc, st, 0, 200);
        for (unsigned r = 0; r < 3; r++) {
            KeccakP1600_Permute_24rounds(so);
            ntruplus_mlkfips202_keccakf1600_permute(sc);
            KeccakP1600_ExtractBytes(so, a, 0, 200);
            ntruplus_mlkfips202_keccakf1600_extract_bytes(sc, b, 0, 200);
            if (memcmp(a, b, 200)) {
                fprintf(stderr, "permutation mismatch trial=%u round=%u\n", t, r);
                return 1;
            }
        }
    }
    puts("x1 Keccak-f[1600]: 12001 permutations equal (zero-state KAT + 4000 random states x 3)");
    return 0;
}

static int test_grid(void) {
    static const size_t outs[] = {0, 1, 2, 7, 8, 31, 32, 33, 64, 135, 136, 137, 191, 192, 193,
                                  215, 216, 217, 223, 224, 225, 247, 248, 249, 271, 272, 273,
                                  287, 288, 289, 319, 320, 321, 407, 408, 409, 543, 544, 545, 599, 600};
    static const size_t ins[] = {0, 1, 32, 129, 135, 136, 137, 141, 177, 271, 272, 273, 407, 408,
                                 409, 699, 700, 1153, 1297, 1729};
    unsigned long long before = cases;
    for (size_t inlen = 0; inlen <= 700; inlen++)
        for (size_t o = 0; o < sizeof outs / sizeof outs[0]; o++)
            if (check(inlen, outs[o])) return 1;
    for (size_t i = 0; i < sizeof ins / sizeof ins[0]; i++)
        for (size_t outlen = 0; outlen <= 600; outlen++)
            if (check(ins[i], outlen)) return 1;
    for (size_t k = 1; k * RATE + 2 <= 1770; k++)
        for (size_t d = 0; d < 5; d++)
            for (size_t o = 0; o < sizeof outs / sizeof outs[0]; o++)
                if (check(k * RATE + d - 2, outs[o])) return 1;
    for (unsigned t = 0; t < 200; t++)
        if (check((size_t)(next64() % MAX_IN), (size_t)(next64() % MAX_OUT))) return 1;
    printf("SHAKE256 grid: %llu cases equal (inlen 0..700 x %zu outlens, outlen 0..600 x %zu inlens, "
           "k*136+-2 up to 1770, 200 random up to %d/%d bytes; misaligned, canaries, input unchanged)\n",
           cases - before, sizeof outs / sizeof outs[0], sizeof ins / sizeof ins[0], MAX_IN, MAX_OUT);
    return 0;
}

static int test_shapes(void) {
    static const size_t shape[][2] = {{32, HG_OUT}, {1 + HF_IN, HF_OUT}, {1 + HG_IN, HG_OUT}, {1 + HH_IN, HH_OUT}};
    unsigned long long before = cases;
    for (unsigned s = 0; s < 4; s++)
        for (unsigned t = 0; t < 3000; t++)
            if (check(shape[s][0], shape[s][1])) return 1;
    uint8_t msg[POLY + 64], o1[POLY + 64], o2[POLY + 64], b1[POLY], b2[POLY];
    for (unsigned t = 0; t < 3000; t++) {
        fill(msg, sizeof msg);
        memset(o1, 0xa5, sizeof o1); memset(o2, 0xa5, sizeof o2);
        hash_f(o1, msg); CAND(hash_f)(o2, msg);
        if (memcmp(o1, o2, sizeof o1)) { fprintf(stderr, "hash_f mismatch t=%u\n", t); return 1; }
        memset(o1, 0xa5, sizeof o1); memset(o2, 0xa5, sizeof o2);
        hash_g(o1, msg); CAND(hash_g)(o2, msg);
        if (memcmp(o1, o2, sizeof o1)) { fprintf(stderr, "hash_g mismatch t=%u\n", t); return 1; }
        memset(o1, 0xa5, sizeof o1); memset(o2, 0xa5, sizeof o2);
        hash_h(o1, msg); CAND(hash_h)(o2, msg);
        if (memcmp(o1, o2, sizeof o1)) { fprintf(stderr, "hash_h mismatch t=%u\n", t); return 1; }
        /* kem.c crypto_kem_enc_derand: hash_g(ct, ct) in place. */
        memcpy(b1, msg, POLY); memcpy(b2, msg, POLY);
        hash_g(b1, b1); CAND(hash_g)(b2, b2);
        if (memcmp(b1, b2, POLY)) { fprintf(stderr, "in-place hash_g mismatch t=%u\n", t); return 1; }
        /* Domain separation: the wrapper equals SHAKE256(prefix || msg). */
        uint8_t data[1 + POLY], ref[HH_OUT];
        data[0] = 0x01; memcpy(data + 1, msg, POLY);
        ntruplus_mlkfips202_shake256(ref, HG_OUT, data, 1 + HG_IN);
        CAND(hash_g)(o2, msg);
        if (memcmp(ref, o2, HG_OUT)) { fprintf(stderr, "hash_g domain byte mismatch\n"); return 1; }
        data[0] = 0x00; ntruplus_mlkfips202_shake256(ref, HF_OUT, data, 1 + HF_IN);
        CAND(hash_f)(o2, msg);
        if (memcmp(ref, o2, HF_OUT)) { fprintf(stderr, "hash_f domain byte mismatch\n"); return 1; }
        data[0] = 0x02; ntruplus_mlkfips202_shake256(ref, HH_OUT, data, 1 + HH_IN);
        CAND(hash_h)(o2, msg);
        if (memcmp(ref, o2, HH_OUT)) { fprintf(stderr, "hash_h domain byte mismatch\n"); return 1; }
        cases += 7;
    }
    printf("NTRU+%d call shapes: %llu cases equal (SHAKE %d->%d, %d->%d, %d->%d, %d->%d x 3000; "
           "hash_f/g/h + in-place hash_g + domain bytes 0x00/0x01/0x02 x 3000; untouched tails)\n",
           NTRUPLUS_N, cases - before, 32, HG_OUT, 1 + HF_IN, HF_OUT, 1 + HG_IN, HG_OUT, 1 + HH_IN, HH_OUT);
    return 0;
}

static int hexval(int c) { return c <= '9' ? c - '0' : (c | 32) - 'a' + 10; }

static int test_vectors(const char *path) {
    FILE *f = fopen(path, "r");
    if (!f) { perror(path); return 1; }
    static char line[16384];
    static uint8_t msg[4096], exp[512], got[512];
    unsigned n = 0;
    while (fgets(line, sizeof line, f)) {
        if (line[0] == '#' || line[0] == '\n') continue;
        size_t inlen, outlen;
        char *p = line, *q;
        inlen = strtoul(p, &q, 10); p = q;
        outlen = strtoul(p, &q, 10); p = q + 1;
        if (inlen > sizeof msg || outlen > sizeof exp) { fclose(f); return 1; }
        for (size_t i = 0; i < inlen; i++, p += 2) msg[i] = (uint8_t)(hexval(p[0]) << 4 | hexval(p[1]));
        p += inlen ? 1 : 2;
        for (size_t i = 0; i < outlen; i++, p += 2) exp[i] = (uint8_t)(hexval(p[0]) << 4 | hexval(p[1]));
        fips202avx_shake256(got, outlen, msg, inlen);
        if (memcmp(got, exp, outlen)) { fprintf(stderr, "Official fails CAVP vector %u\n", n); fclose(f); return 1; }
        ntruplus_mlkfips202_shake256(got, outlen, msg, inlen);
        if (memcmp(got, exp, outlen)) { fprintf(stderr, "candidate fails CAVP vector %u\n", n); fclose(f); return 1; }
        n++;
    }
    fclose(f);
    if (n != 76) { fprintf(stderr, "expected 76 CAVP vectors, read %u\n", n); return 1; }
    printf("NIST CAVP SHAKE256 subset: %u/76 vectors pass for Official and candidate\n", n);
    return 0;
}

int main(int argc, char **argv) {
    if (argc != 2) { fprintf(stderr, "usage: %s shake256_cavp_subset.txt\n", argv[0]); return 2; }
    if (test_vectors(argv[1]) || test_permutation() || test_grid() || test_shapes()) return 1;
    printf("NTRU+%d SHAKE256 differential: pass (%llu SHAKE cases, %llu output bytes compared)\n",
           NTRUPLUS_N, cases, bytes_compared);
    return 0;
}
