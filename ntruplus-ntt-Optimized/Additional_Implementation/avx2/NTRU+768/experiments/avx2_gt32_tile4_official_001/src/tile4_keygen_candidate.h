#ifndef GT32_TILE4_KEYGEN_CANDIDATE_H
#define GT32_TILE4_KEYGEN_CANDIDATE_H

#include <stdint.h>

#include "api.h"

int crypto_kem_keypair_gt32_production_candidate(
	uint8_t pk[CRYPTO_PUBLICKEYBYTES],
	uint8_t sk[CRYPTO_SECRETKEYBYTES]);

#endif
