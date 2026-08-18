#ifndef POLY_H
#define POLY_H

#include <stdint.h>
#include "api.h"
#include "params.h"

/*
 * Elements of R_q = Z_q[X]/(X^n - X^n/2 + 1). Represents polynomial
 * coeffs[0] + X*coeffs[1] + X^2*xoeffs[2] + ... + X^{n-1}*coeffs[n-1]
 */
typedef struct{
	int16_t coeffs[NTRUPLUS_N];
} poly __attribute__((aligned(32)));

NTRUPLUS_INTERNAL NTRUPLUS_SYSV
void poly_cbd1(poly *r, const uint8_t buf[NTRUPLUS_N/4]);
NTRUPLUS_INTERNAL NTRUPLUS_SYSV
void poly_sotp_encode(poly *r, const uint8_t msg[NTRUPLUS_N/8],
                      const uint8_t buf[NTRUPLUS_N/4]);
NTRUPLUS_INTERNAL
int poly_sotp_decode(uint8_t msg[NTRUPLUS_N/8], const poly *a,
                     const uint8_t buf[NTRUPLUS_N/4]);

NTRUPLUS_INTERNAL NTRUPLUS_SYSV
void poly_add(poly *r, const poly *a, const poly *b);
NTRUPLUS_INTERNAL NTRUPLUS_SYSV
void poly_sub(poly *c, const poly *a, const poly *b);
NTRUPLUS_INTERNAL NTRUPLUS_SYSV void poly_triple(poly *r);
NTRUPLUS_INTERNAL NTRUPLUS_SYSV void poly_crepmod3(poly *r);

#endif
