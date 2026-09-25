/*
 * Shoup BaseMul vs Official poly_basemul differential (mod q), NTRU+768 / 864 / 1152 AVX2
 * (parameter from params.h).  SHOUP(r, a, b): a lazy, b canonical, r not overlapping a/b.
 *
 * Cases, each compared word by word mod q with Official poly_basemul (which is symmetric
 * in its operands mod q) and through poly_tobytes (byte-exact); every output word must lie in
 * the proven output range (shoup_env.h, from prove_basemul_shoup.py --emit-env):
 *   - real Encap inputs: a = HT Forward of a CBD1 r, b = h = poly_frombytes of random
 *     canonical bytes (plus all-0 / all-(q-1));
 *   - real Decap inputs: a = c - HT Forward of a {-1,0,1} message polynomial (poly_sub),
 *     c and b = hinv canonical;
 *   - adversarial: a uniform in, and at the ends of, the proven caller envelopes (the box
 *     the exhaustive proof covers), b in {0, 1, q-1, (q-1)/2} or uniform canonical;
 * with 64-bit canaries around r and a/b checked unchanged.
 */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"
#include "poly.h"
#include "shoup_env.h"

#define CAT_(a, b, c) a##b##c
#define CAT(a, b, c) CAT_(a, b, c)
#define SHOUP CAT(ntruplus, NTRUPLUS_N, _officialopt_basemul_shoup)
#define HTNTT CAT(ntruplus, NTRUPLUS_N, _officialopt_ntt_ht)
void SHOUP(poly *, const poly *, const poly *);
void HTNTT(poly *);

static uint64_t state = UINT64_C(0x5b0a95e1d) ^ NTRUPLUS_N;
static uint32_t random_word(void) {
    state ^= state << 13;
    state ^= state >> 7;
    state ^= state << 17;
    return (uint32_t)state;
}

static unsigned long cases;

static int check(const poly *a, const poly *b, int lo, int hi, const char *what, unsigned t) {
    struct { uint64_t before; poly p; uint64_t after; } cand;
    poly off, a0 = *a, b0 = *b;
    uint8_t w0[NTRUPLUS_POLYBYTES], w1[NTRUPLUS_POLYBYTES];
    cand.before = UINT64_C(0x93c467e37db0c7a4);
    cand.after = UINT64_C(0xd1be3f810152cb56);
    memset(&cand.p, 0x5a, sizeof cand.p);
    SHOUP(&cand.p, a, b);
    poly_basemul(&off, b, a);
    if (cand.before != UINT64_C(0x93c467e37db0c7a4) || cand.after != UINT64_C(0xd1be3f810152cb56) ||
        memcmp(&a0, a, sizeof a0) || memcmp(&b0, b, sizeof b0)) {
        fprintf(stderr, "canary / input immutability failure %s t=%u\n", what, t);
        return 1;
    }
    for (unsigned i = 0; i < NTRUPLUS_N; i++) {
        int x = cand.p.coeffs[i], y = off.coeffs[i];
        if (((x - y) % NTRUPLUS_Q + NTRUPLUS_Q) % NTRUPLUS_Q) {
            fprintf(stderr, "Shoup != Official mod q %s t=%u word %u (%d vs %d)\n", what, t, i, x, y);
            return 1;
        }
        if (x < lo || x > hi) {
            fprintf(stderr, "Shoup output %d outside proven [%d, %d] %s t=%u\n", x, lo, hi, what, t);
            return 1;
        }
    }
    poly_tobytes(w0, &off);
    poly_tobytes(w1, &cand.p);
    if (memcmp(w0, w1, sizeof w0)) {
        fprintf(stderr, "tobytes differ %s t=%u\n", what, t);
        return 1;
    }
    cases++;
    return 0;
}

static void canonical(poly *p, unsigned t) {
    uint8_t wire[NTRUPLUS_POLYBYTES];
    for (unsigned i = 0; i < NTRUPLUS_N; i++)
        p->coeffs[i] = (int16_t)(t == 0 ? 0 : t == 1 ? NTRUPLUS_Q - 1 : (int)(random_word() % NTRUPLUS_Q));
    poly_tobytes(wire, p);
    if (poly_frombytes(p, wire)) __builtin_trap();
}

int main(void) {
    poly a, b, m;
    uint8_t buf[NTRUPLUS_N / 4];
    unsigned long before = cases;
    for (unsigned t = 0; t < 5000; t++) {
        for (size_t i = 0; i < sizeof buf; i++) buf[i] = (uint8_t)random_word();
        poly_cbd1(&a, buf);
        HTNTT(&a);
        canonical(&b, t);
        if (check(&a, &b, SHOUP_ENCAP_OUT_LO, SHOUP_ENCAP_OUT_HI, "encap", t)) return 1;
    }
    printf("  %-24s cases=%lu Shoup == Official mod q\n", "encap inputs", cases - before);
    before = cases;
    for (unsigned t = 0; t < 5000; t++) {
        poly c;
        canonical(&c, t);
        for (unsigned i = 0; i < NTRUPLUS_N; i++) m.coeffs[i] = (int16_t)((int)(random_word() % 3) - 1);
        HTNTT(&m);
        poly_sub(&a, &c, &m);
        canonical(&b, t + 7);
        if (check(&a, &b, SHOUP_DECAP_OUT_LO, SHOUP_DECAP_OUT_HI, "decap", t)) return 1;
    }
    printf("  %-24s cases=%lu Shoup == Official mod q\n", "decap inputs", cases - before);
    before = cases;
    static const int alo[2] = {SHOUP_ENCAP_A_LO, SHOUP_DECAP_A_LO}, ahi[2] = {SHOUP_ENCAP_A_HI, SHOUP_DECAP_A_HI};
    static const int olo[2] = {SHOUP_ENCAP_OUT_LO, SHOUP_DECAP_OUT_LO}, ohi[2] = {SHOUP_ENCAP_OUT_HI, SHOUP_DECAP_OUT_HI};
    static const int bfix[4] = {0, 1, NTRUPLUS_Q - 1, (NTRUPLUS_Q - 1) / 2};
    for (unsigned t = 0; t < 40000; t++) {
        unsigned k = t & 1U, mode = (t >> 1) % 4;
        for (unsigned i = 0; i < NTRUPLUS_N; i++) {
            uint32_t r = random_word();
            if (mode == 0) a.coeffs[i] = (int16_t)(r & 1 ? alo[k] : ahi[k]);
            else if (mode == 1) a.coeffs[i] = (int16_t)((r & 3) == 0 ? alo[k] : (r & 3) == 1 ? ahi[k] :
                                                       (r & 3) == 2 ? alo[k] + 1 : ahi[k] - 1);
            else a.coeffs[i] = (int16_t)(alo[k] + (int)(r % (uint32_t)(ahi[k] - alo[k] + 1)));
            uint32_t s = random_word();
            b.coeffs[i] = (int16_t)(mode == 3 ? (int)(s % NTRUPLUS_Q) : bfix[s & 3]);
        }
        if (check(&a, &b, olo[k], ohi[k], "adversarial envelope", t)) return 1;
    }
    printf("  %-24s cases=%lu Shoup == Official mod q\n", "adversarial envelope", cases - before);
    printf("NTRU+%d Shoup BaseMul == Official poly_basemul (mod q, tobytes byte-exact) differential: pass "
           "(%lu cases, outputs in the proven ranges, canaries intact, inputs unchanged)\n", NTRUPLUS_N, cases);
    return 0;
}
