#ifndef GT32_ENCAP_DATA_GEOMETRY_056_H
#define GT32_ENCAP_DATA_GEOMETRY_056_H

#include <stdint.h>
#include "params.h"

enum geometry_056_profile {
	GEOMETRY_056_CURRENT = 0,
	GEOMETRY_056_SWAP_C_WORK = 1,
	GEOMETRY_056_ROTATE_ONE = 2,
	GEOMETRY_056_PROFILES = 3
};

enum geometry_056_region {
	GEOMETRY_056_CBD = 0,
	GEOMETRY_056_R_PRODUCER = 1,
	GEOMETRY_056_B3 = 2,
	GEOMETRY_056_REGIONS = 3
};

int geometry_056_encap(enum geometry_056_profile profile,
	uint8_t ct[NTRUPLUS_CIPHERTEXTBYTES], uint8_t ss[NTRUPLUS_SSBYTES],
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8]);

long long geometry_056_measure_region(enum geometry_056_profile profile,
	enum geometry_056_region region,
	const uint8_t pk[NTRUPLUS_PUBLICKEYBYTES],
	const uint8_t coins[NTRUPLUS_N / 8]);

#endif
