#ifndef NTRUPLUS1152_EXP001_ENCAP_H4_M3B_EXACT_EGRESS_H
#define NTRUPLUS1152_EXP001_ENCAP_H4_M3B_EXACT_EGRESS_H
#include <stdint.h>
void ntruplus1152_exp001_gt9x16_prod3_aos_full_wire_monotone_scale1_lazy_reduce(int16_t state[1152]);
int ntruplus1152_exp001_encap_h4_m3b_exact_egress_wire(uint8_t ct[1728], const uint8_t pk[1728],
             const int16_t r_scale1[1152], const int16_t m_scale1[1152],
             int16_t scratch[1152]);
#endif
