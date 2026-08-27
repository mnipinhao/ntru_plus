#ifndef GT105_CANDIDATE_H
#define GT105_CANDIDATE_H
#include <stdint.h>
void gt103_ntt_ql2_avx2(int16_t *out,const int16_t *in);
void gt103_basemul_general_ql2_avx2(int16_t *out,const int16_t *a,
	const int16_t *b);
void gt103_pack_ql2_sum_avx2(uint8_t *out,const int16_t *product,
	const int16_t *message);
void gt105_b3_ql2_virtual_pack_avx2(int16_t *scratch,const int16_t *h,
	const int16_t *r,const int16_t *message,uint8_t *ct);
void gt105_b3_ql2_virtual_pack_direct_avx2(int16_t *scratch,const int16_t *h,
	const int16_t *r,const int16_t *message,uint8_t *ct);
int gt105_encap_virtual(uint8_t *ct,uint8_t *ss,const uint8_t *pk,
	const uint8_t *coins);
int gt105_encap_virtual_direct(uint8_t *ct,uint8_t *ss,const uint8_t *pk,
	const uint8_t *coins);
#endif
