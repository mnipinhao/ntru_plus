#ifndef NTRUPLUS1152_EXP001_H_DECODE_NATURAL_Q_ASM_H
#define NTRUPLUS1152_EXP001_H_DECODE_NATURAL_Q_ASM_H
#include <stdint.h>
int ntruplus1152_exp001_poly_frombytes_h_natural_q(int16_t out[1152], const uint8_t pk[1728]);
void ntruplus1152_exp001_f0_ma2_planes_natural_q_scale4_preprojected_h(int16_t out[1152], const int16_t r[1152], const int16_t m[1152], const int16_t h_natural[1152]);
#endif
