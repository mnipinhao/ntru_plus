#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "internal/ntt.h"
static uint32_t state = 123;
static uint32_t next(void) {
    state ^= state << 13; state ^= state >> 17; state ^= state << 5;
    return state;
}
int main(void) {
    poly in, generic, small, alias;
    for (int n = 0; n < 4096; n++) {
        int16_t *v = (int16_t *)&in;
        for (int i = 0; i < 768; i++)
            v[i] = n < 5 ? n - 2 : (int)(next() % 5) - 2;
        gt_internal_poly_ntt_loose(&generic, &in);
        gt_internal_poly_ntt_encap_small(&small, &in);
        if (memcmp(&generic, &small, sizeof generic)) return 1;
        alias = in;
        gt_internal_poly_ntt_encap_small(&alias, &alias);
        if (memcmp(&generic, &alias, sizeof generic)) return 2;
    }
    puts("4096 signed [-2,2] exact/alias Encap-small cases: PASS");
    return 0;
}
