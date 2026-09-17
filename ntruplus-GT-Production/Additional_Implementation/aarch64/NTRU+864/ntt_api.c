#include "base.h"
#include "poly.h"

void ntt_asm(int16_t out[864],
                                            const int16_t in[864]);

void poly_ntt(poly *out, const poly *in)
{
    ntt_asm(out->coeffs, in->coeffs);
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
