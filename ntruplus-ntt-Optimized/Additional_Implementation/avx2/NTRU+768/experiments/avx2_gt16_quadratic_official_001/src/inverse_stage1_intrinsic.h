#ifndef ROUND4C_INVERSE_STAGE1_INTRINSIC_H
#define ROUND4C_INVERSE_STAGE1_INTRINSIC_H

#include <stdint.h>

void round4c_inverse_stage1_i0(int16_t out[768], const int16_t quadratic[768]);
void round4c_inverse_stage1_i1(int16_t out[768], const int16_t quadratic[768]);
void round4c_inverse_ntt16_i0(int16_t out[768], const int16_t quadratic[768]);
void round4c_inverse_ntt16_i1(int16_t out[768], const int16_t quadratic[768]);
void round4c_inverse_full_i0(int16_t out[768], const int16_t quadratic[768]);

#endif
