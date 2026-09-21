#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "poly.h"

void ntruplus768_officialopt_ntt_early_const(poly *);

static uint64_t random_state = UINT64_C(0x76820260921a7d3f);
static uint32_t next_word(void) {
    random_state ^= random_state << 13;
    random_state ^= random_state >> 7;
    random_state ^= random_state << 17;
    return (uint32_t)random_state;
}

int main(void) {
    poly official, candidate;
    struct { uint64_t before; poly state; uint64_t after; } guarded;
    for (unsigned trial = 0; trial < 10003; trial++) {
        for (unsigned i = 0; i < NTRUPLUS_N; i++) {
            if (trial < 2) official.coeffs[i] = (int16_t)(trial ? (i & 1U ? -3 : 3) : 0);
            else if (trial < 2U+2U*NTRUPLUS_N)
                official.coeffs[i] = (i == (trial-2U)/2U) ?
                    (int16_t)((trial & 1U) ? -3 : 3) : 0;
            else if (trial & 1U)
                official.coeffs[i] = (int16_t)((int)(next_word()%3U)-1);
            else
                official.coeffs[i] = (int16_t)(3*((int)(next_word()%3U)-1));
        }
        if (trial & 2U) official.coeffs[0] = 4;
        candidate = official;
        guarded.before = UINT64_C(0x71761a8d910c2e7b);
        guarded.after = UINT64_C(0xd400997a225ef128);
        guarded.state = candidate;
        poly_ntt(&official);
        ntruplus768_officialopt_ntt_early_const(&guarded.state);
        if (memcmp(&official, &guarded.state, sizeof official) ||
            guarded.before != UINT64_C(0x71761a8d910c2e7b) ||
            guarded.after != UINT64_C(0xd400997a225ef128)) {
            fprintf(stderr, "Forward schedule raw mismatch trial=%u\n", trial);
            return 1;
        }
    }
    puts("Official Forward early-constant raw differential: pass (10003 cases)");
    return 0;
}
