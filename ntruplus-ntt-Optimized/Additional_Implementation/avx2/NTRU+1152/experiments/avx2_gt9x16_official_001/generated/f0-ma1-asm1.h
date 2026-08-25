#ifndef NTRUPLUS1152_EXP001_F0_MA1_ASM1_H
#define NTRUPLUS1152_EXP001_F0_MA1_ASM1_H
#include <stdint.h>
void ntruplus1152_exp001_f0_ma1_asm1_c0(
    uint8_t output[1728], const int16_t r_f0[1152],
    const int16_t m_f0[1152], const int16_t h_official[1152],
    int16_t chunk_scratch[256]);
void ntruplus1152_exp001_f0_ma1_asm1_c1(
    uint8_t output[1728], const int16_t r_f0[1152],
    const int16_t m_f0[1152], const int16_t h_official[1152],
    int16_t chunk_scratch[256]);
#endif
