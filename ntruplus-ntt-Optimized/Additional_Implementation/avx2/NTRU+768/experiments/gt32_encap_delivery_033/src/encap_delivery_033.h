#ifndef GT32_ENCAP_DELIVERY_033_H
#define GT32_ENCAP_DELIVERY_033_H

#include <stdint.h>

#include "params.h"

void gt32_033_b3_addm(int16_t out[NTRUPLUS_N],
	const int16_t h[NTRUPLUS_N], const int16_t r[NTRUPLUS_N],
	const int16_t m[NTRUPLUS_N]);

int gt32_encap_delivery_033(uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	uint8_t ss[NTRUPLUS_SSBYTES], const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8]);

#endif
