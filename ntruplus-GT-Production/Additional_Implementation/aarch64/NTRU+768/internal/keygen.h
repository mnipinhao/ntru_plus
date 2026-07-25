#ifndef NTRUPLUS768_INTERNAL_KEYGEN_H
#define NTRUPLUS768_INTERNAL_KEYGEN_H

#include "layout.h"

/*
 * Keygen-only CQ contract. The generic GT transform remains block-major;
 * this endpoint writes CQ directly for the keygen baseinv/basemul pipeline.
 */
void gt_keygen_poly_ntt_to_cq(gt_cq_poly *out_cq,
                              const poly *in_coefficients);
int gt_keygen_baseinv_cq_to_cq_scaled_r(
    gt_cq_poly *out_cq, const gt_cq_poly *in_cq);
void gt_keygen_basemul_cq_cq_to_cq_scaled_r(
    gt_cq_poly *out_cq, const gt_cq_poly *a_cq,
    const gt_cq_poly *b_scaled_r_cq);
void gt_keygen_tobytes_cq(uint8_t out[NTRUPLUS_POLYBYTES],
                          const gt_cq_poly *in_cq);

#endif
