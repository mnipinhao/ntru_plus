#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "internal.h"
#include "baseinv_tables.inc"

static uint64_t state = UINT64_C(0x096f10a11a5b3c4d);

static uint32_t rnd(void)
{
	state ^= state << 13;
	state ^= state >> 7;
	state ^= state << 17;
	return (uint32_t)state;
}

int main(void)
{
	static int16_t coeff[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t frontend[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t inplace[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t h[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t h_copy[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t r[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t m[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t m_copy[NTRUPLUS_N] __attribute__((aligned(64)));
	static int16_t expected[NTRUPLUS_N] __attribute__((aligned(64)));
	uint8_t wire0[NTRUPLUS_POLYBYTES], wire1[NTRUPLUS_POLYBYTES];

	for (int test = 0; test < 1000; test++) {
		for (size_t i = 0; i < NTRUPLUS_N; i++)
			coeff[i] = (int16_t)((int32_t)(rnd() % 3u) - 1);
		memcpy(inplace, coeff, sizeof inplace);
		ntruplus768_ntt_frontend_avx2(frontend, coeff);
		ntruplus768_ntt_frontend_avx2(inplace, inplace);
		if (memcmp(frontend, inplace, sizeof frontend) != 0) {
			fprintf(stderr, "frontend alias mismatch %d\n", test);
			return 1;
		}
		ntruplus768_ntt_m_avx2(r, frontend);
		ntruplus768_ntt_m_avx2(inplace, inplace);
		if (memcmp(r, inplace, sizeof r) != 0) {
			fprintf(stderr, "ntt_m alias mismatch %d\n", test);
			return 1;
		}
		for (size_t i = 0; i < NTRUPLUS_N; i++)
			coeff[i] = (int16_t)((int32_t)(rnd() % 3u) - 1);
		ntruplus768_ntt_frontend_avx2(frontend, coeff);
		ntruplus768_ntt_m_avx2(h, frontend);
		for (size_t i = 0; i < NTRUPLUS_N; i++)
			coeff[i] = (int16_t)((int32_t)(rnd() % 3u) - 1);
		ntruplus768_ntt_frontend_avx2(frontend, coeff);
		ntruplus768_ntt_m_avx2(m, frontend);
		memcpy(h_copy, h, sizeof h);
		memcpy(m_copy, m, sizeof m);
		ntruplus768_basemul_general_m_avx2(expected, h, r);
		ntruplus768_basemul_general_m_avx2(r, h, r);
		if (memcmp(r, expected, sizeof r) != 0 ||
		    memcmp(h, h_copy, sizeof h) != 0 ||
		    memcmp(m, m_copy, sizeof m) != 0) {
			fprintf(stderr, "B3 ownership mismatch %d\n", test);
			return 1;
		}
		ntruplus768_pack_m_sum_highrange12699_avx2(wire0, expected, m);
		ntruplus768_pack_m_sum_highrange12699_avx2(wire1, r, m);
		if (memcmp(wire0, wire1, sizeof wire0) != 0) {
			fprintf(stderr, "suffix mismatch %d\n", test);
			return 1;
		}
	}
	puts("PASS frontend-inplace + ntt_m-inplace + B3-r-alias + Q24 exact");
	return 0;
}
