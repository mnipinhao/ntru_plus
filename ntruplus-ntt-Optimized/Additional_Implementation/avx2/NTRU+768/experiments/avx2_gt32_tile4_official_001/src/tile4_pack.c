#include <stddef.h>
#include <stdint.h>

#include "tile4.h"
#include "../generated/tile4_serialized_mapping.h"

int poly_frombytes(int16_t *r, const uint8_t *a);

static int frombytes_mapped(int16_t out[GT32_TILE4_POLY_WORDS],
	const uint8_t in[GT32_TILE4_SERIALIZED_BYTES], const uint16_t mapping[768])
{
	uint32_t invalid = 0;
	for (size_t pair = 0; pair < 384; pair++) {
		const size_t byte = 3U * pair;
		const uint16_t first = (uint16_t)in[byte]
			| (uint16_t)((uint16_t)(in[byte + 1U] & 15U) << 8);
		const uint16_t second = (uint16_t)(in[byte + 1U] >> 4)
			| (uint16_t)((uint16_t)in[byte + 2U] << 4);
		out[mapping[2U * pair]] = (int16_t)first;
		out[mapping[2U * pair + 1U]] = (int16_t)second;
		invalid |= (uint32_t)(first >= GT32_TILE4_Q);
		invalid |= (uint32_t)(second >= GT32_TILE4_Q);
	}
	return (int)(invalid != 0U);
}

int gt32_tile4_frombytes_aos_ref(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const uint8_t in[GT32_TILE4_SERIALIZED_BYTES])
{
	return frombytes_mapped(out, in, gt32_tile4_serialized_to_aos);
}

int gt32_tile4_frombytes_bm_soa_ref(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const uint8_t in[GT32_TILE4_SERIALIZED_BYTES])
{
	return frombytes_mapped(out, in, gt32_tile4_serialized_to_bm_soa);
}

static void official_words_mapped(int16_t out[GT32_TILE4_POLY_WORDS],
	const int16_t official[GT32_TILE4_POLY_WORDS], const uint16_t mapping[768])
{
	for (size_t serialized = 0; serialized < 768; serialized++) {
		const size_t within = serialized % 128U;
		const size_t official_word = 128U * (serialized / 128U)
			+ within / 8U + 16U * (within % 8U);
		out[mapping[serialized]] = official[official_word];
	}
}

int gt32_tile4_frombytes_aos_official_bridge(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const uint8_t in[GT32_TILE4_SERIALIZED_BYTES])
{
	int16_t official[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	const int result = poly_frombytes(official, in);
	official_words_mapped(out, official, gt32_tile4_serialized_to_aos);
	return result;
}

int gt32_tile4_frombytes_bm_soa_official_bridge(
	int16_t out[GT32_TILE4_POLY_WORDS],
	const uint8_t in[GT32_TILE4_SERIALIZED_BYTES])
{
	int16_t official[GT32_TILE4_POLY_WORDS] __attribute__((aligned(32)));
	const int result = poly_frombytes(official, in);
	official_words_mapped(out, official, gt32_tile4_serialized_to_bm_soa);
	return result;
}
