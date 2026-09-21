#ifndef NTRUPLUS768_INTERNAL_KEYGEN_H
#define NTRUPLUS768_INTERNAL_KEYGEN_H

#include "layout.h"

/*
 * Keygen-only CQ contract. The generic GT transform remains block-major;
 * this endpoint writes CQ directly for the keygen baseinv/basemul pipeline.
 */
void poly_ntt_keygen_cq(gt_cq_poly *out_cq,
                              const poly *in_coefficients);
int poly_baseinv_keygen_cq_scaled_r(
    gt_cq_poly *out_cq, const gt_cq_poly *in_cq);
void poly_basemul_keygen_cq_scaled_r(
    gt_cq_poly *out_cq, const gt_cq_poly *a_cq,
    const gt_cq_poly *b_scaled_r_cq);
void poly_tobytes_keygen_cq(uint8_t out[NTRUPLUS_POLYBYTES],
                          const gt_cq_poly *in_cq);

#endif
