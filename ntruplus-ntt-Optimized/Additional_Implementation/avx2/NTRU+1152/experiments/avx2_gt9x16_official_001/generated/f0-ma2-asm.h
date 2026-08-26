#ifndef NTRUPLUS1152_EXP001_F0_MA2_ASM_H
#define NTRUPLUS1152_EXP001_F0_MA2_ASM_H
#include <stdint.h>
void ntruplus1152_exp001_f0_ma2_asm0_b0p0(
    int16_t out[64], const int16_t r[64], const int16_t m[64],
    const int16_t h[1152]);
void ntruplus1152_exp001_f0_ma2_chunk0(
    uint8_t out[192], const int16_t r[1152], const int16_t m[1152],
    const int16_t h[1152], int16_t plane_scratch[128]);
void ntruplus1152_exp001_f0_ma2_full(
    uint8_t out[1728], const int16_t r[1152], const int16_t m[1152],
    const int16_t h[1152], int16_t plane_scratch[128]);
void ntruplus1152_exp001_f0_ma2_native_full(
    uint8_t out[1728], const int16_t r_planes[1152],
    const int16_t m_planes[1152], const int16_t h[1152],
    int16_t plane_scratch[128]);
#endif
