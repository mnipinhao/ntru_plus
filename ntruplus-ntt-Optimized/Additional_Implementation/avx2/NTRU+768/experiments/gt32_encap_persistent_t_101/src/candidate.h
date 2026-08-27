#ifndef GT101_CANDIDATE_H
#define GT101_CANDIDATE_H
#include <stdint.h>
#include "params.h"
void gt101_ntt_t_avx2(int16_t *, const int16_t *);
void gt101_pack_t_avx2(uint8_t *, const int16_t *);
void gt101_basemul_general_m_t_avx2(int16_t *, const int16_t *, const int16_t *);
int gt101_encap_t(uint8_t *, uint8_t *, const uint8_t *, const uint8_t *);
#endif

