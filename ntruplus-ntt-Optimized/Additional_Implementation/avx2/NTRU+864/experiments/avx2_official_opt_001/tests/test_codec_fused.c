/*
 * NTRU+864 AVX2 layout-fused codec differential (Option A, Phase A gate 1).
 *
 * Fused kernels (asm/ntruplus864_officialopt_codec_fused.s) against the
 * Official poly_tobytes / poly_frombytes linked from the pinned upstream
 * poly.c + pack.s in the same binary, plus an independent scalar model of
 * the wire format (canonical residue, 12 bits per coefficient, little endian,
 * coefficient order = internal-layout order restored by poly_ntt_pack).
 *
 * tobytes: every int16 value in every coefficient position (constant polys
 * and a 65536-poly Latin sweep), every lazy-Forward caller envelope, and
 * >= 100k random arbitrary-int16 polys; bytes must match Official exactly.
 * frombytes: random valid encodings, all-boundary patterns, every 12-bit
 * value 0..4095 at every one of the 864 positions over a valid background,
 * all-positions-equal patterns and random byte strings (mostly invalid);
 * output poly AND return value must match Official exactly.
 * Every call: 256-byte canaries on both sides of the output, input
 * immutability, and a sweep of output/input byte misalignments (0..31) for
 * the byte arrays (poly pointers keep Official's 32-byte contract).
 */
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "params.h"
#include "poly.h"

void ntruplus864_officialopt_tobytes_fused(uint8_t r[NTRUPLUS_POLYBYTES], const poly *a);
int ntruplus864_officialopt_frombytes_fused(poly *r, const uint8_t a[NTRUPLUS_POLYBYTES]);

/* internal layout: per 96-coefficient block, 16-bit word 16*r + l holds wire
 * coefficient 6*l + r (the permutation poly_ntt_pack undoes). */
static unsigned wire_index(unsigned i) {
    unsigned b = i / 96, w = i % 96;
    return 96 * b + 6 * (w % 16) + w / 16;
}

enum { N = NTRUPLUS_N, NB = NTRUPLUS_POLYBYTES, CAN = 256 };
static uint64_t state = UINT64_C(0x864c0dec20260923);
static uint32_t rnd(void) {
    state ^= state << 13;
    state ^= state >> 7;
    state ^= state << 17;
    return (uint32_t)state;
}
static int canonical(int x) {
    int r = x % NTRUPLUS_Q;
    return r < 0 ? r + NTRUPLUS_Q : r;
}

static void model_tobytes(uint8_t *out, const poly *a) {
    uint16_t c[N];
    for (unsigned i = 0; i < N; i++) c[wire_index(i)] = (uint16_t)canonical(a->coeffs[i]);
    for (unsigned i = 0; i < N / 2; i++) {
        out[3 * i] = (uint8_t)c[2 * i];
        out[3 * i + 1] = (uint8_t)((c[2 * i] >> 8) | (c[2 * i + 1] << 4));
        out[3 * i + 2] = (uint8_t)(c[2 * i + 1] >> 4);
    }
}
static void encode12(uint8_t *out, const uint16_t c[N]) { /* wire order values */
    for (unsigned i = 0; i < N / 2; i++) {
        out[3 * i] = (uint8_t)c[2 * i];
        out[3 * i + 1] = (uint8_t)((c[2 * i] >> 8) | (c[2 * i + 1] << 4));
        out[3 * i + 2] = (uint8_t)(c[2 * i + 1] >> 4);
    }
}

static unsigned long tob_cases, fromb_cases, fromb_fail_cases, model_checks;
static uint8_t out_o[NB + 2 * CAN + 32], out_f[NB + 2 * CAN + 32];
static poly pbuf_o[3], pbuf_f[3];
static uint8_t inbuf[NB + 32];

static int check_canary(const uint8_t *buf, size_t len, uint8_t pat) {
    for (size_t i = 0; i < len; i++)
        if (buf[i] != pat) return 1;
    return 0;
}

static int tob_case(const poly *a_in) {
    static poly a;
    poly keep;
    a = *a_in;
    keep = a;
    unsigned mis = (unsigned)(tob_cases % 32);
    memset(out_o, 0xa5, sizeof out_o);
    memset(out_f, 0x5a, sizeof out_f);
    poly_tobytes(out_o + CAN + mis, &a);
    ntruplus864_officialopt_tobytes_fused(out_f + CAN + mis, &a);
    tob_cases++;
    if (memcmp(&a, &keep, sizeof a)) return fprintf(stderr, "tobytes: input modified\n"), 1;
    if (memcmp(out_o + CAN + mis, out_f + CAN + mis, NB)) {
        for (unsigned i = 0; i < NB; i++)
            if (out_o[CAN + mis + i] != out_f[CAN + mis + i]) {
                fprintf(stderr, "tobytes mismatch at byte %u (official %02x fused %02x)\n", i,
                        out_o[CAN + mis + i], out_f[CAN + mis + i]);
                break;
            }
        return 1;
    }
    if (check_canary(out_f, CAN + mis, 0x5a) ||
        check_canary(out_f + CAN + mis + NB, sizeof out_f - CAN - mis - NB, 0x5a))
        return fprintf(stderr, "tobytes: canary overwritten\n"), 1;
    if ((tob_cases & 15) == 0) {   /* independent wire model on a sample */
        uint8_t m[NB];
        model_tobytes(m, &a);
        model_checks++;
        if (memcmp(m, out_f + CAN + mis, NB)) return fprintf(stderr, "tobytes != scalar model\n"), 1;
    }
    return 0;
}

static int fromb_case(const uint8_t *bytes) {
    unsigned mis = (unsigned)(fromb_cases % 32);
    uint8_t keep[NB];
    memcpy(inbuf + mis, bytes, NB);
    memcpy(keep, bytes, NB);
    memset(pbuf_o, 0xa5, sizeof pbuf_o);
    memset(pbuf_f, 0x5a, sizeof pbuf_f);
    int ro = poly_frombytes(&pbuf_o[1], inbuf + mis);
    int rf = ntruplus864_officialopt_frombytes_fused(&pbuf_f[1], inbuf + mis);
    fromb_cases++;
    fromb_fail_cases += ro != 0;
    if (memcmp(inbuf + mis, keep, NB)) return fprintf(stderr, "frombytes: input modified\n"), 1;
    if (ro != rf) return fprintf(stderr, "frombytes return mismatch %d vs %d\n", ro, rf), 1;
    if (memcmp(&pbuf_o[1], &pbuf_f[1], sizeof(poly))) {
        for (unsigned i = 0; i < N; i++)
            if (pbuf_o[1].coeffs[i] != pbuf_f[1].coeffs[i]) {
                fprintf(stderr, "frombytes coeff mismatch at %u (%d vs %d)\n", i,
                        pbuf_o[1].coeffs[i], pbuf_f[1].coeffs[i]);
                break;
            }
        return 1;
    }
    if (check_canary((uint8_t *)&pbuf_f[0], sizeof(poly), 0x5a) ||
        check_canary((uint8_t *)&pbuf_f[2], sizeof(poly), 0x5a))
        return fprintf(stderr, "frombytes: canary overwritten\n"), 1;
    /* independent model: wire value v at wire index w, fail iff any v >= q */
    int mf = 0;
    for (unsigned i = 0; i < N; i++) {
        unsigned w = wire_index(i), p = 3 * (w / 2);
        unsigned v = (w & 1) ? (unsigned)(bytes[p + 1] >> 4) | ((unsigned)bytes[p + 2] << 4)
                             : (unsigned)bytes[p] | ((unsigned)(bytes[p + 1] & 15) << 8);
        if ((unsigned)(uint16_t)pbuf_f[1].coeffs[i] != v) return fprintf(stderr, "frombytes != model\n"), 1;
        mf |= v >= NTRUPLUS_Q;
    }
    if (mf != rf) return fprintf(stderr, "frombytes fail flag != model\n"), 1;
    return 0;
}

static const int lazy_envelopes[][2] = { /* range_proof ledger, all callers */
    {-17961, 17957}, {-17193, 17194}, {-17193, 17193}, {-16382, 16385}, {-15580, 15580},
    {-1838, 1838}, {-16385, 19838}, {-17404, 17404}, {0, NTRUPLUS_Q - 1},
};

static int tobytes_gate(void) {
    poly a;
    /* every int16 value in every position: constants + Latin sweep */
    for (int v = -32768; v <= 32767; v++) {
        for (unsigned i = 0; i < N; i++) a.coeffs[i] = (int16_t)v;
        if (tob_case(&a)) return 1;
        for (unsigned i = 0; i < N; i++) a.coeffs[i] = (int16_t)(v + 40503 * (int)i);
        if (tob_case(&a)) return 1;
    }
    unsigned long exhaustive = tob_cases;
    /* lazy-Forward-reachable caller envelopes: random and extreme-only */
    for (size_t e = 0; e < sizeof lazy_envelopes / sizeof lazy_envelopes[0]; e++) {
        int lo = lazy_envelopes[e][0], hi = lazy_envelopes[e][1];
        for (unsigned t = 0; t < 4000; t++) {
            for (unsigned i = 0; i < N; i++) {
                int x = (t & 1) ? ((rnd() & 1) ? hi : lo)
                                : lo + (int)(rnd() % (unsigned)(hi - lo + 1));
                a.coeffs[i] = (int16_t)x;
            }
            if (tob_case(&a)) return 1;
        }
    }
    unsigned long envelope = tob_cases - exhaustive;
    /* arbitrary int16 */
    for (unsigned t = 0; t < 120000; t++) {
        for (unsigned i = 0; i < N; i++) a.coeffs[i] = (int16_t)rnd();
        if (tob_case(&a)) return 1;
    }
    printf("tobytes: pass (%lu cases: %lu all-int16-per-position, %lu lazy-envelope, 120000 random int16; "
           "%lu scalar-model checks; canaries, immutability, 32 output misalignments)\n",
           tob_cases, exhaustive, envelope, model_checks);
    return 0;
}

static int frombytes_gate(void) {
    uint16_t c[N];
    uint8_t b[NB];
    static const uint16_t boundary[] = {0, 1, 2, NTRUPLUS_Q - 2, NTRUPLUS_Q - 1, NTRUPLUS_Q,
                                        NTRUPLUS_Q + 1, 2048, 4094, 4095};
    /* random valid encodings */
    for (unsigned t = 0; t < 100000; t++) {
        for (unsigned i = 0; i < N; i++) c[i] = (uint16_t)(rnd() % NTRUPLUS_Q);
        encode12(b, c);
        if (fromb_case(b)) return 1;
    }
    unsigned long valid = fromb_cases;
    /* boundary patterns: all-equal, and random mixes of boundary values */
    for (size_t k = 0; k < sizeof boundary / sizeof boundary[0]; k++) {
        for (unsigned i = 0; i < N; i++) c[i] = boundary[k];
        encode12(b, c);
        if (fromb_case(b)) return 1;
    }
    for (unsigned t = 0; t < 20000; t++) {
        unsigned lim = (t & 1) ? 5 : 10; /* even t: may include values >= q */
        for (unsigned i = 0; i < N; i++) c[i] = boundary[rnd() % lim];
        encode12(b, c);
        if (fromb_case(b)) return 1;
    }
    /* every 12-bit value at every position (single-lane injection) */
    for (unsigned v = 0; v < 4096; v++) {
        for (unsigned i = 0; i < N; i++) c[i] = (uint16_t)(rnd() % NTRUPLUS_Q);
        for (unsigned pos = 0; pos < N; pos++) {
            uint16_t save = c[pos];
            c[pos] = (uint16_t)v;
            encode12(b, c);
            if (fromb_case(b)) return 1;
            c[pos] = save;
        }
        for (unsigned i = 0; i < N; i++) c[i] = (uint16_t)v;   /* all positions = v */
        encode12(b, c);
        if (fromb_case(b)) return 1;
    }
    unsigned long injected = fromb_cases;
    /* arbitrary byte strings */
    for (unsigned t = 0; t < 100000; t++) {
        for (unsigned i = 0; i < NB; i++) b[i] = (uint8_t)rnd();
        if (fromb_case(b)) return 1;
    }
    /* round trip: frombytes_fused(tobytes_fused(a)) == canonical(a) */
    for (unsigned t = 0; t < 20000; t++) {
        poly a, back;
        for (unsigned i = 0; i < N; i++) a.coeffs[i] = (int16_t)rnd();
        ntruplus864_officialopt_tobytes_fused(b, &a);
        if (ntruplus864_officialopt_frombytes_fused(&back, b)) return fprintf(stderr, "round trip rejected\n"), 1;
        for (unsigned i = 0; i < N; i++)
            if (back.coeffs[i] != canonical(a.coeffs[i])) return fprintf(stderr, "round trip mismatch\n"), 1;
    }
    printf("frombytes: pass (%lu cases, %lu rejected by Official: %lu random valid, %lu boundary+"
           "every-value-every-position, 100000 random bytes; output and return equal, scalar model, "
           "canaries, immutability, 32 input misalignments; 20000 fused round trips)\n",
           fromb_cases, fromb_fail_cases, valid, injected - valid);
    return 0;
}

int main(void) {
    if (tobytes_gate() || frombytes_gate()) {
        fputs("FAIL\n", stderr);
        return 1;
    }
    puts("NTRU+864 fused codec differential: pass");
    return 0;
}
