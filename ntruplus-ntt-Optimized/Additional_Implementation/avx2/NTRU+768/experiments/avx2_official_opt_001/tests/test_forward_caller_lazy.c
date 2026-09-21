#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "poly.h"

void ntruplus768_officialopt_ntt_caller_lazy(poly *);

static uint64_t state = UINT64_C(0x768a1e20260921);
static uint32_t random_word(void) {
    state ^= state << 13;
    state ^= state >> 7;
    state ^= state << 17;
    return (uint32_t)state;
}

static int equivalent(int16_t a, int16_t b) {
    return ((int)a - (int)b) % NTRUPLUS_Q == 0;
}

int main(void) {
    enum { TRIALS = 10003, DOMAINS = 4 };
    struct guarded_poly {
        uint64_t before;
        poly p;
        uint64_t after;
    } candidate;
    poly official;
    for (unsigned domain = 0; domain < DOMAINS; domain++) {
        for (unsigned trial = 0; trial < TRIALS; trial++) {
            int amplitude = domain < 2 ? 3 : domain == 2 ? 1 : 2;
            for (unsigned i = 0; i < NTRUPLUS_N; i++) {
                int16_t value;
                if (trial == 0) value = 0;
                else if (trial == 1) value = (int16_t)((i & 1U) ? -amplitude : amplitude);
                else if (trial < 2U + 2U * NTRUPLUS_N) {
                    value = (i == (trial - 2U) / 2U) ?
                        (int16_t)((trial & 1U) ? -amplitude : amplitude) : 0;
                } else {
                    unsigned width = domain == 3 ? 5U : 3U;
                    int center = (int)(width / 2U);
                    value = (int16_t)((int)(random_word() % width) - center);
                    if (domain == 0 || domain == 1) value = (int16_t)(3 * value);
                }
                official.coeffs[i] = value;
            }
            if (domain == 0) {
                static const int16_t f0_values[3] = {-2, 1, 4};
                official.coeffs[0] = f0_values[trial % 3U];
            }
            candidate.before = UINT64_C(0x526701aa234de096);
            candidate.after = UINT64_C(0xe43d4018ad917c25);
            candidate.p = official;
            poly_ntt(&official);
            ntruplus768_officialopt_ntt_caller_lazy(&candidate.p);
            if (candidate.before != UINT64_C(0x526701aa234de096) ||
                candidate.after != UINT64_C(0xe43d4018ad917c25)) {
                fprintf(stderr, "Forward lazy canary failure domain=%u trial=%u\n", domain, trial);
                return 1;
            }
            for (unsigned i = 0; i < NTRUPLUS_N; i++) {
                if (!equivalent(candidate.p.coeffs[i], official.coeffs[i])) {
                    fprintf(stderr, "Forward lazy residue failure domain=%u trial=%u lane=%u\n",
                            domain, trial, i);
                    return 1;
                }
            }
        }
    }
    puts("Official caller-lazy Forward residue/canary differential: pass (40012 cases)");
    return 0;
}
