#ifndef NTRUPLUS768_POLY_H
#define NTRUPLUS768_POLY_H

#include <stdint.h>

#include "params.h"

typedef struct {
    int16_t coeffs[NTRUPLUS_N];
} poly __attribute__((aligned(16)));

/* Canonical encoding of a reduced block-major (Encap) polynomial: the
 * ciphertext boundary.  Key generation packs pk/sk with poly_tobytes_keygen_cq. */
void poly_tobytes_encap(uint8_t out[NTRUPLUS_POLYBYTES], const poly *a);
/*
 * Decode every coefficient and return 1 iff any decoded 12-bit value is
 * outside [0, NTRUPLUS_Q). The output is complete on both return paths.
 */
int poly_frombytes_encap(poly *out,
                   const uint8_t in[NTRUPLUS_POLYBYTES]);

void poly_cbd1(poly *out, const uint8_t buf[NTRUPLUS_N / 4]);
void poly_sotp_encode(poly *out, const uint8_t msg[NTRUPLUS_N / 8],
                      const uint8_t buf[NTRUPLUS_N / 4]);
int poly_sotp_decode(uint8_t msg[NTRUPLUS_N / 8], const poly *a,
                     const uint8_t buf[NTRUPLUS_N / 4]);

/* Encapsulation-only a*b+c endpoint; its result is packed immediately. */
void poly_basemul_add_encap(poly *out, const poly *a, const poly *b,
                      const poly *c);

void poly_sub(poly *out, const poly *a, const poly *b);
void poly_triple(poly *out, const poly *in);
/* Centers modulo q, then modulo 3; input [-3456,3456]. Exact alias allowed.
 * Test oracle: the KEM uses the mod 3 fused into poly_invntt_ternary_decap. */
void poly_crepmod3(poly *out, const poly *in);

#endif
