#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "poly.h"

void ntruplus768_officialopt_invntt_ct_cohort(poly *);
void ntruplus768_officialopt_invntt_ct_wresident(poly *);
void ntruplus768_officialopt_invntt_ct_earlynorm(poly *);

static uint64_t state = UINT64_C(0x768c720260921);
static uint32_t random_word(void) {
    state ^= state << 13;
    state ^= state >> 7;
    state ^= state << 17;
    return (uint32_t)state;
}

int main(void) {
    struct guarded {
        uint64_t before;
        poly value;
        uint64_t after;
    } control, wresident, earlynorm;
    for (unsigned trial = 0; trial < 5003; trial++) {
        for (unsigned i = 0; i < NTRUPLUS_N; i++) {
            int value;
            if (trial == 0) value = 0;
            else if (trial < 2U + 2U * NTRUPLUS_N)
                value = i == (trial - 1U) / 2U ? ((trial & 1U) ? 1728 : -1728) : 0;
            else if (trial & 1U) value = (int)(random_word() % 15289U) - 7644;
            else value = (int)(random_word() % 3457U) - 1728;
            control.value.coeffs[i] = (int16_t)value;
        }
        control.before = wresident.before = earlynorm.before = UINT64_C(0x91b0d3025e7a7681);
        control.after = wresident.after = earlynorm.after = UINT64_C(0x23190921afe8375a);
        wresident.value = earlynorm.value = control.value;
        ntruplus768_officialopt_invntt_ct_cohort(&control.value);
        ntruplus768_officialopt_invntt_ct_wresident(&wresident.value);
        ntruplus768_officialopt_invntt_ct_earlynorm(&earlynorm.value);
        if (control.before != UINT64_C(0x91b0d3025e7a7681) ||
            control.after != UINT64_C(0x23190921afe8375a) ||
            wresident.before != control.before || wresident.after != control.after ||
            earlynorm.before != control.before || earlynorm.after != control.after ||
            memcmp(&control.value, &wresident.value, sizeof(poly)) ||
            memcmp(&control.value, &earlynorm.value, sizeof(poly))) {
            fprintf(stderr, "CT control raw/canary mismatch trial=%u\n", trial);
            return 1;
        }
    }
    puts("CT cohort vs wresident/earlynorm: 5003 raw bit-exact cases passed");
    return 0;
}
