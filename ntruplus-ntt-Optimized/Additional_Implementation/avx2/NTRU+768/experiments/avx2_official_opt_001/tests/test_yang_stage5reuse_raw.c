#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "poly.h"

void ntruplus768_officialopt_invntt_yang_pair32(poly *);
void ntruplus768_officialopt_invntt_yang_stage5reuse(poly *);

static uint64_t state = UINT64_C(0x768c720260923);
static uint32_t random_word(void) {
    state ^= state << 13;
    state ^= state >> 7;
    state ^= state << 17;
    return (uint32_t)state;
}

int main(void) {
    struct guarded { uint64_t before; poly p; uint64_t after; } control, candidate;
    for (unsigned trial = 0; trial < 5003; trial++) {
        for (unsigned i = 0; i < NTRUPLUS_N; i++) {
            int value;
            if (!trial) value = 0;
            else if (trial < 1U + 2U * NTRUPLUS_N)
                value = i == (trial - 1U) / 2U ? ((trial & 1U) ? 1728 : -1728) : 0;
            else if (trial & 1U) value = (int)(random_word() % 15289U) - 7644;
            else value = (int)(random_word() % 3457U) - 1728;
            control.p.coeffs[i] = (int16_t)value;
        }
        control.before = candidate.before = UINT64_C(0x91b0d3025e7a7681);
        control.after = candidate.after = UINT64_C(0x23190921afe8375a);
        candidate.p = control.p;
        ntruplus768_officialopt_invntt_yang_pair32(&control.p);
        ntruplus768_officialopt_invntt_yang_stage5reuse(&candidate.p);
        if (control.before != candidate.before || control.after != candidate.after ||
            control.before != UINT64_C(0x91b0d3025e7a7681) ||
            control.after != UINT64_C(0x23190921afe8375a) ||
            memcmp(&control.p, &candidate.p, sizeof(poly))) {
            fprintf(stderr, "stage5reuse raw/canary mismatch trial=%u\n", trial);
            return 1;
        }
    }
    puts("pair32 vs stage5reuse: 5003 raw bit-exact/canary cases passed");
    return 0;
}
