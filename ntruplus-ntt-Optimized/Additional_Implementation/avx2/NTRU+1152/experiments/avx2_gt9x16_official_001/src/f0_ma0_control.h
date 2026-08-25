#ifndef NTRUPLUS1152_EXP001_F0_MA0_CONTROL_H
#define NTRUPLUS1152_EXP001_F0_MA0_CONTROL_H
#include <stdint.h>
void ntruplus1152_exp001_f0_ma0_control(
    uint8_t output[1728], const int16_t r_f0[1152],
    const int16_t m_f0[1152], const int16_t h_official[1152],
    int16_t scratch[3456]);
#endif
