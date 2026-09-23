#ifndef NTRUPLUS768_INTERNAL_KEYGEN_H
#define NTRUPLUS768_INTERNAL_KEYGEN_H

#include "layout.h"

/*
 * Keygen-only CQ contract. The generic GT transform remains block-major;
 * this endpoint writes CQ directly for the keygen baseinv/basemul pipeline.
 */
void poly_ntt_keygen_cq(gt_cq_poly *out_cq,
                              const poly *in_coefficients);
/* Inverts every base element of in_cq (CQ).  Returns 1 if some element is not
 * invertible, and then zeroes out_cq; otherwise returns 0 and writes the
 * inverses, scaled by R, in CQ as poly_basemul_keygen_cq_scaled_r expects.
 * Branch-free up to the returned value, which is declassified for TIMECOP. */
int poly_baseinv_keygen_cq_scaled_r(
    gt_cq_poly *out_cq, const gt_cq_poly *in_cq);
void poly_basemul_keygen_cq_scaled_r(
    gt_cq_poly *out_cq, const gt_cq_poly *a_cq,
    const gt_cq_poly *b_scaled_r_cq);
void poly_tobytes_keygen_cq(uint8_t out[NTRUPLUS_POLYBYTES],
                          const gt_cq_poly *in_cq);

#endif
