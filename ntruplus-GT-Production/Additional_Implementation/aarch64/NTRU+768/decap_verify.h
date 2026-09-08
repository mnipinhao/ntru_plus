#ifndef NTRUPLUS768_INTERNAL_DECAP_VERIFY_H
#define NTRUPLUS768_INTERNAL_DECAP_VERIFY_H

#include <stdint.h>

#include "params.h"
#include "poly.h"

/*
 * Checked packed ct/f consumer for the production decapsulation path.
 * It retains ct in Decap QSoA layout and emits the scaled R^-1 product
 * expected by poly_invntt_decap_scale().
 */
int poly_frombytes_basemul_decap_scale(
    poly *out, poly *decoded_ct,
    const uint8_t packed_ct[NTRUPLUS_POLYBYTES],
    const uint8_t packed_f[NTRUPLUS_POLYBYTES]);

int poly_frombytes_decap(
    poly *out, const uint8_t in[NTRUPLUS_POLYBYTES]);
void poly_tobytes_decap(
    uint8_t out[NTRUPLUS_POLYBYTES], const poly *in);
void poly_basemul_decap(
    poly *out, const poly *a, const poly *b);
void poly_invntt_decap_scale(poly *inout);
void poly_ntt_decap(poly *out, const poly *in);

#endif
