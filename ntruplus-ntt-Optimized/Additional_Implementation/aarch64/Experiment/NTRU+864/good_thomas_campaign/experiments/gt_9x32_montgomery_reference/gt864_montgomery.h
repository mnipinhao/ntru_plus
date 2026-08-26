#ifndef GT864_MONTGOMERY_H
#define GT864_MONTGOMERY_H

#include <stdint.h>

#include "gt864_reference.h"

void gt864_mont_forward(int16_t out[GT864_N], const int16_t in[GT864_N]);
void gt864_mont_inverse(int16_t out[GT864_N], const int16_t in[GT864_N]);
void gt864_mont_basemul(int16_t out[GT864_N], const int16_t a[GT864_N],
                        const int16_t b[GT864_N]);
void gt864_mont_mul(int16_t out[GT864_N], const int16_t a[GT864_N],
                    const int16_t b[GT864_N]);
void gt864_grid_to_legacy(int16_t out[GT864_N], const int16_t in[GT864_N]);
void gt864_legacy_to_grid(int16_t out[GT864_N], const int16_t in[GT864_N]);

#endif
