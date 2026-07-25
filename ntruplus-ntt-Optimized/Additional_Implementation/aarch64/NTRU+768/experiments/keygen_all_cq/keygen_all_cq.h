#ifndef NTRUPLUS768_EXPERIMENT_KEYGEN_ALL_CQ_H
#define NTRUPLUS768_EXPERIMENT_KEYGEN_ALL_CQ_H

#include "gt/keygen_bpq_cq.h"

/*
 * Experiment-only early-CQ keygen backend. The production BPQ/CQ backend
 * remains the default unless GT_EXPERIMENT_USE_KEYGEN_ALL_CQ is defined.
 */
void gt_experiment_keygen_bpq_to_cq(gt_cq_poly *out_cq,
                                    const gt_bpq_poly *in_bpq);
void gt_experiment_poly_ntt_to_bpq(gt_bpq_poly *out_bpq,
                                   const poly *in_coefficients);
void gt_experiment_poly_ntt_to_cq(gt_cq_poly *out_cq,
                                  const poly *in_coefficients);
int gt_experiment_keygen_baseinv_cq_to_cq_scaled_r(
    gt_cq_poly *out_cq, const gt_cq_poly *in_cq);
void gt_experiment_keygen_basemul_cq_cq_to_cq_scaled_r(
    gt_cq_poly *out_cq, const gt_cq_poly *a_cq,
    const gt_cq_poly *b_scaled_r_cq);

#endif
