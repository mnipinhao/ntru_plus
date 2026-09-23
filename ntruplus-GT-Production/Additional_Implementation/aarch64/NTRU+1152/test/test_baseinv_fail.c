/* Per-leaf non-invertibility suite for NTRU+1152 baseinv.
 *
 * Owed since G5: NTRU+864 gates this with 808 failure/alias/wipe cases, and
 * until now the 1152 package had only incidental coverage -- a handful of
 * naturally non-invertible inputs and an all-zero transform.
 *
 * A leaf of Z_q[X]/(X^4 - zeta) is non-invertible exactly when its norm
 * t0^2 - t1*t2 vanishes.  The cheapest witness is the zero leaf, so this walks
 * every one of the 288 leaves, zeroes it inside an otherwise invertible
 * polynomial, and requires rejection with a fully cleared output -- then does
 * the same through an exact out==in alias.
 */
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include "poly.h"
#include "inverse.h"

static uint32_t s = 20260917u;
static uint32_t rnd(void) { s ^= s << 13; s ^= s >> 17; s ^= s << 5; return s; }

int main(void)
{
    static poly base, in, out;
    int leaves = 0, rejected = 0, cleared = 0, alias_ok = 0, wrong = 0;

    /* Find an invertible starting point. */
    for (int attempt = 0; attempt < 64; attempt++) {
        for (int i = 0; i < NTRUPLUS_N; i++)
            base.coeffs[i] = (int16_t)(rnd() % 3457);
        if (poly_baseinv(&out, &base) == 0)
            break;
        if (attempt == 63) { printf("FAIL: no invertible base found\n"); return 1; }
    }

    /* Each leaf occupies four lanes at GT stride 8 inside its 32-int16 group. */
    for (int group = 0; group < 36; group++) {
        for (int lane = 0; lane < 8; lane++) {
            int b = 32 * group + lane;

            memcpy(&in, &base, sizeof in);
            for (int c = 0; c < 4; c++)
                in.coeffs[b + 8 * c] = 0;
            leaves++;

            memset(&out, 0x5a, sizeof out);
            if (poly_baseinv(&out, &in) != 1) { wrong++; continue; }
            rejected++;

            int nonzero = 0;
            for (int i = 0; i < NTRUPLUS_N; i++)
                nonzero |= out.coeffs[i];
            if (nonzero == 0) cleared++;

            /* Exact alias: the same rejection must clear in place. */
            memcpy(&out, &in, sizeof out);
            if (poly_baseinv(&out, &out) == 1) {
                nonzero = 0;
                for (int i = 0; i < NTRUPLUS_N; i++)
                    nonzero |= out.coeffs[i];
                if (nonzero == 0) alias_ok++;
            }
        }
    }

    printf("leaves probed      %d\n", leaves);
    printf("rejected with 1    %d\n", rejected);
    printf("output cleared     %d\n", cleared);
    printf("alias also cleared %d\n", alias_ok);

    if (leaves != 288 || rejected != 288 || cleared != 288 || alias_ok != 288 || wrong) {
        printf("FAIL\n");
        return 1;
    }
    printf("PASS: every one of the 288 leaves rejects and clears, aliased and not\n");
    return 0;
}
