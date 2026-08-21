#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "params.h"

#define ITERATIONS 200000

void ntruplus768_pack_m_lazy10788_avx2(uint8_t *, const int16_t *);
void gt041_ntruplus768_pack_m_lazy10788_avx2(uint8_t *, const int16_t *);
void ntruplus768_basemul_general_m_avx2(int16_t *, const int16_t *, const int16_t *);
void gt041_ntruplus768_basemul_general_m_avx2(int16_t *, const int16_t *, const int16_t *);

static int16_t a[NTRUPLUS_N] __attribute__((aligned(64)));
static int16_t b[NTRUPLUS_N] __attribute__((aligned(64)));
static int16_t out[NTRUPLUS_N] __attribute__((aligned(64)));
static uint8_t bytes[NTRUPLUS_POLYBYTES] __attribute__((aligned(64)));
static volatile uint64_t sink;

__attribute__((noinline)) static void run_pack_control(void)
{ ntruplus768_pack_m_lazy10788_avx2(bytes, a); }
__attribute__((noinline)) static void run_pack_candidate(void)
{ gt041_ntruplus768_pack_m_lazy10788_avx2(bytes, a); }
__attribute__((noinline)) static void run_b3_control(void)
{ ntruplus768_basemul_general_m_avx2(out, a, b); }
__attribute__((noinline)) static void run_b3_candidate(void)
{ gt041_ntruplus768_basemul_general_m_avx2(out, a, b); }

int main(int argc, char **argv)
{
	uint32_t state = 1;
	void (*run)(void);
	if (argc != 2) return 2;
	for (unsigned i = 0; i < NTRUPLUS_N; i++) {
		state = state * 1664525U + 1013904223U;
		a[i] = (int16_t)((int)(state % 21577U) - 10788);
		state = state * 1664525U + 1013904223U;
		b[i] = (int16_t)((int)(state % 21577U) - 10788);
	}
	if (strcmp(argv[1], "pack_control") == 0) run = run_pack_control;
	else if (strcmp(argv[1], "pack_candidate") == 0) run = run_pack_candidate;
	else if (strcmp(argv[1], "b3_control") == 0) run = run_b3_control;
	else if (strcmp(argv[1], "b3_candidate") == 0) run = run_b3_candidate;
	else return 3;
	for (unsigned i = 0; i < ITERATIONS; i++) run();
	sink = bytes[0] + (uint16_t)out[0];
	printf("%llu\n", (unsigned long long)sink);
	return 0;
}
