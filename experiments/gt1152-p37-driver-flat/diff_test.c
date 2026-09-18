/* P37 -- the flattened driver must be bit-identical to the loop-nest driver.
 *
 * Both are linked here and run on the same inputs.  The comparison is over all
 * 1152 output coefficients, exactly, for every case -- not a hash, so a
 * mismatch says which coefficient.
 */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "params.h"
#include "inverse_tables.h"
#include "inverse16_tables.h"

void invntt_ternary_asm(int16_t *, const int16_t *, const int16_t *,
                        const int16_t *, const int16_t *, const int16_t *);
void invntt_ternary_ref(int16_t *, const int16_t *, const int16_t *,
                        const int16_t *, const int16_t *, const int16_t *);

#define ARGS &invntt9_constants[0][0][0][0][0], &invntt16_constants[0][0], \
             &invntt16_main_constants[0][0], &invntt16_tail_constants[0][0]

static int16_t in[NTRUPLUS_N], a[NTRUPLUS_N], b[NTRUPLUS_N];

int main(void)
{
    uint64_t s = 0x9e3779b97f4a7c15ULL;
    long cases = 0, bad = 0;
    const int16_t B = 2497;                 /* the inherited input contract */

    for (int trial = 0; trial < 4000; trial++) {
        for (int i = 0; i < NTRUPLUS_N; i++) {
            s ^= s << 13; s ^= s >> 7; s ^= s << 17;
            if (trial == 0)      in[i] = 0;
            else if (trial == 1) in[i] = B;
            else if (trial == 2) in[i] = -B;
            else if (trial == 3) in[i] = (i & 1) ? B : -B;
            else                 in[i] = (int16_t)((int)(s % (2u * B + 1)) - B);
        }
        memset(a, 0x5a, sizeof a);
        memset(b, 0xa5, sizeof b);
        invntt_ternary_ref(a, in, ARGS);
        invntt_ternary_asm(b, in, ARGS);
        cases++;
        for (int i = 0; i < NTRUPLUS_N; i++)
            if (a[i] != b[i]) {
                if (bad < 5)
                    printf("  trial %d coeff %d: nest %d, flat %d\n",
                           trial, i, a[i], b[i]);
                bad++;
            }
    }
    printf("%ld trials x %d coefficients: %ld mismatches\n",
           cases, NTRUPLUS_N, bad);
    return bad != 0;
}
