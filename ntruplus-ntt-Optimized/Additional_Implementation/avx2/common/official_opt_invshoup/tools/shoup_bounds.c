/*
 * Exhaustive per-term bounds for the Shoup BaseMul range proof (prove_basemul_shoup.py).
 * Instruction semantics exactly as AVX2 (vpmullw low 16 bits signed, vpmulhrsw
 * (x*y + 2^14) >> 15 truncated to 16 bits, vpmulhuw unsigned high 16 bits, vpsllw).
 *
 * stdin commands, one per line, one output line each:
 *   B amin amax cu        data term  a*b - q*mulhrs(a, mulhu(16b, cu)),  a in [amin, amax], b in [0, q)
 *                         -> "B tmin tmax overflow"
 *   Z smin smax z zc      zeta term  s*z - q*mulhrs(s, zc),              s in [smin, smax]
 *                         -> "Z tmin tmax overflow"
 * The term is the exact integer (64-bit), and overflow counts the cases in which it is
 * not an int16 or differs from the machine value lo16(a*b) - lo16(q*quotient) read as
 * int16 (never expected; both are reported).
 */
#include <stdint.h>
#include <stdio.h>

#define Q 3457

static int16_t mulhrs(int16_t a, int16_t b) { return (int16_t)(((int32_t)a * b + (1 << 14)) >> 15); }
static uint16_t mulhu(uint16_t a, uint16_t b) { return (uint16_t)(((uint32_t)a * b) >> 16); }

static void term(int32_t a, int32_t b, int16_t quot, long *mn, long *mx, long *ov) {
    long t = (long)a * b - (long)Q * quot;
    int16_t machine = (int16_t)((int16_t)(a * b) - (int16_t)(Q * quot));
    if (t < -32768 || t > 32767 || machine != t) (*ov)++;
    if (t < *mn) *mn = t;
    if (t > *mx) *mx = t;
}

int main(void) {
    char c;
    long x0, x1, x2, x3;
    while (scanf(" %c", &c) == 1) {
        long mn = 1L << 40, mx = -(1L << 40), ov = 0;
        if (c == 'B') {
            if (scanf("%ld %ld %ld", &x0, &x1, &x2) != 3) return 2;
            for (int32_t b = 0; b < Q; b++) {
                uint16_t comp = mulhu((uint16_t)(b << 4), (uint16_t)x2);
                for (long a = x0; a <= x1; a++)
                    term((int32_t)a, b, mulhrs((int16_t)a, (int16_t)comp), &mn, &mx, &ov);
            }
            printf("B %ld %ld %ld\n", mn, mx, ov);
        } else if (c == 'Z') {
            if (scanf("%ld %ld %ld %ld", &x0, &x1, &x2, &x3) != 4) return 2;
            for (long s = x0; s <= x1; s++)
                term((int32_t)s, (int32_t)x2, mulhrs((int16_t)s, (int16_t)x3), &mn, &mx, &ov);
            printf("Z %ld %ld %ld\n", mn, mx, ov);
        } else {
            return 2;
        }
        fflush(stdout);
    }
    return 0;
}
