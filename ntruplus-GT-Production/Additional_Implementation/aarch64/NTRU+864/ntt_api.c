#include "base.h"
#include "poly.h"

void ntt_asm(int16_t out[864], const int16_t in[864], int16_t *scratch);

void poly_ntt(poly *out, const poly *in)
{
    /* Caller-owned so the leaf allocates nothing the caller cannot name, which
     * is how mlkem-native's kernels are arranged.  Not cleared: under the
     * Official-aligned policy this is an assembly working frame, not secret
     * data with a lifetime, and NTRU+768 stopped clearing its equivalent. */
    int16_t scratch[896];

    ntt_asm(out->coeffs, in->coeffs, scratch);
}

void poly_basemul(poly *out, const poly *a, const poly *b)
{
    basemul_asm(out->coeffs, a->coeffs, b->coeffs);
}

void poly_basemul_add(poly *out, const poly *a, const poly *b,
                            const poly *c)
{
    basemul_add_asm(out->coeffs, a->coeffs, b->coeffs,
                                  c->coeffs);
}
