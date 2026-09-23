/*
 * Caller-bounded lazy Forward differential for Official NTRU+864/1152 AVX2.
 * Adapted from NTRU+768 avx2_official_opt_001/tests/test_forward_caller_lazy.c.
 *
 * For every case, on the Official caller domains:
 *   - lazy == Official (mod q) lane by lane;
 *   - Official terminal Barrett applied to the lazy output reproduces the
 *     Official output bit-exactly (the only deleted operation);
 *   - lazy output lies inside the per-domain proven bound (range_proof/);
 *   - 64-bit canaries around the polynomial are untouched.
 * Plus producer-domain checks (cbd1, triple, sotp_encode, crepmod3) and an
 * exhaustive signed-word check that poly_tobytes/poly_frombytes canonicalise
 * any int16 lane, which is what makes the lazy representation wire-invisible.
 *
 * Build with -DLAZY_NTT=ntruplus{N}_officialopt_ntt_caller_lazy.
 */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"
#include "poly.h"

#ifndef LAZY_NTT
#error "define LAZY_NTT"
#endif
void LAZY_NTT(poly *);

static uint64_t state = UINT64_C(0x86411520260923);
static uint32_t random_word(void) {
    state ^= state << 13;
    state ^= state >> 7;
    state ^= state << 17;
    return (uint32_t)state;
}

static int barrett(int x) { /* Official vpmulhrsw(_16xv)/vpmullw(q)/vpsubw */
    return x - NTRUPLUS_Q * ((x * 9 + (1 << 14)) >> 15);
}

static int canonical(int x) {
    int r = x % NTRUPLUS_Q;
    return r < 0 ? r + NTRUPLUS_Q : r;
}

/* Caller domains and the proven lazy output bounds (range_proof ledger). */
struct domain {
    const char *name;
    int lo, hi;          /* coefficient input interval */
    int step;            /* 3 for triple(cbd1) domains, else 1 */
    int f0;              /* keygen f: coeff 0 in {-2,1,4} */
    int out_lo, out_hi;  /* proven lazy output interval */
};
static const struct domain domains[] = {
    {"asm_contract[-3,4]", -3, 4, 1, 0, -17961, 17957},
    {"keygen_f", -3, 3, 3, 1, -17193, 17194},
    {"keygen_g", -3, 3, 3, 0, -17193, 17193},
    {"decap_msg[-2,2]", -2, 2, 1, 0, -16382, 16385},
    {"encap_r_m_reenc[-1,1]", -1, 1, 1, 0, -15580, 15580},
};
enum { NDOMAINS = sizeof domains / sizeof domains[0], RANDOM = 1000, EXTREME = 1000 };

static int16_t pick(const struct domain *d, int extreme) {
    if (extreme)
        return (int16_t)((random_word() & 1U) ? d->hi : d->lo);
    unsigned width = (unsigned)((d->hi - d->lo) / d->step + 1);
    return (int16_t)(d->lo + d->step * (int)(random_word() % width));
}

static int producer_checks(void) {
    poly p;
    uint8_t buf[NTRUPLUS_N / 4], msg[NTRUPLUS_N / 8];
    for (unsigned t = 0; t < 2000; t++) {
        for (size_t i = 0; i < sizeof buf; i++) buf[i] = (uint8_t)random_word();
        for (size_t i = 0; i < sizeof msg; i++) msg[i] = (uint8_t)random_word();
        if (t == 0) memset(buf, 0xff, sizeof buf);
        if (t == 1) memset(buf, 0x00, sizeof buf);
        poly_cbd1(&p, buf);
        for (unsigned i = 0; i < NTRUPLUS_N; i++)
            if (p.coeffs[i] < -1 || p.coeffs[i] > 1) return 1;
        poly_triple(&p);
        for (unsigned i = 0; i < NTRUPLUS_N; i++)
            if (p.coeffs[i] != -3 && p.coeffs[i] != 0 && p.coeffs[i] != 3) return 2;
        poly_sotp_encode(&p, msg, buf);
        for (unsigned i = 0; i < NTRUPLUS_N; i++)
            if (p.coeffs[i] < -1 || p.coeffs[i] > 1) return 3;
    }
    /* crepmod3 on every signed word: Decap Forward input domain [-2,2]. */
    for (int base = -32768; base < 32768; base += NTRUPLUS_N) {
        for (unsigned i = 0; i < NTRUPLUS_N; i++) {
            int x = base + (int)i;
            p.coeffs[i] = (int16_t)(x > 32767 ? 32767 : x);
        }
        poly_crepmod3(&p);
        for (unsigned i = 0; i < NTRUPLUS_N; i++)
            if (p.coeffs[i] < -2 || p.coeffs[i] > 2) return 4;
    }
    return 0;
}

static int wire_checks(unsigned *calls) {
    poly a, c, back;
    uint8_t wa[NTRUPLUS_POLYBYTES], wc[NTRUPLUS_POLYBYTES];
    for (int base = -32768; base < 32768; base += NTRUPLUS_N) {
        for (unsigned i = 0; i < NTRUPLUS_N; i++) {
            int x = base + (int)i;
            if (x > 32767) x = (int)(random_word() % 65536U) - 32768;
            a.coeffs[i] = (int16_t)x;
            c.coeffs[i] = (int16_t)canonical(x);
        }
        poly_tobytes(wa, &a);
        poly_tobytes(wc, &c);
        if (memcmp(wa, wc, sizeof wa)) return 1;
        if (poly_frombytes(&back, wa)) return 2;
        if (memcmp(&back, &c, sizeof back)) return 3;
        (*calls)++;
    }
    return 0;
}

int main(void) {
    struct guarded_poly {
        uint64_t before;
        poly p;
        uint64_t after;
    } candidate;
    poly official;
    unsigned long total = 0;

    int status = producer_checks();
    if (status) {
        fprintf(stderr, "caller producer domain check failed (%d)\n", status);
        return 1;
    }
    unsigned wire_calls = 0;
    status = wire_checks(&wire_calls);
    if (status) {
        fprintf(stderr, "tobytes/frombytes canonicalisation failed (%d)\n", status);
        return 1;
    }

    for (unsigned di = 0; di < NDOMAINS; di++) {
        const struct domain *d = &domains[di];
        int amp[2] = {d->lo, d->hi};
        const unsigned structured = 3U + 4U * NTRUPLUS_N;
        const unsigned trials = structured + RANDOM + EXTREME;
        int seen_lo = 0, seen_hi = 0;
        for (unsigned trial = 0; trial < trials; trial++) {
            for (unsigned i = 0; i < NTRUPLUS_N; i++) {
                int16_t v;
                if (trial == 0) v = (int16_t)d->hi;                     /* constant max */
                else if (trial == 1) v = (int16_t)d->lo;                /* constant min */
                else if (trial == 2) v = (int16_t)amp[i & 1U];          /* alternating */
                else if (trial < structured) {                          /* impulses */
                    unsigned k = trial - 3U, pos = k / 4U, kind = k % 4U;
                    if (kind < 2) v = (i == pos) ? (int16_t)amp[kind] : 0;
                    else v = (i == pos) ? (int16_t)amp[kind - 2] : (int16_t)amp[3 - kind];
                } else v = pick(d, trial >= structured + RANDOM);
                if (d->step == 3 && v % 3) v = (int16_t)(v < 0 ? -3 : 3);
                official.coeffs[i] = v;
            }
            if (d->f0) {
                static const int16_t f0_values[3] = {-2, 1, 4};
                official.coeffs[0] = f0_values[trial % 3U];
            }
            candidate.before = UINT64_C(0x526701aa234de096);
            candidate.after = UINT64_C(0xe43d4018ad917c25);
            candidate.p = official;
            poly_ntt(&official);
            LAZY_NTT(&candidate.p);
            if (candidate.before != UINT64_C(0x526701aa234de096) ||
                candidate.after != UINT64_C(0xe43d4018ad917c25)) {
                fprintf(stderr, "canary failure domain=%s trial=%u\n", d->name, trial);
                return 1;
            }
            for (unsigned i = 0; i < NTRUPLUS_N; i++) {
                int x = candidate.p.coeffs[i], o = official.coeffs[i];
                if ((x - o) % NTRUPLUS_Q) {
                    fprintf(stderr, "residue failure domain=%s trial=%u lane=%u\n", d->name, trial, i);
                    return 1;
                }
                if (barrett(x) != o) {
                    fprintf(stderr, "Barrett identity failure domain=%s trial=%u lane=%u\n",
                            d->name, trial, i);
                    return 1;
                }
                if (x < d->out_lo || x > d->out_hi) {
                    fprintf(stderr, "bound failure domain=%s trial=%u lane=%u value=%d\n",
                            d->name, trial, i, x);
                    return 1;
                }
                if (x < seen_lo) seen_lo = x;
                if (x > seen_hi) seen_hi = x;
            }
        }
        total += trials;
        printf("  %-24s cases=%u observed=[%d,%d] proven=[%d,%d]\n", d->name, trials,
               seen_lo, seen_hi, d->out_lo, d->out_hi);
    }
    printf("NTRU+%d caller-lazy Forward residue/Barrett-identity/bound/canary differential: "
           "pass (%lu cases); producers pass; tobytes/frombytes canonical on all int16 "
           "(%u polys)\n", NTRUPLUS_N, total, wire_calls);
    return 0;
}
