/* P68 differential gate: the lane-basis chain must reproduce the production
 * chain bit for bit, for every input in the representative range. */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <stdlib.h>
#include "inverse_tables.h"
#include "inverse16_tables.h"
#include "invntt9_lane_tables.h"

void invntt_ternary_asm(int16_t*, const int16_t*, const int16_t*, const int16_t*,
                        const int16_t*, const int16_t*);
void invntt_ternary_p68_asm(int16_t*, const int16_t*, const int16_t*, const int16_t*,
                            const int16_t*, const int16_t*);

static uint64_t s0 = 0x243f6a8885a308d3ULL;
static uint64_t rnd(void){ s0 ^= s0<<13; s0 ^= s0>>7; s0 ^= s0<<17; return s0; }

int main(int argc, char **argv)
{
    int trials = argc > 1 ? atoi(argv[1]) : 200;
    int16_t in[1152], a[1152], b[1152];
    int bad = 0, first = -1;

    for (int k = 0; k < trials; k++) {
        for (int i = 0; i < 1152; i++) in[i] = (int16_t)(rnd() % 3457) - 1728;
        if (k == 0) for (int i = 0; i < 1152; i++) in[i] = 0;
        if (k == 1) { memset(in, 0, sizeof in); in[0] = 1; }

        invntt_ternary_asm    (a, in, &invntt9_constants[0][0][0][0][0],
                               &invntt16_constants[0][0],
                               &invntt16_main_constants[0][0],
                               &invntt16_tail_constants[0][0]);
        invntt_ternary_p68_asm(b, in, &invntt9_constants_lane[0][0][0][0],
                               &invntt16_constants[0][0],
                               &invntt16_main_constants[0][0],
                               &invntt16_tail_constants[0][0]);

        for (int i = 0; i < 1152; i++)
            if (a[i] != b[i]) { if (first < 0) { first = i;
                fprintf(stderr, "  trial %d coeff %d: production %d, P68 %d\n", k, i, a[i], b[i]); }
                bad++; }
    }
    printf("%s  %d trials, %d mismatching coefficients\n",
           bad ? "FAIL" : "PASS", trials, bad);
    return bad != 0;
}
