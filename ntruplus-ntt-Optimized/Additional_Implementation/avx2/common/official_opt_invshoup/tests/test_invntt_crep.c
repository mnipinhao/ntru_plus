/*
 * Inverse D (fused inverse NTT + crepmod3) vs Official poly_crepmod3(poly_invntt_scale(x))
 * bit-exact differential, NTRU+864 / NTRU+1152 AVX2 (parameter from params.h).
 *
 * INVCREP (the candidate entry) must equal the Official pair word for word on the
 * Decap domain, i.e. on kem.c's poly_basemul_scale(&m, &c, &f) output with c, f
 * canonical.  Cases:
 *   - real Decap inputs: poly_basemul_scale(c, f), c = poly_frombytes of random
 *     canonical bytes (plus all-0 and all-(q-1)), f = a keygen f through Official
 *     poly_ntt + poly_tobytes/poly_frombytes (canonical, as Decap reads sk);
 *   - box-uniform: every lane uniform in its proven Decap-domain interval
 *     (decap_box[] from prove_invntt_crep.py --emit-box);
 *   - box corners: every lane at one end of its interval;
 * each with 64-bit canaries around the candidate polynomial; every output word
 * must also lie in {-1, 0, 1}.
 */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "params.h"
#include "poly.h"
#include "invcrep_box.h"

#define CAT_(a, b, c) a##b##c
#define CAT(a, b, c) CAT_(a, b, c)
#define INVCREP CAT(ntruplus, NTRUPLUS_N, _officialopt_invntt_crep)
void INVCREP(poly *);

static uint64_t state = UINT64_C(0x5eed1c7e9) ^ NTRUPLUS_N;
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
    INVCREP(&cand.p);
    poly_invntt_scale(&off);
    poly_crepmod3(&off);
    if (cand.before != UINT64_C(0x93c467e37db0c7a4) || cand.after != UINT64_C(0xd1be3f810152cb56)) {
        fprintf(stderr, "canary failure %s t=%u\n", what, t);
        return 1;
    }
    if (memcmp(&cand.p, &off, sizeof off)) {
        fprintf(stderr, "Inverse D != Official crepmod3(invntt) %s t=%u\n", what, t);
        return 1;
    }
    for (unsigned i = 0; i < NTRUPLUS_N; i++)
        if (cand.p.coeffs[i] < -1 || cand.p.coeffs[i] > 1) {
            fprintf(stderr, "output outside {-1,0,1} %s t=%u\n", what, t);
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
        poly_ntt(&f);
        poly_tobytes(wire, &f);
        if (poly_frombytes(&f, wire)) return 1;
        poly_basemul_scale(&p, &c, &f);
        for (unsigned i = 0; i < NTRUPLUS_N; i++)
            if (p.coeffs[i] < decap_box[i][0] || p.coeffs[i] > decap_box[i][1]) {
                fprintf(stderr, "real Decap input outside the proven box lane %u\n", i);
                return 1;
            }
        if (compare(&p, "decap basemul_scale", t)) return 1;
    }
    printf("  %-24s cases=%lu Inverse D == Official bit-exact\n", "decap inputs", cases - before);
    before = cases;
    for (unsigned t = 0; t < 100000; t++) {
        for (unsigned i = 0; i < NTRUPLUS_N; i++) {
            uint32_t span = (uint32_t)(decap_box[i][1] - decap_box[i][0] + 1);
            p.coeffs[i] = (int16_t)(decap_box[i][0] + (int)(random_word() % span));
        }
        if (compare(&p, "box uniform", t)) return 1;
    }
    printf("  %-24s cases=%lu Inverse D == Official bit-exact\n", "box uniform", cases - before);
    before = cases;
    for (unsigned t = 0; t < 50000; t++) {
        for (unsigned i = 0; i < NTRUPLUS_N; i++)
            p.coeffs[i] = decap_box[i][t < 2 ? t : random_word() & 1U];
        if (compare(&p, "box corners", t)) return 1;
    }
    printf("  %-24s cases=%lu Inverse D == Official bit-exact\n", "box corners", cases - before);
    printf("NTRU+%d Inverse D (invntt+crepmod3 fused) == Official crepmod3(invntt) bit-exact differential: "
           "pass (%lu cases, canaries intact, outputs in {-1,0,1})\n", NTRUPLUS_N, cases);
    return 0;
}
