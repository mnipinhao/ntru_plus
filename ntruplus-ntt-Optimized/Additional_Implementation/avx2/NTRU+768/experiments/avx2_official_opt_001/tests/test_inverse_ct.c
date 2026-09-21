#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "poly.h"

void ntruplus768_officialopt_invntt_ct(poly *);

static uint64_t state = UINT64_C(0x768c720260921);
static uint32_t random_word(void) {
    state ^= state << 13;
    state ^= state >> 7;
    state ^= state << 17;
    return (uint32_t)state;
}

int main(void) {
    enum { TRIALS = 5003 };
    struct guarded {
        uint64_t before;
        poly p;
        uint64_t after;
    } candidate;
    poly official;
    for (unsigned trial = 0; trial < TRIALS; trial++) {
        for (unsigned i = 0; i < NTRUPLUS_N; i++) {
            int value;
            if (trial == 0) value = 0;
            else if (trial < 2U + 2U * NTRUPLUS_N)
                value = i == (trial - 1U) / 2U ? ((trial & 1U) ? 1728 : -1728) : 0;
            else if (trial & 1U) value = (int)(random_word() % 15289U) - 7644;
            else value = (int)(random_word() % 3457U) - 1728;
            official.coeffs[i] = (int16_t)value;
        }
        candidate.before = UINT64_C(0x91b0d3025e7a7681);
        candidate.after = UINT64_C(0x23190921afe8375a);
        candidate.p = official;
        poly_invntt_scale(&official);
        ntruplus768_officialopt_invntt_ct(&candidate.p);
        if (candidate.before != UINT64_C(0x91b0d3025e7a7681) ||
            candidate.after != UINT64_C(0x23190921afe8375a)) {
            fprintf(stderr, "CT inverse canary failure trial=%u\n", trial);
            return 1;
        }
        for (unsigned i = 0; i < NTRUPLUS_N; i++) {
            if (((int)official.coeffs[i] - (int)candidate.p.coeffs[i]) % NTRUPLUS_Q) {
                fprintf(stderr, "CT inverse residue mismatch trial=%u index=%u official=%d candidate=%d\n",
                        trial, i, official.coeffs[i], candidate.p.coeffs[i]);
                return 1;
            }
        }
        poly_crepmod3(&official);
        poly_crepmod3(&candidate.p);
        if (memcmp(&official, &candidate.p, sizeof(poly))) {
            fprintf(stderr, "CT inverse crepmod3 mismatch trial=%u\n", trial);
            return 1;
        }
    }
    for (unsigned trial = 0; trial < 1003; trial++) {
        poly a, b, input;
        for (unsigned i = 0; i < NTRUPLUS_N; i++) {
            a.coeffs[i] = (int16_t)(random_word() % NTRUPLUS_Q);
            b.coeffs[i] = (int16_t)(random_word() % NTRUPLUS_Q);
        }
        poly_basemul_scale(&input, &a, &b);
        for (unsigned i = 0; i < NTRUPLUS_N; i++) {
            if (input.coeffs[i] < -7644 || input.coeffs[i] > 7644) {
                fprintf(stderr, "BaseMulScale bound violation trial=%u index=%u value=%d\n",
                        trial, i, input.coeffs[i]);
                return 1;
            }
        }
        official = input;
        candidate.p = input;
        poly_invntt_scale(&official);
        ntruplus768_officialopt_invntt_ct(&candidate.p);
        for (unsigned i = 0; i < NTRUPLUS_N; i++) {
            if (((int)official.coeffs[i] - (int)candidate.p.coeffs[i]) % NTRUPLUS_Q) {
                fprintf(stderr, "CT inverse BaseMulScale residue mismatch trial=%u index=%u\n",
                        trial, i);
                return 1;
            }
        }
        poly_crepmod3(&official);
        poly_crepmod3(&candidate.p);
        if (memcmp(&official, &candidate.p, sizeof(poly))) {
            fprintf(stderr, "CT inverse BaseMulScale crepmod3 mismatch trial=%u\n", trial);
            return 1;
        }
    }
    printf("Official vs CT inverse: %d direct and 1003 BaseMulScale residue/crepmod3 cases passed\n", TRIALS);
    return 0;
}
