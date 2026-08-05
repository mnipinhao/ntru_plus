#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "tile4.h"

#define GT_QINV 12929
#define GT_R (-147)

static const int16_t omega32_mont[32] = {
	-147, 484, -794, 874, 109, 864, -446, -554,
	366, -429, -1339, 11, -1118, 177, 1181, 1591,
	147, -484, 794, -874, -109, -864, 446, 554,
	-366, 429, 1339, -11, 1118, -177, -1181, -1591
};

static int16_t signed_high16(int32_t value)
{
	return (int16_t)(value >> 16);
}

static int16_t factor_qinv(int16_t factor)
{
	return (int16_t)(uint16_t)((uint32_t)(uint16_t)factor * GT_QINV);
}

static int16_t montgomery_fixed(int16_t value, int16_t factor)
{
	const int16_t low = (int16_t)(uint16_t)((uint32_t)(uint16_t)value
		* (uint32_t)(uint16_t)factor_qinv(factor));
	const int16_t high = signed_high16((int32_t)value * factor);
	const int16_t correction = signed_high16((int32_t)low * GT32_TILE4_Q);

	return (int16_t)(high - correction);
}

static unsigned bitreverse(unsigned value, unsigned bits)
{
	unsigned result = 0;

	for (unsigned i = 0; i < bits; i++) {
		result = (result << 1) | (value & 1U);
		value >>= 1;
	}
	return result;
}

static unsigned forward_power(unsigned stage, unsigned group_start)
{
	if (stage == 1U) {
		return 0;
	}
	return bitreverse(group_start >> (6U - stage), stage - 1U)
		<< (5U - stage);
}

static void forward_one_coefficient(int16_t value[32])
{
	for (unsigned stage = 1; stage <= 5; stage++) {
		const unsigned distance = 32U >> stage;
		for (unsigned group = 0; group < 32; group += 2U * distance) {
			const int16_t factor = omega32_mont[forward_power(stage, group)];
			for (unsigned j = 0; j < distance; j++) {
				const int16_t low = value[group + j];
				const int16_t product = stage == 1U
					? value[group + distance + j]
					: montgomery_fixed(value[group + distance + j], factor);
				value[group + j] = (int16_t)(low + product);
				value[group + distance + j] = (int16_t)(low - product);
			}
		}
	}
}

static void inverse_one_coefficient(int16_t value[32])
{
	for (unsigned length = 2; length <= 32; length <<= 1) {
		const unsigned distance = length >> 1;
		for (unsigned group = 0; group < 32; group += length) {
			for (unsigned j = 0; j < distance; j++) {
				const unsigned power = j * (32U / length);
				const int16_t factor = omega32_mont[(32U - power) & 31U];
				const int16_t low = value[group + j];
				const int16_t product = length == 2U
					? value[group + distance + j]
					: montgomery_fixed(value[group + distance + j], factor);
				value[group + j] = (int16_t)(low + product);
				value[group + distance + j] = (int16_t)(low - product);
			}
		}
	}
}

static void tile_transform(int16_t out[GT32_TILE4_WORDS],
	const int16_t in[GT32_TILE4_WORDS], int inverse)
{
	int16_t local[GT32_TILE4_WORDS];

	memcpy(local, in, sizeof(local));
	for (unsigned coefficient = 0; coefficient < 4; coefficient++) {
		int16_t stream[32];
		for (unsigned q = 0; q < 32; q++)
			stream[q] = local[16U * (q / 4U) + 4U * (q % 4U) + coefficient];
		if (inverse != 0)
			inverse_one_coefficient(stream);
		else
			forward_one_coefficient(stream);
		for (unsigned q = 0; q < 32; q++)
			out[16U * (q / 4U) + 4U * (q % 4U) + coefficient] = stream[q];
	}
}

void gt32_tile4_forward_tile_ref(int16_t out[GT32_TILE4_WORDS],
	const int16_t in[GT32_TILE4_WORDS])
{
	tile_transform(out, in, 0);
}

void gt32_tile4_inverse_tile_ref(int16_t out[GT32_TILE4_WORDS],
	const int16_t in[GT32_TILE4_WORDS])
{
	tile_transform(out, in, 1);
}

void gt32_tile4_forward_all_ref(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS])
{
	for (unsigned tile = 0; tile < GT32_TILE4_TILES; tile++)
		gt32_tile4_forward_tile_ref(out + tile * GT32_TILE4_WORDS,
			in + tile * GT32_TILE4_WORDS);
}

void gt32_tile4_inverse_all_ref(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t in[GT32_TILE4_POLY_WORDS])
{
	for (unsigned tile = 0; tile < GT32_TILE4_TILES; tile++)
		gt32_tile4_inverse_tile_ref(out + tile * GT32_TILE4_WORDS,
			in + tile * GT32_TILE4_WORDS);
}
