#ifndef GT32_ENCAP_B3_ADDM_032_H
#define GT32_ENCAP_B3_ADDM_032_H

#include <stdint.h>

#include "params.h"

typedef void (*gt32_032_local_fn)(int16_t out[NTRUPLUS_N],
	const int16_t h[NTRUPLUS_N], const int16_t r[NTRUPLUS_N],
	const int16_t m[NTRUPLUS_N]);

void gt32_032_local_control_normal(int16_t out[NTRUPLUS_N],
	const int16_t h[NTRUPLUS_N], const int16_t r[NTRUPLUS_N],
	const int16_t m[NTRUPLUS_N]);
void gt32_032_local_candidate_normal(int16_t out[NTRUPLUS_N],
	const int16_t h[NTRUPLUS_N], const int16_t r[NTRUPLUS_N],
	const int16_t m[NTRUPLUS_N]);
void gt32_032_local_control_reversed(int16_t out[NTRUPLUS_N],
	const int16_t h[NTRUPLUS_N], const int16_t r[NTRUPLUS_N],
	const int16_t m[NTRUPLUS_N]);
void gt32_032_local_candidate_reversed(int16_t out[NTRUPLUS_N],
	const int16_t h[NTRUPLUS_N], const int16_t r[NTRUPLUS_N],
	const int16_t m[NTRUPLUS_N]);

int gt32_032_encap_control_normal(uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	uint8_t ss[NTRUPLUS_SSBYTES], const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8]);
int gt32_032_encap_candidate_normal(uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	uint8_t ss[NTRUPLUS_SSBYTES], const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8]);
int gt32_032_encap_control_reversed(uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	uint8_t ss[NTRUPLUS_SSBYTES], const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8]);
int gt32_032_encap_candidate_reversed(uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	uint8_t ss[NTRUPLUS_SSBYTES], const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8]);

#endif
