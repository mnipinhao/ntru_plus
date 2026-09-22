#ifndef NTRUPLUS768_INTERNAL_DECAP_VERIFY_H
#define NTRUPLUS768_INTERNAL_DECAP_VERIFY_H

#include <stdint.h>

#include "params.h"
#include "poly.h"

/*
 * Checked packed ct/f consumer for the production decapsulation path.
 * It retains ct in Decap QSoA layout and emits the scaled R^-1 product,
 * element-major per group, expected by poly_invntt_ternary_decap().
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

/* Working area of poly_invntt_ternary_decap: three row buffers + one stripe. */
#define POLY_INVNTT_TERNARY_DECAP_SCRATCHBYTES 2048

/*
 * Good-Thomas inverse of the first decapsulation product fused with the
 * centered mod-3 map: in place, output in {-1,0,1}, equal to poly_crepmod3
 * of the exact inverse.  scratch is caller-owned and holds secret
 * intermediates on return; the caller must clear it.
 */
void poly_invntt_ternary_decap(
    poly *inout, uint8_t scratch[POLY_INVNTT_TERNARY_DECAP_SCRATCHBYTES]);

/* Decap-only signed [-2,2] input (both KEM callers are ternary).
 * Top-split quotient is exactly zero; output remains Decap QSoA.
 * This is not an arbitrary-coefficient Forward entry. */
void poly_ntt_decap(poly *out, const poly *in);

#endif
