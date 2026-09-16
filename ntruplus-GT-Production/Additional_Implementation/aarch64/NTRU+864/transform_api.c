#include "gt864_fr0_basemul_d1.h"
#include "poly.h"

void gt864_forward_poly_ntt_p41_k1_kem_only(int16_t out[864],
                                            const int16_t in[864]);

void gt_d1_poly_ntt(poly *out, const poly *in)
{
    gt864_forward_poly_ntt_p41_k1_kem_only(out->coeffs, in->coeffs);
}

void gt_d1_poly_basemul(poly *out, const poly *a, const poly *b)
{
    gt864_fr0_basemul_d1_neon(out->coeffs, a->coeffs, b->coeffs);
}

void gt_d1_poly_basemul_add(poly *out, const poly *a, const poly *b,
                            const poly *c)
{
    gt864_fr0_basemul_add_d1_neon(out->coeffs, a->coeffs, b->coeffs,
                                  c->coeffs);
}
