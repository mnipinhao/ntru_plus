#ifndef GT_KEYGEN_BPQ_CQ_H
#define GT_KEYGEN_BPQ_CQ_H

#include <stdint.h>

#include "poly.h"

/* Internal keygen-only layout contract. These are not generic poly APIs. */
void gt_keygen_ntt_bpq_mul3(poly *out_bpq, const poly *small);
void gt_keygen_ntt_bpq_mul3_add1(poly *out_bpq, const poly *small);

int gt_keygen_baseinv_bpq_to_cq_scaled_r(poly *out_cq,
                                          const poly *in_bpq);
void gt_keygen_basemul_bpq_cq_to_cq_scaled_r(poly *out_cq,
                                              const poly *in_bpq,
                                              const poly *in_cq_scaled_r);

void gt_keygen_tobytes_cq(uint8_t out[NTRUPLUS_POLYBYTES],
                          const poly *in_cq);
void gt_keygen_tobytes_bpq_p1(uint8_t out[NTRUPLUS_POLYBYTES],
                              const poly *in_bpq);

#endif
