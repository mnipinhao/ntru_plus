#ifndef GT864_NATIVE_H
#define GT864_NATIVE_H
#include "poly.h"
/* FR0 R0 -> centered FR0 R0 inverse. Exact alias allowed, partial overlap forbidden.
 * Returns 1 and clears output on noninvertibility, 0 on success. */
int gt864_native_poly_baseinv(poly *out, const poly *in);
/* Decaps FIRST product only: R0 inputs in [0,4095], FR0 R^-1 output.
 * The matching inverse returns centered natural R0. Exact alias supported. */
void gt864_native_basemul_for_inverse(int16_t *out,const int16_t *a,const int16_t *b);
void gt864_native_inverse(poly *out,const poly *in);
#endif
