#ifndef GT103_CANDIDATE_H
#define GT103_CANDIDATE_H
#include <stdint.h>
void gt103_ntt_ql2_avx2(int16_t *, const int16_t *);
void gt103_basemul_general_ql2_avx2(int16_t *, const int16_t *, const int16_t *);
void gt103_pack_ql2_sum_avx2(uint8_t *, const int16_t *, const int16_t *);
int gt103_encap_ql2(uint8_t *, uint8_t *, const uint8_t *, const uint8_t *);
int gt103_encap_matched_control(uint8_t *,uint8_t *,const uint8_t *,const uint8_t *);
int gt103_encap_matched_candidate(uint8_t *,uint8_t *,const uint8_t *,const uint8_t *);
#endif
