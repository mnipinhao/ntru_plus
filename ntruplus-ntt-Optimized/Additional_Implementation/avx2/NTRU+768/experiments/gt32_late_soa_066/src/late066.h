#ifndef GT32_LATE_SOA_066_H
#define GT32_LATE_SOA_066_H

#include <stdint.h>

#include "params.h"

typedef struct __attribute__((aligned(64))) {
	int16_t product[NTRUPLUS_N];
	int16_t post_i1[NTRUPLUS_N];
	int16_t inverse_rows[NTRUPLUS_N];
} late066_region_scratch;

void late066_inverse_prefix_m_to_post_i1_asm(
	int16_t out[NTRUPLUS_N], const int16_t in[NTRUPLUS_N]);

void late066_post_i1_control(int16_t out[NTRUPLUS_N],
	const int16_t c[NTRUPLUS_N], const int16_t f[NTRUPLUS_N],
	late066_region_scratch *scratch);
void late066_post_i1_candidate(int16_t out[NTRUPLUS_N],
	const int16_t c[NTRUPLUS_N], const int16_t f[NTRUPLUS_N],
	late066_region_scratch *scratch);
void late066_crep_control(int16_t out[NTRUPLUS_N],
	const int16_t c[NTRUPLUS_N], const int16_t f[NTRUPLUS_N],
	late066_region_scratch *scratch);
void late066_crep_candidate(int16_t out[NTRUPLUS_N],
	const int16_t c[NTRUPLUS_N], const int16_t f[NTRUPLUS_N],
	late066_region_scratch *scratch);

int late066_decode_crep_control(int16_t out[NTRUPLUS_N],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);
int late066_decode_crep_candidate(int16_t out[NTRUPLUS_N],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);
int late066_recover_only_control(uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);
int late066_recover_only_candidate(uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);

int late066_dec_control(uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);
int late066_dec_candidate(uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);

int late066_recover_trace_control(uint8_t msg[NTRUPLUS_N / 8],
	uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);
int late066_recover_trace_candidate(uint8_t msg[NTRUPLUS_N / 8],
	uint8_t recovered_r[NTRUPLUS_POLYBYTES],
	const uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	const uint8_t sk[NTRUPLUS_SECRETKEYBYTES]);

void late_soa_full_basemul_i2_fused_asm(int16_t out[NTRUPLUS_N],
	const int16_t a[NTRUPLUS_N], const int16_t b[NTRUPLUS_N]);
void gt32_tile4_attr_inverse_i1_cross3_asm(int16_t out[NTRUPLUS_N],
	const int16_t in[NTRUPLUS_N]);

#endif
