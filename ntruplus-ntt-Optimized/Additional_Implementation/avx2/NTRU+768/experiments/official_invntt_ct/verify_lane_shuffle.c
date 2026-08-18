#include <immintrin.h>
#include <stdint.h>
#include <stdio.h>

static void dump(const char *level, __m256i value)
{
	int16_t lanes[16];
	_mm256_storeu_si256((__m256i *)lanes, value);
	printf("%s", level);
	for (unsigned i = 0; i < 16; ++i) printf(" %d", lanes[i]);
	putchar('\n');
}

int main(void)
{
	int16_t ids[8][16] __attribute__((aligned(32)));
	__m256i r[8];
	for (unsigned reg = 0; reg < 8; ++reg)
		for (unsigned lane = 0; lane < 16; ++lane)
			ids[reg][lane] = (int16_t)(100 * (int)reg + (int)lane);
	for (unsigned reg = 0; reg < 8; ++reg)
		r[reg] = _mm256_load_si256((const __m256i *)ids[reg]);

	__m256i o6[8];
	o6[0] = _mm256_blend_epi16(r[0], _mm256_slli_epi64(r[1], 16), 0xaa);
	o6[1] = _mm256_blend_epi16(r[2], _mm256_slli_epi64(r[3], 16), 0xaa);
	o6[2] = _mm256_blend_epi16(r[4], _mm256_slli_epi64(r[5], 16), 0xaa);
	o6[3] = _mm256_blend_epi16(r[6], _mm256_slli_epi64(r[7], 16), 0xaa);
	o6[7] = _mm256_blend_epi16(_mm256_srli_epi64(r[6], 16), r[7], 0xaa);
	o6[6] = _mm256_blend_epi16(_mm256_srli_epi64(r[4], 16), r[5], 0xaa);
	o6[5] = _mm256_blend_epi16(_mm256_srli_epi64(r[2], 16), r[3], 0xaa);
	o6[4] = _mm256_blend_epi16(_mm256_srli_epi64(r[0], 16), r[1], 0xaa);
	for (unsigned i = 0; i < 8; ++i) { char name[8]; snprintf(name, sizeof(name), "L6.%u", i); dump(name, o6[i]); }

	__m256i o5[8];
	o5[0] = _mm256_blend_epi32(r[0], _mm256_slli_epi64(r[1], 32), 0xaa);
	o5[1] = _mm256_blend_epi32(r[2], _mm256_slli_epi64(r[3], 32), 0xaa);
	o5[2] = _mm256_blend_epi32(r[4], _mm256_slli_epi64(r[5], 32), 0xaa);
	o5[3] = _mm256_blend_epi32(r[6], _mm256_slli_epi64(r[7], 32), 0xaa);
	o5[7] = _mm256_blend_epi32(_mm256_srli_epi64(r[6], 32), r[7], 0xaa);
	o5[6] = _mm256_blend_epi32(_mm256_srli_epi64(r[4], 32), r[5], 0xaa);
	o5[5] = _mm256_blend_epi32(_mm256_srli_epi64(r[2], 32), r[3], 0xaa);
	o5[4] = _mm256_blend_epi32(_mm256_srli_epi64(r[0], 32), r[1], 0xaa);
	for (unsigned i = 0; i < 8; ++i) { char name[8]; snprintf(name, sizeof(name), "L5.%u", i); dump(name, o5[i]); }

	__m256i o4[8] = {
		_mm256_unpacklo_epi64(r[0], r[1]), _mm256_unpacklo_epi64(r[2], r[3]),
		_mm256_unpacklo_epi64(r[4], r[5]), _mm256_unpacklo_epi64(r[6], r[7]),
		_mm256_unpackhi_epi64(r[0], r[1]), _mm256_unpackhi_epi64(r[2], r[3]),
		_mm256_unpackhi_epi64(r[4], r[5]), _mm256_unpackhi_epi64(r[6], r[7]),
	};
	for (unsigned i = 0; i < 8; ++i) { char name[8]; snprintf(name, sizeof(name), "L4.%u", i); dump(name, o4[i]); }

	__m256i o3[8] = {
		_mm256_permute2x128_si256(r[0], r[1], 0x20), _mm256_permute2x128_si256(r[2], r[3], 0x20),
		_mm256_permute2x128_si256(r[4], r[5], 0x20), _mm256_permute2x128_si256(r[6], r[7], 0x20),
		_mm256_permute2x128_si256(r[0], r[1], 0x31), _mm256_permute2x128_si256(r[2], r[3], 0x31),
		_mm256_permute2x128_si256(r[4], r[5], 0x31), _mm256_permute2x128_si256(r[6], r[7], 0x31),
	};
	for (unsigned i = 0; i < 8; ++i) { char name[8]; snprintf(name, sizeof(name), "L3.%u", i); dump(name, o3[i]); }
	return 0;
}
