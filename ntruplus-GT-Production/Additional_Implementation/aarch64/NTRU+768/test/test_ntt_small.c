#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "encap.h"
#include "reference/poly_reference.h"
static uint32_t state = 123;
static uint32_t next(void) {
    state ^= state << 13; state ^= state >> 17; state ^= state << 5;
    return state;
}
int main(void) {
    poly in, generic, small, alias, lazy;
    uint8_t a[1152], b[1152];
    for (int n = 0; n < 4096; n++) {
        int16_t *v = (int16_t *)&in;
        for (int i = 0; i < 768; i++)
            v[i] = n < 5 ? n - 2 : (int)(next() % 5) - 2;
        poly_ntt_loose(&generic, &in);
        poly_ntt_encap_small(&small, &in);
        if (memcmp(&generic, &small, sizeof generic)) return 1;
        alias = in;
        poly_ntt_encap_small(&alias, &alias);
        if (memcmp(&generic, &alias, sizeof generic)) return 2;
        poly_ntt_encap_small_lazy(&lazy, &in);
        alias=in; poly_ntt_encap_small_lazy(&alias,&alias);
        if (memcmp(&alias,&lazy,sizeof lazy)) return 3;
        for(int i=0;i<768;i++) {
            int x=lazy.coeffs[i];
            if(x < -21050 || x > 21050 || (x-generic.coeffs[i])%3457) return 4;
        }
        poly_tobytes_encap_loose(a,&generic);
        poly_tobytes_encap_loose(b,&lazy);
        if(memcmp(a,b,sizeof a)) return 5;
    }
    puts("4096 signed [-2,2] exact/alias plus lazy modular/range/pack cases: PASS");
    return 0;
}
