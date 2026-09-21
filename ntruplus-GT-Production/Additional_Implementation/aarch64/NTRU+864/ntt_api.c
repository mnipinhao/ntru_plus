#include "base.h"
#include "poly.h"
#include "secure_clear.h"

void ntt_asm(int16_t out[864], const int16_t in[864], int16_t *scratch);

void poly_ntt(poly *out, const poly *in)
{
    /* The leaf works out of this buffer and allocates none of its own, so the
     * transform of f, g and the recovered message is reachable from C and is
     * cleared here.  It previously allocated 1792 bytes itself and cleared
     * nothing, where NTRU+768's asm/ntt.S has cleared its equivalent since P0. */
    int16_t scratch[896];

    ntt_asm(out->coeffs, in->coeffs, scratch);
    secure_clear(scratch, sizeof scratch);
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
