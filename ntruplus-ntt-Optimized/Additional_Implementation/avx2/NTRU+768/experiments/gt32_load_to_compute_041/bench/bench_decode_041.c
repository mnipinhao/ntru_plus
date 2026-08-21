#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "cpucycles.h"
#include "params.h"

#define SAMPLES 63
#define INNER 64

int ntruplus768_unpack_m_avx2(int16_t *, const uint8_t *);
int gt041d_ntruplus768_unpack_m_avx2(int16_t *, const uint8_t *);
void ntruplus768_pack_m_lazy10788_avx2(uint8_t *, const int16_t *);

static int16_t coeff[NTRUPLUS_N] __attribute__((aligned(64)));
static int16_t out0[NTRUPLUS_N] __attribute__((aligned(64)));
static int16_t out1[NTRUPLUS_N] __attribute__((aligned(64)));
static uint8_t wire[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
static volatile uint64_t sink;

static void set12(uint8_t *p, unsigned index, unsigned value)
{
	const unsigned bit = index * 12U;
	const unsigned byte = bit >> 3;
	const unsigned shift = bit & 7U;
	uint32_t word = p[byte] | ((uint32_t)p[byte + 1] << 8);
	if (byte + 2 < NTRUPLUS_POLYBYTES)
		word |= (uint32_t)p[byte + 2] << 16;
	word &= ~((uint32_t)0xfff << shift);
	word |= (uint32_t)value << shift;
	p[byte] = (uint8_t)word;
	p[byte + 1] = (uint8_t)(word >> 8);
	if (byte + 2 < NTRUPLUS_POLYBYTES)
		p[byte + 2] = (uint8_t)(word >> 16);
}

static int cmp_u64(const void *x, const void *y)
{
	const uint64_t a = *(const uint64_t *)x, b = *(const uint64_t *)y;
	return (a > b) - (a < b);
}

static uint64_t measure(unsigned candidate)
{
	uint64_t samples[SAMPLES];
	for (unsigned warm = 0; warm < 256; warm++)
		if (candidate) gt041d_ntruplus768_unpack_m_avx2(out1, wire);
		else ntruplus768_unpack_m_avx2(out0, wire);
	for (unsigned s = 0; s < SAMPLES; s++) {
		const long long begin = cpucycles();
		for (unsigned i = 0; i < INNER; i++)
			if (candidate) gt041d_ntruplus768_unpack_m_avx2(out1, wire);
			else ntruplus768_unpack_m_avx2(out0, wire);
		samples[s] = (uint64_t)(cpucycles() - begin);
	}
	qsort(samples, SAMPLES, sizeof samples[0], cmp_u64);
	return samples[SAMPLES / 2] / INNER;
}

int main(void)
{
	for (unsigned i = 0; i < NTRUPLUS_N; i++)
		coeff[i] = (int16_t)((i * 1777U + 31U) % 3457U);
	ntruplus768_pack_m_lazy10788_avx2(wire, coeff);
	if (ntruplus768_unpack_m_avx2(out0, wire) != 0 ||
	    gt041d_ntruplus768_unpack_m_avx2(out1, wire) != 0) return 10;
	for (unsigned i = 0; i < NTRUPLUS_N; i++)
		if (out0[i] != out1[i]) return 11;
	for (unsigned slot = 0; slot < NTRUPLUS_N; slot++) {
		ntruplus768_pack_m_lazy10788_avx2(wire, coeff);
		set12(wire, slot, 3457U);
		const int r0 = ntruplus768_unpack_m_avx2(out0, wire);
		const int r1 = gt041d_ntruplus768_unpack_m_avx2(out1, wire);
		if (r0 != r1 || r0 == 0) return 12;
		for (unsigned i = 0; i < NTRUPLUS_N; i++)
			if (out0[i] != out1[i]) return 13;
	}
	ntruplus768_pack_m_lazy10788_avx2(wire, coeff);
	for (unsigned round = 0; round < 32; round++) {
		const unsigned first = round & 1U;
		const uint64_t a = measure(first), b = measure(first ^ 1U);
		printf("round %u control %" PRIu64 " candidate %" PRIu64 "\n",
		       round, first ? b : a, first ? a : b);
	}
	sink = (uint16_t)out0[0] + (uint16_t)out1[1];
	return (int)(sink & 0U);
}
