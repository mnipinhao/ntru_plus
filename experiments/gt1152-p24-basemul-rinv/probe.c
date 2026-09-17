/* Does basemul_rinv's pre-normalization output really stay inside +/-2752? */
#include <stdio.h>
#include <stdint.h>
#include <arm_neon.h>
#include "poly.h"

int  probe_pre = 0, probe_post = 0;
int16x8_t probe_normalize(int16x8_t a);

void basemul_rinv_asm(int16_t*, const int16_t*, const int16_t*);

static uint64_t s = 0x9E3779B97F4A7C15ull;
static uint64_t rnd(void){ s^=s<<13; s^=s>>7; s^=s<<17; return s; }

int main(void){
    static int16_t a[NTRUPLUS_N], b[NTRUPLUS_N], o[NTRUPLUS_N];
    for (int trial = 0; trial < 20000; trial++) {
        int mode = trial % 3;
        for (int i = 0; i < NTRUPLUS_N; i++) {
            if (mode == 0)      { a[i] = (int16_t)(rnd() % 4096); b[i] = (int16_t)(rnd() % 4096); }
            else if (mode == 1) { a[i] = 4095; b[i] = 4095; }
            else                { a[i] = (int16_t)((rnd()&1) ? 4095 : 0); b[i] = (int16_t)((rnd()&1) ? 4095 : 0); }
        }
        basemul_rinv_asm(o, a, b);
    }
    printf("20000 trials, inputs in [0,4095] per the declared contract\n");
    printf("  max |pre-normalization|  %5d   (G2 bound 2752, must not exceed 1728+q=5185)\n", probe_pre);
    printf("  max |post-normalization| %5d   (D7 contract 2497; Barrett gave 1729)\n", probe_post);
    return !(probe_pre <= 2752 && probe_post <= 1728);
}
