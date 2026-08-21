#ifndef GT32_ENCAP_ACTIVE_WORKING_SET_057_H
#define GT32_ENCAP_ACTIVE_WORKING_SET_057_H

#include <stdint.h>
#include "params.h"

enum working_set_057_profile {
	WORKING_SET_057_A_FIVE_ACTIVE = 0,
	WORKING_SET_057_B_FOUR_ACTIVE_RESERVED = 1,
	WORKING_SET_057_C_FOUR_ACTIVE_COMPACT = 2,
	WORKING_SET_057_PROFILES = 3
};

int working_set_057_reserved(enum working_set_057_profile profile,
	uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES], uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8]);

int working_set_057_compact(uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES],
	uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8]);

#endif
