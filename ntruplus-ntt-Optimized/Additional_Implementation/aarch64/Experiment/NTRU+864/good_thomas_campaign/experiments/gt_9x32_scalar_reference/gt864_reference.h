#ifndef GT864_REFERENCE_H
#define GT864_REFERENCE_H

#include <stdint.h>

#define GT864_Q 3457
#define GT864_N 864
#define GT864_ROWS 9
#define GT864_COLUMNS 32
#define GT864_LEAF_DEGREE 3

void gt864_forward_direct(int16_t out[GT864_N],
                          const int16_t in[GT864_N]);
void gt864_forward(int16_t out[GT864_N], const int16_t in[GT864_N]);
void gt864_inverse(int16_t out[GT864_N], const int16_t in[GT864_N]);
void gt864_basemul(int16_t out[GT864_N], const int16_t a[GT864_N],
                   const int16_t b[GT864_N]);
void gt864_mul(int16_t out[GT864_N], const int16_t a[GT864_N],
               const int16_t b[GT864_N]);
void gt864_schoolbook_mul(int16_t out[GT864_N], const int16_t a[GT864_N],
                          const int16_t b[GT864_N]);

#endif
