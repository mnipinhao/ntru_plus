#ifndef NTRUPLUS768_POLY_H
#define NTRUPLUS768_POLY_H

#include <stdint.h>

#include "params.h"

typedef struct {
    int16_t coeffs[NTRUPLUS_N];
} poly __attribute__((aligned(16)));

/* Canonical public-key, secret-key, and ciphertext byte boundary. */
void poly_tobytes(uint8_t out[NTRUPLUS_POLYBYTES], const poly *a);
void poly_frombytes(poly *out,
                    const uint8_t in[NTRUPLUS_POLYBYTES]);

void poly_cbd1(poly *out, const uint8_t buf[NTRUPLUS_N / 4]);
void poly_sotp_encode(poly *out, const uint8_t msg[NTRUPLUS_N / 8],
                      const uint8_t buf[NTRUPLUS_N / 4]);
int poly_sotp_decode(uint8_t msg[NTRUPLUS_N / 8], const poly *a,
                     const uint8_t buf[NTRUPLUS_N / 4]);

void poly_ntt(poly *out, const poly *in);

/*
 * The production decapsulation pair keeps one R^-1 factor after basemul and
 * absorbs it in the inverse transform's final constants.
 */
void poly_basemul(poly *out, const poly *a, const poly *b);
void poly_invntt(poly *out, const poly *in);

/* Encapsulation-only a*b+c endpoint; its result is packed immediately. */
void poly_basemul_add(poly *out, const poly *a, const poly *b,
                      const poly *c);

void poly_sub(poly *out, const poly *a, const poly *b);
void poly_triple(poly *out, const poly *in);
void poly_crepmod3(poly *out, const poly *in);

#endif
