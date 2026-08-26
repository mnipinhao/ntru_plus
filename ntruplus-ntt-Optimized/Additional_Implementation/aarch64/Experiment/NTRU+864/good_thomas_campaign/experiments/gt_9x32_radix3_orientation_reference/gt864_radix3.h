#ifndef GT864_RADIX3_H
#define GT864_RADIX3_H

#include <stdint.h>

#include "gt864_montgomery.h"

/*
 * Experimental forward transform with the same public representation as
 * gt864_mont_forward(), but with its nine-point stage expressed as two levels
 * of radix-3 butterflies using the reduced-constant orientation.
 */
void gt864_radix3_forward(int16_t out[GT864_N],
                          const int16_t in[GT864_N]);

/* Full reference product using radix3_forward and the frozen GT basemul/inverse. */
void gt864_radix3_mul(int16_t out[GT864_N], const int16_t a[GT864_N],
                      const int16_t b[GT864_N]);

#endif
