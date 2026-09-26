#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include "poly.h"
#include "reference/poly_reference.h"

static int reference_mod3(int x)
{
    if (x > 1728) x -= 3457;
    if (x < -1728) x += 3457;
    x %= 3;
    if (x > 1) x -= 3;
    if (x < -1) x += 3;
    return x;
}

int main(void)
{
    poly in, out, alias;
    unsigned cases = 0;
    for (int first = -3456; first <= 3456; first += NTRUPLUS_N) {
        for (int i = 0; i < NTRUPLUS_N; ++i) {
            int x = first + i;
            in.coeffs[i] = (int16_t)(x <= 3456 ? x : 3456);
        }
        alias = in;
        poly_crepmod3(&out, &in);
        poly_crepmod3(&alias, &alias);
        for (int i = 0; i < NTRUPLUS_N; ++i) {
            if (out.coeffs[i] != reference_mod3(in.coeffs[i]) ||
                alias.coeffs[i] != out.coeffs[i]) {
                fprintf(stderr, "mod3 mismatch: input=%d actual=%d expected=%d\n",
                        in.coeffs[i], out.coeffs[i], reference_mod3(in.coeffs[i]));
                return 1;
            }
            ++cases;
        }
    }
    for (int i = 0; i < NTRUPLUS_N; ++i) {
        in.coeffs[i] = (int16_t)(i - 384);
        out.coeffs[i] = (int16_t)(384 - i);
    }
    alias = in;
    poly_sub(&alias, &alias, &out);
    for (int i = 0; i < NTRUPLUS_N; ++i)
        if (alias.coeffs[i] != in.coeffs[i] - out.coeffs[i]) return 2;
    printf("support: %u mod3 lanes cover [-3456,3456], out-of-place/alias and sub passed\n", cases);
    return 0;
}
