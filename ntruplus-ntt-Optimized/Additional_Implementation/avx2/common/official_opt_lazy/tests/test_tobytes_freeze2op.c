/*
 * poly_tobytes 2-op freeze differential vs Official (NTRU+768 / NTRU+1152).
 *
 * Build with -DFREEZE_TOBYTES=ntruplus{N}_officialopt_tobytes_freeze2op and
 * -DLAZY_NTT=ntruplus{N}_officialopt_ntt_caller_lazy.  The oracle is the
 * linked Official poly_tobytes of the same pinned pack.s.
 *
 *  1. every int16 value at every coefficient position: polys
 *     a[i] = base + K*i (mod 2^16) for all 65536 bases and K in {0, 1, 40503}
 *     (K = 0: constant polys; odd K: each position sees every value once, in
 *     mixed neighbourhoods); wire bytes == Official, and poly_frombytes of
 *     the wire accepts and returns x mod q in every lane;
 *  2. 20000 random int16 polys, 2000 polys of the edge set
 *     {-32768, -32767, -q, -q+1, -1, 0, 1, q-1, q, q+1, 32766, 32767} and
 *     the Barrett tie points;
 *  3. lazy-Forward caller envelopes: uniform and endpoint values inside every
 *     proven lazy output interval, plus real lazy Forward outputs of the KEM
 *     producers (cbd1, triple(cbd1), sotp_encode, crepmod3 image [-2,2]);
 *  4. 64-bit canaries around the poly and the wire array, input immutability,
 *     every wire misalignment 0..31;
 *  5. guard pages: the wire array and the poly each placed flush against a
 *     PROT_NONE page, before and after (adapted from NTRU+864
 *     avx2_official_opt_001/tests/test_codec_guard.c), so any out-of-bounds
 *     read or write faults.
 */
#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

#include "params.h"
#include "poly.h"

#ifndef FREEZE_TOBYTES
#error "define FREEZE_TOBYTES"
#endif
#ifndef LAZY_NTT
#error "define LAZY_NTT"
#endif
void FREEZE_TOBYTES(uint8_t r[NTRUPLUS_POLYBYTES], const poly *a);
void LAZY_NTT(poly *);

enum { NB = NTRUPLUS_POLYBYTES, PB = (int)sizeof(poly), N = NTRUPLUS_N, Q = NTRUPLUS_Q };

static uint64_t rng = UINT64_C(0x2f0e5a1152768023);
static uint32_t next(void) {
    rng ^= rng << 13; rng ^= rng >> 7; rng ^= rng << 17;
    return (uint32_t)(rng >> 16);
}
static int canonical(int x) { int r = x % Q; return r < 0 ? r + Q : r; }

static unsigned long compared;

/* Official vs candidate on one poly: canaries, immutability, wire equality,
 * frombytes round trip to the canonical residues. */
static int check(const poly *in, const char *what, unsigned tag) {
    static struct { uint64_t before; poly p; uint64_t after; } gp;
    static struct { uint64_t before; uint8_t b[NB + 32]; uint64_t after; } gw;
    uint8_t ref[NB];
    poly back;
    unsigned mis = tag % 32U;
    gp.before = UINT64_C(0x0123456789abcdef); gp.after = UINT64_C(0xfedcba9876543210);
    gw.before = UINT64_C(0x5a5a5a5a5a5a5a5a); gw.after = UINT64_C(0xa5a5a5a5a5a5a5a5);
    gp.p = *in;
    memset(gw.b, 0xc3, sizeof gw.b);
    poly_tobytes(ref, in);
    FREEZE_TOBYTES(gw.b + mis, &gp.p);
    if (gp.before != UINT64_C(0x0123456789abcdef) || gp.after != UINT64_C(0xfedcba9876543210) ||
        gw.before != UINT64_C(0x5a5a5a5a5a5a5a5a) || gw.after != UINT64_C(0xa5a5a5a5a5a5a5a5)) {
        fprintf(stderr, "FAIL canary %s tag=%u\n", what, tag); return 1;
    }
    for (unsigned i = 0; i < sizeof gw.b; i++)
        if ((i < mis || i >= mis + NB) && gw.b[i] != 0xc3) {
            fprintf(stderr, "FAIL out-of-range wire write %s tag=%u byte=%u\n", what, tag, i); return 1;
        }
    if (memcmp(&gp.p, in, PB)) { fprintf(stderr, "FAIL input modified %s tag=%u\n", what, tag); return 1; }
    if (memcmp(ref, gw.b + mis, NB)) {
        fprintf(stderr, "FAIL wire mismatch %s tag=%u\n", what, tag); return 1;
    }
    if (poly_frombytes(&back, ref)) { fprintf(stderr, "FAIL frombytes reject %s tag=%u\n", what, tag); return 1; }
    for (unsigned i = 0; i < N; i++)
        if (back.coeffs[i] != canonical(in->coeffs[i])) {
            fprintf(stderr, "FAIL residue %s tag=%u lane=%u\n", what, tag, i); return 1;
        }
    compared++;
    return 0;
}

/* Proven lazy Forward output intervals per caller domain (range_proof/
 * prove_forward_lazy.py EXPECTED_LAZY; the freeze itself is proven for every
 * int16, section 1 covers all of them). */
static const int envelopes[][2] = {
#if NTRUPLUS_N == 768
    {-16058, 16035}, {-15251, 15252}, {-15251, 15251}, {-14449, 14449}, {-13636, 13636}};
#else
    {-17961, 17957}, {-17193, 17194}, {-17193, 17193}, {-16382, 16385}, {-15580, 15580}};
#endif

typedef struct { uint8_t *map; size_t len; uint8_t *p; } guarded;
static guarded guard_alloc(size_t size, int before) {
    size_t pg = (size_t)sysconf(_SC_PAGESIZE);
    size_t data = (size + pg - 1) / pg * pg;
    guarded g;
    g.len = data + 2 * pg;
    g.map = mmap(NULL, g.len, PROT_READ | PROT_WRITE, MAP_PRIVATE | MAP_ANONYMOUS, -1, 0);
    if (g.map == MAP_FAILED) { perror("mmap"); exit(2); }
    if (mprotect(g.map, pg, PROT_NONE) || mprotect(g.map + pg + data, pg, PROT_NONE)) {
        perror("mprotect"); exit(2);
    }
    g.p = before ? g.map + pg : g.map + pg + data - size;
    return g;
}

static int guard_checks(void) {
    poly src;
    uint8_t ref[NB];
    unsigned rounds = 0;
    /* poly and wire sizes are multiples of 32, so both placements keep the
     * poly 32-byte aligned (vmovdqa); the wire array needs no alignment. */
    for (int before = 0; before < 2; before++) {
        guarded wire = guard_alloc(NB, before), pl = guard_alloc(PB, before);
        poly *gp = (poly *)pl.p;
        for (int r = 0; r < 500; r++, rounds++) {
            for (unsigned i = 0; i < N; i++) {
                switch (r % 4) {
                case 0: src.coeffs[i] = (int16_t)next(); break;
                case 1: src.coeffs[i] = (int16_t)(i & 1 ? INT16_MAX : INT16_MIN); break;
                case 2: src.coeffs[i] = (int16_t)(Q - 1); break;
                default: src.coeffs[i] = (int16_t)(envelopes[0][0] +
                             (int)(next() % (unsigned)(envelopes[0][1] - envelopes[0][0] + 1))); break;
                }
            }
            memcpy(gp, &src, PB);
            poly_tobytes(ref, &src);
            FREEZE_TOBYTES(wire.p, gp);
            if (memcmp(ref, wire.p, NB) || memcmp(gp, &src, PB)) {
                fprintf(stderr, "FAIL guard %s round %d\n", before ? "leading" : "trailing", r); return 1;
            }
        }
        munmap(wire.map, wire.len);
        munmap(pl.map, pl.len);
    }
    printf("  guard pages (wire %d B, poly %d B; leading + trailing PROT_NONE): %u rounds, no fault\n",
           NB, PB, rounds);
    return 0;
}

int main(void) {
    static poly p;
    static const unsigned ks[3] = {0, 1, 40503};
    unsigned long c0;

    /* 1. every value at every position */
    c0 = compared;
    for (unsigned k = 0; k < 3; k++)
        for (unsigned base = 0; base < 65536U; base++) {
            for (unsigned i = 0; i < N; i++) p.coeffs[i] = (int16_t)(uint16_t)(base + ks[k] * i);
            if (check(&p, "exhaustive", base)) return 1;
        }
    printf("  every int16 value at every position (K=0,1,40503): %lu polys\n", compared - c0);

    /* 2. random and edge polys */
    c0 = compared;
    static const int edge[] = {-32768, -32767, -Q, -Q + 1, -1, 0, 1, Q - 1, Q, Q + 1, 32766, 32767,
                               -3291, 3291, -1729, 1729, -1728, 1728, 3456 * 9, -3456 * 9};
    const unsigned ne = sizeof edge / sizeof edge[0];
    for (unsigned t = 0; t < 20000; t++) {
        for (unsigned i = 0; i < N; i++) p.coeffs[i] = (int16_t)next();
        if (check(&p, "random", t)) return 1;
    }
    for (unsigned t = 0; t < 2000; t++) {
        for (unsigned i = 0; i < N; i++) p.coeffs[i] = (int16_t)edge[next() % ne];
        if (check(&p, "edge", t)) return 1;
    }
    printf("  random + edge-set polys: %lu\n", compared - c0);

    /* 3. lazy-Forward caller envelopes */
    c0 = compared;
    for (unsigned e = 0; e < sizeof envelopes / sizeof envelopes[0]; e++) {
        int lo = envelopes[e][0], hi = envelopes[e][1];
        unsigned w = (unsigned)(hi - lo + 1);
        for (unsigned t = 0; t < 4000; t++) {
            for (unsigned i = 0; i < N; i++) {
                unsigned r = next();
                p.coeffs[i] = (int16_t)(t % 4 == 0 ? (r & 1 ? hi : lo) : lo + (int)(r % w));
            }
            if (check(&p, "envelope", t)) return 1;
        }
    }
    {
        uint8_t buf[N / 4], msg[N / 8];
        for (unsigned t = 0; t < 4000; t++) {
            for (size_t i = 0; i < sizeof buf; i++) buf[i] = (uint8_t)next();
            for (size_t i = 0; i < sizeof msg; i++) msg[i] = (uint8_t)next();
            switch (t % 4) {
            case 0: poly_cbd1(&p, buf); break;
            case 1: poly_cbd1(&p, buf); poly_triple(&p); p.coeffs[0] = (int16_t)(p.coeffs[0] + 1); break;
            case 2: poly_sotp_encode(&p, msg, buf); break;
            default:
                for (unsigned i = 0; i < N; i++) p.coeffs[i] = (int16_t)next();
                poly_crepmod3(&p);
                break;
            }
            LAZY_NTT(&p);
            if (check(&p, "lazy-forward-output", t)) return 1;
        }
    }
    printf("  lazy-Forward envelopes + real lazy Forward outputs: %lu polys\n", compared - c0);

    if (guard_checks()) return 1;
    printf("NTRU+%d tobytes 2-op freeze vs Official: pass (%lu polys byte-exact, frombytes "
           "round trip canonical, canaries, immutability, 32 wire misalignments, guard pages)\n",
           N, compared);
    return 0;
}
