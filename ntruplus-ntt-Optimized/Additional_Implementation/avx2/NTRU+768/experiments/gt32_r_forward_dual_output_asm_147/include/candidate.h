#ifndef GT147_CANDIDATE_H
#define GT147_CANDIDATE_H

#include <stdint.h>

void gt147_ntt_m_wire_avx2(int16_t m[768], const int16_t frontend[768],
                           uint8_t wire[1152]);

#endif

