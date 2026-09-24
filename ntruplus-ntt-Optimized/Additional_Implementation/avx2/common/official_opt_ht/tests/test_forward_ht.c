/*
 * HT Forward vs caller-lazy Forward bit-exact differential (NTRU+768 / 864 / 1152 AVX2).
 *
 * HT_NTT (ntruplusN_officialopt_ntt_ht) must equal LAZY_NTT
 * (ntruplusN_officialopt_ntt_caller_lazy) word for word, so every bound and
 * consumer proof of the lazy Forward carries over unchanged.  Cases:
 *   - the lazy differential's caller domains (asm contract [-3,4], keygen f/g,
 *     decap [-2,2], encap/re-encap [-1,1]): constant min/max, alternating,
 *     all 4N impulse patterns, 1000 random and 1000 extreme (+-endpoint) polys;
 *   - real producer outputs: cbd1+triple (+f0 in {-2,1,4}), cbd1, sotp_encode,
 *     crepmod3 of random words (2000 each);
 *   - 20000 uniformly random int16 polynomials (the equality is unconditional);
 * each with 64-bit canaries around the candidate polynomial, and, on the
 * caller domains, Official poly_ntt == Barrett(HT) lane by lane.
 * Build with -DHT_NTT=... -DLAZY_NTT=... .
 */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"
#include "poly.h"

#if !defined(HT_NTT) || !defined(LAZY_NTT)
#error "define HT_NTT and LAZY_NTT"
#endif
void HT_NTT(poly *);
void LAZY_NTT(poly *);

static uint64_t state = UINT64_C(0x76820240924);
static uint32_t random_word(void) {
    state ^= state << 13;
    state ^= state >> 7;
    state ^= state << 17;
    return (uint32_t)state;
}

static int barrett(int x) { return x - NTRUPLUS_Q * ((x * 9 + (1 << 14)) >> 15); }

struct domain { const char *name; int lo, hi, step, f0; };
static const struct domain domains[] = {
    {"asm_contract[-3,4]", -3, 4, 1, 0},
    {"keygen_f", -3, 3, 3, 1},
    {"keygen_g", -3, 3, 3, 0},
    {"decap_msg[-2,2]", -2, 2, 1, 0},
    {"encap_r_m_reenc[-1,1]", -1, 1, 1, 0},
};
enum { NDOMAINS = sizeof domains / sizeof domains[0], RANDOM = 1000, EXTREME = 1000,
       FULL_RANDOM = 20000, PRODUCER = 2000 };

static unsigned long cases;
static int seen_lo, seen_hi;

/* HT vs lazy on one input; optionally also Official == Barrett(HT). */
static int compare(const poly *in, int official_check, const char *what, unsigned trial) {
    struct { uint64_t before; poly p; uint64_t after; } cand;
    poly lazy = *in, official = *in;
    cand.before = UINT64_C(0x526701aa234de096);
    cand.after = UINT64_C(0xe43d4018ad917c25);
    cand.p = *in;
    HT_NTT(&cand.p);
    LAZY_NTT(&lazy);
    if (cand.before != UINT64_C(0x526701aa234de096) || cand.after != UINT64_C(0xe43d4018ad917c25)) {
        fprintf(stderr, "canary failure %s trial=%u\n", what, trial);
        return 1;
    }
    if (memcmp(&cand.p, &lazy, sizeof lazy)) {
        for (unsigned i = 0; i < NTRUPLUS_N; i++)
            if (cand.p.coeffs[i] != lazy.coeffs[i]) {
                fprintf(stderr, "HT != lazy %s trial=%u lane=%u (%d vs %d)\n", what, trial, i,
                        cand.p.coeffs[i], lazy.coeffs[i]);
                break;
            }
        return 1;
    }
    if (official_check) {
        poly_ntt(&official);
        for (unsigned i = 0; i < NTRUPLUS_N; i++) {
            if (barrett(cand.p.coeffs[i]) != official.coeffs[i]) {
                fprintf(stderr, "Barrett(HT) != Official %s trial=%u lane=%u\n", what, trial, i);
                return 1;
            }
            if (cand.p.coeffs[i] < seen_lo) seen_lo = cand.p.coeffs[i];
            if (cand.p.coeffs[i] > seen_hi) seen_hi = cand.p.coeffs[i];
        }
    }
    cases++;
    return 0;
}

static int16_t pick(const struct domain *d, int extreme) {
    if (extreme) return (int16_t)((random_word() & 1U) ? d->hi : d->lo);
    unsigned width = (unsigned)((d->hi - d->lo) / d->step + 1);
    return (int16_t)(d->lo + d->step * (int)(random_word() % width));
}

int main(void) {
    poly p;
    for (unsigned di = 0; di < NDOMAINS; di++) {
        const struct domain *d = &domains[di];
        int amp[2] = {d->lo, d->hi};
        const unsigned structured = 3U + 4U * NTRUPLUS_N;
        const unsigned trials = structured + RANDOM + EXTREME;
        unsigned long before = cases;
        seen_lo = seen_hi = 0;
        for (unsigned trial = 0; trial < trials; trial++) {
            for (unsigned i = 0; i < NTRUPLUS_N; i++) {
                int16_t v;
                if (trial == 0) v = (int16_t)d->hi;
                else if (trial == 1) v = (int16_t)d->lo;
                else if (trial == 2) v = (int16_t)amp[i & 1U];
                else if (trial < structured) {
                    unsigned k = trial - 3U, pos = k / 4U, kind = k % 4U;
                    if (kind < 2) v = (i == pos) ? (int16_t)amp[kind] : 0;
                    else v = (i == pos) ? (int16_t)amp[kind - 2] : (int16_t)amp[3 - kind];
                } else v = pick(d, trial >= structured + RANDOM);
                if (d->step == 3 && v % 3) v = (int16_t)(v < 0 ? -3 : 3);
                p.coeffs[i] = v;
            }
            if (d->f0) {
                static const int16_t f0_values[3] = {-2, 1, 4};
                p.coeffs[0] = f0_values[trial % 3U];
            }
            if (compare(&p, 1, d->name, trial)) return 1;
        }
        printf("  %-24s cases=%lu HT==lazy bit-exact, Barrett(HT)==Official, observed=[%d,%d]\n",
               d->name, cases - before, seen_lo, seen_hi);
    }
    /* real producer outputs */
    uint8_t buf[NTRUPLUS_N / 4], msg[NTRUPLUS_N / 8];
    unsigned long before = cases;
    for (unsigned t = 0; t < PRODUCER; t++) {
        for (size_t i = 0; i < sizeof buf; i++) buf[i] = (uint8_t)random_word();
        for (size_t i = 0; i < sizeof msg; i++) msg[i] = (uint8_t)random_word();
        poly_cbd1(&p, buf);
        if (compare(&p, 1, "cbd1", t)) return 1;                 /* encap r / re-encap */
        poly_triple(&p);
        if (compare(&p, 1, "cbd1+triple", t)) return 1;          /* keygen g */
        p.coeffs[0] += 1;
        if (compare(&p, 1, "cbd1+triple+1", t)) return 1;        /* keygen f */
        poly_sotp_encode(&p, msg, buf);
        if (compare(&p, 1, "sotp_encode", t)) return 1;          /* encap m */
        for (unsigned i = 0; i < NTRUPLUS_N; i++) p.coeffs[i] = (int16_t)random_word();
        poly_crepmod3(&p);
        if (compare(&p, 1, "crepmod3", t)) return 1;             /* decap m */
    }
    printf("  %-24s cases=%lu HT==lazy bit-exact, Barrett(HT)==Official\n", "producers", cases - before);
    before = cases;
    for (unsigned t = 0; t < FULL_RANDOM; t++) {
        for (unsigned i = 0; i < NTRUPLUS_N; i++) p.coeffs[i] = (int16_t)random_word();
        if (t == 0) for (unsigned i = 0; i < NTRUPLUS_N; i++) p.coeffs[i] = INT16_MIN;
        if (t == 1) for (unsigned i = 0; i < NTRUPLUS_N; i++) p.coeffs[i] = INT16_MAX;
        if (compare(&p, 0, "full-int16", t)) return 1;
    }
    printf("  %-24s cases=%lu HT==lazy bit-exact\n", "uniform int16", cases - before);
    printf("NTRU+%d HT Forward == caller-lazy Forward bit-exact differential: pass (%lu cases, canaries intact)\n",
           NTRUPLUS_N, cases);
    return 0;
}
