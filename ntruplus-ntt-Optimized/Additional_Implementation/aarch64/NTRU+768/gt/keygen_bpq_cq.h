#ifndef GT_KEYGEN_BPQ_CQ_H
#define GT_KEYGEN_BPQ_CQ_H

#include <stdint.h>

#include "poly.h"

/* Private layouts with the same storage ABI as poly but distinct C types. */
typedef struct {
    poly storage;
} gt_bpq_poly;

typedef struct {
    poly storage;
} gt_cq_poly;

typedef char gt_bpq_poly_size_must_match_poly[
    sizeof(gt_bpq_poly) == sizeof(poly) ? 1 : -1];
typedef char gt_cq_poly_size_must_match_poly[
    sizeof(gt_cq_poly) == sizeof(poly) ? 1 : -1];
#if defined(__STDC_VERSION__) && __STDC_VERSION__ >= 201112L
_Static_assert(_Alignof(gt_bpq_poly) == _Alignof(poly),
               "BPQ storage alignment must match poly");
_Static_assert(_Alignof(gt_cq_poly) == _Alignof(poly),
               "CQ storage alignment must match poly");
#endif

/* Internal keygen-only layout contract. These are not generic poly APIs. */
void gt_keygen_ntt_bpq_mul3(gt_bpq_poly *out_bpq, const poly *small);
void gt_keygen_ntt_bpq_mul3_add1(gt_bpq_poly *out_bpq, const poly *small);

int gt_keygen_baseinv_bpq_to_cq_scaled_r(gt_cq_poly *out_cq,
                                          const gt_bpq_poly *in_bpq);
void gt_keygen_basemul_bpq_cq_to_cq_scaled_r(
    gt_cq_poly *out_cq, const gt_bpq_poly *in_bpq,
    const gt_cq_poly *in_cq_scaled_r);

void gt_keygen_tobytes_cq(uint8_t out[NTRUPLUS_POLYBYTES],
                          const gt_cq_poly *in_cq);
void gt_keygen_tobytes_bpq_p1(uint8_t out[NTRUPLUS_POLYBYTES],
                              const gt_bpq_poly *in_bpq);

#endif
