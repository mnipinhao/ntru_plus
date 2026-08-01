#ifndef NTRUPLUS768_INTERNAL_DECAP_VERIFY_H
#define NTRUPLUS768_INTERNAL_DECAP_VERIFY_H

#include <stdint.h>

#include "params.h"
#include "poly.h"

/*
 * Checked packed ct/f consumer for the production decapsulation path.
 * It retains ct in Decap QSoA layout and emits the scaled R^-1 product
 * expected by gt_decap_poly_invntt_scale().
 */
int gt_decap_checked_ct_f_basemul_scale64(
    poly *out, poly *decoded_ct,
    const uint8_t packed_ct[NTRUPLUS_POLYBYTES],
    const uint8_t packed_f[NTRUPLUS_POLYBYTES]);

int gt_decap_poly_frombytes(
    poly *out, const uint8_t in[NTRUPLUS_POLYBYTES]);
void gt_decap_poly_tobytes(
    uint8_t out[NTRUPLUS_POLYBYTES], const poly *in);
void gt_decap_poly_basemul(
    poly *out, const poly *a, const poly *b);
void gt_decap_poly_invntt_scale(poly *inout);
void gt_decap_poly_sub(
    poly *out, const poly *a, const poly *b);
void gt_decap_poly_ntt(poly *out, const poly *in);

/* Private decapsulation endpoint with a prevalidated QSoA h^-1 operand. */
void gt_decap_verify_predecoded_qsoa_to_bytes(
    uint8_t out[NTRUPLUS_POLYBYTES], const poly *c_minus_m2,
    const poly *hinv_qsoa);

/* Internal QSoA pointwise kernel used by gt_decap_verify_to_bytes(). */
void gt_decap_verify_pointwise(poly *out_qsoa, const poly *gt_input,
                               const poly *hinv_qsoa);
int qsoa_frombytes(poly *out,
                   const uint8_t in[NTRUPLUS_POLYBYTES]);
void qsoa_tobytes(uint8_t out[NTRUPLUS_POLYBYTES], const poly *in);

#endif
