/*
 * HT inverse NTT vs Official poly_invntt_scale bit-exact differential (NTRU+768 AVX2).
 *
 * ntruplus768_officialopt_invntt_ht must equal Official poly_invntt_scale word for
 * word (so crepmod3 and every later Decap step see identical data).  Cases:
 *   - real Decap inputs: poly_basemul_scale(c, f) with c a canonical
 *     ciphertext polynomial (poly_frombytes of random canonical bytes, plus the
 *     all-0 and all-(q-1) extremes) and f the secret-key polynomial as Decap
 *     reads it (caller-lazy Forward of a keygen f, through tobytes/frombytes);
 *   - constant min/max, alternating, every signed-word impulse pair (2N);
 *   - 20000 uniformly random int16 polynomials (the equality is unconditional);
 * each with 64-bit canaries around the candidate polynomial.
 */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"
#include "poly.h"

void ntruplus768_officialopt_invntt_ht(poly *);
void ntruplus768_officialopt_ntt_caller_lazy(poly *);

static uint64_t state = UINT64_C(0x1a2b3c4d768);
static uint32_t random_word(void) {
    state ^= state << 13;
    state ^= state >> 7;
    state ^= state << 17;
    return (uint32_t)state;
}

static unsigned long cases;

static int compare(const poly *in, const char *what, unsigned t) {
    struct { uint64_t before; poly p; uint64_t after; } cand;
    poly off = *in;
    cand.before = UINT64_C(0x93c467e37db0c7a4);
    cand.after = UINT64_C(0xd1be3f810152cb56);
    cand.p = *in;
    ntruplus768_officialopt_invntt_ht(&cand.p);
    poly_invntt_scale(&off);
    if (cand.before != UINT64_C(0x93c467e37db0c7a4) || cand.after != UINT64_C(0xd1be3f810152cb56)) {
        fprintf(stderr, "canary failure %s t=%u\n", what, t);
        return 1;
    }
    if (memcmp(&cand.p, &off, sizeof off)) {
        fprintf(stderr, "HT inverse != Official %s t=%u\n", what, t);
        return 1;
    }
    cases++;
    return 0;
}

int main(void) {
    poly p, c, f;
    uint8_t buf[NTRUPLUS_N / 4], wire[NTRUPLUS_POLYBYTES];
    unsigned long before = cases;
    for (unsigned t = 0; t < 5000; t++) {
        for (unsigned i = 0; i < NTRUPLUS_N; i++)
            c.coeffs[i] = (int16_t)(t == 0 ? 0 : t == 1 ? NTRUPLUS_Q - 1 : (int)(random_word() % NTRUPLUS_Q));
        poly_tobytes(wire, &c);
        if (poly_frombytes(&c, wire)) return 1;
        for (size_t i = 0; i < sizeof buf; i++) buf[i] = (uint8_t)random_word();
        poly_cbd1(&f, buf);
        poly_triple(&f);
        f.coeffs[0] += 1;
        ntruplus768_officialopt_ntt_caller_lazy(&f);
        poly_tobytes(wire, &f);
        if (poly_frombytes(&f, wire)) return 1;
        poly_basemul_scale(&p, &c, &f);
        if (compare(&p, "decap basemul_scale", t)) return 1;
    }
    printf("  %-24s cases=%lu HT inverse == Official bit-exact\n", "decap inputs", cases - before);
    before = cases;
    static const int16_t amp[2] = {INT16_MIN, INT16_MAX};
    for (unsigned t = 0; t < 3; t++) {
        for (unsigned i = 0; i < NTRUPLUS_N; i++) p.coeffs[i] = t < 2 ? amp[t] : amp[i & 1U];
        if (compare(&p, "constant/alternating", t)) return 1;
    }
    for (unsigned pos = 0; pos < NTRUPLUS_N; pos++)
        for (unsigned k = 0; k < 2; k++) {
            memset(&p, 0, sizeof p);
            p.coeffs[pos] = amp[k];
            if (compare(&p, "impulse", pos)) return 1;
        }
    printf("  %-24s cases=%lu HT inverse == Official bit-exact\n", "structured extremes", cases - before);
    before = cases;
    for (unsigned t = 0; t < 20000; t++) {
        for (unsigned i = 0; i < NTRUPLUS_N; i++) p.coeffs[i] = (int16_t)random_word();
        if (compare(&p, "uniform int16", t)) return 1;
    }
    printf("  %-24s cases=%lu HT inverse == Official bit-exact\n", "uniform int16", cases - before);
    printf("NTRU+%d HT inverse NTT == Official poly_invntt_scale bit-exact differential: pass "
           "(%lu cases, canaries intact)\n", NTRUPLUS_N, cases);
    return 0;
}
