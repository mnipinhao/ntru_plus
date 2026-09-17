#ifndef NTRUPLUS_INVERSE_H
#define NTRUPLUS_INVERSE_H
#include "poly.h"
/* FR0 R0 -> centered FR0 R0 inverse. Exact alias allowed.
 * Returns 1 and clears output on noninvertibility, 0 on success. */
int poly_baseinv(poly *out, const poly *in);
/* Decaps FIRST product only: R0 inputs in [0,4095], FR0 R^-1 output,
 * normalized to [-1729,1728] per decision D7. Exact alias supported. */
void poly_basemul_rinv(int16_t *out, const int16_t *a, const int16_t *b);
/* Decapsulation consumer: FR0 R^-1 -> natural ternary. Exact alias. */
void poly_invntt_ternary(poly *out, const poly *in);
#endif
