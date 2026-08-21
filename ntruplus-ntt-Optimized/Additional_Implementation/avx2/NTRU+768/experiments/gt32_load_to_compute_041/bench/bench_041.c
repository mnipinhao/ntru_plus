#include <inttypes.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

#include "cpucycles.h"
#include "params.h"

#define SAMPLES 63
#define INNER 64

void ntruplus768_pack_m_lazy10788_avx2(uint8_t *, const int16_t *);
void gt041_ntruplus768_pack_m_lazy10788_avx2(uint8_t *, const int16_t *);
void ntruplus768_basemul_general_m_avx2(int16_t *, const int16_t *, const int16_t *);
void gt041_ntruplus768_basemul_general_m_avx2(int16_t *, const int16_t *, const int16_t *);

static int16_t a[NTRUPLUS_N] __attribute__((aligned(64)));
static int16_t b[NTRUPLUS_N] __attribute__((aligned(64)));
static int16_t out0[NTRUPLUS_N] __attribute__((aligned(64)));
static int16_t out1[NTRUPLUS_N] __attribute__((aligned(64)));
static uint8_t bytes0[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
static uint8_t bytes1[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
static volatile uint64_t sink;

static int cmp_u64(const void *x, const void *y)
{
	const uint64_t a0 = *(const uint64_t *)x;
	const uint64_t b0 = *(const uint64_t *)y;
	return (a0 > b0) - (a0 < b0);
}

static uint64_t median_region(unsigned region, unsigned candidate)
{
	uint64_t values[SAMPLES];
	for (unsigned warm = 0; warm < 256; warm++) {
		if (region == 0) {
			if (candidate) gt041_ntruplus768_pack_m_lazy10788_avx2(bytes1, a);
			else ntruplus768_pack_m_lazy10788_avx2(bytes0, a);
		} else {
			if (candidate) gt041_ntruplus768_basemul_general_m_avx2(out1, a, b);
			else ntruplus768_basemul_general_m_avx2(out0, a, b);
		}
	}
	for (unsigned sample = 0; sample < SAMPLES; sample++) {
		const long long begin = cpucycles();
		for (unsigned i = 0; i < INNER; i++) {
			if (region == 0) {
				if (candidate) gt041_ntruplus768_pack_m_lazy10788_avx2(bytes1, a);
				else ntruplus768_pack_m_lazy10788_avx2(bytes0, a);
			} else {
				if (candidate) gt041_ntruplus768_basemul_general_m_avx2(out1, a, b);
				else ntruplus768_basemul_general_m_avx2(out0, a, b);
			}
		}
		values[sample] = (uint64_t)(cpucycles() - begin);
	}
	qsort(values, SAMPLES, sizeof values[0], cmp_u64);
	return values[SAMPLES / 2] / INNER;
}

int main(void)
{
	uint32_t state = 1;
	for (unsigned i = 0; i < NTRUPLUS_N; i++) {
		state = state * 1664525U + 1013904223U;
		a[i] = (int16_t)((int)(state % 21577U) - 10788);
		state = state * 1664525U + 1013904223U;
		b[i] = (int16_t)((int)(state % 21577U) - 10788);
	}
	ntruplus768_pack_m_lazy10788_avx2(bytes0, a);
	gt041_ntruplus768_pack_m_lazy10788_avx2(bytes1, a);
	ntruplus768_basemul_general_m_avx2(out0, a, b);
	gt041_ntruplus768_basemul_general_m_avx2(out1, a, b);
	for (unsigned i = 0; i < NTRUPLUS_POLYBYTES; i++)
		if (bytes0[i] != bytes1[i]) return 10;
	for (unsigned i = 0; i < NTRUPLUS_N; i++)
		if (out0[i] != out1[i]) return 11;
	printf("cpucycles_implementation %s\n", cpucycles_implementation());
	printf("pack_control %p\n", (void *)(uintptr_t)ntruplus768_pack_m_lazy10788_avx2);
	printf("pack_candidate %p\n", (void *)(uintptr_t)gt041_ntruplus768_pack_m_lazy10788_avx2);
	printf("b3_control %p\n", (void *)(uintptr_t)ntruplus768_basemul_general_m_avx2);
	printf("b3_candidate %p\n", (void *)(uintptr_t)gt041_ntruplus768_basemul_general_m_avx2);
	for (unsigned round = 0; round < 32; round++) {
		const unsigned first = round & 1U;
		const uint64_t p0 = median_region(0, first);
		const uint64_t p1 = median_region(0, first ^ 1U);
		const uint64_t b0 = median_region(1, first);
		const uint64_t b1 = median_region(1, first ^ 1U);
		printf("round %u order %c pack_control %" PRIu64 " pack_candidate %" PRIu64
		       " b3_control %" PRIu64 " b3_candidate %" PRIu64 "\n", round,
		       first ? 'B' : 'A', first ? p1 : p0, first ? p0 : p1,
		       first ? b1 : b0, first ? b0 : b1);
	}
	sink = bytes0[0] + bytes1[1] + (uint16_t)out0[2] + (uint16_t)out1[3];
	printf("sink %" PRIu64 "\n", sink);
	return 0;
}
