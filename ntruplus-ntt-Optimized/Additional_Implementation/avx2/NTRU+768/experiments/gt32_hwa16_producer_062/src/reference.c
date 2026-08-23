#include "producer.h"

#include <string.h>

void hwa16_from_tile4(int16_t out[PRODUCER062_TILE_WORDS],
	const int16_t in[PRODUCER062_TILE_WORDS])
{
	int16_t tmp[PRODUCER062_TILE_WORDS];
	for (unsigned c = 0; c < 4; ++c)
		for (unsigned q = 0; q < 32; ++q)
			tmp[32U * c + q] =
				in[16U * (q / 4U) + 4U * (q % 4U) + c];
	memcpy(out, tmp, sizeof(tmp));
}

void hwa16_to_tile4(int16_t out[PRODUCER062_TILE_WORDS],
	const int16_t in[PRODUCER062_TILE_WORDS])
{
	int16_t tmp[PRODUCER062_TILE_WORDS];
	for (unsigned c = 0; c < 4; ++c)
		for (unsigned q = 0; q < 32; ++q)
			tmp[16U * (q / 4U) + 4U * (q % 4U) + c] =
				in[32U * c + q];
	memcpy(out, tmp, sizeof(tmp));
}
