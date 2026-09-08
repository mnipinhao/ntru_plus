#ifndef NTRUPLUS768_TEST_POLY_REFERENCE_H
#define NTRUPLUS768_TEST_POLY_REFERENCE_H

#include "../../poly.h"

/* Test-only generic block-major pair. Basemul retains R^-1; the inverse
 * absorbs that factor. Not the dedicated production Decap interface. */
void poly_basemul(poly *out, const poly *a, const poly *b);
void poly_invntt(poly *out, const poly *in);

#endif
