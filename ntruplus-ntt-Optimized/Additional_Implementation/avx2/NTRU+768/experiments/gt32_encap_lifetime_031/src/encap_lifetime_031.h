#ifndef GT32_ENCAP_LIFETIME_031_H
#define GT32_ENCAP_LIFETIME_031_H

#include <stdint.h>

#include "params.h"

typedef struct {
	int16_t r_hat[NTRUPLUS_N];
	uint8_t r_encoded[NTRUPLUS_POLYBYTES];
	int16_t m_hat[NTRUPLUS_N];
	uint8_t ciphertext[NTRUPLUS_CIPHERTEXTBYTES];
	uint8_t shared_secret[NTRUPLUS_SSBYTES];
} gt32_encap_031_trace;

int gt32_encap_031_control_trace(gt32_encap_031_trace *trace,
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8]);
int gt32_encap_031_candidate_trace(gt32_encap_031_trace *trace,
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8]);
int gt32_encap_lifetime_031(uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8]);

#endif
